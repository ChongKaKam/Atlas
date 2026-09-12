"""Versioned KB scope registry; no semantic placement or shared approval decisions."""
import json
from pathlib import Path
import re
import tempfile


def read_layout(root):
    root = Path(root)
    path = root / ".atlas" / "layout.json"
    if (root / ".atlas").is_symlink() or path.is_symlink():
        raise ValueError("layout configuration must not be symlinked")
    if (root / ".atlas").exists() and not (root / ".atlas").is_dir():
        raise ValueError(".atlas must be a directory")
    if not path.exists():
        return {"version": 1, "scopes": {"knowledge": {"kind": "legacy"}, "projects": {"kind": "legacy"}}}
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate layout key: {key}")
            result[key] = value
        return result
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    if not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] != 2:
        raise ValueError("unsupported KB layout version; no automatic migration")
    scopes = data.get("scopes")
    if not isinstance(scopes, dict) or scopes.get("shared") != {"kind": "shared"}:
        raise ValueError("layout requires the shared scope")
    for name, settings in scopes.items():
        validate_scope(name, settings.get("kind") if isinstance(settings, dict) else None)
    return data


def validate_scope(name, kind):
    if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", name):
        raise ValueError("scope name must be a lowercase-kebab-case directory name")
    if name in {"assets", "knowledge", "projects"}:
        raise ValueError(f"reserved scope name: {name}")
    if kind not in {"project", "domain", "shared"} or (name == "shared") != (kind == "shared"):
        raise ValueError("scope kind must be project/domain; shared is reserved for shared knowledge")


def write_layout(root, data):
    path = Path(root) / ".atlas" / "layout.json"
    if path.parent.is_symlink() or path.is_symlink():
        raise ValueError("refusing to write symlinked layout configuration")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        temporary.replace(path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def add_scope(root, name, kind):
    root = Path(root).resolve(strict=True)
    validate_scope(name, kind)
    data = read_layout(root)
    if data["version"] != 2:
        raise ValueError("legacy KB: propose and approve a layout migration before registering scopes")
    previous = data["scopes"].get(name)
    if previous and previous.get("kind") != kind:
        raise ValueError("existing scope kind differs; review the ownership change first")
    target = root / name
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise ValueError("scope must be a real directory inside the KB")
    target.mkdir(exist_ok=True)
    data["scopes"][name] = previous or {"kind": kind}
    write_layout(root, data)
    return {"root": str(root), "scope": name, "kind": kind, "path": str(target)}
