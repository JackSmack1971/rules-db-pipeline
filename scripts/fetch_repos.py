\
#!/usr/bin/env python3
import os, subprocess, sys, pathlib
from utils.common import VENDOR_DIR, ensure_dirs, have_exe, run

REPOS = [
    ("eslint", "https://github.com/eslint/eslint.git"),
    ("typescript-eslint", "https://github.com/typescript-eslint/typescript-eslint.git"),
    ("semgrep-rules", "https://github.com/semgrep/semgrep-rules.git"),
    ("pmd", "https://github.com/pmd/pmd.git"),
    ("checkstyle", "https://github.com/checkstyle/checkstyle.git"),
    ("ruff", "https://github.com/astral-sh/ruff.git"),
    ("roslyn-analyzers", "https://github.com/dotnet/roslyn-analyzers.git"),
    ("dotnet-docs", "https://github.com/dotnet/docs.git"),
    ("codeql", "https://github.com/github/codeql.git"),
]

def git(cmd, cwd=None):
    return run(["git"] + cmd, cwd=cwd)

if __name__ == "__main__":
    ensure_dirs()
    if not have_exe("git"):
        print("WARN: git not found; skipping repo fetch. Some adapters will have limited output.", file=sys.stderr)
        sys.exit(0)

    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in REPOS:
        dest = VENDOR_DIR / name
        if not dest.exists():
            print(f"Cloning {name} ...")
            res = git(["clone", "--depth", "1", "--quiet", url, str(dest)])
            if res.returncode != 0:
                print(f"WARN: clone failed for {name}: {res.stderr.strip()}", file=sys.stderr)
        else:
            print(f"Updating {name} ...")
            res = git(["-C", str(dest), "pull", "--ff-only", "--quiet"])
            if res.returncode != 0:
                print(f"WARN: pull failed for {name}: {res.stderr.strip()}", file=sys.stderr)
    print("Repo fetch complete.")
