#!/usr/bin/env python3
"""春季/秋季征文获奖候选清单 —— 供人工核对，不写入 awards.jsonl。

来源：各赛事活动页「获奖公示」tab。这些页面没有中间跳转页，公示数据直接
可解析：
- UUID 页（746/789/725/772）：纯静态 HTML，奖项写在图片 alt 属性
  （如 alt="02金奖.jpg"），nid 在 data-nid。
- 老页面（669/699）：Vue SPA，JS bundle 里 status==2 的 reward-list 区块，
  奖项由图片文件名（669: alt 文字；699: n1/n2/n3/n4/n5 档位）确定。

注意：
- 473/632/481 三个页面无获奖公示区块（632 无 reward 区块，473/481 为纯静态
  且无获奖文字），暂不产出候选。
- 669「题材鼓励奖」段存在 3 个与前面重复的 nid（672431/669124/670405），
  疑为模板热区坐标复用，需人工目视确认，不自动写入。
- 699 的 697258 图片映射缺失，按版位推断为推荐奖首部，需人工确认。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# UUID 页：(track, award, nid) —— 从 data-nid + img alt 精确提取
UUID_AWARDS = [
    # 746 2025春征 — essayActivity_d892261b
    (746, "金奖", 738162), (746, "银奖", 740593),
    (746, "铜奖", 737435), (746, "铜奖", 738492), (746, "铜奖", 738770),
    (746, "推荐奖", 739670), (746, "推荐奖", 739112), (746, "推荐奖", 737766),
    (746, "推荐奖", 737409), (746, "推荐奖", 741973),
    # 789 2026春征 — essayActivity_52f25c52
    (789, "金奖", 774528), (789, "银奖", 770804), (789, "铜奖", 772261),
    (789, "新人奖", 771720), (789, "新人奖", 774426), (789, "新人奖", 770340),
    # 725 2024秋征 — essayActivity_0a10b388
    (725, "金奖", 720699), (725, "银奖", 721779),
    (725, "铜奖", 727388), (725, "铜奖", 724273), (725, "铜奖", 720532),
    (725, "推荐奖", 722484), (725, "推荐奖", 723128), (725, "推荐奖", 722600),
    (725, "星火奖", 726385), (725, "星火奖", 724040), (725, "星火奖", 724589),
    # 772 2025秋征 — essayActivity_d568a583
    (772, "金奖", 759314), (772, "银奖", 760079),
    (772, "铜奖", 762215), (772, "铜奖", 759671),
    (772, "新人奖", 759738), (772, "新人奖", 763251), (772, "新人奖", 760981),
]

# 669 2023主题秋征 — zw20230930（status==2 reward-list）
AWARDS_669 = [
    (669, "金奖", 670734),
    (669, "银奖", 667702), (669, "银奖", 667704),
    (669, "铜奖", 668238), (669, "铜奖", 672431), (669, "铜奖", 669124),
    (669, "编辑推荐奖", 669905), (669, "编辑推荐奖", 675093), (669, "编辑推荐奖", 670405),
    (669, "编辑推荐奖", 668466), (669, "编辑推荐奖", 672498),
    (669, "星火奖", 670655), (669, "星火奖", 667902), (669, "星火奖", 671035),
    (669, "星火奖", 670423), (669, "星火奖", 674563),
    # 题材鼓励奖：前 3 个 nid 与铜奖/编辑推荐重复，需人工确认
    (669, "题材鼓励奖", 672431), (669, "题材鼓励奖", 669124), (669, "题材鼓励奖", 670405),
    (669, "题材鼓励奖", 672560), (669, "题材鼓励奖", 672592),
]

# 699 2024春征 — zw20240301（图片名 n1~n5 分档）
AWARDS_699 = [
    (699, "金奖", 692762),
    (699, "银奖", 694027), (699, "银奖", 696781),
    (699, "铜奖", 696732), (699, "铜奖", 695213), (699, "铜奖", 693131),
    # 697258 图片 n4-1 映射缺失，按版位推断为推荐奖
    (699, "推荐奖", 697258), (699, "推荐奖", 694785), (699, "推荐奖", 691082),
    (699, "推荐奖", 691006), (699, "推荐奖", 693020),
    (699, "星火奖", 690983), (699, "星火奖", 691059), (699, "星火奖", 691457),
    (699, "星火奖", 691218), (699, "星火奖", 690939),
]

SOURCES = {
    669: "https://pages.sfacg.com/h5/act/zw20230930/",
    699: "https://pages.sfacg.com/h5/act/zw20240301/",
    746: "https://pages.sfacg.com/h5/act/zw/essayActivity_d892261b-8719-4e3b-b01a-b84278b2996b.html",
    789: "https://pages.sfacg.com/h5/act/zw/essayActivity_52f25c52-1de0-4608-90fc-293aac35a588.html",
    725: "https://pages.sfacg.com/h5/act/zw/essayActivity_0a10b388-bf92-410c-801a-59c91b853c3f.html",
    772: "https://pages.sfacg.com/h5/act/zw/essayActivity_d568a583-bde8-4f16-809a-8ab7097261be.html",
}

ALL = UUID_AWARDS + AWARDS_669 + AWARDS_699


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
                    idx[str(r["nid"])] = (r["title"], r["author"], name)
    return idx


def main():
    idx = roster_index()
    from collections import defaultdict
    by = defaultdict(list)
    for tid, award, nid in ALL:
        by[tid].append((award, nid))
    for tid in sorted(by):
        m = json.load(open(os.path.join(ROOT, "data", str(tid), "meta.json"), encoding="utf-8"))
        print(f"\n===== {tid} {m['contest_name']}  ({len(by[tid])} 条)")
        print(f"  {SOURCES[tid]}")
        for award, nid in by[tid]:
            r = idx.get(str(nid))
            if r:
                print(f"  {award:<8} {nid:<8} {r[0][:24]:26} {r[1][:10]:12} [roster {r[2]}]")
            else:
                print(f"  {award:<8} {nid:<8} {'!!! roster 缺失':26}")
    print(f"\n合计 {len(ALL)} 条候选")


if __name__ == "__main__":
    main()
