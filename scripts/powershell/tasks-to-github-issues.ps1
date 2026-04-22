#requires -Version 5.1
<#
.SYNOPSIS
  Create GitHub issues from unchecked tasks in specs/.../tasks.md (Spec Kit /speckit.taskstoissues).

.DESCRIPTION
  Requires GitHub CLI (https://cli.github.com/) and `gh auth login`.
  Repo is resolved from `git remote get-url origin` (must be github.com).

.PARAMETER TasksPath
  Path to tasks.md relative to repository root.

.PARAMETER DryRun
  Print tasks only; do not create issues.

.PARAMETER DelaySeconds
  Sleep between API calls to reduce rate-limit risk.
#>
param(
    [string] $TasksPath = "specs/001-telegram-language-bot/tasks.md",
    [switch] $DryRun,
    [int] $DelaySeconds = 1
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\.."))

if (-not $DryRun -and -not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "Install GitHub CLI (gh) and run: gh auth login. See https://cli.github.com/"
}

$remote = git config --get remote.origin.url
if (-not $remote) {
    Write-Error "Missing git remote.origin.url"
}

if ($remote -match 'github\.com[:/](?<owner>[^/]+)/(?<repo>[^/.]+)(\.git)?') {
    $owner = $Matches['owner']
    $repoName = $Matches['repo']
}
else {
    Write-Error "origin is not a GitHub URL: $remote"
}

$fullPath = Join-Path (Get-Location) $TasksPath
if (-not (Test-Path $fullPath)) {
    Write-Error "File not found: $fullPath"
}

$lines = Get-Content -LiteralPath $fullPath -Encoding UTF8
$phase = "Unknown"
$created = 0

foreach ($line in $lines) {
    if ($line -match '^##\s+Phase\s+\d+') {
        $phase = $line.TrimStart("#").Trim()
        continue
    }
    if ($line -notmatch '^-\s+\[\s*\]\s+(T\d+)\s+(.+)$') {
        continue
    }
    $taskId = $Matches[1]
    $description = $Matches[2].Trim()
    $title = "[$taskId] $description"
    if ($title.Length -gt 240) {
        $title = $title.Substring(0, 237) + "..."
    }

    $body = @"
## $taskId

$description

| Поле | Значение |
|------|----------|
| Фаза (из tasks.md) | $phase |
| Фича | \`001-telegram-language-bot\` |

### Артефакты
- [spec.md](https://github.com/$owner/$repoName/blob/main/specs/001-telegram-language-bot/spec.md)
- [plan.md](https://github.com/$owner/$repoName/blob/main/specs/001-telegram-language-bot/plan.md)
- [tasks.md](https://github.com/$owner/$repoName/blob/main/specs/001-telegram-language-bot/tasks.md)

_Создано скриптом \`scripts/powershell/tasks-to-github-issues.ps1\` (Spec Kit taskstoissues)._
"@

    if ($DryRun) {
        Write-Host "DRY-RUN [$taskId] $phase :: $title"
        $created++
        continue
    }

    $bodyFile = [System.IO.Path]::GetTempFileName()
    try {
        Set-Content -LiteralPath $bodyFile -Value $body -Encoding UTF8
        gh issue create --repo "$owner/$repoName" --title $title --body-file $bodyFile | Write-Host
    }
    finally {
        Remove-Item -LiteralPath $bodyFile -Force -ErrorAction SilentlyContinue
    }
    $created++
    if ($DelaySeconds -gt 0) {
        Start-Sleep -Seconds $DelaySeconds
    }
}

Write-Host "Done. Tasks processed: $created."
