"""
_curator_lib.py — Internal shared library for curator
Not a CLI; import only.

Python >= 3.11 required (tomllib is stdlib).
"""

from __future__ import annotations

import json
import os
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

# ── Version ────────────────────────────────────────────────────────────────────
VERSION = "1.0.0"

# ── Defaults ───────────────────────────────────────────────────────────────────
_DEFAULTS: dict[str, Any] = {
    "library": {
        "name": "Course Library",
        "unsorted_dir": "0x0_unsorted",
        "excluded_dirs": [".git", "utils", "node_modules", "__pycache__", ".venv", "venv", ".idea", ".vscode"],
        "depth": "cat/sub/course",
    },
    "video": {
        "extensions": [".mp4", ".flv", ".mkv", ".avi", ".ts", ".webm", ".m4v"],
    },
    "naming": {
        "category_pattern": r"^\d{2}_[A-Z][A-Za-z0-9_]+$",
        "subtopic_pattern": r"^[A-Z][A-Za-z0-9_]+$",
        "course_pattern": "",
        "rules": {},
        "source_prefixes": {},
    },
}


# ── Config ─────────────────────────────────────────────────────────────────────

def load_config(root: Path, config_path: Path | None = None) -> dict[str, Any]:
    """Load courses.toml and merge with built-in defaults.

    Args:
        root: Library root directory.
        config_path: Explicit path to courses.toml; defaults to <root>/courses.toml.

    Returns:
        Merged config dict.  Missing keys are filled from _DEFAULTS.
    """
    path = config_path or (root / "courses.toml")
    cfg: dict[str, Any] = {}

    if path.exists():
        try:
            with open(path, "rb") as fh:
                cfg = tomllib.load(fh)
        except tomllib.TOMLDecodeError as exc:
            _die(f"courses.toml parse error: {exc}")
    # else: file missing — pure defaults, that's fine for count/lint/print

    # Deep-merge defaults under cfg
    for section, defaults in _DEFAULTS.items():
        if section not in cfg:
            cfg[section] = {}
        for key, val in defaults.items():
            cfg[section].setdefault(key, val)

    # Support [naming.patterns] from courses.toml as an alias for category_pattern/subtopic_pattern/course_pattern
    naming_sec = cfg.get("naming", {})
    patterns_sec = naming_sec.get("patterns", {})
    if isinstance(patterns_sec, dict):
        if "category_dir" in patterns_sec:
            naming_sec["category_pattern"] = patterns_sec["category_dir"]
        elif "category_pattern" in patterns_sec:
            naming_sec["category_pattern"] = patterns_sec["category_pattern"]

        if "subtopic_dir" in patterns_sec:
            naming_sec["subtopic_pattern"] = patterns_sec["subtopic_dir"]
        elif "subtopic_pattern" in patterns_sec:
            naming_sec["subtopic_pattern"] = patterns_sec["subtopic_pattern"]

        if "course_dir" in patterns_sec:
            naming_sec["course_pattern"] = patterns_sec["course_dir"]
        elif "course_pattern" in patterns_sec:
            naming_sec["course_pattern"] = patterns_sec["course_pattern"]

    # Validate naming regex patterns (if non-empty)
    for key in ("category_pattern", "subtopic_pattern", "course_pattern"):
        pat = cfg["naming"].get(key, "")
        if pat:
            try:
                re.compile(pat)
            except re.error as exc:
                _die(f"courses.toml [naming].{key} is not a valid regex: {exc}")

    # Resolve root: CLI --root > toml [library].root > auto-detected
    if "root" not in cfg["library"]:
        cfg["library"]["root"] = str(root)

    return cfg


# ── Directory helpers ──────────────────────────────────────────────────────────

def resolve_root(cfg: dict[str, Any], cli_root: str | None) -> Path:
    """Return the effective library root."""
    if cli_root:
        return Path(cli_root).resolve()
    return Path(cfg["library"]["root"]).resolve()


def get_categories(root: Path, cfg: dict[str, Any], include_unsorted: bool = False) -> list[Path]:
    """Return sorted list of category directories under *root*."""
    excluded = set(cfg["library"]["excluded_dirs"])
    unsorted = cfg["library"]["unsorted_dir"]
    cats: list[Path] = []
    try:
        entries = sorted(root.iterdir())
    except PermissionError:
        return []
    for entry in entries:
        if not entry.is_dir():
            continue
        name = entry.name
        if name in excluded or name == "__pycache__" or name.startswith("."):
            continue
        if name == unsorted:
            if include_unsorted:
                cats.append(entry)
            continue
        cats.append(entry)
    return cats


