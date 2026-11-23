#!/usr/bin/env python3
"""校验归档格式：contests.json 覆盖、roster schema、awards schema、meta 完整性。

默认只校验已采集（有 roster.jsonl）的赛事；--strict 要求全部 100 个赛事都已采集。
awards 独立校验，不依赖 roster（获奖可先于清单迁入）。
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
ROSTER_KEYS = {"nid", "title", "author", "form_id", "intro", "cover"}
AWARD_REQUIRED = {"nid", "title", "award", "source", "verified"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="要求全部赛事已采集")
    args = ap.parse_args()

    cfgs = json.load(open(os.path.join(ROOT, "contests.json"), encoding="utf-8"))
    errors = []
    total_roster = 0
    total_awards = 0
    seen_tags = set()
    collected = 0

    for cfg in cfgs:
        tag = cfg["contest_track_id"]
        seen_tags.add(tag)
        d = os.path.join(DATA, str(tag))
        roster = os.path.join(d, "roster.jsonl")
        meta_path = os.path.join(d, "meta.json")
        awards = os.path.join(d, "awards.jsonl")

        # 清单：有则校验，无则按需报错
        has_roster = os.path.exists(roster)
        if has_roster:
            collected += 1
            if not os.path.exists(meta_path):
                errors.append(f"tag {tag}: 缺 meta.json")
            nids = set()
            for i, line in enumerate(open(roster, encoding="utf-8"), 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except Exception as e:
                    errors.append(f"tag {tag} roster L{i}: JSON 错误 {e}")
                    continue
                if set(row.keys()) != ROSTER_KEYS:
                    errors.append(f"tag {tag} roster L{i}: 字段不符 {sorted(row.keys())}")
                if not isinstance(row.get("nid"), int) or row["nid"] <= 0:
                    errors.append(f"tag {tag} roster L{i}: nid 非法")
                if row.get("nid") in nids:
                    errors.append(f"tag {tag} roster L{i}: nid 重复 {row['nid']}")
                nids.add(row.get("nid"))
                total_roster += 1
            if os.path.exists(meta_path):
                try:
                    meta = json.load(open(meta_path, encoding="utf-8"))
                    if meta.get("contest_track_id") != tag:
                        errors.append(f"tag {tag}: meta.contest_track_id 不符")
                    if not meta.get("snapshots"):
                        errors.append(f"tag {tag}: meta 无快照")
                except Exception as e:
                    errors.append(f"tag {tag}: meta JSON 错误 {e}")
        elif args.strict:
            errors.append(f"tag {tag}: 缺 roster.jsonl")

        # 获奖：独立校验
        if os.path.exists(awards):
            for i, line in enumerate(open(awards, encoding="utf-8"), 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except Exception as e:
                    errors.append(f"tag {tag} awards L{i}: JSON 错误 {e}")
                    continue
                if not AWARD_REQUIRED.issubset(row.keys()):
                    errors.append(f"tag {tag} awards L{i}: 缺必填字段")
                if not isinstance(row.get("verified"), bool):
                    errors.append(f"tag {tag} awards L{i}: verified 非 bool")
                total_awards += 1

    expected = {c["contest_track_id"] for c in cfgs}
    if seen_tags != expected:
        errors.append("注册表 tag 不完整")

    print(f"已采集赛事 {collected}/{len(expected)}，清单 {total_roster} 条，获奖 {total_awards} 条")
    if errors:
        print(f"发现 {len(errors)} 个错误：", file=sys.stderr)
        for e in errors[:50]:
            print("  -", e, file=sys.stderr)
        sys.exit(1)
    print("校验通过")


if __name__ == "__main__":
    main()
