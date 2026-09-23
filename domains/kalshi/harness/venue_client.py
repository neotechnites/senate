"""Authentic Kalshi Trade API v2 Client for Kalshi Domain Pod."""

import base64
import json
import os
import re
import ssl
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.parse
import urllib.error

from domains.kalshi.verify.caps import PER_MARKET_HARD_USD
from domains.kalshi.harness.positions import (POSITION_COUNT_KEYS,
                                              POSITION_EXPOSURE_CENT_KEYS,
                                              POSITION_EXPOSURE_DOLLAR_KEYS,
                                              parse_position_row)

BASE_URL = "https://api.elections.kalshi.com"
TRADE_API_PREFIX = "/trade-api/v2"

# ======================================================================
# RATE-LIMIT CONTENTION IS NOT A DATA ERROR (Ryan, 2026-08-18)
# ======================================================================
# Plan row 61 (KXYELLVISITS-27MAR31-T5000000) was refused every cycle with
# "expiry unreadable from venue (fail closed)".  The expiry was perfectly
# readable — expected_expiration_time 2027-04-07T15:30:00Z, fetched by hand on
# the first try.  What the engine actually caught was an HTTP 429 thrown by our
# OWN research lanes saturating the shared venue rate limit, and every read path
# in the pod funnels `except Exception` into "unreadable" / ok=False.
#
#     Failing closed is correct.  Silently losing the placement for a full
#     5-minute cycle, and logging it as though the venue served bad data, is not.
#
# So: a 429 is RETRIED PROMPTLY, in-cycle, with exponential backoff, and it is
# recorded as a DISTINCT diagnosis from a genuinely absent/malformed payload.
# Fail-closed behaviour is untouched — when the retries are exhausted the caller
# still refuses.  Only the diagnosis and the retry policy change.
#
# The budget is deliberately small: 4 attempts at 0.35s/0.70s/1.40s is ~2.5s
# worst case, which fits inside a 300s cadence cycle many times over and cannot
# stall the DEFENSIVE path.
RATE_LIMIT_MAX_ATTEMPTS = 4
RATE_LIMIT_BASE_SLEEP_SEC = 0.35
RATE_LIMIT_MAX_SLEEP_SEC = 5.0

_RE_429 = re.compile(r"\b429\b")

# ======================================================================
# THE DEFENSIVE CANCEL MUST NOT PAY FOR ENDPOINT ARCHAEOLOGY (2026-08-18)
# ======================================================================
# 13:42:04.590  SHIELD_ALARM on KXGENERICBALLOTVOTEHUB-26AUG21-T6.8
# 13:42:06.748  ATOMIC_NOOP, alarm_to_cancel_ms 1971.4, cancel_ms 1963.9,
#               cancel_attempts 3 — against every other reactive trip that
#               night, which measured 90-263 ms with cancel_attempts 1.
# Three more trips on the same seat measured 1611 / 1711 / 2015 ms.
#
# THE ARITHMETIC.  The seat had already FILLED, so the order id was dead.
# `cancel_order` walked all three candidate paths, each a signed DELETE round
# trip (~160 ms), and PlacementEngine._cancel_with_retry then repeated the whole
# thing 3 times with a 250 ms sleep between attempts:
#       3 attempts x 3 candidate paths x ~160 ms  +  2 x 250 ms  =  ~1.96 s.
# Nine round trips to discover, nine times, that an order that no longer exists
# cannot be cancelled.
#
# WHY THAT IS A SAFETY HOLE AND NOT MERELY WASTE.  The observed case was a dead
# order, where the delay costs nothing.  But NOTHING IN THE OLD CODE RESTRICTED
# THE FAN-OUT TO DEAD ORDERS.  `except Exception: continue` treated a socket
# timeout, a TLS error, a 5xx and a 429 exactly like a 410 Gone — so a LIVE
# order whose cancel hit one transient blip would then probe two endpoints the
# pod has EMPIRICALLY MEASURED AS DEAD (404 and 410 as of 2026-08-18), which
# cannot possibly cancel it, before failing.  With the old timeout=10 that was
# up to 3 x 10 s per attempt and 3 x that per engine retry: ~90 s of a naked
# seat resting in a book that is eating the queue in front of it.
#
# THE RULE.  Fallback probing answers exactly one question — "is this URL SHAPE
# still served here?" — so it may only be triggered by an answer to that
# question.  404 / 405 / 410 / 501 are such answers.  A timeout, a DNS failure,
# a reset connection, a 5xx or a 429 say NOTHING about the URL; they are raised
# immediately as CancelPathTransientError so the caller retries the CORRECT
# path at once instead of touring the graveyard.  The fallback keeps its full
# behaviour for the genuinely ambiguous case it was written for.
#
# Plus two hard bounds, because "fast in the common case" is not a guarantee:
#   * every cancel request carries CANCEL_REQUEST_TIMEOUT_SEC, not the generic
#     read timeout of 10 s — a defensive cancel that has not been answered in
#     5 s has failed;
#   * the whole call, candidates included, is capped by CANCEL_TOTAL_BUDGET_SEC.
# And the path that actually worked is remembered, so a venue rollback costs
# ONE probing cancel rather than one per cancel forever.
CANCEL_REQUEST_TIMEOUT_SEC = float(os.environ.get("KALSHI_CANCEL_REQUEST_TIMEOUT_SEC", "5.0"))
CANCEL_TOTAL_BUDGET_SEC = float(os.environ.get("KALSHI_CANCEL_TOTAL_BUDGET_SEC", "8.0"))

# The only HTTP statuses that mean "this URL shape is not served here" and can
# therefore justify trying a different URL shape.  Everything else — including
# 401/403 (auth), 429 (rate limit) and every 5xx — is about the request or the
# server, not about the path, and probing another path cannot help.
ENDPOINT_DEAD_STATUSES = frozenset((404, 405, 410, 501))


class CancelPathTransientError(RuntimeError):
    """A cancel attempt failed for a reason that says nothing about the endpoint.

    Raised INSTEAD OF walking the remaining candidate paths, because those paths
    are known-dead and probing them would only add latency to the defensive
    cancel of a possibly-live order.  Callers already retry cancels promptly
    (PlacementEngine._cancel_with_retry, QueueShieldMonitor's retry campaign);
    this is the failure they should retry, and retry against the SAME path.
    """

    def __init__(self, message: str, cause: Optional[BaseException] = None,
                 path: Optional[str] = None):
        super().__init__(message)
        self.cause = cause
        self.path = path


def http_status_of(exc: BaseException) -> Optional[int]:
    """The HTTP status carried by `exc`, or None when it carries none."""
    for attr in ("code", "status"):
        val = getattr(exc, attr, None)
        if val is not None:
            try:
                return int(val)
            except (TypeError, ValueError):
                pass
    return None


def is_endpoint_shaped_failure(exc: BaseException) -> bool:
    """Could `exc` mean 'this URL shape is not served here'?

    True ONLY for the statuses in ENDPOINT_DEAD_STATUSES.  A transport failure
    (timeout, reset, DNS, TLS) carries no status at all and is never endpoint
    evidence — that conflation is what let a transient blip on a LIVE order's
    cancel turn into a tour of two empirically-dead endpoints.
    """
    code = http_status_of(exc)
    return code is not None and code in ENDPOINT_DEAD_STATUSES


