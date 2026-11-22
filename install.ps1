# AGY Pulse (agy-statusline) Windows Installer
# Usage (one-liner):
#   irm https://raw.githubusercontent.com/Arielkap/agy-statusline/main/install.ps1 | iex
# Or from a cloned repo:
#   powershell -ExecutionPolicy Bypass -File .\install.ps1

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/Arielkap/agy-statusline.git"
$RawBase = "https://raw.githubusercontent.com/Arielkap/agy-statusline/main"
$RepoDir = Join-Path $env:USERPROFILE ".agy-statusline"
$TargetDir = Join-Path $env:USERPROFILE "bin"
$TargetScript = Join-Path $TargetDir "agy_statusline.py"
$TargetThemePy = Join-Path $TargetDir "agy_theme.py"
$SettingsDir = Join-Path $env:USERPROFILE ".gemini\antigravity-cli"
$SettingsFile = Join-Path $SettingsDir "settings.json"
$SkillDir = Join-Path $env:USERPROFILE ".gemini\skills\th"

function Find-Python {
    $candidates = @(
        @{ Exe = "python"; Prefix = @(); Display = "python" },
        @{ Exe = "python3"; Prefix = @(); Display = "python3" },
        @{ Exe = "py"; Prefix = @("-3"); Display = "py -3" }
    )
    foreach ($c in $candidates) {
        $cmd = Get-Command $c.Exe -ErrorAction SilentlyContinue
        if ($cmd) {
            try {
                $verCheck = & $c.Exe @($c.Prefix + @("-c", "import sys; print(sys.executable); raise SystemExit(0 if sys.version_info >= (3, 8) else 1)")) 2>$null
                if ($LASTEXITCODE -eq 0 -and $verCheck) {
                    $resolvedExe = ($verCheck | Select-Object -First 1).Trim()
                    # Ignore Windows Store stub if it resolved strangely
                    if ($resolvedExe -and (Test-Path $resolvedExe)) {
                        return @{
                            Exe = $c.Exe
                            Prefix = $c.Prefix
                            Display = $c.Display
                            FullExe = $resolvedExe
                            InPath = $true
                        }
                    }
                }
            } catch {
                continue
            }
        }
    }
    return $null
}

Write-Host "==> Checking Python 3.8+..."
$py = Find-Python
if (-not $py) {
    Write-Error "Python 3.8+ not found. Install Python first (e.g. 'winget install Python.Python.3.12'), restart your terminal, and re-run."
    exit 1
}
Write-Host "    Found Python: $($py.FullExe)"

# Determine source files (local repo vs remote one-liner)
$SourceDir = $null
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "agy_statusline.py"))) {
    $SourceDir = $PSScriptRoot
} else {
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd) {
        if (Test-Path (Join-Path $RepoDir ".git")) {
            Write-Host "==> Updating existing clone in $RepoDir..."
            git -C $RepoDir pull --ff-only
        } else {
            Write-Host "==> Cloning repository to $RepoDir..."
            git clone $RepoUrl $RepoDir
        }
        $SourceDir = $RepoDir
    } else {
        Write-Host "==> Downloading files from GitHub to $RepoDir..."
        New-Item -ItemType Directory -Force -Path (Join-Path $RepoDir "skills\th") | Out-Null
        Invoke-WebRequest -UseBasicParsing -Uri "$RawBase/agy_statusline.py" -OutFile (Join-Path $RepoDir "agy_statusline.py")
        Invoke-WebRequest -UseBasicParsing -Uri "$RawBase/agy_theme.py" -OutFile (Join-Path $RepoDir "agy_theme.py")
        Invoke-WebRequest -UseBasicParsing -Uri "$RawBase/skills/th/SKILL.md" -OutFile (Join-Path $RepoDir "skills\th\SKILL.md")
        $SourceDir = $RepoDir
    }
}

Write-Host "==> Preparing bin directory: $TargetDir"
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

Copy-Item -Force (Join-Path $SourceDir "agy_statusline.py") $TargetScript
Copy-Item -Force (Join-Path $SourceDir "agy_theme.py") $TargetThemePy

