# patches/

Host-local patches that have **no upstream home**. These are not plugins — `hermes plugins
install` will not touch this directory, and nothing here is installable.

They live here because a patch that exists only on one machine is one `git pull` away from
disappearing. Each entry records what it changes, why, what it was applied against, and how to
re-apply it.

| Patch | Applies to | Base revision |
|---|---|---|
| [`tradingagents-settings-from-config.patch`](tradingagents-settings-from-config.patch) | `~/.hermes/plugins/tradingagents` (third-party plugin) | `130ba17d75207a990f55cc956ef2b3b643709167` |
| [`langfuse-plugin-env-settings.patch`](langfuse-plugin-env-settings.patch) | `plugins/observability/langfuse/` in the `hermes-agent` checkout (bundled plugin) | upstream `422bc9bde9` at time of writing |

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

## Langfuse — take `base_url` / `environment` / `release` from the environment

The bundled Langfuse plugin resolves those three through `_secret(...)`, so
`LANGFUSE_BASE_URL` and `HERMES_LANGFUSE_ENV` never take effect. The patch switches those three
lookups to `_env(...)`, leaving `PUBLIC_KEY` / `SECRET_KEY` on the secret path.

Without it, `base_url` falls back to `https://cloud.langfuse.com` and traces lose their
`environment` / `release` tags.

```bash
cd ~/.hermes/hermes-agent
git apply /path/to/langfuse-plugin-env-settings.patch
git status --short          # expect: M plugins/observability/langfuse/__init__.py
```

This one patches a **bundled** file, so it is also the only thing keeping the `hermes-agent`
checkout dirty. Upstream may fix it eventually; check before re-applying:

```bash
grep -n 'LANGFUSE_{name}' plugins/observability/langfuse/__init__.py
# still `_secret(...)` -> patch still needed
```
