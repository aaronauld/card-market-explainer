# Event document format

Event documents are the files the system retrieves to explain a price move. Each one describes **one dated event** (a tournament result, a set release, a rotation, a ban, a reprint, an announcement) in plain English, with metadata at the top.

They live in `data/events/`, one Markdown file per event.

## File name

`YYYY-MM-DD-short-slug.md`, using the event's `date` (below). Lowercase, hyphens, no spaces.

Examples: `2024-08-18-worlds-2024-masters-results.md`, `2023-11-03-paradox-rift-release.md`.

The file name without `.md` is the document's id. Eval entries in `docs/eval-questions.md` list these ids under **Event docs**, and recall@k checks whether they come back.

## Front matter

The file starts with a metadata block between two `---` lines. Keep it simple so it can be read without a YAML library: one `key: value` per line, and lists as lines starting with `- `.

```
---
date: 2024-08-18
start_date: 2024-08-16
title: Pokémon TCG World Championships 2024, Masters results
type: tournament_result
cards:
  - sv04-124
sets:
  - sv04
sources:
  - https://limitlesstcg.com/tournaments/420
  - https://www.pokemon.com/us/play-pokemon/worlds/2024/tcg-masters
written: 2026-10-25
---
```

| Field | Required | Meaning |
|---|---|---|
| `date` | yes | When the information became public. For a tournament, the last day (when final results were known). For a release, the release date. For an announcement, the day it was published. `YYYY-MM-DD`. |
| `start_date` | no | First day, for multi-day events. |
| `title` | yes | Short, specific title. |
| `type` | yes | One of `tournament_result`, `set_release`, `rotation`, `ban_list`, `reprint`, `announcement`, `other`. |
| `cards` | no | TCGdex card ids (from the `cards` table) that the document is about, e.g. `sv04-124`. List every printing in the data that the event affects. Cards not in the `cards` table go in the body only. |
| `sets` | no | TCGdex set ids, e.g. `sv04`. |
| `sources` | yes | URLs the facts come from, primary sources first. |
| `written` | yes | Date the document was written. |

Why these fields: `date` lets retrieval filter to events near a price move (e.g. within 30 days before it). `cards` and `sets` let it filter to events about the card in the question. `type` helps analysis later (which kinds of cause the system gets wrong).

## Body

Plain Markdown after the front matter. Aim for 100-300 words.

1. **Summary**: one or two sentences saying what happened and when.
2. **Details**: the facts a price explanation would need: placings and decks, which cards were reprinted or banned, dates things took effect. Use card names, set names and numbers in the text (e.g. "Roaring Moon ex (Paradox Rift 124)"), because retrieval matches on the words.
3. **Sources**: the source list again, with credit (e.g. "Results from Limitless TCG").

## Rules

- **Own words only.** Summarise facts; never paste text from the source. Tournament placings and dates are facts and fine to state. Credit Bulbapedia when used (non-commercial licence).
- **One event per document.** If two things happened (a release and a tournament), write two documents. Two-source eval questions rely on this.
- **No price claims.** Event documents say what happened, not what it did to prices. The system has to connect the event to the price itself; writing "this made the card spike" would leak the answer.
- **Only verified facts.** If something is unconfirmed, leave it out.

## Distractor documents

The corpus must contain more than the documents the eval questions point at. If it only held the right answers, retrieval would be trivially easy and recall@k would be meaningless. Add documents for other events in the same period (other tournaments, set releases, announcements) even when no eval question uses them. A rough target is at least two or three other documents for every one that an eval question needs.