def _video_extensions(cfg: dict[str, Any]) -> frozenset[str]:
    return frozenset(e.lower() for e in cfg["video"]["extensions"])


# ── Counting ───────────────────────────────────────────────────────────────────

def count_course(path: Path, cfg: dict[str, Any]) -> tuple[int, int]:
    """Return (sections, videos) for a single course directory.

    sections = number of immediate subdirectories.
    videos   = total video files (recursive).
    """
    exts = _video_extensions(cfg)
    try:
        subdirs = [e for e in path.iterdir() if e.is_dir()]
    except PermissionError:
        return 0, 0
    sections = len(subdirs)
    videos = 0
    for dirpath, _, filenames in os.walk(path):
        for fn in filenames:
            if Path(fn).suffix.lower() in exts:
                videos += 1
    return sections, videos


def count_all(
    root: Path,
    cfg: dict[str, Any],
    filter_cat: str | None = None,
    include_unsorted: bool = False,
) -> list[dict[str, Any]]:
    """Walk the library and return per-course count rows.

    Each row is a dict with keys:
        path        relative path string (category/subtopic/course or category/course)
        category    top-level category name
        subtopic    subtopic name (empty for 2-level libraries)
        course      course folder name
        sections    int
        videos      int
        summary     human-readable string e.g. "(7 sections, 40 lessons)"
    """
    depth = cfg["library"].get("depth", "cat/sub/course")
    rows: list[dict[str, Any]] = []

    for cat in get_categories(root, cfg, include_unsorted):
        if filter_cat and filter_cat.lower() not in cat.name.lower():
            continue

        if depth == "cat/course":
            # 2-level: direct course folders inside category
            try:
                courses = sorted(e for e in cat.iterdir() if e.is_dir())
            except PermissionError:
                continue
            for course in courses:
                sections, videos = count_course(course, cfg)
                rows.append(_make_row(cat.name, "", course.name, sections, videos))
        else:
            # 3-level default: category / subtopic / course
            try:
                subtopics = sorted(e for e in cat.iterdir() if e.is_dir())
            except PermissionError:
                continue
            for sub in subtopics:
                try:
                    courses = sorted(e for e in sub.iterdir() if e.is_dir())
                except PermissionError:
                    continue
                for course in courses:
                    sections, videos = count_course(course, cfg)
                    rows.append(_make_row(cat.name, sub.name, course.name, sections, videos))

    return rows


def _make_row(cat: str, sub: str, course: str, sections: int, videos: int) -> dict[str, Any]:
    parts = [p for p in [cat, sub, course] if p]
    rel = "/".join(parts)
    if sections > 0 and videos > 0:
        summary = f"({sections} sections, {videos} lessons)"
    elif videos > 0:
        summary = f"({videos} lessons)"
    else:
        summary = "(no video files)"
    return {
        "path": rel,
        "category": cat,
        "subtopic": sub,
        "course": course,
        "sections": sections,
        "videos": videos,
        "summary": summary,
    }


# ── Lint / violations ──────────────────────────────────────────────────────────

def scan_violations(
    root: Path,
    cfg: dict[str, Any],
    check_cats: bool = True,
) -> list[dict[str, str]]:
    """Scan for naming-convention violations.

    Returns list of dicts with keys: level, path, message.
    """
    naming = cfg["naming"]
    cat_re = re.compile(naming["category_pattern"]) if naming["category_pattern"] else None
    sub_re = re.compile(naming["subtopic_pattern"]) if naming["subtopic_pattern"] else None
    crs_re = re.compile(naming["course_pattern"]) if naming["course_pattern"] else None

    violations: list[dict[str, str]] = []
    depth = cfg["library"].get("depth", "cat/sub/course")

    for cat in get_categories(root, cfg, include_unsorted=False):
        if check_cats and cat_re and not cat_re.match(cat.name):
            violations.append({
                "level": "category",
                "path": cat.name,
                "message": f"Category violates pattern ({naming['category_pattern']}): {cat.name}",
            })
        if depth == "cat/course":
            try:
                courses = sorted(e for e in cat.iterdir() if e.is_dir())
            except PermissionError:
                continue
            for course in courses:
                if crs_re and not crs_re.match(course.name):
                    violations.append({
                        "level": "course",
                        "path": f"{cat.name}/{course.name}",
                        "message": f"Course violates pattern: {cat.name}/{course.name}",
                    })
        else:
            try:
                subtopics = sorted(e for e in cat.iterdir() if e.is_dir())
            except PermissionError:
                continue
            for sub in subtopics:
                if sub_re and not sub_re.match(sub.name):
                    violations.append({
                        "level": "subtopic",
                        "path": f"{cat.name}/{sub.name}",
                        "message": f"Subtopic violates pattern ({naming['subtopic_pattern']}): {cat.name}/{sub.name}",
                    })
                try:
                    courses = sorted(e for e in sub.iterdir() if e.is_dir())
                except PermissionError:
                    continue
                for course in courses:
                    if crs_re and not crs_re.match(course.name):
                        violations.append({
                            "level": "course",
                            "path": f"{cat.name}/{sub.name}/{course.name}",
                            "message": f"Course violates pattern: {cat.name}/{sub.name}/{course.name}",
                        })

    return violations


