#!/usr/bin/env python3
"""候选：校园都市征文（414）获奖名单，用户目视/提供。

赛事：SF轻小说第二届校园征文大赛
来源：https://pages.sfacg.com/h5/act/xyzw2019/
共 12 条：金奖 1、银奖 2、铜奖 3、新星奖 6。全部匹配 414 roster。
作者信息保留在 roster，不写入 awards.jsonl。

轻微差异（按唯一书名/作者匹配确认，不写入 awards）：
- 用户作《女儿心》，roster 作《女兒心》（繁体「兒」），nid 247674，作者乱世银娘。
- 用户作者「jjb发发呆」，roster 作「jjb发发」，nid 247961。
- 用户作者「垲依」，roster 作「瑄依」，nid 247719。

其余 9 条书名与作者均精确匹配。
"""

SOURCE = "https://pages.sfacg.com/h5/act/xyzw2019/"

# (contest_track_id, award, nid)
CANDIDATES = [
    (414, "金奖", 247710),
    (414, "银奖", 249460),
    (414, "银奖", 247961),
    (414, "铜奖", 247801),
    (414, "铜奖", 247907),
    (414, "铜奖", 247674),
    (414, "新星奖", 253762),
    (414, "新星奖", 251746),
    (414, "新星奖", 247861),
    (414, "新星奖", 248147),
    (414, "新星奖", 247719),
    (414, "新星奖", 248247),
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
