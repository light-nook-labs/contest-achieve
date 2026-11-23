# awards.jsonl 记录格式

获奖是静态终态，与清单分离。本文件**可人工编辑**：自动提取的结果填入后，人工核实可改 `award`、`verified`、`note`。

```json
{"nid":774528,"title":"我的魔法少女……","award":"金奖","source":"zw20260504 活动页 img[data-nid] alt","verified":true,"verified_at":"2026-11-21","note":""}
```

## 字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `nid` | int | 是 | 作品 id，主键（与 roster 共享） |
| `title` | str | 是 | 书名，便于人工核对 |
| `award` | str | 是 | 奖项名，只写页面/公告里确实出现的真实奖项，不臆造、不写占位 |
| `source` | str | 是 | 证据来源（活动页路径 / 公告 URL / 用户观测），留痕 |
| `verified` | bool | 是 | true = 已核实。当前所有记录均为 true |
| `verified_at` | str | 否 | 核实日期 YYYY-MM-DD，未核实留空串 |
| `note` | str | 否 | 补充说明，如「同名多届」「alt 退化为数字靠 HTML 结构恢复」 |

## 规则

- 按 `nid` 去重；同一作品多届获奖则多行的 `nid` 相同，靠 `source`/`note` 区分。
- `award` 只写页面/公告里确实出现的奖项名；`alt` 退化为纯数字的届（如八征冬），按 HTML 结构恢复档位但不臆造中文名，写 `第N档` 并在 `note` 说明。
- 入围/初审/复审展示**不是获奖**，不得混入本文件。
- **只写核实过的事实**：没有官方公示或人工确认依据的条目不要写入，不要迁入净名单里的待定条目。
  原先的 `待逐档标定` / `verified=false` 占位记录已被判定不可靠并全部删除，不再使用。
- 空文件表示尚未核实获奖，不影响清单使用。
- 归档文件本身**不冗余**赛事字段。站点导出 `docs/data/awards.json` 时会额外加上 `contest_track_id` / `contest_name` / `series`，方便总览页筛选；那只是发布层派生数据，不是归档 schema。
