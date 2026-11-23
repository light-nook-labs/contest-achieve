#!/usr/bin/env python3
"""从 contests.json 读赛事配置，调用征文 API，归一化落 roster.jsonl + meta.json。

用法：
  python tools/harvest.py --all
  python tools/harvest.py --tags 793 794
  python tools/harvest.py --tags 793 --size 500 --delay 0.6

设计：
- contest_track_id 为主键，URL 模板从 contests.json 读（改 URL 只改注册表）。
- 不依赖 HTTP 状态码判活：必须拿到 novels 数组且记录字段合法才算成功。
- 分页从 page_start 起，空页或连续失败即停；降 size 重试（500→200→20→1）。
- 断点续采：已存在的 data/<contest_track_id>/roster.jsonl 会读取已抓 nid，跳过重复。
"""
import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTESTS = os.path.join(ROOT, "contests.json")
DATA = os.path.join(ROOT, "data")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
REFERER = "https://pages.sfacg.com/h5/act/zw20260504/pc"
COVER_PREFIX = "https://rs.sfacg.com/web/novel/images/NovelCover/Big/"
TZ = timezone(timedelta(hours=8))


def now():
    return datetime.now(TZ).isoformat(timespec="seconds")


def normalize(rec, endpoint):
    """新旧端点统一到 6 字段 schema；返回 None 表示记录非法。"""
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


def fetch_page(session, url_tpl, tag, endpoint, page, size):
    """返回 (records, total_page, ok)。不靠 status 判活。"""
    url = url_tpl.format(contest_track_id=tag, page=page, size=size)
    try:
        r = session.get(url, timeout=30)
        d = r.json()
    except Exception:
        return None, None, False
    if endpoint == "modern":
        data = d.get("data") or {}
        novels = data.get("novels")
        total = data.get("totalPage")
    else:
        novels = d.get("novels")
        total = d.get("totalPage")
    if not isinstance(novels, list):
        return None, None, False
    return novels, total, True


def load_existing(path):
    if not os.path.exists(path):
        return set(), 0
    seen = set()
    n = 0
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


def harvest_tag(cfg, size, delay):
    tag = cfg["contest_track_id"]
    d = os.path.join(DATA, str(tag))
    os.makedirs(d, exist_ok=True)
    roster = os.path.join(d, "roster.jsonl")
    meta_path = os.path.join(d, "meta.json")
    seen, existing_lines = load_existing(roster)

    session = requests.Session()
    session.headers.update({"user-agent": UA, "referer": REFERER})

    total_page = None
    pages = []
    added = 0
    page = int(cfg.get("page_start", 0))
    size_sequence = [size, 200, 20, 1]
    max_page = 5000

    while page < max_page:
        got = None
        for s in size_sequence:
            if s > size:
                continue
            novels, total, ok = fetch_page(session, cfg["url_template"], tag, cfg["api_generation"], page, s)
            if ok:
                got = (novels, total)
                if total is not None:
                    total_page = total
                break
            time.sleep(delay)
        if got is None or not got[0]:
            break
        novels = got[0]
        batch = []
        for rec in novels:
            norm = normalize(rec, cfg["api_generation"])
            if norm and norm["nid"] not in seen:
                seen.add(norm["nid"])
                batch.append(norm)
        if batch:
            with open(roster, "a", encoding="utf-8") as f:
                for row in batch:
                    f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            added += len(batch)
        pages.append(page)
        if total_page is not None and page >= total_page - 1:
            break
        page += 1
        time.sleep(delay)

    sha = ""
    if os.path.exists(roster):
        h = hashlib.sha256()
        with open(roster, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        sha = h.hexdigest()

    snap = {
        "captured_at": now(), "total_pages": total_page, "fetched_pages": pages,
        "novel_count": existing_lines + added, "sha256": sha,
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
    meta["snapshots"].append(snap)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return len(seen), added, pages, total_page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="采集全部赛事")
    ap.add_argument("--tags", nargs="+", type=int, help="指定赛道 ID（contest_track_id）")
    ap.add_argument("--size", type=int, default=500, help="每页条数（旧端点自动限 200）")
    ap.add_argument("--delay", type=float, default=0.6, help="请求间隔秒")
    args = ap.parse_args()

    cfgs = json.load(open(CONTESTS, encoding="utf-8"))
    if args.all:
        selected = cfgs
    elif args.tags:
        want = set(args.tags)
        selected = [c for c in cfgs if c["contest_track_id"] in want]
        missing = want - {c["contest_track_id"] for c in selected}
        if missing:
            print("未在 contests.json 找到赛道:", sorted(missing), file=sys.stderr)
    else:
        ap.error("需指定 --all 或 --tags")

    for cfg in selected:
        tag = cfg["contest_track_id"]
        size = min(args.size, 200) if cfg["api_generation"] == "legacy" else args.size
        t0 = time.time()
        try:
            total, added, pages, tp = harvest_tag(cfg, size, args.delay)
            print(f"tag {tag:4} {cfg['contest_name']:24} 共 {total:6} 本 新增 {added:5} 页 {len(pages):3}/{tp} 用时 {time.time()-t0:.1f}s", flush=True)
        except Exception as e:
            print(f"tag {tag:4} {cfg['contest_name']:24} 失败: {e}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
