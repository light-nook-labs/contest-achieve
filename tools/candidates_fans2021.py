#!/usr/bin/env python3
"""候选：2021 同人征文（468 失业魔王 / 469 英雄再临）获奖名单。

公示页：https://pages.sfacg.com/h5/act/fanszw202112end/
活动页：https://pages.sfacg.com/h5/act/fanszw202112/
（活动页接口 getNovels params.tagIds="468,469"，确认覆盖两个赛道）

公示图共 3 张：封面/LICENSE、获奖区 6 个 nid、人气参与奖 10 个 nid。
用户目视确认奖项分组：
- 一等奖 1：514562 失业魔王：世界线因我而变动（468）
- 二等奖 2：515313 我真的不想越帮越忙啊！（468）、514313 英雄再临之霍伦思帝国篇前传（469）
- 三等奖 3：508745 失业魔王之平行世界（468）、514094 失业魔王：剑魔灭世（468）、
             508904 英雄？早就不爱了（469）
- 人气参与奖 10：公示页数据中的 popularData，9 本可在 roster 找到并按书名归属赛道；
  510029 英雄再临之伊文的游戏在全库 roster 均不存在（作品已下架/缺失），按用户此前规则不写入。

共导入 15 条；所有 nid 的书名/作者/赛道均与 roster 交叉验证通过。
"""

SOURCE = "https://pages.sfacg.com/h5/act/fanszw202112end/"

# (contest_track_id, award, nid)
CANDIDATES = [
    (468, "一等奖", 514562),
    (468, "二等奖", 515313),
    (469, "二等奖", 514313),
    (468, "三等奖", 508745),
    (468, "三等奖", 514094),
    (469, "三等奖", 508904),
    (468, "人气参与奖", 514033),
    (469, "人气参与奖", 509236),
    (469, "人气参与奖", 510486),
    (468, "人气参与奖", 511972),
    (469, "人气参与奖", 509609),
    (469, "人气参与奖", 509160),
    (469, "人气参与奖", 513095),
    (468, "人气参与奖", 508931),
    (469, "人气参与奖", 510614),
]

# 公示页列出但全库 roster 缺失，暂不导入。
SKIPPED = [
    (469, "人气参与奖", 510029, "英雄再临之伊文的游戏", "全库 roster 无此书"),
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
