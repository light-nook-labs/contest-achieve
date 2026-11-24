"""导入第三届夏征（三征）获奖名单。

来源：SF 官方公示「第三届SF原创轻小说征文大赛，奖项公布！」
https://news.sfacg.com/Files/2015-12-15/f92f9252-2158-46b4-9459-67fa02b4428f.shtml
三征按奖项档位拆成 9 个赛道（641-649），每个赛道收录对应档位作品：
  641 长篇金 / 642 长篇银 / 643 长篇铜 / 644 中篇金 / 645 中篇银 / 646 中篇铜
  647 短篇金 / 648 短篇银 / 649 短篇铜
15 条获奖中 13 条在对应档位赛道 roster 精确命中；
2 条（42757、44541）不在目标档位赛道，由全库 roster 提供 nid/作者佐证，
按四征冬征先例在 note 标注例外写入。按 (nid, award) 去重，幂等可重跑。
"""

import json
import os

SOURCE = "SF 官方公示「第三届SF原创轻小说征文大赛，奖项公布！」 https://news.sfacg.com/Files/2015-12-15/f92f9252-2158-46b4-9459-67fa02b4428f.shtml"
VERIFIED_AT = "2026-11-24"

# (赛道 ID, 奖项, 名单书名, roster 书名, 例外备注)
ROWS = [
    # 长篇
    (641, "金奖", "暗杀失败的他反而变成了她骑士？", "暗杀失败的他反而变成了她骑士？", ""),
    (642, "银奖", "剑仙同桌俏剑灵", "剑仙同桌俏剑灵", ""),
    (643, "铜奖", "机键圣母", "机键圣母", ""),
    (643, "铜奖", "承诺之地", "承诺之地", ""),
    (643, "铜奖", "作为神的我并非没有烦恼", "作为神的我并非没有烦恼",
     "官方公示长篇铜奖；该书不在 643 档位赛道 roster，全库 roster（赛道 58，作者绘空事丶）佐证 nid 42757，按档位例外写入"),
    # 中篇
    (644, "金奖", "世界倾坠之时", "世界倾坠之时", ""),
    (645, "银奖", "山城皮影", "山城皮影", ""),
    (646, "铜奖", "N+M+X+2的突破", "N+M+X+2的突破", ""),
    # 短篇
    (647, "金奖", "图灵爱人", "图灵爱人", ""),
    (648, "银奖", "把秒者的爱情", "把秒者的爱情", ""),
    (649, "铜奖", "早安 哥哥 喵", "早安 哥哥 喵", ""),
    (649, "铜奖", "角奴", "角奴", ""),
    (649, "铜奖", "红袍之王", "红袍之王", ""),
    (649, "铜奖", "一眸间的幸福", "一眸间的幸福", ""),
    (649, "铜奖", "林•魂", "林·魂",
     "官方公示短篇铜奖；名单用「•」，roster 用「·」；该书不在 649 档位赛道 roster，全库 roster（赛道 387，作者 lely莫西西）佐证 nid 44541，按档位例外写入"),
]


def roster_index():
    idx = {}
    for p in __import__("glob").glob("data/*/roster.jsonl"):
        for line in open(p, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            idx[str(r.get("nid"))] = r
    return idx


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
    all_roster = roster_index()
    targets = {tid: target_index(tid) for tid in {r[0] for r in ROWS}}
    pending = []
    for tid, award, user_title, roster_title, note in ROWS:
        r = targets[tid].get(roster_title)
        if r:
            nid = str(r["nid"])
            actual = r.get("title", "")
        else:
            # 例外：按名单书名在全库找唯一 nid
            cands = [v for k, v in all_roster.items()
                     if str(v.get("title", "")).strip().strip("《》") in (roster_title, user_title)]
            if not cands:
                print(f"MISS {tid} {award} {user_title}")
                continue
            r = cands[0]
            nid = str(r["nid"])
            actual = r.get("title", "")
        rec = {
            "nid": nid,
            "title": actual,
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
