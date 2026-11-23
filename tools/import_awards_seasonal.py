#!/usr/bin/env python3
"""导入：春秋征文获奖公示候选（669 2023主题秋征、699 2024春征）。

数据来自活动页「获奖公示」tab，经人工目视核对确认（用户回复「没有问题」）。
- 669 zw20230930：Vue SPA，status==2 reward-list，alt 标注金/银/铜/编辑推荐/
  星火/题材鼓励。题材鼓励奖前 3 个 nid 与铜奖/编辑推荐重复，为官方页面本身
  如此，按 (nid, award) 复合键保留。
- 699 zw20240301：Vue SPA，图片名 n1~n5 分档（金/银/铜/推荐/星火）。

746/789/725/772 的现有记录已核对与公示页一致，不在本脚本改动范围。

幂等：按 (nid, award) 去重，重复执行不产生重复行。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-11-23"

SOURCE_669 = "https://pages.sfacg.com/h5/act/zw20230930/ 获奖公示（2023主题秋征，人工目视核对）"
SOURCE_699 = "https://pages.sfacg.com/h5/act/zw20240301/ 获奖公示（2024春征，人工目视核对）"

AWARDS = [
    # 669 2023主题秋征
    (669, "金奖", 670734),
    (669, "银奖", 667702), (669, "银奖", 667704),
    (669, "铜奖", 668238), (669, "铜奖", 672431), (669, "铜奖", 669124),
    (669, "编辑推荐奖", 669905), (669, "编辑推荐奖", 675093), (669, "编辑推荐奖", 670405),
    (669, "编辑推荐奖", 668466), (669, "编辑推荐奖", 672498),
    (669, "星火奖", 670655), (669, "星火奖", 667902), (669, "星火奖", 671035),
    (669, "星火奖", 670423), (669, "星火奖", 674563),
    (669, "题材鼓励奖", 672431), (669, "题材鼓励奖", 669124), (669, "题材鼓励奖", 670405),
    (669, "题材鼓励奖", 672560), (669, "题材鼓励奖", 672592),
    # 699 2024春征
    (699, "金奖", 692762),
    (699, "银奖", 694027), (699, "银奖", 696781),
    (699, "铜奖", 696732), (699, "铜奖", 695213), (699, "铜奖", 693131),
    (699, "推荐奖", 697258), (699, "推荐奖", 694785), (699, "推荐奖", 691082),
    (699, "推荐奖", 691006), (699, "推荐奖", 693020),
    (699, "星火奖", 690983), (699, "星火奖", 691059), (699, "星火奖", 691457),
    (699, "星火奖", 691218), (699, "星火奖", 690939),
]

SOURCES = {669: SOURCE_669, 699: SOURCE_699}


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
        r = idx.get(str(nid))
        if not r:
            raise SystemExit(f"nid {nid} 不在 roster，中止")
        title, real_track = r
        if str(real_track) != str(tid):
            raise SystemExit(f"nid {nid} 属赛道 {real_track}，与声明 {tid} 不符，中止")
        by_track.setdefault(str(tid), []).append((nid, title, award))

    for tid, rows in by_track.items():
        source = SOURCES[int(tid)]
        path = os.path.join(ROOT, "data", tid, "awards.jsonl")
        existing = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                existing = [json.loads(line) for line in f if line.strip()]
        seen = {(r["nid"], r.get("award")) for r in existing}

        added = 0
        for nid, title, award in rows:
            if (nid, award) in seen:
                continue
            existing.append({
                "nid": nid,
                "title": title,
                "award": award,
                "source": source,
                "verified": True,
                "verified_at": TODAY,
                "note": "",
            })
            seen.add((nid, award))
            added += 1

        with open(path, "w", encoding="utf-8") as f:
            for r in existing:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        print(f"赛道 {tid}: 新增 {added}，现有 {len(existing)} 条")


if __name__ == "__main__":
    main()
