#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"
PUBLISHED_MARKETPLACE = os.environ.get(
    "OPENECONAI_MARKETPLACE_SOURCE",
    "OpenEconAI/plugins",
)
CHECK_SOURCES = os.environ.get("OPENECONAI_CHECK_PUBLISHED_SOURCES") == "1"
CHECK_INSTALLS = os.environ.get("OPENECONAI_CHECK_PUBLISHED_INSTALLS") == "1"
EXPECTED_VERSIONS = {"econ-review": "0.2.2", "econ-write": "0.1.2"}


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=env,
        timeout=180,
    )
    if result.returncode != 0:
        details = [
            f"command failed with exit code {result.returncode}: {command!r}",
        ]
        if result.stdout.strip():
            details.append(f"stdout:\n{result.stdout.strip()}")
        if result.stderr.strip():
            details.append(f"stderr:\n{result.stderr.strip()}")
        raise AssertionError("\n".join(details))
    return result


def source_version(name: str, ref: str) -> str:
    match = re.fullmatch(rf"{re.escape(name)}--v(\d+\.\d+\.\d+)", ref)
    if match is None:
        raise AssertionError(f"unexpected release ref for {name}: {ref}")
    return match.group(1)


def require_executable(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise unittest.SkipTest(f"{name} is not installed")
    return executable


@unittest.skipUnless(
    CHECK_SOURCES,
    "set OPENECONAI_CHECK_PUBLISHED_SOURCES=1 to verify remote release refs",
)
class PublishedSourceTests(unittest.TestCase):
    def test_pinned_tags_exist_and_plugin_manifests_match(self) -> None:
        git = require_executable("git")
        marketplace = load_json(CLAUDE_MANIFEST)

        with tempfile.TemporaryDirectory(prefix="openeconai-source-check-") as temp_root:
            for plugin in marketplace["plugins"]:
                name = plugin["name"]
                source = plugin["source"]
                url = source["url"]
                ref = source["ref"]
                version = source_version(name, ref)

                with self.subTest(plugin=name, ref=ref):
                    run(
                        [
                            git,
                            "ls-remote",
                            "--exit-code",
                            "--refs",
                            url,
                            f"refs/tags/{ref}",
                        ]
                    )
                    checkout = Path(temp_root) / name
                    run(
                        [
                            git,
                            "clone",
                            "--depth=1",
                            "--branch",
                            ref,
                            "--single-branch",
                            url,
                            str(checkout),
                        ]
                    )
                    plugin_root = checkout / source.get("path", "")
                    claude = load_json(plugin_root / ".claude-plugin" / "plugin.json")
                    codex = load_json(plugin_root / ".codex-plugin" / "plugin.json")
                    self.assertEqual(claude["name"], name)
                    self.assertEqual(codex["name"], name)
                    self.assertEqual(claude["version"], version)
                    self.assertEqual(codex["version"], version)
                    self.assertEqual(claude["version"], codex["version"])


@unittest.skipUnless(
    CHECK_INSTALLS,
    "set OPENECONAI_CHECK_PUBLISHED_INSTALLS=1 to exercise the published catalog",
)
class PublishedInstallTests(unittest.TestCase):
    def test_claude_discovers_and_installs_both_plugins(self) -> None:
        claude = require_executable("claude")
        with tempfile.TemporaryDirectory(prefix="openeconai-claude-") as config_dir:
            env = os.environ.copy()
            env["CLAUDE_CONFIG_DIR"] = config_dir
            env["GIT_TERMINAL_PROMPT"] = "0"
            run([claude, "plugin", "marketplace", "add", PUBLISHED_MARKETPLACE], env=env)
            listing = json.loads(
                run([claude, "plugin", "marketplace", "list", "--json"], env=env).stdout
            )
            self.assertIn("openeconai", {entry["name"] for entry in listing})
            for name in EXPECTED_VERSIONS:
                run([claude, "plugin", "install", f"{name}@openeconai"], env=env)
            installed = json.loads(run([claude, "plugin", "list", "--json"], env=env).stdout)
            installed_versions = {entry["id"]: entry["version"] for entry in installed}
            self.assertEqual(
                {
                    f"{name}@openeconai": installed_versions[f"{name}@openeconai"]
                    for name in EXPECTED_VERSIONS
                },
                {
                    f"{name}@openeconai": version
                    for name, version in EXPECTED_VERSIONS.items()
                },
            )

    def test_codex_discovers_and_installs_both_plugins(self) -> None:
        codex = require_executable("codex")
        with tempfile.TemporaryDirectory(prefix="openeconai-codex-") as codex_home:
            env = os.environ.copy()
            env["CODEX_HOME"] = codex_home
            env["GIT_TERMINAL_PROMPT"] = "0"
            run([codex, "plugin", "marketplace", "add", PUBLISHED_MARKETPLACE, "--json"], env=env)
            listing = json.loads(
                run(
                    [
                        codex,
                        "plugin",
                        "list",
                        "--marketplace",
                        "openeconai",
                        "--available",
                        "--json",
                    ],
                    env=env,
                ).stdout
            )
            self.assertEqual(
                {entry["name"] for entry in listing["available"]},
                set(EXPECTED_VERSIONS),
            )
            for name in EXPECTED_VERSIONS:
                run([codex, "plugin", "add", f"{name}@openeconai", "--json"], env=env)
            installed = json.loads(run([codex, "plugin", "list", "--json"], env=env).stdout)
            installed_versions = {
                entry["name"]: entry["version"] for entry in installed["installed"]
            }
            self.assertEqual(installed_versions, EXPECTED_VERSIONS)


if __name__ == "__main__":
    unittest.main()
