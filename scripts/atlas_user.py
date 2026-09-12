#!/usr/bin/env python3
"""Atlas user configuration and explicit, fast-forward-only Skill updates."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from atlas_layout import add_scope, read_layout, write_layout

SKILL_ROOT = Path(__file__).resolve().parents[1]


class NotConfigured(ValueError):
    pass


def config_path():
    base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config").expanduser()
    if not base.is_absolute():
        raise ValueError("XDG_CONFIG_HOME must be absolute")
    return base / "atlas" / "config.json"


def read_config(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate configuration key: {key}")
            result[key] = value
        return result
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    if not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] != 1:
        raise ValueError(f"unsupported configuration version: {path}")
    if not isinstance(data.get("kb_root"), str) or not data["kb_root"].strip():
        raise ValueError(f"missing kb_root: {path}")
    return data


def resolve_kb(explicit=None, cwd=None):
    if explicit is not None and not str(explicit).strip():
        raise ValueError("explicit KB path must not be empty")
    cwd = Path(cwd or Path.cwd()).expanduser().resolve(strict=True)
    if not cwd.is_dir():
        raise ValueError(f"working directory is not a directory: {cwd}")
    selected, source, base = explicit, "explicit", cwd
    if selected is None:
        for directory in (cwd, *cwd.parents):
            candidate = directory / ".atlas" / "config.json"
            if candidate.exists() or candidate.is_symlink():
                selected = read_config(candidate)["kb_root"]
                source, base = str(candidate), directory
                break
    if selected is None and "ATLAS_KB_ROOT" in os.environ:
        selected, source = os.environ["ATLAS_KB_ROOT"], "ATLAS_KB_ROOT"
        if not selected.strip() or not Path(selected).expanduser().is_absolute():
            raise ValueError("ATLAS_KB_ROOT must be a nonempty absolute path")
    if selected is None:
        candidate = config_path()
        if not candidate.exists() and not candidate.is_symlink():
            raise NotConfigured("No knowledge base configured. Run init --kb /absolute/path, or pass a KB path.")
        selected, source = read_config(candidate)["kb_root"], str(candidate)
        if not Path(selected).expanduser().is_absolute():
            raise ValueError(f"global kb_root must be absolute: {candidate}")
    path = Path(selected).expanduser()
    path = (base / path).resolve(strict=True)
    if not path.is_dir():
        raise ValueError(f"knowledge base is not a directory: {path}")
    if path == SKILL_ROOT or path.is_relative_to(SKILL_ROOT):
        raise ValueError("Keep the knowledge base outside the Atlas Skill directory")
    return {"root": str(path), "source": source}


def initialize(kb, project=None, create=False):
    if not str(kb).strip():
        raise ValueError("KB path must not be empty")
    root = Path(kb).expanduser().resolve()
    if root.is_relative_to(SKILL_ROOT) or SKILL_ROOT.is_relative_to(root):
        raise ValueError("Skill and knowledge-base directories must not contain each other")
    project_root = Path(project).expanduser().resolve(strict=True) if project else None
    if project_root and not project_root.is_dir():
        raise ValueError("project root must be a directory")
    target = project_root / ".atlas" / "config.json" if project_root else config_path()
    if target.is_symlink():
        raise ValueError(f"refusing to replace symlink configuration: {target}")
    # Validate existing configuration before creating anything. Preserve unknown settings.
    data = read_config(target) if target.exists() else {"version": 1}
    if not root.exists() and not create:
        raise ValueError("KB does not exist; use --create to initialize a new empty directory")
    if root.exists() and not root.is_dir():
        raise ValueError(f"KB is not a directory: {root}")
    if create:
        if root.exists() and any(root.iterdir()):
            raise ValueError("--create requires an empty or new KB directory; no existing notes will be overwritten")
        root.mkdir(parents=True, exist_ok=True)
        for name in ("README.md", "CONVENTIONS.md"):
            with (root / name).open("x", encoding="utf-8") as stream:
                stream.write((SKILL_ROOT / "assets" / "knowledge-base" / name).read_text(encoding="utf-8"))
        (root / "shared").mkdir()
        write_layout(root, {"version": 2, "scopes": {"shared": {"kind": "shared"}}})
    data["kb_root"] = os.path.relpath(root, project_root) if project_root else str(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replacement; never truncate the previous configuration on failure.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        temporary.replace(target)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return {"config": str(target), "root": str(root), "created": create,
            "note": "Project configuration and ATLAS_KB_ROOT can override the global setting; run resolve from your project."}


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, timeout=60)
    if result.returncode:
        raise ValueError(result.stderr.strip() or result.stdout.strip() or "Git command failed")
    return result.stdout.strip()


def audit_snapshot(repo, kb):
    if kb is None:
        return {"status": "not-configured", "note": "No KB scanned or modified"}
    result = subprocess.run([sys.executable, str(repo / "scripts" / "atlas.py"), "audit", kb["root"], "--json"],
                            text=True, capture_output=True, timeout=60)
    try:
        report = json.loads(result.stdout)
        if result.returncode not in (0, 1) or not isinstance(report.get("findings"), list):
            raise ValueError("invalid audit output")
        return {"status": "checked", "exit_code": result.returncode, **report}
    except (ValueError, AttributeError):
        return {"status": "unavailable", "error": result.stderr.strip() or result.stdout.strip()}


def compare_audits(before, after):
    if before.get("status") != "checked" or after.get("status") != "checked":
        return {"status": "unavailable"}
    def keyed(report):
        return {json.dumps(item, sort_keys=True): item for item in report.get("findings", [])}
    old, new = keyed(before), keyed(after)
    return {"status": "compared", "introduced": [new[k] for k in sorted(new.keys() - old.keys())],
            "resolved": [old[k] for k in sorted(old.keys() - new.keys())],
            "unchanged_count": len(old.keys() & new.keys()),
            "coverage": {"layout_before": before.get("layout"), "layout_after": after.get("layout"),
                         "documents_before": before.get("documents"), "documents_after": after.get("documents")}}


def local_context(kb):
    if kb is None:
        return None
    root = Path(kb["root"])
    layout = read_layout(root)
    # Report only names of opt-in profiles. Do not load or execute their contents.
    profiles = root / ".atlas" / "capture-profiles"
    names = [] if profiles.is_symlink() or not profiles.is_dir() else sorted(
        p.name for p in profiles.glob("*.md") if p.is_file() and not p.is_symlink())
    return {"layout": layout, "capture_profiles": names,
            "conventions": [str(p) for p in [root / "CONVENTIONS.md", *[
                root / scope / "CONVENTIONS.md" for scope in layout["scopes"]]] if p.is_file() and not p.is_symlink()]}


def update_skill(apply=False, explicit=None, cwd=None):
    repo = SKILL_ROOT
    if Path(git(repo, "rev-parse", "--show-toplevel")).resolve() != repo:
        raise ValueError("Atlas must be its own Git checkout; ZIP installs cannot use self-update")
    branch = git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    if git(repo, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Skill worktree has local changes; commit or handle them yourself before updating")
    remote = git(repo, "for-each-ref", "--format=%(upstream:remotename)", f"refs/heads/{branch}")
    remote_ref = git(repo, "for-each-ref", "--format=%(upstream:remoteref)", f"refs/heads/{branch}")
    if not remote or remote == "." or not remote_ref.startswith("refs/heads/"):
        raise ValueError("Current branch needs a configured remote tracking branch")
    url = git(repo, "remote", "get-url", remote)
    before = git(repo, "rev-parse", "HEAD")
    try:
        kb = resolve_kb(explicit, cwd)
    except NotConfigured:
        kb = None
    if kb:
        root = Path(kb["root"])
        if root.is_relative_to(repo) or repo.is_relative_to(root):
            raise ValueError("Skill and knowledge-base directories must not contain each other")
    report = {"skill": str(repo), "branch": branch, "remote": url, "tracking_ref": remote_ref,
              "before": before, "knowledge_base": kb, "local_context": local_context(kb),
              "audit_before": audit_snapshot(repo, kb)}
    # Read the remote without fetching or changing the installed Skill on a check.
    advertised = git(repo, "ls-remote", "--exit-code", remote, remote_ref).split()
    if len(advertised) != 2 or advertised[1] != remote_ref:
        raise ValueError("Remote tracking branch was not found unambiguously")
    report.update(remote_head=advertised[0], status="current" if advertised[0] == before else "different")
    if not apply:
        report["note"] = "Check only. Different does not prove fast-forward eligibility; update without --check uses git pull --ff-only."
        return report
    if report["audit_before"]["status"] == "unavailable":
        raise ValueError("Pre-update KB audit unavailable; install requirements in this Python environment first: " +
                         report["audit_before"].get("error", ""))
    requirements = (repo / "scripts" / "requirements.txt").read_bytes()
    # Recheck immediately before mutation. No stash, reset, force, or rebase.
    if git(repo, "status", "--porcelain", "--untracked-files=all") or git(repo, "rev-parse", "HEAD") != before:
        raise ValueError("Skill changed during preflight; retry after reviewing it")
    git(repo, "-c", "core.hooksPath=/dev/null", "-c", "rebase.autoStash=false", "-c", "merge.autoStash=false",
        "pull", "--ff-only", "--no-rebase", remote, remote_ref)
    after = git(repo, "rev-parse", "HEAD")
    report.update(after=after, status="updated" if after != before else "unchanged")
    try:
        report["changes"] = git(repo, "diff", "--no-ext-diff", "--no-textconv", "--name-status", before, after, "--")
        report["diff_stat"] = git(repo, "diff", "--no-ext-diff", "--no-textconv", "--stat", before, after, "--")
        report["requirements_changed"] = requirements != (repo / "scripts" / "requirements.txt").read_bytes()
        report["audit_after"] = audit_snapshot(repo, kb)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        report["audit_after"] = {"status": "unavailable", "error": str(exc)}
    report["audit_diff"] = compare_audits(report["audit_before"], report["audit_after"])
    report["integration"] = {"code": "fast-forwarded" if after != before else "unchanged",
                             "local_customization": "preserved-not-migrated",
                             "next": ["Read changed Skill instructions and templates using before/after diff",
                                      "Apply the user's selected local capture profile to the new base template",
                                      "Propose KB layout/config migrations separately; shared changes require content review"]}
    report["note"] = "Pull completed; no KB migration or dependency installation performed. Review audit differences; reload Skill instructions if the commit changed."
    if report["audit_after"]["status"] == "unavailable":
        report["status"] = "updated-check-failed"
    elif report["audit_after"].get("errors", 0):
        report["status"] = "updated-with-kb-errors"
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="persist global default or project override")
    init.add_argument("--kb", required=True, help="user-selected KB path")
    init.add_argument("--project", help="project root; omit for global configuration")
    init.add_argument("--create", action="store_true", help="create a new KB from templates; never overwrite notes")
    for name in ("resolve", "update", "scopes"):
        command = commands.add_parser(name)
        command.add_argument("--kb", help="explicit KB override")
        command.add_argument("--cwd", help="project context (default: invocation working directory)")
        if name == "update":
            mode = command.add_mutually_exclusive_group()
            mode.add_argument("--check", action="store_true", help="only check; default performs a safe pull")
            mode.add_argument("--apply", action="store_true", help="compatibility alias; update already pulls by default")
        if name == "scopes":
            command.add_argument("--add", help="register/create the user-selected scope")
            command.add_argument("--kind", choices=["project", "domain"], help="required with --add")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = initialize(args.kb, args.project, args.create)
        elif args.command == "resolve":
            result = resolve_kb(args.kb, args.cwd)
        elif args.command == "scopes":
            if bool(args.add) != bool(args.kind):
                raise ValueError("--add and --kind must be used together")
            kb = resolve_kb(args.kb, args.cwd)
            result = add_scope(kb["root"], args.add, args.kind) if args.add else {**kb, **local_context(kb)}
        else:
            result = update_skill(not args.check, args.kb, args.cwd)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get("status") in ("updated-check-failed", "updated-with-kb-errors") else 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Atlas management error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
