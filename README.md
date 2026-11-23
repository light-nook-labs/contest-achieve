# contest-achieve

sfacg 征文赛事的**集中化归档**。目的：活动页随时可能下线、API 状态码不可信、URL 格式会变，本仓库保存一份统一格式、可长期维护的赛事清单与获奖记录，作为下游数据集/种子的稳定输入。

## 设计原则

1. **统一格式**：新旧 API 的字段差异在采集器里抹平，归档只存一种 schema（见 `schema/`）。不保留 sfacg 原始字段名。
2. **`contest_track_id` 为主键**：目录名、站点 URL、记录归属都用这个数字。它标识「某届征文的某个赛道/赛项」；赛事名和 URL 会变，它不变。API 里的 `tagIds` / `tagId` 只是上游参数名。
3. **清单与获奖分离**：清单是抓取快照（`roster.jsonl`），获奖是静态终态、可人工补齐（`awards.jsonl`），两者独立更新。
4. **不存观测快照**：字数/收藏/赞/状态会随时间变，不属于归档，留在下游 dataset。
5. **站点只读 JSON**：发布层不内联数据、不生成上百个 HTML；页面是静态壳，运行时 fetch JSON 渲染。

## 目录结构

```
contest-achieve/
├── README.md
├── schema/
│   ├── roster.md         参赛清单记录格式
│   └── awards.md         获奖记录格式
├── contests.json         赛事注册表：100 个赛道的 ID/名称/系列/接口/清单 URL 模板/活动页 URL
├── data/<contest_track_id>/
│   ├── meta.json         赛事元数据 + 抓取快照记录
│   ├── roster.jsonl      参赛清单（统一格式，每行一条）
│   └── awards.jsonl      获奖名单（可手动编辑，可为空）
├── site/                 站点源文件（静态壳 + Vue 应用 + CSS）
│   ├── index.html
│   ├── contest.html
│   ├── awards.html
│   └── assets/
├── tools/
│   ├── harvest.py        采集器：从 contests.json 读赛事，归一化落盘
│   ├── verify.py         校验器：schema 合规 + 赛事覆盖
│   ├── import_awards.py  一次性获奖迁移脚本
│   ├── migrate_keys.py   一次性键名迁移（幂等，已执行）
│   ├── add_activity_urls.py 一次性补活动页 URL（幂等，已执行）
│   └── build_site.py     导出 JSON + 复制静态壳 → docs/
└── docs/                 发布目录（GitHub Pages 从此目录 serve）
```

## 环境

用 uv 管理，首次运行自动建环境并装依赖（无需手动建 venv）：

```bash
uv run python tools/verify.py
```

依赖声明在 `pyproject.toml`，锁定版本在 `uv.lock`。采集只需 `requests`；站点运行时 Vue 3 已内置在 `site/assets/`，无 CDN 依赖。

## 采集

```bash
uv run python tools/harvest.py --all              # 全部赛事
uv run python tools/harvest.py --tags 793 794     # 指定赛道
uv run python tools/verify.py                     # 校验（--strict 要求全部采集）
```

采集器从 `contests.json` 读清单 API 模板——**URL 格式变了只改注册表**，不改代码。
断点续采：重跑同一命令会跳过已抓 nid。获奖可先于清单迁入，两者独立。

## 活动页 URL

`contests.json` 每条赛道有 `activity_url` 字段，指向该届官方活动页（参赛展 / 获奖公示所在页），
首页赛事列表可点开查找获奖。来源为 novly-proj 的 `docs/contest-roster-harvest.md` §2 权威台账
（逐届页面实证，一届多赛道共用一个活动页）。页面已下线或未取到的赛道留空字符串，不臆造 URL。
当前 100 条中 61 条有活动页 URL；新增赛事时按台账补该字段即可。

## 获奖补齐

直接编辑 `data/<contest_track_id>/awards.jsonl`，一行一条 JSON，字段见 `schema/awards.md`。
`verified=true` 表示人工核实过。**只写核实过的事实，不写入未核定的待定条目。**

十三征获奖由 `tools/import_awards_13th.py` 依据官网公示页标定（752 长篇 15 / 753 中篇 5 / 754 短篇 5，
金 3 / 银 3 / 铜 9 / 推荐 5 / 星火 5），经人工核验；公示页「大赏」从未颁发，不写入。
原净名单迁入的 852 条 `待逐档标定` 记录经用户判定不可靠，已由 `tools/prune_13th_unverified.py`
与 `tools/prune_all_unverified.py` 全部删除。现共 **69 本、8 个赛道，全部已核实**。

## 站点部署（GitHub Pages）

```bash
uv run python tools/build_site.py   # 生成 docs/
```

生成物：

- `docs/index.html` — 赛事索引，搜索/筛选/分页；「获奖」列可点进该赛事的获奖列表
- `docs/contest.html?contest_track_id=793` — 赛事详情，按需 fetch 清单并搜索/分页
- `docs/awards.html?contest_track_id=752` — 单赛事获奖列表，页面开头提供官方公示页链接（`activity_url`）
- `docs/data/site.json` — 构建时间与汇总统计
- `docs/data/contests.json` — 全部赛道元数据 + 计数
- `docs/data/roster/<contest_track_id>.json` — 已采赛道的清单
- `docs/data/awards.json` — 合并获奖，带冗余赛道字段便于筛选

本地预览（浏览器禁止 `file://` 读取 JSON，必须走 HTTP）：

```bash
cd docs && python -m http.server 8000
# 打开 http://localhost:8000
```

在 GitHub 仓库 Settings → Pages → Source 选 `main` 分支的 `/docs` 目录即可上线。
每次采集/补获奖后重跑 `build_site.py` 并提交 `docs/`。
