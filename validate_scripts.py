#!/usr/bin/env python3
"""Validate Blood on the Clocktower script JSON files against expected schema.

The project consumes scripts authored by the Chinese BotC community. Authors
use a variety of tools and ID conventions; this validator does NOT try to
impose a canonical format. It only flags issues that would break loading
(errors) or signal schema drift worth human attention (warnings).

Usage:
    python3 validate_scripts.py                      # all scripts in 剧本JSON/
    python3 validate_scripts.py path/to/script.json  # single file
    python3 validate_scripts.py 剧本JSON/2025.11/    # a subdirectory
    python3 validate_scripts.py --quiet              # hide warnings
    python3 validate_scripts.py --strict             # exit 1 also on warnings
    python3 validate_scripts.py --summary            # only show final summary

Design:
    Default behaviour is REPORT not REJECT. Users of this repository cannot
    edit authors' scripts; they can only know what is off. Exit code reflects
    whether errors (critical breakage) were seen, not whether warnings were.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).parent

VALID_TEAMS = {"townsfolk", "outsider", "minion", "demon", "traveler", "fabled"}

# Tolerated team values that indicate the entry is NOT a role but an embedded
# jinx (配对克制) definition. Found in ~250 entries across 剧本JSON/.
JINX_ENTRY_TEAMS = {"a jinxed", "A jinxed", "jinxes"}

# Known British-spelling typos that would silently fail role lookup.
TEAM_TYPOS = {"traveller": "traveler"}

# Fields required on a regular role entry (README: Custom Character Support).
REQUIRED_FIELDS = {"id", "name", "team", "ability"}

# Fields documented in README + community extensions that are widely used
# (e.g. appear > 50 times across 剧本JSON/ or used in src/roles.json).
KNOWN_ROLE_FIELDS = {
    # official / README
    "id", "name", "team", "ability", "image", "edition",
    "firstNight", "otherNight", "firstNightReminder", "otherNightReminder",
    "reminders", "remindersGlobal", "setup",
    # community standard (observed in src/roles.json and most scripts)
    "flavor", "attribution", "isCustom",
    "GstoneID",      # 具石社区 role id
    "name_eng",      # English role name
    "official_id",   # official English id mapping (e.g. "washerwoman")
    "name_id",       # alt id field
    "isOfficial",    # bool: is this an officially published role
    # script-tooling markers (observed in dozens of scripts)
    "script", "isbutton", "ismeet",
    # embedded jinx metadata attached to role entries
    "jinxes",
    # official Script Tool metadata (e.g. bag-duplicate markers)
    "special",
}

# Fields that are NOT consumed by product code but appear in author data.
# Tracked separately so we can audit later (promote to KNOWN or clean up).
SUSPICIOUS_FIELDS = {"sch_team"}

# _meta schema — README documents id/name/author/logo; community adds
# group lists and descriptions.
META_KNOWN_FIELDS = {
    # README
    "id", "name", "author", "logo", "almanac",
    # community: per-team role lists in _meta
    "townsfolk", "outsider", "minion", "demon",
    "townsfolkName", "outsidersName", "minionsName", "demonsName",
    "a jinxed", "a jinxedName", "A jinxed",
    "a role",
    # misc prose fields
    "description", "state", "status", "credits", "additional",
}


class Issue:
    __slots__ = ("level", "path", "index", "eid", "kind", "detail")

    def __init__(self, level, path, index, eid, kind, detail=""):
        self.level = level        # 'error' | 'warn' | 'info'
        self.path = path
        self.index = index        # entry index in the array, -1 for file-level
        self.eid = eid
        self.kind = kind          # short category, used for aggregation
        self.detail = detail

    def format(self):
        loc = f"[{self.index}:{self.eid}]" if self.index >= 0 else "[file]"
        msg = f"{self.kind}: {self.detail}" if self.detail else self.kind
        return f"  {self.level.upper():5} {loc} {msg}"


def validate_entry(entry, idx, known_ids):
    issues = []

    if not isinstance(entry, dict):
        issues.append(("error", idx, "?", "not-an-object",
                       f"type={type(entry).__name__}"))
        return issues

    eid = entry.get("id", "<missing-id>")

    # _meta header — separate schema
    if entry.get("id") == "_meta":
        if idx != 0:
            issues.append(("warn", idx, eid, "meta-not-at-start",
                           f"_meta at index {idx}, expected 0"))
        if "name" not in entry:
            issues.append(("warn", idx, eid, "meta-missing-name", ""))
        for k in entry.keys():
            if k not in META_KNOWN_FIELDS:
                issues.append(("warn", idx, eid, "meta-unknown-field", k))
        return issues

    # {id}-only reference (official Script Tool style)
    if set(entry.keys()) == {"id"}:
        if known_ids is not None and entry["id"] not in known_ids:
            issues.append(("warn", idx, eid, "id-ref-unknown",
                           f"id={entry['id']!r} not in src/roles.json"))
        else:
            issues.append(("info", idx, eid, "id-ref", ""))
        return issues

    # Embedded jinx entry (team=a jinxed/jinxes) — not a role, skip role-schema
    if entry.get("team") in JINX_ENTRY_TEAMS:
        issues.append(("info", idx, eid, "jinx-entry", ""))
        return issues

    # Full role entry
    if not isinstance(entry.get("id"), str) or not entry.get("id"):
        issues.append(("error", idx, eid, "bad-id",
                       f"got {entry.get('id')!r}"))

    for m in REQUIRED_FIELDS - entry.keys():
        issues.append(("error", idx, eid, "missing-required", m))

    if "team" in entry:
        t = entry["team"]
        if t in TEAM_TYPOS:
            issues.append(("error", idx, eid, "team-typo",
                           f"got {t!r}, likely {TEAM_TYPOS[t]!r}"))
        elif t not in VALID_TEAMS:
            issues.append(("error", idx, eid, "invalid-team",
                           f"got {t!r}"))

    for nf in ("firstNight", "otherNight"):
        if nf in entry and not isinstance(entry[nf], (int, float)):
            issues.append(("error", idx, eid, "non-numeric-night",
                           f"{nf}={entry[nf]!r}"))
        elif nf in entry and isinstance(entry[nf], bool):
            # bool is subclass of int in Python; treat as error
            issues.append(("error", idx, eid, "non-numeric-night",
                           f"{nf} is bool"))

    for af in ("reminders", "remindersGlobal"):
        if af in entry and not isinstance(entry[af], list):
            issues.append(("error", idx, eid, "not-array",
                           f"{af}={entry[af]!r}"))

    if "setup" in entry:
        s = entry["setup"]
        if isinstance(s, bool):
            pass
        elif s in (0, 1):
            issues.append(("warn", idx, eid, "setup-not-bool",
                           f"got {s!r}, expected true/false"))
        else:
            issues.append(("error", idx, eid, "setup-invalid",
                           f"got {s!r}"))

    if entry.get("ability") == "":
        issues.append(("warn", idx, eid, "empty-ability", ""))

    if entry.get("image") == "":
        issues.append(("warn", idx, eid, "empty-image", ""))

    for k in entry.keys():
        if k in KNOWN_ROLE_FIELDS:
            continue
        if k in SUSPICIOUS_FIELDS:
            issues.append(("warn", idx, eid, "suspicious-field", k))
        else:
            issues.append(("warn", idx, eid, "unknown-field", k))

    return issues


def validate_script(path, known_ids):
    bom_issue = None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        if "BOM" in str(e):
            # JS JSON.parse cannot consume a UTF-8 BOM; record and retry.
            bom_issue = Issue("error", path, -1, "?", "utf8-bom",
                              "file has UTF-8 BOM; JS JSON.parse will fail")
            try:
                with open(path, encoding="utf-8-sig") as f:
                    data = json.load(f)
            except Exception as e2:
                return [bom_issue,
                        Issue("error", path, -1, "?", "invalid-json", str(e2))]
        else:
            return [Issue("error", path, -1, "?", "invalid-json", str(e))]
    except OSError as e:
        return [Issue("error", path, -1, "?", "read-failed", str(e))]

    if not isinstance(data, list):
        return [Issue("error", path, -1, "?", "root-not-array",
                      f"got {type(data).__name__}")]

    issues = [bom_issue] if bom_issue else []
    # id -> [indexes]; only track hashable string ids to stay robust against
    # authors who put arrays/objects where a string id belongs
    ids_seen = {}

    for idx, entry in enumerate(data):
        if isinstance(entry, dict):
            eid_val = entry.get("id")
            if isinstance(eid_val, str) and eid_val and eid_val != "_meta":
                ids_seen.setdefault(eid_val, []).append(idx)
        for level, ent_idx, eid, kind, detail in validate_entry(entry, idx, known_ids):
            issues.append(Issue(level, path, ent_idx, eid, kind, detail))

    for id_, idxs in ids_seen.items():
        if len(idxs) > 1:
            idx_list = ", ".join(str(i) for i in idxs)
            issues.append(Issue("error", path, idxs[0], id_, "duplicate-id",
                                f"appears {len(idxs)} times at indexes [{idx_list}]"))

    return issues


def load_known_ids():
    roles_path = REPO_ROOT / "src" / "roles.json"
    if not roles_path.exists():
        return None
    try:
        with open(roles_path, encoding="utf-8") as f:
            roles = json.load(f)
        return {r["id"] for r in roles if isinstance(r, dict) and "id" in r}
    except Exception as e:
        print(f"warning: failed to load src/roles.json: {e}", file=sys.stderr)
        return None


def collect_files(targets):
    seen = set()
    files = []
    for t in targets:
        tp = Path(t)
        candidates = []
        if tp.is_file() and tp.suffix == ".json":
            candidates = [tp]
        elif tp.is_dir():
            candidates = sorted(tp.rglob("*.json"))
        else:
            print(f"warning: path not found or not JSON: {t}", file=sys.stderr)
            continue
        for c in candidates:
            key = c.resolve()
            if key in seen:
                continue
            seen.add(key)
            files.append(c)
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Validate BotC script JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Design:")[0],
    )
    parser.add_argument("targets", nargs="*", default=["剧本JSON"],
                        help="File(s) or dir(s) to validate (default: 剧本JSON/)")
    parser.add_argument("--quiet", action="store_true",
                        help="Hide warnings and info in per-file output; "
                             "errors only. Summary totals are unaffected.")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 also when only warnings are found")
    parser.add_argument("--summary", action="store_true",
                        help="Show aggregate summary only, no per-file detail")
    args = parser.parse_args()

    known_ids = load_known_ids()
    if known_ids is None:
        print("note: could not load src/roles.json; id-ref checks skipped",
              file=sys.stderr)
    else:
        print(f"loaded {len(known_ids)} known role ids from src/roles.json",
              file=sys.stderr)

    files = collect_files(args.targets)
    if not files:
        print("no JSON files found.", file=sys.stderr)
        return 0
    print(f"validating {len(files)} file(s)...", file=sys.stderr)

    all_issues = []
    files_with_err = 0
    files_with_warn_only = 0

    for fp in files:
        issues = validate_script(fp, known_ids)
        has_err = any(i.level == "error" for i in issues)
        has_warn = any(i.level == "warn" for i in issues)
        if has_err:
            files_with_err += 1
        elif has_warn:
            files_with_warn_only += 1

        if not args.summary:
            if args.quiet:
                shown = [i for i in issues if i.level == "error"]
            else:
                shown = issues  # errors + warnings + info
            if shown:
                print(f"\n{fp}")
                for i in shown:
                    print(i.format())

        all_issues.extend(issues)

    errs = sum(1 for i in all_issues if i.level == "error")
    warns = sum(1 for i in all_issues if i.level == "warn")
    infos = sum(1 for i in all_issues if i.level == "info")

    print(f"\n{'=' * 60}")
    print(f"summary: {len(files)} files scanned")
    print(f"  files with errors:       {files_with_err}")
    print(f"  files with warnings only: {files_with_warn_only}")
    print(f"  totals: errors={errs} warnings={warns} info={infos}")

    err_kinds = Counter(i.kind for i in all_issues if i.level == "error")
    if err_kinds:
        print("\ntop error kinds:")
        for kind, cnt in err_kinds.most_common(10):
            print(f"  {cnt:6}  {kind}")

    warn_kinds = Counter(i.kind for i in all_issues if i.level == "warn")
    if warn_kinds:
        print("\ntop warning kinds:")
        for kind, cnt in warn_kinds.most_common(10):
            print(f"  {cnt:6}  {kind}")

    if errs > 0:
        return 1
    if warns > 0 and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
