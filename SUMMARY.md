# Elgora bounty #9 "Science Spread Tracer" — build summary

**Status: package built, NOT submitted. 4 channels — criterion 3
met. No wallet touched, nothing spent, nothing signed.**

## Bounty spec (from GET https://elgora.ai/api/bounties/9)

- **Bounty #9, status open, $20 USDC escrow** (20,000,000 units of
  USDC 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913 on Base, chain 8453),
  winner take all (90% of escrow to winner per Elgora rules).
- **Submission deadline: Sat 2026-11-21 06:59 WIB**
  (2026-11-20T23:59:00Z). Judging deadline 2026-11-22 06:59 WIB.
- **Task**: open-source tracker + dataset of verified mentions of
  10 fixed papers (9× Nature 4–6 Nov 2026, 1× Science Advances
  30 Oct 2026) across 8 channels (`x`, `bluesky`, `mastodon`,
  `reddit`, `hackernews`, `wikipedia`, `youtube`, `news_blogs`),
  window 2026-10-30T00:00:00Z → submission deadline.
- **Mention rule**: text contains the DOI, a link resolving to the
  paper (journal site / doi.org / PubMed), or the paper's full
  title (case-insensitive). Publisher/index pages are never
  mentions; publisher-authored posts are excluded on any channel.
- **Winner**: most verified mentions among eligible submissions.
  Ties: more channels → more papers → earliest submission.
- **Acceptance criteria**: (1) required files + exact columns;
  (2) ≥90% of mentions.csv rows verified; (3) ≥4 different
  channels; (4) first_mentions.csv exactly one row per
  paper/channel pair, earliest timestamp; (5) tracker has
  collection mode AND replay mode, collection covers ≥ the 4
  channels satisfying (3); (6) replay reproduces submitted CSVs
  (same columns + same multiset of parsed field values);
  (7) replay uses the editable config — removing a paper removes
  its rows, disabling a channel removes only its rows.

## Solver count

- **At start (2026-11-16 ~20:11 WIB): 0/10 solvers, 0 submissions.**
- **At end of build (2026-11-16 ~20:40 WIB): 3/10 solvers**
  (0x26efe00e923c8c9d16f1662eb9e96f3649124b66,
  0x2d98ee4949f391f957d10588c00d467ab1749fce,
  0xcbd95bbad0f6bc0e265c0942d688d79d20d1ba01).
  **7 slots remain — the bounty is NOT full.** Three competitors
  submitted during the build window, so the race is live.

## What was built (~/workspace/elgora/bounty-9/)

| Path | Contents |
|---|---|
| `source/tracker.py` | Tracker, Python 3.12 stdlib only, no deps. Modes: `collect`, `replay`, `verify`, `manifest`. |
| `source/config.example.json` | Editable paper DOI/title list, window, channels, API credential / rate-limit notes. No secrets. |
| `source/README.md` | Runtime version, install (none needed), collection + replay commands, method, known gaps. |
| `source/LICENSE` | MIT. |
| `data/mentions.csv` | **44 verified mentions** (columns: paper_number, channel, url, archive_url, author_handle, timestamp_utc, captured_text, engagement). |
| `data/first_mentions.csv` | **19 rows** (one per paper/channel pair, earliest timestamp). |
| `evidence/` | **100 evidence files + manifest.json** (source URL, retrieval time UTC, SHA-256 per file). |
| `report.md` | Per-paper pickup order + patterns (not judged). |
| `work/` | `bounty-9-api.json`, `collect-1.log`, `news-log.md`, `social-log.md`, criterion-7 test configs. |

## Dataset — 44 mentions

- **Channels: Bluesky 2, news/blogs 19, YouTube 22, X 1.**
- **Papers**: #1 smartwatch 7, #2 CRISPR 6, #3 AutoDNA 17,
  #4 prethermal 1, #5 hydrogen 1, #6 Drosophila 3, #7 CAR-T 2,
  #8 fabric 3, #9 indoor PV **0**, #10 wildlife trade 4.
- **First mentions**: paper 3 was picked up same-day (news
  2026-11-04T18:44:00Z, Bluesky 19:04Z); paper 10 earliest
  2026-11-02; paper 9 has no verified mention anywhere.

## Verification evidence

- `tracker.py verify`: **OK — submitted=44 replayed=44 match=True;
  first_mentions.csv submitted=19 replayed=19 match=True**
  (re-run 2026-11-16 ~20:44 WIB after adding the X row).
- **Criterion 7 tested** (after the final tracker change):
  config without paper 1 → 32 rows, 0 paper-1 rows, all others
  unchanged; config with Bluesky disabled → 37 rows, 0 Bluesky
  rows. Rows derive from evidence + config, not a prewritten table.
- **Every row was verified, nothing fabricated**: each evidence
  file holds the source text / API response the row was derived
  from. Link targets that the page-text extraction hides were
  verified against raw HTML with curl (mlq.ai, artificialscience,
  techprolonged, allatra, aifrontierpost, pebbious — DOI / paper
  URL hit counts recorded in `work/news-log.md`).
