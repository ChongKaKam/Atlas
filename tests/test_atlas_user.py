"""Configuration and self-update tests using isolated KBs and local Git remotes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
import io
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "scripts"))
import atlas_user as user


class ConfigurationFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="atlas-user-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.env = patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.base / "config")})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.override = os.environ.pop("ATLAS_KB_ROOT", None)
        if self.override is not None:
            self.addCleanup(os.environ.__setitem__, "ATLAS_KB_ROOT", self.override)
        self.kb = self.base / "global-kb"
        self.project = self.base / "project"
        self.project.mkdir()
        user.initialize(self.kb, create=True)


class UserTests(ConfigurationFixture):
    def test_global_init_create_and_resolve(self):
        self.assertEqual(user.resolve_kb(cwd=self.project)["root"], str(self.kb))
        self.assertTrue((self.kb / "CONVENTIONS.md").is_file())
        self.assertEqual(user.read_config(user.config_path())["version"], 1)

    def test_precedence_and_nearest_project(self):
        envkb = self.base / "env-kb"
        envkb.mkdir()
        os.environ["ATLAS_KB_ROOT"] = str(envkb)
        self.assertEqual(user.resolve_kb(cwd=self.project)["root"], str(envkb))
        projectkb = self.project / "notes"
        user.initialize(projectkb, project=self.project, create=True)
        child = self.project / "src"
        child.mkdir()
        self.assertEqual(user.resolve_kb(cwd=child)["root"], str(projectkb))
        self.assertEqual(user.resolve_kb(self.kb, child)["source"], "explicit")
        self.assertEqual(user.read_config(self.project / ".atlas/config.json")["kb_root"], "notes")
        user.initialize(self.kb, project=child)
        self.assertEqual(user.resolve_kb(cwd=child)["root"], str(self.kb))

    def test_invalid_override_does_not_fall_back(self):
        for value in ("", "relative", str(self.base / "missing")):
            os.environ["ATLAS_KB_ROOT"] = value
            with self.assertRaises((ValueError, OSError)):
                user.resolve_kb(cwd=self.project)
        self.assertEqual(user.resolve_kb(self.kb, self.project)["root"], str(self.kb))

    def test_bad_project_config_blocks_fallback(self):
        (self.project / ".atlas").mkdir()
        target = self.project / ".atlas/config.json"
        for data in ('{}', '{bad', '{"version":1,"kb_root":"x","kb_root":"y"}',
                     '{"version":true,"kb_root":"x"}', '{"version":2,"kb_root":"x"}'):
            target.write_text(data)
            with self.assertRaises(ValueError):
                user.resolve_kb(cwd=self.project)

    def test_init_preserves_notes_and_extra_config(self):
        before = {p: p.read_bytes() for p in self.kb.rglob("*") if p.is_file()}
        with self.assertRaises(ValueError):
            user.initialize(self.kb, create=True)
        config = user.read_config(user.config_path())
        config["future_setting"] = 42
        user.config_path().write_text(json.dumps(config))
        user.initialize(self.kb)
        self.assertEqual(user.read_config(user.config_path())["future_setting"], 42)
        self.assertEqual(before, {p: p.read_bytes() for p in self.kb.rglob("*") if p.is_file()})

    def test_missing_and_skill_paths_rejected(self):
        with self.assertRaises(ValueError):
            user.initialize(self.base / "absent")
        with self.assertRaises(ValueError):
            user.initialize(SOURCE)
        with self.assertRaises(ValueError):
            user.resolve_kb(SOURCE)
        user.config_path().unlink()
        with self.assertRaises(user.NotConfigured):
            user.resolve_kb(cwd=self.project)

    def test_config_symlink_not_replaced(self):
        target = user.config_path()
        original = target.read_bytes()
        target.rename(target.with_suffix(".backup"))
        target.symlink_to(target.with_suffix(".backup"))
        with self.assertRaises(ValueError):
            user.initialize(self.kb)
        self.assertEqual(target.read_bytes(), original)

    def test_audit_cli_uses_configuration_without_root(self):
        result = subprocess.run([sys.executable, str(SOURCE / "scripts/atlas.py"), "audit", "--json"],
                                cwd=self.project, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["root"], str(self.kb))


class UpdateTests(ConfigurationFixture):
    def setUp(self):
        super().setUp()
        self.remote = self.base / "remote.git"
        self.author = self.base / "author"
        self.install = self.base / "installed-atlas"
        self.run_git(self.base, "init", "--bare", str(self.remote))
        self.run_git(self.base, "init", "-b", "main", str(self.author))
        self.identity(self.author)
        (self.author / "scripts").mkdir()
        for name in ("atlas.py", "requirements.txt", "atlas_user.py", "atlas_layout.py"):
            shutil.copyfile(SOURCE / "scripts" / name, self.author / "scripts" / name)
        (self.author / "SKILL.md").write_text("# Test Skill\n")
        (self.author / ".gitignore").write_text("__pycache__/\n")
        self.run_git(self.author, "add", ".")
        self.run_git(self.author, "commit", "-m", "initial")
        self.run_git(self.author, "remote", "add", "origin", str(self.remote))
        self.run_git(self.author, "push", "-u", "origin", "main")
        self.run_git(self.base, "clone", "-b", "main", str(self.remote), str(self.install))
        self.identity(self.install)
        scope = patch.object(user, "SKILL_ROOT", self.install)
        scope.start()
        self.addCleanup(scope.stop)
        # init --create also needs the packaged templates in this synthetic checkout.
        shutil.copytree(SOURCE / "assets", self.install / "assets")
        self.run_git(self.install, "add", "assets")
        self.run_git(self.install, "commit", "-m", "templates")
        self.run_git(self.install, "push")
        self.run_git(self.author, "pull", "--ff-only")

    def run_git(self, repo, *args):
        result = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def identity(self, repo):
        self.run_git(repo, "config", "user.name", "Atlas Test")
        self.run_git(repo, "config", "user.email", "atlas-test@example.invalid")
        self.run_git(repo, "config", "commit.gpgsign", "false")

    def upstream_change(self, name="SKILL.md", value="# Updated Skill\n"):
        (self.author / name).write_text(value)
        self.run_git(self.author, "add", name)
        self.run_git(self.author, "commit", "-m", "upstream change")
        self.run_git(self.author, "push")

    def test_fast_forward_and_kb_read_only(self):
        user.add_scope(self.kb, "compiler", "domain")
        notes = self.kb / "compiler"
        (notes / "Example.md").write_text("---\ntype: concept\nstatus: draft\ncreated: 2026-09-10\n"
                                        "updated: 2026-09-10\n---\n\n# Example\n\nUser knowledge.\n")
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.kb.rglob("*") if p.is_file()}
        self.upstream_change()
        report = user.update_skill(cwd=self.project)
        self.assertEqual(report["status"], "different")
        self.assertEqual(self.run_git(self.install, "rev-parse", "HEAD"), report["before"])
        report = user.update_skill(True, cwd=self.project)
        self.assertEqual(report["status"], "updated")
        self.assertNotEqual(report["before"], report["after"])
        self.assertEqual(report["audit_after"]["status"], "checked")
        self.assertIn("SKILL.md", report["changes"])
        self.assertEqual(report["audit_diff"]["introduced"], [])
        self.assertEqual(report["integration"]["code"], "fast-forwarded")
        self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.kb.rglob("*") if p.is_file()})

    def test_dirty_and_untracked_refused(self):
        for name in ("SKILL.md", "untracked.txt"):
            with self.subTest(name=name):
                path = self.install / name
                old = path.read_bytes() if path.exists() else None
                path.write_text("local work")
                with self.assertRaisesRegex(ValueError, "local changes"):
                    user.update_skill(True, cwd=self.project)
                self.assertEqual(path.read_text(), "local work")
                if old is None:
                    path.unlink()
                else:
                    path.write_bytes(old)

    def test_divergence_refused_without_discarding_commit(self):
        self.upstream_change()
        (self.install / "local.txt").write_text("local")
        self.run_git(self.install, "add", "local.txt")
        self.run_git(self.install, "commit", "-m", "local change")
        before = self.run_git(self.install, "rev-parse", "HEAD")
        with self.assertRaises(ValueError):
            user.update_skill(True, cwd=self.project)
        self.assertEqual(self.run_git(self.install, "rev-parse", "HEAD"), before)
        self.assertEqual((self.install / "local.txt").read_text(), "local")

    def test_detached_and_no_tracking_refused(self):
        self.run_git(self.install, "checkout", "--detach")
        with self.assertRaises(ValueError):
            user.update_skill(cwd=self.project)
        self.run_git(self.install, "checkout", "main")
        self.run_git(self.install, "branch", "--unset-upstream")
        with self.assertRaisesRegex(ValueError, "tracking"):
            user.update_skill(cwd=self.project)

    def test_missing_dependencies_prevents_apply(self):
        with patch.object(user, "audit_snapshot", return_value={"status": "unavailable", "error": "missing deps"}):
            with self.assertRaisesRegex(ValueError, "Pre-update"):
                user.update_skill(True, cwd=self.project)

    def test_requirements_change_reported_and_post_failure_distinct(self):
        self.upstream_change("scripts/requirements.txt", "# changed requirements\n")
        with patch.object(user, "audit_snapshot", side_effect=[{"status": "checked", "errors": 0},
                                                               {"status": "unavailable", "error": "new dependency"}]):
            report = user.update_skill(True, cwd=self.project)
        self.assertTrue(report["requirements_changed"])
        self.assertEqual(report["status"], "updated-check-failed")
        self.assertNotEqual(report["after"], report["before"])

    def test_invalid_kb_blocks_update(self):
        with self.assertRaises(OSError):
            user.update_skill(True, explicit=self.base / "gone", cwd=self.project)

    def test_zip_install_refused(self):
        with patch.object(user, "SKILL_ROOT", self.project):
            with self.assertRaises(ValueError):
                user.update_skill(True, cwd=self.project)

    def test_current_version_noop(self):
        self.assertEqual(user.update_skill(cwd=self.project)["status"], "current")
        report = user.update_skill(True, cwd=self.project)
        self.assertEqual(report["status"], "unchanged")
        self.assertEqual(report["before"], report["after"])

    def test_no_kb_still_allows_skill_update(self):
        user.config_path().unlink()
        self.upstream_change()
        report = user.update_skill(True, cwd=self.project)
        self.assertEqual(report["status"], "updated")
        self.assertIsNone(report["knowledge_base"])
        self.assertEqual(report["audit_after"]["status"], "not-configured")

    def test_symlink_install_resolves_real_checkout(self):
        link = self.base / "skill-link"
        link.symlink_to(self.install, target_is_directory=True)
        result = subprocess.run([sys.executable, str(link / "scripts/atlas_user.py"), "update",
                                 "--cwd", str(self.project)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["skill"], str(self.install))

    def test_nested_kb_blocks_pull(self):
        for root in (self.install, self.base):
            with self.assertRaises(ValueError):
                user.update_skill(True, explicit=root, cwd=self.project)

    def test_update_cli_pulls_by_default_check_does_not(self):
        self.upstream_change()
        before = self.run_git(self.install, "rev-parse", "HEAD")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(user.main(["update", "--check", "--cwd", str(self.project)]), 0)
        self.assertEqual(self.run_git(self.install, "rev-parse", "HEAD"), before)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(user.main(["update", "--cwd", str(self.project)]), 0)
        self.assertNotEqual(self.run_git(self.install, "rev-parse", "HEAD"), before)

    def test_local_capture_profile_survives_update(self):
        profiles = self.kb / ".atlas/capture-profiles"
        profiles.mkdir()
        profile = profiles / "code-reading.md"
        profile.write_text("# Code reading\n\nPreserve exact revisions and call edges.\n")
        before = (profile.read_bytes(), profile.stat().st_mtime_ns)
        self.upstream_change()
        report = user.update_skill(True, cwd=self.project)
        self.assertEqual(report["local_context"]["capture_profiles"], ["code-reading.md"])
        self.assertEqual(report["local_context"]["layout"]["version"], 2)
        self.assertEqual(before, (profile.read_bytes(), profile.stat().st_mtime_ns))

    def test_audit_comparison_classifies_findings(self):
        old = {"code": "old", "path": "llvm/A.md"}
        same = {"code": "same", "path": "shared/B.md"}
        new = {"code": "new", "path": "llvm/C.md"}
        result = user.compare_audits({"status": "checked", "findings": [old, same]},
                                     {"status": "checked", "findings": [same, new]})
        self.assertEqual(result["introduced"], [new])
        self.assertEqual(result["resolved"], [old])
        self.assertEqual(result["unchanged_count"], 1)


if __name__ == "__main__":
    unittest.main()
