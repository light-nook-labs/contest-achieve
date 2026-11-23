"""十一征（2023）获奖候选清单（供人工目视核对，不写入数据）。

数据来源：活动页 https://pages.sfacg.com/h5/act/zw20230504/pc 最后一个 tab「晋级&获奖」。
- 长篇（653）：公示组件 pt（shortlink pnerQW3nwNinYiEo），list 里标题图 1/3/7/13/19
  与作品卡片交替。标题图目视确认：金1/银3/铜5/编辑推荐5/星火5；大赏「轮空」不写入。
- 中篇（654）/短篇（655）：公示组件 vt（shortlink PrLpQ3nYiEowN），两个 tab 各5张卡片，
  文件名 z-a/z-b/z-c 与 d-a/d-b/d-c 规律 = 金1/银1/铜3（已目视确认金奖横幅）。

所有 29 个 nid 已与 roster.jsonl 书名/作者交叉验证，均属各自赛道。
"""
SOURCE = "https://pages.sfacg.com/h5/act/zw20230504/pc 公示（十一征，用户目视核对）"

# (contest_track_id, award, nid)
CANDIDATES = [
    # 653 长篇（19）
    (653, "金奖", 666497),
    (653, "银奖", 645960), (653, "银奖", 649639), (653, "银奖", 651213),
    (653, "铜奖", 653340), (653, "铜奖", 651053), (653, "铜奖", 651555),
    (653, "铜奖", 639193), (653, "铜奖", 639022),
    (653, "编辑推荐奖", 663282), (653, "编辑推荐奖", 643934), (653, "编辑推荐奖", 659729),
    (653, "编辑推荐奖", 657930), (653, "编辑推荐奖", 639089),
    (653, "星火奖", 663267), (653, "星火奖", 652893), (653, "星火奖", 665275),
    (653, "星火奖", 648953), (653, "星火奖", 644274),
    # 654 中篇（5）
    (654, "金奖", 641691), (654, "银奖", 639946),
    (654, "铜奖", 647349), (654, "铜奖", 639701), (654, "铜奖", 639096),
    # 655 短篇（5）
    (655, "金奖", 665362), (655, "银奖", 640702),
    (655, "铜奖", 641437), (655, "铜奖", 642925), (655, "铜奖", 662244),
]


def main():
    import json, os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    idx = {}
    for name in os.listdir(os.path.join(root, "data")):
        p = os.path.join(root, "data", name, "roster.jsonl")
        if not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            idx[str(r["nid"])] = (r["title"], r["author"])

    from collections import defaultdict
    by_track = defaultdict(list)
    for tid, award, nid in CANDIDATES:
        by_track[str(tid)].append((award, str(nid)))
    for tid in sorted(by_track):
        print(f"===== {tid}（{len(by_track[tid])} 条）")
        for award, nid in by_track[tid]:
            r = idx.get(nid)
            print(f"  {award:<10} {nid} | {r[0] if r else '⚠️不在roster'} | {r[1] if r else ''}")
        print()


if __name__ == "__main__":
    main()
