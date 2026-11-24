#!/usr/bin/env python3
"""导入：五征冬征（466）获奖名单（用户提供，16 条）。

候选见 candidates_466.py。作者不写入 awards.jsonl，按 nid 关联 roster。
导入前检查目标文件：已有记录则中止，避免重复发现导致重复写入。
幂等：按 (nid, award) 复合键去重，重复执行不产生重复行。

注意：早期赛事的 nid 常被后续聚合标签重复收录，因此这里只校验 nid 存在于
目标赛道 roster，而不要求它在全库唯一。
"""
import json
import os

from candidates_466 import CANDIDATES, CONTEST_TRACK_ID, NOTE, SOURCE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-11-24"


def main():
    tid = str(CONTEST_TRACK_ID)
    roster_path = os.path.join(ROOT, "data", tid, "roster.jsonl")
    idx = {}
    with open(roster_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                idx[str(r["nid"])] = r

    rows = []
    for track, award, nid, title in CANDIDATES:
        if str(track) != tid:
            raise SystemExit(f"候选赛道 {track} 与目标 {tid} 不符，中止")
        if str(nid) not in idx:
            raise SystemExit(f"nid {nid} 不在赛道 {tid} roster，中止")
        actual_title = idx[str(nid)]["title"]
        if actual_title != title:
            raise SystemExit(f"nid {nid} 书名不符：候选 {title!r}，roster {actual_title!r}，中止")
        rows.append((nid, title, award))

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
    for nid, title, award in rows:
        key = (str(nid), award)
        if key in by_key:
            r = by_key[key]
            if not r.get("verified") or r.get("source") != SOURCE:
                r.update({"title": title, "verified": True, "verified_at": TODAY,
                          "source": SOURCE, "note": NOTE})
                updated += 1
        else:
            existing.append({
                "nid": str(nid),
                "title": title,
                "award": award,
                "source": SOURCE,
                "verified": True,
                "verified_at": TODAY,
                "note": NOTE,
            })
            added += 1

    with open(path, "w", encoding="utf-8") as f:
        for r in existing:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"赛道 {tid}: 新增 {added}，更新 {updated}，现有 {len(existing)} 条")


if __name__ == "__main__":
    main()
