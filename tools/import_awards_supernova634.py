"""导入超新星杯短篇小说征文大赛（634）获奖名单。

来源：用户从官方 App 提供（2026-11-24），活动页 https://pages.sfacg.com/h5/act/zw20230331/
该赛事为投票制，名次并列：第1名 1 本、第2名 2 本、第3名 3 本。
6 条全部在 634 roster 精确命中。按 (nid, award) 去重，幂等可重跑。
"""

import json
import os

SOURCE = "超新星杯短篇小说征文大赛获奖名单（用户从官方 App 提供 2026-11-24，投票制名次并列：第1名1本/第2名2本/第3名3本）"
VERIFIED_AT = "2026-11-24"

# (赛道, 名次/奖项, roster 书名) —— 名次并列
ROWS = [
    (634, "第1名", "下班后，一车叔叔都被变成美少女"),
    (634, "第2名", "我邂逅了变成猫的少女"),
    (634, "第2名", "改变世界的方式有很多"),
    (634, "第3名", "坏叻，怎么只有我在吹牛"),
    (634, "第3名", "孟婆与阎王妹子不得不说的那些事"),
    (634, "第3名", "今天笔仙大人成功索命了吗？"),
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
    for tid, award, roster_title in ROWS:
        r = targets[tid].get(roster_title)
        if not r:
            print(f"MISS {tid} {award} {roster_title}")
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
