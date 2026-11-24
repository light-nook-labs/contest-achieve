"""导入第二届夏征（二征）获奖名单。

来源：用户从官方渠道提供（2026-11-24），未给出公开 URL。
二征按奖项档位拆成 3 个赛道（638 金 / 639 银 / 640 铜），
8 条获奖全部在对应档位赛道 roster 精确命中。
按 (nid, award) 去重，幂等可重跑。
"""

import json
import os

SOURCE = "第二届夏征获奖名单（用户从官方渠道提供 2026-11-24，未给出公开 URL）"
VERIFIED_AT = "2026-11-24"

ROWS = [
    (638, "金奖", "法辛幻想物语", "法辛幻想物语"),
    (639, "银奖", "带我走吧 稻草人", "带我走吧 稻草人"),
    (639, "银奖", "星汉之间", "星汉之间"),
    (640, "铜奖", "落樱之剑", "落樱之剑"),
    (640, "铜奖", "思想品德俱乐部", "思想品德俱乐部"),
    (640, "铜奖", "奇想绘界", "奇想绘界"),
    (640, "铜奖", "追忆曾经被我们杀死的那个女孩", "追忆曾经被我们杀死的那个女孩"),
]


def target_index(tid):
    idx = {}
    p = f"data/{tid}/roster.jsonl"
    if not os.path.exists(p):
        return idx
    for line in open(p, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        idx[str(r.get("title", "")).strip().strip("《》")] = r
    return idx


def main():
    targets = {tid: target_index(tid) for tid in {r[0] for r in ROWS}}
    pending = []
    for tid, award, user_title, roster_title in ROWS:
        r = targets[tid].get(roster_title)
        if not r:
            print(f"MISS {tid} {award} {user_title} (lookup={roster_title})")
            continue
        rec = {
            "nid": str(r["nid"]),
            "title": r.get("title", ""),
            "award": award,
            "source": SOURCE,
            "verified": True,
            "verified_at": VERIFIED_AT,
        }
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
