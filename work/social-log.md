# Social-channel log — Elgora bounty #9 "Science Spread Tracer" (social subagent)

- Window: 2026-10-30T00:00:00Z to 2026-11-20T23:59:00Z (original post/upload time; date-only = 00:00:00 UTC).
- Mention rule: text contains the paper's DOI, a link resolving to the paper (doi.org / nature.com / science.org / PubMed), or the paper's FULL title (case-insensitive). One post/video = one mention, even if it names two papers.
- Evidence: one JSON file per verified post/video in `~/workspace/elgora/bounty-9/evidence/`, fields exactly `channel, url, retrieved_utc, headline, published_time, author, publication, text, links`.
- Work done 2026-11-16 (UTC). Read-only; no wallet actions, no submissions.

## Verified totals

| Channel | Verified | Evidence files |
|---|---|---|
| YouTube | **21** | `youtube_01`–`youtube_21` |
| Bluesky | **8** | `bluesky_01`–`bluesky_08` |
| Mastodon | **0** | — |
| Reddit | **0** | — |
| X | **0** | — |
| **Total** | **29** | |

### Per-paper verified counts (distinct posts/videos; youtube_09 counts once for paper 3 and once for paper 6 as it mentions both)

| # | Paper (short) | YouTube | Bluesky | Mastodon | Reddit | X | Total |
|---|---|---|---|---|---|---|---|
| 1 | Smartwatch hypertension | 2 | 2 | 0 | 0 | 0 | 4 |
| 2 | CRISPR base editing ANGPTL3 | 4 | 0 | 0 | 0 | 0 | 4 |
| 3 | AutoDNA AI-native lab | 7 | 2 | 0 | 0 | 0 | 9 |
| 4 | Prethermal dynamical phase transitions | 0 | 1 | 0 | 0 | 0 | 1 |
| 5 | Hydrogen derivatives China carbon neutrality | 0 | 0 | 0 | 0 | 0 | **0** |
| 6 | Drosophila courtship cues | 2 | 1 | 0 | 0 | 0 | 3 |
| 7 | In vivo CAR-T double knockout screen | 1 | 1 | 0 | 0 | 0 | 2 |
| 8 | Molecularly woven fabric | 2 | 1 | 0 | 0 | 0 | 3 |
| 9 | Indoor photovoltaics commercialization | 0 | 0 | 0 | 0 | 0 | **0** |
| 10 | Global wildlife trade data gaps | 3 | 0 | 0 | 0 | 0 | 3 |

## YouTube — 21 verified

Method: discovery via curl to `youtube.com/results?search_query=...` parsing `videoId`s, then watch-page fetch extracting `uploadDate`, author, title, `shortDescription`. No yt-dlp installed. Title/description text repaired for double-encoded UTF-8 mojibake before writing; full-title/DOI presence re-verified by grep in each written file. `published_time` converted from the page's `uploadDate` (with timezone offset) to UTC `...Z`.