# Build command prefix usable by cmd /c without quote-stripping issues
if ($py.Display -eq "py -3") {
    $PyCmd = "py -3"
} elseif ($py.Display -eq "python") {
    $PyCmd = "python"
} else {
    $PyCmd = "call `"$($py.FullExe)`""
}

$ThemeCmdPath = Join-Path $TargetDir "agy-theme.cmd"
$ThCmdPath = Join-Path $TargetDir "th.cmd"
$StatusCmdPath = Join-Path $TargetDir "agy_statusline.cmd"

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($ThemeCmdPath, "@echo off`r`n$PyCmd `"%~dp0agy_theme.py`" %*`r`n", $utf8NoBom)
[System.IO.File]::WriteAllText($ThCmdPath, "@echo off`r`n$PyCmd `"%~dp0agy_theme.py`" %*`r`n", $utf8NoBom)
[System.IO.File]::WriteAllText($StatusCmdPath, "@echo off`r`n$PyCmd `"%~dp0agy_statusline.py`" %*`r`n", $utf8NoBom)

# Add %USERPROFILE%\bin to User PATH if missing
$userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
$pathParts = @()
if ($userPath) {
    $pathParts = $userPath -split ";" | Where-Object { $_ -and $_.Trim() -ne "" }
}
if ($pathParts -notcontains $TargetDir) {
    Write-Host "==> Adding $TargetDir to User PATH..."
    $newUserPath = ($pathParts + $TargetDir) -join ";"
    [System.Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
    $env:Path = "$env:Path;$TargetDir"
}

# Install /th skill adapted for Windows
Write-Host "==> Installing /th skill into $SkillDir"
New-Item -ItemType Directory -Force -Path $SkillDir | Out-Null
$skillSrc = Join-Path $SourceDir "skills\th\SKILL.md"
$skillContent = [System.IO.File]::ReadAllText($skillSrc, $utf8NoBom)
$skillContent = $skillContent.Replace("~/bin/agy-theme", "`"$ThemeCmdPath`"")
[System.IO.File]::WriteAllText((Join-Path $SkillDir "SKILL.md"), $skillContent, $utf8NoBom)

# Configure settings.json
Write-Host "==> Updating Antigravity CLI settings: $SettingsFile"
New-Item -ItemType Directory -Force -Path $SettingsDir | Out-Null
if (-not (Test-Path $SettingsFile)) {
    [System.IO.File]::WriteAllText($SettingsFile, "{}`n", $utf8NoBom)
}

$statusLineCommand = "$PyCmd `"$TargetScript`""

$pyUpdate = @'
import json
import sys

settings_path, cmd_str = sys.argv[1], sys.argv[2]
with open(settings_path, "r", encoding="utf-8-sig") as f:
    raw = f.read().strip()
cfg = json.loads(raw) if raw else {}

cfg["statusLine"] = {
    "type": "command",
    "command": cmd_str,
    "enabled": True,
    "stack_with_default": True,
}

allows = cfg.setdefault("permissions", {}).setdefault("allow", [])
cmd_rule = f"command({cmd_str})"
if cmd_rule not in allows:
    allows.append(cmd_rule)

with open(settings_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")
'@

$tmpPy = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "agy_setup_" + [System.Guid]::NewGuid().ToString("N") + ".py")
try {
    [System.IO.File]::WriteAllText($tmpPy, $pyUpdate, $utf8NoBom)
    & $py.Exe @($py.Prefix + @($tmpPy, $SettingsFile, $statusLineCommand))
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to update $SettingsFile"
        exit 1
    }
} finally {
    Remove-Item -Force -ErrorAction SilentlyContinue $tmpPy
}

Write-Host "==> Running self-test..."
$sampleJson = '{"terminal_width": 140, "model": {"id": "gemini-4-hydrogen-high", "display_name": "Gemini 4 Hydrogen (High)"}, "context_window": {"total_input_tokens": 125000, "total_output_tokens": 25000, "context_window_size": 1048576, "used_percentage": 14.3}, "quota": {"gemini-5h": {"remaining_fraction": 0.85, "reset_in_seconds": 3600}, "gemini-weekly": {"remaining_fraction": 0.95, "reset_in_seconds": 518400}, "gemini-argon-wtu-weekly": {"remaining_fraction": 1.0, "reset_in_seconds": 498000}, "3p-5h": {"remaining_fraction": 1.0, "reset_in_seconds": 18000}, "3p-weekly": {"remaining_fraction": 0.5, "reset_in_seconds": 259200}}}'
$sampleJson | & $py.Exe @($py.Prefix + @($TargetScript))

Write-Host ""
Write-Host "==> Installation complete!"
Write-Host "    1. Open a NEW Windows Terminal tab (to load updated PATH)."
Write-Host "    2. Run 'agy' and type /skills reload, then try /th (or 'th' in PowerShell/CMD)."
