\
# Cross-platform-ish Makefile. On Windows, run via Git Bash or 'make' from Chocolatey.
# You can override PY in the environment:  set PY=py -3
PY ?= python

.DEFAULT_GOAL := build-db

init:
	$(PY) -m pip install -r requirements.txt

fetch-repos:
	$(PY) scripts/fetch_repos.py

ingest:
	$(PY) scripts/ingest_sonar.py
	$(PY) scripts/ingest_semgrep.py
	$(PY) scripts/ingest_eslint.py
	$(PY) scripts/ingest_typescript_eslint.py
	$(PY) scripts/ingest_pylint.py
	$(PY) scripts/ingest_ruff.py
	$(PY) scripts/ingest_pmd.py
	$(PY) scripts/ingest_checkstyle.py
	$(PY) scripts/ingest_clang_tidy.py
	$(PY) scripts/ingest_dotnet.py
	$(PY) scripts/ingest_codeql.py

consolidate:
	$(PY) scripts/consolidate.py

packs:
	$(PY) scripts/build_packs.py

build-db: init fetch-repos ingest consolidate packs

clean:
	- del rules-db\\normalized\\*.jsonl 2> NUL || true
	- del rules-db\\normalized\\rules.jsonl 2> NUL || true
	- rmdir /S /Q rules-db\\policy-packs 2> NUL || true
