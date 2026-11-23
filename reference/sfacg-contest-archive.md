# SFACG 征文归档参考（端点 · 清单字段 · 赛道编号 · 获奖形态）

给维护本归档仓库的 agent 用。只保留端点、字段、赛道编号台账、获奖判定的硬事实；
不含任何下游项目的术语、口径或统计。文中数字为快照现值、随活动页版本变化，禁止硬编码进代码。

## 1. 两套清单 API

清单接口只返回 6 个字段（作品 id / 标题 / 作者 / intro / 封面 / 形式码），**无字数、收藏、状态、更新时间**。
本仓库已从这两套抹平到统一 schema（见 `../schema/roster.md`），下表仅为来源事实。

| 归档字段 | 新端点原始键 | 旧端点原始键 |
|---|---|---|
| `nid` | `novelID` | `NovelID` |
| `title` | `novelName` | `NovelName` |
| `author` | `authorName` | `AuthorName` |
| `form_id` | `categoryID` | `CategoryID` |
| `intro` | `intro` | `Intro` |
| `cover` | `cover`（完整 URL） | `Cover`（相对路径，需补前缀） |

### 新 SPA（2023 起，size 大）

```
GET https://pages.sfacg.com/api/essay/getNovels?tagIds=704&page=1&size=500
→ {status:{errorCode,msg}, data:{totalPage, novels[]}}
```

条目字段小驼峰：`novelID / novelName / authorName / intro / cover / categoryID`。
`totalPage` 是按当前 size 算的页数，**不是固定值**。

### 旧 H5（2018–2022）

```
GET https://pages.sfacg.com/ajax/ashx/Common.ashx?op=getNovelsByTag&tagId=415&ps=200&pi=0
→ {status, novels[], totalPage}   # status 是裸整数 200，无 data 包裹
```

条目字段首字母大写：`NovelID / NovelName / AuthorName / Intro / Cover / CategoryID`。

### 参数与陷阱

- 新：`tagIds`（复数）+ `page`（起始随版本变，以页面实际传参为准）+ `size≤500`；旧：`tagId`（单数）+ `pi`（**稳定 0 基**）+ `ps≤200`。
  `tagIds`/`tagId` 是上游 API 的查询参数名，**不是归档主键名**；归档统一叫 `contest_track_id`。
- 本仓库 `contests.json` 的模板统一用 **0 基**，`page_start` 字段兜底。
- 早期赛道（275–277 / 377–380 / 383–386 / 278）新旧两套都 alive，但**返回顺序与 totalPage 不同，分页参数不可跨套混用**；台账按页面登记，`api_generation: legacy` 走旧 H5，`modern` 走新 API。
- `size` 对个别赛道有边界（如 724 在 `size=500` 返回空、`size=1/3/8` 正常）：判空须降 size 重试（500→200→20→1）。
- **状态码不可信**：HTTP 200 + `status=200` 不代表有数据，必须拿到 `novels` 数组且字段合法才算成功（部分死链赛道返回 200 + 文案页）。
- 只取清单元数据，不取正文、不登录；串行限速 0.25–0.6s 无风控迹象。

### `form_id` 的真实含义

`categoryID` / `CategoryID` 在归档里叫 `form_id`，表示**作品形式/赛道属性**，不是题材，也不是「未分类」：

- `0` = 长篇 / 中篇（抽样字数中位数约 183 万字）
- `1` = 对话小说
- `3` = 短篇（抽样字数中位数约 2.7 万字）

题材是另一套字段（小程序接口 `minipapi.sfacg.com/pas/mpapi/novels/{nid}?expand=typeName` 的 `typeId` / `typeName`，如 26=都市、24=科幻、28=同人），不要混用。
存在个别错配（长篇赛道里有 `3`，部分长/短篇赛道都标 `1`），所以只作为弱分类信号。

## 2. 活动页 URL 形态（按年代）

| 世代 | URL | 清单取法 | 对应届 |
|---|---|---|---|
| 早期静态页（三征 2015） | `book.sfacg.com/zw2015/` | 参赛展为空，脚本仅登录态，**无清单 API** | 三征 |
| 静态页 + 内嵌 JS（四/五征 2016–17） | `book.sfacg.com/zwYYYY/list.html` | `js/list.js` 写死 `tagIds`，走旧 H5 | 四 275–277 / 五 377–380 |
| H5 活动页（六征 2018） | `pages.sfacg.com/h5/act/zw2018/` | `bridge.showSysTagDetail(383–386)`，走旧 H5 | 六 383–386 |
| H5 活动页（2019–2022） | `pages.sfacg.com/{h5,pc}/act/zwYYYY/`、`/act/djzwYYYY/`（冬） | 页面 JS 顶部 `tagIds=[...]`，走旧 H5 | — |
| SPA 活动页（2023 起） | `pages.sfacg.com/h5/act/zwYYYYMMDD/pc` | 打包 JS 内 `longTagId/middleTagId/shotTagId`，走新 API | 十二征起 |
| UUID 页（2024 秋起） | 随机串路径 | 获奖名单在页面 HTML，见 §4 | 2024 秋征起 |

