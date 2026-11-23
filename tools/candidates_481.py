"""481（2022 主题秋征）获奖候选清单（用户目视核对确认）。

来源：https://pages.sfacg.com/h5/act/zw20220930/
获奖区在 SPA `js/index.1858c64f.js` 的 isEnd 分支 `.awards`，11 个作品热区按
背景图分组数量为 1/2/3/5；用户目视确认四组依次为 金奖 / 银奖 / 铜奖 / 推荐奖。

11 个 nid 已与 roster.jsonl 书名/作者交叉验证，均属赛道 481。
"""
SOURCE = "https://pages.sfacg.com/h5/act/zw20220930/ 公示（2022主题秋征，用户目视核对）"

# (contest_track_id, award, nid)
CANDIDATES = [
    (481, "金奖", 598456),
    (481, "银奖", 591485), (481, "银奖", 591904),
    (481, "铜奖", 528740), (481, "铜奖", 598586), (481, "铜奖", 596295),
    (481, "推荐奖", 598533), (481, "推荐奖", 593818), (481, "推荐奖", 581210),
    (481, "推荐奖", 594902), (481, "推荐奖", 591391),
]


def main():
    import json
    import os

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "data", "481", "roster.jsonl")
    idx = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                idx[str(r["nid"])] = (r["title"], r["author"])

    for award, nid in [(a, n) for _, a, n in CANDIDATES]:
        r = idx.get(str(nid))
        print(f"  {award:<6} {nid} | {r[0] if r else '⚠️不在roster'} | {r[1] if r else ''}")


if __name__ == "__main__":
    main()
