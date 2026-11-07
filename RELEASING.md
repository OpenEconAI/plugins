# Releasing the catalog

To release a plugin through the catalog, update its `ref` and `sha` in both
`.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`. The
`sha` is the full commit the tag peels to. Once the tag is pushed, run
`git ls-remote <url> 'refs/tags/<ref>' 'refs/tags/<ref>^{}'` and take the
`^{}` line (an annotated tag) or else the only line (a lightweight tag). Before
then, `git rev-parse HEAD` in the source clone gives it only if the tag will go
on that exact commit. A tag on a squash or merge commit points to a commit
that does not exist yet, so pin the branch tip for the checks below and
replace the `sha` once the tag is pushed. Get the pin right before users
install it: Claude Code does not update an installed plugin whose version is
unchanged, so a corrected `sha` with the same version never reaches them.

Copy the `description` and `license` from the pinned commit's
`.claude-plugin/plugin.json` into the Claude entry (and a summary into the
table at the top of the README), and copy the plugin's standalone prompt from
its README into the README's **Standalone install**. Then update
`EXPECTED_SOURCES` in `tests/test_marketplace.py` and `EXPECTED_VERSIONS` in
`tests/test_published_release.py`, and `EXPECTED_SKILLS` in
`tests/test_marketplace.py` when a plugin adds or renames a skill. Bump the
catalog `version` in `.claude-plugin/marketplace.json` and in the pin examples
under **Versions** in the README, add a dated heading for it to the changelog,
and tag the catalog's merge commit as `vX.Y.Z`; plugin tags use
`<plugin>--vX.Y.Z`.

Run the offline catalog and schema checks before every release:

```bash
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
```

Before the plugin tags are published, check the catalog against local clones
of the source repositories. Put each clone, checked out at the commit you will
tag, in one folder under its repository name (`econ-paper-review-skill`,
`econ-writing-skill`, `econ-slides-skill`, `matlab-plot-skill`). The check
requires each clone's `HEAD` to be the pinned `sha`, or, for a pin on a squash
or merge commit, a fetched local tag that peels to the `sha` and has the same
tree as `HEAD`. It then compares the plugin manifests and README at that
commit, not the working tree, with the catalog entry and the standalone
prompts in the README:

```bash
OPENECONAI_LOCAL_SOURCES=/path/to/folder-with-clones \
  python3 -m unittest discover -s tests -p 'test_published_release.py' -v
```

After publishing the pinned plugin tags, run the same checks against GitHub.
Each tag must peel to the pinned `sha`, and the manifests and README at the tag
must match. Each pinned plugin must also ship the skills in `EXPECTED_SKILLS`
and, where `claude` is installed, pass `claude plugin validate`. A tag that is
not on GitHub yet is reported as skipped;
`OPENECONAI_REQUIRE_PUBLISHED_TAGS=1` makes it fail instead, so use it for the
final run:

```bash
OPENECONAI_CHECK_PUBLISHED_SOURCES=1 OPENECONAI_REQUIRE_PUBLISHED_TAGS=1 \
  python3 -m unittest discover -s tests -p 'test_published_release.py' -v
```

CI runs this check on every pull request and on pushes to main, so a PR that
changes a pin shows a failing **Published sources** check until its source tags
are on GitHub.

After publishing this catalog, exercise clean installations with both clients:

```bash
OPENECONAI_CHECK_PUBLISHED_INSTALLS=1 \
  python3 -m unittest discover -s tests -p 'test_published_release.py' -v
```
