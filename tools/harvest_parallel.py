#!/usr/bin/env python3
"""并行采集 contests.json 中 series=未知 的赛事清单。

与 harvest.py 共用同一 schema（roster 6 字段 + meta snapshots），按 (tag,page) 并发请求，
单赛事内按页序写 roster，支持断点续采（已有 roster 跳过已存在 nid）。
用法：
  uv run python tools/harvest_parallel.py --workers 6
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
import threading
import time
from datetime import datetime, timedelta, timezone

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTESTS = os.path.join(ROOT, "contests.json")
DATA = os.path.join(ROOT, "data")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
REFERER = "https://pages.sfacg.com/h5/act/zw20260504/pc"
COVER_PREFIX = "https://rs.sfacg.com/web/novel/images/NovelCover/Big/"
TZ = timezone(timedelta(hours=8))
WRITE_LOCK = threading.Lock()


def now():
    return datetime.now(TZ).isoformat(timespec="seconds")


def normalize(rec, endpoint):
    if endpoint == "modern":
        gid, title, author = rec.get("novelID"), rec.get("novelName"), rec.get("authorName")
        cid, intro, cover = rec.get("categoryID"), rec.get("intro"), rec.get("cover")
    else:
        gid, title, author = rec.get("NovelID"), rec.get("NovelName"), rec.get("AuthorName")
        cid, intro, cover = rec.get("CategoryID"), rec.get("Intro"), rec.get("Cover")
    if not isinstance(gid, int) or gid <= 0 or not isinstance(title, str) or not title.strip():
        return None
    if isinstance(cover, str) and cover and not cover.startswith("http"):
        cover = COVER_PREFIX + cover
    return {
        "nid": gid,
        "title": title,
        "author": author if isinstance(author, str) else "",
        "form_id": cid if isinstance(cid, int) else 0,
        "intro": intro if isinstance(intro, str) else "",
        "cover": cover if isinstance(cover, str) else "",
    }


def fetch_page(session, cfg, page, size):
    url = cfg["url_template"].format(contest_track_id=cfg["contest_track_id"], page=page, size=size)
    for attempt in range(4):
        try:
            r = session.get(url, timeout=30)
            d = r.json()
            if cfg["api_generation"] == "modern":
                data = d.get("data") or {}
                novels, total = data.get("novels"), data.get("totalPage")
            else:
                novels, total = d.get("novels"), d.get("totalPage")
            if isinstance(novels, list):
                return novels, total
        except Exception:
            pass
        time.sleep(0.4 * (attempt + 1))
    return None, None


def load_existing(path):
    if not os.path.exists(path):
        return set(), 0
    seen, n = set(), 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                seen.add(json.loads(line)["nid"])
                n += 1
            except Exception:
                pass
    return seen, n


def harvest_tag(cfg, size, workers):
    tag = cfg["contest_track_id"]
    d = os.path.join(DATA, str(tag))
    os.makedirs(d, exist_ok=True)
    roster = os.path.join(d, "roster.jsonl")
    meta_path = os.path.join(d, "meta.json")
    seen, existing_lines = load_existing(roster)

    session = requests.Session()
    session.headers.update({"user-agent": UA, "referer": REFERER})
    first, total_page = fetch_page(session, cfg, 0, size)
    if first is None or not first:
        return tag, 0, 0, 0, "empty-first-page"
    if total_page is None:
        total_page = 0
    pages = list(range(1, int(total_page)))
    results = {0: first}
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fetch_page, session, cfg, p, size): p for p in pages}
        for fut in concurrent.futures.as_completed(futs):
            p = futs[fut]
            novels, _ = fut.result()
            if novels is None:
                errors.append(p)
            else:
                results[p] = novels

    # 按页序写入；跳过重复 nid
    added = 0
    with WRITE_LOCK:
        with open(roster, "a", encoding="utf-8") as f:
            for p in range(int(total_page)):
                for rec in results.get(p, []):
                    norm = normalize(rec, cfg["api_generation"])
                    if norm and norm["nid"] not in seen:
                        seen.add(norm["nid"])
                        f.write(json.dumps(norm, ensure_ascii=False, separators=(",", ":")) + "\n")
                        added += 1
        sha = ""
        if os.path.exists(roster):
            h = hashlib.sha256()
            with open(roster, "rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    h.update(chunk)
            sha = h.hexdigest()
        snap = {
            "captured_at": now(), "total_pages": int(total_page),
            "fetched_pages": sorted(results), "novel_count": existing_lines + added, "sha256": sha,
        }
        meta = {
            "contest_track_id": tag,
            "contest_name": cfg["contest_name"],
            "series": cfg["series"],
            "api_generation": cfg["api_generation"],
            "url_template": cfg["url_template"],
            "page_start": cfg.get("page_start", 0),
            "snapshots": [],
        }
        if os.path.exists(meta_path):
            try:
                meta["snapshots"] = json.load(open(meta_path, encoding="utf-8")).get("snapshots", [])
            except Exception:
                pass
        # 已是完整快照则不重复追加
        old = meta["snapshots"][-1] if meta["snapshots"] else {}
        if not (old.get("total_pages") == int(total_page) and added == 0 and old.get("novel_count") == existing_lines):
            meta["snapshots"].append(snap)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
            f.write("\n")
    return tag, len(seen), added, int(total_page), f"errors={len(errors)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6, help="每赛事内并发页数")
    ap.add_argument("--size", type=int, default=200)
    args = ap.parse_args()
    cfgs = json.load(open(CONTESTS, encoding="utf-8"))
    selected = [c for c in cfgs if c["series"] == "未知"]
    t0 = time.time()
    for i, cfg in enumerate(selected, 1):
        try:
            tag, total, added, tp, note = harvest_tag(cfg, args.size, args.workers)
            print(f"[{i}/{len(selected)}] tag {tag:4} 共 {total:6} 新增 {added:6} 页 {tp:4} {note} 用时 {time.time()-t0:.0f}s", flush=True)
        except Exception as e:
            print(f"[{i}/{len(selected)}] tag {cfg['contest_track_id']} 失败: {e}", flush=True)


if __name__ == "__main__":
    main()
