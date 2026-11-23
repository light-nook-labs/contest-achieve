#!/usr/bin/env python3
"""一次性清理：删除十三征长篇（赛道 752）中未核实的待标定记录。

依据：用户提供并确认 https://pages.sfacg.com/h5/act/zw20250504/YiEoewNrQpersdQerQnWin
是十三征**唯一**的获奖公示页面。该页公示的 25 部作品已由 import_awards_13th.py 标定；
752 中其余 431 条 `待逐档标定` + `verified=false` 的记录并非真实获奖，删除。

只删除同时满足：赛道 752、award == "待逐档标定"、verified == false 的记录。
已核实记录（verified=true）与其他赛道一律不动。幂等：无匹配时直接跳过。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "752", "awards.jsonl")

with open(PATH, encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]

kept = [
    r for r in rows
    if not (r.get("award") == "待逐档标定" and r.get("verified") is False)
]
removed = len(rows) - len(kept)

if removed:
    with open(PATH, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")

print(f"赛道 752: 删除 {removed} 条未核实待标定记录，保留 {len(kept)} 条已核实获奖")