| File | Video | Author | Published (UTC) | Paper(s) | Qualifying evidence |
|---|---|---|---|---|---|
| youtube_01_smartwatch-hypertension-pawpress | azbc3ahBVbo | Paw Press News | 2026-11-05T22:51:01Z | 1 | Full title + nature.com link in description |
| youtube_02_autodna-gerwynn | diKuxDcv6bI | GerWynn | 2026-11-10T04:44:33Z | 3 | DOI 10.1038/s41586-026-11228-6 in description |
| youtube_03_autodna-whoawire | Jso_YgNx2BU | Whoa Wire | 2026-11-05T22:00:01Z | 3 | Full title + nature link |
| youtube_04_autodna-neuralblack | -qJGs2y-0-o | NEURAL_BLACK | 2026-11-15T18:00:53Z | 3 | DOI + full title |
| youtube_05_autodna-intelhivehindi | 8xV9DxEy-j8 | Intellectual Hive Hindi | 2026-11-15T07:50:38Z | 3 | DOI + full title |
| youtube_06_autodna-nexosfutura | feRg50qb0bQ | Nexus Futura | 2026-11-07T19:46:44Z | 3 | DOI as plain text in description |
| youtube_07_autodna-alphaexplorer | vrE1Vy9d4fs | Alpha Explorer | 2026-11-09T03:50:51Z | 3 | Full title + nature link |
| youtube_08_autodna-latestsci | I-lSVc5XYqc | Latest Scientific Papers | 2026-11-05T01:57:49Z | 3 | DOI + full title |
| youtube_09_copernicus-autodna-drosophila | kQBXKaC9uxw | Copernicus | 2026-11-16T09:00:30Z | 3 + 6 | One video, two papers; nature links for 11228-6 and 11209-9 |
| youtube_10_crispr-latestsci | fgfOabHRD40 | Latest Scientific Papers | 2026-11-06T22:53:04Z | 2 | DOI + full title |
| youtube_11_crispr-agebiotech | HsxFTByJuPA | Age and Biotech Explorations | 2026-11-07T13:40:36Z | 2 | DOI + full title |
| youtube_12_crispr-healthbiotech | 1FJrFCPiVOg | Health, Bio Tech, Wellness and Mindfulness | 2026-11-08T15:05:34Z | 2 | Full title + nature link |
| youtube_13_crispr-fueradeespecie | 6oUkZM74wjI | FUERA DE ESPECIE | 2026-11-10T09:33:33Z | 2 | DOI (nature link in description) |
| youtube_14_drosophila-latestsci | o9R5eIMqHkA | Latest Scientific Papers | 2026-11-05T00:58:34Z | 6 | DOI + full title |
| youtube_15_cart-sciencenow | s2B8FXD9jBo | ScienceNow! | 2026-11-06T05:58:40Z | 7 | DOI + full title |
| youtube_16_fabric-latestsci | aNNvqsgCZ-c | Latest Scientific Papers | 2026-11-04T21:49:40Z | 8 | DOI + full title |
| youtube_17_fabric-sciencenow | 0sdK8ftcMv0 | ScienceNow! | 2026-11-06T01:52:03Z | 8 | DOI + full title |
| youtube_18_wildlife-mobylanguage | VAS-IR-PeeA | Moby Language Club | 2026-11-03T07:30:37Z | 10 | DOI as plain text |
| youtube_19_wildlife-lowlatency | 5SZ2gAHl2hc | Low Latency | 2026-11-12T12:50:21Z | 10 | Full title only |
| youtube_20_wildlife-twomineexplainer | IuioAL67oJo | Two Minutes Explainer | 2026-11-12T13:40:02Z | 10 | DOI + full title |
| youtube_21_smartwatch-unzappedtv | IsHi-YxowEk | unZappedTV | 2026-11-10T00:13:36Z | 1 | Full title + nature link |

### YouTube — tried and REJECTED (one-line reasons)

- CTX310 videos (ZzTqu_zbE3A, Msdqj9soUiM 2025, genetechtimes embed dU5PXzL-FVk) — different CRISPR trial, not paper 2.
- 2iFrRkUH5_8 (Spaceainews AutoDNA Shorts), rzBHwGAAkVc (fruit flies), eUnfiF3lJbU (molecular fabric), 6JFJkw7z6lM (touchscreen fabric), ZG4tEVzGREI / h0OoFApHLXc / WBdhFI9hKBc / wIfFqg_gNJ4 (general CAR-T), EgOIQ68loP4 (wildlife) — topic-only, no DOI/title/link.
- All hydrogen candidates (R2dTpPohpjI, pDhZa7Fv7D4, iDJGz9NHZP4, 6FEBLtoJ5bc, 7E1yygXQAf8, ZLPeRU-mlTg, _3B-r6XpAeM, LokLlE8GP94) — topic-only, none names paper 5.
- All prethermal candidates incl. acMfzDWZKsQ (Stanford seminar 2026-10-29) and -RQqgVU9ZXc ("180 Atoms… Prethermal State") — topic-only, none names paper 4.
- All indoor-PV candidates (XYHBEq_bnJY, oGXkHMhpI10, EeRSQUw4qp4, Fft4UT7kGxg, jWjD2O8vIpA, KaFXgWG475Q, -PwAjTiv-r8, iqX1_EqIfTg) — topic-only, none names paper 9.
- Old/unrelated prethermal, Drosophila, CAR-T videos from 2012–2025; smartwatch videos from 2024–2025 predating paper 1.

