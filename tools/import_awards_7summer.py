"""导入第七届夏征（七征）获奖名单。

用户提供来源：官方手机 App 公示（2026-11-24）。
名单原文每条带固定前缀「第七届夏征长篇铜奖」，真正分组在后面：
长篇 / 中篇小说 / 短篇小说 / 对话小说·长篇 / 对话小说·短篇 + 奖项档位。
赛道映射：408 长 / 409 中 / 410 短 / 411 对话长 / 412 对话短（经书名核对确认）。
按书名在对应赛道 roster 中核对 nid；按 (nid, award) 去重，幂等可重跑。
两条无法可靠匹配的条目暂缺，待用户确认后补（见 SKIPPED）。
"""

import json
import os

# (赛道 ID, 奖项, 名单书名, roster 实际书名, 备注)
ROWS = []

def add(tid, award, user_title, actual=None, note=""):
    ROWS.append((tid, award, user_title, actual or user_title, note))

# 两条书名差异：roster 里找到唯一相近书，按实际书名导入并注明原文
DIFF_NOTE = "名单书名与 roster 略有出入，按 roster 实际书名匹配"

# 长篇 -> 408（名单 14 条，1 条待确认跳过，导入 13）
add(408, "金奖", "异界医生的我娶了个龙傲天美少女")
add(408, "银奖", "被我气坏的高傲美少女都喜欢我啦")
add(408, "银奖", "被各方仙子妖尊宠溺的我很烦恼")
add(408, "银奖", "我转生就超神")
add(408, "铜奖", "掌控时间的我是不是已经无敌了")
add(408, "铜奖", "变成狐娘的我被青龙圣女捕获了", "变成狐娘的我被真龙圣女捕获了", DIFF_NOTE + "（青龙→真龙）")
add(408, "铜奖", "最强的我想养个女徒弟")
add(408, "铜奖", "来自深渊的我今天也要拯救人类")
add(408, "铜奖", "少年校花和少女校霸")
add(408, "编辑推荐奖", "谁能挡我第二刀")
add(408, "编辑推荐奖", "我才不要在异界当什么魔师啊")
add(408, "编辑推荐奖", "家里养个富美少女")
# SKIPPED: 天才大师姐是我前世夙敌（408 编辑推荐奖；用户确认该书已下架 died，全库 roster 无记录）
add(408, "编辑推荐奖", "带着修真界仙子们天下无敌")

# 中篇小说 -> 409（5 条）
add(409, "金奖", "我的青春不会是老套的童话物语")
add(409, "银奖", "世上最后的5人")
add(409, "铜奖", "潮汐遗物")
add(409, "铜奖", "小小的勇者与穿越者咖啡厅")
add(409, "铜奖", "梦境终点")

# 短篇小说 -> 410（5 条）
add(410, "金奖", "星球娘们的日常")
add(410, "银奖", "星野结衣的愿望清单")
add(410, "铜奖", "我和她和她的恋爱物语")
add(410, "铜奖", "花岬")
add(410, "铜奖", "蝶羽之痕")

# 对话小说·长篇 -> 411（名单 14 条，1 条待确认跳过，导入 13）
add(411, "金奖", "网恋真的会见光死")
add(411, "银奖", "误入灵异聊天室的我会发生什么")
add(411, "银奖", "密室之都")
add(411, "银奖", "当世界有了超能力")
add(411, "铜奖", "活下去生存游戏里的假千金")
add(411, "铜奖", "交换身体的错误示范")
add(411, "铜奖", "克苏鲁世界观中调查员们真不轻松")
add(411, "铜奖", "不正经史莱姆城主与七美德圣女")
add(411, "铜奖", "我的网恋对象是超级偶像")
# SKIPPED: 我舰长天命上班女武神（411 编辑推荐奖；用户确认该书已下架 died，全库 roster 仅有相近作「失忆舰长天命上班」等，非同一本）
add(411, "编辑推荐奖", "SCP基金会异闻录")
add(411, "编辑推荐奖", "天降女友掉进了我的异世界")
add(411, "编辑推荐奖", "万恶之源的同学聚会")
add(411, "编辑推荐奖", "关于我变成小兽娘这件事")

# 对话小说·短篇 -> 412（9 条）
add(412, "金奖", "天堂通讯")
add(412, "银奖", "恋爱神的恶作剧")
add(412, "银奖", "天降怪兽了怎么办3在线等2急1")
add(412, "银奖", "地狱无尽延伸")
add(412, "铜奖", "若表白被拒可以有多少种花式")
add(412, "铜奖", "告诉网友我变兽了", "告诉网友我变身了", DIFF_NOTE + "（变兽→变身）")
add(412, "铜奖", "校园生活注定生死不明")
add(412, "铜奖", "迟到的正义")
add(412, "铜奖", "小志今天也有很努力呢")

SOURCE = "官方 App 公示「第七届夏征奖」（用户提供 2026-11-24）"
VERIFIED_AT = "2026-11-24"


def roster_index(tid):
    path = f"data/{tid}/roster.jsonl"
    idx = {}
    if not os.path.exists(path):
        return idx
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        idx[str(r.get("title", "")).strip().strip("《》")] = r
    return idx


def main():
    indexes = {}
    pending = []
    for tid, award, user_title, actual, note in ROWS:
        if tid not in indexes:
            indexes[tid] = roster_index(tid)
        r = indexes[tid].get(actual)
        if not r:
            print(f"MISS {tid} {award} {user_title} (lookup={actual})")
            continue
        rec = {
            "nid": str(r["nid"]),
            "title": r.get("title", ""),
            "award": award,
            "source": SOURCE,
            "verified": True,
            "verified_at": VERIFIED_AT,
        }
        if note:
            rec["note"] = note
        pending.append((tid, rec))

    existing = {}
    for tid in {t for t, _ in pending}:
        path = f"data/{tid}/awards.jsonl"
        seen = set()
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                if line.strip():
                    a = json.loads(line)
                    seen.add((str(a.get("nid")), a.get("award")))
        existing[tid] = (path, seen)

    added = {}
    for tid, rec in pending:
        path, seen = existing[tid]
        key = (rec["nid"], rec["award"])
        if key in seen:
            continue
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        seen.add(key)
        added[tid] = added.get(tid, 0) + 1

    print("新增:", dict(sorted(added.items())))
    print("合计:", sum(added.values()))


if __name__ == "__main__":
    main()
