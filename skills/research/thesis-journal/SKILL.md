---
name: thesis-journal
description: Use when recording, checking, or reviewing a position thesis or trade log.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [thesis, journal, positions, review]
    category: research
---

# Thesis Journal

## When to Use
- "Log my thesis for X" / "I bought X because..."
- "Does anything break my thesis on X?"
- "Weekly review" / "What did I get wrong this month?"

Not for: generating new trade ideas or a buy/sell call (use `trading-analysis`).

## Storage (local only)
`/home/deploy/Documents/research-journal/`
- `theses/<TICKER>.md`: one file per position
- `journal.md`: append-only dated entries
Never send journal contents to external services. Never copy them into memory.

## Thesis file format
```
# <TICKER> (opened YYYY-MM-DD, status: open|closed)
## Thesis (user's words)
## Assumptions (each testable)
- A1: <claim> | breaks if: <observable condition> | check via: <source>
## Exit / invalidation
## Log
- YYYY-MM-DD: <event> -> <which assumption, holds/weakened/broken> [source]
```

## Procedure
1. **Record:** write down the user's reasoning as they gave it. Then turn it into testable assumptions and confirm them with the user. Don't add assumptions they didn't make.
2. **Check:** for each assumption, gather evidence from the named source. Use `sec-filings` for filings, the web for news, and the TradingAgents report from `trading-analysis` if it is under 6 hours old (don't force a re-run). Classify each as holds, weakened, broken, or no new info. Append the result to Log.
3. **Review:** read the journal and closed theses, then compare the entry reasoning with the outcome. Name one recurring pattern. If the data is thin, say so.

## TradingAgents digest (avoid re-reading 100 KB reports)
After a TradingAgents report exists for a journaled ticker, append a digest to the thesis Log instead of re-reading the full report later:
```
- YYYY-MM-DD TA digest: decision=<BUY/HOLD/SELL> | levels: support/resistance/invalidation as stated
  | fundamentals: <3 facts, with period> | changed vs last digest: <...> | report: <abs path>
```
- For any later check, read the digests first. Open the full report only when a digest is missing or the user asks.
- Fundamentals (filings, margins, guidance) change quarterly. Technicals and news change daily. Before suggesting a new run, say which of those has actually changed since the last digest.
- Never call `tradingagents_analyze` from this skill. Suggest a run only when an assumption is weakened or broken, or the last digest is older than the user's chosen cadence.

## Rules
- Use the user's judgment. The agent never says "buy" or "sell".
- Give a source and a date for every claim of evidence. Treat rumors and social posts as unverified.
- "No new info" is a valid result. Don't invent a reason for concern.
