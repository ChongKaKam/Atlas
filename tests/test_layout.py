"""Scope-first inventory and legacy compatibility; all fixtures are temporary."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from atlas import KnowledgeBase
from atlas_layout import add_scope, read_layout, write_layout

NOTE = "---\ntype: concept\nstatus: draft\ncreated: 2026-09-12\nupdated: 2026-09-12\n---\n\n# Example\n\n"


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="atlas-layout-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "README.md").write_text("# KB\n")
        (self.root / "CONVENTIONS.md").write_text("# Rules\n\n```atlas-tags\n```\n")
        (self.root / "shared").mkdir()
        write_layout(self.root, {"version": 2, "scopes": {"shared": {"kind": "shared"}}})

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_scope_registration_and_scan(self):
        add_scope(self.root, "compiler-x", "project")
        add_scope(self.root, "llvm", "domain")
        self.write("llvm/A.md", NOTE + "[Shared](../shared/B.md)\n")
        self.write("compiler-x/C.md", NOTE)
        self.write("shared/B.md", NOTE)
        self.write("llvm/README.md", "# LLVM\n\n[A](A.md)\n")
        kb = KnowledgeBase(self.root)
        kb.audit()
        self.assertFalse([f for f in kb.findings if f.severity == "error"])
        self.assertEqual({d.relative for d in kb.docs if d.curated}, {"llvm/A.md", "compiler-x/C.md", "shared/B.md"})
        self.assertIn("## llvm\n", kb.index())
        self.assertNotIn("## llvm/A.md", kb.index())

    def test_bad_scope_names_and_kind_changes(self):
        for name, kind in [("../escape", "domain"), ("assets", "domain"), ("shared", "project"),
                           ("LLVM", "domain"), ("x", "shared"), ("knowledge", "domain")]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                add_scope(self.root, name, kind)
        add_scope(self.root, "llvm", "domain")
        with self.assertRaises(ValueError):
            add_scope(self.root, "llvm", "project")

    def test_existing_notes_not_rewritten_on_registration(self):
        note = self.write("llvm/A.md", NOTE)
        before = (note.read_bytes(), note.stat().st_mtime_ns)
        add_scope(self.root, "llvm", "domain")
        add_scope(self.root, "llvm", "domain")
        self.assertEqual(before, (note.read_bytes(), note.stat().st_mtime_ns))

    def test_unregistered_missing_and_excluded_directories(self):
        add_scope(self.root, "llvm", "domain")
        self.write("scratch/Not-curated.md", "arbitrary input")
        self.write("llvm/assets/Input.md", "raw source")
        self.write(".atlas/capture-profiles/test.md", "user instructions")
        (self.root / "shared").rmdir()
        kb = KnowledgeBase(self.root)
        self.assertTrue(any(f.code == "unregistered-scope" for f in kb.findings))
        self.assertTrue(any(f.code == "layout" and f.path == "shared" for f in kb.findings))
        self.assertEqual(len(kb.docs), 2)

    def test_legacy_is_readable_but_not_silently_migrated(self):
        (self.root / ".atlas/layout.json").unlink()
        self.write("knowledge/llvm/Old.md", NOTE)
        kb = KnowledgeBase(self.root)
        self.assertEqual(kb.layout["version"], 1)
        self.assertIn("knowledge/llvm/Old.md", {d.relative for d in kb.docs})
        with self.assertRaisesRegex(ValueError, "migration"):
            add_scope(self.root, "llvm", "domain")
        self.assertFalse((self.root / ".atlas/layout.json").exists())

    def test_invalid_layout_never_falls_back(self):
        for value in ['{}', '{"version":3}', '{"version":true}', '{"version":2,"scopes":{}}',
                      '{"version":2,"version":2,"scopes":{"shared":{"kind":"shared"}}}',
                      '{"version":2,"scopes":{"shared":{"kind":"shared"},"../escape":{"kind":"domain"}}}']:
            self.write(".atlas/layout.json", value)
            with self.assertRaises(ValueError):
                KnowledgeBase(self.root)

    def test_scope_generated_index_does_not_hide_orphan(self):
        add_scope(self.root, "llvm", "domain")
        self.write("llvm/A.md", NOTE)
        self.write("llvm/INDEX.md", "# Index\n\n[A](A.md)\n")
        kb = KnowledgeBase(self.root)
        kb.audit()
        self.assertTrue(any(f.code == "orphan" and f.path == "llvm/A.md" for f in kb.findings))

    def test_symlink_scope_and_layout_not_followed(self):
        add_scope(self.root, "llvm", "domain")
        self.write("llvm/A.md", NOTE)
        (self.root / "shared").rmdir()
        (self.root / "shared").symlink_to(self.root / "llvm", target_is_directory=True)
        kb = KnowledgeBase(self.root)
        self.assertTrue(any(f.code == "symlink" and f.path == "shared" for f in kb.findings))
        self.assertNotIn("shared/A.md", {d.relative for d in kb.docs})
        with self.assertRaises(ValueError):
            add_scope(self.root, "shared", "shared")
        path = self.root / ".atlas/layout.json"
        path.rename(path.with_suffix(".backup"))
        path.symlink_to(path.with_suffix(".backup"))
        with self.assertRaises(ValueError):
            read_layout(self.root)


if __name__ == "__main__":
    unittest.main()