def is_rate_limited(exc: BaseException) -> bool:
    """True when `exc` is the venue's rate limiter, not a data or shape error.

    Checks the structured status first (urllib.error.HTTPError.code, or a
    .status/.code attribute on any other client's exception) and falls back to
    the textual `429` token, which is how the pod's other paced readers
    (depth_sampler, fillrate_logger) have always detected it.
    """
    for attr in ("code", "status"):
        val = getattr(exc, attr, None)
        if val is not None:
            try:
                return int(val) == 429
            except (TypeError, ValueError):
                pass
    return bool(_RE_429.search(str(exc)))


def _retry_after_sec(exc: BaseException, fallback: float) -> float:
    """Honour a Retry-After header when the venue sends one, capped."""
    headers = getattr(exc, "headers", None)
    raw = None
    if headers is not None:
        try:
            raw = headers.get("Retry-After")
        except Exception:
            raw = None
    if raw is not None:
        try:
            return max(0.0, min(RATE_LIMIT_MAX_SLEEP_SEC, float(str(raw).strip())))
        except (TypeError, ValueError):
            pass
    return max(0.0, min(RATE_LIMIT_MAX_SLEEP_SEC, float(fallback)))


def call_with_rate_limit_retry(
    fn: Any,
    *args: Any,
    attempts: int = RATE_LIMIT_MAX_ATTEMPTS,
    base_sleep: float = RATE_LIMIT_BASE_SLEEP_SEC,
    sleep_fn: Any = time.sleep,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Call `fn`, retrying ONLY on venue rate-limit (429) responses.

    Returns {ok, value, error, attempts, retries, rate_limited}.  A non-429
    failure returns immediately with rate_limited=False — a genuine data error
    must NOT be papered over with retries.  Exhausting the 429 budget returns
    ok=False with rate_limited=True, which the caller reports as such and then
    STILL fails closed.  Never raises.
    """
    n = max(1, int(attempts))
    last: Optional[BaseException] = None
    for i in range(n):
        try:
            return {"ok": True, "value": fn(*args, **kwargs), "error": None,
                    "attempts": i + 1, "retries": i, "rate_limited": False}
        except Exception as exc:  # noqa: BLE001 — classified, then re-reported
            last = exc
            if not is_rate_limited(exc):
                return {"ok": False, "value": None, "error": exc,
                        "attempts": i + 1, "retries": i, "rate_limited": False}
            if i < n - 1:
                sleep_fn(_retry_after_sec(exc, float(base_sleep) * (2 ** i)))
    return {"ok": False, "value": None, "error": last,
            "attempts": n, "retries": n - 1, "rate_limited": True}


def rate_limit_note(res: Dict[str, Any]) -> str:
    """The audit fragment that tells a 429 apart from bad data, in one place."""
    if res.get("rate_limited"):
        return f"rate-limited, retried {res.get('retries', 0)} times"
    err = res.get("error")
    return f"venue read failed: {str(err)[:120]}" if err is not None else ""


def _get_ssl_context() -> ssl.SSLContext:
    """Create robust SSL context supporting macOS framework certificate bundles."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _load_env_candidates() -> Dict[str, str]:
    """Search standard candidate locations for Kalshi API credentials."""
    env_vars = {}
    repo_root = Path(__file__).resolve().parents[3]
    candidates = [
        Path.cwd() / ".env",
        repo_root / "nestor" / ".env",
        Path.home() / ".env",
        Path.home() / "nestor" / ".env",
        Path.home() / "senate" / "nestor" / ".env",
        Path.home() / "kalshi_data" / ".env",
    ]
    for cp in candidates:
        if cp.exists() and cp.is_file():
            try:
                for line in cp.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        val = v.strip().strip("'").strip('"')
                        if "PATH" in k and val.startswith("."):
                            val = str((cp.parent / val).resolve())
                        env_vars[k.strip()] = val
            except Exception:
                pass
    return env_vars


class KalshiVenueClient:
    """Venue client supporting authenticated portfolio access and unauthenticated public book data."""

    def __init__(
        self,
        api_key_id: Optional[str] = None,
        private_key_path: Optional[str] = None,
        base_url: str = BASE_URL,
    ):
        file_env = _load_env_candidates()
        self.api_key_id = (
            api_key_id
            or os.environ.get("KALSHI_API_KEY")
            or os.environ.get("KALSHI_API_KEY_ID")
            or file_env.get("KALSHI_API_KEY")
            or file_env.get("KALSHI_API_KEY_ID")
        )
        self.base_url = base_url.rstrip("/")
        self._private_key = None
        self._ssl_ctx = _get_ssl_context()
        # Index into CANCEL_PATH_TEMPLATES of the path that last cancelled
        # successfully.  None = use the preregistered correct-first order.
        self._cancel_path_idx: Optional[int] = None

        key_path = (
            private_key_path
            or os.environ.get("KALSHI_PRIVATE_KEY_PATH")
            or file_env.get("KALSHI_PRIVATE_KEY_PATH")
        )
        if key_path:
            expanded_path = os.path.expanduser(key_path)
            if os.path.exists(expanded_path):
                try:
                    from cryptography.hazmat.primitives import serialization
                    with open(expanded_path, "rb") as f:
                        self._private_key = serialization.load_pem_private_key(f.read(), password=None)
                except Exception:
                    self._private_key = None

    @property
    def has_credentials(self) -> bool:
        """Check if authenticated credentials (API key + private key) are loaded."""
        return bool(self.api_key_id and self._private_key)


    def _sign_headers(self, method: str, bare_path: str) -> Dict[str, str]:
        """Sign request. Invariant: bare_path MUST exclude query parameters."""
        if not (self.api_key_id and self._private_key):
            raise RuntimeError("Kalshi authenticated endpoints require KALSHI_API_KEY and private key.")

        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding

        if "?" in bare_path:
            bare_path = bare_path.split("?")[0]

        ts = str(int(time.time() * 1000))
        msg = (ts + method.upper() + bare_path).encode("utf-8")
        sig = self._private_key.sign(
            msg,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
            hashes.SHA256(),
        )
        return {
            "KALSHI-ACCESS-KEY": self.api_key_id,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode("utf-8"),
            "KALSHI-ACCESS-TIMESTAMP": ts,
            "Content-Type": "application/json",
        }

    def fetch_public_orderbook(self, ticker: str) -> Dict[str, Any]:
        """Fetch live public order book for a given ticker."""
        path = f"{TRADE_API_PREFIX}/markets/{ticker}/orderbook"
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, headers={"User-Agent": "SenateArchitect/2.0"})
        with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def fetch_balance(self) -> Dict[str, Any]:
        """Fetch live authenticated portfolio balance from Kalshi Trade API."""
        bare_path = f"{TRADE_API_PREFIX}/portfolio/balance"
        url = f"{self.base_url}{bare_path}"
        headers = self._sign_headers("GET", bare_path)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def fetch_open_orders(self) -> List[Dict[str, Any]]:
        """Fetch active resting open orders for this account."""
        bare_path = f"{TRADE_API_PREFIX}/portfolio/orders"
        url = f"{self.base_url}{bare_path}?status=resting"
        headers = self._sign_headers("GET", bare_path)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("orders", [])

    def fetch_fills(self, ticker: Optional[str] = None, limit: int = 200) -> List[Dict[str, Any]]:
        """Fetch recent fills for this account (newest first)."""
        bare_path = f"{TRADE_API_PREFIX}/portfolio/fills"
        query = f"?limit={int(limit)}"
        if ticker:
            query += f"&ticker={urllib.parse.quote(ticker)}"
        url = f"{self.base_url}{bare_path}{query}"
        headers = self._sign_headers("GET", bare_path)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("fills", [])

    def fetch_public_trades(self, ticker: str, max_pages: int = 20,
                            per_page: int = 100) -> tuple:
        """Fetch this market's PUBLIC trade tape.  (trades, capped).

        UNAUTHENTICATED, READ-ONLY.  Nothing on this path can place, cancel or
        modify an order; it is a plain GET of the same endpoint any browser
        hits, and it exists so the hazard gate (harness/hazard_gate.py) can ask
        how often this market throws a print bigger than the wall we rest
        behind.

        `capped` is True when the walk stopped on max_pages rather than on the
        venue running out of cursor — i.e. the history is TRUNCATED.  The gate
        re-anchors a truncated tape's denominator at the earliest print actually
        returned, so truncation can only OVERSTATE hazard.  Losing that flag
        would silently understate it, which is why it is returned rather than
        inferred.

        UNITS: each trade's `count_fp` is CONTRACTS ALREADY (see the UNITS block
        in hazard_gate.py).  It is returned untouched; no caller may divide it
        by a price.
        """
        bare_path = f"{TRADE_API_PREFIX}/markets/trades"
        out: List[Dict[str, Any]] = []
        cursor: Optional[str] = None
        capped = True
        for _ in range(max(1, int(max_pages))):
            params = {"ticker": ticker, "limit": int(per_page)}
            if cursor:
                params["cursor"] = cursor
            url = f"{self.base_url}{bare_path}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(
                url, headers={"User-Agent": "SenateArchitect/2.0",
                              "Accept": "application/json"})
            with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=15) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            page = body.get("trades") or []
            out.extend(page)
            cursor = body.get("cursor") or None
            if not cursor or not page:
                capped = False
                break
        return out, capped

    def fetch_market(self, ticker: str) -> Dict[str, Any]:
        """Fetch public market metadata (expected_expiration_time, close_time, status)."""
        path = f"{TRADE_API_PREFIX}/markets/{ticker}"
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, headers={"User-Agent": "SenateArchitect/2.0"})
        with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("market", body)

    def fetch_positions(self) -> List[Dict[str, Any]]:
        """Fetch all settled/active market positions for this account."""
        bare_path = f"{TRADE_API_PREFIX}/portfolio/positions"
        url = f"{self.base_url}{bare_path}"
        headers = self._sign_headers("GET", bare_path)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("market_positions", [])

    # ==================================================================
    # MT-1 (2026-09-09): LIFETIME P&L NEEDS THE DEPOSITS LEDGER, NOT A GUESS
    # ==================================================================
    # The pod printed "Cash: $966.10 | Positions: $14.52 | P&L: $+14.52" and
    # the Domain Head reported +$14.52 as the account's P&L.  Truth: $2,600
    # deposited across 13 deposits, account value ~$981, lifetime P&L
    # ~-$1,619.  The oracle read `raw_bal.get("lifetime_deposits",
    # cents_bal)`: the balance endpoint carries NO such key, so "deposits"
    # silently became the cash balance and "P&L" collapsed to the positions
    # mark.  Deposits live on their own paged endpoint,
    # GET /portfolio/deposits (list key "deposits"; amount in
    # "amount_dollars" (string) / "amount_cents" / "amount" (cents)), and
    # withdrawals on /portfolio/withdrawals, which 404s on an account that
    # has never withdrawn (nestor-wt-lipv5/tools/oracle/oracle.py, the
    # working reference: 13 rows, $2,600.00, 2026-08-06).  Both are read
    # with the same signed GET as fills/positions and walked to the end of
    # the cursor; a truncated ledger would understate deposits and so
    # OVERSTATE P&L, which is the one direction the oracle must never err.
    def _fetch_portfolio_ledger(self, endpoint: str, list_key: str,
                                limit: int = 200) -> List[Dict[str, Any]]:
        """Walk a paged /portfolio/<endpoint> ledger to the end of its cursor."""
        bare_path = f"{TRADE_API_PREFIX}/portfolio/{endpoint}"
        out: List[Dict[str, Any]] = []
        cursor: Optional[str] = None
        while True:
            params: Dict[str, Any] = {"limit": int(limit)}
            if cursor:
                params["cursor"] = cursor
            url = f"{self.base_url}{bare_path}?{urllib.parse.urlencode(params)}"
            headers = self._sign_headers("GET", bare_path)
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=15) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            # H1 (2026-09-09): a page WITHOUT the list key (renamed key, empty
            # body, error envelope with HTTP 200) is UNREADABLE, not empty.
            # Reading it as [] would total deposits to $0 and print lifetime
            # P&L = +account value -- the exact overstatement this ledger
            # exists to prevent.  An empty list under the right key is a
            # genuine empty page; the oracle decides what that means.
            if not isinstance(body, dict) or list_key not in body:
                raise ValueError(
                    f"/portfolio/{endpoint} page carries no '{list_key}' key: "
                    f"{json.dumps(body)[:200]}")
            page = body.get(list_key) or []
            out.extend(page)
            cursor = body.get("cursor") or None
            if not cursor or not page:
                return out

    def fetch_deposits(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Fetch EVERY deposit this account has ever made (paged, cursor-walked).

        Lifetime deposits are the denominator of lifetime P&L.  This is the
        only place they may come from; the oracle refuses to derive them
        from the balance (MT-1 above).
        """
        return self._fetch_portfolio_ledger("deposits", "deposits", limit=limit)

    def fetch_withdrawals(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Fetch every withdrawal (paged).  A 404 is "never withdrawn" -> [].

        The venue answers 404 on /portfolio/withdrawals for an account with
        no withdrawal history (reference oracle.py, 2026-08-06); that is a
        zero, not a failure, and only because the deposits page just proved
        the auth works.  Any other HTTP error propagates.
        """
        try:
            return self._fetch_portfolio_ledger("withdrawals", "withdrawals", limit=limit)
        except urllib.error.HTTPError as exc:
            if getattr(exc, "code", None) == 404:
                return []
            raise

    # ==================================================================
    # FLAT-1 (2026-09-05): THE POD COULD BUY BUT COULD NEVER SELL
    # ==================================================================
    # 25 lifetime fills, every one an informed sweep of a dead ladder: one
    # instant, ~1,300ct through whatever wall we rested behind, and the price
    # re-rated against us.  Every fill left an OPEN POSITION, and not one of
    # them was ever flattened -- the KXSNOWCRABCATCH position from 09-03 is
    # still open today, and a $50 seat on KXKR-26SEPIDSALES-1.5 joined it
    # this afternoon.  Why?  Because `place_post_only_order` below was the
    # pod's ONLY write path and it expresses BUYING only: side "yes" is a V2
    # bid at p, side "no" is a V2 ask at 100-p.  Selling YES held after a
    # sweep down to <=10c must be spelled as side="no" at acquire 100-p >=
    # 90c, which its own guard (`acquire_c >= 90`) rejects -- correctly, for
    # an ACQUIRE.  So the exact regime a sweep leaves us in ("price re-rates
    # against us") was the one regime the wire refused to let us leave.
    #
    # THE RULE.  A close REDUCES exposure, so it carries neither the $25 cost
    # cap nor the 90c acquire ceiling nor the cheap-NO ban -- those guard
    # capital going IN.  What a close must never do is create a NEW position
    # by over-selling, so its one hard guard is the venue's own live position
    # for the ticker: `count <= abs(position)` on the held side, read fresh
    # from GET /portfolio/positions at call time and FAILING CLOSED when that
    # read is unreadable or shows nothing held.  post_only stays True: even a
    # flatten is a maker order; we do not cross a book that just ran us over.
    #
    # FIELD NAMES (FLAT-10, 2026-09-05).  The venue's positions row carries
    # the signed contract count as `position_fp` / `position` and the
    # at-risk dollars as `market_exposure_fp` / `market_exposure_dollars`
    # (strings) or `market_exposure` (integer cents).  Until today this
    # class and harness/positions.py each kept their OWN key list and they
    # had already drifted (this one read `market_exposure_fp`, the leaf did
    # not) -- two parsers of one feed that nobody had ever confirmed
    # against a live row, because fetch_positions returned the body raw and
    # no code ever read a field from it.  Per the cancel-endpoint lesson
    # below, a docs-derived field name is a HYPOTHESIS until one live read
    # confirms it.  So there is now ONE parser (positions.parse_position_row)
    # that REPORTS which key it read; the engine pins those names into
    # kalshi.ops.positions_schema on the first live read, and a row with NO
    # recognisable count key is UNREADABLE (raise), never flat (0).  The
    # tuples stay exposed here for existing importers; they alias the leaf.
    POSITION_COUNT_KEYS = POSITION_COUNT_KEYS
    POSITION_EXPOSURE_DOLLAR_KEYS = POSITION_EXPOSURE_DOLLAR_KEYS
    POSITION_EXPOSURE_CENT_KEYS = POSITION_EXPOSURE_CENT_KEYS
    CLOSE_CLIENT_ORDER_PREFIX = "kfl-"

    def fetch_position(self, ticker: str) -> Dict[str, Any]:
        """The venue's LIVE position in one ticker, parsed.

        Returns {ticker, position_ct (signed: +YES / -NO contracts),
        held_side ('yes' | 'no' | None when flat), held_ct (abs),
        exposure_usd (None when the row carries no readable cost),
        count_key / exposure_key (the row keys actually read -- FLAT-10
        pins these), raw}.  A ticker absent from the feed, or present with
        zero contracts and no cost, is FLAT (position_ct 0.0, held_side
        None) -- the venue lists only tickers it holds.  Raises on any
        transport or auth failure and on a present row whose contract count
        is unreadable, so a caller that must not guess (the close) fails
        closed.
        """
        tk = str(ticker)
        rows = self.fetch_positions()  # raises -> caller fails closed
        row: Optional[Dict[str, Any]] = None
        for p in rows or []:
            if str(p.get("ticker")) == tk:
                row = p
                break
        flat = {"ticker": tk, "position_ct": 0.0, "held_side": None, "held_ct": 0.0,
                "exposure_usd": None, "count_key": None, "exposure_key": None, "raw": None}
        if row is None:
            return flat
        parsed = parse_position_row(row)  # raises ValueError on an unreadable count
        if parsed is None:
            flat["raw"] = row
            return flat
        parsed["ticker"] = tk
        return parsed

    def place_post_only_close(
        self,
        ticker: str,
        held_side: str,
        sell_price_cents: int,
        count: int,
        client_order_id: str,
    ) -> Dict[str, Any]:
        """Submit a post-only maker order that REDUCES a held position.

        `held_side` is the side we HOLD ("yes" / "no"); `sell_price_cents` is
        the price, in that side's own cents, we are willing to be paid.  In V2
        single-book YES-leg terms: selling held YES at p is side="ask" price=p;
        selling held NO at p is the same book's bid at (100-p).  See the FLAT-1
        receipt above for why this exists and why it carries no cost cap and
        no acquire ceiling.  The one hard guard is the live position.
        """
        side = str(held_side).lower()
        if side not in ("yes", "no"):
            raise ValueError(f"place_post_only_close: held_side must be 'yes' or 'no', got {held_side!r}")
        sell_c = int(sell_price_cents)
        if not 1 <= sell_c <= 99:
            raise ValueError(f"place_post_only_close: sell price {sell_c}c outside 1..99c")
        cnt = float(count)
        if not cnt > 0:
            raise ValueError(f"place_post_only_close: count must be > 0, got {count!r}")

        # THE GUARD: never sell more than the venue says we hold.  Read live,
        # fail closed.  A close that over-sells is an ACQUIRE of the other
        # side wearing a close's exemptions, and that is exactly the trap the
        # acquire guards exist to stop.
        try:
            pos = self.fetch_position(ticker)
        except Exception as exc:  # noqa: BLE001 -- any failure means we cannot prove what we hold
            raise ValueError(
                f"place_post_only_close refused for {ticker}: live position unreadable "
                f"({type(exc).__name__}: {str(exc)[:140]}) -- cannot prove what is held, "
                f"fail closed.") from exc
        held_ct = float(pos["position_ct"])
        if side == "yes" and held_ct <= 0:
            raise ValueError(
                f"place_post_only_close refused for {ticker}: venue shows {held_ct:+.0f}ct, "
                f"no YES held to sell (fail closed).")
        if side == "no" and held_ct >= 0:
            raise ValueError(
                f"place_post_only_close refused for {ticker}: venue shows {held_ct:+.0f}ct, "
                f"no NO held to sell (fail closed).")
        if cnt > abs(held_ct) + 1e-9:
            raise ValueError(
                f"place_post_only_close refused for {ticker}: count {cnt:.0f} exceeds held "
                f"{abs(held_ct):.0f}ct -- a close may only reduce, never flip, a position.")

        coid = str(client_order_id)
        if not coid.startswith(self.CLOSE_CLIENT_ORDER_PREFIX):
            coid = self.CLOSE_CLIENT_ORDER_PREFIX + coid

        bare_path = f"{TRADE_API_PREFIX}/portfolio/events/orders"
        url = f"{self.base_url}{bare_path}"
        headers = self._sign_headers("POST", bare_path)

        if side == "yes":
            v2_side, v2_price_c = "ask", sell_c
        else:
            v2_side, v2_price_c = "bid", 100 - sell_c
        payload = {
            "ticker": ticker,
            "side": v2_side,
            "count": f"{cnt:.2f}",
            "price": f"{v2_price_c / 100.0:.4f}",
            "time_in_force": "good_till_canceled",
            "self_trade_prevention_type": "maker",
            "post_only": True,
            "client_order_id": coid,
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
        # WIRE-1 (2026-09-10): NEVER SWALLOW THE VENUE'S OWN EXPLANATION.
        #
        # THE INCIDENT.  Between 07:05Z and 07:33Z the book fell 17 -> 4 seats
        # ($423 -> $99.55 escrow) because EIGHT re-placements in a row were
        # refused by the exchange.  Every one logged exactly this and no more:
        #     "NOT placed - venue placement failed: HTTP Error 409: Conflict"
        # urllib's HTTPError carries the response BODY and Kalshi puts the
        # machine-readable reason in it -- but the body is readable only off
        # the exception object, and letting the error propagate untouched threw
        # it away.  The pod could see the venue say no eight times and could not
        # see WHY once.  A refusal we cannot read is a refusal we cannot fix.
        #
        # Re-raises the SAME exception class carrying the status line, the body,
        # and the payload we sent -- a 409 is ABOUT the payload (duplicate
        # client_order_id, self-cross, a size or price the book will not take).
        # No order semantics change and no retry is added: placement behaviour
        # is identical, only the message grows.
        try:
            with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                body = exc.read().decode("utf-8", "replace")[:600]
            except Exception:                                    # noqa: BLE001
                body = "<body unreadable>"
            sent = {k: payload[k] for k in
                    ("ticker", "side", "count", "price", "post_only",
                     "time_in_force", "self_trade_prevention_type",
                     "client_order_id") if k in payload}
            raise urllib.error.HTTPError(
                exc.url, exc.code,
                f"{exc.reason} -- venue said: {body} -- we sent: {json.dumps(sent)}",
                exc.headers, None) from exc

    # ==================================================================
    # FLAT-11 (2026-09-09): THE POD COULD SELL, BUT ONLY AS A MAKER --
    # SO IT COULD STILL NEVER LEAVE A SWEPT MARKET.
    # ==================================================================
    # FLAT-1 gave the pod a close.  It gave it a POST-ONLY close: the payload
    # above hard-codes `post_only: True`, and placement_engine._flatten_price
    # cannot return a crossing price by construction (an explicit price at or
    # through the best bid of the held side is REFUSED there, and the derived
    # price joins the ask or leads the bid by a tick).  Against the books a
    # sweep leaves behind, that is a close that can never fill:
    #
    #   2026-09-09 17:5xZ, the FLAT-10 1-contract probe on
    #   KXKR-26SEPIDSALES-1.5 was placed at 4c -- JOINING the best YES ask,
    #   behind 13,275 contracts already resting there (book at the time:
    #   YES bids 1c x 1000 / 2c x 575 / 3c x 4,430; NO bid 96c x 13,275,
    #   i.e. the YES ask is 4c x 13,275).  ~200ct/day lift that level.  The
    #   probe cannot fill, so FLAT-10's close semantics can NEVER be
    #   verified, so the FLAT-10 cap can never lift, so the position can
    #   never be closed.  Two dead positions -- KXKR 294ct YES (cost
    #   $49.98) and KXSNOWCRABCATCH-26-NONE 138ct YES (cost $24.84) -- hold
    #   $74.82 of the $530 cap, three seats of LIP-earning capacity, in
    #   markets that will not pay us anything.
    #
    # MEASURED (scratchpad flatten_policy.md, 2026-09-09; 29 market-day
    # clusters, LIP era): for a fill whose HELD-SIDE COST is <= 20c, taker-
    # flatten immediately -- mean -$15.6/fill immediate vs -$25.5 hold,
    # difference -$9.9 (95% CI -19.4..-2.3, P(hold-imm <= 0) = 0.997).  For a
    # held cost > 20c, HOLD: hold +$10.5 vs immediate -$7.0.  Resting a close
    # at the entry price is dominated (-$3.2 vs immediate) and the 6-24h
    # window is the worst possible exit on every cut.  So the pod needs a
    # taker close for the cheap-fill leg, and only for it.
    #
    # THE RULE.  This primitive is the SAME reduce-only close as the one
    # above -- same live `fetch_position` read, same fail-closed behaviour
    # when that read is unreadable, same held-side match, same
    # `count <= abs(held)`, same 1..99c band, same forced `kfl-` client
    # order id, and the same per-market cap exemption (a close only REDUCES
    # exposure, so the $25 cap, the 90c acquire ceiling and the cheap-NO ban
    # -- all guards on capital going IN -- do not apply).  It differs in two
    # things only:
    #   * `post_only: False` plus `time_in_force: "immediate_or_cancel"`, so
    #     the order crosses into the resting bid and either fills now or
    #     dies.  IOC on this endpoint is a HYPOTHESIS (see the cancel-path
    #     receipt: a docs-derived field is a hypothesis until one live call
    #     confirms it), so a venue rejection that NAMES the field falls back
    #     once to good_till_canceled -- a crossing GTC order also fills
    #     immediately against a resting bid; the leftover, if any, rests.
    #     The fallback is reported in the response under `_tif`.
    #   * `allow_cross` must be passed True BY THE CALLER.  The wire never
    #     decides to cross on its own: crossing is a policy decision
    #     (kalshi.flatten.policy.allow_taker, ratified by Ryan) and the
    #     engine passes it down explicitly or this call raises.
    TAKER_TIME_IN_FORCE = "immediate_or_cancel"
    TAKER_TIME_IN_FORCE_FALLBACK = "good_till_canceled"

    def place_taker_close(
        self,
        ticker: str,
        held_side: str,
        sell_price_cents: int,
        count: int,
        client_order_id: str,
        allow_cross: bool = False,
    ) -> Dict[str, Any]:
        """Submit a REDUCE-ONLY close that CROSSES into the bid (a taker sale).

        `held_side` is the side we HOLD ("yes" / "no"); `sell_price_cents` is
        the price, in that side's own cents, we are willing to be paid -- for
        a taker close that is the best bid of the held side, not a tick above
        it.  V2 mapping is identical to place_post_only_close: selling held
        YES at p is side="ask" price=p; selling held NO at p is the same
        book's bid at (100-p).  `allow_cross` MUST be True: see FLAT-11.
        """
        if allow_cross is not True:
            raise ValueError(
                "place_taker_close refused: allow_cross must be passed True by the caller -- "
                "the wire never decides to cross a book on its own (FLAT-11); crossing is the "
                "kalshi.flatten.policy.allow_taker decision and the engine passes it down.")
        side = str(held_side).lower()
        if side not in ("yes", "no"):
            raise ValueError(f"place_taker_close: held_side must be 'yes' or 'no', got {held_side!r}")
        sell_c = int(sell_price_cents)
        if not 1 <= sell_c <= 99:
            raise ValueError(f"place_taker_close: sell price {sell_c}c outside 1..99c")
        cnt = float(count)
        if not cnt > 0:
            raise ValueError(f"place_taker_close: count must be > 0, got {count!r}")

        # THE GUARD, unchanged from the post-only close: never sell more than
        # the venue says we hold, read live, fail closed.  A close that
        # over-sells is an ACQUIRE of the other side wearing a close's
        # exemptions -- and a TAKER over-sell would fill instantly.
        try:
            pos = self.fetch_position(ticker)
        except Exception as exc:  # noqa: BLE001 -- any failure means we cannot prove what we hold
            raise ValueError(
                f"place_taker_close refused for {ticker}: live position unreadable "
                f"({type(exc).__name__}: {str(exc)[:140]}) -- cannot prove what is held, "
                f"fail closed.") from exc
        held_ct = float(pos["position_ct"])
        if side == "yes" and held_ct <= 0:
            raise ValueError(
                f"place_taker_close refused for {ticker}: venue shows {held_ct:+.0f}ct, "
                f"no YES held to sell (fail closed).")
        if side == "no" and held_ct >= 0:
            raise ValueError(
                f"place_taker_close refused for {ticker}: venue shows {held_ct:+.0f}ct, "
                f"no NO held to sell (fail closed).")
        if cnt > abs(held_ct) + 1e-9:
            raise ValueError(
                f"place_taker_close refused for {ticker}: count {cnt:.0f} exceeds held "
                f"{abs(held_ct):.0f}ct -- a close may only reduce, never flip, a position.")

        coid = str(client_order_id)
        if not coid.startswith(self.CLOSE_CLIENT_ORDER_PREFIX):
            coid = self.CLOSE_CLIENT_ORDER_PREFIX + coid

        bare_path = f"{TRADE_API_PREFIX}/portfolio/events/orders"
        url = f"{self.base_url}{bare_path}"

        if side == "yes":
            v2_side, v2_price_c = "ask", sell_c
        else:
            v2_side, v2_price_c = "bid", 100 - sell_c

        def _payload(tif: str) -> Dict[str, Any]:
            return {
                "ticker": ticker,
                "side": v2_side,
                "count": f"{cnt:.2f}",
                "price": f"{v2_price_c / 100.0:.4f}",
                "time_in_force": tif,
                # the same STP value the accepted close payload carries; a
                # taker close never invents an enum this repo has not seen
                # the venue accept.
                "self_trade_prevention_type": "maker",
                "post_only": False,
                "client_order_id": coid,
            }

        def _post(tif: str) -> Dict[str, Any]:
            headers = self._sign_headers("POST", bare_path)
            data_bytes = json.dumps(_payload(tif)).encode("utf-8")
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
                out = json.loads(resp.read().decode("utf-8"))
            if isinstance(out, dict):
                out["_tif"] = tif
            return out

        try:
            return _post(self.TAKER_TIME_IN_FORCE)
        except urllib.error.HTTPError as exc:
            # Only a rejection that NAMES the time-in-force field falls back;
            # anything else (auth, cap, a bad price) is the venue telling us
            # something real and is raised.
            body = ""
            try:
                body = exc.read().decode("utf-8", "replace")[:400]
            except Exception:  # noqa: BLE001
                body = ""
            blob = f"{getattr(exc, 'code', '')} {body}".lower()
            if getattr(exc, "code", None) in (400, 422) and (
                    "time_in_force" in blob or "immediate_or_cancel" in blob or "tif" in blob):
                return _post(self.TAKER_TIME_IN_FORCE_FALLBACK)
            raise

    # ==================================================================
    # CAP-4 (2026-09-05): THE WIRE'S CAP WAS PER-ORDER AND STATELESS
    # ==================================================================
    # Ryan, verbatim: "never to have more than 25$ in any market" -- resting
    # orders AND open positions, per ticker.  Until today the last check
    # before the POST (below) and the broker's twin (senate/harness/
    # order_broker.validate_order_intent) looked at THIS ORDER's notional
    # only.  Two $25 orders on one ticker passed both.  A $25 order on a
    # ticker already holding a $25 position (KXSNOWCRABCATCH, filled 09-03,
    # never flattened) passed both.  The broker's token budget is a SESSION
    # budget, not a per-market one, and the placement engine never routes
    # through it -- placement_engine._place_qualified calls
    # place_post_only_order directly -- so the broker guarded only the
    # manual CLI `--live` path.  Every upstream gate (invariants, _qualify,
    # CAP-2's venue_same_ticker_usd) reads state that was fetched earlier in
    # the cycle; the wire is the one place that can read the venue AT THE
    # INSTANT OF THE POST.
    #
    # THE RULE.  Before the payload is built, read the venue's own resting
    # orders and position for this ticker, and refuse when
    #     this order + same-ticker resting collateral + same-ticker
    #     position cost  >  PER_MARKET_HARD_USD.
    # Both reads FAIL CLOSED: a transport/auth failure, an exhausted 429
    # budget, or a same-ticker row whose price/count/cost cannot be parsed
    # means the ticker's exposure cannot be proven and the order is refused.
    # Only a venue-confirmed 429 is retried (call_with_rate_limit_retry,
    # ~2.5 s worst case), because a 429 is our own lanes' contention, not
    # data.  A position that holds contracts but reports no readable cost
    # counts as the FULL cap -- unknown exposure is not zero exposure.
    #
    # ACK-LAG (2026-09-11) -- THE EXCLUSION THIS BLOCK USED TO REFUSE.
    # The original receipt here reasoned that the wire reads AFTER the cancel
    # is acked, "so the released order is already absent", and priced a venue
    # lag at "one cycle of lost LIP".  Both halves were wrong in production.
    # The venue's open-orders LISTING lags its own cancel ACK essentially every
    # time at the ~100-250 ms gap between our cancel ack and our place, so the
    # just-cancelled $24.84 was still listed, $24.84 + $24.84 > $25, and the
    # replacement was refused.  Measured off queue_shield_run.log (unique
    # order ids, kind ATOMIC_CASH_AFTER_CANCEL, why "... already in <T> on the
    # venue"): onset 2026-09-05T23:34Z, the day CAP-4 shipped; 2026-09-10 alone
    # turned 279 live seats into cash against 380 clean replaces -- 42 % of
    # every cancel-then-place.  And "one cycle" was not the price either: a
    # seat that goes to cash re-enters only if its market is still inside the
    # entry band and armor at the next reconcile, which is how the book read
    # 15/20 at 00:53Z.
    #
    # THE RULE NOW.  The caller may name ONE order it has just watched the
    # venue ACK as cancelled (`cancel_acked_order_id`).  That order's RESTING
    # collateral is excluded from the same-ticker sum, and nothing else is:
    #   * a cancel ACK means the matching engine has removed the order -- it
    #     cannot fill afterwards; only the read-side listing is behind;
    #   * any contracts it filled BEFORE the cancel are in the POSITION, which
    #     is still read and still counted in full (opaque cost = full cap);
    #   * every OTHER listed order on the ticker still counts, so a genuine
    #     second live order is refused exactly as before;
    #   * the id comes only from the engine's two atomic paths, each of which
    #     passes it strictly after its own cancel returned success
    #     (tests/test_ack_lag_replace.py pins both call sites and the lag).
    # With no id passed the check is byte-for-byte the CAP-4 check.
    #
    # The close paths (place_post_only_close, place_taker_close) are exempt:
    # a close REDUCES exposure and carries its own guard (count <= held).
    ORDER_COUNT_KEYS = ("remaining_count_fp", "remaining_count", "count")

    @staticmethod
    def _resting_order_price_cents(o: Dict[str, Any]) -> Optional[int]:
        """Price in cents of the HELD outcome side of a venue order row.  Same
        key logic as placement_engine._order_price_cents (kept in lock-step by
        tests/test_wire_same_ticker_cap.py); None = unreadable."""
        side = str(o.get("outcome_side") or o.get("side") or "").lower()
        for key, scale in ((f"{side}_price", 1), (f"{side}_price_dollars", 100), ("price", 1)):
            v = o.get(key)
            if v is not None:
                try:
                    return int(round(float(v) * scale))
                except (TypeError, ValueError):
                    continue
        return None

    @classmethod
    def _resting_order_count(cls, o: Dict[str, Any]) -> Optional[int]:
        for k in cls.ORDER_COUNT_KEYS:
            if o.get(k) is not None:
                try:
                    return int(float(o[k]))
                except (TypeError, ValueError):
                    continue
        return None

    def venue_committed_usd(self, ticker: str,
                            cancel_acked_order_id: Optional[str] = None) -> Dict[str, Any]:
        """Dollars the venue says are ALREADY in `ticker` at this instant:
        every resting order on it plus the cost of any open position.

        Returns {usd, orders_usd, n_orders, position_ct, position_usd,
        opaque, detail}.  RAISES (so the caller fails closed) when either
        feed is unreadable or a same-ticker row cannot be parsed.
        """
        tk = str(ticker)
        res = call_with_rate_limit_retry(self.fetch_open_orders, sleep_fn=time.sleep)
        if not res["ok"]:
            raise ValueError(
                f"resting orders unreadable for {tk} ({rate_limit_note(res)})")
        orders_usd = 0.0
        n_orders = 0
        acked_usd = 0.0
        n_acked = 0
        for o in res["value"] or []:
            if str(o.get("ticker")) != tk:
                continue
            if cancel_acked_order_id and str(o.get("order_id")) == str(cancel_acked_order_id):
                # ACK-LAG: the venue acked this cancel; its listing is behind.
                # Parsed only for the audit line -- an unreadable row is not a
                # reason to refuse, because the order is already gone.
                px_a = self._resting_order_price_cents(o)
                ct_a = self._resting_order_count(o)
                if px_a is not None and ct_a is not None:
                    acked_usd += round(px_a / 100.0 * ct_a, 2)
                n_acked += 1
                continue
            px = self._resting_order_price_cents(o)
            ct = self._resting_order_count(o)
            if px is None or ct is None:
                raise ValueError(
                    f"resting order {o.get('order_id')!r} on {tk} carries no readable "
                    f"price/count (keys={sorted(o.keys())})")
            orders_usd += round(px / 100.0 * ct, 2)
            n_orders += 1
        pos = self.fetch_position(tk)  # raises on transport failure or an unreadable row
        position_ct = float(pos["position_ct"])
        exposure = pos["exposure_usd"]
        opaque = False
        position_usd = 0.0
        if position_ct != 0.0 or exposure:
            if exposure is None:
                opaque = True
                position_usd = PER_MARKET_HARD_USD
            else:
                position_usd = float(exposure)
        total = round(orders_usd + position_usd, 2)
        detail = (f"{n_orders} resting order(s) ${orders_usd:.2f} + position "
                  f"{position_ct:+.0f}ct ${position_usd:.2f}"
                  + (" [cost unreadable -> counted as full cap]" if opaque else "")
                  + (f" [excluded {n_acked} cancel-ACKED order ${acked_usd:.2f} "
                     f"({cancel_acked_order_id}): venue listing lags its own ack]"
                     if n_acked else ""))
        return {"usd": total, "orders_usd": round(orders_usd, 2), "n_orders": n_orders,
                "position_ct": position_ct, "position_usd": round(position_usd, 2),
                "opaque": opaque, "detail": detail,
                "acked_excluded_usd": round(acked_usd, 2), "n_acked_excluded": n_acked}

    def place_post_only_order(
        self,
        ticker: str,
        side: str,
        price_cents: int,
        count: int,
        client_order_id: str,
        cancel_acked_order_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submit post-only maker limit order to Kalshi.

        cancel_acked_order_id: the ONE order the caller has just seen the venue
        ACK as cancelled, whose stale listing must not count against this
        order's per-market cap.  See ACK-LAG above venue_committed_usd."""
        cnt = float(count)
        acquire_c = int(price_cents)
        cost_usd = round((acquire_c / 100.0) * cnt, 2)

        # LAST LINE (2026-09-05): was `> 50.01`.  Every upstream gate had $50
        # too, so a $50 seat reached the wire and was swept (KXKR, 09-05).
        # Ryan: "never to have more than 25$ in any market".  This check is
        # the wire's own, independent of any fact or plan row.
        if cost_usd > PER_MARKET_HARD_USD + 0.01:
            raise ValueError(f"SENATE INVARIANT BREACH: Order cost ${cost_usd:.2f} exceeds ${PER_MARKET_HARD_USD:.2f} single-market cap.")
        if acquire_c >= 90:
            raise ValueError(f"SENATE INVARIANT BREACH: Acquire price {acquire_c}c >= 90c strictly prohibited (asymmetric negative-EV trap).")
        tk_upper = str(ticker).upper()
        if side.lower() == "no" and acquire_c <= 35 and ("BALLOT" in tk_upper or "BOND" in tk_upper or "FUND" in tk_upper):
            raise ValueError(f"SENATE INVARIANT BREACH: Selling cheap NO at {acquire_c}c on high-probability measure '{ticker}' prohibited.")

        # CAP-4 (2026-09-05): this order PLUS what the venue already holds
        # in this ticker.  See the receipt above venue_committed_usd.  Any
        # read failure refuses -- fail closed at the wire.
        try:
            committed = (self.venue_committed_usd(ticker) if not cancel_acked_order_id
                         else self.venue_committed_usd(
                             ticker, cancel_acked_order_id=cancel_acked_order_id))
        except Exception as exc:  # noqa: BLE001 -- unprovable exposure is refused
            raise ValueError(
                f"SENATE INVARIANT BREACH: same-ticker exposure for {ticker} unreadable "
                f"({type(exc).__name__}: {str(exc)[:160]}) -- cannot prove the "
                f"${PER_MARKET_HARD_USD:.2f} per-market cap holds, fail closed.") from exc
        if cost_usd + committed["usd"] > PER_MARKET_HARD_USD + 0.005:
            raise ValueError(
                f"SENATE INVARIANT BREACH: Order cost ${cost_usd:.2f} + ${committed['usd']:.2f} "
                f"already in {ticker} on the venue ({committed['detail']}) exceeds "
                f"${PER_MARKET_HARD_USD:.2f} single-market cap (orders AND positions, per ticker).")

        # CreateOrder V2 (the legacy /portfolio/orders POST was removed June 2026,
        # returns HTTP 410 Gone — verified live 2026-08-17). V2 uses single-book
        # YES-leg semantics: a YES bid at p is side="bid" price=p; a NO bid at p
        # is the same book's ask at (100-p). Prices/counts are fixed-point
        # dollar strings.
        bare_path = f"{TRADE_API_PREFIX}/portfolio/events/orders"
        url = f"{self.base_url}{bare_path}"
        headers = self._sign_headers("POST", bare_path)

        if side.lower() == "yes":
            v2_side, v2_price_c = "bid", acquire_c
        else:
            v2_side, v2_price_c = "ask", 100 - acquire_c
        payload = {
            "ticker": ticker,
            "side": v2_side,
            "count": f"{cnt:.2f}",
            "price": f"{v2_price_c / 100.0:.4f}",
            "time_in_force": "good_till_canceled",
            "self_trade_prevention_type": "maker",
            "post_only": True,
            "client_order_id": client_order_id,
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
        # WIRE-1 (2026-09-10): NEVER SWALLOW THE VENUE'S OWN EXPLANATION.
        #
        # THE INCIDENT.  Between 07:05Z and 07:33Z the book fell 17 -> 4 seats
        # ($423 -> $99.55 escrow) because EIGHT re-placements in a row were
        # refused by the exchange.  Every one logged exactly this and no more:
        #     "NOT placed - venue placement failed: HTTP Error 409: Conflict"
        # urllib's HTTPError carries the response BODY and Kalshi puts the
        # machine-readable reason in it -- but the body is readable only off
        # the exception object, and letting the error propagate untouched threw
        # it away.  The pod could see the venue say no eight times and could not
        # see WHY once.  A refusal we cannot read is a refusal we cannot fix.
        #
        # Re-raises the SAME exception class carrying the status line, the body,
        # and the payload we sent -- a 409 is ABOUT the payload (duplicate
        # client_order_id, self-cross, a size or price the book will not take).
        # No order semantics change and no retry is added: placement behaviour
        # is identical, only the message grows.
        try:
            with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                body = exc.read().decode("utf-8", "replace")[:600]
            except Exception:                                    # noqa: BLE001
                body = "<body unreadable>"
            sent = {k: payload[k] for k in
                    ("ticker", "side", "count", "price", "post_only",
                     "time_in_force", "self_trade_prevention_type",
                     "client_order_id") if k in payload}
            raise urllib.error.HTTPError(
                exc.url, exc.code,
                f"{exc.reason} -- venue said: {body} -- we sent: {json.dumps(sent)}",
                exc.headers, None) from exc


    # DELETE templates, correct-first.  Kept as templates (not formatted paths)
    # so the learned "this one works" hint can be an index into a stable list.
    CANCEL_PATH_TEMPLATES = (
        TRADE_API_PREFIX + "/portfolio/events/orders/{oid}",  # CancelOrder V2 (correct)
        TRADE_API_PREFIX + "/orders/{oid}",                   # 404 as of 2026-08-18
        TRADE_API_PREFIX + "/portfolio/orders/{oid}",         # 410 Gone as of 2026-08-18
    )

    def cancel_order(
        self,
        order_id: str,
        deadline_s: Optional[float] = None,
        request_timeout_s: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Cancel an existing order on Kalshi.

        2026-08-18 INCIDENT: the docs' V2 cancel path (/trade-api/v2/orders/{id})
        returns HTTP 404 against the live venue.  It was adopted from the docs
        without an empirical test and it broke the DEFENSIVE path — the queue
        shield's first live withdrawal failed, leaving the shield believing it
        was flat while the order was still resting.  A defensive action must
        never depend on one unverified endpoint: try both, legacy last, and
        raise only if BOTH fail.

        2026-08-18T03:07Z SECOND LIVE FAILURE: the shield alarmed on
        KXYELLVISITS, the cancel-first fast path engaged correctly (1082ms
        alarm->cancel), and BOTH paths then known failed — /orders/{id} with 404
        and /portfolio/orders/{id} with 410 Gone.  The real CancelOrder V2 path
        MIRRORS CreateOrder V2 (POST /portfolio/events/orders):
            DELETE /trade-api/v2/portfolio/events/orders/{order_id}
        Ordered correct-first so the working path is tried before the two
        known-dead ones, which are retained only as fallbacks in case the venue
        rolls back.

        2026-08-18T13:42Z THIRD INCIDENT — 1971 ms.  See the module header note
        (`THE DEFENSIVE CANCEL MUST NOT PAY FOR ENDPOINT ARCHAEOLOGY`).  The
        fallback loop is now gated on the ONLY evidence that can justify it:
        a 404/405/410/501 answer, which is the venue saying this URL shape is
        not served.  Any other failure — timeout, reset, TLS, 5xx, 429 — raises
        CancelPathTransientError IMMEDIATELY, without touring the two dead
        endpoints, so a LIVE order's defensive cancel is never delayed by
        probing that could not have helped it.  The whole call is additionally
        capped by `deadline_s`, and each request by `request_timeout_s`.
        """
        budget = CANCEL_TOTAL_BUDGET_SEC if deadline_s is None else float(deadline_s)
        per_request = (CANCEL_REQUEST_TIMEOUT_SEC if request_timeout_s is None
                       else float(request_timeout_s))
        started = time.monotonic()

        templates = list(self.CANCEL_PATH_TEMPLATES)
        order = list(range(len(templates)))
        # THE LEARNED PATH.  If the venue ever rolls back, the first cancel pays
        # for the probe and every cancel after it goes straight to the endpoint
        # that answered.  Absent a hint the preregistered correct-first order is
        # used unchanged, so the healthy venue still costs exactly one DELETE.
        hint = getattr(self, "_cancel_path_idx", None)
        if isinstance(hint, int) and 0 <= hint < len(templates):
            order.remove(hint)
            order.insert(0, hint)

        last_err: Optional[BaseException] = None
        tried: List[str] = []
        for n, idx in enumerate(order):
            bare_path = templates[idx].format(oid=order_id)
            remaining = budget - (time.monotonic() - started)
            if n and remaining <= 0:
                raise RuntimeError(
                    f"cancel_order exhausted its {budget:.1f}s budget for {order_id} "
                    f"after {tried}: {last_err}")
            # The first attempt always gets the full per-request timeout; later
            # probes get whatever is left of the budget, never more.
            timeout = per_request if n == 0 else max(0.5, min(per_request, remaining))
            tried.append(bare_path)
            try:
                url = f"{self.base_url}{bare_path}"
                headers = self._sign_headers("DELETE", bare_path)
                req = urllib.request.Request(url, headers=headers, method="DELETE")
                with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=timeout) as resp:
                    body = resp.read().decode("utf-8")
                    self._cancel_path_idx = idx
                    return json.loads(body) if body.strip() else {"ok": True, "path": bare_path}
            except Exception as exc:  # noqa: BLE001 - classified, then re-reported
                last_err = exc
                if not is_endpoint_shaped_failure(exc):
                    # NOT evidence about the endpoint.  Probing the remaining
                    # candidates cannot cancel this order and, if the order is
                    # LIVE, every millisecond spent doing so is naked exposure.
                    raise CancelPathTransientError(
                        f"cancel_order aborted for {order_id}: {bare_path} failed "
                        f"transiently ({type(exc).__name__}: {str(exc)[:140]}). The "
                        f"remaining candidate paths are empirically dead (404/410) "
                        f"and cannot fix a transient failure — retry THIS path "
                        f"instead of delaying a possibly-live order's cancel.",
                        cause=exc, path=bare_path) from exc
                continue
        raise RuntimeError(
            f"cancel_order failed on all paths for {order_id} (tried {tried}): {last_err}")
