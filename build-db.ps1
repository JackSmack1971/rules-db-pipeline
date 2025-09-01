\
param(
  [string]$Python = "py -3"
)
Write-Host "== Rules DB build (PowerShell wrapper) =="
& $Python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Warning "pip install failed"; exit 1 }

$steps = @(
  "scripts/fetch_repos.py",
  "scripts/ingest_sonar.py",
  "scripts/ingest_semgrep.py",
  "scripts/ingest_eslint.py",
  "scripts/ingest_typescript_eslint.py",
  "scripts/ingest_pylint.py",
  "scripts/ingest_ruff.py",
  "scripts/ingest_pmd.py",
  "scripts/ingest_checkstyle.py",
  "scripts/ingest_clang_tidy.py",
  "scripts/ingest_dotnet.py",
  "scripts/ingest_codeql.py",
  "scripts/consolidate.py",
  "scripts/build_packs.py"
)

foreach ($s in $steps) {
  Write-Host "-> Running $s"
  & $Python $s
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "Step failed: $s (continuing, some sources may be missing)"
  }
}
Write-Host "== Done. Outputs in rules-db/ =="
