"""导入第九届夏征（九征）获奖名单。

用户提供来源：官方手机 App 公示页「第九届夏征奖」（2026-11-24）。
按书名在对应赛道 roster 中核对 nid；按 (nid, award) 去重，幂等可重跑。
星火奖按作品所属赛道分别归档（参照十征 475/479 的做法）。
"""

import json
import os

# (赛道 ID, 奖项, 书名, 备注)
ROWS = []

# 长篇小说 -> 457
LONG = [
    ("只想好好活下去却超越了主角", "金奖"),
    ("被千金小姐们柴刀后选择贤者模式", "银奖"),
    ("重生为美少女后每天都在挨收拾", "银奖"),
    ("为啥你们要试图攻略我这个男配啊", "银奖"),
    ("死亡游戏的金手指是各位美少女", "铜奖"),
    ("我在行天司那些年", "铜奖"),
    ("这些仙子天天都想被我收拾", "铜奖"),
    ("就你们这帮仙子还想倒追我", "铜奖"),
    ("我才不要被系统变成女主角啊", "铜奖"),
    ("在糟糕世界转生为圣女我绝不屈服", "推荐奖"),
    ("强娶魔王后的重启人生", "推荐奖"),
    ("我的反派女友又有什么坏心思呢", "推荐奖"),
    ("说好只是交易仙子们竟然都动心了", "推荐奖"),
    ("拒绝仙子师姐们的爱恋很难吗", "推荐奖"),
]
for title, award in LONG:
    note = "名单原文《可恶的柴刀女被它砍到了》，按 roster 书名匹配" if title == "可恶的柴刀又被它砍到了" else ""
    ROWS.append((457, award, title, note))

# 中篇小说 -> 458
MID = [
    ("命运尽头的你和我", "金奖"),
    ("住在我房间的幽灵小姐", "银奖"),
    ("德古拉的新郎", "铜奖"),
    ("猫与生之歌", "铜奖"),
    ("坏小孩的日记", "铜奖"),
]
for title, award in MID:
    ROWS.append((458, award, title, ""))

# 短篇小说 -> 459
SHORT = [
    ("被永生者", "金奖"),
    ("庇护所", "银奖"),
    ("我变成她的一条狗", "铜奖"),
    ("重庆陷阱", "铜奖"),
    ("将臣", "铜奖"),
]
for title, award in SHORT:
    ROWS.append((459, award, title, ""))

# 星火奖：按作品所属赛道归档（457 长篇 / 462 对话）
SPARK = [
    (457, "我的萌神寝室"),
    (457, "为何徒儿们看我的眼神总不对劲"),
    (457, "失恋后的我捡到了大小姐"),
    (457, "打败怪物的最好办法就是成为怪物"),
    (457, "明明很爱我却偏偏要分手后才说"),
    (457, "可恶的柴刀又被它砍到了"),
    (457, "才不是小狼狗的盘中餐"),
    (457, "被黑化少女包围的我还想抢救一下"),
    (462, "沙尼亚特的誓约"),
    (462, "战舰电竞与校园之恋"),
]
for tid, title in SPARK:
    note = "星火奖；名单原文《可恶的柴刀女被它砍到了》，按 roster 书名匹配" if title == "可恶的柴刀又被它砍到了" else "星火奖"
    ROWS.append((tid, "星火奖", title, note))

SOURCE = "官方 App 公示「第九届夏征奖」（用户提供 2026-11-24）"
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
    for tid, award, title, note in ROWS:
        if tid not in indexes:
            indexes[tid] = roster_index(tid)
        r = indexes[tid].get(title)
        if not r:
            print(f"MISS {tid} {award} {title}")
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
