#!/usr/bin/env python3
"""Read-only acceptance checks for the Second Brain system layer."""

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path


def read_text(path):
    return path.read_text(encoding="utf-8", errors="replace")


def frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    result = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return result
        if line and not line[0].isspace() and ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def section(text, heading):
    marker = "## " + heading
    start = text.find(marker)
    if start < 0:
        return ""
    end = text.find("\n---", start)
    return text[start:end if end >= 0 else None].strip()


def markdown_hashes(root):
    result = {}
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


class Suite:
    def __init__(self):
        self.results = []

    def check(self, name, condition, detail=""):
        self.results.append((name, bool(condition), detail))

    @property
    def failed(self):
        return [item for item in self.results if not item[1]]


def run(root):
    suite = Suite()
    system = root / "00-System"
    required = [
        root / "RESEARCH_PROTOCOL.md",
        root / "AGENTS.md",
        root / "CLAUDE.md",
        root / "index.md",
        system / "START-HERE.md",
        system / "ENGINEERING-CONTRACT.md",
        system / "LINK-REGISTRY.md",
        system / "MAINTENANCE.md",
        system / "Scripts" / "lint-vault.py",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    suite.check("Core system files exist", not missing, ", ".join(missing))

    agents = read_text(root / "AGENTS.md")
    claude = read_text(root / "CLAUDE.md")
    agents_bootstrap = section(agents, "Bootstrap and Scoped Context")
    claude_bootstrap = section(claude, "Bootstrap and Scoped Context")
    suite.check("AGENTS and CLAUDE bootstrap blocks match", agents_bootstrap == claude_bootstrap and bool(agents_bootstrap))

    start = read_text(system / "START-HERE.md")
    contract = read_text(system / "ENGINEERING-CONTRACT.md")
    context_terms = ["6,000 tokens", "no more than five", "25%", "Do not begin by recursively reading"]
    suite.check("Scoped context budget is explicit", all(term in start for term in context_terms))
    suite.check("Index-first retrieval is explicit", "Search `index.md`" in start and "Load only the notes" in start)
    suite.check("Default query behavior is non-writing", "answer without saving" in start and "Write Gate" in start)

    graph_terms = [
        "node_id", "inputs", "output_schema", "dependencies", "parallel_safe",
        "completion_gate", "failure_behavior", "fan-out", "barrier", "Reduce",
        "Fresh-Context Verification", "fake-edge", "pipeline", "anchors",
    ]
    suite.check("Workflow graph contract is complete", all(term.casefold() in contract.casefold() for term in graph_terms))
    link_terms = ["resolved", "planned", "broken", "renamed", "external-to-wiki", "meaningful links"]
    suite.check("Knowledge graph classifications are explicit", all(term in contract for term in link_terms))

    project_dirs = sorted(path for path in (root / "03-Projects").iterdir() if path.is_dir())
    project_failures = []
    for project in project_dirs:
        state = project / "PROJECT-STATE.md"
        decisions = project / "DECISIONS.md"
        if not state.exists() or not decisions.exists():
            project_failures.append(project.name)
            continue
        meta = frontmatter(read_text(state))
        if meta.get("canonical_state", "").casefold() != "true":
            project_failures.append(project.name + " (not canonical)")
    suite.check("Every project has canonical state and decisions", len(project_dirs) == 3 and not project_failures, ", ".join(project_failures))

    freshness_files = []
    freshness_failures = []
    for path in sorted((root / "02-Wiki").glob("*.md")):
        meta = frontmatter(read_text(path))
        if meta.get("freshness_class") in {"dynamic", "periodic"}:
            freshness_files.append(path.name)
            if not meta.get("valid_as_of") or not meta.get("review_after"):
                freshness_failures.append(path.name)
    suite.check("Time-sensitive wiki notes carry freshness dates", len(freshness_files) >= 16 and not freshness_failures, ", ".join(freshness_failures))

    maintenance = read_text(system / "MAINTENANCE.md")
    maintenance_terms = ["Weekly Check", "Monthly Check", "Milestone or Quarterly Check", "approval", "read-only"]
    suite.check("Maintenance rhythm and approval gates exist", all(term.casefold() in maintenance.casefold() for term in maintenance_terms))

    before = markdown_hashes(root)
    lint = subprocess.run(
        [sys.executable, str(system / "Scripts" / "lint-vault.py"), "--root", str(root)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    after = markdown_hashes(root)
    suite.check("Linter passes without critical issues", lint.returncode == 0 and "**Result:** PASS" in lint.stdout, lint.stderr.strip())
    changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    suite.check("Linter leaves every Markdown file unchanged", not changed, ", ".join(changed))
    suite.check("Index and link registry are synchronized", "**Indexed wiki pages:** 204/204" in lint.stdout and "registry drift" not in lint.stdout.casefold())

    # These checks validate that the two behavioral walkthroughs have enforceable
    # routing rules. Actual model behavior remains observable only during use.
    suite.check("Scoped-query walkthrough has a bounded route", "Up to five candidate wiki notes" in start and "Original source passages only when verification is required" in start)
    suite.check("Graph walkthrough has independent verification", "normalized worker artifacts" in contract and "should not receive worker chain-of-thought" in contract)

    return suite


def render(suite):
    passed = len(suite.results) - len(suite.failed)
    output = [
        "# Vault System Acceptance Results",
        "",
        "**Result:** {}".format("PASS" if not suite.failed else "FAIL"),
        "",
        "**Checks:** {}/{} passed".format(passed, len(suite.results)),
        "",
        "## Automated Checks",
        "",
    ]
    for name, ok, detail in suite.results:
        line = "- [{}] {}".format("x" if ok else " ", name)
        if detail and not ok:
            line += " — " + detail
        output.append(line)
    output.extend([
        "",
        "## Scope",
        "",
        "The suite validates structure, contracts, synchronization, and non-mutation. It does not certify the truth of every research claim or guarantee future agent behavior.",
        "",
    ])
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Read-only Second Brain system acceptance tests")
    parser.add_argument("--root", type=Path, help="Vault root (defaults to two levels above this script)")
    args = parser.parse_args()
    root = (args.root or Path(__file__).resolve().parents[2]).resolve()
    suite = run(root)
    print(render(suite))
    return 1 if suite.failed else 0


if __name__ == "__main__":
    sys.exit(main())
