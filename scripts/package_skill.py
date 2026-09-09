#!/usr/bin/env python3
"""Package Atlas's distributable files; never include the development knowledge base."""
import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root / "dist" / "atlas.zip")
    args = parser.parse_args()
    output = args.output.expanduser().absolute()
    files = [root / name for name in ("SKILL.md", "README.md", "CONTRIBUTING.md")]
    if (root / "LICENSE").is_file():
        files.append(root / "LICENSE")
    for folder in ("agents", "references", "assets", "scripts", "tests"):
        for path in (root / folder).rglob("*"):
            relative = path.relative_to(root)
            if (not path.is_file() or path.is_symlink()
                    or any(part.startswith(".") or part == "__pycache__" for part in relative.parts)
                    or path.suffix not in {".md", ".py", ".yaml", ".yml", ".txt"}):
                continue
            # A file under a symlinked directory must not escape the package source.
            if any(parent.is_symlink() for parent in path.parents if parent != root and root in parent.parents):
                continue
            files.append(path)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(output, "x", ZIP_DEFLATED) as archive:
            for path in sorted(files):
                archive.write(path, "atlas/" + path.relative_to(root).as_posix())
        print(f"Created {output} ({len(files)} files)")
    except FileExistsError:
        parser.exit(1, f"Refusing to overwrite {output}; choose a new --output path.\n")
    except OSError as exc:
        parser.exit(1, f"Package error: {exc}\n")


if __name__ == "__main__":
    main()
