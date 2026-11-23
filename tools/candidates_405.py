#!/usr/bin/env python3
"""候选：崩坏3rd 征文（405）获奖名单，用户提供公示后确认。

来源：https://pages.sfacg.com/h5/act/sfxbbb/
用户给出 18 本，其中 17 本精确/近似匹配 roster 并核对归属 405：
- 一等奖 2：186950 崩坏3rd短篇小说集 / 184355 律空四重奏
- 二等奖 5：178619 岁晏、180156 愚者之偿、186223 天穹之战、
            187223 如那天温柔的风、179739 傲娇女王的养成指南
            （用户另给《叹长生》，roster 无此书，暂缺）
- 三等奖 10：177874 为崩坏世界献上美好的祝福、185939 致我所爱的女孩、
             183829 崩坏3rd同人文一一绀海之汐（用户作「——」）、
             179937 即使世界崩坏我也要勇敢地活下去（用户作「的」）、
             178292 舰长家今天的饭、183133 隽风塔楼重制版、
             178900 布洛妮娅的舞台剧、178133 崩坏3舰长的逆袭、
             178772 穿越成舰长的我再不做清洁工了、178191 崩坏3rd穿越成为女武神吧

《叹长生》（二等奖）在所有赛道 roster 均未找到，暂不写入，待用户确认。
所有 nid 均已与 roster 的书名/作者/赛道交叉验证通过。
"""
SOURCE = "https://pages.sfacg.com/h5/act/sfxbbb/"

# (contest_track_id, award, nid)
CANDIDATES = [
    (405, "一等奖", 186950),
    (405, "一等奖", 184355),
    (405, "二等奖", 178619),
    (405, "二等奖", 180156),
    (405, "二等奖", 186223),
    (405, "二等奖", 187223),
    (405, "二等奖", 179739),
    (405, "三等奖", 177874),
    (405, "三等奖", 185939),
    (405, "三等奖", 183829),
    (405, "三等奖", 179937),
    (405, "三等奖", 178292),
    (405, "三等奖", 183133),
    (405, "三等奖", 178900),
    (405, "三等奖", 178133),
    (405, "三等奖", 178772),
    (405, "三等奖", 178191),
]


def roster_title(nid):
    """供人工核对：返回 roster 中的真实书名。"""
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
