#!/usr/bin/env python3
"""导入：十二征（2024）官网获奖公示的 29 部获奖作品。

来源（人工目视核对确认）：
- 长篇终审公布: https://pages.sfacg.com/h5/act/zw20240504/YiEoewNrQperQerQnWin
- 中/短篇终审公布: https://pages.sfacg.com/h5/act/zw20240504/Q3PrLponYiEwN

奖项、作品名、作者来自公示卡片逐张目视核对；书名/作者与 roster.jsonl 交叉验证
（705589《失败了，就会恶堕成妖女》未进入采集清单，仅以公示卡片为据，note 已标注）。
大赏标注「本次轮空」，从未颁发，不写入。

幂等：按 nid 去重，重复执行不产生重复行；已存在记录不回退。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-11-23"

SOURCE_LONG = "https://pages.sfacg.com/h5/act/zw20240504/YiEoewNrQperQerQnWin 公示（十二征·长篇终审，人工目视核对）"
SOURCE_SHORT = "https://pages.sfacg.com/h5/act/zw20240504/Q3PrLponYiEwN 公示（十二征·中/短篇终审，人工目视核对）"

# (contest_track_id, award, nid)
AWARDS = [
    # 十二征-长篇 (702)
    (702, "金奖", 705464),
    (702, "银奖", 708316),
    (702, "银奖", 708045),
    (702, "银奖", 703954),
    (702, "铜奖", 713298),
    (702, "铜奖", 705589),
    (702, "铜奖", 702351),
    (702, "铜奖", 716987),
    (702, "铜奖", 711657),
    (702, "编辑推荐奖", 705110),
    (702, "编辑推荐奖", 718624),
    (702, "编辑推荐奖", 718727),
    (702, "编辑推荐奖", 700575),
    (702, "编辑推荐奖", 700215),
    (702, "星火奖", 707407),
    (702, "星火奖", 714477),
    (702, "星火奖", 704587),
    (702, "星火奖", 715189),
    (702, "星火奖", 718504),
    # 十二征-中篇 (703)
    (703, "金奖", 715955),
    (703, "银奖", 718551),
    (703, "铜奖", 719355),
    (703, "铜奖", 720717),
    (703, "铜奖", 700285),
    # 十二征-短篇 (704)
    (704, "金奖", 709232),
    (704, "银奖", 700141),
    (704, "铜奖", 704157),
    (704, "铜奖", 710642),
    (704, "铜奖", 720357),
]

# 未进入 roster 的作品，公示卡片为唯一依据
NOT_IN_ROSTER = {705589}


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
    for tid, award, nid in AWARDS:
        if str(nid) in idx:
            title, real_track = idx[str(nid)]
            if str(real_track) != str(tid):
                raise SystemExit(f"nid {nid} 属赛道 {real_track}，与声明 {tid} 不符，中止")
        else:
            if nid not in NOT_IN_ROSTER:
                raise SystemExit(f"nid {nid} 不在 roster 且未登记例外，中止")
            title = "失败了，就会恶堕成妖女"  # 取自公示卡片
        by_track.setdefault(str(tid), []).append((nid, title, award))

    for tid, rows in by_track.items():
        source = SOURCE_LONG if tid == "702" else SOURCE_SHORT
        path = os.path.join(ROOT, "data", tid, "awards.jsonl")
        existing = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                existing = [json.loads(line) for line in f if line.strip()]
        by_nid = {r["nid"]: r for r in existing}

        added = updated = 0
        for nid, title, award in rows:
            note = "公示卡片为据，未进入采集清单" if nid in NOT_IN_ROSTER else ""
            if nid in by_nid:
                r = by_nid[nid]
                if r.get("award") != award or not r.get("verified"):
                    r["award"] = award
                    r["verified"] = True
                    r["verified_at"] = TODAY
                    r["source"] = source
                    r["note"] = note
                    updated += 1
            else:
                existing.append({
                    "nid": nid,
                    "title": title,
                    "award": award,
                    "source": source,
                    "verified": True,
                    "verified_at": TODAY,
                    "note": note,
                })
                added += 1

        with open(path, "w", encoding="utf-8") as f:
            for r in existing:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        print(f"赛道 {tid}: 新增 {added}，更新 {updated}，现有 {len(existing)} 条")


if __name__ == "__main__":
    main()
