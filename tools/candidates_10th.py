"""十征（2022）获奖候选清单（用户目视核对确认）。

来源：https://pages.sfacg.com/h5/act/zw2022/winner.html
数据硬编码在 `js/winner.54aa1778.js` 的 openNovel / openNovel2 热区：
- c1/c2/c3/c4（475 长篇）分组数量 1/3/5/5，用户确认为 金奖/银奖/铜奖/推荐奖。
- z1/z2/z3（476 中篇）、d1/d2/d3（477 短篇）分组数量 1/1/3，用户确认为 金奖/银奖/铜奖。
- xh（星火奖）10 条，其中 6 条属 475、4 条属 479（对话赛道），按 roster 归属拆分。

全部 34 个 nid 已与 roster.jsonl 书名/作者交叉验证，均属声明赛道。
"""
SOURCE = "https://pages.sfacg.com/h5/act/zw2022/winner.html 公示（十征，用户目视核对）"

# (contest_track_id, award, nid)
CANDIDATES = [
    # 475 长篇 — 14 条
    (475, "金奖", 570628),
    (475, "银奖", 558705), (475, "银奖", 567122), (475, "银奖", 556321),
    (475, "铜奖", 568750), (475, "铜奖", 558132), (475, "铜奖", 563924),
    (475, "铜奖", 585451), (475, "铜奖", 579164),
    (475, "推荐奖", 548678), (475, "推荐奖", 582328), (475, "推荐奖", 576657),
    (475, "推荐奖", 552966), (475, "推荐奖", 550911),
    # 476 中篇 — 5 条
    (476, "金奖", 548842),
    (476, "银奖", 593049),
    (476, "铜奖", 591052), (476, "铜奖", 565208), (476, "铜奖", 570518),
    # 477 短篇 — 5 条
    (477, "金奖", 579284),
    (477, "银奖", 592306),
    (477, "铜奖", 552804), (477, "铜奖", 550302), (477, "铜奖", 549546),
    # 星火奖 — 10 条（按 roster 赛道拆分）
    (475, "星火奖", 548667), (475, "星火奖", 562629), (475, "星火奖", 562119),
    (475, "星火奖", 590959), (475, "星火奖", 587578), (475, "星火奖", 585238),
    (479, "星火奖", 556923), (479, "星火奖", 588321), (479, "星火奖", 572061),
    (479, "星火奖", 579138),
]


def main():
    import json
    import os

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    idx = {}
    for name in os.listdir(os.path.join(root, "data")):
        path = os.path.join(root, "data", name, "roster.jsonl")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    idx[str(r["nid"])] = (r["title"], r["author"], name)

    for tid, award, nid in CANDIDATES:
        r = idx.get(str(nid))
        ok = bool(r) and r[2] == str(tid)
        mark = "" if ok else " ⚠️赛道不符/不在roster"
        print(f"{tid} {award:<5} {nid} | {r[0] if r else '?'} | {r[1] if r else ''}{mark}")


if __name__ == "__main__":
    main()
