# Changelog

Notable changes to the OpenEcon.ai plugin catalog. Catalog releases are tagged
`vX.Y.Z`. Each entry lists the plugin release tags that the catalog pins; plugin
tags use `<plugin>--vX.Y.Z`.

## v0.1.6 - 2026-11-07

Pins:

- `econ-review--v0.3.3` (was `econ-review--v0.3.2`)
- `econ-write--v0.1.2` (unchanged)
- `econ-slides--v0.3.1` (unchanged)
- `matlab-plot-skill--v0.2.2` (unchanged)

The new pin has the full commit its tag points to as its `sha`, in both
manifests. The descriptions, the licenses, and the standalone prompts match
the pinned releases unchanged.

## v0.1.5 - 2026-11-07

Pins:

- `econ-review--v0.3.2` (was `econ-review--v0.3.1`)
- `econ-write--v0.1.2` (unchanged)
- `econ-slides--v0.3.1` (was `econ-slides--v0.3.0`)
- `matlab-plot-skill--v0.2.2` (was `matlab-plot-skill--v0.2.1`)

Each new pin has the full commit its tag points to as its `sha`, in both
manifests. The descriptions, the licenses, and the standalone prompts match
the pinned releases unchanged.

## v0.1.4 - 2026-11-07

Pins:

- `econ-review--v0.3.1` (was `econ-review--v0.3.0`)
- `econ-write--v0.1.2` (unchanged)
- `econ-slides--v0.3.0` (was `econ-slides--v0.2.0`)
- `matlab-plot-skill--v0.2.1` (was `matlab-plot-skill--v0.2.0`)

Each new pin has the full commit its tag points to as its `sha`, in both
manifests. Checked with Claude Code 2.1.319 and Codex CLI 0.164.0.

Added:

- A CI job that checks every pinned release tag on GitHub.
- Tests check that each pinned plugin passes `claude plugin validate` and
  ships the expected skills, and that the skills table lists every skill.
- A "Report a problem" README section and a new-issue page that link to each
  plugin's own repository. Blank issues stay available for the catalog itself.

Changed:

- "Use one method per client" moves before Install. It says that a skill
  installed both ways loads twice, where to find a standalone copy that an
  earlier prompt installed (including the older `~/.codex/skills` folder),
  and whether to keep it or remove it.
- The git prerequisite says to use Claude Code 2.1.288 or newer with git
  older than 2.39, because earlier versions can fail to install Econ Review or
  install an incomplete copy.
- The Econ Review prerequisites now say that the setup never uploads a
  manuscript, as Econ Review's README does.
- The Econ Review prerequisites follow Econ Review 0.3.1 on Python 3.15: it
  worked in a macOS test, but 3.13 or 3.14 is the safer choice.
- The Econ Review entry's description is copied from its 0.3.1 manifest: run
  econ-review-setup after each plugin update, as well as after a direct
  install. The other descriptions, the licenses, and the standalone prompts
  match the pinned releases unchanged.
- The maintainer release checks move from the README to `RELEASING.md`.

## v0.1.3 - 2026-11-07

Pins:

- `econ-review--v0.3.0` (was `econ-review--v0.2.2`)
- `econ-write--v0.1.2` (unchanged)
- `econ-slides--v0.2.0` (new)
- `matlab-plot-skill--v0.2.0` (new)

Added:

- Econ Slides (`econ-slides`) in the Claude Code and Codex manifests, as
  requested in hanlulong/econ-slides-skill#1.
- MATLAB Plot (`matlab-plot-skill`) in both manifests. Its plugin root is the
  repository root, so both entries use a `url` source. It needs a local
  MATLAB install.
- A 40-character commit `sha` next to the `ref` of Econ Review, Econ Slides
  and MATLAB Plot, in both manifests: the commit each release tag points to.
  Both clients install the pinned commit.
- An MIT `LICENSE` for the catalog's own files.
- This changelog, and a top-level `version` in the Claude Code manifest.
- GitHub Actions: the offline tests and a JSON check on Ubuntu and macOS,
  `claude plugin validate . --strict`, a weekly report-only link check, and
  Dependabot updates for the pinned actions.

Changed:

- The README leads with the native plugin commands for both clients. The
  paste-to-agent prompts move under "Standalone install", copied from the
  source repositories, and the README says that the Econ Review, Econ Write,
  and MATLAB Plot prompts replace the matching `@openeconai` plugin in that
  client.
- The README documents the namespaced skill names, the one-step
  `--marketplace` install, Claude Code's auto-update default for third-party
  marketplaces, the one-method-per-client rule, and pinning the catalog to a
  release tag.
- The README states each plugin's license, including Econ Review's PolyForm
  Noncommercial terms.
- The README adds "Before you start" (supported clients, git, and each
  plugin's prerequisites), says whether to type each command in a session or
  in the terminal and when to start a new session, asks for econ-review-setup
  again after an Econ Review update, and adds an "Uninstall" section that
  removes Econ Review's support data before the plugin, after checking that
  no other copy needs it.
- The Update section says how to update a standalone copy, and asks you to
  run only the lines for the plugins you installed, since `codex plugin add`
  installs a missing one. The Codex skill names use the `$plugin:skill` form
  from the source READMEs.
- Each entry's description and license, and the Econ Review, Econ Slides
  and MATLAB Plot standalone prompts, are copied from the pinned release,
  including Econ Slides' new description and its TeX-distribution and
  `uv pip install -p` prompt.
- The opt-in published-source check also compares each entry's description and
  license with the pinned `plugin.json`, and checks that the standalone
  prompts match the source READMEs at the pinned tag. It checks that each tag
  peels to the pinned `sha`, and skips a tag that is not published yet unless
  `OPENECONAI_REQUIRE_PUBLISHED_TAGS=1` is set.
- A new opt-in check, `OPENECONAI_LOCAL_SOURCES`, compares the catalog with
  the pinned commit in local clones of the source repositories before their
  tags are published.

## v0.1.2 - 2026-07-15

Pins `econ-review--v0.2.2` and `econ-write--v0.1.2`. The tag is on the pull
request head (874c2b2), whose tree is identical to the merge commit (58ee30c).

## v0.1.1 - 2026-07-14

Pins `econ-review--v0.2.1` and `econ-write--v0.1.1`. The README leads with
paste-to-agent prompts that follow each source repository's `INSTALL.md`, and
the direct plugin commands move into a collapsed section.

## v0.1.0 - 2026-07-14

Launches the `openeconai` marketplace for Claude Code
(`.claude-plugin/marketplace.json`) and Codex
(`.agents/plugins/marketplace.json`), pinning `econ-review--v0.2.0` and
`econ-write--v0.1.0`.
