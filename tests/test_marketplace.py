#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MANIFEST = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_NAMES = ["econ-review", "econ-write"]
EXPECTED_SOURCES = {
    "econ-review": {
        "source": "git-subdir",
        "url": "https://github.com/hanlulong/econ-paper-review-skill.git",
        "path": "econ-review",
        "ref": "econ-review--v0.2.0",
    },
    "econ-write": {
        "source": "url",
        "url": "https://github.com/hanlulong/econ-writing-skill.git",
        "ref": "econ-write--v0.1.0",
    },
}


def strict_json(path: Path) -> dict:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict:
        result: dict = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def plugins_by_name(marketplace: dict) -> dict[str, dict]:
    plugins = marketplace["plugins"]
    return {plugin["name"]: plugin for plugin in plugins}


class MarketplaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.claude = strict_json(CLAUDE_MANIFEST)
        self.codex = strict_json(CODEX_MANIFEST)
        self.claude_plugins = plugins_by_name(self.claude)
        self.codex_plugins = plugins_by_name(self.codex)

    def test_one_identity_exposes_exactly_two_plugins_in_both_clients(self) -> None:
        for marketplace in (self.claude, self.codex):
            with self.subTest(manifest=marketplace):
                self.assertEqual(marketplace["name"], "openeconai")
                names = [plugin["name"] for plugin in marketplace["plugins"]]
                self.assertEqual(names, PLUGIN_NAMES)
                self.assertEqual(len(names), len(set(names)))

    def test_client_manifests_have_identical_sources_and_pins(self) -> None:
        for name in PLUGIN_NAMES:
            with self.subTest(plugin=name):
                self.assertEqual(self.claude_plugins[name]["source"], EXPECTED_SOURCES[name])
                self.assertEqual(self.codex_plugins[name]["source"], EXPECTED_SOURCES[name])
                self.assertEqual(
                    self.claude_plugins[name]["source"],
                    self.codex_plugins[name]["source"],
                )
                ref = EXPECTED_SOURCES[name]["ref"]
                self.assertRegex(ref, rf"^{re.escape(name)}--v\d+\.\d+\.\d+$")

    def test_claude_manifest_contains_only_claude_catalog_fields(self) -> None:
        self.assertEqual(
            self.claude["$schema"],
            "https://json.schemastore.org/claude-code-marketplace.json",
        )
        self.assertEqual(self.claude["owner"]["name"], "OpenEcon.ai")
        self.assertNotIn("interface", self.claude)
        for plugin in self.claude["plugins"]:
            with self.subTest(plugin=plugin["name"]):
                self.assertNotIn("policy", plugin)
                self.assertIn("displayName", plugin)
                self.assertIn("description", plugin)

    def test_codex_manifest_contains_required_policy_and_no_claude_metadata(self) -> None:
        self.assertEqual(self.codex["interface"]["displayName"], "OpenEcon.ai")
        self.assertNotIn("$schema", self.codex)
        self.assertNotIn("owner", self.codex)
        for plugin in self.codex["plugins"]:
            with self.subTest(plugin=plugin["name"]):
                self.assertEqual(
                    plugin["policy"],
                    {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                )
                self.assertEqual(plugin["category"], "Education & Research")
                self.assertNotIn("displayName", plugin)
                self.assertNotIn("author", plugin)
                self.assertNotIn("license", plugin)

    def test_https_sources_are_portable_and_versioned(self) -> None:
        for name, source in EXPECTED_SOURCES.items():
            with self.subTest(plugin=name):
                self.assertTrue(source["url"].startswith("https://github.com/"))
                self.assertTrue(source["url"].endswith(".git"))
                self.assertIn("ref", source)
                self.assertNotIn("sha", source)

    def test_documentation_uses_only_the_shared_identity(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for selector in ("econ-review@openeconai", "econ-write@openeconai"):
            self.assertIn(selector, readme)
        self.assertIn("OpenEconAI/plugins", readme)
        self.assertNotIn("@econ-paper-review", readme)

    def test_catalog_contains_no_embedded_plugin_payload(self) -> None:
        self.assertFalse((ROOT / "econ-review").exists())
        self.assertFalse((ROOT / "econ-write").exists())

    def test_catalog_contains_exactly_two_client_manifests(self) -> None:
        manifests = sorted(
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("marketplace.json")
            if ".git" not in path.parts
        )
        self.assertEqual(
            manifests,
            [".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"],
        )


if __name__ == "__main__":
    unittest.main()
