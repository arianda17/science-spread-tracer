# Science Spread Tracer — collection report (not judged)

Dataset built 2026-11-16. Tracker + dataset: 44 verified mentions of
10 papers across 4 channels (Bluesky 2, news/blogs 19, YouTube 22,
X 1).
Window: 2026-10-30T00:00:00Z – 2026-11-20T23:59:00Z.
Full method and per-candidate logs: `work/news-log.md`,
`work/social-log.md`, `source/README.md`.

## Per-paper pickup order

| # | Paper (short) | Rows | Channels | First mention |
|---|---|---|---|---|
| 1 | Smartwatch hypertension | 7 | bluesky, news, youtube | 2026-11-05T16:48:50Z Bluesky (@spjuraschek, paper co-author) |
| 2 | CRISPR ANGPTL3 | 6 | news, youtube | 2026-11-06T22:53:04Z YouTube |
| 3 | AutoDNA AI-native lab | 16 | bluesky, news, youtube | 2026-11-04T18:44:00Z news (The World of AI, same day as publication) |
| 4 | Prethermal phase transitions | 1 | news | 2026-11-04T00:00:00Z news (ScienceView, borderline — see below) |
| 5 | Hydrogen derivatives China | 1 | news | 2026-11-09T00:28:39Z news (ScienMag) |
| 6 | Drosophila courtship | 3 | news, youtube | 2026-11-04T18:00:04Z news (Phys.org, same day) |
| 7 | CAR-T double knockout | 2 | news, youtube | 2026-11-06T05:58:40Z YouTube |
| 8 | Molecularly woven fabric | 3 | news, youtube | 2026-11-04T21:49:40Z YouTube (same day) |
| 9 | Indoor photovoltaics | 0 | — | no verified mention on any channel |
| 10 | Wildlife trade | 4 | news, youtube | 2026-11-02T12:50:00Z news (Newswise) |

## Patterns

- **AutoDNA (paper 3) dominates**: 17 of 44 rows. Fastest pickup
  (news + Bluesky within hours of publication), the most roundup /
  aggregator coverage, and the only paper with long-form explainers
  a week later (AI Frontier Post Nov 6, Pebblous Nov 8). It also
  produced the most rejected near-misses (liveinthefuture.org,
  wisevoter.com — articles about the paper with no DOI, no paper
  link and no full title in the text).
- **YouTube is the volume channel**: 22 rows, mostly small
  explainer / paper-summary channels (Latest Scientific Papers,
  ScienceNow!, Copernicus, FUERA DE ESPECIE) posting within 1–2
  days of publication with the DOI and full title in the video
  description. One video can cover several papers: the Copernicus
  episode links both the AutoDNA paper and the Drosophila paper,
  and yields one row per paper.
- **News wires are same-day for the accessible papers**
  (MedicalXpress / Phys.org on papers 1 and 6 within hours) but
  slow for others (CAR-T news Nov 12, 8 days after publication;
  woven fabric news Nov 12).
- **Bluesky is thin after the publisher exclusion**: the most
  active posters are the publishers themselves (@nature.com,
  @springernature.com — 6 posts found, all excluded by the bounty
  rule). The only surviving Bluesky rows are a paper co-author
  posting his own paper (Juraschek, paper 1) and a science
  communicator (Stephen Turner, paper 3).
- **The long tail (papers 4, 5, 9)**: a theory paper, an
  energy-systems paper and a review/roadmap paper. Paper 4 has
  exactly one row (a ScienceView release page that mirrors the
  paper abstract — borderline, flagged below). Paper 5 has one
  (ScienMag, 5 days after publication). Paper 9 has zero verified
  mentions on any channel after two search rounds.
- **Confusion risk (paper 2)**: a different CRISPR trial (CTX310,
  AHA presentation) dominated CRISPR news in the same week;
  several videos and articles about CTX310 were rejected because
  they do not name the Nature paper.
- **No Hacker News, no Wikipedia**: the public APIs work and were
  queried for every paper/DOI — zero hits on both. The papers are
  too new (4–6 Nov) for Wikipedia articles to cite them yet, and
  no HN discussion exists.

## Borderline rows (kept, flagged — submitter may drop any of them)

- `news_04_prethermal-scienceview.json` (paper 4): the ScienceView
  page is a release page whose text is the paper abstract, not a
  written news article. Kept because it has a headline (the full
  title), a date, a publication name and a verified doi.org link
  to the paper. Dropping it costs 1 row; paper 4 would go to 0.
- `news_03_autodna-theworldofai.json` and
  `news_03_autodna-ai-hpc.json` (paper 3): aggregator / roundup
  style pages (daily briefing, weekly watch) with a substantive
  written section on AutoDNA, headline, date and paper link.
- `news_03_autodna-pebblous.json` (paper 3): the page labels the
  article "AI-generated". Substantive long-form analysis with
  sources; the bounty spec does not exclude AI-generated articles.
- `news_01_smartwatch-watchesreviewed.json` (paper 1): saved as
  evidence but yields **0 rows** in the tracker — its text has no
  DOI, no full title and no resolvable paper link. It is in
  `evidence/` for transparency, not in the dataset.

## The 4th channel — found via X (2026-11-16 ~20:43 WIB)

Acceptance criterion 3 needs 4 different channels; this dataset
now has 4 (Bluesky, news/blogs, YouTube, X). What was tried for
the 4th:

- **X — FOUND**: post by @Gamehu520 (Gamehu, verified, not a
  publisher), 10 Nov 2026 13:46:18Z, AutoDNA paper 3, link card
  to the Nature article (t.co verified via curl, HTTP 200;
  timestamp confirmed by Snowflake decode of the status ID).
  Found by the user from his phone X app; verified logged-out
  in the browser (X login still rate-limited). The earlier
  BioTender lead (@Junioryu136689, seen as a retweet on a
  TwStalker mirror) stays unresolved — TwStalker profile pages
  expose only recent tweets, TwStalker search returns nothing,
  xcancel returns HTTP 451, a nitter instance was unreachable.
- **Mastodon**: unauthenticated search returns empty on ~20
  instances; #AutoDNA hashtag timelines on mastodon.social and
  fediscience.org are empty; web-index searches empty.
- **Reddit**: search JSON 403 on both old and www reddit; PullPush
  API Cloudflare-blocked; no indexed post found.
- **Hacker News / Wikipedia**: APIs work, zero hits for all 10
  papers.

Criterion 3 is now met — the 4th channel (X) is verified, so the
package is submittable once funded + pushed to a public repo.
