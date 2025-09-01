\
import os, json, hashlib, re, subprocess, sys, time, pathlib

BASE = pathlib.Path(__file__).resolve().parents[1]
DB_DIR = BASE / "rules-db"
NORM_DIR = DB_DIR / "normalized"
RAW_DIR = DB_DIR / "raw"
VENDOR_DIR = DB_DIR / "vendor"

def ensure_dirs():
    for p in [DB_DIR, NORM_DIR, RAW_DIR, VENDOR_DIR]:
        p.mkdir(parents=True, exist_ok=True)

def sha256_of_dict(d: dict) -> str:
    h = hashlib.sha256(json.dumps(d, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return f"sha256:{h}"

SEV_MAP = {
    # normalized severities
    "info": "info", "minor": "minor", "major": "major", "critical": "critical", "blocker": "blocker",
    # aliases
    "warning": "major", "error": "critical",
    "suggestion": "minor", "convention": "minor",
    "refactor": "major",
    "c": "minor", "r": "major", "w": "major", "e": "critical", "f": "blocker",
    "1": "blocker","2":"critical","3":"major","4":"minor","5":"info"
}

def norm_sev(s: str) -> str:
    if not s: return "info"
    s = str(s).strip().lower()
    return SEV_MAP.get(s, SEV_MAP.get(s.split()[0], "info"))

def write_jsonl(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def append_jsonl(path, records):
    with open(path, "a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def canon_record(*, source, language, rule_id, name, summary, description_md,
                 category, severity, tags, mappings, links, meta):
    if isinstance(language, str): language = [language]
    rec = {
        "uid": f"{source}:{(language[0] if language else '*')}:{rule_id}",
        "source": source,
        "language": language or ["*"],
        "rule_id": rule_id,
        "name": name or rule_id,
        "summary": summary or (name or "")[:180],
        "description_md": description_md or "",
        "category": (category or "code_smell").lower(),
        "severity": norm_sev(severity),
        "tags": sorted(list(set(tags or []))),
        "mappings": mappings or {},
        "links": links or {},
        "meta": meta or {}
    }
    rec["meta"]["hash"] = sha256_of_dict(rec)
    return rec

def have_exe(exe):
    from shutil import which
    return which(exe) is not None

def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)
