# Science Spread Tracer

Open-source tracker + dataset of verified public mentions of ten
Nature / Science Advances papers (published 30 Oct – 6 Nov 2026)
across eight channels (X, Bluesky, Mastodon, Reddit, Hacker News,
Wikipedia, YouTube, news/blogs). Built for Elgora bounty #9
("Science Spread Tracer", $20 USDC, winner take all: most verified
mentions among eligible submissions).

## Runtime

- **Python 3.10+** (developed and tested on Python 3.12.3).
- **Dependencies: none.** The tracker uses only the Python standard
  library (`urllib`, `csv`, `json`, `difflib`, ...). There is nothing
  to install and no pinned third-party versions to manage.

## Installation

```sh
cp source/config.example.json config.json   # edit papers / window / channels
python3 source/tracker.py --help
```

No API keys, accounts or paid services are needed for the channels
implemented in `collect` mode (Hacker News, Bluesky, Wikipedia,
Reddit, news seed URLs). See `config.example.json` for the per-channel
credentials / rate-limit notes.

## Commands

Collection (fetches public sources, saves raw evidence to `evidence/`,
then builds both CSVs from that evidence):

```sh
python3 source/tracker.py collect \
  --config source/config.example.json \
  --evidence-dir evidence \
  --out-dir data
```

Replay (rebuilds both CSVs from the supplied `evidence/` only —
no network access, no credentials, no reading of the submitted
CSVs, no hard-coded rows):

```sh
python3 source/tracker.py replay \
  --config source/config.example.json \
  --evidence-dir evidence \
  --out-dir /tmp/replay-out
```

Verify the replay reproduces the submitted CSVs (same columns and
same multiset of parsed field values, ignoring row order, quoting,
line endings and BOM):

```sh
python3 source/tracker.py verify \
  --config source/config.example.json \
  --evidence-dir evidence \
  --out-dir data
```

Regenerate the evidence manifest (`evidence/manifest.json`: one entry
per evidence file with source URL, retrieval time in UTC, SHA-256):

```sh
python3 source/tracker.py manifest --evidence-dir evidence
```

## How it works

1. **Collection.** One fetcher per API channel:
   - `hackernews`: Algolia HN search API, DOI query + title-keyword
     query per paper, restricted to the window by `created_at_i`.
   - `bluesky`: public `app.bsky.feed.searchPosts` (no auth), DOI +
     title-keyword queries, newest first.
   - `wikipedia`: MediaWiki search for the DOI, then the article's
     revisions inside the window (with content); a line diff finds
     the revision that introduced the DOI/title.
   - `reddit`: `old.reddit.com/search.json`, DOI + title-keyword
     queries (unauthenticated; may 429, retried twice).
   - `news_blogs` / `mastodon` / `youtube` / `x`: page-extract
     evidence — the article/post/video page fetched and saved with
     headline, publication time, author and full text (news pages
     were found by web search; see `report.md`). `collect` also
     supports a `news_seed_urls` list in the config, fetched and
     extracted with the same code path.
   Raw API responses / page extracts are saved verbatim as
   `evidence/<channel>_*.json` with `source_url`, `retrieved_utc`
   and the query used.
2. **Extraction (shared by collect and replay).** For each evidence
   file, the tracker matches every record against the configured
   papers: a record refers to a paper when its text contains the
   DOI, a link resolving to the paper (doi.org / journal site /
   PubMed), or the paper's full title (case-insensitive). The
   record's timestamp must fall inside the configured window
   (date-only values read as 00:00:00 UTC; earliest publication
   time wins when a page shows several). Rows are de-duplicated by
   (paper, URL): one record (e.g. a roundup video or article) may
   mention several papers, and each (paper, URL) pair is one
   mention. `captured_text` is the text around the first paper
   reference, at most 2,000 characters.
3. **Outputs.** `data/mentions.csv` (one row per mention) and
   `data/first_mentions.csv` (one row per paper/channel pair, with
   the earliest timestamp and its URL), both derived only from
   evidence + config.
