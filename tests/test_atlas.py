"""Behavioral regression tests for the deterministic CLI; no live KB writes."""
from contextlib import redirect_stdout, redirect_stderr
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "atlas.py"
sys.path.insert(0, str(MODULE.parent))
spec = importlib.util.spec_from_file_location("atlas", MODULE)
atlas = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = atlas
spec.loader.exec_module(atlas)


def note(title="Alpha", body="", metadata=""):
    return ("---\ntype: concept\nstatus: draft\ncreated: 2026-09-09\n"
            "updated: 2026-09-09\n" + metadata + "---\n\n# " + title + "\n\n" + body + "\n")


class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="atlas-tests-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write("README.md", "# Test KB\n\n[A](knowledge/llvm/A.md)\n")
        self.write("CONVENTIONS.md", "# Conventions\n\n```atlas-tags\ncodegen\nrisc-v\n```\n")
        self.write("knowledge/llvm/A.md", note(metadata="tags: [codegen]\n"))

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            result = atlas.main([args[0], str(self.root), *args[1:]])
        return result, out.getvalue(), err.getvalue()

    def findings(self, command="audit"):
        _, out, _ = self.run_cli(command, "--json")
        return json.loads(out)["findings"]

    def codes(self, command="audit"):
        return {f["code"] for f in self.findings(command)}

    def test_clean_and_read_only(self):
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(self.run_cli("audit", "--strict")[0], 0)
        self.assertEqual(self.run_cli("build-index")[0], 0)
        after = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_reference_images_nested_paths_and_code_ignored(self):
        self.write("assets/image (1).png", "fixture")
        self.write("knowledge/llvm/B.md", note("Beta"))
        self.write("knowledge/llvm/A.md", note(body=(
            "[B][target]\n\n[target]: B.md\n\n![image](../../assets/image%20%281%29.png)\n"
            "\n`[fake](missing.md)`\n\n```md\n[also fake](missing.md)\n# Fake H1\n```\n")))
        self.assertNotIn("broken-link", self.codes())
        self.assertNotIn("h1", self.codes())
        self.assertNotIn("orphan", self.codes())

    def test_broken_link_line_and_fragment_boundary(self):
        self.write("knowledge/llvm/A.md", note(body="[bad](Missing.md)\n[local](#hello)"))
        findings = self.findings("check-links")
        self.assertTrue(any(f["code"] == "broken-link" and f["line"] > 6 for f in findings))
        self.assertIn("anchor-unchecked", {f["code"] for f in findings})
        self.assertEqual(self.run_cli("check-links")[0], 1)

    def test_parentheses_link(self):
        self.write("knowledge/llvm/B(1).md", note("B"))
        self.write("knowledge/llvm/A.md", note(body="[B](B(1).md)"))
        self.assertNotIn("broken-link", self.codes())

    def test_external_and_html(self):
        self.write("knowledge/llvm/A.md", note(body='[web](https://example.invalid/a)\n<a href="missing.md">html</a>'))
        self.assertNotIn("broken-link", self.codes())
        self.assertIn("html-unchecked", self.codes())

    def test_outside_root_and_symlink(self):
        with tempfile.TemporaryDirectory(prefix="atlas-outside-") as outside:
            external = Path(outside) / "Secret.md"
            external.write_text("not valid yaml", encoding="utf-8")
            (self.root / "knowledge/llvm/Secret.md").symlink_to(external)
            self.write("knowledge/llvm/A.md", note(body="[outside](Secret.md)"))
            codes = self.codes()
            self.assertIn("symlink", codes)
            self.assertIn("outside-root", codes)
            self.assertNotIn("frontmatter", codes)

    def test_symlink_directory(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "projects").symlink_to(outside, target_is_directory=True)
            self.assertIn("symlink", self.codes())

    def test_metadata_bad_types_do_not_crash(self):
        text = note().replace("type: concept", "type: [concept]").replace("status: draft", "status: {}")
        self.write("knowledge/llvm/A.md", text.replace("---\n\n#", "tags: [3, true]\naliases: test\n---\n\n#"))
        self.assertIn("schema", self.codes())
        self.assertEqual(self.run_cli("validate")[0], 1)

    def test_duplicate_yaml_key(self):
        self.write("knowledge/llvm/A.md", note(metadata="type: guide\n"))
        self.assertIn("frontmatter", self.codes())

    def test_yaml_unsafe_tag_rejected(self):
        self.write("knowledge/llvm/A.md", note(metadata="aliases: !!python/object:example {}\n"))
        self.assertIn("frontmatter", self.codes())

    def test_dates_and_quoted_dates(self):
        self.write("knowledge/llvm/A.md", note().replace("2026-09-09", '"2026-09-09"'))
        self.assertNotIn("date", self.codes())
        self.write("knowledge/llvm/A.md", note().replace("updated: 2026-09-09", "updated: '2026-02-30'"))
        self.assertIn("date", self.codes())
        self.write("knowledge/llvm/A.md", note().replace("updated: 2026-09-09", "updated: 2026-01-01"))
        self.assertIn("date-order", self.codes())

    def test_invalid_unquoted_yaml_date_is_reported(self):
        self.write("knowledge/llvm/A.md", note().replace("2026-09-09", "2026-02-30"))
        self.assertIn("frontmatter", self.codes())

    def test_missing_and_unclosed_frontmatter(self):
        self.write("knowledge/llvm/A.md", "# No metadata\n")
        self.assertIn("frontmatter", self.codes())
        self.write("knowledge/llvm/A.md", "---\ntype: concept\n")
        self.assertIn("frontmatter", self.codes())

    def test_vocabulary_strict_and_missing(self):
        self.write("knowledge/llvm/A.md", note(metadata="tags: [unknown]\n"))
        self.assertIn("unknown-tag", self.codes())
        self.assertEqual(self.run_cli("validate")[0], 0)
        self.assertEqual(self.run_cli("validate", "--strict")[0], 1)
        self.write("CONVENTIONS.md", "# Human maintained vocabulary\n")
        self.assertIn("vocabulary-missing", self.codes())
        self.assertNotIn("unknown-tag", self.codes())

    def test_bad_tag_and_multiple_vocabularies(self):
        self.write("TAGS.md", "```atlas-tags\nLLVM\n```\n")
        self.write("knowledge/llvm/A.md", note(metadata="tags: [LLVM, codegen, codegen]\n"))
        self.assertTrue({"vocabulary-duplicate", "vocabulary-syntax", "tag-syntax", "repeated-value"} <= self.codes())

    def test_duplicate_names_and_orphan(self):
        self.write("knowledge/mlir/A.md", note("Other subject"))
        self.assertIn("duplicate-filename", self.codes())
        self.assertIn("orphan", self.codes())

    def test_index_does_not_hide_orphans(self):
        self.write("knowledge/mlir/B.md", note("孤立"))
        _, generated, _ = self.run_cli("build-index")
        self.write("INDEX.md", generated)
        self.assertIn("orphan", self.codes())

    def test_index_repeatability_staleness_and_no_write(self):
        self.write("knowledge/mlir/中文.md", note("中文 [类型]"))
        one = self.run_cli("build-index")[1]
        self.assertEqual(one, self.run_cli("build-index")[1])
        self.assertIn("%E4%B8%AD", one)
        self.assertFalse((self.root / "INDEX.md").exists())
        self.assertEqual(self.run_cli("build-index", "--check")[0], 1)
        self.write("INDEX.md", one)
        self.assertEqual(self.run_cli("build-index", "--check")[0], 0)
        self.write("knowledge/llvm/A.md", note("Changed title"))
        self.assertEqual(self.run_cli("build-index", "--check")[0], 1)

    def test_invalid_schema_produces_no_index(self):
        self.write("knowledge/llvm/A.md", "# Invalid\n")
        code, out, err = self.run_cli("build-index")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("error", err)

    def test_wikilink_not_inline_code(self):
        self.write("knowledge/llvm/A.md", note(body="`[[code]]`"))
        self.assertNotIn("wikilink", self.codes())
        self.write("knowledge/llvm/A.md", note(body="[[note]]"))
        self.assertIn("wikilink", self.codes())

    def test_control_and_invalid_root(self):
        (self.root / "README.md").unlink()
        self.assertIn("control-file", self.codes())
        with redirect_stderr(io.StringIO()):
            self.assertEqual(atlas.main(["audit", str(self.root / "absent")]), 2)


if __name__ == "__main__":
    unittest.main()
