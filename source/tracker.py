#!/usr/bin/env python3
"""Science Spread Tracer -- Elgora bounty #9.

Tracks verified public mentions of ten Nature / Science Advances papers
across eight channels (x, bluesky, mastodon, reddit, hackernews,
wikipedia, youtube, news_blogs) inside a fixed date window, and produces
data/mentions.csv + data/first_mentions.csv.

Two modes (see source/README.md):

  collect   fetch public sources, save raw evidence to evidence/,
            then build both CSVs from that evidence.
  replay    rebuild both CSVs from the supplied evidence/ only.
            No network access, no credentials, no reading of the
            submitted CSVs, no hard-coded rows. Rows are derived
            from evidence content using the paper/channel
            configuration, so editing the config changes the output
            (criterion 7).

Python 3.10+ standard library only. No third-party dependencies.
"""

import argparse
import csv
import difflib
import hashlib
import html as htmlmod
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

UA = "ScienceSpreadTracer/1.0 (Elgora bounty #9; +https://elgora.ai)"
WINDOW_START = "2026-10-30T00:00:00Z"
WINDOW_END = "2026-11-20T23:59:00Z"

MENTION_COLUMNS = [
    "paper_number", "channel", "url", "archive_url",
    "author_handle", "timestamp_utc", "captured_text", "engagement",
]
FIRST_COLUMNS = ["paper_number", "channel", "first_timestamp_utc", "url"]

CHANNELS = [
    "x", "bluesky", "mastodon", "reddit",
    "hackernews", "wikipedia", "youtube", "news_blogs",
]

# Publishers / indexes whose pages are never mentions (bounty spec).
EXCLUDED_HOSTS = (
    "nature.com", "science.org", "pubmed.ncbi.nlm.nih.gov",
    "europepmc.org", "scholar.google.", "semanticscholar.org",
    "researchgate.net", "crossref.org", "altmetric.com",
)


# ---------------------------------------------------------------- config

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    papers = []
    for p in cfg["papers"]:
        papers.append({
            "number": int(p["number"]),
            "title": p["title"],
            "doi": p["doi"].lower(),
            "journal": p.get("journal", ""),
        })
    win = cfg.get("window", {})
    start = win.get("start_utc", WINDOW_START)
    end = win.get("end_utc", WINDOW_END)
    enabled = cfg.get("channels", {})
    enabled = {c: bool(enabled.get(c, True)) for c in CHANNELS}
    return {
        "papers": papers,
        "window_start": start,
        "window_end": end,
        "channels": enabled,
        "news_seed_urls": cfg.get("news_seed_urls", []),
    }


def norm_text(s):
    """Lowercase + collapse whitespace, for case-insensitive matching."""
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def doi_suffix(doi):
    return doi.split("/", 1)[1] if "/" in doi else doi


def refers_to_paper(text, urls, paper):
    """True when text/urls refer to the paper (bounty rule).

    Matches when the text contains the DOI, a link that resolves to the
    paper (doi.org, journal site, PubMed), or the paper's full title,
    compared case-insensitively.
    """
    t = norm_text(text)
    doi = paper["doi"]
    if doi in t:
        return True
    title = norm_text(paper["title"])
    if title and title in t:
        return True
    # A bare journal/DOI link inside the text itself also resolves to
    # the paper (e.g. "nature.com/articles/s41586-026-11336-3").
    suffix = doi_suffix(doi)
    if ("nature.com/articles/" + suffix) in t:
        return True
    if ("science.org/doi/" + suffix) in t:
        return True
    if ("doi.org/" + doi) in t:
        return True
    for u in urls or []:
        ul = (u or "").lower()
        if doi in ul:
            return True
        if "doi.org/" + doi in ul:
            return True
        if doi_suffix(doi) in ul and (
            "nature.com/articles/" in ul or "science.org/doi/" in ul
            or "pubmed.ncbi.nlm.nih.gov" in ul
        ):
            return True
    return False


# ---------------------------------------------------------------- time

