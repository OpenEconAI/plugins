# OpenEcon.ai Plugins

The official OpenEcon.ai marketplace for economics research tools. One catalog
provides native installation and updates for Claude Code and Codex.

## Add the marketplace

Claude Code:

```text
/plugin marketplace add OpenEconAI/plugins
```

Or from a terminal:

```bash
claude plugin marketplace add OpenEconAI/plugins
```

Codex:

```bash
codex plugin marketplace add OpenEconAI/plugins
```

## Install a plugin

### Econ Review

```text
/plugin install econ-review@openeconai
```

```bash
codex plugin add econ-review@openeconai
```

### Econ Write

```text
/plugin install econ-write@openeconai
```

```bash
codex plugin add econ-write@openeconai
```

Econ Write is ready when the plugin is loaded. Econ Review bundles its complete
first-party workflow, setup tool, and verified Review Desk. It does not bundle
a Python interpreter, third-party Python packages, or Poppler. After installing
Econ Review, paste this into your assistant:

```text
Use econ-review-setup to finish setup on this machine. Show me the dry run, then
prepare its private user-level Python runtime and Review Desk. Check PDF support.
Do not install system packages; if Poppler is missing, report the options and
wait for separate instructions.
```

Running setup after reviewing the dry run may download the version-constrained
Python dependencies. Poppler installation remains a separate user decision.

## Update

Claude Code:

```bash
claude plugin marketplace update openeconai
claude plugin update econ-review@openeconai
claude plugin update econ-write@openeconai
```

Codex:

```bash
codex plugin marketplace upgrade openeconai
codex plugin add econ-review@openeconai
codex plugin add econ-write@openeconai
```

## Source and licensing

The catalog points to versioned releases in the
[Econ Review](https://github.com/hanlulong/econ-paper-review-skill) and
[Econ Writing Skill](https://github.com/hanlulong/econ-writing-skill)
repositories. Each plugin retains the license stated in its source repository;
this catalog does not alter those terms.

## Maintainer release checks

Run the offline catalog and schema checks before every release:

```bash
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
```

After publishing the pinned plugin tags, verify that each tag exists and that
its Claude and Codex manifests match the tag version:

```bash
OPENECONAI_CHECK_PUBLISHED_SOURCES=1 \
  python3 -m unittest discover -s tests -p 'test_published_release.py' -v
```

After publishing this catalog, exercise clean installations with both clients:

```bash
OPENECONAI_CHECK_PUBLISHED_INSTALLS=1 \
  python3 -m unittest discover -s tests -p 'test_published_release.py' -v
```
