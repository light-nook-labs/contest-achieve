#!/usr/bin/env python3
"""导入：非 X 征 / 非春秋征文 官网获奖公示的 97 部获奖作品。

来源（人工目视核对确认，见 tools/candidates_other.py）：
- UUID 静态页（774/722/747/748/755/726/724）：data-nid + 图片 alt 奖项标注
- 旧 SPA 页（692/485）：JS 内嵌获奖热区 + 分档标题图

奖项、作品名、作者来自公示页目视核对，nid 已与 roster.jsonl 交叉验证。
708175 / 731965 未进入采集清单，取自公示卡片，note 已标注。

幂等：按 (nid, award) 复合键去重（669 类同 nid 多奖项需保留），重复执行不产生重复行。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-11-23"

SOURCES = {
    "774": "https://pages.sfacg.com/h5/act/zw/essayActivity_373481c3-8fb0-4113-83fb-5058a816f828.html 公示（九征冬征，人工目视核对）",
    "722": "https://pages.sfacg.com/h5/act/zw/essayActivity_7465fc4b-8c7e-4e23-a30c-721ec33ced8b.html 公示（少年·幻想校园，人工目视核对）",
    "747": "https://pages.sfacg.com/h5/act/zw/essayActivity_775951e5-ac60-4df4-a8d3-4ffb64173398.html 公示（少年·二次元创想·长篇，人工目视核对）",
    "748": "https://pages.sfacg.com/h5/act/zw/essayActivity_775951e5-ac60-4df4-a8d3-4ffb64173398.html 公示（少年·二次元创想·短篇，人工目视核对）",
    "755": "https://pages.sfacg.com/h5/act/zw/essayActivity_e5950dc7-7f12-4fca-8049-8fd2afd9c0eb.html 公示（奇幻世界主题征文，人工目视核对）",
    "726": "https://pages.sfacg.com/h5/act/zw/essayActivity_c49534b9-73b2-46c9-a33f-b8144b448662.html 公示（八征冬征，人工目视核对）",
    "724": "https://pages.sfacg.com/h5/act/zw/essayActivity_c7ff7adf-4f9d-416d-a5e0-796683eb6763.html 公示（点鸭·秋色回忆，人工目视核对）",
    "692": "https://pages.sfacg.com/h5/act/zw20231204/ 公示（七征冬征，人工目视核对）",
    "485": "https://pages.sfacg.com/h5/act/zw20221205/ 公示（六征冬征，人工目视核对）",
}

# (contest_track_id, award, nid) —— 与 tools/candidates_other.py 一致
AWARDS = [
    ("774", "金奖", "765752"), ("774", "银奖", "765742"),
    ("774", "铜奖", "765405"), ("774", "铜奖", "764263"), ("774", "铜奖", "767807"),
    ("774", "推荐奖", "764973"), ("774", "推荐奖", "769788"), ("774", "推荐奖", "767294"),
    ("774", "推荐奖", "768408"), ("774", "推荐奖", "766171"),

    ("722", "金奖", "711927"), ("722", "银奖", "708175"), ("722", "银奖", "706926"),
    ("722", "铜奖", "713432"), ("722", "铜奖", "715731"), ("722", "铜奖", "714617"),
    ("722", "推荐奖", "715969"), ("722", "推荐奖", "706700"), ("722", "推荐奖", "712009"),
    ("722", "推荐奖", "709446"), ("722", "推荐奖", "707074"), ("722", "星火奖", "715276"),

    ("747", "金奖", "740306"), ("747", "银奖", "740427"), ("747", "铜奖", "740402"),
    ("747", "推荐奖", "743181"), ("747", "推荐奖", "741013"), ("747", "推荐奖", "739943"),
    ("747", "推荐奖", "740235"), ("747", "推荐奖", "738197"),

    ("748", "金奖", "737829"), ("748", "银奖", "737826"), ("748", "铜奖", "739987"),

    ("755", "金奖", "756478"), ("755", "银奖", "750555"), ("755", "铜奖", "753932"),
    ("755", "推荐奖", "748335"), ("755", "推荐奖", "756296"),

    ("726", "金奖", "730611"), ("726", "银奖", "731325"),
    ("726", "铜奖", "731965"), ("726", "铜奖", "731246"), ("726", "铜奖", "731099"),
    ("726", "编辑推荐奖", "728365"), ("726", "编辑推荐奖", "728392"),
    ("726", "编辑推荐奖", "729846"), ("726", "编辑推荐奖", "729653"),
    ("726", "编辑推荐奖", "729938"),

    ("724", "金奖", "719864"), ("724", "银奖", "723174"), ("724", "银奖", "721897"),
    ("724", "铜奖", "720494"), ("724", "铜奖", "719408"), ("724", "铜奖", "718124"),
    ("724", "编辑推荐奖", "722895"), ("724", "编辑推荐奖", "720819"),
    ("724", "编辑推荐奖", "719494"), ("724", "编辑推荐奖", "721656"),
    ("724", "编辑推荐奖", "719523"), ("724", "编辑推荐奖", "719912"),
    ("724", "编辑推荐奖", "719928"), ("724", "编辑推荐奖", "720013"),
    ("724", "编辑推荐奖", "720327"), ("724", "编辑推荐奖", "719036"),
    ("724", "编辑推荐奖", "719336"), ("724", "编辑推荐奖", "719357"),

    ("692", "金奖", "677177"), ("692", "银奖", "681052"), ("692", "银奖", "689388"),
    ("692", "铜奖", "679145"), ("692", "铜奖", "681376"), ("692", "铜奖", "682171"),
    ("692", "编辑推荐奖", "684584"), ("692", "编辑推荐奖", "681010"),
    ("692", "编辑推荐奖", "684035"), ("692", "编辑推荐奖", "678022"),
    ("692", "编辑推荐奖", "677327"), ("692", "编辑推荐奖", "680606"),
    ("692", "优秀题材奖", "683850"), ("692", "优秀题材奖", "683372"),
    ("692", "优秀题材奖", "684254"),

    ("485", "金奖", "619932"), ("485", "银奖", "607055"), ("485", "银奖", "607090"),
    ("485", "铜奖", "610163"), ("485", "铜奖", "616047"), ("485", "铜奖", "626073"),
    ("485", "编辑推荐奖", "612677"), ("485", "编辑推荐奖", "621313"),
    ("485", "编辑推荐奖", "624389"), ("485", "编辑推荐奖", "614827"),
    ("485", "编辑推荐奖", "621308"), ("485", "编辑推荐奖", "607208"),
    ("485", "创意奖", "607418"), ("485", "创意奖", "607056"),
    ("485", "创意奖", "625069"), ("485", "创意奖", "625033"),
]

# 未进入 roster 的作品，书名/作者取自公示卡片
NOT_IN_ROSTER = {
    "708175": ("重生后就开始养成小女友", "月下樱花树"),
    "731965": ("不是你们夫妻出轨对象怎么都是我", "流心麻糬"),
}


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
    for tid, award, nid in AWARDS:
        if nid in idx:
            title, real_track = idx[nid]
            if str(real_track) != str(tid):
                raise SystemExit(f"nid {nid} 属赛道 {real_track}，与声明 {tid} 不符，中止")
        else:
            if nid not in NOT_IN_ROSTER:
                raise SystemExit(f"nid {nid} 不在 roster 且未登记例外，中止")
            title = NOT_IN_ROSTER[nid][0]
        by_track.setdefault(tid, []).append((nid, title, award))

    for tid, rows in by_track.items():
        source = SOURCES[tid]
        path = os.path.join(ROOT, "data", tid, "awards.jsonl")
        existing = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                existing = [json.loads(line) for line in f if line.strip()]
        # 按 (nid, award) 去重，保留信息更完整的记录（完整 URL source / 更新的校验日期）。
        # 注意历史记录 nid 为整数，本脚本 AWARDS 中为字符串，统一转字符串比较。
        def quality(r):
            return (1 if str(r.get("source", "")).startswith("http") else 0, r.get("verified_at", ""))

        deduped = []
        seen = {}
        for r in existing:
            key = (str(r["nid"]), r.get("award"))
            if key not in seen:
                seen[key] = r
                deduped.append(r)
            elif quality(r) > quality(seen[key]):
                deduped[deduped.index(seen[key])] = r
                seen[key] = r
        existing = deduped
        by_key = {(str(r["nid"]), r.get("award")): r for r in existing}

        added = updated = 0
        for nid, title, award in rows:
            note = "公示卡片为据，未进入采集清单" if nid in NOT_IN_ROSTER else ""
            key = (str(nid), award)
            if key in by_key:
                r = by_key[key]
                if not r.get("verified") or r.get("source") != source:
                    r["verified"] = True
                    r["verified_at"] = TODAY
                    r["source"] = source
                    r["note"] = note
                    updated += 1
            else:
                existing.append({
                    "nid": nid,
                    "title": title,
                    "award": award,
                    "source": source,
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
