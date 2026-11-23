#!/usr/bin/env python3
"""十二征（2024）获奖公示候选清单 —— 供人工核对，不写入 awards.jsonl。

来源（用户提供的两个公示 URL）：
- 中/短篇终审公布: https://pages.sfacg.com/h5/act/zw20240504/Q3PrLponYiEwN
- 长篇终审公布:   https://pages.sfacg.com/h5/act/zw20240504/YiEoewNrQperQerQnWin

提取方式：Vue SPA 的 JS bundle (index.820980da.js) 里，获奖作品为图片热区，
每张图片绑定 openNovel(nid)；奖项、作品名、作者写在图片画面上，已逐张 OCR 核对。
作品名/作者与 roster.jsonl 交叉验证一致（唯一例外见下方 note）。

大赏（01/02 卡片）标注「大赏本次轮空」，从未颁发，不列入。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (contest_track_id, award, nid, card_no)
CANDIDATES = [
    # 十二征-长篇 (702) — YiEoewNrQperQerQnWin，卡片 03~21
    (702, "金奖",       705464, 3),
    (702, "银奖",       708316, 4),
    (702, "银奖",       708045, 5),
    (702, "银奖",       703954, 6),
    (702, "铜奖",       713298, 7),
    (702, "铜奖",       705589, 8),   # 不在 roster 中，仅有公示卡片为证
    (702, "铜奖",       702351, 9),
    (702, "铜奖",       716987, 10),
    (702, "铜奖",       711657, 11),
    (702, "编辑推荐奖", 705110, 12),
    (702, "编辑推荐奖", 718624, 13),
    (702, "编辑推荐奖", 718727, 14),
    (702, "编辑推荐奖", 700575, 15),
    (702, "编辑推荐奖", 700215, 16),
    (702, "星火奖",     707407, 17),
    (702, "星火奖",     714477, 18),
    (702, "星火奖",     704587, 19),
    (702, "星火奖",     715189, 20),
    (702, "星火奖",     718504, 21),
    # 十二征-中篇 (703) — Q3PrLponYiEwN，tab1 (z1~z5)
    (703, "金奖", 715955, 1),
    (703, "银奖", 718551, 2),
    (703, "铜奖", 719355, 3),
    (703, "铜奖", 720717, 4),
    (703, "铜奖", 700285, 5),
    # 十二征-短篇 (704) — Q3PrLponYiEwN，tab2 (d1~d5)
    (704, "金奖", 709232, 1),
    (704, "银奖", 700141, 2),
    (704, "铜奖", 704157, 3),
    (704, "铜奖", 710642, 4),
    (704, "铜奖", 720357, 5),
]

SOURCES = {
    702: "https://pages.sfacg.com/h5/act/zw20240504/YiEoewNrQperQerQnWin",
    703: "https://pages.sfacg.com/h5/act/zw20240504/Q3PrLponYiEwN",
    704: "https://pages.sfacg.com/h5/act/zw20240504/Q3PrLponYiEwN",
}


def roster_index():
    idx = {}
    for name in os.listdir(os.path.join(ROOT, "data")):
        path = os.path.join(ROOT, "data", name, "roster.jsonl")
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                idx[str(r["nid"])] = (r["title"], r["author"], name)
    return idx


def main():
    idx = roster_index()
    print(f"{'track':6} {'award':10} {'nid':8} {'卡片':4} {'书名':28} {'作者':12} 校验")
    print("-" * 100)
    for tid, award, nid, card in CANDIDATES:
        r = idx.get(str(nid))
        if not r:
            print(f"{tid:<6} {award:<10} {nid:<8} {card:<4} {'(roster 缺失)':28} {'':12} !! 缺失")
            continue
        title, author, real_track = r
        ok = "OK" if str(real_track) == str(tid) else f"!! 赛道实为 {real_track}"
        print(f"{tid:<6} {award:<10} {nid:<8} {card:<4} {title[:26]:28} {author[:10]:12} {ok}")
    print(f"\n合计 {len(CANDIDATES)} 条")


if __name__ == "__main__":
    main()
