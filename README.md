# Rules DB Pipeline (Windows-friendly)

This toolkit builds a **local, file-based database of coding rules** from multiple ecosystems (Sonar, Semgrep, ESLint, Pylint, Ruff, PMD, Checkstyle, clang-tidy, .NET CA analyzers, CodeQL).

> You **do not need** all tools installed. Each adapter will **skip gracefully** if its prerequisites (e.g., `git`, `clang-tidy`) are missing.

## Quick Start (Windows)

1) Install Python 3.10+ and Git for Windows.
2) (Optional) Install `make` via Git Bash or Chocolatey (`choco install make`).
3) In PowerShell from this folder:
   ```powershell
   py -m pip install -r requirements.txt
   ```
4) Run with **Make** (preferred):
   ```powershell
   make build-db
   ```
   Or with the PowerShell wrapper:
   ```powershell
   ./build-db.ps1
   ```

### Outputs

```
rules-db/
  normalized/
    sonar.jsonl
    semgrep.jsonl
    eslint.jsonl
    typescript-eslint.jsonl
    pylint.jsonl
    ruff.jsonl
    pmd.jsonl
    checkstyle.jsonl
    clang_tidy.jsonl
    dotnet.jsonl
    codeql.jsonl
    rules.jsonl         # merged & de-duplicated
  policy-packs/
    <lang>/<axis>.jsonl  # adaptability, consistency, intentionality, responsibility
  catalog/
    views.sql
```

### Notes

- **Network use:** Adapters that clone repos need internet access. If offline, they will be skipped.
- **Licensing/ToS:** Review each upstream project's license/terms and your use-case before redistribution.
- **Extensibility:** Add new adapters under `scripts/` and register them in the Makefile and PowerShell wrapper.
