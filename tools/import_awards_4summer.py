"""导入第四届夏征（四征）获奖名单。

来源：网易新闻官方通稿「第四届SF原创轻小说征文大赛圆满落幕」
https://m.163.com/news/article/C7OPAKFR00014JB5.html?spss=adap_pc
该通稿只列出三个金奖（长/中/短各一），无银奖/铜奖等其他档位。
按书名在对应赛道 roster 中核对 nid；按 (nid, award) 去重，幂等可重跑。
"""

import json
import os

# (赛道 ID, 奖项, 名单书名, roster 实际书名, 备注)
ROWS = [
    (275, "金奖", "深蓝公主伊莉娜", "深蓝公主伊莉娜", ""),
    (276, "金奖", "希瓦计划", "希瓦计划", ""),
    (277, "金奖", "种人小正是大家的希望!!!", "种人小正是大家的希望！！！", "通稿用半角感叹号，roster 为全角"),
]

SOURCE = "网易新闻官方通稿「第四届SF原创轻小说征文大赛圆满落幕」 https://m.163.com/news/article/C7OPAKFR00014JB5.html?spss=adap_pc"
VERIFIED_AT = "2026-11-24"


def main():
    by_tid = {}
    for tid, award, user_title, actual, note in ROWS:
        idx = {}
        path = f"data/{tid}/roster.jsonl"
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            idx[str(r.get("title", "")).strip().strip("《》")] = r
        r = idx.get(actual)
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
        by_tid.setdefault(tid, []).append(rec)

    added = {}
    for tid, recs in by_tid.items():
        path = f"data/{tid}/awards.jsonl"
        seen = set()
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                if line.strip():
                    a = json.loads(line)
                    seen.add((str(a.get("nid")), a.get("award")))
        n = 0
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            for rec in recs:
                key = (rec["nid"], rec["award"])
                if key in seen:
                    continue
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                seen.add(key)
                n += 1
        if n:
            added[tid] = n

    print("新增:", dict(sorted(added.items())))
    print("合计:", sum(added.values()))


if __name__ == "__main__":
    main()
