#!/usr/bin/env python3
"""一次性清理：删除所有赛道中未核实的 `待逐档标定` 获奖记录。

依据：用户确认这些净名单迁入的待标定条目不可靠，删除。
只删除同时满足 award == "待逐档标定" 且 verified == false 的记录；
任何已核实记录或其他奖项一律不动。幂等：无匹配时跳过。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

total_removed = 0
for name in sorted(os.listdir(DATA)):
    path = os.path.join(DATA, name, "awards.jsonl")
    if not os.path.exists(path):
        continue
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]

    kept = [
        r for r in rows
        if not (r.get("award") == "待逐档标定" and r.get("verified") is False)
    ]
    removed = len(rows) - len(kept)
    if removed:
        with open(path, "w", encoding="utf-8") as f:
            for r in kept:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        print(f"赛道 {name}: 删除 {removed} 条，保留 {len(kept)} 条")
        total_removed += removed

print(f"合计删除 {total_removed} 条未核实待标定记录")
