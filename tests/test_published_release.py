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

# unittest discover puts tests/ on sys.path; this binds the dict, not a TestCase.
from test_marketplace import EXPECTED_SKILLS


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"
README = ROOT / "README.md"
PUBLISHED_MARKETPLACE = os.environ.get(
    "OPENECONAI_MARKETPLACE_SOURCE",
    "OpenEconAI/plugins",
)
CHECK_SOURCES = os.environ.get("OPENECONAI_CHECK_PUBLISHED_SOURCES") == "1"
CHECK_INSTALLS = os.environ.get("OPENECONAI_CHECK_PUBLISHED_INSTALLS") == "1"
# A pinned tag that is not on its remote yet is skipped, not failed, so the
# check can run before every source is published. Set this to 1 for the final
# post-publish run, where a missing tag must fail.
REQUIRE_TAGS = os.environ.get("OPENECONAI_REQUIRE_PUBLISHED_TAGS") == "1"
# A directory holding clones of the source repositories, one folder per
# repository name (econ-paper-review-skill, econ-writing-skill, ...). When set,
# LocalSourceTests compares the catalog with the pinned commit in each clone
# before publishing.
LOCAL_SOURCES = os.environ.get("OPENECONAI_LOCAL_SOURCES", "")
# Held by its maintainer: pinned by ref only, and the README keeps the
# standalone prompt from the catalog's main branch.
HELD_PLUGINS = {"econ-write"}
EXPECTED_VERSIONS = {
    "econ-review": "0.3.1",
    "econ-write": "0.1.2",
    "econ-slides": "0.3.0",
    "matlab-plot-skill": "0.2.1",
}


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


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


def repository_name(url: str) -> str:
    name = url.rstrip("/").rsplit("/", 1)[1]
    return name[: -len(".git")] if name.endswith(".git") else name


def fenced_text_blocks(markdown: str) -> list[str]:
    return re.findall(r"^```text\n(.*?)^```$", markdown, flags=re.M | re.S)


def standalone_prompt(readme: str, display_name: str) -> str:
    standalone = readme.split("\n## Standalone install\n", 1)[1].split("\n## ", 1)[0]
    subsection = standalone.split(f"\n### {display_name}\n", 1)[1].split("\n### ", 1)[0]
    blocks = fenced_text_blocks(subsection)
    if len(blocks) != 1:
        raise AssertionError(f"expected one standalone prompt for {display_name}")
    return blocks[0]


