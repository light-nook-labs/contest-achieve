#!/usr/bin/env python3
"""一次性迁移：给 contests.json 每条赛道补 activity_url（官方活动页地址）。

数据来源（唯一权威台账）：
  novly-proj/docs/contest-roster-harvest.md §2「活动页 URL 台账」+ §3「URL 命名规律」
  该文档是逐届页面实证的 tagId/URL 权威；本脚本把「同一活动页 URL」映射到
  该届下的每个赛道（一届多赛道共用一张活动页）。

字段语义：
  activity_url = 该赛道所属赛事的官方活动页地址（看参赛展/获奖公示的页面）；
  与 url_template（清单 API 模板）不同。页面下线/未取到的留空字符串 ""，
  不臆造 URL。

幂等：重复运行不会改变结果。
用法：uv run python tools/add_activity_urls.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTESTS = os.path.join(ROOT, "contests.json")

# 活动页 URL → 该页面覆盖的赛道 ID（同一届的长/中/短/对话赛道共用一张页）
PAGES = [
    # X 征（夏季主线）
    ("https://book.sfacg.com/zw2016/", [275, 276, 277]),
    ("https://book.sfacg.com/zw2017/", [377, 378, 379, 380]),
    ("https://pages.sfacg.com/h5/act/zw2018/", [383, 384, 385, 386]),
    ("https://pages.sfacg.com/h5/act/zw2019/", [408, 409, 410, 411, 412]),
    ("https://pages.sfacg.com/h5/act/zw2020/", [418, 419, 420]),
    ("https://pages.sfacg.com/h5/act/zw2021/", [457, 458, 459, 462]),
    ("https://pages.sfacg.com/h5/act/zw2022/", [475, 476, 477, 479]),
    ("https://pages.sfacg.com/h5/act/zw20230504/pc", [653, 654, 655]),
    ("https://pages.sfacg.com/h5/act/zw20240504/pc", [702, 703, 704]),
    ("https://pages.sfacg.com/h5/act/zw20250504/pc", [752, 753, 754]),
    ("https://pages.sfacg.com/h5/act/zw20260504/pc", [793, 794]),
    # 冬征
    ("https://pages.sfacg.com/h5/act/djzw2018/", [381]),
    ("https://pages.sfacg.com/h5/act/djzw2019/", [406]),
    ("https://pages.sfacg.com/h5/act/djzw2020/", [415]),
    ("https://pages.sfacg.com/pc/act/djzw2021/", [454]),
    ("https://pages.sfacg.com/h5/act/djzw2022/", [466]),
    ("https://pages.sfacg.com/h5/act/zw20221205/", [485]),
    ("https://pages.sfacg.com/h5/act/zw20231204/", [692]),
    ("https://pages.sfacg.com/h5/act/zw/essayActivity_c49534b9-73b2-46c9-a33f-b8144b448662.html", [726]),
    ("https://pages.sfacg.com/h5/act/zw/essayActivity_373481c3-8fb0-4113-83fb-5058a816f828.html", [774]),
    # 春征
    ("https://pages.sfacg.com/h5/act/zw20220301/", [473]),
    ("https://pages.sfacg.com/h5/act/zw20230301/", [632]),
    ("https://pages.sfacg.com/h5/act/zw20240301/", [699]),
    ("https://pages.sfacg.com/h5/act/zw/essayActivity_d892261b-8719-4e3b-b01a-b84278b2996b.html", [746]),
    ("https://pages.sfacg.com/h5/act/zw/essayActivity_52f25c52-1de0-4608-90fc-293aac35a588.html", [789]),
    # 秋征（主题制）
    ("https://pages.sfacg.com/h5/act/zw20220930/", [481]),
    ("https://pages.sfacg.com/h5/act/zw20230930/", [669]),
    ("https://pages.sfacg.com/h5/act/zw/essayActivity_0a10b388-bf92-410c-801a-59c91b853c3f.html", [725]),
    ("https://pages.sfacg.com/h5/act/zw/essayActivity_d568a583-bde8-4f16-809a-8ab7097261be.html", [772]),
    # 少年主题
    ("https://pages.sfacg.com/h5/act/zw/essayActivity_7465fc4b-8c7e-4e23-a30c-721ec33ced8b.html", [722]),
    ("https://pages.sfacg.com/h5/act/zw/essayActivity_775951e5-ac60-4df4-a8d3-4ffb64173398.html", [747, 748]),
    # 独立主题
    ("https://pages.sfacg.com/h5/act/zw/essayActivity_e5950dc7-7f12-4fca-8049-8fd2afd9c0eb.html", [755]),
    # 对话线
    ("https://pages.sfacg.com/h5/act/zw/essayActivity_c7ff7adf-4f9d-416d-a5e0-796683eb6763.html", [724]),
]


def build_map():
    mapping = {}
    for url, tags in PAGES:
        for tag in tags:
            if tag in mapping:
                raise SystemExit(f"赛道 {tag} 重复映射到两个活动页")
            mapping[tag] = url
    return mapping


def main():
    url_by_tag = build_map()
    rows = json.load(open(CONTESTS, encoding="utf-8"))
    known = {r["contest_track_id"] for r in rows}

    stray = set(url_by_tag) - known
    if stray:
        print(f"警告：台账中的赛道未注册，忽略 {sorted(stray)}")

    changed = 0
    for row in rows:
        tag = row["contest_track_id"]
        value = url_by_tag.get(tag, "")
        if row.get("activity_url") != value:
            row["activity_url"] = value
            changed += 1
        # 保持字段顺序稳定：activity_url 紧跟 url_template
        order = ["contest_track_id", "contest_name", "series", "api_generation",
                 "page_start", "url_template", "activity_url"]
        row_ordered = {k: row[k] for k in order if k in row}
        for k, v in row.items():
            if k not in row_ordered:
                row_ordered[k] = v
        row.clear()
        row.update(row_ordered)

    with open(CONTESTS, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
        f.write("\n")

    filled = sum(1 for r in rows if r.get("activity_url"))
    print(f"contests.json：{len(rows)} 条赛道，{filled} 条有活动页 URL，"
          f"{len(rows) - filled} 条页面下线/未取（留空）；本次改动 {changed} 条。")


if __name__ == "__main__":
    main()
