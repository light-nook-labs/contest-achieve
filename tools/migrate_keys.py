#!/usr/bin/env python3
"""一次性迁移：只改需要改的键，保留简洁键名。

最终目标 schema：
  roster.jsonl  : nid, title, author, form_id, intro, cover
                  （category_id → form_id；其余保持原始简洁键）
  awards.jsonl  : nid, title, award, source, verified, verified_at, note
                  （全部保持原始键名）
  contests.json : contest_track_id, contest_name, series, api_generation, page_start, url_template
  meta.json     : 同上 + snapshots（total_pages, fetched_pages, novel_count, captured_at, sha256）

本脚本幂等，既能从原始状态迁移，也能修正上一版过度改名留下的键。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def apply_map(row, mapping):
    """按 mapping 改名；mapping: old -> new。返回是否改动。"""
    changed = False
    for old, new in mapping.items():
        if old in row and old != new:
            row[new] = row.pop(old)
            changed = True
    return changed


def migrate_contests():
    path = os.path.join(ROOT, "contests.json")
    rows = load_json(path)
    mapping = {"tag": "contest_track_id", "name": "contest_name", "endpoint": "api_generation", "url": "url_template"}
    changed_any = False
    for row in rows:
        changed = apply_map(row, mapping)
        if "api_generation" in row:
            vals = {"old": "legacy", "new": "modern"}
            if row["api_generation"] in vals:
                row["api_generation"] = vals[row["api_generation"]]
                changed = True
        if "{tag}" in row.get("url_template", ""):
            row["url_template"] = row["url_template"].replace("{tag}", "{contest_track_id}")
            changed = True
        changed_any |= changed
    if changed_any:
        dump_json(path, rows)
    return changed_any


def migrate_meta_files():
    changed_any = False
    mapping = {"tag": "contest_track_id", "name": "contest_name", "endpoint": "api_generation", "url": "url_template"}
    snap_mapping = {"total_page": "total_pages", "pages": "fetched_pages", "count": "novel_count"}
    for name in os.listdir(os.path.join(ROOT, "data")):
        path = os.path.join(ROOT, "data", name, "meta.json")
        if not os.path.exists(path):
            continue
        meta = load_json(path)
        changed = apply_map(meta, mapping)
        if "api_generation" in meta:
            vals = {"old": "legacy", "new": "modern"}
            if meta["api_generation"] in vals:
                meta["api_generation"] = vals[meta["api_generation"]]
                changed = True
        if "{tag}" in meta.get("url_template", ""):
            meta["url_template"] = meta["url_template"].replace("{tag}", "{contest_track_id}")
            changed = True
        for snap in meta.get("snapshots", []):
            changed |= apply_map(snap, snap_mapping)
        if changed:
            dump_json(path, meta)
            changed_any = True
    return changed_any


def migrate_jsonl(filename, mapping, required):
    changed_any = False
    for name in os.listdir(os.path.join(ROOT, "data")):
        path = os.path.join(ROOT, "data", name, filename)
        if not os.path.exists(path):
            continue
        rows = []
        changed = False
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                changed |= apply_map(row, mapping)
                rows.append(row)
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                for row in rows:
                    ordered = {k: row[k] for k in required if k in row}
                    for k, v in row.items():
                        if k not in ordered:
                            ordered[k] = v
                    f.write(json.dumps(ordered, ensure_ascii=False, separators=(",", ":")) + "\n")
            changed_any = True
    return changed_any


def main():
    results = {
        "contests.json": migrate_contests(),
        "meta.json": migrate_meta_files(),
        "roster.jsonl": migrate_jsonl(
            "roster.jsonl",
            {
                "category_id": "form_id",
                "novel_id": "nid",
                "novel_name": "title",
                "author_name": "author",
                "introduction": "intro",
                "cover_url": "cover",
            },
            ["nid", "title", "author", "form_id", "intro", "cover"],
        ),
        "awards.jsonl": migrate_jsonl(
            "awards.jsonl",
            {
                "novel_id": "nid",
                "novel_name": "title",
                "award_name": "award",
                "evidence_source": "source",
                "is_verified": "verified",
            },
            ["nid", "title", "award", "source", "verified", "verified_at", "note"],
        ),
    }
    for label, changed in results.items():
        print(f"{label}: {'已调整' if changed else '无需调整（已是目标键名）'}")
    if not any(results.values()):
        print("全部已是目标键名。", file=sys.stderr)


if __name__ == "__main__":
    main()