- **一/二/三征无清单 API**：页面下线或参赛展空，用户 DevTools + 页面渲染双重实证无数据包、无静态清单。不在 `contests.json` 内，不要尝试补。
- 四/五/六征曾有「早期无 API」误判，已订正：编号写在 `list.js` / `showSysTagDetail` 里，接口实测可用。
- `contest_track_id` 是「某届比赛的某个赛项/赛道」编号，每次新增、生产号跨届不复用（十三征 752/753/754 vs 十二征 702/703/704）；sandbox 号会撞，不采。**只能从页面现场取，不能从届次/赛项名推导**。
- 跨征文聚合大编号（如 125）需按「同标注比例」排除，不是单届赛事。
- **逐届完整 URL 台账的权威在下游项目** `novly-proj/docs/contest-roster-harvest.md` §2（含每条赛事的确切活动页地址、UUID 页完整串）。本仓库把「赛道 → 活动页 URL」落到 `contests.json` 的 `activity_url` 字段（`tools/add_activity_urls.py` 迁移），供首页查找获奖公示。UUID 页必须用完整 UUID + `.html`，短 hash 会 404；页面下线/未取的赛道留空，勿臆造。

## 3. 赛道编号台账

权威台账见 `../../contests.json`（100 个赛道，主键键名为 `contest_track_id`，含赛事名/系列/`api_generation`/清单 API 模板 `url_template`/活动页 URL `activity_url`）。来源为各届活动页实证，
按系列归类：X 征（四~十四征，主线）、冬征（一~九征）、春征（2022–2026）、秋征（2021–2026）、
少年主题系列、对话线、34 个独立赛事（IP 联动 / 题材主题 / 对话节日）。

赛事不止四季主线：本地 24 万条 `contest` 标注含 99 种赛事；34 个独立赛事各有专属 `contest_track_id` 且清单接口存活。
编号段 1–850 探活约 447 个活跃编号，多数是单一赛项。真正无 API 的只剩库外一/二/三征。

## 4. 获奖名单：形态与判定

获奖**不在任何 API**，写死在活动页静态资源里。一条 GET 即得全量名单、无分页无鉴权；字段只有 nid + 书名。
具体名单已落在本仓库 `data/<contest_track_id>/awards.jsonl`（净 911 本），本节只讲判定法则。

### 四代存放形态

| 代 | 形态 | 可靠字段 | 奖项名来源 |
|---|---|---|---|
| 1 | 早期静态页 | 无 | 无获奖名单 |
| 2 | 十二/十三征 JS 静态 JSON（webpack 模块） | `novelId`/`novelName` | 邻域奖项图标 + favs 跃升判获奖模块；module id 跨届变，不能硬编码 |
| 3 | UUID 页 HTML `img[data-nid]`（2024 秋起六届） | `data-nid` | `alt` 尽力解析；纯数字档位靠标题图 `<p>` 恢复，不臆造中文名 |
| 4 | 日期式 Vue render 硬编码（七征冬/六征冬/2024 春） | 函数参数 nid | 标题图分组 + 规则名额，仅数量模式唯一匹配才用 |

### 判定法则（关键）

- **入围 ≠ 获奖**：十二/十三征活动页 JS 里初审/复审/展示数组与获奖数组混在一起（前者 favs 中位个位数、后者上千），整包抓会把入围当获奖。必须按模块邻域图标 + favs 跃升判定哪几组才是获奖，只取获奖模块。本仓库现有 911 本已剔除 602 本入围污染。
- **奖项名不臆造**：`alt` 纯数字（如八征冬）只能按 HTML 结构恢复档位写 `第N档`，不编中文名；未知一律 `待逐档标定`（现 867 本）。
- **获奖是历史终态**：书可能后来断更/下架，获奖徽标仍是事实；但获奖不等于当前优质，不用于打分排序。
- 独立赛事（IP 联动 / 题材 / 对话节日）**没有获奖名单**，只有参赛清单；不要臆造。

## 5. 交叉核对用端点（非本仓库数据，仅排查时用）

- 详情页：`m.sfacg.com/b/{nid}/`（移动，15KB）、`book.sfacg.com/Novel/{nid}/`（PC，73KB）。
- **状态码不可信**：无效 nid 也返回 200 + 文案页，判存在必须匹配文案（如「作品不存在」），不能只看 HTTP 码。
- 移动版 `.book_Author` 有作者头像/名/作品集；作者 intro 只有 PC 版 `.author-box .author-desc` 有。
