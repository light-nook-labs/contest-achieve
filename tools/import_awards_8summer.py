"""导入第八届夏征（八征）获奖名单。

用户提供来源：官方手机 App 公示（2026-11-24）。
名单原文每条带固定前缀「第八届夏征长篇银奖·」，真正的分组在后面：
长篇 / 中篇小说 / 短篇小说 + 奖项档位。
按书名在对应赛道 roster 中核对 nid；按 (nid, award) 去重，幂等可重跑。
"""

import json
import os

# (赛道 ID, 奖项, 名单书名, roster 实际书名, 备注)
ROWS = []

# 长篇 -> 418（19 条）
LONG = [
    ("黑化少女观察日记与我的求生指南", "金奖"),
    ("反派师尊的我带着徒弟们天下无敌", "银奖"),
    ("穿越后成了魔道大师兄", "银奖"),
    ("反正朕只是个爱摸鱼的魔王", "银奖"),
    ("无敌的我偏偏情商太高", "铜奖"),
    ("本死灵术士要攻略已死的美少女们", "铜奖"),
    ("黑化仙子怎么可能杀死主角的我", "铜奖"),
    ("圣女小姐霸占了我的地下城", "铜奖"),
    ("因为作死我被变成了弱气吸血鬼", "铜奖"),
    ("为了诸天没事我娶了反派BOSS", "推荐奖"),
    ("我可以进入少女们的噩梦", "推荐奖"),
    ("新徒儿是魔教女尊却也喜欢我", "推荐奖"),
    ("劫回来的夫人竟然是傲天女剑帝", "推荐奖"),
    ("为了报仇美少女求我重出江湖", "推荐奖"),
    ("我被堕落成魔物的少女们疯狂倒追", "新星奖"),
    ("我的分身招惹了一群仙子大佬", "新星奖"),
    ("在异世软饭硬吃的日子", "新星奖"),
    ("嫁作他人妇", "新星奖"),
    ("每天都是颓废摸鱼小城管", "新星奖"),
]
for title, award in LONG:
    ROWS.append((418, award, title, title, ""))

# 中篇小说 -> 419（5 条）
# 格式：(名单书名, 奖项, roster 实际书名, 备注)
MID = [
    ("恋爱清剿计划", "金奖", "恋爱清剿计划", ""),
    ("被少女疯狂逼婚的我天生面瘫", "银奖", "被少女疯狂逼婚的我天生面瘫", ""),
    ("被时间束缚的少女", "铜奖", "被时间束缚的少女", ""),
    ("世界尽头的图图书物语", "铜奖", "世界尽头的图书物语", "名单原文《世界尽头的图图书物语》，按 roster 书名匹配"),
    ("识人不清的我转生成了恶役千金", "铜奖", "识人不清的我转生成了恶役千金", ""),
]
for user_title, award, actual, note in MID:
    ROWS.append((419, award, user_title, actual, note))

# 短篇小说 -> 420（5 条）
SHORT = [
    ("鼠群酒吧", "金奖"),
    ("失落之海", "银奖"),
    ("重生到刚遇到她时的我不想错过她", "铜奖"),
    ("迟暮骑士踏上约定的回程", "铜奖"),
    ("起舞", "铜奖"),
]
for title, award in SHORT:
    ROWS.append((420, award, title, title, ""))

SOURCE = "官方 App 公示「第八届夏征奖」（用户提供 2026-11-24）"
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
