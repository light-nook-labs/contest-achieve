#!/usr/bin/env python3
"""一次性导入：十三征（2025）官网获奖公示的 25 部获奖作品。

来源：https://pages.sfacg.com/h5/act/zw20250504/YiEoewNrQpersdQerQnWin
证据：奖项公示页是 Vue SPA，获奖作品与奖项硬编码在
      /h5/act/zw20250504/js/index.d34358c7.js 的 Xe 渲染模板中。
      每张作品图绑定 openNovel(nid)，奖项写在图片文件名
      （02金奖作品 / 04银奖作品 / 06铜奖作品 / 08推荐奖作品 / 10星火奖作品）。
      书名/作者由 nid 从 roster.jsonl join 得到（比 OCR 更可靠，已抽样用图片核对）。

「大赏」从未颁发，公示页也标注「大赏本次轮空」，不写入。

行为：
- 752：已有的 15 个 nid 就地标定 award，verified=true，source 补公示 URL；其余记录不动。
- 753 / 754：新建 awards.jsonl，写入金/银/铜各档。
- 幂等：重复执行不会重复写入；已标定的记录不会回退。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_URL = "https://pages.sfacg.com/h5/act/zw20250504/YiEoewNrQpersdQerQnWin"
TODAY = "2026-11-23"

# (contest_track_id, award, nid) —— 经人工核验的 25 部
AWARDS = [
    (752, "金奖", 759334),
    (752, "银奖", 753537),
    (752, "铜奖", 751089),
    (752, "铜奖", 758795),
    (752, "铜奖", 747572),
    (752, "推荐奖", 747887),
    (752, "推荐奖", 755660),
    (752, "推荐奖", 757489),
    (752, "推荐奖", 744362),
    (752, "推荐奖", 755132),
    (752, "星火奖", 758855),
    (752, "星火奖", 746249),
    (752, "星火奖", 754010),
    (752, "星火奖", 755374),
    (752, "星火奖", 753889),
    (753, "金奖", 759040),
    (753, "银奖", 758410),
    (753, "铜奖", 756107),
    (753, "铜奖", 747911),
    (753, "铜奖", 759973),
    (754, "金奖", 758957),
    (754, "银奖", 746723),
    (754, "铜奖", 755065),
    (754, "铜奖", 759837),
    (754, "铜奖", 751851),
]


def roster_index():
    idx = {}
    for name in os.listdir(os.path.join(ROOT, "data")):
        tid = name
        path = os.path.join(ROOT, "data", tid, "roster.jsonl")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    idx[r["nid"]] = (r["title"], tid)
    return idx


def main():
    idx = roster_index()
    by_track = {}
    for tid, award, nid in AWARDS:
        if nid not in idx:
            raise SystemExit(f"nid {nid} 不在 roster 中，中止导入")
        title, roster_tid = idx[nid]
        if str(roster_tid) != str(tid):
            raise SystemExit(f"nid {nid} 在 roster 属赛道 {roster_tid}，与导入声明 {tid} 不符")
        by_track.setdefault(str(tid), []).append((nid, title, award))

    for tid, rows in by_track.items():
        path = os.path.join(ROOT, "data", tid, "awards.jsonl")
        existing = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                existing = [json.loads(line) for line in f if line.strip()]
        by_nid = {r["nid"]: r for r in existing}

        updated = added = 0
        for nid, title, award in rows:
            source = f"{SOURCE_URL} 公示（十三征，图片文件名标注奖项）"
            if nid in by_nid:
                r = by_nid[nid]
                if r.get("award") != award or not r.get("verified"):
                    r["award"] = award
                    r["verified"] = True
                    r["verified_at"] = TODAY
                    r["source"] = source
                    updated += 1
            else:
                existing.append({
                    "nid": nid,
                    "title": title,
                    "award": award,
                    "source": source,
                    "verified": True,
                    "verified_at": TODAY,
                    "note": "",
                })
                added += 1

        with open(path, "w", encoding="utf-8") as f:
            for r in existing:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        print(f"赛道 {tid}: 更新 {updated} 条，新增 {added} 条，现有 {len(existing)} 条")


if __name__ == "__main__":
    main()
