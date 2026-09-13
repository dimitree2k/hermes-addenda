# yeoman-a2a — Hermes side of the Hermes/Yeoman A2A profile

A Hermes plugin (`kind: platform`) that implements one **bilateral** agent-to-agent contract:
`urn:hermes-yeoman:a2a-profile:v1`. It registers the platform name `yeoman`.

This is deliberately *not* a general A2A feature. The profile URI, the pinned contract package and
the skill set are fixed for one counterparty. Hermes's bundled `a2a` plugin stays untouched and
keeps serving generic A2A peers; this plugin serves the Yeoman relationship.

## Layout

| Module | Contains | Peer-aware? |
|---|---|---|
| `transport.py` | Agent Card serving, JSON-RPC `SendMessage`, task store, polling, deadline policy, routing into the live session | **No** |
| `profile.py` | Profile URI, contract version, schema validation, skill catalogue, result builders | **Yes — the whole binding** |
| `protocol.py` | Transport primitives (task store, turn tracker, rate limiter, message shapes) | No |
| `security.py` | Peer authentication, redaction, audit log, prompt-injection framing | No |
| `tools.py` | Outbound client tools (`a2a_discover`, `a2a_call`, `a2a_skill_call`, `a2a_list`, `a2a_history`, `a2a_orchestrate`) | Partly |

`transport.py` never names the peer; every Yeoman-specific constant lives in `profile.py`. That
split is the point: when Hermes grows a generic profile seam, `profile.py` is what survives.

## Skills

| Direction | Skill | Meaning |
|---|---|---|
| Yeoman → Hermes | `search.web` | Web search via Hermes's configured providers |
| Yeoman → Hermes | `research.deep` | Long-running research: immediate `WORKING`, then polling to a structured report |
| Hermes → Yeoman | `whatsapp.send` | Deliver text / image / file / voice to a policy-approved recipient |
| Hermes → Yeoman | `media.voice.generate` | Produce a voice artifact without sending it |

Behaviour inherited from the profile contract: exactly one authoritative `application/json`
DataPart per request; schema validation in both directions; Agent Card discovery gated on live
runtime capability; idempotency by key; stable task/context correlation; a bounded deadline that
reports `DEADLINE_EXCEEDED` (retryable) rather than a generic failure.

## Install

```bash
hermes plugins install dimitree2k/hermes-addenda/yeoman-a2a --no-enable
pip install "hermes-yeoman-a2a-contracts==1.0.1"   # declare-only; Hermes never auto-installs it
hermes plugins enable yeoman-a2a
hermes gateway restart
```

Configuration is read from the `yeoman` platform section (`gateway.platforms.yeoman.extra`); the
transport's env vars keep their `A2A_*` names (`A2A_PORT`, `A2A_BEARER_TOKEN`, `A2A_PEER_TOKENS`,
`A2A_HOST`, `A2A_AGENT_NAME`, `A2A_ALLOW_ALL_USERS`, `A2A_HOME_CHANNEL`), so moving off the bundled
plugin needs no secret migration.

Run it alongside the bundled `a2a` platform only on a different port — both bind an HTTP listener.

## Retirement condition

Disable this plugin (`hermes plugins disable yeoman-a2a`) if Hermes ever ships a generic
profile/skill-provider seam on the bundled A2A platform **and** the profile can be expressed
through it. Until then this stays: the contract is bilateral and will not be absorbed upstream.
