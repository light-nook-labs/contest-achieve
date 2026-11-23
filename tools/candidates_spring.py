"""春征获奖候选清单（供人工目视核对，不写入数据）。

数据来源：活动页最后一个 tab「获奖」区块。
- 473（2022 春征）：Vue SPA，获奖组件 GetAwardWorks。6 个图片热区（分档标题图确认
  金1/银2/铜3）+ JS 数据直接标注的 sparkPrizeList（星火奖5）/commendedList（推荐奖5）。
- 632（2023 春征）：Vue SPA，获奖区在懒加载 chunk 的 End 组件里，按 item1~item6 分组，
  人数 1/2/3/5/5/5。item1~3 为金/银/铜（人数+同构推断）；item4~6 各5人，奖项名画在
  图片上、JS 无文字标注，需人工目视确认（暂用占位）。

所有 nid 已与 roster.jsonl 书名/作者交叉验证，且都属于各自赛道。
"""

SOURCE_473 = "https://pages.sfacg.com/h5/act/zw20220301/"
SOURCE_632 = "https://pages.sfacg.com/h5/act/zw20230301/"

# 473：奖项确定（图片热区分档已确认，星火/推荐 JS 明确标注）
CANDIDATES_473 = [
    ("金奖", "538652"),
    ("银奖", "541581"), ("银奖", "540307"),
    ("铜奖", "532516"), ("铜奖", "536611"), ("铜奖", "538855"),
    ("星火奖", "538631"), ("星火奖", "529938"), ("星火奖", "534476"),
    ("星火奖", "538912"), ("星火奖", "532079"),
    ("推荐奖", "547760"), ("推荐奖", "530917"), ("推荐奖", "530038"),
    ("推荐奖", "538636"), ("推荐奖", "548375"),
]

# 632：item1~3 金银铜；item4~6 三组各5人奖项名由用户目视确认
# = 推荐奖（A）/ 鼓励奖（B）/ 星火奖（C）。
# 注意 nid 635145 在 A、B 两组各出现一次（官方页面热区复用），按 (nid,award) 双键保留两条。
CANDIDATES_632 = [
    ("金奖", "627189"),
    ("银奖", "636601"), ("银奖", "626412"),
    ("铜奖", "629008"), ("铜奖", "626782"), ("铜奖", "632966"),
    ("推荐奖", "628167"), ("推荐奖", "636425"), ("推荐奖", "632848"),
    ("推荐奖", "626294"), ("推荐奖", "635145"),
    ("鼓励奖", "635145"), ("鼓励奖", "626428"), ("鼓励奖", "626389"),
    ("鼓励奖", "632090"), ("鼓励奖", "626649"),
    ("星火奖", "626176"), ("星火奖", "615840"), ("星火奖", "626440"),
    ("星火奖", "629193"), ("星火奖", "632122"),
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

    for tid, name, source, cands in [
        ("473", "2022春征", SOURCE_473, CANDIDATES_473),
        ("632", "2023春征", SOURCE_632, CANDIDATES_632),
    ]:
        print(f"===== {tid} {name} （{len(cands)} 条）{source}")
        for award, nid in cands:
            r = idx.get(nid)
            print(f"  {award:<12} {nid} | {r[0] if r else '⚠️不在roster'} | {r[1] if r else ''}")
        print()


if __name__ == "__main__":
    main()