# ── Tree builder ───────────────────────────────────────────────────────────────

def build_tree_data(
    root: Path,
    cfg: dict[str, Any],
    include_unsorted: bool = False,
    filter_cat: str | None = None,
) -> list[dict[str, Any]]:
    """Return nested structure for the `print` command.

    Top-level list of category dicts:
      name, subtopics (list), total_courses, total_videos
    Each subtopic dict:
      name, courses (list), total_videos
    Each course dict:
      name, sections, videos, summary
    """
    depth = cfg["library"].get("depth", "cat/sub/course")
    result: list[dict[str, Any]] = []

    for cat in get_categories(root, cfg, include_unsorted):
        if filter_cat and filter_cat.lower() not in cat.name.lower():
            continue

        cat_entry: dict[str, Any] = {
            "name": cat.name,
            "subtopics": [],
            "total_courses": 0,
            "total_videos": 0,
        }

        if depth == "cat/course":
            try:
                courses = sorted(e for e in cat.iterdir() if e.is_dir())
            except PermissionError:
                result.append(cat_entry)
                continue
            pseudo_sub: dict[str, Any] = {"name": "", "courses": [], "total_videos": 0}
            for course in courses:
                sections, videos = count_course(course, cfg)
                row = _make_row(cat.name, "", course.name, sections, videos)
                pseudo_sub["courses"].append(row)
                pseudo_sub["total_videos"] += videos
                cat_entry["total_courses"] += 1
                cat_entry["total_videos"] += videos
            cat_entry["subtopics"].append(pseudo_sub)
        else:
            try:
                subtopics = sorted(e for e in cat.iterdir() if e.is_dir())
            except PermissionError:
                result.append(cat_entry)
                continue
            for sub in subtopics:
                sub_entry: dict[str, Any] = {
                    "name": sub.name,
                    "courses": [],
                    "total_videos": 0,
                }
                try:
                    courses = sorted(e for e in sub.iterdir() if e.is_dir())
                except PermissionError:
                    cat_entry["subtopics"].append(sub_entry)
                    continue
                for course in courses:
                    sections, videos = count_course(course, cfg)
                    row = _make_row(cat.name, sub.name, course.name, sections, videos)
                    sub_entry["courses"].append(row)
                    sub_entry["total_videos"] += videos
                    cat_entry["total_courses"] += 1
                    cat_entry["total_videos"] += videos
                cat_entry["subtopics"].append(sub_entry)

        result.append(cat_entry)

    return result


# ── Triage ─────────────────────────────────────────────────────────────────────