def require_executable(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise unittest.SkipTest(f"{name} is not installed")
    return executable


def skip_or_fail(test: unittest.TestCase, message: str) -> None:
    if REQUIRE_TAGS:
        test.fail(f"{message} (OPENECONAI_REQUIRE_PUBLISHED_TAGS=1)")
    test.skipTest(message)


# git's messages for a remote that answers but has no such repository (GitHub
# asks for credentials for a missing or private one). These fail even without
# OPENECONAI_REQUIRE_PUBLISHED_TAGS, because rerunning later will not help.
MISSING_REPOSITORY_MESSAGES = (
    "repository not found",
    "could not read username",
    "does not appear to be a git repository",
    "' not found",
)


def published_tag_commit(test: unittest.TestCase, git: str, url: str, ref: str) -> str:
    """Return the commit that refs/tags/<ref> peels to on the remote, or skip."""
    tag = f"refs/tags/{ref}"
    result = subprocess.run(
        [git, "ls-remote", "--tags", url, tag, f"{tag}^{{}}"],
        check=False,
        capture_output=True,
        text=True,
        env=git_env(),
        timeout=180,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        if any(message in stderr.lower() for message in MISSING_REPOSITORY_MESSAGES):
            test.fail(f"{url} is missing or private: {stderr}")
        skip_or_fail(
            test, f"cannot reach {url} (offline, or the repository is unreachable): {stderr}"
        )
    refs = dict(
        reversed(line.split("\t", 1)) for line in result.stdout.splitlines() if "\t" in line
    )
    # An annotated tag is listed twice; the ^{} line holds the commit it points to.
    commit = refs.get(f"{tag}^{{}}", refs.get(tag))
    if commit is None:
        skip_or_fail(test, f"{ref} is not on {url} yet; push the tag, then rerun this check")
    return commit


def assert_manifests_match_entry(
    test: unittest.TestCase, plugin: dict, claude: dict, codex: dict
) -> None:
    name = plugin["name"]
    version = source_version(name, plugin["source"]["ref"])
    test.assertEqual(claude["name"], name)
    test.assertEqual(codex["name"], name)
    test.assertEqual(claude["version"], version)
    test.assertEqual(codex["version"], version)
    test.assertEqual(version, EXPECTED_VERSIONS[name])
    test.assertEqual(plugin["description"], claude["description"])
    test.assertEqual(plugin["license"], claude["license"])
    test.assertEqual(plugin["repository"], claude["repository"])
    test.assertEqual(plugin["displayName"], codex["interface"]["displayName"])


def assert_plugin_root_matches_entry(test: unittest.TestCase, plugin: dict, plugin_root: Path) -> None:
    assert_manifests_match_entry(
        test,
        plugin,
        load_json(plugin_root / ".claude-plugin" / "plugin.json"),
        load_json(plugin_root / ".codex-plugin" / "plugin.json"),
    )


def skill_name(skill_file: Path) -> str:
    """Return the `name:` from a SKILL.md's leading `---` frontmatter block."""
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise AssertionError(f"{skill_file} has no frontmatter")
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line[len("name:") :].strip().strip("\"'")
    raise AssertionError(f"{skill_file} has no name in its frontmatter")


def skill_names(plugin_root: Path, manifest: dict) -> set[str]:
    """Return the names of the skills under a plugin manifest's `skills` paths."""
    paths = manifest.get("skills", "./skills/")
    if isinstance(paths, str):
        paths = [paths]
    names = set()
    for path in paths:
        directory = plugin_root / path
        if (directory / "SKILL.md").is_file():
            skill_files = [directory / "SKILL.md"]
        else:
            skill_files = sorted(directory.glob("*/SKILL.md"))
        names.update(skill_name(skill_file) for skill_file in skill_files)
    return names


def assert_ships_expected_skills(
    test: unittest.TestCase, name: str, plugin_root: Path, manifest_dir: str
) -> None:
    manifest = load_json(plugin_root / manifest_dir / "plugin.json")
    test.assertEqual(
        skill_names(plugin_root, manifest),
        set(EXPECTED_SKILLS[name]),
        f"the skills in {plugin_root} ({manifest_dir}) differ from EXPECTED_SKILLS[{name!r}]",
    )


def assert_prompt_matches_source(
    test: unittest.TestCase, readme: str, plugin: dict, source_readme: str, where: str
) -> None:
    prompt = standalone_prompt(readme, plugin["displayName"])
    test.assertIn(
        prompt,
        fenced_text_blocks(source_readme),
        f"the {plugin['displayName']} standalone prompt differs from {where}",
    )


def git_output(git: str, checkout: Path, *args: str) -> str:
    return run([git, "-C", str(checkout), *args], env=git_env()).stdout


def local_tag_commit(git: str, checkout: Path, ref: str) -> str:
    result = subprocess.run(
        [git, "-C", str(checkout), "rev-parse", "--verify", "--quiet", f"refs/tags/{ref}^{{commit}}"],
        check=False,
        capture_output=True,
        text=True,
        env=git_env(),
        timeout=180,
    )
    return result.stdout.strip()


@unittest.skipUnless(
    CHECK_SOURCES,
    "set OPENECONAI_CHECK_PUBLISHED_SOURCES=1 to verify remote release refs",
)
class PublishedSourceTests(unittest.TestCase):
    def test_pinned_tags_peel_to_the_pinned_sha_and_manifests_match(self) -> None:
        git = require_executable("git")
        claude = shutil.which("claude")
        marketplace = load_json(CLAUDE_MANIFEST)

        with tempfile.TemporaryDirectory(prefix="openeconai-source-check-") as temp_root:
            validate_env = git_env()
            validate_env["CLAUDE_CONFIG_DIR"] = str(Path(temp_root) / "claude-config")
            for plugin in marketplace["plugins"]:
                name = plugin["name"]
                source = plugin["source"]
                url = source["url"]
                ref = source["ref"]

                with self.subTest(plugin=name, ref=ref):
                    commit = published_tag_commit(self, git, url, ref)
                    expected = source.get("sha", commit if name in HELD_PLUGINS else None)
                    self.assertEqual(
                        commit,
                        expected,
                        f"{ref} peels to {commit} on {url}, but the catalog pins {expected}",
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
                        ],
                        env=git_env(),
                    )
                    head = run([git, "-C", str(checkout), "rev-parse", "HEAD"]).stdout.strip()
                    self.assertEqual(head, expected)
                    plugin_root = checkout / source.get("path", "")
                    assert_plugin_root_matches_entry(self, plugin, plugin_root)
                    for manifest_dir in (".claude-plugin", ".codex-plugin"):
                        assert_ships_expected_skills(self, name, plugin_root, manifest_dir)
                    # Not every source repository validates its plugin in CI, so
                    # validate each pinned tree here. Without --strict, warnings
                    # pass and only errors fail.
                    with self.subTest(plugin=name, check="claude plugin validate"):
                        if claude is None:
                            self.skipTest("claude is not installed")
                        run([claude, "plugin", "validate", str(plugin_root)], env=validate_env)

    def test_standalone_prompts_match_source_readmes(self) -> None:
        git = require_executable("git")
        marketplace = load_json(CLAUDE_MANIFEST)
        readme = README.read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory(prefix="openeconai-prompt-check-") as temp_root:
            for plugin in marketplace["plugins"]:
                name = plugin["name"]
                source = plugin["source"]
                with self.subTest(plugin=name, ref=source["ref"]):
                    if name in HELD_PLUGINS:
                        continue
                    published_tag_commit(self, git, source["url"], source["ref"])
                    checkout = Path(temp_root) / name
                    run(
                        [
                            git,
                            "clone",
                            "--depth=1",
                            "--branch",
                            source["ref"],
                            "--single-branch",
                            source["url"],
                            str(checkout),
                        ],
                        env=git_env(),
                    )
                    assert_prompt_matches_source(
                        self,
                        readme,
                        plugin,
                        (checkout / "README.md").read_text(encoding="utf-8"),
                        f"README.md at {source['ref']}",
                    )


@unittest.skipUnless(
    LOCAL_SOURCES,
    "set OPENECONAI_LOCAL_SOURCES=<dir with the source clones> to check them before publishing",
)
class LocalSourceTests(unittest.TestCase):
    def test_entries_and_prompts_match_the_pinned_local_commits(self) -> None:
        git = require_executable("git")
        marketplace = load_json(CLAUDE_MANIFEST)
        readme = README.read_text(encoding="utf-8")

        for plugin in marketplace["plugins"]:
            source = plugin["source"]
            if plugin["name"] in HELD_PLUGINS:
                continue
            sha = source["sha"]
            checkout = Path(LOCAL_SOURCES) / repository_name(source["url"])
            with self.subTest(plugin=plugin["name"], checkout=str(checkout)):
                self.assertTrue(checkout.is_dir(), f"no source clone at {checkout}")
                head = git_output(git, checkout, "rev-parse", "HEAD").strip()
                if head != sha:
                    # A tag placed on a squash or merge commit pins a commit the
                    # release branch never had. Accept it once the clone has
                    # fetched that tag and the commit's tree is the checked-out one.
                    tagged = local_tag_commit(git, checkout, source["ref"])
                    self.assertEqual(
                        tagged,
                        sha,
                        f"{checkout} is at {head}, but the catalog pins {sha}. Check out "
                        f"the commit you will tag; if {source['ref']} is already on "
                        "GitHub, run `git fetch --tags` in the clone and rerun.",
                    )
                    self.assertEqual(
                        git_output(git, checkout, "rev-parse", f"{sha}^{{tree}}"),
                        git_output(git, checkout, "rev-parse", "HEAD^{tree}"),
                        f"{source['ref']} ({sha}) does not have the tree checked out in {checkout}",
                    )
                # Read the pinned commit, not the working tree, so uncommitted
                # edits cannot make the check pass.
                prefix = f"{source['path']}/" if source.get("path") else ""
                assert_manifests_match_entry(
                    self,
                    plugin,
                    json.loads(
                        git_output(git, checkout, "show", f"{sha}:{prefix}.claude-plugin/plugin.json")
                    ),
                    json.loads(
                        git_output(git, checkout, "show", f"{sha}:{prefix}.codex-plugin/plugin.json")
                    ),
                )
                assert_prompt_matches_source(
                    self,
                    readme,
                    plugin,
                    git_output(git, checkout, "show", f"{sha}:README.md"),
                    f"README.md at {sha} in {checkout}",
                )


@unittest.skipUnless(
    CHECK_INSTALLS,
    "set OPENECONAI_CHECK_PUBLISHED_INSTALLS=1 to exercise the published catalog",
)
class PublishedInstallTests(unittest.TestCase):
    def test_claude_discovers_and_installs_every_plugin(self) -> None:
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
            install_paths = {entry["id"]: entry.get("installPath") for entry in installed}
            for name in EXPECTED_VERSIONS:
                with self.subTest(plugin=name, check="installed skills"):
                    install_path = install_paths.get(f"{name}@openeconai")
                    self.assertTrue(
                        install_path,
                        f"`claude plugin list --json` reports no installPath for {name}@openeconai",
                    )
                    assert_ships_expected_skills(self, name, Path(install_path), ".claude-plugin")
            # The right version from the wrong commit would pass the check
            # above, so compare the commit Claude Code recorded for each install.
            records = load_json(Path(config_dir) / "plugins" / "installed_plugins.json")
            installed_commits = {
                plugin_id: entries[0].get("gitCommitSha")
                for plugin_id, entries in records.get("plugins", {}).items()
                if entries
            }
            pinned_commits = {
                f"{plugin['name']}@openeconai": plugin["source"]["sha"]
                for plugin in load_json(CLAUDE_MANIFEST)["plugins"]
                if "sha" in plugin["source"]
            }
            self.assertEqual(
                {plugin_id: installed_commits.get(plugin_id) for plugin_id in pinned_commits},
                pinned_commits,
            )

    def test_codex_discovers_and_installs_every_plugin(self) -> None:
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
            added = {
                name: json.loads(
                    run([codex, "plugin", "add", f"{name}@openeconai", "--json"], env=env).stdout
                )
                for name in EXPECTED_VERSIONS
            }
            installed = json.loads(run([codex, "plugin", "list", "--json"], env=env).stdout)
            installed_versions = {
                entry["name"]: entry["version"] for entry in installed["installed"]
            }
            self.assertEqual(installed_versions, EXPECTED_VERSIONS)
            for name, result in added.items():
                with self.subTest(plugin=name, check="installed skills"):
                    # Read the path Codex reports; never guess its cache layout.
                    installed_path = result.get("installedPath")
                    if not installed_path:
                        self.skipTest(f"`codex plugin add --json` reports no installedPath for {name}")
                    assert_ships_expected_skills(self, name, Path(installed_path), ".codex-plugin")


if __name__ == "__main__":
    unittest.main()
