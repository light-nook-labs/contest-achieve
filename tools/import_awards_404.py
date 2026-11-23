#!/usr/bin/env python3
"""导入：少女前线征文（404）获奖公示（共 8 部，用户目视确认）。

来源：https://pages.sfacg.com/h5/act/sfxsq/
奖项：一等奖 1（你是我的军旗）；二等奖 2（突袭者的守望、少女前线的幻觉之痛）；
      三等奖 5（时至今日少女们仍在努力着、少女与枪与指挥官、铁血的远征、
                Contrast、烙印）。
候选见 candidates_404.py。

幂等：按 (nid, award) 复合键去重，重复执行不产生重复行；已存在记录不回退。
"""
import json
import os

from candidates_404 import CANDIDATES, SOURCE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-11-23"


def roster_index():
    idx = {}
    for name in os.listdir(os.path.join(ROOT, "data")):
        path = os.path.join(ROOT, "data", name, "roster.jsonl")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    idx[str(r["nid"])] = (r["title"], name)
    return idx


def main():
    idx = roster_index()
    by_track = {}
    for tid, award, nid in CANDIDATES:
        if str(nid) not in idx:
            raise SystemExit(f"nid {nid} 不在 roster，中止")
        title, real_track = idx[str(nid)]
        if str(real_track) != str(tid):
            raise SystemExit(f"nid {nid} 属赛道 {real_track}，与声明 {tid} 不符，中止")
        by_track.setdefault(str(tid), []).append((nid, title, award))

    for tid, rows in by_track.items():
        path = os.path.join(ROOT, "data", tid, "awards.jsonl")
        existing = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                existing = [json.loads(line) for line in f if line.strip()]
        by_key = {(str(r["nid"]), r.get("award")): r for r in existing}

        added = updated = 0
        for nid, title, award in rows:
            key = (str(nid), award)
            if key in by_key:
                r = by_key[key]
                if not r.get("verified") or r.get("source") != SOURCE:
                    r.update({"title": title, "verified": True, "verified_at": TODAY,
                              "source": SOURCE, "note": ""})
                    updated += 1
            else:
                existing.append({
                    "nid": nid,
                    "title": title,
                    "award": award,
                    "source": SOURCE,
                    "verified": True,
                    "verified_at": TODAY,
                    "note": "",
                })
                added += 1

        with open(path, "w", encoding="utf-8") as f:
            for r in existing:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        print(f"赛道 {tid}: 新增 {added}，更新 {updated}，现有 {len(existing)} 条")


if __name__ == "__main__":
    main()
