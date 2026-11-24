"""导入第一届夏征（一征）获奖名单。

来源：用户从官方渠道提供（2026-11-24），未给出公开 URL。
一征按奖项档位拆成 3 个赛道（635 金 / 636 银 / 637 铜），
5 条获奖全部在对应档位赛道 roster 精确命中。
按 (nid, award) 去重，幂等可重跑。
"""

import json
import os

SOURCE = "第一届夏征获奖名单（用户从官方渠道提供 2026-11-24，未给出公开 URL）"
VERIFIED_AT = "2026-11-24"

ROWS = [
    (635, "金奖", "剑魄少女与藏剑少年", "剑魄少女与藏剑少年", ""),
    (636, "银奖", "墓地邪影", "墓地邪影", ""),
    (637, "铜奖", "科嘉西走廊", " 科嘉西走廊", "名单无前导空格，roster 标题带前导空格"),
    (637, "铜奖", "除妖所打工记", "除妖所打工记", ""),
    (637, "铜奖", "比自己更爱你", "比自己更爱你", ""),
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
    for tid, award, user_title, roster_title, note in ROWS:
        r = targets[tid].get(roster_title.strip())
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
