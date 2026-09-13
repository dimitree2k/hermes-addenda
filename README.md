# hermes-addenda

Addenda for [Hermes Agent](https://github.com/NousResearch/hermes-agent): plugins that add
capabilities the official `hermes-agent` tree does not ship.

**Why this repo exists.** Some capabilities belong to a specific deployment rather than to the
upstream product. Patching upstream to carry them means a fork, a permanent rebase burden, and a
live install that drifts from stock. Hermes supports third-party plugins natively, so those
capabilities live here instead — and the live install can track `origin/main` untouched.

This is the clean split:

| Vehicle | Purpose | Lifetime |
|---|---|---|
| **Fork + PR** against `NousResearch/hermes-agent` | *Propose* something to upstream | Temporary — delete the fork once merged |
| **This repo** | Permanent home for what upstream does not ship | Long-lived, installed as plugins |
| `hermes plugins disable <name>` | Retire an addendum once upstream ships the equivalent | The switch |

Upstream's own policy, from `plugins/AGENTS.md`:

> **Plugins never touch core** — plugins live in their own directory and work within the ABCs /
> hooks / `ctx` surface we provide. […] third-party-product plugins […] ship as standalone plugin
> repos (`~/.hermes/plugins/`).

## Addenda

| Plugin | Platform | What it adds | Upstream status |
|---|---|---|---|
| [`yeoman-a2a/`](yeoman-a2a/) | `yeoman` | Hermes side of the strict Hermes/Yeoman A2A profile (`urn:hermes-yeoman:a2a-profile:v1`) | Not proposed — bilateral integration |

Two host-local patches with no upstream home are kept in [`patches/`](patches/) — one for the
third-party `tradingagents` plugin, one for the bundled Langfuse plugin. They are not plugins and
are not installable; they exist so a `git pull` or `hermes plugins update` cannot silently drop
them.

## Install

`hermes plugins install` understands a subdirectory, so one repo can hold many addenda:

```bash
# install exactly one addendum out of this repo
hermes plugins install dimitree2k/hermes-addenda/yeoman-a2a --no-enable

# or pin immutably
hermes plugins install dimitree2k/hermes-addenda/yeoman-a2a --ref <40-hex-sha>

hermes plugins validate ./yeoman-a2a      # static check
hermes plugins doctor ./yeoman-a2a        # check against the real runtime contracts
hermes plugins capabilities               # declared vs granted capabilities
hermes gateway restart                    # activate after enabling
```

## Reproducing the whole set

`hermes plugins pack` pins a set of plugins to exact commit SHAs:

```bash
hermes plugins pack export > packs/addenda.yaml   # from a host that already has them
hermes plugins pack install packs/addenda.yaml    # on a fresh host
```

## Conventions for addenda here

1. **One directory per plugin, at the repo root.** Upstream's own
   [`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins) does the same.
2. **Self-contained.** No imports from another addendum and none from the bundled `plugins/`
   tree. Cross-plugin import paths are covered by `hermes plugins compat` precisely because they
   can move; an addendum that imports them breaks on someone else's schedule.
3. **Directory name = platform name.** The registry derives a platform name from the manifest
   `name` (stripping a trailing `-platform`) or else the directory basename. Keep them aligned:
   `yeoman-a2a/` + `name: yeoman-a2a-platform` → platform `yeoman`.
4. **One repo, one SHA.** `--ref` pins the entire repo, so tag per addendum
   (`yeoman-a2a-v1.0.0`) and treat a SHA as a set version.
5. **No credentials.** Config arrives through `requires_env` / `optional_env`, which the installer
   prompts for and writes to `.env`.
6. **Retirement is a first-class outcome.** Each addendum's README states what would let you
   disable it.
