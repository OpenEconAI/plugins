# OpenEcon.ai Plugins

The official OpenEcon.ai marketplace for economics research tools. One catalog
installs and updates these plugins in Claude Code and Codex:

| Plugin | What it does | License |
| --- | --- | --- |
| [Econ Review](https://github.com/hanlulong/econ-paper-review-skill) (`econ-review`) | A source-grounded referee report and prioritized revision plan for an economics paper. | [PolyForm Noncommercial 1.0.0](#licenses) |
| [Econ Write](https://github.com/hanlulong/econ-writing-skill) (`econ-write`) | Write, edit, restructure, and audit economics papers. | MIT |
| [Econ Slides](https://github.com/hanlulong/econ-slides-skill) (`econ-slides`) | Economics research talks in LaTeX/Beamer: paper-to-talk decks, discussant slides, speaker scripts, and edits to existing Beamer decks. | MIT |
| [MATLAB Plot](https://github.com/hanlulong/matlab-plot-skill) (`matlab-plot-skill`) | Publication-quality MATLAB figures for papers, LaTeX or Overleaf, and Beamer slides, rendered and checked before delivery. Needs a local MATLAB. | MIT |

## Before you start

- **Client.** Claude Code, or Codex in the Codex CLI or the ChatGPT desktop
  app. Plugins aren't available in the Codex IDE extension; use a
  [standalone install](#standalone-install) there.
- **git** on your `PATH`. Both clients clone the catalog with it. On macOS,
  `xcode-select --install` provides it. With git older than 2.39 (for example
  on Ubuntu 22.04), use Claude Code 2.1.288 or newer (run `claude update`):
  earlier versions can fail to install Econ Review, or install an incomplete
  copy.
- **Econ Review:** Python 3.10 or newer with `venv` and pip. The macOS system
  `python3` is 3.9, which is too old: install Python 3.13 or 3.14 from
  [python.org](https://www.python.org/downloads/macos/) (3.15 worked in a macOS
  test, but some dependencies do not yet ship ready-made 3.15 packages, so 3.13
  or 3.14 is the safer choice), or run `brew install python@3.12` or
  `uv python install 3.12`. It also needs
  [Poppler](https://poppler.freedesktop.org/) on your `PATH` for PDF input
  (`brew install poppler`, or conda-forge). Its setup skill creates a private
  Python environment (about 80 MB) and the local Review Desk viewer, served at
  `http://127.0.0.1:48127/`, in a support folder outside both clients. The
  setup never uploads a manuscript.
- **Econ Write:** nothing else.
- **Econ Slides:** a TeX distribution with XeLaTeX (MacTeX, TeX Live, or
  MiKTeX) and Python 3.10 or newer with PyMuPDF; see its
  [README](https://github.com/hanlulong/econ-slides-skill#install).
- **MATLAB Plot:** a local MATLAB R2021a or newer with `matlab` on your
  `PATH` (check with `matlab -batch "disp(version)"`); see its
  [prerequisites](https://github.com/hanlulong/matlab-plot-skill#prerequisites).
  In Codex on macOS, approve the request to run `matlab` outside the sandbox.

## Use one method per client

In each client, install a given skill either as a plugin from this catalog or
as a standalone copy, not both: with both, the client loads the skill twice.

An earlier prompt from this page may have installed a standalone copy. Look
for `~/.claude/skills/<name>` (Claude Code), `~/.agents/skills/<name>` or the
older `~/.codex/skills/<name>` (Codex), or the same folders inside a project
(`.claude/skills/<name>`, `.agents/skills/<name>`), where `<name>` is the
plugin name, for example `econ-review`. Either keep that copy and update it by
pasting its prompt again (see [Standalone install](#standalone-install)), or
remove it before you install the plugin. For a linked Econ Slides copy, remove
only the link, not the clone it points to. Removing a standalone Econ Review
copy keeps its support data, which the plugin reuses.

## Install

### Claude Code

In a Claude Code session, type these commands: add the marketplace once, then
install each plugin you want.

```text
/plugin marketplace add OpenEconAI/plugins
/plugin install econ-review@openeconai
/plugin install econ-write@openeconai
/plugin install econ-slides@openeconai
/plugin install matlab-plot-skill@openeconai
```

In a session, `/plugin install` opens the plugin's details; choose a scope
there to finish installing. On Claude Code 2.1.275 or later,
`/plugin install econ-review --marketplace OpenEconAI/plugins` adds the
marketplace and opens the plugin in one step.

Or run these in your terminal, outside Claude Code:

```bash
claude plugin marketplace add OpenEconAI/plugins
claude plugin install econ-review@openeconai
claude plugin install econ-write@openeconai
claude plugin install econ-slides@openeconai
claude plugin install matlab-plot-skill@openeconai
```

On Claude Code 2.1.292 or later,
`claude plugin install econ-review --marketplace OpenEconAI/plugins` does both
steps at once. Then start a new Claude Code session, or run `/reload-plugins`
in an open one, before you use the skills.

### Codex

In your terminal, add the marketplace once, then add each plugin you want:

```bash
codex plugin marketplace add OpenEconAI/plugins
codex plugin add econ-review@openeconai
codex plugin add econ-write@openeconai
codex plugin add econ-slides@openeconai
codex plugin add matlab-plot-skill@openeconai
```

Or run `codex`, then type `/plugins` to browse and install them in a session.
Then start a new Codex session before you use the skills; bundled skills load
in new sessions.

### Finish setup

Native plugin clients cannot run Econ Review's machine setup automatically at
install time. After installing Econ Review, send the agent:

```text
Run econ-review-setup now and finish its user-level setup with Review Desk.
```

The setup writes to its support folder and may download Python packages. In
Codex, approve its requests to do so outside the sandbox.

The other plugins are ready once the client loads them and the tools under
[Before you start](#before-you-start) are installed.

### Use the skills

Plugin skills are namespaced by plugin. The skills can also activate from an
ordinary request, such as "review this paper in quick mode".

| Plugin | Claude Code | Codex (type `$`, or `@` to pick the plugin or skill) |
| --- | --- | --- |
| Econ Review | `/econ-review:econ-review`, `/econ-review:econ-review-setup` | `$econ-review:econ-review`, `$econ-review:econ-review-setup` |
| Econ Write | `/econ-write:econ-write` | `$econ-write:econ-write` |
| Econ Slides | `/econ-slides:econ-slides` | `$econ-slides:econ-slides` |
| MATLAB Plot | `/matlab-plot-skill:matlab-plot-skill` | `$matlab-plot-skill:matlab-plot-skill` |

## Update

These steps update plugin installs. A standalone copy from one of the
"Install or update" prompts under [Standalone install](#standalone-install)
updates when you paste that prompt again; for a linked Econ Slides copy, run
`git pull` in its clone.

Run only the lines for the plugins you installed. To add another plugin, use
the commands under [Install](#install).

Claude Code turns auto-update off by default for third-party marketplaces such
as this one. To turn it on, run `/plugin`, open the **Marketplaces** tab,
select **openeconai**, and choose **Enable auto-update**. To update now, select
**Update marketplace** there instead: it updates every plugin you installed
from this catalog. Or run these in your terminal:

```bash
claude plugin marketplace update openeconai
claude plugin update econ-review@openeconai
claude plugin update econ-write@openeconai
claude plugin update econ-slides@openeconai
claude plugin update matlab-plot-skill@openeconai
```

Restart Claude Code, or run `/reload-plugins`, to load the updates.

Codex, in your terminal (skip the lines for plugins you never installed,
because `codex plugin add` also installs a plugin you don't have yet):

```bash
codex plugin marketplace upgrade openeconai
codex plugin add econ-review@openeconai
codex plugin add econ-write@openeconai
codex plugin add econ-slides@openeconai
codex plugin add matlab-plot-skill@openeconai
```

Then start a new Codex session to load the updates.

After Econ Review updates in either client, including an automatic update,
send the agent this message in a new session:

```text
Run econ-review-setup now and finish its user-level setup with Review Desk.
```

This moves the shared support data, including Review Desk, to the version the
updated plugin ships. It reuses the managed runtime when its requirements are
unchanged and reports "Already current" for anything that is.

## Uninstall

### Econ Review's support data comes first

Removing the Econ Review plugin keeps its support data: the private Python
environment, its descriptor, and Review Desk. The same data serves the plugin
in both clients and every standalone copy, so remove it only when you are
removing the last Econ Review copy. Check first; these commands change
nothing: `claude plugin list` and `codex plugin list` show the plugin in each
client, and a standalone copy lives in `~/.claude/skills/econ-review` (Claude
Code) or `~/.agents/skills/econ-review` (Codex), or in a project's
`.claude/skills` or `.agents/skills` folder. If no other copy remains, remove
the data before you uninstall the plugin, while its cleanup script is still
installed. In a session where the plugin is loaded, send the agent:

```text
Remove Econ Review's support data with econ-review-setup.
```

The agent shows what the cleanup would delete and waits for your confirmation.
If the plugin is already gone, delete the support folder yourself. On macOS it
is `~/Library/Application Support/econ-review`: open it in Finder with
**Go > Go to Folder**, or quote it in a terminal, because the path contains a
space (`rm -rf "$HOME/Library/Application Support/econ-review"`). On Linux it
is `${XDG_DATA_HOME:-$HOME/.local/share}/econ-review`, and on Windows
`%USERPROFILE%\.econ-review`. A custom support location you chose is never
deleted automatically.

### Remove the plugins

In your terminal, run the lines for the plugins you installed, in the client
you use. Claude Code:

```bash
claude plugin uninstall econ-review@openeconai
claude plugin uninstall econ-write@openeconai
claude plugin uninstall econ-slides@openeconai
claude plugin uninstall matlab-plot-skill@openeconai
```

These remove user-scope installs, the default. If you chose the project or
local scope when installing, add `--scope project` or `--scope local`, or
uninstall from the **Installed** tab in `/plugin`.

Codex:

```bash
codex plugin remove econ-review@openeconai
codex plugin remove econ-write@openeconai
codex plugin remove econ-slides@openeconai
codex plugin remove matlab-plot-skill@openeconai
```

To remove the catalog too, run `claude plugin marketplace remove openeconai`
or `codex plugin marketplace remove openeconai`. In Claude Code this also
uninstalls every plugin you installed from it. In Codex it does not: installed
plugins stay and keep loading, so remove them first (`codex plugin remove`
still works after the catalog is gone). Start a new session afterwards (in
Claude Code, `/reload-plugins` also works).

## Standalone install

Standalone copies of Econ Review, Econ Write, and MATLAB Plot keep the short
skill names: `/econ-review`, `/econ-write`, and `/matlab-plot-skill` in Claude
Code, `$econ-review`, `$econ-write`, and `$matlab-plot-skill` in Codex. A
linked Econ Slides copy keeps `/econ-slides` in Claude Code.

Paste a prompt into the client you want to set up. Your agent runs the steps
itself; approve its permission prompts when asked. The Econ Review, Econ
Write, and MATLAB Plot prompts replace any `econ-review@openeconai`,
`econ-write@openeconai`, or `matlab-plot-skill@openeconai` plugin in that
client.

### Econ Review

```text
Install or update Econ Review as a standalone skill for this client. Read and
follow the complete instructions at
https://github.com/hanlulong/econ-paper-review-skill/blob/main/INSTALL.md.
Handle installation, same-client migration, and verification yourself; keep
exactly one active copy for this client, do not change the other client, and do
not ask me to run commands. Report completion or the one genuine blocker.
```

### Econ Write

```text
Install or update Econ Write for me. Read and follow the complete agent
instructions at https://github.com/hanlulong/econ-writing-skill/blob/main/INSTALL.md.
Handle every step yourself, including migration and verification. Do not ask me
to run commands. Finish with a concise result.
```

### Econ Slides

This prompt does not remove the plugin. Uninstall `econ-slides@openeconai`
from that client first (`claude plugin uninstall econ-slides@openeconai` or
`codex plugin remove econ-slides@openeconai`).

```text
Help me install the econ-slides skill from
https://github.com/hanlulong/econ-slides-skill: clone it to a stable location,
then link its skills/econ-slides folder as an Agent Skill — into
~/.claude/skills/econ-slides for Claude Code and ~/.agents/skills/econ-slides
for Codex (whichever of the two I use).
Verify that xelatex is available, that `python3 --version` is 3.10 or newer,
and that python3 can import pymupdf (PyMuPDF). If xelatex is missing, tell me
which TeX distribution to install (MacTeX, TeX Live or MiKTeX). If the Python
version or the PyMuPDF check fails, create ~/.venvs/econ-slides with a Python
3.10+ and install the repo's requirements.txt there (for example
`uv venv -p 3.12 ~/.venvs/econ-slides && uv pip install -p ~/.venvs/econ-slides -r requirements.txt`),
and tell me to run the skill's scripts with that venv's python. Then confirm
the skill loads.
```

### MATLAB Plot

```text
Install or update matlab-plot-skill as a standalone skill for the client I am
using (Claude Code or Codex) from https://github.com/hanlulong/matlab-plot-skill.
If the matlab-plot-skill@openeconai plugin is installed in this client, remove
it first. Clone the repo to a stable folder outside every skills directory, or
git pull an existing clone, then run its installer for this client only:
./install.sh --target claude|codex --force (or .\install.ps1 -Target
claude|codex -Force on Windows). If the installer warns about an older copy in
~/.codex/skills, remove it with the command it prints. Check that
`matlab -batch "disp(version)"` works (in Codex, run it outside the sandbox).
If matlab is not on PATH, look in /Applications/MATLAB_R20*.app/bin,
C:\Program Files\MATLAB\R20*\bin or /usr/local/MATLAB/R20*/bin and tell me how
to add it. Then confirm the skill loads.
```

Each source repository documents its other installation methods, updates, and
removal.

## Report a problem

Report a problem with a plugin in its own repository:
[Econ Review](https://github.com/hanlulong/econ-paper-review-skill/issues/new/choose),
[Econ Write](https://github.com/hanlulong/econ-writing-skill/issues/new),
[Econ Slides](https://github.com/hanlulong/econ-slides-skill/issues/new/choose),
or [MATLAB Plot](https://github.com/hanlulong/matlab-plot-skill/issues/new/choose).
Open an issue here only for the catalog itself, such as a broken install
command or a wrong pin.

## Licenses

Each plugin keeps the license of its source repository; this catalog does not
change those terms.

| Plugin | License | Terms |
| --- | --- | --- |
| Econ Review | [PolyForm Noncommercial 1.0.0](https://github.com/hanlulong/econ-paper-review-skill/blob/main/LICENSE) | Source-available. Free for personal research, study, and other noncommercial use. Commercial use needs separate terms: contact [hanlulong@gmail.com](mailto:hanlulong@gmail.com). |
| Econ Write | [MIT](https://github.com/hanlulong/econ-writing-skill/blob/main/LICENSE) | Open source. |
| Econ Slides | [MIT](https://github.com/hanlulong/econ-slides-skill/blob/main/LICENSE) | Open source. |
| MATLAB Plot | [MIT](https://github.com/hanlulong/matlab-plot-skill/blob/main/LICENSE) | Open source. MATLAB itself is licensed separately by MathWorks. |

The catalog's own files (the marketplace manifests, this README, and the
tests) are available under the [MIT License](LICENSE).

## Versions

Each catalog entry pins a release tag of its plugin (`ref`). An entry that
also lists a `sha` pins the commit that tag points to: Claude Code and Codex
both install that commit, so moving the tag later does not change what you
get.
The [changelog](CHANGELOG.md) lists the pins in every catalog release. To stay
on one catalog release, add the marketplace at its tag:

```text
/plugin marketplace add OpenEconAI/plugins#v0.1.5
```

```bash
codex plugin marketplace add OpenEconAI/plugins --ref v0.1.5
```

If you already added `openeconai` without a tag, both clients refuse to add it
again from a different source, so remove it first with
`claude plugin marketplace remove openeconai` or
`codex plugin marketplace remove openeconai`. In Claude Code that also
uninstalls its plugins, so reinstall them afterwards; Econ Review's support
data is kept.

## Maintainer release checks

Maintainers: see [RELEASING.md](RELEASING.md).
