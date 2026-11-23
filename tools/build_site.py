#!/usr/bin/env python3
"""把 data/ 归档导出为前端可 fetch 的 JSON，并复制静态站点壳到 docs/。

输出：
  docs/index.html            赛事索引（静态壳）
  docs/contest.html          赛事详情（静态壳，?contest_track_id=…）
  docs/awards.html           获奖总览（静态壳）
  docs/assets/*              来自 site/assets/（Vue 3 + CSS + app.js）
  docs/data/site.json        构建时间与汇总统计
  docs/data/contests.json    全部赛道元数据 + 计数
  docs/data/roster/<id>.json 已采赛道的清单
  docs/data/awards.json      合并获奖（冗余赛道/赛事/系列字段）

用法：uv run python tools/build_site.py
"""
import json
import os
import shutil
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
TZ = timezone(timedelta(hours=8))


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")


def build_contest_rows(cfgs):
    rows = []
    for cfg in cfgs:
        contest_track_id = cfg["contest_track_id"]
        d = os.path.join(DATA, str(contest_track_id))
        roster = read_jsonl(os.path.join(d, "roster.jsonl"))
        awards = read_jsonl(os.path.join(d, "awards.jsonl"))
        meta_path = os.path.join(d, "meta.json")
        meta = load_json(meta_path) if os.path.exists(meta_path) else {}
        snapshots = meta.get("snapshots") or []
        last = snapshots[-1] if snapshots else {}
        rows.append({
            "contest_track_id": contest_track_id,
            "contest_name": cfg["contest_name"],
            "series": cfg["series"],
            "api_generation": cfg["api_generation"],
            "url_template": cfg["url_template"],
            "activity_url": cfg.get("activity_url", ""),
            "page_start": cfg.get("page_start", 0),
            "roster_count": len(roster),
            "award_count": len(awards),
            "collected": bool(roster),
            "captured_at": last.get("captured_at", ""),
            "total_pages": last.get("total_pages"),
            "fetched_pages": last.get("fetched_pages", []),
            "novel_count": last.get("novel_count", 0),
        })
    return rows


def main():
    if os.path.exists(DOCS):
        shutil.rmtree(DOCS)
    shutil.copytree(SITE, DOCS)
    os.makedirs(os.path.join(DOCS, "data", "roster"), exist_ok=True)

    cfgs = load_json(os.path.join(ROOT, "contests.json"))
    contests = build_contest_rows(cfgs)

    award_rows = []
    for c in contests:
        contest_track_id = c["contest_track_id"]
        d = os.path.join(DATA, str(contest_track_id))
        roster = read_jsonl(os.path.join(d, "roster.jsonl"))
        if roster:
            dump_json(os.path.join(DOCS, "data", "roster", f"{contest_track_id}.json"), roster)
        for award in read_jsonl(os.path.join(d, "awards.jsonl")):
            award_rows.append({
                **award,
                "contest_track_id": contest_track_id,
                "contest_name": c["contest_name"],
                "series": c["series"],
            })

    dump_json(os.path.join(DOCS, "data", "contests.json"), contests)
    dump_json(os.path.join(DOCS, "data", "awards.json"), award_rows)
    dump_json(os.path.join(DOCS, "data", "site.json"), {
        "built_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "contests_total": len(contests),
        "contests_collected": sum(1 for c in contests if c["collected"]),
        "roster_total": sum(c["roster_count"] for c in contests),
        "award_total": len(award_rows),
    })

    print(f"站点已生成到 {DOCS}")
    print(f"  赛道 {len(contests)}（已采 {sum(1 for c in contests if c['collected'])}），"
          f"清单 {sum(c['roster_count'] for c in contests)}，获奖 {len(award_rows)}")


if __name__ == "__main__":
    main()
