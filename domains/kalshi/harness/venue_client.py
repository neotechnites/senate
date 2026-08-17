"""Authentic Kalshi Trade API v2 Client for Kalshi Domain Pod."""

import base64
import json
import os
import ssl
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = "https://api.elections.kalshi.com"
TRADE_API_PREFIX = "/trade-api/v2"


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

    def fetch_positions(self) -> List[Dict[str, Any]]:
        """Fetch all settled/active market positions for this account."""
        bare_path = f"{TRADE_API_PREFIX}/portfolio/positions"
        url = f"{self.base_url}{bare_path}"
        headers = self._sign_headers("GET", bare_path)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("market_positions", [])

    def place_post_only_order(
        self,
        ticker: str,
        side: str,
        price_cents: int,
        count: int,
        client_order_id: str,
    ) -> Dict[str, Any]:
        """Submit post-only maker limit order to Kalshi."""
        cnt = float(count)
        acquire_c = int(price_cents)
        cost_usd = round((acquire_c / 100.0) * cnt, 2)

        if cost_usd > 50.01:
            raise ValueError(f"SENATE INVARIANT BREACH: Order cost ${cost_usd:.2f} exceeds $50.00 single-market cap.")
        if acquire_c >= 90:
            raise ValueError(f"SENATE INVARIANT BREACH: Acquire price {acquire_c}c >= 90c strictly prohibited (asymmetric negative-EV trap).")
        tk_upper = str(ticker).upper()
        if side.lower() == "no" and acquire_c <= 35 and ("BALLOT" in tk_upper or "BOND" in tk_upper or "FUND" in tk_upper):
            raise ValueError(f"SENATE INVARIANT BREACH: Selling cheap NO at {acquire_c}c on high-probability measure '{ticker}' prohibited.")

        bare_path = f"{TRADE_API_PREFIX}/portfolio/orders"
        url = f"{self.base_url}{bare_path}"
        headers = self._sign_headers("POST", bare_path)

        payload = {
            "ticker": ticker,
            "action": "buy",
            "type": "limit",
            "side": side.lower(),
            "count": count,
            "yes_price": price_cents if side.lower() == "yes" else 100 - price_cents,
            "post_only": True,
            "client_order_id": client_order_id,
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
        with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))


    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an existing order on Kalshi."""
        bare_path = f"{TRADE_API_PREFIX}/portfolio/orders/{order_id}"
        url = f"{self.base_url}{bare_path}"
        headers = self._sign_headers("DELETE", bare_path)
        req = urllib.request.Request(url, headers=headers, method="DELETE")
        with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
