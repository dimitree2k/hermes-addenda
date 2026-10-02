---
name: market-brief
description: Use when producing a scheduled market, earnings-week, or macro brief.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [brief, macro, earnings, watchlist, cron]
    category: research
---

# Market Brief

## When to Use
A cron job or user asks for a pre-market brief, earnings-week map, macro calendar, or weekly review.

## Inputs
- Watchlist: `/home/deploy/Documents/research-journal/watchlist.txt` (one ticker per line)
- Open theses: `/home/deploy/Documents/research-journal/theses/`

## Sources
| Section | Source | Reliability |
|---|---|---|
| FOMC dates | federalreserve.gov/monetarypolicy/fomccalendars.htm | official |
| CPI / jobs dates | bls.gov release schedule (may block bots; fall back to web search, label it) | official |
| Watchlist filings | `sec-filings` skill (EDGAR) | official |
| Earnings dates | company IR page / web search | secondary; label "unconfirmed" unless IR page |
| News | web search | secondary; cite outlet + time |
| Prices / futures | none configured | omit; say "no live data" |
| Consensus estimates | none free | omit unless a cited source states it |

## Format (≤ 15 lines, Telegram-friendly)
1. Today/this week: macro events with dates and times (ET and Berlin)
2. Watchlist: new filings, then news with source and time
3. Thesis flags: any `thesis-journal` assumption touched (link the file)
4. Gaps: what couldn't be verified

## Rules
- Quiet days get a one-line brief ("Nothing material on watchlist"). Don't pad it.
- Never state a price or estimate without a source and timestamp.
- Never trigger a TradingAgents run from a brief. If a report already exists, reference it.
