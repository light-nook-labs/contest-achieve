# 交接说明（当前状态，2026-11-23）

本仓库是 SFACG 征文赛事的独立归档项目（非 novly-proj 子目录），只存**参赛清单**与**获奖记录**两类稳定数据，不存字数/收藏/状态等随时间变化的观测字段。发布站点在 `docs/`，由 GitHub Pages 直接 serve。

## 一、数据现状

- **赛事注册表**：`contests.json` 共 100 个赛道，主键 `contest_track_id`。
  每条含 `contest_name` / `series` / `api_generation`（`legacy`/`modern`）/ `page_start` /
  `url_template`（清单 API 模板，占位符 `{contest_track_id}`）/ `activity_url`（官方活动页）。
- **活动页 URL**：100 条中 **61 条有 `activity_url`**，39 条页面下线或未取到（留空）。
  来源为 novly-proj `docs/contest-roster-harvest.md` §2 权威台账，由 `tools/add_activity_urls.py` 迁移。
  首页赛事列表可直接点开活动页查找获奖公示。**UUID 页必须用完整 UUID + `.html`，短 hash 会 404。**
- **参赛清单**：100/100 赛道全部采集完成，共 **135,663 条**，无空赛道；`verify.py --strict` 通过。
- **获奖记录**：8 个赛道共 **69 条**，全部 `verified=true`，均为人工核实、可靠数据。分布：
  725(11) / 746(10) / 752(15) / 753(5) / 754(5) / 772(7) / 774(10) / 789(6)。
  其中 25 条十三征获奖由 `tools/import_awards_13th.py` 依据官网公示（用户提供、人工核验通过）标定，
  分布金 3/银 3/铜 9/推荐 5/星火 5，`verified_at=2026-11-23`、`source` 指向公示 URL；
  公示页「大赏」从未颁发（标注「本次轮空」），不写入。
- **已删除的不可靠数据**：原净名单迁入的 852 条 `待逐档标定` + `verified=false` 记录全部删除
  （752 的 431 条由 `tools/prune_13th_unverified.py`，其余 421 条由 `tools/prune_all_unverified.py`）。
  用户判定：只有官网公示/人工核实的奖项才算获奖，净名单中的待标定条目不可靠。
  备份：`/tmp/752_awards_before_prune.jsonl`、`/tmp/awards_all_before_prune.tar.gz`。
  485/692/699/702/726 的 awards.jsonl 已清空（保留空文件，符合 schema「空文件表示尚未核实」）。
  **当前无任何 `待逐档标定` 残留；今后新增获奖必须是核实过的事实，不再迁入待定条目。**

## 二、键名方案（已迁移，勿回退）

- `roster.jsonl`：`nid / title / author / form_id / intro / cover`（6 字段，顺序固定）。
  `form_id` 是作品形式码：**0=长/中篇，1=对话小说，3=短篇**，非题材、非「未分类」，存在个别错配，只作弱信号。
- `awards.jsonl`：`nid / title / award / source / verified / verified_at / note`。
- `meta.json`：`contest_track_id / contest_name / series / api_generation / page_start / url_template / snapshots[]`；
  快照内 `captured_at / total_pages / fetched_pages / novel_count / sha256`。
- raw API 键（`novelID` / `NovelID` 等）只出现在采集器输入端与参考文档的「来源对照」，归档数据中无残留。
- 一次性迁移脚本 `tools/migrate_keys.py`、`tools/add_activity_urls.py`、`tools/import_awards_13th.py`、`tools/prune_13th_unverified.py`、`tools/prune_all_unverified.py` 均幂等，保留供审计，无需重跑。

## 三、站点

静态壳 + 前端 fetch JSON，不再逐赛道生成 HTML：

- `site/`：`index.html`（索引，「获奖」列可点进列表）、`contest.html?contest_track_id=<id>`（详情）、
  `awards.html?contest_track_id=<id>`（单赛事获奖列表，开头有公示页 `activity_url` 链接）、
  `assets/app.js` / `style.css` / 本地 vendored Vue 3（无 CDN）。无全局获奖总览页，各页导航只留「赛事索引」。
- `tools/build_site.py`：纯数据导出 + 复制站点壳 → `docs/`。
- `docs/data/`：`site.json`、`contests.json`（含 `activity_url`）、`roster/<id>.json`、`awards.json`。

数据变动后必须重跑 `uv run python tools/build_site.py`，再视需要提交 `docs/`。
本地预览必须走 HTTP（`cd docs && python -m http.server 8000`），双击 HTML 会被浏览器禁止读 JSON。

## 四、工作流

```bash
uv run python tools/harvest.py --all          # 断点续采清单（已全量完成）
uv run python tools/harvest.py --tags 793 794 # 指定赛道
uv run python tools/verify.py                 # 校验；--strict 要求全部 100 赛道
uv run python tools/build_site.py             # 重建站点数据
```

## 五、待办（优先级）

1. **人工补获奖**：编辑 `data/<contest_track_id>/awards.jsonl`，只添加**核实过的事实**，不再迁入待定条目。
   官网公示页是可靠证据来源；提取获奖作品可用 nid（硬编码在活动页 JS 的 `openNovel(nid)`）+ 图片文件名标奖项，比 OCR 更准。
   若某赛事确认只有一个公示页，页面之外的条目不要写入。
2. **活动页 URL**：若用户在 App 观测到此前「未取」赛事的活动页，按台账补 `contests.json` 的 `activity_url`（勿编造）。
3. **URL 同步**：SFACG 改 URL 格式时只改 `contests.json` 的 `url_template` / `activity_url`，不改代码。
4. **提交推送**：本仓库尚未 commit/push（仅 `Initial commit`，项目文件均未跟踪）。

## 六、坑

- 不信任 HTTP 状态码：必须是含合法 `novels` 数组的响应才算有效；空响应降 size 500→200→20→1 重试。
- 分页两套接口均 0 基；部分小赛道 `size=200` 返空，需降 size。
- 一/二/三征无清单 API（用户 DevTools 实证），不尝试补。
- 数字均为快照，禁止硬编码进代码，用现算值。
