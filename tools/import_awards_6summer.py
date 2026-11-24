"""导入第六届夏征（六征）获奖名单。

用户提供来源：官方手机 App 公示（2026-11-24）。
名单原文每条带固定前缀「第六届夏征长篇铜奖」，真正分组在后面：
长篇 / 中篇小说 / 短篇小说 / 对话小说 + 奖项档位。
赛道映射：383 长 / 384 中 / 385 短 / 386 对话（经书名核对确认）。
按书名在对应赛道 roster 中核对 nid；按 (nid, award) 去重，幂等可重跑。
三条 roster 无匹配的条目暂缺，待用户确认后补（见 SKIPPED）。
"""

import json
import os

# (赛道 ID, 奖项, 名单书名, roster 实际书名, 备注)
ROWS = []

def add(tid, award, user_title, actual=None, note=""):
    ROWS.append((tid, award, user_title, actual or user_title, note))

# 长篇 -> 383（名单 12 条，1 条待确认跳过，导入 11）
add(383, "金奖", "领主什么的无所谓啦")
add(383, "银奖", "好徒儿你就饶了为师伐")
add(383, "银奖", "圣女殿下请停止你的幻想")
add(383, "银奖", "我的女友是反派")
add(383, "铜奖", "成为神帝后我才发现全班都穿越了")
add(383, "铜奖", "当绝美少年来到女权世界")
# 被俘后血族女王将我初拥为了女儿 → 改名为《血姬与骑士》（用户确认 2026-11-24）
add(383, "铜奖", "被俘后血族女王将我初拥为了女儿", "血姬与骑士", "名单原书名《被俘后血族女王将我初拥为了女儿》，该书已改名为《血姬与骑士》（用户确认）")
add(383, "编辑推荐奖", "百物语之主")
add(383, "编辑推荐奖", "配角什么的我才不要当呢")
add(383, "编辑推荐奖", "无冕之王与魔女的轮舞")
add(383, "编辑推荐奖", "幸运值Max的异世界生活")
add(383, "编辑推荐奖", "身为魔尊的我不只是一个NPC")

# 中篇小说 -> 384（5 条）
add(384, "金奖", "那依然盛开在地下城的夕雾花")
add(384, "银奖", "我的生命还剩下八小时")
add(384, "铜奖", "姐姐雪莉的复仇汤")
add(384, "铜奖", "欧西里斯的天平")
add(384, "铜奖", "残翼丶泥淖中绽放的生命")

# 短篇小说 -> 385（名单 5 条，1 条待确认跳过，导入 4）
add(385, "金奖", "从那天起繁殖成为了法律")
add(385, "银奖", "眼泪工厂")
# SKIPPED: 未成曲调先有情（385 铜奖；用户确认该书已下架 died，全库 roster 无记录）
add(385, "铜奖", "我亲爱的欧米伽小姐")
add(385, "铜奖", "你杀我千千万万遍")

# 对话小说 -> 386（名单 5 条，1 条待确认跳过，导入 4）
add(386, "金奖", "拯救计划")
add(386, "银奖", "心理咨询室")
add(386, "铜奖", "来自未来的她名叫小鹿酱")
# SKIPPED: 死去的女友忽然发来消息（386 铜奖；用户确认该书已下架 died，全库 roster 仅有相近作「死去的女友以诡异的姿态归来了！」等，非同一本）
add(386, "铜奖", "極上無限超絕亂武默示錄")

SOURCE = "官方 App 公示「第六届夏征奖」（用户提供 2026-11-24）"
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
