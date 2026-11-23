# roster.jsonl 记录格式

每行一条 JSON，字段固定 6 个，不含任何溯源字段（溯源在 `meta.json` 的快照记录里）。

```json
{"nid":784181,"title":"我堕落魔女养个魔法少女怎么了？","author":"量子巫女","form_id":0,"intro":"巴虺觉得自己一定是造了什么孽……","cover":"https://rs.sfacg.com/web/novel/images/NovelCover/Big/2026/09/9507a07f-....jpg"}
```

## 字段

| 字段 | 类型 | 来源（新端点） | 来源（旧端点） | 说明 |
|---|---|---|---|---|
| `nid` | int | `novelID` | `NovelID` | 作品 id，清单内主键 |
| `title` | str | `novelName` | `NovelName` | 书名 |
| `author` | str | `authorName` | `AuthorName` | 作者名（原样保留） |
| `form_id` | int | `categoryID` | `CategoryID` | **作品形式码**：`0`=长篇/中篇，`1`=对话小说，`3`=短篇。不是题材，也不是「未分类」 |
| `intro` | str | `intro` | `Intro` | 简介，原样保留（含换行） |
| `cover` | str | `cover` | `Cover` | 封面。新端点已是完整 URL；旧端点为相对路径，拼 `https://rs.sfacg.com/web/novel/images/NovelCover/Big/` 前缀 |

### `form_id` 的含义（实测结论）

全站采样只有 `0 / 1 / 3` 三个值，且与赛事赛道、作品字数高度对应：

- `0`：十二/十三/十四征的长篇、中篇赛道全为 0；抽样字数中位数约 183 万字。
- `3`：同届短篇赛道全为 3；抽样字数中位数约 2.7 万字。
- `1`：对话赛事（九征-对话、对话小说春节/情人节/开学季等）全为 1。

它**不是题材**。题材是另一套字段（小程序接口 `typeId` / `typeName`，如 26=都市、24=科幻、28=同人）。同一个 `form_id=0` 下能查到都市/魔幻/玄幻/游戏。

它也**不是完美可靠**：长篇赛道里有 2 本 `form_id=3`（字数 5.8 万、14.7 万，疑似短篇投长篇赛道）；「怪谈异闻·长篇/短篇」「春节征文·长篇/短篇」两个赛道都标 `1`。因此只能当作站点登记的作品形式/赛道属性，存在个别错配，**不要据此推断作品题材或质量**。

交叉核对方法（仅排查用）：`https://minipapi.sfacg.com/pas/mpapi/novels/{nid}?expand=typeName`，看 `typeId` / `expand.typeName`。

## 规则

- 按 `nid` 去重，同一赛事内不重复。
- 抓取失败/空记录不写行，留待下次续采。
- 不写字数、收藏、赞、状态等观测字段。
- 字段顺序固定为上表顺序，便于 git diff。
- 旧仓库里曾写作 `category_id` 并注释「0 表示未分类」，这是错误结论，已统一改为 `form_id`。
