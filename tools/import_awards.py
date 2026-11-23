#!/usr/bin/env python3
"""把 analysis/out/contest_awards_normalized.csv 的 911 本净获奖迁入本仓库。

edition -> contest_track_id 映射（挂到该届主赛道；获奖表无赛道字段，统一挂主赛道）：
  十二征→702  十三征→752  七征冬征→692  六征冬征→485  2024春征→699
  2024秋征→725  九征冬征→774  2025春征→746  八征冬征→726
  2025秋征→772  2026春征→789

用法：python tools/import_awards.py <csv路径>
"""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

EDITION_TAG = {
    "十二征": 702, "十三征": 752, "七征冬征": 692, "六征冬征": 485,
    "2024春征": 699, "2024秋征": 725, "九征冬征": 774, "2025春征": 746,
    "八征冬征": 726, "2025秋征": 772, "2026春征": 789,
}


def main():
    if len(sys.argv) < 2:
        sys.exit("用法: python tools/import_awards.py <csv路径>")
    src = sys.argv[1]
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    by_tag = {}
    for r in rows:
        tag = EDITION_TAG.get(r["edition"])
        if tag is None:
            print(f"警告: 未知届 {r['edition']}，跳过 nid {r['nid']}", file=sys.stderr)
            continue
        award = r.get("award") or "待逐档标定"
        by_tag.setdefault(tag, []).append({
            "nid": int(r["nid"]),
            "title": r.get("title", ""),
            "award": award,
            "source": f"{r.get('source_nid','')} 活动页（{r['edition']}）",
            "verified": award != "待逐档标定",
            "verified_at": "" if award == "待逐档标定" else "2026-11-21",
            "note": "",
        })

    total = 0
    for tag, items in sorted(by_tag.items()):
        d = os.path.join(DATA, str(tag))
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "awards.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for row in items:
                f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        print(f"tag {tag:4} 获奖 {len(items):4} 本 -> {path}")
        total += len(items)
    print(f"共迁入 {total} 本到 {len(by_tag)} 个赛事")


if __name__ == "__main__":
    main()
