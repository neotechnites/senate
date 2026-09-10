#!/usr/bin/env bash
# Talk to the CANONICAL steward DB on the VPS. The local data/steward.db is a seed
# copy only and is no longer authoritative.
#   ./remote.sh sql "SELECT * FROM obligations;"     -- query/modify the live DB
#   ./remote.sh say "text"                           -- queue a message to Ryan
#   ./remote.sh log                                  -- tail the daemon log
#   ./remote.sh health                               -- service + heartbeat
set -euo pipefail
K=~/.ssh/senate_vps_ed25519; H=ubuntu@129.146.115.241
DB=/home/steward/steward/data/steward.db
r() { ssh -i $K -o BatchMode=yes $H "$@"; }
case "${1:-health}" in
  sql)  r "sudo -u steward sqlite3 -header $DB \"${2}\"" ;;
  say)  r "sudo -u steward sqlite3 $DB \"INSERT INTO outbox (text) VALUES ('$(printf '%s' "$2" | sed "s/'/''/g")');\"" && echo queued ;;
  log)  r "sudo tail -${2:-30} /home/steward/steward/logs/daemon.log" ;;
  health) r "systemctl is-active steward; sudo -u steward sqlite3 $DB \"SELECT key||'='||value FROM daemon_state;\"" ;;
  *) echo "usage: $0 {sql|say|log|health}"; exit 1 ;;
esac
