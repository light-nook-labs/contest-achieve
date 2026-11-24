#!/usr/bin/env python3
"""导入：四征冬征（454）获奖名单（用户提供，16 条）。

候选见 candidates_454.py。作者不写入 awards.jsonl，按 nid 关联 roster。
导入前检查目标文件：已有记录则中止，避免重复发现导致重复写入。
幂等：按 (nid, award) 复合键去重，重复执行不产生重复行。

早期 nid 常被后续聚合标签重复收录，因此这里只校验 nid 在目标赛道 roster；
ROSTER_EXCEPTIONS 中的 2 条单独校验全库 nid/作者，并在 note 中标注例外。
"""
import json
import os
import sys

from candidates_454 import (
    AUTHORS, CANDIDATES, CONTEST_TRACK_ID, NOTE, ROSTER_EXCEPTIONS, SOURCE,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-11-24"


def load_roster(path):
    idx = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                idx[str(r["nid"])] = r
    return idx


def main():
    tid = str(CONTEST_TRACK_ID)
    target = load_roster(os.path.join(ROOT, "data", tid, "roster.jsonl"))
    # 例外条目需从全库找到 nid/作者佐证；只收集候选 nid，避免载入全部清单到内存。
    wanted = {str(nid) for _, _, nid, _ in CANDIDATES if int(nid) in ROSTER_EXCEPTIONS}
    global_idx = {}
    for name in os.listdir(os.path.join(ROOT, "data")):
        path = os.path.join(ROOT, "data", name, "roster.jsonl")
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            if str(r["nid"]) in wanted:
                global_idx[str(r["nid"])] = r

    rows = []
    for track, award, nid, title in CANDIDATES:
        if str(track) != tid:
            raise SystemExit(f"候选赛道 {track} 与目标 {tid} 不符，中止")
        key = str(nid)
        in_target = key in target
        if not in_target and int(nid) not in ROSTER_EXCEPTIONS:
            raise SystemExit(f"nid {nid} 不在赛道 {tid} roster 且未登记例外，中止")
        ref = target.get(key) or global_idx.get(key)
        if not ref:
            raise SystemExit(f"nid {nid} 在全库 roster 中也找不到，中止")
        if ref["title"] != title:
            raise SystemExit(f"nid {nid} 书名不符：候选 {title!r}，roster {ref['title']!r}，中止")
        if ref.get("author") != AUTHORS.get(nid):
            raise SystemExit(f"nid {nid} 作者不符：候选 {AUTHORS.get(nid)!r}，roster {ref.get('author')!r}，中止")
        note = NOTE if in_target else NOTE + "；" + ROSTER_EXCEPTIONS[nid]
        rows.append((nid, title, award, note))

    path = os.path.join(ROOT, "data", tid, "awards.jsonl")
    existing = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = [json.loads(line) for line in f if line.strip()]
    if existing:
        print(f"警告：赛道 {tid} 已有 {len(existing)} 条获奖记录，请人工核对；本次中止。")
        return
    by_key = {(str(r["nid"]), r.get("award")): r for r in existing}

    added = updated = 0
    for nid, title, award, note in rows:
        key = (str(nid), award)
        if key in by_key:
            r = by_key[key]
            if not r.get("verified") or r.get("source") != SOURCE:
                r.update({"title": title, "verified": True, "verified_at": TODAY,
                          "source": SOURCE, "note": note})
                updated += 1
        else:
            existing.append({
                "nid": str(nid),
                "title": title,
                "award": award,
                "source": SOURCE,
                "verified": True,
                "verified_at": TODAY,
                "note": note,
            })
            added += 1

    with open(path, "w", encoding="utf-8") as f:
        for r in existing:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"赛道 {tid}: 新增 {added}，更新 {updated}，现有 {len(existing)} 条")


if __name__ == "__main__":
    main()
