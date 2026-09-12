#!/usr/bin/env python3
"""Read-only Atlas checks. Index generation writes to stdout, never to the KB."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit, quote
from atlas_layout import read_layout

try:
    import yaml
    from markdown_it import MarkdownIt
except ImportError:
    sys.exit("Missing dependencies. Install scripts/requirements.txt in a Python virtual environment.")

TYPES = {"concept", "guide", "investigation", "decision", "reference", "overview"}
STATES = {"draft", "reviewed", "deprecated"}
FIELDS = {"type", "status", "created", "updated", "aliases", "tags"}
CONTROLS = ("README.md", "CONVENTIONS.md", "TAGS.md", "INDEX.md")
TAG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
MD = MarkdownIt("commonmark")


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate keys rather than silently keeping the final value."""


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ValueError("metadata keys must be strings")
        if key in result:
            raise ValueError(f"duplicate metadata key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


@dataclass
class Finding:
    severity: str
    code: str
    path: str
    line: int
    message: str


@dataclass
class Document:
    path: Path
    relative: str
    curated: bool
    meta: dict
    body: str
    offset: int
    tokens: list

    @property
    def title(self):
        for i, token in enumerate(self.tokens):
            if token.type == "heading_open" and token.tag == "h1":
                return self.tokens[i + 1].content
        return self.path.stem


class KnowledgeBase:
    def __init__(self, root):
        self.root = Path(root).expanduser().resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("knowledge-base root must be a directory")
        self.findings = []
        self.docs = []
        self.layout = read_layout(self.root)
        for path in self.inventory():
            relative = path.relative_to(self.root).as_posix()
            parts = relative.split("/")
            curated = parts[0] in self.layout["scopes"]
            if self.layout["version"] == 2 and len(parts) == 2 and parts[1] in CONTROLS:
                curated = False
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                self.add("error", "read", relative, 1, str(exc))
                continue
            meta, body, offset = {}, text, 0
            lines = text.splitlines(keepends=True)
            if lines and lines[0].strip() == "---":
                end = next((i for i in range(1, len(lines))
                            if lines[i].strip() == "---"), None)
                if end is None:
                    self.add("error", "frontmatter", relative, 1, "unclosed frontmatter")
                else:
                    body, offset = "".join(lines[end + 1:]), end + 1
                    try:
                        parsed = yaml.load("".join(lines[1:end]), Loader=UniqueLoader)
                        if not isinstance(parsed, dict):
                            raise ValueError("frontmatter must be a mapping")
                        meta = parsed
                    except (yaml.YAMLError, ValueError, RecursionError) as exc:
                        self.add("error", "frontmatter", relative, 1, str(exc))
            elif curated:
                self.add("error", "frontmatter", relative, 1, "missing frontmatter")
            self.docs.append(Document(path, relative, curated, meta, body, offset, MD.parse(body)))

    def add(self, severity, code, path, line, message):
        self.findings.append(Finding(severity, code, path, line, message))

    def inventory(self):
        paths = []
        for name in CONTROLS:
            path = self.root / name
            if path.is_symlink():
                self.add("warning", "symlink", name, 1, "symlink not read")
            elif path.is_file():
                paths.append(path)
        if self.layout["version"] == 2:
            for child in sorted(self.root.iterdir()):
                if child.is_dir() and not child.name.startswith(".") and child.name != "assets" and child.name not in self.layout["scopes"]:
                    self.add("warning", "unregistered-scope", child.name, 1, "directory not registered; Markdown inside was not inspected")
        for name in sorted(self.layout["scopes"]):
            base = self.root / name
            if base.is_symlink():
                self.add("warning", "symlink", name, 1, "symlink tree not read")
                continue
            if base.exists() and not base.is_dir():
                self.add("error", "layout", name, 1, "expected a directory")
                continue
            def walk_error(exc):
                self.add("error", "read", str(exc.filename), 1, str(exc))
            if not base.exists():
                if self.layout["version"] == 2:
                    self.add("error", "layout", name, 1, "registered scope directory missing")
                continue
            for folder, dirs, files in os.walk(base, followlinks=False, onerror=walk_error):
                for child in list(dirs):
                    p = Path(folder) / child
                    if p.is_symlink():
                        self.add("warning", "symlink", p.relative_to(self.root).as_posix(), 1,
                                 "symlink tree not read")
                dirs[:] = sorted(d for d in dirs if not d.startswith(".")
                                 and (self.layout["version"] != 2 or d != "assets")
                                 and not (Path(folder) / d).is_symlink())
                for filename in sorted(files):
                    p = Path(folder) / filename
                    if filename.startswith(".") or p.suffix.lower() != ".md":
                        continue
                    if p.is_symlink():
                        self.add("warning", "symlink", p.relative_to(self.root).as_posix(), 1,
                                 "symlink not read")
                    else:
                        paths.append(p)
        return sorted(paths)

    def vocabulary(self):
        blocks = []
        for doc in self.docs:
            if doc.relative in {"CONVENTIONS.md", "TAGS.md"}:
                blocks.extend((doc, t) for t in doc.tokens
                              if t.type == "fence" and t.info.strip() == "atlas-tags")
        if not blocks:
            self.add("warning", "vocabulary-missing", "CONVENTIONS.md", 1,
                     "no atlas-tags block; vocabulary membership not checked")
            return None
        if len(blocks) > 1:
            self.add("error", "vocabulary-duplicate", "CONVENTIONS.md", 1,
                     "keep exactly one atlas-tags block in CONVENTIONS.md or TAGS.md")
        vocabulary = set()
        for doc, token in blocks:
            for i, value in enumerate(token.content.splitlines()):
                value = value.strip()
                if not value:
                    continue
                line = doc.offset + token.map[0] + i + 2
                if not TAG.fullmatch(value):
                    self.add("error", "vocabulary-syntax", doc.relative, line, value)
                elif value in vocabulary:
                    self.add("warning", "vocabulary-repeat", doc.relative, line, value)
                vocabulary.add(value)
        return vocabulary

    def validate(self):
        vocabulary = self.vocabulary()
        names, paths = {}, {}
        for doc in self.docs:
            if not doc.curated:
                continue
            path = doc.relative
            meta = doc.meta
            for key, allowed in (("type", TYPES), ("status", STATES)):
                if not isinstance(meta.get(key), str) or meta[key] not in allowed:
                    self.add("error", "schema", path, 1, f"invalid/missing {key}")
            dates = {}
            for key in ("created", "updated"):
                value = str(meta.get(key, ""))
                try:
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                        raise ValueError()
                    dates[key] = date.fromisoformat(value)
                except ValueError:
                    self.add("error", "date", path, 1, f"{key} must be a real YYYY-MM-DD date")
            if len(dates) == 2 and dates["updated"] < dates["created"]:
                self.add("error", "date-order", path, 1, "updated precedes created")
            for key in meta.keys() - FIELDS:
                self.add("warning", "unknown-field", path, 1, f"not in default schema: {key}")
            for key in ("tags", "aliases"):
                values = meta.get(key, [])
                if not isinstance(values, list) or any(not isinstance(x, str) or not x.strip() for x in values):
                    self.add("error", "schema", path, 1, f"{key} must be a list of nonempty strings")
                    continue
                if len(values) != len(set(values)):
                    self.add("warning", "repeated-value", path, 1, key)
                if key == "tags":
                    for value in values:
                        if not TAG.fullmatch(value):
                            self.add("error", "tag-syntax", path, 1, value)
                        elif vocabulary is not None and value not in vocabulary:
                            self.add("warning", "unknown-tag", path, 1, value)
            headings = [t for t in doc.tokens if t.type == "heading_open" and t.tag == "h1"]
            if len(headings) != 1:
                self.add("error", "h1", path, 1, f"expected one H1, found {len(headings)}")
            if doc.tokens and (doc.tokens[0].type != "heading_open" or doc.tokens[0].tag != "h1"):
                self.add("warning", "title-position", path, doc.offset + 1, "H1 should lead the body")
            for token in doc.tokens:
                if token.type == "inline":
                    for child in token.children or []:
                        if child.type == "text" and re.search(r"\[\[[^\]]+\]\]", child.content):
                            self.add("warning", "wikilink", path, doc.offset + token.map[0] + 1,
                                     "use a relative Markdown link")
            if " " in doc.path.name or doc.path.suffix != ".md":
                self.add("warning", "filename", path, 1, "avoid spaces; use lowercase .md extension")
            names.setdefault(doc.path.name.casefold(), []).append(path)
            paths.setdefault(path.casefold(), []).append(path)
            for i, line in enumerate(doc.body.splitlines(), doc.offset + 1):
                if "\t" in line:
                    self.add("warning", "format-tab", path, i, "tab character; inspect intentional code indentation")
        for group in names.values():
            if len(group) > 1:
                self.add("warning", "duplicate-filename", group[0], 1, ", ".join(group))
        for group in paths.values():
            if len(group) > 1:
                self.add("error", "case-collision", group[0], 1, ", ".join(group))

    def check_links(self, orphans=False):
        inbound = {doc.path: set() for doc in self.docs if doc.curated}
        for doc in self.docs:
            for token in doc.tokens:
                if token.type in {"html_block", "html_inline"}:
                    self.add("warning", "html-unchecked", doc.relative,
                             doc.offset + (token.map or [0])[0] + 1, "HTML links not checked")
                if token.type != "inline":
                    continue
                line = doc.offset + token.map[0] + 1
                for child in token.children or []:
                    if child.type == "html_inline":
                        self.add("warning", "html-unchecked", doc.relative, line, "HTML links not checked")
                    if child.type not in {"link_open", "image"}:
                        continue
                    dest = child.attrGet("href" if child.type == "link_open" else "src") or ""
                    try:
                        url = urlsplit(dest)
                    except ValueError:
                        self.add("error", "link-url", doc.relative, line, dest)
                        continue
                    if url.scheme or url.netloc:
                        continue
                    raw = unquote(url.path)
                    if raw.startswith("/"):
                        self.add("warning", "absolute-link", doc.relative, line, dest)
                        continue
                    if "\x00" in raw:
                        self.add("error", "link-url", doc.relative, line, "NUL in path")
                        continue
                    try:
                        target = (doc.path.parent / raw).resolve() if raw else doc.path
                    except (OSError, RuntimeError):
                        self.add("error", "link-path", doc.relative, line, dest)
                        continue
                    if not target.is_relative_to(self.root):
                        self.add("warning", "outside-root", doc.relative, line,
                                 f"external local path not inspected: {dest}")
                        continue
                    if not target.exists():
                        self.add("error", "broken-link", doc.relative, line, dest)
                    elif target in inbound and target != doc.path:
                        scope_index = (self.layout["version"] == 2 and len(Path(doc.relative).parts) == 2
                                       and doc.path.name == "INDEX.md")
                        if doc.relative != "INDEX.md" and not scope_index:
                            inbound[target].add(doc.path)
                    if url.fragment:
                        self.add("info", "anchor-unchecked", doc.relative, line,
                                 f"target path checked, heading anchor requires review: {dest}")
        if orphans:
            for target, sources in inbound.items():
                if not sources:
                    self.add("warning", "orphan", target.relative_to(self.root).as_posix(), 1,
                             "no inbound Markdown document links (generated INDEX excluded); not a deletion recommendation")

    def audit(self):
        for name in ("README.md", "CONVENTIONS.md"):
            if not any(doc.relative == name for doc in self.docs):
                self.add("error", "control-file", name, 1, "missing readable control file")
        self.validate()
        self.check_links(orphans=True)

    def index(self):
        lines = ["# Knowledge Index", "", "<!-- Generated by Atlas; Markdown documents remain authoritative. -->", ""]
        previous = None
        for doc in self.docs:
            if not doc.curated:
                continue
            group = "/".join(doc.relative.split("/")[:1 if self.layout["version"] == 2 else 2])
            if group != previous:
                if previous is not None:
                    lines.append("")
                lines.extend([f"## {group}", ""])
                previous = group
            title = doc.title.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
            lines.append(f"- [{title}]({quote(doc.relative, safe='/')}) — {doc.meta.get('type', '?')}; {doc.meta.get('status', '?')}")
        return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "check-links", "audit", "build-index"])
    parser.add_argument("root", nargs="?", help="KB root; omit to use project/environment/global configuration")
    parser.add_argument("--json", action="store_true", help="machine-readable diagnostic output")
    parser.add_argument("--strict", action="store_true", help="warnings also cause exit 1")
    parser.add_argument("--check", action="store_true", help="build-index only: compare existing INDEX.md without writing")
    args = parser.parse_args(argv)
    if args.check and args.command != "build-index":
        parser.error("--check is only valid for build-index")
    if args.json and args.command == "build-index" and not args.check:
        parser.error("build-index emits Markdown; use --check with --json for diagnostics")
    try:
        if args.root is None:
            from atlas_user import resolve_kb
            args.root = resolve_kb()["root"]
        kb = KnowledgeBase(args.root)
        if args.command == "build-index":
            kb.validate()
            if args.check:
                path = kb.root / "INDEX.md"
                if path.is_symlink() or not path.is_file() or path.read_text(encoding="utf-8") != kb.index():
                    kb.add("error", "index-stale", "INDEX.md", 1, "missing, symlinked or outdated index")
            elif not any(f.severity == "error" or (args.strict and f.severity == "warning") for f in kb.findings):
                print(kb.index(), end="")
                for f in kb.findings:
                    print(f"{f.severity} {f.path}:{f.line} [{f.code}] {f.message}", file=sys.stderr)
                return 0
        elif args.command == "validate":
            kb.validate()
        elif args.command == "check-links":
            kb.check_links()
        else:
            kb.audit()
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Atlas input error: {exc}", file=sys.stderr)
        return 2
    findings = sorted(kb.findings, key=lambda f: (f.path, f.line, f.code))
    if args.json:
        print(json.dumps({"root": str(kb.root), "layout": kb.layout, "documents": len(kb.docs),
                          "findings": [asdict(f) for f in findings],
                          "errors": sum(f.severity == "error" for f in findings),
                          "warnings": sum(f.severity == "warning" for f in findings)}, ensure_ascii=False, indent=2))
    else:
        stream = sys.stderr if args.command == "build-index" and not args.check else sys.stdout
        for f in findings:
            print(f"{f.severity} {f.path}:{f.line} [{f.code}] {f.message}", file=stream)
        print(f"Checked {len(kb.docs)} Markdown files; {sum(f.severity == 'error' for f in findings)} errors; "
              f"{sum(f.severity == 'warning' for f in findings)} warnings.", file=stream)
    return int(any(f.severity == "error" or (args.strict and f.severity == "warning") for f in findings))


if __name__ == "__main__":
    sys.exit(main())
