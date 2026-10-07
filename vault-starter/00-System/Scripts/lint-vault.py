#!/usr/bin/env python3
"""Read-only structural health check for the Second Brain vault.

The script writes only a Markdown report to stdout. It never edits the vault.
"""

import argparse
import hashlib
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path


WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
REQUIRED_WIKI_FIELDS = {
    "title", "created", "updated", "language", "tags", "aliases",
    "page_type", "status", "sources",
}
ALLOWED_WIKI_STATUSES = {"needs-verification", "reviewed"}
REQUIRED_PROJECT_FIELDS = {
    "project", "status", "updated", "freshness_class", "valid_as_of",
    "review_after", "canonical_state",
}


def read_text(path):
    return path.read_text(encoding="utf-8", errors="replace")


def frontmatter(text):
    """Return a minimal top-level YAML mapping without requiring PyYAML."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    result = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return result
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def parse_inline_list(value):
    value = (value or "").strip()
    if not (value.startswith("[") and value.endswith("]")):
        return []
    return [item.strip().strip('"').strip("'") for item in value[1:-1].split(",") if item.strip()]


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def link_target(raw):
    target = raw.split("|", 1)[0].split("#", 1)[0].strip()
    return Path(target).name if target else ""


def links(text):
    return [link_target(match) for match in WIKILINK_RE.findall(text) if link_target(match)]


def potential_atomic_links(text):
    """Collect links inside sections titled Potential Atomic Pages."""
    collected = []
    active_level = None
    for line in text.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip().casefold()
            if title == "potential atomic pages":
                active_level = level
            elif active_level is not None and level <= active_level:
                active_level = None
        if active_level is not None:
            collected.extend(links(line))
    return collected


def registry_section(text, heading):
    found = False
    values = set()
    for line in text.splitlines():
        if line.strip() == "## " + heading:
            found = True
            continue
        if found and line.startswith("## "):
            break
        if found:
            match = re.match(r"^- `([^`]+)`", line)
            if match:
                values.add(match.group(1))
    return values


def short_list(items, limit=12):
    items = sorted(items, key=str.casefold)
    shown = ", ".join("`{}`".format(item) for item in items[:limit])
    if len(items) > limit:
        shown += " … (+{} more)".format(len(items) - limit)
    return shown or "none"


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def markdown_report(root):
    today = date.today()
    critical = []
    warnings = []
    metrics = []

    wiki_dir = root / "02-Wiki"
    wiki_files = sorted(wiki_dir.glob("*.md"))
    all_md = [p for p in root.rglob("*.md") if ".git" not in p.parts]
    stems = {path.stem for path in all_md}
    stems_folded = {stem.casefold() for stem in stems}
    wiki_stems = {path.stem for path in wiki_files}

    missing_schema = []
    invalid_status = []
    statuses = Counter()
    freshness = Counter()
    freshness_missing = []
    freshness_overdue = []
    identity_owners = defaultdict(set)
    title_owners = defaultdict(set)

    wiki_texts = {}
    for path in wiki_files:
        text = read_text(path)
        wiki_texts[path] = text
        meta = frontmatter(text)
        missing = sorted(REQUIRED_WIKI_FIELDS - set(meta))
        if missing:
            missing_schema.append("{} ({})".format(path.name, ", ".join(missing)))
        status = meta.get("status", "<missing>")
        statuses[status] += 1
        if status not in ALLOWED_WIKI_STATUSES:
            invalid_status.append("{} ({})".format(path.name, status))

        title = meta.get("title", "").strip()
        if title:
            title_owners[title.casefold()].add(path.name)
            identity_owners[title.casefold()].add(path.name)
        for alias in parse_inline_list(meta.get("aliases")):
            identity_owners[alias.casefold()].add(path.name)

        freshness_class = meta.get("freshness_class", "").strip()
        if freshness_class:
            freshness[freshness_class] += 1
        if freshness_class in {"dynamic", "periodic"}:
            absent = [field for field in ("valid_as_of", "review_after") if not meta.get(field)]
            if absent:
                freshness_missing.append("{} ({})".format(path.name, ", ".join(absent)))
            review_date = parse_date(meta.get("review_after"))
            if review_date and review_date < today:
                freshness_overdue.append(path.name)

    if missing_schema:
        critical.append("Wiki frontmatter fields are missing: " + short_list(missing_schema))
    if invalid_status:
        critical.append("Wiki pages have an unsupported status: " + short_list(invalid_status))
    if freshness_missing:
        warnings.append("Dynamic/periodic wiki pages lack freshness dates: " + short_list(freshness_missing))
    if freshness_overdue:
        warnings.append("Wiki pages are due for a freshness review: " + short_list(freshness_overdue))

    duplicate_titles = ["{} -> {}".format(name, sorted(owners)) for name, owners in title_owners.items() if len(owners) > 1]
    identity_collisions = ["{} -> {}".format(name, sorted(owners)) for name, owners in identity_owners.items() if len(owners) > 1]
    if duplicate_titles:
        critical.append("Duplicate page titles: " + short_list(duplicate_titles))
    if identity_collisions:
        warnings.append("Title/alias collisions need review: " + short_list(identity_collisions))

    index_path = root / "index.md"
    if not index_path.exists():
        critical.append("`index.md` is missing.")
        indexed_wiki = set()
    else:
        index_targets = {target.casefold() for target in links(read_text(index_path))}
        indexed_wiki = {stem for stem in wiki_stems if stem.casefold() in index_targets}
        missing_from_index = wiki_stems - indexed_wiki
        absent_index_targets = {target for target in links(read_text(index_path)) if target.casefold() not in stems_folded}
        if missing_from_index:
            critical.append("Wiki pages absent from `index.md`: " + short_list(missing_from_index))
        if absent_index_targets:
            critical.append("`index.md` points to absent targets: " + short_list(absent_index_targets))

    missing_occurrences = []
    planned = set()
    wiki_incoming = Counter()
    for source, text in wiki_texts.items():
        source_planned = set(potential_atomic_links(text))
        for target in links(text):
            if target.casefold() in {stem.casefold() for stem in wiki_stems}:
                canonical = next(stem for stem in wiki_stems if stem.casefold() == target.casefold())
                if canonical != source.stem:
                    wiki_incoming[canonical] += 1
            elif target.casefold() not in stems_folded:
                missing_occurrences.append(target)
                if target in source_planned:
                    planned.add(target)
    missing_unique = set(missing_occurrences)
    broken = missing_unique - planned

    registry_path = root / "00-System" / "LINK-REGISTRY.md"
    if not registry_path.exists():
        critical.append("`00-System/LINK-REGISTRY.md` is missing.")
    else:
        registry_text = read_text(registry_path)
        registered_planned = registry_section(registry_text, "Explicitly Planned Targets")
        registered_broken = registry_section(registry_text, "Broken-by-Rule Review Queue")
        if planned != registered_planned:
            critical.append("Planned-link registry drift: current {}, registry {}.".format(len(planned), len(registered_planned)))
        if broken != registered_broken:
            critical.append("Broken-link registry drift: current {}, registry {}.".format(len(broken), len(registered_broken)))
    if broken:
        warnings.append("The classified broken-link review queue contains {} targets; no automatic repair is authorized.".format(len(broken)))

    orphans = sorted(stem for stem in wiki_stems if wiki_incoming[stem] == 0)
    if orphans:
        warnings.append("Wiki-to-wiki incoming-link count is zero for {} pages: {}".format(len(orphans), short_list(orphans)))

    digest_owners = defaultdict(list)
    for path in all_md:
        digest_owners[file_hash(path)].append(str(path.relative_to(root)))
    exact_duplicates = [paths for paths in digest_owners.values() if len(paths) > 1]
    if exact_duplicates:
        warnings.append("Exact duplicate Markdown content occurs in {} groups; review only, do not auto-delete: {}".format(
            len(exact_duplicates), short_list([" = ".join(group) for group in exact_duplicates], limit=5)))

    projects_dir = root / "03-Projects"
    project_dirs = sorted(path for path in projects_dir.iterdir() if path.is_dir()) if projects_dir.exists() else []
    project_issues = []
    project_freshness = []
    for project_dir in project_dirs:
        state_path = project_dir / "PROJECT-STATE.md"
        decisions_path = project_dir / "DECISIONS.md"
        if not state_path.exists():
            project_issues.append("{}: PROJECT-STATE.md missing".format(project_dir.name))
        if not decisions_path.exists():
            project_issues.append("{}: DECISIONS.md missing".format(project_dir.name))
        if state_path.exists():
            meta = frontmatter(read_text(state_path))
            missing = REQUIRED_PROJECT_FIELDS - set(meta)
            if missing:
                project_issues.append("{}: missing {}".format(project_dir.name, ", ".join(sorted(missing))))
            if meta.get("canonical_state", "").casefold() != "true":
                project_issues.append("{}: canonical_state is not true".format(project_dir.name))
            freshness_class = meta.get("freshness_class", "")
            review_value = meta.get("review_after", "")
            if freshness_class == "dynamic" and not review_value:
                project_issues.append("{}: dynamic state lacks review_after".format(project_dir.name))
            elif freshness_class == "periodic" and not review_value:
                project_freshness.append("{}: set review_after at the next known milestone".format(project_dir.name))
            review_date = parse_date(review_value)
            if review_date and review_date < today:
                project_freshness.append("{}: review was due {}".format(project_dir.name, review_date.isoformat()))
    if project_issues:
        critical.append("Project-state contract failures: " + short_list(project_issues))
    if project_freshness:
        warnings.append("Project-state freshness attention: " + short_list(project_freshness))

    sources_path = root / "01-Library" / "Sources-In-Progress.md"
    source_age = None
    if sources_path.exists():
        match = re.search(r"\*\*Last reconciled:\*\*\s*(\d{4}-\d{2}-\d{2})", read_text(sources_path))
        reconciled = parse_date(match.group(1)) if match else None
        if reconciled:
            source_age = (today - reconciled).days
            if source_age > 14:
                warnings.append("`Sources-In-Progress.md` was last reconciled {} days ago.".format(source_age))
        else:
            warnings.append("`Sources-In-Progress.md` has no parseable Last reconciled date.")
    else:
        critical.append("`01-Library/Sources-In-Progress.md` is missing.")

    metrics.extend([
        ("Wiki pages", len(wiki_files)),
        ("Indexed wiki pages", "{}/{}".format(len(indexed_wiki), len(wiki_files))),
        ("Wiki statuses", ", ".join("{}={}".format(key, statuses[key]) for key in sorted(statuses))),
        ("Freshness-classified wiki pages", ", ".join("{}={}".format(key, freshness[key]) for key in sorted(freshness)) or "0"),
        ("Missing link occurrences", len(missing_occurrences)),
        ("Explicitly planned missing targets", len(planned)),
        ("Broken-by-rule targets", len(broken)),
        ("Wiki-to-wiki zero-incoming pages", len(orphans)),
        ("Project areas checked", len(project_dirs)),
        ("Source-state age", "{} days".format(source_age) if source_age is not None else "unknown"),
    ])

    result = "PASS" if not critical else "FAIL"
    output = [
        "# Vault Health Report",
        "",
        "**Generated:** {}".format(today.isoformat()),
        "",
        "**Result:** {}".format(result),
        "",
        "This is a read-only structural check. Warnings are review queues, not authorization to rewrite or delete notes.",
        "",
        "## Critical Issues",
        "",
    ]
    output.extend(["- " + item for item in critical] or ["- None."])
    output.extend(["", "## Warnings", ""])
    output.extend(["- " + item for item in warnings] or ["- None."])
    output.extend(["", "## Metrics", ""])
    output.extend(["- **{}:** {}".format(name, value) for name, value in metrics])
    output.extend(["", "## Interpretation", ""])
    if critical:
        output.append("Resolve critical structural drift before relying on automated routing or write-back.")
    else:
        output.append("The structural contract passes. Address warnings through deliberate review; do not auto-fix them.")
    return "\n".join(output) + "\n", critical, warnings


def main():
    parser = argparse.ArgumentParser(description="Read-only Second Brain vault linter")
    parser.add_argument("--root", type=Path, help="Vault root (defaults to two levels above this script)")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when warnings exist")
    args = parser.parse_args()
    root = (args.root or Path(__file__).resolve().parents[2]).resolve()
    report, critical, warnings = markdown_report(root)
    sys.stdout.write(report)
    if critical or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
