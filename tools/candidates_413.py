#!/usr/bin/env python3
"""候选：龙之谷征文（413）获奖名单，用户目视/提供。

来源：https://pages.sfacg.com/h5/act/sfxlzg/
共 6 条：一等奖 1、二等奖 2、三等奖 3。全部书名精确匹配 413 roster，
作者信息保留在 roster，不写入 awards.jsonl。

- 一等奖：记载外的英雄（244215，Zcraft）
- 二等奖：黑骑士外传1之骑士之路（251956，小氷）、迷时（243916，太易軒）
- 三等奖：给主神跑腿的我被迫去救世（243653，站到死）、
          龙之谷之英雄降临（249079，山楂渣）、龙之谷战士向右（249711，Rubysalo）
"""

SOURCE = "https://pages.sfacg.com/h5/act/sfxlzg/"

# (contest_track_id, award, nid)
CANDIDATES = [
    (413, "一等奖", 244215),
    (413, "二等奖", 251956),
    (413, "二等奖", 243916),
    (413, "三等奖", 243653),
    (413, "三等奖", 249079),
    (413, "三等奖", 249711),
]


def roster_title(nid):
    """供人工核对：返回 roster 中的真实书名及赛道目录。"""
    import json
    import os

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in os.listdir(os.path.join(root, "data")):
        path = os.path.join(root, "data", name, "roster.jsonl")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    if str(r["nid"]) == str(nid):
                        return r["title"], name
    return None, None
