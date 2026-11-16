# Science Spread Tracer

Open-source tracker + verified dataset of mentions of 10 Nature/Science papers across 8 channels. Submission for Elgora bounty #9 ($20 USDC, Base).

## What is this

- `source/tracker.py` — Python 3.12 stdlib-only tracker (`collect` / `replay` / `verify` / `manifest`). No dependencies.
- `data/mentions.csv` — 44 verified mentions (Bluesky 2, news/blogs 19, YouTube 22, X 1).
- `data/first_mentions.csv` — 19 rows, one per paper/channel pair (earliest timestamp).
- `evidence/` — 100 evidence files + `manifest.json` (source URL, retrieval time UTC, SHA-256 per file). Every dataset row traces to a saved evidence file.
- `SUMMARY.md` — build summary, verification evidence, known gaps.
- `report.md` — collection report (per-paper pickup, patterns).

## Papers

10 fixed papers (9× Nature, 4–6 Nov 2026; 1× Science Advances, 30 Oct 2026), window 2026-10-30 → 2026-11-20 23:59 UTC. Full DOI/title list in `source/config.example.json`.

## Verify

```sh
python3 source/tracker.py verify --config source/config.example.json --evidence-dir evidence --out-dir data
# mentions.csv: submitted=44 replayed=44 match=True
# first_mentions.csv: submitted=19 replayed=19 match=True
# VERIFY: OK
```

## License

MIT — see `source/LICENSE`.