## Bluesky — 8 verified

Method: web search for discovery; `public.api.bsky.app` `searchPosts` is 403 from this VM, but `getPostThread` / `getAuthorFeed` return 200 via curl, and `embed.bsky.app/oembed` works and returns exact post text. Author feeds scanned with pagination back to 2026-10-23/26: nature.com (200 posts), springernature.com (100), natureportfolio.nature.com (100) — no posts about papers 2, 5, 9, 10. Short-link resolutions verified by following redirects with curl.

| File | URL | Author | Published (UTC) | Paper | Qualifying evidence |
|---|---|---|---|---|---|
| bluesky_01_smartwatch-springernature | bsky.app/profile/springernature.com/post/3mzvpyu7l6l2j | @springernature.com | 2026-11-09T20:06:00.405Z | 1 | spklr.io/63326EV4xM verified to resolve to nature.com/articles/s41586-026-11336-3 |
| bluesky_02_smartwatch-juraschek | bsky.app/profile/spjuraschek.bsky.social/post/3mzld4mhzqc25 | @spjuraschek.bsky.social (Stephen P Juraschek, paper coauthor) | 2026-11-05T16:48:50.573Z | 1 | Link facet + embed external URI are the full paper URL |
| bluesky_03_autodna-nature | bsky.app/profile/nature.com/post/3mzy6ms2ytr2p | @nature.com | 2026-11-10T19:33:01.007Z | 3 | Full title + go.nature.com/4jZ1dr0 → verified resolves to 11228-6 |
| bluesky_04_autodna-stephenturner | bsky.app/profile/stephenturner.us/post/3mzj2aj3flk2n | @stephenturner.us | 2026-11-04T19:04:37.523Z | 3 | Full title + nature.com/articles/s41586-026-11228-6 |
| bluesky_05_drosophila-nature | bsky.app/profile/nature.com/post/3mzzpl7wqhk27 | @nature.com | 2026-11-11T10:09:01.940Z | 6 | Full title + go.nature.com/3UyMsAM → verified resolves to 11209-9 |
| bluesky_06_woven-fabric-nature | bsky.app/profile/nature.com/post/3mzpzpqnc4i2g | @nature.com | 2026-11-07T13:43:53.550Z | 8 | Full title + go.nature.com/4iZqOPC → verified resolves to 11218-8 |
| bluesky_07_prethermal-nature | bsky.app/profile/nature.com/post/3mzzvkkrxb52d | @nature.com | 2026-11-11T11:56:02.055Z | 4 | Full title + go.nature.com/3X69EXY → verified resolves to 11225-9 |
| bluesky_08_cart-nature | bsky.app/profile/nature.com/post/3n223jvbttv2i | @nature.com | 2026-11-11T13:43:01.959Z | 7 | Full title + go.nature.com/4iXSt3k → verified resolves to 10956-z |

### Bluesky — tried and REJECTED (one-line reasons)

- nature.com post 3mzisedhtdp2f — go.nature.com/4BJp18K resolves to d41586-026-03552-8 news story, not paper 3.
- stephenturner.us post 3mzj2aikfnc2n — links d41586-026-03270-1 News & Views, not paper 3.
- nature.com post 3mzkxvh3hhs27 — go.nature.com/4kyH7Ef resolves to d41586-026-03271-0 news story, not paper 6.
- nature.com post 3mzxltz4agi2p — different hydrogen paper ("Towards observing interstitial hydrogen…"), not paper 5.
- Nature Portfolio post 3mzly5btwka2v (2026-11-05T23:05:01.538Z, smartwatch, go.nature.com/482Fh7f → rdcu.be/rZdgik1eKFMa) — link target returns HTTP 202 with AWS WAF challenge and empty body, unresolvable from this VM, so NOT counted despite likely being paper 1.