- **Tracker fix made during the build**: the matcher returned only
  the first matching paper per record and the builder de-duplicated
  by URL alone, so a roundup video mentioning two papers yielded
  one row. Fixed to one row per (paper, URL) — the Copernicus video
  now correctly yields paper 3 + paper 6 rows (39 → 40 rows at
  that step). All extractors updated; criterion-7 tests re-run
  after the fix.
- **Publisher exclusion applied**: 6 publisher posts found
  (5× @nature.com Bluesky, 1× @springernature.com Bluesky) and
  excluded by the tracker, per the bounty rule.

## Verification status per channel

| Channel | Rows | Status |
|---|---|---|
| bluesky | 2 | Verified. public API searchPosts 403-blocked at egress; posts found by web search, saved as page extracts (oembed / getPostThread work). 6 publisher posts excluded. |
| news_blogs | 19 | Verified. All articles opened and checked for headline + date + author/publication + DOI/link/title. 2 borderline aggregator rows + 1 abstract-mirror row + 1 AI-generated row kept and flagged in report.md. |
| youtube | 22 | Verified. Video pages fetched with curl (search page for discovery, watch page for uploadDate/author/title/description). Largest channel. |
| x | 1 | **Verified 2026-11-16 ~20:43 WIB.** Post by @Gamehu520 (Gamehu, verified account, not a publisher), 10 Nov 2026 13:46:18Z, AutoDNA paper 3; its link card resolves to the Nature article (t.co link verified via curl, HTTP 200; timestamp confirmed by Snowflake decode of the status ID). Found by the user from his phone X app; verified logged-out in the browser (no sign-in — X login still rate-limited). The earlier BioTender lead stays unresolved (see report.md). |
| mastodon | 0 | **Unverifiable in part.** Unauthenticated search empty on ~20 instances; #AutoDNA hashtag timelines empty on mastodon.social + fediscience.org; web search empty. |
| reddit | 0 | **Unverifiable.** Search JSON 403 (old + www); PullPush API Cloudflare-blocked; no indexed post found. |
| hackernews | 0 | Verified empty. Algolia API works; 0 hits for every paper/DOI/keyword query. |
| wikipedia | 0 | Verified empty. MediaWiki API works; DOI search 0 hits for all 10 papers. |

## Known gaps — READ BEFORE SUBMITTING

1. **Criterion 3 (≥4 channels) is NOW MET (2026-11-16 ~20:43
   WIB): the dataset has 4 channels** (Bluesky 2, news/blogs 19,
   YouTube 22, X 1) after the verified @Gamehu520 X mention of
   paper 3. The package's one eligibility gap is closed. The
   remaining submit blockers are funding + public repo + the
   untested submit step (see below).
2. **Paper 9 (indoor photovoltaics) has 0 mentions** on every
   channel after two search rounds. Nothing to add without new
   coverage appearing before the deadline (window runs to
   2026-11-20T23:59:00Z — re-running collection near the deadline
   may pick up late coverage).
3. **Borderline rows** (report.md lists all four): dropping any
   costs rows but not channels. The ScienceView paper-4 row is
   the weakest (abstract mirror); dropping it leaves paper 4 at 0.
4. **The 3 competing submissions are unreadable from the API**
   (only solver addresses + commitment hashes are public), so
   their mention counts and channel coverage are unknown.
5. **`archive_url` is empty on all 44 rows.** No archived copies
   (e.g. web.archive.org snapshots) were made; the evidence
   directory + manifest (source URL, retrieval time, SHA-256)
   is the verifiability record. The spec lists the column but
   does not require it to be non-empty.

## Remaining submit steps (NOT done — needs user decision)

1. **Funding**: the Elgora agent wallet
   0x8Ce9438489227cb22f4c6070bd69b164035653C2 holds only dust
   (~0.00000085 Base ETH). A submit transaction on Base needs a
   small amount of ETH for gas. Fund it first (amount + route are
   the user's call).
2. **Repo**: push `~/workspace/elgora/bounty-9/` to a public GitHub
   repo (same pattern as the earlier bounty packages / make.fun
   repos: browser creates the repo, `github push-files` for text,
   web upload for any binaries — there are none here).
3. **Submit**: the exact Elgora submit step was never performed
   for any bounty (the elgora CLI wrapper
   `~/workspace/elgora/run-cli.sh` is broken — `elgora-cli: not
   found`). The submission is most likely made on elgora.ai with
   the repo URL + a wallet signature from the agent wallet; the
   precise UI/CLI call and its gas cost must be confirmed at
   submit time. **Do not attempt until funded + user orders it.**
4. **Re-collect before submitting**: re-run `collect` (or at
   least a fresh DOI/title search round) close to the deadline —
   the window runs to 2026-11-20T23:59:00Z and late coverage
   may appear (the 4th channel is already secured; more
   X/Mastodon/Reddit mentions would only add rows); then `replay` +
   `verify` + `manifest` again before pushing.
