# PANOPTICON — Windows 10 PC setup
### The goal: Ryan plays on the PC, the head edits from the Mac, changes flow both ways.

Everything below is one session. Skip Astra and Blender.

---

## PART 0 — How to open an Administrator PowerShell

You need this for Part 1. A normal PowerShell will fail those commands with "Access is denied".

**Windows Search is broken on this machine** (has been since the drive clone), so none of
these routes use it.

**Route 1, best:** press **Win+X** (or right-click the Start button). A menu appears. Click
**Windows PowerShell (Admin)**. Click **Yes** on the prompt.

**Route 2:** press **Win+R**, type `powershell`, then press **Ctrl+Shift+Enter** instead of
Enter — that combination means "run as administrator".

**Route 3, if both fail:** press **Ctrl+Shift+Esc** for Task Manager. If it looks small, click
**More details**. Then **File**, **Run new task**, type `powershell`, tick **Create this task
with administrative privileges**, click OK.

Whichever you use, check the title bar says **Administrator: Windows PowerShell**. If it does
not, you are in a normal shell and Part 1 will fail with "Access is denied".

For Part 2, use **Win+X** then **Windows PowerShell** (the entry without "(Admin)"), or Win+R
and plain Enter.

---

## PART 1 — run these in the Administrator PowerShell

### 1. Stop the machine sleeping
The PC being always on is what makes the 60 remote hours usable.
```powershell
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change monitor-timeout-ac 15
```

### 2. OpenSSH Server — this is what lets the head reach the PC
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
New-NetFirewallRule -Name sshd -DisplayName "OpenSSH Server" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```
Make PowerShell the shell an SSH session gets, or remote commands behave oddly:
```powershell
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell `
  -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force
```

### 3. Tailscale
```powershell
winget install --id tailscale.tailscale -e
```
Then run `tailscale up`, sign in with the SAME account as the Mac. Note the machine name it reports.

---

## PART 2 — Normal PowerShell (no admin)

### 4. Git
```powershell
winget install --id Git.Git -e
```
Close and reopen PowerShell so PATH updates. Then:
```powershell
git config --global core.autocrlf false
git config --global init.defaultBranch main
```
`core.autocrlf false` matters: the repo's .gitattributes already normalises line endings, and
autocrlf on top of it makes every file look modified the moment it crosses machines.

### 5. Godot 4.7.2 — the EXACT version, not winget
winget will install whatever it has. The version must match `.godot-version` character for
character; a mismatch silently rewrites project.godot and can one-way upgrade scene formats.