def parse_ts(value):
    """Parse an ISO-8601 timestamp to an aware UTC datetime.

    Date-only -> 00:00:00 UTC. Naive -> read as UTC. Returns None when
    the value cannot be parsed.
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        s += "T00:00:00Z"
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def fmt_ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def in_window(dt, cfg):
    start = parse_ts(cfg["window_start"])
    end = parse_ts(cfg["window_end"])
    return start <= dt <= end


# ---------------------------------------------------------------- text

# The bounty excludes the papers' own publishers/journals (and research
# indexes) as mention sources "on any channel": a post by the publisher
# itself (e.g. Nature's own Bluesky account) is the paper announcing
# itself, not the paper spreading. Author handles/names that identify
# the publisher are therefore skipped in every extractor.
PUBLISHER_AUTHORS = {
    "nature.com", "springernature.com", "nature", "nature portfolio",
    "science.org", "science", "science magazine", "science advances",
}


def is_publisher_author(author):
    if not author:
        return False
    h = str(author).strip().lower().lstrip("@")
    h = h.split("/")[0]
    return h in PUBLISHER_AUTHORS


def strip_html(s):
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = htmlmod.unescape(s)
    return re.sub(r"[ \t\r\f\v]+", " ", s).strip()


def snippet_around(text, paper, limit=2000):
    """Up to `limit` chars of text centred on the first paper reference.

    Falls back to the start of the text when no reference is found.
    Tries to cut on sentence boundaries.
    """
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if len(text) <= limit:
        return text
    low = text.lower()
    idx = -1
    for needle in (paper["doi"], norm_text(paper["title"])[:60]):
        i = low.find(needle)
        if i != -1:
            idx = i
            break
    if idx == -1:
        idx = 0
    start = max(0, idx - limit // 4)
    end = min(len(text), start + limit)
    chunk = text[start:end]
    # Trim to sentence boundaries where possible.
    if start > 0:
        m = re.search(r"[.!?]\s", chunk)
        if m:
            chunk = chunk[m.end():]
    if end < len(text):
        m = list(re.finditer(r"[.!?](\s|$)", chunk))
        if m:
            chunk = chunk[: m[-1].start() + 1]
    return chunk.strip()[:limit]


def canonical_url(url):
    """Normalise a URL for de-duplication (strip fragment, trailing /)."""
    if not url:
        return ""
    u = url.strip()
    u = u.split("#", 1)[0]
    if len(u) > 1 and u.endswith("/"):
        u = u.rstrip("/")
    return u


def host_of(url):
    try:
        return urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return ""


def is_excluded_host(url):
    h = host_of(url)
    return any(h == e or h.endswith("." + e) for e in EXCLUDED_HOSTS)


# ---------------------------------------------------------------- csv io

def write_mentions_csv(mentions, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MENTION_COLUMNS,
                           lineterminator="\n")
        w.writeheader()
        for m in mentions:
            w.writerow({c: m.get(c, "") for c in MENTION_COLUMNS})


def write_first_csv(mentions, path):
    groups = {}
    for m in mentions:
        key = (m["paper_number"], m["channel"])
        groups.setdefault(key, []).append(m)
    rows = []
    for (num, ch), ms in sorted(groups.items()):
        ms_sorted = sorted(ms, key=lambda r: (r["timestamp_utc"], r["url"]))
        first = ms_sorted[0]
        rows.append({
            "paper_number": num,
            "channel": ch,
            "first_timestamp_utc": first["timestamp_utc"],
            "url": first["url"],
        })
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIRST_COLUMNS,
                           lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return rows


def read_csv_rows(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------- manifest

def build_manifest(evidence_dir):
    """evidence/manifest.json: file -> source URL, retrieval time, SHA-256."""
    entries = []
    for name in sorted(os.listdir(evidence_dir)):
        if not name.endswith(".json") or name == "manifest.json":
            continue
        path = os.path.join(evidence_dir, name)
        with open(path, "rb") as f:
            raw = f.read()
        try:
            doc = json.loads(raw.decode("utf-8"))
        except Exception:
            doc = {}
        entries.append({
            "file": name,
            "channel": doc.get("channel", ""),
            "source_url": doc.get("source_url", ""),
            "retrieved_utc": doc.get("retrieved_utc", ""),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })
    out = os.path.join(evidence_dir, "manifest.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"evidence": entries}, f, indent=2)
        f.write("\n")
    return entries


# ---------------------------------------------------------------- extractors
# Each extractor takes one evidence document + config and returns a list
# of mention dicts. Evidence files never carry paper numbers: the paper
# is matched here, from the config, so editing the config changes the
# output (acceptance criterion 7).


def _match_records(text, urls, cfg):
    """All config papers (by number) the record refers to.

    One record (e.g. a roundup video or article) may legitimately
    mention several papers; each is a separate verified mention.
    """
    return [paper for paper in sorted(cfg["papers"], key=lambda p: p["number"])
            if refers_to_paper(text, urls, paper)]


def _row(paper, channel, url, author, dt, captured, engagement):
    return {
        "paper_number": paper["number"],
        "channel": channel,
        "url": canonical_url(url),
        "archive_url": "",
        "author_handle": author or "",
        "timestamp_utc": fmt_ts(dt),
        "captured_text": (captured or "")[:2000],
        "engagement": "" if engagement is None else str(engagement),
    }


def extract_hackernews(doc, cfg):
    out = []
    for hit in doc.get("records", []):
        if is_publisher_author(hit.get("author")):
            continue
        title = hit.get("title") or ""
        text = strip_html(hit.get("text") or hit.get("comment_text") or "")
        body = (title + " " + text).strip()
        story_url = hit.get("url") or ""
        dt = parse_ts(hit.get("created_at"))
        if dt is None or not in_window(dt, cfg):
            continue
        papers = _match_records(body, [story_url], cfg)
        if not papers:
            continue
        item_url = "https://news.ycombinator.com/item?id=%s" % hit.get("objectID")
        for paper in papers:
            out.append(_row(paper, "hackernews", item_url,
                            hit.get("author"), dt,
                            snippet_around(body, paper),
                            hit.get("points")))
    return out


def extract_bluesky(doc, cfg):
    # Two evidence shapes: (a) searchPosts API records, (b) a single
    # publicly fetched post page (web-search discovery, used because
    # public.api.bsky.app is 403-blocked from this environment).
    if "records" in doc:
        return _extract_bluesky_api(doc, cfg)
    if doc.get("url"):
        return extract_page(doc, cfg)
    return []


def _extract_bluesky_api(doc, cfg):
    out = []
    for post in doc.get("records", []):
        rec = post.get("record", {}) or {}
        text = rec.get("text", "") or ""
        urls = []
        embed = post.get("embed", {}) or {}
        ext = embed.get("external", {}) or {}
        if ext.get("uri"):
            urls.append(ext["uri"])
        author = (post.get("author", {}) or {}).get("handle", "")
        if is_publisher_author(author):
            continue
        dt = parse_ts(rec.get("createdAt"))
        if dt is None or not in_window(dt, cfg):
            continue
        papers = _match_records(text, urls, cfg)
        if not papers:
            continue
        uri = post.get("uri", "")
        rkey = uri.rsplit("/", 1)[-1] if uri else ""
        if not author or not rkey:
            continue
        url = "https://bsky.app/profile/%s/post/%s" % (author, rkey)
        for paper in papers:
            out.append(_row(paper, "bluesky", url, author, dt,
                            snippet_around(text, paper),
                            post.get("likeCount")))
    return out


def extract_reddit(doc, cfg):
    # Two evidence shapes: (a) search JSON children, (b) a single
    # publicly fetched post/comment page (web-search discovery, used
    # because reddit search JSON is 403-blocked from this environment).
    if "records" in doc:
        return _extract_reddit_api(doc, cfg)
    if doc.get("url"):
        return extract_page(doc, cfg)
    return []


def _extract_reddit_api(doc, cfg):
    out = []
    for child in doc.get("records", []):
        d = child.get("data", child) if isinstance(child, dict) else {}
        if is_publisher_author(d.get("author")):
            continue
        title = d.get("title") or ""
        body = d.get("selftext") or d.get("body") or ""
        text = (title + " " + strip_html(body)).strip()
        urls = [u for u in (d.get("url"),) if u]
        created = d.get("created_utc")
        dt = None
        if created:
            try:
                dt = datetime.fromtimestamp(float(created), tz=timezone.utc)
            except (TypeError, ValueError):
                dt = None
        if dt is None:
            dt = parse_ts(d.get("created"))
        if dt is None or not in_window(dt, cfg):
            continue
        papers = _match_records(text, urls, cfg)
        if not papers:
            continue
        permalink = d.get("permalink") or ""
        if not permalink:
            continue
        url = "https://www.reddit.com" + permalink
        for paper in papers:
            out.append(_row(paper, "reddit", url,
                            d.get("author"), dt,
                            snippet_around(text, paper),
                            d.get("score")))
    return out


def extract_wikipedia(doc, cfg):
    out = []
    for rec in doc.get("records", []):
        added = rec.get("added_text") or ""
        dt = parse_ts(rec.get("timestamp"))
        if dt is None or not in_window(dt, cfg):
            continue
        papers = _match_records(added, [], cfg)
        if not papers:
            continue
        url = rec.get("revision_url") or ""
        if not url:
            continue
        for paper in papers:
            out.append(_row(paper, "wikipedia", url,
                            rec.get("author"), dt,
                            snippet_around(added, paper), ""))
    return out


def extract_page(doc, cfg):
    """Generic page-extract evidence: news_blogs, mastodon, youtube, x.

    Document fields: url, headline (or title), published_time,
    author, publication, text, links (optional list of URLs in text).
    """
    channel = doc.get("channel", "")
    url = doc.get("url") or ""
    if not url or is_excluded_host(url):
        return []
    author = doc.get("author") or ""
    if is_publisher_author(author):
        return []
    text = doc.get("text") or ""
    headline = doc.get("headline") or doc.get("title") or ""
    urls = list(doc.get("links") or [])
    if url not in urls:
        urls.append(url)
    # Links are part of the page text for matching: a mention may refer
    # to the paper only through a link in the description/article, and
    # the captured snippet must then contain that link.
    full = (headline + "\n" + text + "\n" + "\n".join(urls)).strip()
    dt = parse_ts(doc.get("published_time"))
    if dt is None or not in_window(dt, cfg):
        return []
    papers = _match_records(full, urls, cfg)
    return [_row(paper, channel, url, doc.get("author"), dt,
                 snippet_around(full, paper),
                 doc.get("engagement"))
            for paper in papers]


EXTRACTORS = {
    "hackernews": extract_hackernews,
    "bluesky": extract_bluesky,
    "reddit": extract_reddit,
    "wikipedia": extract_wikipedia,
    "news_blogs": extract_page,
    "mastodon": extract_page,
    "youtube": extract_page,
    "x": extract_page,
}


def build_mentions(evidence_dir, cfg):
    """Derive all mentions from evidence files (no network)."""
    mentions = []
    seen_urls = set()
    for name in sorted(os.listdir(evidence_dir)):
        if not name.endswith(".json") or name == "manifest.json":
            continue
        path = os.path.join(evidence_dir, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                doc = json.load(f)
        except Exception as exc:
            print("WARN: skipping unreadable evidence %s: %s" % (name, exc),
                  file=sys.stderr)
            continue
        channel = doc.get("channel", "")
        if channel not in EXTRACTORS:
            print("WARN: unknown channel in %s: %r" % (name, channel),
                  file=sys.stderr)
            continue
        if not cfg["channels"].get(channel, True):
            continue
        try:
            rows = EXTRACTORS[channel](doc, cfg)
        except Exception as exc:
            print("WARN: extractor failed for %s: %s" % (name, exc),
                  file=sys.stderr)
            continue
        for m in rows:
            # A mention is (paper, url): one record may mention several
            # papers (e.g. a roundup video), each is a separate mention.
            key = (m["paper_number"], canonical_url(m["url"]))
            if key in seen_urls:
                continue
            seen_urls.add(key)
            mentions.append(m)
    mentions.sort(key=lambda m: (m["paper_number"], m["channel"],
                                 m["timestamp_utc"], m["url"]))
    return mentions


def write_outputs(mentions, out_dir):
    write_mentions_csv(mentions,
                       os.path.join(out_dir, "mentions.csv"))
    first = write_first_csv(mentions,
                            os.path.join(out_dir, "first_mentions.csv"))
    return first


# ---------------------------------------------------------------- fetchers
# Collection only. Replay never calls these.

STOPWORDS = set(
    "a an the of on in for and or to with from by at as is are was were "
    "be been into over under after before between new".split()
)


def http_get(url, timeout=30, retries=2):
    """Fetch a URL. Uses curl: plain urllib hits IncompleteRead /
    connection-closed errors through this VM's egress proxy, while
    curl succeeds reliably (same failure seen with the make.fun API)."""
    import subprocess
    last = None
    for attempt in range(retries + 1):
        try:
            r = subprocess.run(
                ["curl", "-sS", "-A", UA, "--max-time", str(timeout), url],
                capture_output=True, timeout=timeout + 10)
            if r.returncode == 0:
                return r.stdout
            last = RuntimeError("curl exit %d: %s" % (
                r.returncode,
                r.stderr.decode("utf-8", "replace")[:300]))
        except Exception as exc:
            last = exc
        if attempt < retries:
            time.sleep(2 * (attempt + 1))
    raise last


def http_get_json(url, timeout=30, retries=2):
    return json.loads(http_get(url, timeout, retries).decode("utf-8"))


def save_evidence(evidence_dir, name, doc):
    os.makedirs(evidence_dir, exist_ok=True)
    path = os.path.join(evidence_dir, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return path


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def keywords(title, n=5):
    words = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", title)
    seen, out = set(), []
    for w in words:
        lw = w.lower()
        if lw in STOPWORDS or lw in seen:
            continue
        seen.add(lw)
        out.append(w)
        if len(out) >= n:
            break
    return " ".join(out)


def fetch_hackernews(cfg, evidence_dir):
    start_i = int(parse_ts(cfg["window_start"]).timestamp())
    end_i = int(parse_ts(cfg["window_end"]).timestamp())
    for paper in cfg["papers"]:
        for kind, q in (("doi", paper["doi"]),
                        ("kw", keywords(paper["title"]))):
            url = ("https://hn.algolia.com/api/v1/search?query=%s"
                   "&tags=(story,comment)&hitsPerPage=1000"
                   "&numericFilters=%s"
                   % (urllib.parse.quote(q),
                      urllib.parse.quote(
                          "created_at_i>=%d,created_at_i<=%d"
                          % (start_i, end_i))))
            try:
                data = http_get_json(url)
            except Exception as exc:
                print("WARN: HN query failed %r: %s" % (q, exc),
                      file=sys.stderr)
                continue
            save_evidence(evidence_dir,
                          "hackernews_p%d_%s.json" % (paper["number"], kind),
                          {"channel": "hackernews", "source_url": url,
                           "retrieved_utc": now_iso(), "query": q,
                           "records": data.get("hits", [])})
            time.sleep(0.5)


def fetch_bluesky(cfg, evidence_dir):
    for paper in cfg["papers"]:
        for kind, q in (("doi", paper["doi"]),
                        ("kw", keywords(paper["title"]))):
            posts, cursor, pages = [], None, 0
            while pages < 3:
                url = ("https://public.api.bsky.app/xrpc/"
                       "app.bsky.feed.searchPosts?q=%s&limit=100&sort=latest"
                       % urllib.parse.quote(q))
                if cursor:
                    url += "&cursor=" + urllib.parse.quote(cursor)
                try:
                    data = http_get_json(url)
                except Exception as exc:
                    print("WARN: Bluesky query failed %r: %s" % (q, exc),
                          file=sys.stderr)
                    break
                posts.extend(data.get("posts", []))
                cursor = data.get("cursor")
                pages += 1
                if not cursor:
                    break
                time.sleep(0.5)
            save_evidence(evidence_dir,
                          "bluesky_p%d_%s.json" % (paper["number"], kind),
                          {"channel": "bluesky", "source_url": url,
                           "retrieved_utc": now_iso(), "query": q,
                           "records": posts})
            time.sleep(0.5)


def fetch_wikipedia(cfg, evidence_dir):
    api = "https://en.wikipedia.org/w/api.php"
    start = cfg["window_start"].replace("Z", "")
    end = cfg["window_end"].replace("Z", "")
    for paper in cfg["papers"]:
        search_url = (api + "?action=query&list=search&srsearch=%s"
                      "&srprop=snippet&srlimit=20&format=json"
                      % urllib.parse.quote('"%s"' % paper["doi"]))
        try:
            found = http_get_json(search_url)
        except Exception as exc:
            print("WARN: Wikipedia search failed p%d: %s"
                  % (paper["number"], exc), file=sys.stderr)
            continue
        titles = [r["title"] for r in
                  found.get("query", {}).get("search", [])]
        records = []
        for title in titles:
            rev_url = (api + "?action=query&prop=revisions&titles=%s"
                       "&rvprop=ids|timestamp|user|content&rvslots=main"
                       "&rvdir=newer&rvstart=%s&rvend=%s&rvlimit=50"
                       "&format=json&formatversion=2"
                       % (urllib.parse.quote(title),
                          urllib.parse.quote(start),
                          urllib.parse.quote(end)))
            try:
                data = http_get_json(rev_url, timeout=60)
            except Exception as exc:
                print("WARN: Wikipedia revisions failed %r: %s"
                      % (title, exc), file=sys.stderr)
                continue
            pages = data.get("query", {}).get("pages", [])
            if not pages:
                continue
            revs = pages[0].get("revisions", [])
            prev_text = ""
            for rev in revs:
                content = ""
                slots = rev.get("slots", {})
                if "main" in slots:
                    content = slots["main"].get("content", "") or ""
                if prev_text:
                    diff = difflib.unified_diff(
                        prev_text.splitlines(), content.splitlines(),
                        lineterm="")
                    added = [ln[1:] for ln in diff
                             if ln.startswith("+") and not ln.startswith("+++")]
                    added_text = "\n".join(added)
                    if paper in _match_records(added_text, [], cfg):
                        records.append({
                            "page_title": title,
                            "revid": rev.get("revid"),
                            "timestamp": rev.get("timestamp"),
                            "author": rev.get("user"),
                            "added_text": added_text[:4000],
                            "revision_url": (
                                "https://en.wikipedia.org/w/index.php?title=%s"
                                "&oldid=%s" % (urllib.parse.quote(
                                    title.replace(" ", "_")),
                                    rev.get("revid"))),
                        })
                prev_text = content
            time.sleep(0.5)
        save_evidence(evidence_dir,
                      "wikipedia_p%d.json" % paper["number"],
                      {"channel": "wikipedia",
                       "source_url": search_url,
                       "retrieved_utc": now_iso(),
                       "query": paper["doi"], "records": records})


def fetch_reddit(cfg, evidence_dir):
    for paper in cfg["papers"]:
        for kind, q in (("doi", paper["doi"]),
                        ("kw", keywords(paper["title"]))):
            url = ("https://old.reddit.com/search.json?q=%s"
                   "&sort=new&limit=100&restrict_sr=0"
                   % urllib.parse.quote(q))
            try:
                data = http_get_json(url, timeout=30, retries=2)
            except Exception as exc:
                print("WARN: Reddit query failed %r: %s" % (q, exc),
                      file=sys.stderr)
                continue
            children = data.get("data", {}).get("children", [])
            save_evidence(evidence_dir,
                          "reddit_p%d_%s.json" % (paper["number"], kind),
                          {"channel": "reddit", "source_url": url,
                           "retrieved_utc": now_iso(), "query": q,
                           "records": children})
            time.sleep(1.0)


def extract_article(html, url):
    """Best-effort article extraction from raw HTML (no dependencies)."""
    def meta(prop):
        m = re.search(
            r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']+)'
            % re.escape(prop), html, re.I)
        if m:
            return htmlmod.unescape(m.group(1)).strip()
        m = re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']%s["\']'
            % re.escape(prop), html, re.I)
        return htmlmod.unescape(m.group(1)).strip() if m else ""

    title = meta("og:title")
    if not title:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        title = strip_html(m.group(1)) if m else ""
    published = (meta("article:published_time")
                 or meta("datePublished") or meta("publish-date") or "")
    if not published:
        m = re.search(r'<time[^>]+datetime=["\']([^"\']+)', html, re.I)
        published = m.group(1) if m else ""
    if not published:
        m = re.search(
            r'"datePublished"\s*:\s*"([^"]+)"', html)
        published = m.group(1) if m else ""
    author = meta("article:author") or meta("author") or ""
    if not author:
        m = re.search(r'"author"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"', html)
        author = m.group(1) if m else ""
    publication = meta("og:site_name") or ""
    body = html
    m = re.search(r"<article[^>]*>(.*?)</article>", html, re.I | re.S)
    if m:
        body = m.group(1)
    else:
        m = re.search(r"<body[^>]*>(.*?)</body>", html, re.I | re.S)
        body = m.group(1) if m else html
    for tag in ("script", "style", "nav", "header", "footer", "aside"):
        body = re.sub(r"<%s\b.*?</%s>" % (tag, tag), " ", body,
                      flags=re.I | re.S)
    text = strip_html(body)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return {
        "channel": "news_blogs", "url": url,
        "retrieved_utc": now_iso(), "headline": title,
        "published_time": published, "author": author,
        "publication": publication, "text": text[:60000],
    }


def fetch_news(cfg, evidence_dir):
    for i, url in enumerate(cfg["news_seed_urls"]):
        try:
            raw = http_get(url, timeout=30, retries=1)
        except Exception as exc:
            print("WARN: news fetch failed %s: %s" % (url, exc),
                  file=sys.stderr)
            continue
        doc = extract_article(raw.decode("utf-8", "replace"), url)
        slug = re.sub(r"[^A-Za-z0-9]+", "_",
                      urllib.parse.urlparse(url).netloc + url)[:80]
        save_evidence(evidence_dir, "news_%02d_%s.json" % (i, slug), doc)
        time.sleep(1.0)


# ---------------------------------------------------------------- cli

def cmd_collect(args):
    cfg = load_config(args.config)
    if cfg["channels"].get("hackernews"):
        fetch_hackernews(cfg, args.evidence_dir)
    if cfg["channels"].get("bluesky"):
        fetch_bluesky(cfg, args.evidence_dir)
    if cfg["channels"].get("wikipedia"):
        fetch_wikipedia(cfg, args.evidence_dir)
    if cfg["channels"].get("reddit"):
        fetch_reddit(cfg, args.evidence_dir)
    if cfg["channels"].get("news_blogs") and cfg["news_seed_urls"]:
        fetch_news(cfg, args.evidence_dir)
    mentions = build_mentions(args.evidence_dir, cfg)
    write_outputs(mentions, args.out_dir)
    build_manifest(args.evidence_dir)
    print_stats(mentions)


def cmd_replay(args):
    cfg = load_config(args.config)
    mentions = build_mentions(args.evidence_dir, cfg)
    write_outputs(mentions, args.out_dir)
    print_stats(mentions)


def print_stats(mentions):
    by_channel, by_paper = {}, {}
    for m in mentions:
        by_channel[m["channel"]] = by_channel.get(m["channel"], 0) + 1
        by_paper[m["paper_number"]] = by_paper.get(m["paper_number"], 0) + 1
    print("mentions: %d" % len(mentions))
    print("channels: %s" % by_channel)
    print("papers: %s" % dict(sorted(by_paper.items())))


def cmd_verify(args):
    import tempfile
    cfg = load_config(args.config)
    with tempfile.TemporaryDirectory() as tmp:
        replayed = build_mentions(args.evidence_dir, cfg)
        write_outputs(replayed, tmp)
        ok = True
        for name in ("mentions.csv", "first_mentions.csv"):
            a = read_csv_rows(os.path.join(args.out_dir, name))
            b = read_csv_rows(os.path.join(tmp, name))
            key = lambda r: tuple(sorted(r.items()))
            same = sorted(map(key, a)) == sorted(map(key, b))
            print("%s: submitted=%d replayed=%d match=%s"
                  % (name, len(a), len(b), same))
            ok = ok and same
        print("VERIFY: %s" % ("OK" if ok else "FAIL"))
        return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("collect", "replay"):
        p = sub.add_parser(name)
        p.add_argument("--config", required=True)
        p.add_argument("--evidence-dir", required=True)
        p.add_argument("--out-dir", required=True)
    p = sub.add_parser("manifest")
    p.add_argument("--evidence-dir", required=True)
    p = sub.add_parser("verify")
    p.add_argument("--config", required=True)
    p.add_argument("--evidence-dir", required=True)
    p.add_argument("--out-dir", required=True)
    args = ap.parse_args(argv)
    if args.cmd == "collect":
        cmd_collect(args)
    elif args.cmd == "replay":
        cmd_replay(args)
    elif args.cmd == "manifest":
        entries = build_manifest(args.evidence_dir)
        print("manifest: %d evidence files" % len(entries))
    elif args.cmd == "verify":
        return cmd_verify(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