## Mastodon — 0 verified

Method: unauthenticated `api/v2/search` returns empty arrays even for "Nature" on ~20 instances tested (mastodon.social, fediscience.org, scicomm.xyz, scholar.social, mastodon.online, mstdn.social, universeodon.com, mastodon.world, mastodonapp.uk, social.vivaldi.net, mastodon.nl, mastodon.green, ecoevo.social, biologists.social, mathstodon.xyz, qoto.org, toot.io, mas.to 403, sciencemastodon.com / mastodon.technology connection closed) — search requires auth. Discovery only via web-search indexing. `site:mastodon.social` DOI searches returned no results for any of the 10 DOIs; `site:` searches on fediscience.org / scicomm.xyz / scholar.social / hachyderm.io / mastodon.online / mstdn.social also nothing (fediscience hits were unrelated profile RSS feeds). `site:mastodon.social AutoDNA` no results. Final close-out search `"10.1038/s41586-026-11228-6" mastodon OR fediverse` returned only unrelated academic papers about Mastodon itself. Note: generic "mastodon" keyword searches are now polluted by the metal band Mastodon's new album *Marrow Deep*.

**Unverifiable channel, in part:** no candidate posts were found at all, and the platform's unauthenticated search is non-functional from this VM, so absence of hits cannot be proven exhaustively — but every indexed search tried returned zero candidates.

## Reddit — 0 verified

Method: `old.reddit.com/search.json` and `www.reddit.com/search.json` both return **403 Blocked** from this VM. Web searches (`site:reddit.com` DOI, r/science, title queries) returned no Reddit posts for any of the 10 papers.

**Unverifiable channel:** Reddit's search API is 403-blocked from this VM and no indexed Reddit posts surfaced in web search; no candidate posts found to verify.

## X — 0 verified

Method: web searches for the DOIs/titles on X returned no verifiable x.com posts. X post pages are login-walled, and direct `x.com` fetch is blocked by policy from this VM.

One lead, NOT counted: TwStalker mirror showed a retweet by @FridaRomayHgo of an original AutoDNA tweet by @Junioryu136689 ("BioTender") — text: "A new milestone for AI-driven science. Published in Nature, AutoDNA introduces an AI-native experimental laboratory… Paper: doi.org/10.1038/s41586… #AIforScience #AIforBiology #AutonomousLab #Nature". The original tweet's status URL and timestamp could not be obtained: TwStalker and Instalker profile pages for @Junioryu136689 expose only the ~20–25 most recent tweets (Nov 12–16), the AutoDNA tweet (~Nov 4–5) is not among them, and `browser.find` for "AutoDNA" on both mirror pages returned nothing; direct curl to twstalker.com failed ("Remote end closed connection"). Without a post URL and timestamp the mention cannot be verified in-window, so X = 0.

**Unverifiable channel:** X is login-walled and policy-blocked from this VM; the single mirror lead could not be resolved to a verifiable post URL/timestamp.

## Validation

All 29 files (`youtube_01`–`youtube_21`, `bluesky_01`–`bluesky_08`) parse as JSON, carry exactly the 9 required fields, have unique URLs, and `published_time` ends in `Z`. Checked 2026-11-16 ~14:00 UTC.

## Honest gaps

- **X: 0 verified** — the channel most likely to hold mentions of these papers is the one least verifiable from this VM (login wall + policy block + mirrors exposing only recent tweets).
- **Papers 5 and 9: 0 verified mentions on every channel searched** — no YouTube video, Bluesky post, Mastodon post, Reddit post, or X post naming either paper was found.
- **Mastodon / Reddit: 0 verified** — both limited by blocked/unauthenticated search, not necessarily by absence of posts; web-index coverage is the only discovery route and it returned nothing.
- Papers 4 and 7 have only 1–2 verified mentions each; paper 3 (AutoDNA) dominates with 9.
