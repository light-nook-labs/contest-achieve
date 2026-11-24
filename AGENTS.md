# AGENTS.md

Instructions for agents working in this repository. Read this first, then `README.md` and `HANDOFF.md`.

## What this repository is

A centralized archive of SFACG (sfacg.com) novel-contest rosters and awards, plus a JSON-driven static site served via GitHub Pages from `docs/`.

It is an **independent project**, not a subdirectory of `novly-proj`. It stores only:
- contest rosters (the list of participating novels)
- award records (manually correctable)

It does **not** store mutable observation fields (word count, favorites, likes, status). Those belong to the downstream dataset in `novly-proj` and must not be added here.

## Language

- Repository documentation and site copy: Chinese (existing convention).
- This file is in English by explicit request; keep it English.

## Environment

Managed by uv. Dependencies are in `pyproject.toml`, locked in `uv.lock`. No manual venv setup needed — `uv run` creates the environment and installs dependencies on first use.

Always run scripts via `uv run python ...`. The system Python lacks `requests`. The static site has no Python template dependency: Vue 3 is vendored in `site/assets/vue.global.prod.js`.

## Hard rules

1. **`contest_track_id` is the primary key.** Directory names, site URLs and query parameters key off this numeric ID. Contest names and URLs change; it does not. `tagIds` / `tagId` in URL templates are raw upstream API parameter names, not archive keys.
2. **URLs live in `contests.json`.** To handle SFACG URL format changes, edit only that file — never hardcode URLs into scripts or site code. `url_template` is the roster API template (placeholder `{contest_track_id}`); `activity_url` is the official event page where winners are posted. Both are per-track metadata, not mutable observations.
3. **Unified schema only.** Normalize all source differences in `tools/harvest.py::normalize`. `roster.jsonl` must be exactly six fields: `nid/title/author/form_id/intro/cover`. `form_id` is a work-form code (`0`=full/medium novel, `1`=dialogue novel, `3`=short story), **not** a genre and **not** "unclassified".
4. **Awards and rosters are independent.** `awards.jsonl` is a static, human-editable layer. Never derive roster content from awards or vice versa.
5. **Never invent award names.** Unknown awards must be written as `待逐档标定` with evidence in `source`. Finalists / preliminary-review lists are NOT awards — do not mix them in. See `reference/sfacg-contest-archive.md` §4.
6. **Do not trust HTTP status codes.** A response counts as valid only if it contains a `novels` array with legal fields. Some dead tracks return 200 with a text page.
7. **Pagination is 0-based** for both old and new endpoints. On empty responses, retry at smaller sizes (500 → 200 → 20 → 1).
8. **Contests 1/2/3 have no API** (confirmed by user via DevTools). Do not attempt to add them.
9. **Numbers in reference docs are snapshots** — compute current values or mark them as such; never hardcode counts into code.

## Workflow

```bash
# collect rosters (resumable; skips already-collected nids)
uv run python tools/harvest.py --all
uv run python tools/harvest.py --tags 793 794

# validate (no --strict = only collected contests; --strict = require all 100)
uv run python tools/verify.py

# rebuild JSON data + static shells after ANY data change, then commit docs/
uv run python tools/build_site.py
```

## File map

| Path | Role |
|---|---|
| `contests.json` | Track registry: `contest_track_id`, `contest_name`, `series`, `api_generation`, `page_start`, `url_template`, `activity_url`, `start_date` / `end_date` / `result_date` (see `schema/contests.md`; only documented dates, empty string when unknown) |
| `schema/contests.md`, `schema/roster.md`, `schema/awards.md` | Canonical record formats |
| `data/<contest_track_id>/{meta.json,roster.jsonl,awards.jsonl}` | Per-track archive |
| `tools/harvest.py` | Collector with normalization and resume |
| `tools/verify.py` | Schema/coverage validator |
| `tools/import_awards.py` | One-time migration of 911 awards from novly-proj |
| `tools/migrate_keys.py` | One-time, idempotent key migration (kept for audit; archive is already migrated) |
| `tools/add_activity_urls.py` | One-time, idempotent `activity_url` backfill from the authoritative event-page ledger (already applied) |
| `tools/import_awards_13th.py` | One-time, idempotent 13th-contest award calibration from the official event page (25 rows, already applied) |
| `tools/prune_13th_unverified.py` | One-time, idempotent removal of 431 unverified entries in track 752 (already applied) |
| `tools/prune_all_unverified.py` | One-time, idempotent removal of the remaining 421 unverified entries (already applied) |
| `tools/build_site.py` | JSON exporter + static shell copier → `docs/` |
| `site/` | Static site source: three HTML shells, `app.js`, CSS, vendored Vue 3 |
| `reference/sfacg-contest-archive.md` | Concise authoritative reference: two APIs, field mapping, track-ID ledger pointer, URL generations, award formats and rules |
| `HANDOFF.md` | Current state, remaining work, and pitfalls (Chinese) |

## Site architecture

`docs/` is no longer generated per-contest HTML. It contains three static shells plus JSON:

- `docs/index.html` (award-count column links to the per-contest award list), `docs/contest.html?contest_track_id=…`, `docs/awards.html?contest_track_id=…` (single-contest award list with official announcement link at top)
- `docs/data/site.json` — build time and aggregate stats
- `docs/data/contests.json` — all tracks with counts and last capture
- `docs/data/roster/<contest_track_id>.json` — roster, fetched on demand
- `docs/data/awards.json` — 69 awards with redundant `contest_track_id/contest_name/series` for filtering

Vue renders each page at runtime. Because browsers block `fetch()` on `file://`, preview through GitHub Pages or `python -m http.server` from `docs/`.

## Current state (2026-11-23)

- Rosters collected: **all 100 tracks, 135,663 rows**. `verify.py --strict` passes; no empty tracks.
- Awards: 69 records across 8 tracks, all verified. 25 of the 13th contest (tracks 752/753/754) were calibrated from the official event page, confirmed by the user. All 852 unverified `待逐档标定` entries migrated from the upstream net-list were deleted (user judged them unreliable); only official announcements / manually confirmed facts count as awards. The agent does not collect or calibrate awards unless explicitly asked.
- Key migration done: `tag→contest_track_id`, `name→contest_name`, `endpoint→api_generation` (`old/new`→`legacy/modern`), `url→url_template`, `category_id→form_id`; roster keeps the concise `nid/title/author/intro/cover`.
- Site rebuilt as JSON-driven shells; repository not yet committed/pushed.

## Remaining work

1. Keep `contests.json` URL templates in sync if SFACG changes them.
2. After any future roster change, re-run `verify.py` and `build_site.py`, then commit `docs/` if requested.
3. Award records stay manually maintained by the user; the agent does not modify them unless explicitly asked. Only verified facts are written — never migrate pending/unverified entries. For a known official event page, extracting awards via hardcoded `openNovel(nid)` in the SPA JS + award level in image filenames is more reliable than OCR.
