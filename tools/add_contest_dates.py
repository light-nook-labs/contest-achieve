#!/usr/bin/env python3
"""为 contests.json 补齐 start_date / end_date / result_date（YYYY-MM-DD，未知留空串）。

只写能在 novly-proj 文档里核对到的日期，不从 nid 定年窗或「系列规律」反推：
  1. analysis/references/contest-editions.md §官方 App 核实的精确日期（用户逐届查询）
     —— 2024 秋 / 八征冬 / 2025 春 / 十三征 / 奇幻世界 / 2025 秋 / 九征冬 / 2026 春。
  2. 同文档 §官方页面确认 —— 四征 rule.html（2016-07-08 → 10-06）、十二征页面 id。
  3. 同文档 §崩坏3 联动征文 —— 网易号官方通稿（2019-01-04 → 02-11，02-22 公示）。
  4. docs/contest-roster-harvest.md §2/§3 —— 活动页 data-firstpublictime、
     日期式页面 id 自证启动日（春征 03-01 / X 征 05-04 / 秋征 09-30 / 冬征日期式）、
     聚合站佐证的征稿起止与公示日期（722、755）。

同一赛事的多个赛道共享日期。幂等：只填空字段，不覆盖已有值（人工修正优先）。

用法：uv run python tools/add_contest_dates.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "contests.json")
FIELDS = ("start_date", "end_date", "result_date")

DATES = {}


def add(ids, start="", end="", result=""):
    for contest_track_id in ids:
        DATES[contest_track_id] = (start, end, result)


# 四征：官方规则页 book.sfacg.com/zw2016/rule.html
add((275, 276, 277), "2016-07-08", "2016-10-06")

# 崩坏3 × SF 同人征文：网易号官方通稿 2019-01-04
add((405,), "2019-01-04", "2019-02-11", "2019-02-22")

# 春征：日期式活动页 zwYYYY0301，启动日 03-01（页面实证）
add((473,), "2022-03-01")
add((632,), "2023-03-01")
add((699,), "2024-03-01")

# 秋征主题制：日期式活动页 zwYYYY0930，启动日 09-30（页面实证）
add((481,), "2022-09-30")
add((669,), "2023-09-30")

# 冬征：日期式活动页自证启动日
add((485,), "2022-12-05")
add((692,), "2023-12-04")

# X 征：日期式活动页 zwYYYY0504，启动日 05-04（页面 id 自证）
add((653, 654, 655), "2023-05-04")
add((702, 703, 704), "2024-05-04")

# 以下 8 组来自 App 逐届核实的完整赛程
add((725,), "2024-09-30", "2024-12-05")
add((726,), "2024-12-06", "2025-02-28")
add((746,), "2025-03-01", "2025-05-03", "2025-07-11")
add((752, 753, 754), "2025-05-04", "2025-10-07", "2026-01-16")
add((755,), "2025-06-06", "2025-08-31", "2025-11-28")
add((772,), "2025-09-30", "2025-12-04")
add((774,), "2025-12-05", "2026-03-06")
add((789,), "2026-02-27", "2026-05-03", "2026-07-10")

# 活动页 data-firstpublictime / 聚合站佐证
add((722,), "2024-06-21", "2024-08-31", "2024-10-25")
add((724,), result="2024-11-15")
add((747, 748), result="2025-07-11")

# 用户从官方 App 提供的赛程（2026-11-24）
# 十四征此前按页面 id 反推为 05-04，已按 App 修正
add((793, 794), "2026-05-01", "2026-10-07", "2027-01-15")
add((803,), "2026-09-29", "2026-12-03", "2027-02-16")
# 九征四赛道（457/458/459/462）共用赛程
add((457, 458, 459, 462), "2021-05-14", "2021-10-07", "2022-01-14")
# 八征三赛道（418/419/420）共用赛程
add((418, 419, 420), "2020-05-17", "2020-10-07", "2021-01-15")
# 七征五赛道（408-412）共用赛程
add((408, 409, 410, 411, 412), "2019-05-25", "2019-09-24", "2019-12-24")
# 六征四赛道（383-386）共用赛程
add((383, 384, 385, 386), "2018-07-05", "2018-10-05", "2018-12-03")
# 五征四赛道（377-380）共用赛程
add((377, 378, 379, 380), "2017-07-07", "2017-10-07", "2017-12-15")
# 四征三赛道（275-277）共用赛程（起止已在 novly-proj 规则页核实，此处补公布日）
add((275, 276, 277), "2016-07-08", "2016-10-06", "2016-12-01")
# 三征九赛道（641-649，按奖项档位拆分）：公示日由官方公示页日期确认，起止待 App 补充
add((641, 642, 643, 644, 645, 646, 647, 648, 649), result="2015-12-15")


def main():
    with open(PATH, encoding="utf-8") as f:
        cfgs = json.load(f)

    filled = 0
    touched = set()
    for cfg in cfgs:
        for field in FIELDS:
            cfg.setdefault(field, "")
        values = DATES.get(cfg["contest_track_id"])
        if not values:
            continue
        for field, value in zip(FIELDS, values):
            if value and not cfg[field]:
                cfg[field] = value
                filled += 1
                touched.add(cfg["contest_track_id"])

    with open(PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cfgs, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"已填 {filled} 个日期字段，涉及 {len(touched)} 个赛道；"
          f"共 {len(cfgs)} 条赛道记录。")


if __name__ == "__main__":
    main()