4. **Config sensitivity (acceptance criterion 7).** Evidence files
   never carry paper numbers; the paper and channel are matched at
   build time from the config. Removing a paper from the config
   removes all of its rows; disabling a channel removes only that
   channel's rows; other results are unchanged.

## What counts as a verified mention

Per the bounty spec: the row's `captured_text` appears on the page
at its `url` (or its archived copy), refers to the paper in
`paper_number`, is on the given `channel`, and its `timestamp_utc`
is the original publication/posting time inside the window
(30 Oct 2026 00:00 UTC – 20 Nov 2026 23:59 UTC). Pages of the
papers' own publishers/journals and of research indexes (PubMed,
Europe PMC, Google Scholar, Semantic Scholar, ResearchGate,
Crossref, Altmetric) are never mentions. For `news_blogs`, an
article page needs a headline, a publication date and an author
byline or publication name.

## Files

```
source/
  tracker.py           the tracker (collect / replay / verify / manifest)
  config.example.json  papers, window, channels, credentials notes
  README.md            this file
  LICENSE              MIT
data/
  mentions.csv         one row per verified mention
  first_mentions.csv   earliest mention per paper/channel pair
evidence/
  manifest.json        file -> source URL, retrieved_utc, SHA-256
  <channel>_*.json     raw API responses / page extracts
report.md              per-paper channel pickup order + patterns (not judged)
```

## Known gaps (see report.md for detail)

- **Publisher posts excluded by design.** The bounty excludes the
  papers' own publishers/journals as mention sources "on any
  channel", so posts by the publisher itself (e.g. @nature.com /
  @springernature.com on Bluesky) are not counted, even though
  they are real posts. Six such posts were found and are excluded
  by the tracker (`PUBLISHER_AUTHORS` in `tracker.py`).
- **Channels with rows: 3 of 8.** The submitted dataset has rows
  on Bluesky (2), news/blogs (19) and YouTube (22) — 43 mentions
  in total. Acceptance criterion 3 requires 4 different channels;
  no 4th channel could be verified from this environment (see
  below and `report.md`). This is the package's one known
  eligibility gap: the tracker is complete and the replay is
  exact, but a 4th channel needs a verifiable mention from an
  environment with working X / Mastodon / Reddit access.
- **X**: post pages are login-walled and direct fetching is
  blocked from this environment. The one lead found (an AutoDNA
  tweet by @Junioryu136689 "BioTender", seen via a TwStalker
  mirror retweet) could not be resolved to a status URL and
  timestamp: TwStalker profile pages expose only recent tweets
  (the Nov 4-5 tweet is outside the exposed window,
  browser.find confirms "AutoDNA" is absent from the page),
  TwStalker search returns no results, xcancel returns HTTP 451,
  and a nitter instance was unreachable. No `x` rows.
- **Mastodon**: unauthenticated `api/v2/search` returns empty
  arrays on ~20 instances even for "Nature"; web-index searches
  for every DOI returned nothing; the public hashtag timelines
  for #AutoDNA on mastodon.social and fediscience.org both return
  empty arrays. No `mastodon` rows.
- **Reddit**: `old.reddit.com/search.json` and
  `www.reddit.com/search.json` both return 403 from this
  environment, the PullPush search API is Cloudflare-blocked, and
  no indexed Reddit post surfaced in web search. No `reddit` rows.
- **YouTube**: no API key was used; video pages were fetched with
  curl (search results page for discovery, watch page for
  uploadDate / author / title / description) and saved as page
  extracts. 22 rows — the largest channel in this dataset.
- **Bluesky / Reddit APIs**: `public.api.bsky.app` is 403-blocked
  at this environment's egress CDN and both reddit search JSON
  endpoints return 403 here, so the tracker's API fetchers for
  these channels cannot run in this environment. Bluesky rows in
  this submission were found by web search and saved as
  single-post page extracts; the replay path handles both
  evidence shapes identically.
- **Hacker News / Wikipedia**: the public APIs work, but the
  DOI/title searches returned no matches for these papers, so
  those channels contribute no rows.