- Download `Godot_v4.7.2-stable_win64.exe.zip` from https://godotengine.org/download/archive/
- Extract to `C:\tools\godot\`
- Rename the exe to `godot.exe`
**Extracting it:** right-click the downloaded .zip, choose **Extract All**, set the
destination to `C:\tools\godot`, click Extract. Inside you will find one .exe with a long
name — rename it to exactly `godot.exe`.

**Putting it on PATH**, which is what lets you type `godot` from any folder. Do it from
PowerShell rather than the GUI — no search, no dialogs, and it is exact:
```powershell
$old = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$old;C:\tools\godot", "User")
```
Then **close PowerShell entirely and open a new one** — PATH is only read at startup.

(If you ever do want the GUI without search: **Win+R**, then
`rundll32 sysdm.cpl,EditEnvironmentVariables`.)

Then check:
```powershell
godot --version
```
It must print exactly `4.7.2.stable.official.ed1daf0bf`. Anything else and stop.

### 6. An SSH key for neotechnites
The Mac's key is not on this machine, and this is a PERSONAL project — it must not touch the
Stack Integrated account.
```powershell
ssh-keygen -t ed25519 -C "neotechnites-pc" -f $env:USERPROFILE\.ssh\id_ed25519
```
It asks for a passphrase twice. **Press Enter both times** to leave it empty, otherwise every
push will prompt you and unattended runs will hang.

Now copy the PUBLIC key straight to the clipboard — do not try to select it out of the
terminal, PowerShell will wrap it and a wrapped key is a broken key:
```powershell
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | clip
```

Then in the browser:
1. Make sure you are signed in as **neotechnites**, not RyanStackIntegrated. Click your avatar
   top-right and read the username. If it is the work account, sign out or use the browser
   profile where neotechnites is signed in.
2. Go to **github.com/settings/keys**.
3. Click **New SSH key**.
4. Title: `panopticon PC`. Key type: leave as Authentication Key.
5. Click in the Key box and press **Ctrl+V**.
6. Click **Add SSH key**.

Test it:
```powershell
ssh -T git@github.com
```
It must say `Hi neotechnites!`. If it says any other name, stop — the wrong account is in play.

### 7. Clone the game
```powershell
mkdir C:\dev; cd C:\dev
git clone git@github.com:neotechnites/panopticon.git
cd panopticon
git config user.name "Ryan"
git config user.email "ryan@olympus.local"
```
That identity matters: commits must not be stamped with the work address.

### 8. Claude Code, so you can talk to the head from this machine
Install from https://claude.ai/download (native Windows installer — it auto-updates, which the
npm and winget routes do not).

---

## PART 3 — Verify, in order

```powershell
cd C:\dev\panopticon
godot --version                                               # 4.7.2.stable.official.ed1daf0bf
godot --headless --import --path .                            # exit 0, no errors
godot --headless --path . --script res://tools/run_tests.gd   # PASS 21 tests, 347 checks
godot --headless --path . --script res://tools/harness/run_bot_match.gd -- --matches=2
```
That last one is the real test: a bot-versus-bot match running on the machine that ships the
game. If the suite passes and a match resolves, the PC is a full development machine.

Then **open the project in Godot and press F5.** That is the point of the whole session.

---

## PART 4 — The loop, once this works

- **Head edits on the Mac** -> commits -> pushes.
- **Ryan on the PC:** `git pull` -> play.
- **Ryan edits in the Godot editor** (geometry, art, feel) -> commits -> pushes -> head pulls.
- **Head drives the PC directly** over Tailscale SSH for headless runs and to verify on the
  reference GPU: `ssh ryan@<tailscale-name>`.

The one discipline rule: **never both edit the same scene at once.** Godot scene merges are
genuinely bad, and this is solved socially rather than technically by every team that ships.

---

## STILL AN OPEN DECISION — how the Senate pod reaches the PC

The game repo is sorted. The POD (the head's database, decisions and canon) is a different
question, and it is still task 1 in the queue.

- **Option A — private GitHub repo under neotechnites.** Simple, and gives offsite backup.
  But the senate tree carries other domains including Kalshi, which touches money. Pushing all
  of it to a third party is a real decision, not a convenience.
- **Option B — copy over Tailscale, no third party.** `scp -r mac:~/Documents/senate C:\dev\senate`
  Keeps everything on your own machines. Costs you a manual sync.
- **Option C — leave the pod on the Mac for now.** The game works on the PC today either way;
  only the head's own state would live elsewhere.

Head recommendation: B or C until you have decided how you feel about A, because A is the one
that cannot be undone.


---

## APPENDIX — fixing Windows Search, whenever you care to

Broken since the drive clone. The index database is almost certainly stale — it holds absolute
paths and volume identifiers from the old disk. Nothing above depends on it, so this is
optional and can wait.

In an Administrator PowerShell:
```powershell
Stop-Service WSearch
Remove-Item "C:\ProgramData\Microsoft\Search\Data\Applications\Windows\Windows.edb" -Force
Start-Service WSearch
```
Windows rebuilds the index from scratch, which takes a while and hammers the disk — leave it
alone for an hour or two. If search still does nothing after that, the Start menu itself is
damaged rather than the index, and the next step is `sfc /scannow` followed by
`DISM /Online /Cleanup-Image /RestoreHealth`, both in an Administrator PowerShell.
