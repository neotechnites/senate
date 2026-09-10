#!/usr/bin/env bash
# Install + enable the Steward head wake timer on the VPS.
set -euo pipefail
K=~/.ssh/senate_vps_ed25519
H=ubuntu@129.146.115.241
D="$(cd "$(dirname "$0")" && pwd)"

echo "shipping..."
scp -i "$K" -q "$D/wake.sh" "$D/steward-wake.service" "$D/steward-wake.timer" "$H:/tmp/"

echo "installing..."
ssh -i "$K" "$H" bash -s <<'REMOTE'
set -euo pipefail
sudo install -o steward -g steward -m 750 /tmp/wake.sh /home/steward/steward/wake.sh
sudo install -o root -g root -m 644 /tmp/steward-wake.service /etc/systemd/system/steward-wake.service
sudo install -o root -g root -m 644 /tmp/steward-wake.timer   /etc/systemd/system/steward-wake.timer
rm -f /tmp/wake.sh /tmp/steward-wake.service /tmp/steward-wake.timer
sudo systemctl daemon-reload
sudo systemctl enable --now steward-wake.timer
echo "--- timer ---"
systemctl list-timers steward-wake --no-pager --no-legend
echo "--- transport ---"
systemctl is-active steward
echo "--- kalshi unchanged? ---"
for s in nestor autoseat competition-recorder lipband-capture; do
  printf "%s %s mainpid=%s\n" "$s" "$(systemctl is-active $s)" "$(systemctl show -p MainPID --value $s)"
done
echo "crontab md5=$(crontab -l 2>/dev/null | md5sum | cut -c1-12)"
REMOTE
echo "DONE"
