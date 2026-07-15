# OpenEcon.ai Plugins

The official OpenEcon.ai marketplace for economics research tools. One catalog
provides native installation and updates for Claude Code and Codex.

## Install or update

Paste the prompt for the plugin you want into Codex or Claude Code. Your agent
will follow the current installation contract, handle migration and updates,
and verify the result without asking you to run commands.

### Econ Review

```text
Install or update Econ Review. Read and follow the complete instructions at
https://github.com/hanlulong/econ-paper-review-skill/blob/main/INSTALL.md.
Handle the entire installation and verification yourself; do not ask me to run
commands. Report completion or the one genuine blocker.
```

### Econ Write

```text
Install or update Econ Write for me. Read and follow the complete agent
instructions at https://github.com/hanlulong/econ-writing-skill/blob/main/INSTALL.md.
Handle every step yourself, including migration and verification. Do not ask me
to run commands. Finish with a concise result.
```

Each prompt also performs future updates. Econ Review reuses compatible,
verified support state.

<details>
<summary>Direct plugin commands</summary>

Add the shared marketplace once.

Claude Code:

```text
/plugin marketplace add OpenEconAI/plugins
/plugin install econ-review@openeconai
/plugin install econ-write@openeconai
```

Codex:

```bash
codex plugin marketplace add OpenEconAI/plugins
codex plugin add econ-review@openeconai
codex plugin add econ-write@openeconai
```

Native plugin clients cannot run Econ Review's machine setup automatically at
install time. After a direct Econ Review install, send the agent:

```text
Run econ-review-setup now and finish its user-level setup with Review Desk.
```

Econ Write is ready after the client loads the plugin.

For direct updates:

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

</details>

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
