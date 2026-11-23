"""693（2024 主题短篇）获奖候选清单。

来源：https://pages.sfacg.com/h5/act/zw20240105/
获奖数据在 SPA `js/index.7d3dc41b.js` 的 `isShowAwards` 分支 `.award-list`：
三组标题图的 alt 属性直接写明「一等奖 / 二等奖 / 三等奖」（非图片 OCR 猜测），
其后紧跟作品热区 `openNovel2(nid)`，分组数量 1 / 1 / 3，共 5 部。

5 个 nid 已与 roster.jsonl 书名/作者交叉验证，均属赛道 693。
"""
SOURCE = "https://pages.sfacg.com/h5/act/zw20240105/ 公示（2024主题短篇，页面内嵌文字奖项名）"

# (contest_track_id, award, nid)
CANDIDATES = [
    (693, "一等奖", 681784),
    (693, "二等奖", 684176),
    (693, "三等奖", 689024), (693, "三等奖", 684819), (693, "三等奖", 681823),
]


def main():
    import json
    import os

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "data", "693", "roster.jsonl")
    titles = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                titles[str(r["nid"])] = r["title"]
    for tid, award, nid in CANDIDATES:
        print(tid, award, nid, titles.get(str(nid), "⚠️ 不在 roster"))


if __name__ == "__main__":
    main()
