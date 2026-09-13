# patches/

Host-local patches that have **no upstream home**. These are not plugins — `hermes plugins
install` will not touch this directory, and nothing here is installable.

They live here because a patch that exists only on one machine is one `git pull` away from
disappearing. Each entry records what it changes, why, what it was applied against, and how to
re-apply it.

| Patch | Applies to | Base revision |
|---|---|---|
| [`tradingagents-settings-from-config.patch`](tradingagents-settings-from-config.patch) | `~/.hermes/plugins/tradingagents` (third-party plugin) | `130ba17d75207a990f55cc956ef2b3b643709167` |

## Trading agents — read settings from `config.yaml`

The plugin reads `TRADINGAGENTS_DIR`, `TRADINGAGENTS_EXEC_MODE`, `TRADINGAGENTS_PYTHON`,
`TRADINGAGENTS_WATCHLIST` and `TRADINGAGENTS_TIMEOUT_SECONDS` from the environment only. The
patch adds `_configured_settings()` / `_setting()` so they can also come from
`plugins.entries.tradingagents.settings` in `config.yaml`, with the environment still winning.

**Load-bearing:** without it the `settings:` block is ignored, `EXEC_MODE=local` is lost, and the
plugin silently falls back to docker mode.

```bash
cd ~/.hermes/plugins/tradingagents
git diff > /tmp/backup.patch                 # keep whatever is there now
git apply /path/to/tradingagents-settings-from-config.patch
```

Re-apply after `hermes plugins update tradingagents` — that command re-syncs the clone from
`cfournel/hermes-tradingagents-plugin` and discards local edits.

**Worth upstreaming.** Nothing in the patch is deployment-specific; "read plugin settings from
`config.yaml`" is a generic improvement to that plugin. A fork + PR against
`cfournel/hermes-tradingagents-plugin` would retire this entry.

## Retired: Langfuse environment tagging

A patch here used to switch the bundled Langfuse plugin's `environment` / `release` /
`base_url` lookups from `_secret(...)` (profile secret scope) to `_env(...)`. It was
**unnecessary**: the plugin only passes `environment=` to the SDK when the value is
non-empty, and `langfuse._client.client` falls back to
`os.environ["LANGFUSE_TRACING_ENVIRONMENT"]` (and `LANGFUSE_RELEASE`) on its own.

Set those SDK-native variables in `.env` instead:

```
LANGFUSE_TRACING_ENVIRONMENT=heimdall
HERMES_LANGFUSE_ENV=heimdall     # legacy; ignored on this path, kept for reference
```

Dropping the patch left the `hermes-agent` checkout with **zero** local modifications, so
upgrades stay fast-forwards.
