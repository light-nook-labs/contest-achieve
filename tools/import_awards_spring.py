#!/usr/bin/env python3
"""导入：2022 / 2023 春季征文官网获奖公示（共 37 部）。

来源（活动页最后一个 tab「获奖」区块，用户目视核对确认）：
- 473（2022春征）: https://pages.sfacg.com/h5/act/zw20220301/
  6 个图片热区（分档标题图确认 金1/银2/铜3）+ JS 数据标注的 星火奖5 / 推荐奖5。
- 632（2023春征）: https://pages.sfacg.com/h5/act/zw20230301/
  获奖区在懒加载 chunk 的 End 组件，item1~6 分组 = 金1/银2/铜3/推荐5/鼓励5/星火5。
  后三组奖项名由用户目视确认（推荐/鼓励/星火）。
  nid 635145 在推荐奖、鼓励奖各出现一次（官方页面热区复用），按 (nid,award) 双键保留两条。

所有 37 个 nid 已与 roster.jsonl 书名/作者交叉验证，均属各自赛道。

幂等：按 (nid, award) 复合键去重，重复执行不产生重复行；已存在记录不回退。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-11-23"

SOURCE_473 = "https://pages.sfacg.com/h5/act/zw20220301/ 公示（2022春征，用户目视核对）"
SOURCE_632 = "https://pages.sfacg.com/h5/act/zw20230301/ 公示（2023春征，用户目视核对）"

# (contest_track_id, award, nid)
AWARDS = [
    # 2022春征 (473) — 16 条
    (473, "金奖", 538652),
    (473, "银奖", 541581), (473, "银奖", 540307),
    (473, "铜奖", 532516), (473, "铜奖", 536611), (473, "铜奖", 538855),
    (473, "星火奖", 538631), (473, "星火奖", 529938), (473, "星火奖", 534476),
    (473, "星火奖", 538912), (473, "星火奖", 532079),
    (473, "推荐奖", 547760), (473, "推荐奖", 530917), (473, "推荐奖", 530038),
    (473, "推荐奖", 538636), (473, "推荐奖", 548375),
    # 2023春征 (632) — 21 条
    (632, "金奖", 627189),
    (632, "银奖", 636601), (632, "银奖", 626412),
    (632, "铜奖", 629008), (632, "铜奖", 626782), (632, "铜奖", 632966),
    (632, "推荐奖", 628167), (632, "推荐奖", 636425), (632, "推荐奖", 632848),
    (632, "推荐奖", 626294), (632, "推荐奖", 635145),
    (632, "鼓励奖", 635145), (632, "鼓励奖", 626428), (632, "鼓励奖", 626389),
    (632, "鼓励奖", 632090), (632, "鼓励奖", 626649),
    (632, "星火奖", 626176), (632, "星火奖", 615840), (632, "星火奖", 626440),
    (632, "星火奖", 629193), (632, "星火奖", 632122),
]

# 同一 nid 跨奖项（官方热区复用），写入时按 (nid,award) 双键区分
MULTI_AWARD_NIDS = {635145}


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
        if str(nid) not in idx:
            raise SystemExit(f"nid {nid} 不在 roster，中止")
        title, real_track = idx[str(nid)]
        if str(real_track) != str(tid):
            raise SystemExit(f"nid {nid} 属赛道 {real_track}，与声明 {tid} 不符，中止")
        by_track.setdefault(str(tid), []).append((nid, title, award))

    for tid, rows in by_track.items():
        source = SOURCE_473 if tid == "473" else SOURCE_632
        path = os.path.join(ROOT, "data", tid, "awards.jsonl")
        existing = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                existing = [json.loads(line) for line in f if line.strip()]
        # 复合键：字符串 nid + award，兼容历史整数 nid
        by_key = {(str(r["nid"]), r.get("award")): r for r in existing}

        added = updated = 0
        for nid, title, award in rows:
            key = (str(nid), award)
            note = "官方公示页热区复用，同作品跨奖项" if nid in MULTI_AWARD_NIDS else ""
            if key in by_key:
                r = by_key[key]
                if not r.get("verified") or r.get("source") != source:
                    r.update({"title": title, "verified": True, "verified_at": TODAY,
                              "source": source, "note": note})
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
