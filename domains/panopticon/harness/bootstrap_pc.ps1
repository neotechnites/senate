# Panopticon PC bootstrap - run ONCE, in an Administrator PowerShell, on the dev PC.
#
# WHY THIS IS A SCRIPT AND NOT A CHECKLIST: Ryan has ~8 hours a week at this machine and
# ~233 of them left before 2027-04-01 (verify/schedule.py). Setup that could have been
# automated is the most expensive way to spend one. Everything here is idempotent - run
# it again any time; it installs what is missing and reports what it could not do.
#
# IT NEVER FAILS SILENTLY. Every step prints OK / SKIP / MANUAL, and the summary at the
# end is the authority on what still needs a human.

$ErrorActionPreference = "Continue"
$results = @()
function Step($name, $test, $action, $manual) {
    Write-Host "`n=== $name ===" -ForegroundColor Cyan
    $already = $false
    try { $already = & $test } catch { $already = $false }
    if ($already) { Write-Host "OK (already present)" -ForegroundColor Green
                    $script:results += [pscustomobject]@{Step=$name; State="OK"}; return }
    if ($action) {
        try { & $action
              $ok = $false; try { $ok = & $test } catch { $ok = $false }
              if ($ok) { Write-Host "OK (installed)" -ForegroundColor Green
                         $script:results += [pscustomobject]@{Step=$name; State="OK"}; return } }
        catch { Write-Host "action failed: $_" -ForegroundColor Yellow }
    }
    Write-Host "MANUAL: $manual" -ForegroundColor Yellow
    $script:results += [pscustomobject]@{Step=$name; State="MANUAL"; Note=$manual}
}

Write-Host "PANOPTICON PC BOOTSTRAP" -ForegroundColor Magenta
Write-Host "Ship date 2027-04-01. This machine is the development PC and its pod DB is truth."

# --- 1. winget itself -------------------------------------------------------------
Step "winget available" { (Get-Command winget -EA SilentlyContinue) -ne $null } $null `
     "Install 'App Installer' from the Microsoft Store, then re-run this script."

function Wg($id) { winget install --id $id --accept-source-agreements --accept-package-agreements -e -h }

# --- 2. Toolchain -----------------------------------------------------------------
Step "Git"      { (Get-Command git -EA SilentlyContinue) -ne $null }     { Wg "Git.Git" } `
     "Install Git from https://git-scm.com/download/win"
Step "Python 3" { (Get-Command python -EA SilentlyContinue) -ne $null }  { Wg "Python.Python.3.13" } `
     "Install Python 3 from https://www.python.org/downloads/windows/ (check 'Add to PATH')"
Step "Godot 4"  { (Get-Command godot -EA SilentlyContinue) -ne $null -or `
                  (Test-Path "$env:LOCALAPPDATA\Programs\Godot") } { Wg "GodotEngine.GodotEngine" } `
     "Install Godot 4 from https://godotengine.org/download/windows/ and put it on PATH as 'godot' - the headless bot harness shells out to that name."
Step "Blender"  { (Get-Command blender -EA SilentlyContinue) -ne $null -or `
                  (Test-Path "C:\Program Files\Blender Foundation") } { Wg "BlenderFoundation.Blender" } `
     "Install Blender from https://www.blender.org/download/ - Astra drives it through its real UI, so it must be installed locally."
Step "Tailscale" { (Get-Command tailscale -EA SilentlyContinue) -ne $null } { Wg "tailscale.tailscale" } `
     "Install Tailscale from https://tailscale.com/download/windows, then run 'tailscale up' and sign in on BOTH this PC and the Mac."

# --- 3. Claude Code (native Windows installer; auto-updates, unlike winget/npm) ----
Step "Claude Code" { (Get-Command claude -EA SilentlyContinue) -ne $null } `
     { irm https://claude.ai/install.ps1 | iex } `
     "Run in PowerShell:  irm https://claude.ai/install.ps1 | iex"

# --- 4. Remote access from the Mac -------------------------------------------------
Step "OpenSSH Server installed" `
     { (Get-WindowsCapability -Online -Name OpenSSH.Server* | Where-Object State -eq 'Installed') -ne $null } `
     { Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 } `
     "Settings > System > Optional features > Add > OpenSSH Server"
Step "OpenSSH Server running at boot" `
     { (Get-Service sshd -EA SilentlyContinue).Status -eq 'Running' } `
     { Set-Service -Name sshd -StartupType Automatic; Start-Service sshd } `
     "Start-Service sshd; Set-Service sshd -StartupType Automatic"
Step "PC stays awake (it must always be on)" `
     { $false } { powercfg /change standby-timeout-ac 0; powercfg /change hibernate-timeout-ac 0 } `
     "powercfg /change standby-timeout-ac 0"

# --- 5. Workspace ------------------------------------------------------------------
$dev = "C:\dev"
Step "C:\dev exists" { Test-Path $dev } { New-Item -ItemType Directory -Force -Path $dev | Out-Null } `
     "mkdir C:\dev"
Step "Game repo initialised" { Test-Path "$dev\panopticon-game\.git" } `
     { New-Item -ItemType Directory -Force -Path "$dev\panopticon-game" | Out-Null
       Push-Location "$dev\panopticon-game"; git init -q; Pop-Location } `
     "git init C:\dev\panopticon-game"

# --- 6. Summary --------------------------------------------------------------------
Write-Host "`n================ SUMMARY ================" -ForegroundColor Magenta
$results | Format-Table -AutoSize
$manual = $results | Where-Object State -eq "MANUAL"
if ($manual) { Write-Host "$($manual.Count) step(s) need you. Nothing below is done until they are." -ForegroundColor Yellow }
else { Write-Host "Every step reported OK." -ForegroundColor Green }

Write-Host @"

STILL NEEDS A DECISION FROM RYAN - how the Senate repo (which carries the Panopticon pod)
reaches this PC. The repo currently has NO git remote, so there is no clone URL yet:

  OPTION A - private GitHub repo (recommended; also gives you offsite backup)
      on the Mac:  gh repo create senate --private --source=. --push
      on this PC:  cd C:\dev; git clone https://github.com/<you>/senate.git

  OPTION B - direct copy over Tailscale, no third party
      on this PC:  scp -r <mac-tailscale-name>:~/Documents/senate C:\dev\senate

The GAME repo (C:\dev\panopticon-game) is deliberately SEPARATE from the pod: different
lifetime, different audience, and the Senate repo carries trading code that has no
business in a game repo.

THEN, on this PC:
  cd C:\dev\senate\domains\panopticon
  python spinup.py          # boots the Panopticon Domain Head against the pod DB

AND from the Mac, to work remotely:
  ssh <windows-user>@<pc-tailscale-name>
  cd C:\dev\senate\domains\panopticon; python spinup.py
"@ -ForegroundColor Cyan
