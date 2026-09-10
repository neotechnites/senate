#!/usr/bin/env python3
"""Steward transport daemon.

Two jobs, no judgement:
  1. Capture every message Ryan sends to @neoSteward_bot into `conversation`.
  2. Deliver messages the Steward head has queued in `outbox`, honouring quiet hours.

It NEVER composes a message and NEVER closes an obligation. Judgement lives with
the head; this process is the wire.
"""
import json, sqlite3, time, urllib.parse, urllib.request, sys, os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

HOME = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HOME, "data", "steward.db")
CFG = os.path.join(HOME, "data", "telegram.json")
TZ = ZoneInfo("America/Denver")
QUIET_START, QUIET_END = 22, 8          # local hours; emergencies only

cfg = json.load(open(CFG))
TOKEN, CHAT_ID = cfg["bot_token"], int(cfg["chat_id"])
API = f"https://api.telegram.org/bot{TOKEN}/"


def log(msg):
    print(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {msg}", flush=True)


def api(method, params=None, timeout=60):
    url = API + method
    data = urllib.parse.urlencode(params or {}).encode() if params else None
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        log(f"api {method} failed: {e}")
        return {"ok": False, "error": str(e)}


def db():
    c = sqlite3.connect(DB, timeout=30)
    c.execute("PRAGMA journal_mode=WAL")
    return c


def ensure_schema():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS outbox (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            obligation_id INTEGER,
            urgent INTEGER DEFAULT 0,          -- 1 bypasses quiet hours
            queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_at TIMESTAMP,
            telegram_message_id INTEGER,
            error TEXT DEFAULT ''
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS daemon_state (
            key TEXT PRIMARY KEY, value TEXT NOT NULL
        )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_outbox_pending ON outbox(sent_at, id)")


def get_state(k, default=None):
    with db() as c:
        r = c.execute("SELECT value FROM daemon_state WHERE key=?", (k,)).fetchone()
    return r[0] if r else default


def set_state(k, v):
    with db() as c:
        c.execute("INSERT OR REPLACE INTO daemon_state (key,value) VALUES (?,?)", (k, str(v)))


def quiet_now():
    h = datetime.now(TZ).hour
    return h >= QUIET_START or h < QUIET_END


def pull():
    off = get_state("tg_offset")
    p = {"timeout": 50}
    if off:
        p["offset"] = int(off) + 1
    r = api("getUpdates", p, timeout=70)
    if not r.get("ok"):
        time.sleep(5)
        return
    for u in r.get("result", []):
        set_state("tg_offset", u["update_id"])
        m = u.get("message") or u.get("edited_message")
        if not m or m.get("chat", {}).get("id") != CHAT_ID:
            continue
        text = m.get("text") or m.get("caption") or f"[non-text: {list(m.keys())}]"
        at = datetime.fromtimestamp(m["date"], timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        with db() as c:
            c.execute("INSERT INTO conversation (at, direction, channel, text) VALUES (?,?,?,?)",
                      (at, "FROM_RYAN", "telegram", text))
        log(f"IN  {text[:80]!r}")


def push():
    with db() as c:
        rows = c.execute("SELECT id,text,obligation_id,urgent FROM outbox "
                         "WHERE sent_at IS NULL ORDER BY id").fetchall()
    for oid, text, ob, urgent in rows:
        if quiet_now() and not urgent:
            continue                                  # hold until 08:00 local
        r = api("sendMessage", {"chat_id": CHAT_ID, "text": text})
        with db() as c:
            if r.get("ok"):
                mid = r["result"]["message_id"]
                c.execute("UPDATE outbox SET sent_at=CURRENT_TIMESTAMP, telegram_message_id=? WHERE id=?", (mid, oid))
                c.execute("INSERT INTO conversation (direction,channel,text,obligation_id) VALUES (?,?,?,?)",
                          ("TO_RYAN", "telegram", text, ob))
                log(f"OUT {text[:80]!r}")
            else:
                c.execute("UPDATE outbox SET error=? WHERE id=?", (str(r)[:400], oid))
                log(f"OUT FAILED id={oid}: {r}")


def main():
    ensure_schema()
    log(f"steward daemon up; db={DB} chat={CHAT_ID} tz={TZ}")
    set_state("started_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    while True:
        try:
            set_state("heartbeat", datetime.now(timezone.utc).isoformat(timespec="seconds"))
            push()
            pull()
        except Exception as e:
            log(f"loop error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
