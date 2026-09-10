#!/usr/bin/env bash
# Keep the game repo identical on the Mac, the PC and GitHub.
#
# Ryan's rule, 2026-09-09: "every change that happens should be commited, and
# pulled down by whatever computer doesnt have it. i want it all to always stay
# in sync."
#
# The PC clone is set receive.denyCurrentBranch=updateInstead, so a push from
# here updates its WORKING TREE, not just its refs -- the Play shortcut on the
# desktop is current the instant this finishes.
#
# Usage:  sync.sh "commit message"     commit everything, push both ways
#         sync.sh --check              report drift, change nothing
set -euo pipefail

REPO="$HOME/Documents/olympus/panopticon"
cd "$REPO"

echo "== fetching the PC first: it may have commits this Mac has never seen =="
git fetch pc main 2>&1 | tail -2 || echo "   PC unreachable -- is Tailscale up?"

PC_HEAD="$(git rev-parse FETCH_HEAD 2>/dev/null || echo none)"
MINE="$(git rev-parse HEAD)"
if [ "$PC_HEAD" != "none" ] && [ "$PC_HEAD" != "$MINE" ] && \
   ! git merge-base --is-ancestor "$PC_HEAD" HEAD 2>/dev/null; then
    echo "!! The PC has work this Mac does not. Merge it before pushing:"
    echo "   git -C $REPO merge $PC_HEAD"
    exit 1
fi

if [ "${1:-}" = "--check" ]; then
    echo "== drift report =="
    echo "   mac:    $MINE"
    echo "   pc:     $PC_HEAD"
    echo "   github: $(git rev-parse origin/main 2>/dev/null || echo unknown)"
    echo "   uncommitted here: $(git status --porcelain | wc -l | tr -d ' ') files"
    exit 0
fi

MSG="${1:?usage: sync.sh \"commit message\"}"

if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -q -m "$MSG

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01XQcaRV7xNKbCLiSVFznt6T"
    echo "== committed: $(git rev-parse --short HEAD) =="
else
    echo "== nothing to commit; syncing existing history =="
fi

echo "== push -> GitHub =="
git push origin main 2>&1 | tail -2
echo "== push -> PC (updates its working tree) =="
git push pc main 2>&1 | tail -2

echo "== final state =="
echo "   mac:    $(git rev-parse --short HEAD)"
echo "   github: $(git rev-parse --short origin/main)"
echo "   pc:     $(git rev-parse --short "$(git fetch pc main >/dev/null 2>&1; git rev-parse FETCH_HEAD)")"
