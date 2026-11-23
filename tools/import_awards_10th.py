#!/usr/bin/env python3
"""导入：十征（2022）官网最终获奖公示（共 34 部）。

来源：https://pages.sfacg.com/h5/act/zw2022/winner.html
分组与奖项名由用户目视确认：
- c1/c2/c3/c4 → 金奖1/银奖3/铜奖5/推荐奖5（475 长篇）
- z1/z2/z3 → 金奖1/银奖1/铜奖3（476 中篇）
- d1/d2/d3 → 金奖1/银奖1/铜奖3（477 短篇）
- xh → 星火奖10（6 属 475、4 属 479，按 roster 赛道拆分）

候选清单见 candidates_10th.py，34 个 nid 已与 roster.jsonl 书名/作者/赛道交叉验证。

幂等：按 (nid, award) 复合键去重，重复执行不产生重复行；已存在记录不回退。
"""
import json
import os

from candidates_10th import CANDIDATES, SOURCE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-11-23"


def roster_index():
    idx = {}
    for name in os.listdir(os.path.join(ROOT, "data")):
        path = os.path.join(ROOT, "data", name, "roster.jsonl")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    idx[str(r["nid"])] = (r["title"], name)
    return idx


def main():
    idx = roster_index()
    by_track = {}
    for tid, award, nid in CANDIDATES:
        if str(nid) not in idx:
            raise SystemExit(f"nid {nid} 不在 roster，中止")
        title, real_track = idx[str(nid)]
        if str(real_track) != str(tid):
            raise SystemExit(f"nid {nid} 属赛道 {real_track}，与声明 {tid} 不符，中止")
        by_track.setdefault(str(tid), []).append((nid, title, award))

    for tid, rows in by_track.items():
        path = os.path.join(ROOT, "data", tid, "awards.jsonl")
        existing = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                existing = [json.loads(line) for line in f if line.strip()]
        by_key = {(str(r["nid"]), r.get("award")): r for r in existing}

        added = updated = 0
        for nid, title, award in rows:
            key = (str(nid), award)
            if key in by_key:
                r = by_key[key]
                if not r.get("verified") or r.get("source") != SOURCE:
                    r.update({"title": title, "verified": True, "verified_at": TODAY,
                              "source": SOURCE, "note": ""})
                    updated += 1
            else:
                existing.append({
                    "nid": nid,
                    "title": title,
                    "award": award,
                    "source": SOURCE,
                    "verified": True,
                    "verified_at": TODAY,
                    "note": "",
                })
                added += 1

        with open(path, "w", encoding="utf-8") as f:
            for r in existing:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        print(f"赛道 {tid}: 新增 {added}，更新 {updated}，现有 {len(existing)} 条")


if __name__ == "__main__":
    main()
