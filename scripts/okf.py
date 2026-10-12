#!/usr/bin/env python3
"""Maintain an OKF v0.2 bundle (https://github.com/GoogleCloudPlatform/open-knowledge-format).

  okf.py check BUNDLE   conformance (SPEC 11) plus this repo's conventions
  okf.py index BUNDLE   regenerate every index.md from concept frontmatter
"""
import re
import sys
from pathlib import Path

RESERVED = {"index.md", "log.md"}
# Directory headings and descriptions for generated index.md files.
DIRS = {
    "": ("agentic-templates Resources", "Research that breeds and formations are built from."),
    "skills": ("Skills", "Agent Skills and Claude Code plugins: sources, usage, breed fit, security."),
    "portable-agents": ("Portable Agents", "Defining breeds independent of the agent vendor: instructions, skills, agent definitions, runtime, permissions."),
}
# Concepts listed first in their index (start-here documents).
FIRST = ("summary.md", "conventions.md")


def frontmatter(path):
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fm = {}
    for line in m.group(1).splitlines():
        km = re.match(r"([A-Za-z_]+): (.*)", line)
        if km:
            fm[km.group(1)] = km.group(2).strip().strip('"')
    return fm, text[m.end():]


def concepts(directory):
    files = [p for p in directory.glob("*.md") if p.name not in RESERVED]
    return sorted(files, key=lambda p: (p.name not in FIRST, FIRST.index(p.name) if p.name in FIRST else 0, p.name))


def index(bundle):
    for d in [bundle] + sorted(p for p in bundle.rglob("*") if p.is_dir()):
        rel = d.relative_to(bundle).as_posix()
        rel = "" if rel == "." else rel
        heading, blurb = DIRS.get(rel, (d.name, ""))
        out = []
        if rel == "":
            out += ['---', 'okf_version: "0.2"', '---', '']
        out += [f"# {heading}", ""]
        if blurb:
            out += [blurb, ""]
        items = []
        for p in concepts(d):
            fm, _ = frontmatter(p)
            items.append(f"* [{fm.get('title', p.stem)}]({p.name}) - {fm.get('description', '')}")
        if (d / "log.md").exists():
            items.append("* [Update Log](log.md) - chronological history of this bundle")
        for sub in sorted(p for p in d.iterdir() if p.is_dir()):
            srel = sub.relative_to(bundle).as_posix()
            items.append(f"* [{DIRS.get(srel, (sub.name, ''))[0]}]({sub.name}/) - {DIRS.get(srel, ('', ''))[1]}")
        out += items
        (d / "index.md").write_text("\n".join(out) + "\n")


def check(bundle):
    errors = []
    for p in sorted(bundle.rglob("*.md")):
        rel = p.relative_to(bundle)
        fm, body = frontmatter(p)
        if p.name == "index.md":
            if fm is not None and (p.parent != bundle or set(fm) - {"okf_version"}):
                errors.append(f"{rel}: index.md may only carry okf_version, at the bundle root")
            continue
        if p.name == "log.md":
            dates = re.findall(r"^## (.+)$", p.read_text(), re.M)
            if any(not re.fullmatch(r"\d{4}-\d{2}-\d{2}", x) for x in dates) or dates != sorted(dates, reverse=True):
                errors.append(f"{rel}: log dates must be YYYY-MM-DD, newest first")
            continue
        if fm is None or not fm.get("type"):
            errors.append(f"{rel}: missing frontmatter or type")
            continue
        text = p.read_text()
        ids = set(re.findall(r"^  - id: (\S+)", text, re.M))
        defined = set(re.findall(r"^\[\^([^\]]+)\]:", body, re.M))
        used = set(re.findall(r"\[\^([^\]]+)\](?!:)", body))
        if ids != defined or used != defined:
            errors.append(f"{rel}: footnotes and sources differ: {sorted(ids ^ defined | used ^ defined)}")
        for link in re.findall(r"\]\((/[^)#]+)", body):
            if not (bundle / link.lstrip("/")).exists():
                errors.append(f"{rel}: broken link {link}")
    print("\n".join(errors) or "ok")
    return 1 if errors else 0


if __name__ == "__main__":
    cmd, bundle = sys.argv[1], Path(sys.argv[2])
    sys.exit(check(bundle) if cmd == "check" else index(bundle) or 0)