def scan_unsorted(root: Path, cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """Scan the unsorted staging directory and return item details.

    Each item dict:
      name, type ("file"|"dir"), ext (file only),
      size_bytes, size_human,
      subdirs (dir only), files_per_subdir (dir only),
      total_files, extensions (Counter as dict)
    """
    unsorted_name = cfg["library"]["unsorted_dir"]
    unsorted_path = root / unsorted_name
    items: list[dict[str, Any]] = []

    if not unsorted_path.exists():
        return items

    try:
        entries = sorted(unsorted_path.iterdir())
    except PermissionError:
        return items

    for entry in entries:
        item: dict[str, Any] = {"name": entry.name}
        if entry.is_dir():
            item["type"] = "dir"
            # Subdirs and root-level files at depth 1
            try:
                sub_entries = sorted(entry.iterdir())
            except PermissionError:
                sub_entries = []
            subdirs: list[dict[str, Any]] = []
            root_files_all: list[str] = []
            for se in sub_entries:
                if se.is_dir():
                    try:
                        file_count = sum(1 for f in se.iterdir() if f.is_file())
                    except PermissionError:
                        file_count = 0
                    subdirs.append({"name": se.name, "files": file_count})
                else:
                    root_files_all.append(se.name)
            item["subdirs"] = subdirs
            # Store ALL root-level files; renderers apply display cap unless --full
            item["root_files"] = root_files_all
            item["root_files_total"] = len(root_files_all)

            # Walk for extensions and total size
            ext_counts: dict[str, int] = {}
            total_files = 0
            total_bytes = 0
            for dirpath, _, filenames in os.walk(entry):
                for fn in filenames:
                    total_files += 1
                    fp = Path(dirpath) / fn
                    try:
                        total_bytes += fp.stat().st_size
                    except OSError:
                        pass
                    ext = Path(fn).suffix.lower() or "(no ext)"
                    ext_counts[ext] = ext_counts.get(ext, 0) + 1
            item["total_files"] = total_files
            item["extensions"] = ext_counts
            item["size_bytes"] = total_bytes
            item["size_human"] = _human_size(total_bytes)
        else:
            item["type"] = "file"
            item["ext"] = entry.suffix.lower()
            try:
                b = entry.stat().st_size
            except OSError:
                b = 0
            item["size_bytes"] = b
            item["size_human"] = _human_size(b)
            item["total_files"] = 1
            item["extensions"] = {entry.suffix.lower(): 1}
            item["subdirs"] = []

        items.append(item)

    return items


def build_triage_context(root: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    """Build the full triage context dict.

    Raises SystemExit if [triage] section is missing from config.

    Returns dict with:
      library_name, library_root, generated_at,
      naming_rules, source_prefixes, categories,
      items (from scan_unsorted), item_count
    """
    if "triage" not in cfg:
        _die(
            "The [triage] section is missing from courses.toml.\n"
            "Add [[triage.categories]] entries to use the triage command.\n"
            f"Config file: {root / 'courses.toml'}"
        )

    from datetime import datetime, timezone

    naming = cfg["naming"]
    triage_cats = cfg["triage"].get("categories", [])
    items = scan_unsorted(root, cfg)

    # Prompt defaults — used if [triage.prompt] is absent from courses.toml
    _default_prompt = {
        "title": "AI Task Prompt",
        "preamble": "For each item above, provide:",
        "instructions": [
            "Suggested target path         (category/subtopic/ from the Decision Guide)",
            "Suggested renamed folder/file (Source_CourseName naming convention)",
            "The exact `mv` shell command  (use full BASE path shown below)",
            "Confidence level              (high / medium / low)",
            "Notes  (e.g. \"strip [TutsNode.com] prefix\", \"create new subtopic\")",
        ],
    }
    prompt = cfg["triage"].get("prompt", _default_prompt)

    return {
        "library_name": cfg["library"]["name"],
        "library_root": str(root),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "naming_rules": naming.get("rules", {}),
        "source_prefixes": naming.get("source_prefixes", {}),
        "categories": triage_cats,
        "items": items,
        "item_count": len(items),
        "prompt": prompt,
    }


# ── Renderers — count ──────────────────────────────────────────────────────────

def render_count_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No courses found."
    col_w = max(len(r["path"]) for r in rows)
    col_w = max(col_w, 12)
    # Cap at 80 so paths don't push the table out of view
    col_w = min(col_w, 80)
    line_w = col_w + 32
    header = f"{'Course Path':<{col_w}} | Subdirs | Videos | Summary"
    sep = "─" * line_w
    lines = [header, sep]
    for r in rows:
        path = r["path"]
        # Truncate very long paths with ellipsis
        if len(path) > col_w:
            path = path[: col_w - 1] + "…"
        lines.append(
            f"{path:<{col_w}} | {r['sections']:>7} | {r['videos']:>6} | {r['summary']}"
        )
    lines.append(sep)
    total_c = len(rows)
    total_v = sum(r["videos"] for r in rows)
    lines.append(f"  {total_c} courses  ·  {total_v:,} total video lessons")
    return "\n".join(lines)


def render_count_markdown(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "_No courses found._"
    lines = ["| Course Path | Sections | Videos | Summary |", "|-------------|----------|--------|---------|"]
    for r in rows:
        lines.append(f"| `{r['path']}` | {r['sections']} | {r['videos']} | {r['summary']} |")
    total_v = sum(r["videos"] for r in rows)
    lines.append(f"\n**{len(rows)} courses · {total_v:,} total video lessons**")
    return "\n".join(lines)


def render_count_json(rows: list[dict[str, Any]]) -> str:
    total_v = sum(r["videos"] for r in rows)
    return json.dumps({"courses": rows, "total_courses": len(rows), "total_videos": total_v}, indent=2)


# ── Renderers — lint ───────────────────────────────────────────────────────────

def render_lint_text(violations: list[dict[str, str]]) -> str:
    if not violations:
        return "ok  All directories match formatting conventions."
    lines = [f"FAIL  {len(violations)} violation(s) found:"]
    for v in violations:
        lines.append(f"  - {v['message']}")
    return "\n".join(lines)


def render_lint_markdown(violations: list[dict[str, str]]) -> str:
    if not violations:
        return "**All directories match formatting conventions.**"
    lines = [f"**{len(violations)} violation(s) found:**", ""]
    for v in violations:
        lines.append(f"- {v['message']}")
    return "\n".join(lines)


def render_lint_json(violations: list[dict[str, str]]) -> str:
    return json.dumps({"violations": violations, "count": len(violations), "clean": len(violations) == 0}, indent=2)


# ── Renderers — print (tree) ──────────────────────────────────────────────────

def render_tree_text(tree: list[dict[str, Any]]) -> str:
    """Render the library tree with box-drawing characters."""
    lines: list[str] = []
    for ci, cat in enumerate(tree):
        is_last_cat = ci == len(tree) - 1
        cat_prefix = "└── " if is_last_cat else "├── "
        sub_indent = "    " if is_last_cat else "│   "

        # Category header line
        total_subs = sum(1 for s in cat["subtopics"] if s["name"])
        cat_anno = f"({total_subs} subtopics, {cat['total_videos']:,} lessons)" if total_subs else f"({cat['total_videos']:,} lessons)"
        lines.append(f"{cat_prefix}{cat['name']}/  {cat_anno}")

        subs = cat["subtopics"]
        for si, sub in enumerate(subs):
            is_last_sub = si == len(subs) - 1
            sub_prefix = sub_indent + ("└── " if is_last_sub else "├── ")
            crs_indent = sub_indent + ("    " if is_last_sub else "│   ")

            if sub["name"]:
                sub_anno = f"({len(sub['courses'])} courses)"
                lines.append(f"{sub_prefix}{sub['name']}/  {sub_anno}")
            else:
                crs_indent = sub_indent

            courses = sub["courses"]
            for cri, course in enumerate(courses):
                is_last_crs = cri == len(courses) - 1
                crs_prefix = crs_indent + ("└── " if is_last_crs else "├── ")
                lines.append(f"{crs_prefix}{course['course']}  {course['summary']}")

    return "\n".join(lines)


def render_tree_markdown(tree: list[dict[str, Any]]) -> str:
    inner = render_tree_text(tree)
    return f"```\n{inner}\n```"


def render_tree_json(tree: list[dict[str, Any]]) -> str:
    return json.dumps(tree, indent=2)


# ── Renderers — summary ───────────────────────────────────────────────────────

def render_summary_text(
    rows: list[dict[str, Any]],
    violations: list[dict[str, str]],
    cfg: dict[str, Any],
    root: Path,
) -> str:
    lib_name = cfg["library"]["name"]
    total_v = sum(r["videos"] for r in rows)
    total_c = len(rows)
    unsorted_name = cfg["library"]["unsorted_dir"]
    unsorted_path = root / unsorted_name
    unsorted_count = 0
    if unsorted_path.exists():
        try:
            unsorted_count = sum(1 for _ in unsorted_path.iterdir())
        except PermissionError:
            pass
    unsorted_msg = f"{unsorted_name}/ — empty" if unsorted_count == 0 else f"{unsorted_name}/ — {unsorted_count} item(s) awaiting sorting"
    lint_msg = "ok  All directories match conventions." if not violations else f"FAIL  {len(violations)} violation(s) found — run lint for details."
    width = 56
    border_top = "╔" + "═" * width + "╗"
    border_bot = "╚" + "═" * width + "╝"
    title = f"{lib_name} — Health Report"
    title_padded = title.center(width)
    lines = [
        border_top,
        f"║{title_padded}║",
        border_bot,
        "",
        f"  Naming lint  {lint_msg}",
        f"  Courses      {total_c} courses",
        f"  Videos       {total_v:,} total video lessons",
    ]
    prog_name = os.path.basename(sys.argv[0]) if (sys.argv and sys.argv[0]) else "curator"
    lines += [
        "",
        f"  Run  ./{prog_name} print   for full hierarchy.",
        f"  Run  ./{prog_name} lint    for detailed violations.",
        f"  Run  ./{prog_name} triage  to sort unsorted courses.",
    ]
    return "\n".join(lines)


def render_summary_markdown(
    rows: list[dict[str, Any]],
    violations: list[dict[str, str]],
    cfg: dict[str, Any],
    root: Path,
) -> str:
    lib_name = cfg["library"]["name"]
    total_v = sum(r["videos"] for r in rows)
    total_c = len(rows)
    unsorted_name = cfg["library"]["unsorted_dir"]
    unsorted_path = root / unsorted_name
    unsorted_count = 0
    if unsorted_path.exists():
        try:
            unsorted_count = sum(1 for _ in unsorted_path.iterdir())
        except PermissionError:
            pass
    lint_msg = "All directories match conventions." if not violations else f"{len(violations)} violation(s) found."
    lines = [
        f"## {lib_name} — Health Report",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Naming lint | {lint_msg} |",
        f"| Courses | {total_c} |",
        f"| Videos | {total_v:,} total video lessons |",
        f"| Unsorted | {unsorted_name}/ — {'empty' if unsorted_count == 0 else f'{unsorted_count} item(s)'} |",
    ]
    return "\n".join(lines)


def render_summary_json(
    rows: list[dict[str, Any]],
    violations: list[dict[str, str]],
    cfg: dict[str, Any],
    root: Path,
) -> str:
    lib_name = cfg["library"]["name"]
    total_v = sum(r["videos"] for r in rows)
    total_c = len(rows)
    unsorted_name = cfg["library"]["unsorted_dir"]
    unsorted_path = root / unsorted_name
    unsorted_count = 0
    if unsorted_path.exists():
        try:
            unsorted_count = sum(1 for _ in unsorted_path.iterdir())
        except PermissionError:
            pass
    return json.dumps({
        "library": lib_name,
        "courses": total_c,
        "videos": total_v,
        "violations": len(violations),
        "clean": len(violations) == 0,
        "unsorted_count": unsorted_count,
    }, indent=2)


# ── Renderers — triage ────────────────────────────────────────────────────────

def render_triage_text(ctx: dict[str, Any], full: bool = False) -> str:
    _SUBDIRS_LIMIT = 6
    _ROOT_FILES_LIMIT = 10
    sep = "━" * 60
    # Header label: "Item X of N" in --each mode, otherwise item count
    label = ctx.get("_each_label") or f"{ctx['item_count']} item(s) awaiting sorting"
    lines = [
        sep,
        f"  COURSE TRIAGE CONTEXT — {ctx['library_name']}",
        f"  Generated: {ctx['generated_at']}  ·  {label}",
        sep,
        "",
        "## SECTION 1 — Library Rules",
        "(read from courses.toml — authoritative)",
        "",
    ]

    # Naming rules
    rules = ctx.get("naming_rules", {})
    if rules:
        lines.append("  Naming conventions:")
        for k, v in rules.items():
            lines.append(f"    {k:<12}: {v}")
        lines.append("")

    # Source prefixes
    prefixes = ctx.get("source_prefixes", {})
    if prefixes:
        lines.append("  Common source prefixes:")
        for publisher, prefix in prefixes.items():
            lines.append(f"    {publisher} → {prefix}")
        lines.append("")

    # Category decision guide
    cats = ctx.get("categories", [])
    if cats:
        lines.append("  Category Decision Guide:")
        lines.append("  ┌" + "─" * 66 + "┐")
        for entry in cats:
            kws = ", ".join(entry.get("keywords", []))
            target = entry.get("target", "")
            note = entry.get("notes", "")
            row = f"  │  {kws:<38} → {target}"
            if note:
                row += f"  [{note}]"
            lines.append(row)
        lines.append("  └" + "─" * 66 + "┘")
        lines.append("")

    # Section 2
    lines += ["## SECTION 2 — Unsorted Directory Scan", ""]
    items = ctx["items"]
    if not items:
        lines.append(f"  {ctx['library_name']} unsorted dir — empty")
    else:
        lines.append(f"  0x0_unsorted/  ({len(items)} item(s))")
        lines.append("")
        for i, item in enumerate(items, 1):
            lines.append(f"  ┌─ [{i}] \"{item['name']}\" {'─' * max(1, 48 - len(item['name']))}")
            lines.append(f"  │  Type        : {item['type']}")
            if item["type"] == "dir":
                subdirs = item.get("subdirs", [])
                lines.append(f"  │  Subdirs     : {len(subdirs)}" + (" (flat)" if not subdirs else ""))
                display_subdirs = subdirs if full else subdirs[:_SUBDIRS_LIMIT]
                for sd in display_subdirs:
                    lines.append(f"  │    ├── {sd['name']:<40} ({sd['files']} files)")
                if not full and len(subdirs) > _SUBDIRS_LIMIT:
                    lines.append(f"  │    └── ... ({len(subdirs) - _SUBDIRS_LIMIT} more)")
                # Root-level files (most useful for source identification)
                root_files = item.get("root_files", [])
                root_files_total = item.get("root_files_total", 0)
                if root_files:
                    lines.append(f"  │  Files (root): {root_files_total} file(s) directly in dir")
                    display_rf = root_files if full else root_files[:_ROOT_FILES_LIMIT]
                    for rf in display_rf:
                        lines.append(f"  │    ├── {rf}")
                    if not full and root_files_total > _ROOT_FILES_LIMIT:
                        lines.append(f"  │    └── ... ({root_files_total - _ROOT_FILES_LIMIT} more)")
            else:
                lines.append(f"  │  Extension   : {item.get('ext', '')}")
            lines.append(f"  │  Total files : {item['total_files']}")
            exts = item.get("extensions", {})
            ext_str = "  ".join(f"{e} ({c})" for e, c in sorted(exts.items(), key=lambda x: -x[1]))
            lines.append(f"  │  Extensions  : {ext_str}")
            lines.append(f"  │  Total size  : {item['size_human']}")
            lines.append(f"  └{'─' * 66}")
            lines.append("")

    # Section 3
    prompt = ctx.get("prompt", {})
    title = prompt.get("title", "AI Task Prompt")
    preamble = prompt.get("preamble", "For each item above, provide:")
    instructions = prompt.get("instructions", [])
    lines += [
        f"## SECTION 3 — {title}",
        "",
        f"  {preamble}",
    ]
    for i, step in enumerate(instructions, 1):
        lines.append(f"    {i}. {step}")
    lines += [
        "",
        f"  Library root (BASE): {ctx['library_root']}",
        sep,
    ]
    return "\n".join(lines)


def render_triage_markdown(ctx: dict[str, Any], full: bool = False) -> str:
    _SUBDIRS_LIMIT = 6
    _ROOT_FILES_LIMIT = 10
    label = ctx.get("_each_label") or f"{ctx['item_count']} item(s) awaiting sorting"
    lines = [
        f"# Course Triage Context — {ctx['library_name']}",
        "",
        f"**Generated:** {ctx['generated_at']}  |  **{label}**",
        "",
        "---",
        "",
        "## Section 1 — Library Rules",
        "",
    ]

    rules = ctx.get("naming_rules", {})
    if rules:
        lines.append("### Naming Conventions")
        lines.append("")
        lines.append("| Level | Rule |")
        lines.append("|-------|------|")
        for k, v in rules.items():
            lines.append(f"| {k} | {v} |")
        lines.append("")

    prefixes = ctx.get("source_prefixes", {})
    if prefixes:
        lines.append("### Common Source Prefixes")
        lines.append("")
        lines.append("| Publisher / Platform | Prefix |")
        lines.append("|---------------------|--------|")
        for publisher, prefix in prefixes.items():
            lines.append(f"| {publisher} | `{prefix}` |")
        lines.append("")

    cats = ctx.get("categories", [])
    if cats:
        lines.append("### Category Decision Guide")
        lines.append("")
        lines.append("| Keywords | Target Path | Notes |")
        lines.append("|----------|-------------|-------|")
        for entry in cats:
            kws = ", ".join(f"`{k}`" for k in entry.get("keywords", []))
            target = f"`{entry.get('target', '')}`"
            note = entry.get("notes", "")
            lines.append(f"| {kws} | {target} | {note} |")
        lines.append("")

    lines += ["---", "", "## Section 2 — Unsorted Directory Scan", ""]
    items = ctx["items"]
    if not items:
        lines.append("_Unsorted directory is empty._")
    else:
        for i, item in enumerate(items, 1):
            lines.append(f"### [{i}] `{item['name']}`")
            lines.append("")
            lines.append(f"- **Type:** {item['type']}")
            if item["type"] == "dir":
                subdirs = item.get("subdirs", [])
                lines.append(f"- **Subdirs:** {len(subdirs)}")
                display_subdirs = subdirs if full else subdirs[:_SUBDIRS_LIMIT]
                for sd in display_subdirs:
                    lines.append(f"  - `{sd['name']}` ({sd['files']} files)")
                if not full and len(subdirs) > _SUBDIRS_LIMIT:
                    lines.append(f"  - _...{len(subdirs) - _SUBDIRS_LIMIT} more_")
                root_files = item.get("root_files", [])
                root_files_total = item.get("root_files_total", 0)
                if root_files:
                    lines.append(f"- **Files (root):** {root_files_total} file(s) directly in dir")
                    display_rf = root_files if full else root_files[:_ROOT_FILES_LIMIT]
                    for rf in display_rf:
                        lines.append(f"  - `{rf}`")
                    if not full and root_files_total > _ROOT_FILES_LIMIT:
                        lines.append(f"  - _...{root_files_total - _ROOT_FILES_LIMIT} more_")
            else:
                lines.append(f"- **Extension:** `{item.get('ext', '')}`")
            lines.append(f"- **Total files:** {item['total_files']}")
            exts = item.get("extensions", {})
            ext_str = ", ".join(f"`{e}` ({c})" for e, c in sorted(exts.items(), key=lambda x: -x[1]))
            lines.append(f"- **Extensions:** {ext_str}")
            lines.append(f"- **Total size:** {item['size_human']}")
            lines.append("")

    prompt = ctx.get("prompt", {})
    title = prompt.get("title", "AI Task Prompt")
    preamble = prompt.get("preamble", "For each item above, provide:")
    instructions = prompt.get("instructions", [])
    lines += [
        "---",
        "",
        f"## Section 3 — {title}",
        "",
        preamble,
        "",
    ]
    for i, step in enumerate(instructions, 1):
        lines.append(f"{i}. {step}")
    lines += [
        "",
        f"**Library root (BASE):** `{ctx['library_root']}`",
    ]
    return "\n".join(lines)


def render_triage_json(ctx: dict[str, Any]) -> str:
    # Strip internal keys before serialising
    clean = {k: v for k, v in ctx.items() if not k.startswith("_")}
    return json.dumps(clean, indent=2)


def render_triage_each(
    ctx: dict[str, Any],
    fmt: str = "text",
    full: bool = False,
) -> str:
    """Render one complete triage block per unsorted item.

    Each block is self-contained: Section 1 (rules) + Section 2 (single item) +
    Section 3 (prompt).  Blocks are joined by a blank line so the user can copy
    them individually.
    """
    items = ctx["items"]
    if not items:
        # Nothing to split — fall through to normal render
        if fmt == "markdown":
            return render_triage_markdown(ctx, full=full)
        elif fmt == "json":
            return render_triage_json(ctx)
        else:
            return render_triage_text(ctx, full=full)

    total = len(items)
    blocks: list[str] = []
    for idx, item in enumerate(items, 1):
        sub_ctx = {
            **ctx,
            "items": [item],
            "item_count": 1,
            "_each_label": f"Item {idx} of {total}",
        }
        if fmt == "markdown":
            blocks.append(render_triage_markdown(sub_ctx, full=full))
        elif fmt == "json":
            blocks.append(render_triage_json(sub_ctx))
        else:
            blocks.append(render_triage_text(sub_ctx, full=full))

    if fmt == "json":
        # Wrap as a JSON array
        return "[\n" + ",\n".join(blocks) + "\n]"
    elif fmt == "markdown":
        return "\n\n---\n\n".join(blocks)
    else:
        return "\n\n".join(blocks)


# ── Utilities ──────────────────────────────────────────────────────────────────

def _human_size(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024  # type: ignore[assignment]
    return f"{b:.1f} PB"


def _die(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)
