#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MANIFEST = ROOT / ".agents" / "plugins" / "marketplace.json"
README = ROOT / "README.md"
PLUGIN_NAMES = ["econ-review", "econ-write", "econ-slides", "matlab-plot-skill"]
# Held by its maintainer: the entry stays as on main (ref only, no sha).
HELD_PLUGINS = {"econ-write"}
EXPECTED_SOURCES = {
    "econ-review": {
        "source": "git-subdir",
        "url": "https://github.com/hanlulong/econ-paper-review-skill.git",
        "path": "econ-review",
        "ref": "econ-review--v0.3.0",
        "sha": "29af627ae6108c18057ab1db9374a247e31376a4",
    },
    "econ-write": {
        "source": "url",
        "url": "https://github.com/hanlulong/econ-writing-skill.git",
        "ref": "econ-write--v0.1.2",
    },
    "econ-slides": {
        "source": "url",
        "url": "https://github.com/hanlulong/econ-slides-skill.git",
        "ref": "econ-slides--v0.2.0",
        "sha": "92d58565a1abbdbac2b88c27cc5bab50b1672a93",
    },
    "matlab-plot-skill": {
        "source": "url",
        "url": "https://github.com/hanlulong/matlab-plot-skill.git",
        "ref": "matlab-plot-skill--v0.2.0",
        "sha": "79a90ecc53ffc636bb5baefa5ad8d227dccd8332",
    },
}
LICENSE_LABELS = {
    "MIT": "MIT",
    "PolyForm-Noncommercial-1.0.0": "PolyForm Noncommercial 1.0.0",
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


def markdown_section(markdown: str, heading: str) -> str:
    """Return one heading's section, up to the next heading of the same or higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    start = markdown.index(f"\n{heading}\n") + 1
    body = markdown[start + len(heading) :]
    end = re.search(rf"^#{{1,{level}}} ", body, flags=re.M)
    return heading + (body[: end.start()] if end else body)


def plugins_by_name(marketplace: dict) -> dict[str, dict]:
    plugins = marketplace["plugins"]
    return {plugin["name"]: plugin for plugin in plugins}


class MarketplaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.claude = strict_json(CLAUDE_MANIFEST)
        self.codex = strict_json(CODEX_MANIFEST)
        self.claude_plugins = plugins_by_name(self.claude)
        self.codex_plugins = plugins_by_name(self.codex)

    def test_one_identity_exposes_the_same_plugins_in_both_clients(self) -> None:
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

    def test_https_sources_are_portable_and_pinned_to_a_commit(self) -> None:
        for manifest, plugins in (("claude", self.claude_plugins), ("codex", self.codex_plugins)):
            for name, plugin in plugins.items():
                with self.subTest(manifest=manifest, plugin=name):
                    source = plugin["source"]
                    self.assertTrue(source["url"].startswith("https://github.com/"))
                    self.assertTrue(source["url"].endswith(".git"))
                    self.assertRegex(source["ref"], rf"^{re.escape(name)}--v\d+\.\d+\.\d+$")
                    # Both clients check out `sha` when it is set next to `ref`.
                    if name in HELD_PLUGINS:
                        self.assertNotIn("sha", source)
                    else:
                        self.assertRegex(source.get("sha", ""), r"^[0-9a-f]{40}$")

    def test_documentation_uses_only_the_shared_identity(self) -> None:
        readme = README.read_text(encoding="utf-8")
        for name in PLUGIN_NAMES:
            with self.subTest(plugin=name):
                for command in (
                    f"/plugin install {name}@openeconai",
                    f"claude plugin install {name}@openeconai",
                    f"claude plugin update {name}@openeconai",
                    f"codex plugin add {name}@openeconai",
                ):
                    self.assertIn(command, readme)
        self.assertIn("OpenEconAI/plugins", readme)
        self.assertNotIn("@econ-paper-review", readme)

    def test_documentation_leads_with_native_plugin_installation(self) -> None:
        readme = README.read_text(encoding="utf-8")
        install = markdown_section(readme, "## Install")
        standalone = " ".join(markdown_section(readme, "## Standalone install").split())
        self.assertLess(readme.index("\n## Install\n"), readme.index("\n## Standalone install\n"))
        self.assertIn("/plugin marketplace add OpenEconAI/plugins", install)
        self.assertIn("claude plugin marketplace add OpenEconAI/plugins", install)
        self.assertIn("codex plugin marketplace add OpenEconAI/plugins", install)
        self.assertIn("/plugin install econ-review --marketplace OpenEconAI/plugins", install)
        self.assertIn("claude plugin install econ-review --marketplace OpenEconAI/plugins", install)
        self.assertIn(
            "Run econ-review-setup now and finish its user-level setup with Review Desk.",
            install,
        )
        self.assertNotIn("INSTALL.md", install)
        for name in PLUGIN_NAMES:
            with self.subTest(plugin=name):
                self.assertIn(f"`/{name}:{name}`", install)
                # Codex mentions a skill as $plugin:skill, as the source READMEs do.
                self.assertIn(f"`${name}:{name}`", install)
        self.assertIn("Enable auto-update", markdown_section(readme, "## Update"))
        self.assertIn("**Update marketplace**", markdown_section(readme, "## Update"))
        self.assertIn("outside the sandbox", markdown_section(readme, "### Finish setup"))
        self.assertIn("not both", markdown_section(readme, "## Use one method per client"))

        self.assertIn(
            "github.com/hanlulong/econ-paper-review-skill/blob/main/INSTALL.md",
            standalone,
        )
        self.assertIn("github.com/hanlulong/econ-writing-skill/blob/main/INSTALL.md", standalone)
        self.assertIn("github.com/hanlulong/econ-slides-skill", standalone)
        self.assertIn("github.com/hanlulong/matlab-plot-skill", standalone)
        self.assertIn(
            "replace any `econ-review@openeconai`, `econ-write@openeconai`, or "
            "`matlab-plot-skill@openeconai` plugin in that client",
            standalone,
        )
        self.assertIn("approve its permission prompts", standalone)
        self.assertNotIn("without asking you to run commands", readme)

    def test_documentation_lists_prerequisites_before_installation(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertLess(readme.index("\n## Before you start\n"), readme.index("\n## Install\n"))
        before = " ".join(markdown_section(readme, "## Before you start").split())
        for requirement in (
            "IDE extension",
            "**git**",
            "Python 3.10 or newer",
            "Poppler",
            "XeLaTeX",
            "MATLAB R2021a or newer",
            # Econ Review 0.3.0 names tested Python versions; an unversioned
            # `brew install python` now installs the untested 3.15.
            "3.15 is not tested yet",
            "`brew install python@3.12`",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, before)
        self.assertNotIn("`brew install python`", before)
        for plugin in self.claude["plugins"]:
            with self.subTest(plugin=plugin["name"]):
                self.assertIn(f"**{plugin['displayName']}:**", before)

    def test_documentation_says_where_to_type_and_when_to_reload(self) -> None:
        readme = README.read_text(encoding="utf-8")
        install = markdown_section(readme, "## Install")
        update = markdown_section(readme, "## Update")
        self.assertIn("In a Claude Code session, type these commands", install)
        self.assertIn("in your terminal, outside Claude Code", install)
        self.assertIn("In your terminal, add the marketplace once", markdown_section(readme, "### Codex"))
        self.assertIn("start a new Claude Code session, or run `/reload-plugins`", install)
        self.assertIn("start a new Codex session", install)
        self.assertIn("start a new Codex session", update)
        self.assertIn("/reload-plugins", update)
        self.assertIn(
            "Run econ-review-setup now and finish its user-level setup with Review Desk.",
            update,
        )

    def test_update_runs_only_the_lines_for_installed_plugins(self) -> None:
        readme = README.read_text(encoding="utf-8")
        update = markdown_section(readme, "## Update")
        # `claude plugin update` fails for a plugin that is not installed, and
        # `codex plugin add` installs it, so both blocks need this warning.
        first_block = update.index("```")
        self.assertLess(
            update.index("Run only the lines for the plugins you installed."), first_block
        )
        self.assertIn("skip the lines for plugins you never installed", update)
        self.assertLess(
            update.index("skip the lines for plugins you never installed"),
            update.index("codex plugin marketplace upgrade openeconai"),
        )
        self.assertIn("including an automatic update", update)

    def test_uninstall_removes_econ_review_support_data_before_the_plugin(self) -> None:
        readme = README.read_text(encoding="utf-8")
        uninstall = markdown_section(readme, "## Uninstall")
        cleanup = uninstall.index("Remove Econ Review's support data with econ-review-setup.")
        # The shared data is removed only after a read-only check for other copies.
        for check in ("`claude plugin list`", "`codex plugin list`"):
            with self.subTest(check=check):
                self.assertLess(uninstall.index(check), cleanup)
        for name in PLUGIN_NAMES:
            for command in (
                f"claude plugin uninstall {name}@openeconai",
                f"codex plugin remove {name}@openeconai",
            ):
                with self.subTest(command=command):
                    self.assertGreater(uninstall.index(command), cleanup)
        for command in (
            "claude plugin marketplace remove openeconai",
            "codex plugin marketplace remove openeconai",
        ):
            with self.subTest(command=command):
                self.assertGreater(uninstall.index(command), cleanup)
        for path in (
            "~/Library/Application Support/econ-review",
            "${XDG_DATA_HOME:-$HOME/.local/share}/econ-review",
            "%USERPROFILE%\\.econ-review",
        ):
            with self.subTest(path=path):
                self.assertIn(path, uninstall)
        self.assertIn('"$HOME/Library/Application Support/econ-review"', uninstall)
        self.assertIn("`--scope project`", uninstall)
        # Removing the catalog uninstalls its plugins in Claude Code only.
        self.assertIn("In Codex it does not", " ".join(uninstall.split()))

    def test_documentation_states_each_plugin_license(self) -> None:
        readme = README.read_text(encoding="utf-8")
        licenses = markdown_section(readme, "## Licenses")
        for plugin in self.claude["plugins"]:
            with self.subTest(plugin=plugin["name"]):
                rows = [
                    line
                    for line in licenses.splitlines()
                    if line.startswith(f"| {plugin['displayName']} |")
                ]
                self.assertEqual(len(rows), 1)
                self.assertIn(f"[{LICENSE_LABELS[plugin['license']]}]", rows[0])
                self.assertIn(f"({plugin['repository']}/blob/main/LICENSE)", rows[0])
        self.assertIn("noncommercial", licenses)
        self.assertIn("[MIT License](LICENSE)", licenses)
        self.assertTrue((ROOT / "LICENSE").is_file())
        self.assertTrue((ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License\n"))

    def test_documentation_urls_outside_prompts_have_no_trailing_punctuation(self) -> None:
        readme = README.read_text(encoding="utf-8")
        prose = re.sub(r"^```.*?^```$", "", readme, flags=re.M | re.S)
        urls = re.findall(r"https?://[^\s)>\]`]+", prose)
        self.assertTrue(urls)
        for url in urls:
            with self.subTest(url=url):
                self.assertFalse(url.endswith((".", ",", ";", ":")))

    def test_changelog_records_the_catalog_version_and_every_pin(self) -> None:
        version = self.claude["version"]
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertNotIn("version", self.codex)
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        headings = re.findall(r"^## v(\d+\.\d+\.\d+) - \d{4}-\d{2}-\d{2}$", changelog, re.M)
        self.assertTrue(headings, "CHANGELOG.md has no dated release heading")
        self.assertEqual(headings[0], version)
        latest = changelog.split(f"## v{version} ", 1)[1].split("\n## ", 1)[0]
        for name in PLUGIN_NAMES:
            with self.subTest(plugin=name):
                self.assertIn(f"`{EXPECTED_SOURCES[name]['ref']}`", latest)

    def test_documentation_pins_the_current_catalog_release(self) -> None:
        versions = markdown_section(README.read_text(encoding="utf-8"), "## Versions")
        tag = f"v{self.claude['version']}"
        self.assertIn(f"/plugin marketplace add OpenEconAI/plugins#{tag}\n", versions)
        self.assertIn(f"codex plugin marketplace add OpenEconAI/plugins --ref {tag}\n", versions)
        self.assertEqual(set(re.findall(r"\bv\d+\.\d+\.\d+\b", versions)), {tag})
        # Re-adding an unpinned catalog at a tag fails until it is removed.
        self.assertIn("remove it first", versions)

    def test_catalog_contains_no_embedded_plugin_payload(self) -> None:
        for name in PLUGIN_NAMES:
            with self.subTest(plugin=name):
                self.assertFalse((ROOT / name).exists())

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
