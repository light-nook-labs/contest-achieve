# contests.json 赛道注册表

一行一个赛道对象，主键 `contest_track_id`，跨赛事不复用。未知 ID 也在此注册，但 `series="未知"` 不视为赛事。

```json
{"contest_track_id":746,"contest_name":"2025春征","series":"春征","api_generation":"modern","page_start":0,"url_template":"https://pages.sfacg.com/api/essay/getNovels?tagIds={contest_track_id}&page={page}&size={size}","activity_url":"https://pages.sfacg.com/h5/act/zw/essayActivity_d892261b-8719-4e3b-b01a-b84278b2996b.html","start_date":"2025-03-01","end_date":"2025-05-03","result_date":"2025-07-11"}
```

## 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `contest_track_id` | int | 赛道 id，主键 |
| `contest_name` | str | 赛事名；未确认的写「未知」 |
| `series` | str | 系列：`X征` / `冬征` / `春征` / `秋征` / `少年` / `对话` / `独立` / `未知` |
| `api_generation` | str | `legacy`（旧 H5 `getNovelsByTag`）/ `modern`（SPA `getNovels`） |
| `page_start` | int | 清单接口首页页码，两套接口均按实际页面传参；模板默认 0 |
| `url_template` | str | 清单 API 模板，占位符 `{contest_track_id}` / `{page}` / `{size}` |
| `activity_url` | str | 官方活动页 URL；下线或未取到留空串 |
| `start_date` | str | 征稿开始日 `YYYY-MM-DD`，无可靠来源留空串 |
| `end_date` | str | 征稿截止日 `YYYY-MM-DD`，无可靠来源留空串 |
| `result_date` | str | 结果公布/公示日 `YYYY-MM-DD`，无可靠来源留空串 |

## 日期字段的写入规则

- **只写能核对到具体日期的事实**，不从 nid 定年窗、作品创建时间或「系列固定在某日启动」的规律反推。查不到就留空串，站点显示「—」。
- 同一赛事的多个赛道共享同一组日期（如十三征 752/753/754）。
- 当前来源（详见 `tools/add_contest_dates.py` 的注释）：
  1. novly-proj `analysis/references/contest-editions.md` §官方 App 核实的精确日期（用户逐届查询）：2024 秋、八征冬、2025 春、十三征、奇幻世界、2025 秋、九征冬、2026 春。
  2. 同文档官方页面确认：四征 `rule.html` 的 2016-07-08 → 10-06、十二征页面 id `zw20240504`。
  3. 同文档崩坏3 联动：网易号官方通稿 2019-01-04 → 02-11，02-22 公示。
  4. novly-proj `docs/contest-roster-harvest.md` §2/§3：活动页 `data-firstpublictime`、日期式页面 id 自证启动日、聚合站佐证的征稿起止与公示日。
- `tools/add_contest_dates.py` 幂等：只填空字段，不覆盖人工修正。新增日期时可扩充脚本映射，或直接编辑注册表。
- 站点导出 `docs/data/contests.json` 会带上这三个字段，赛事索引与详情页展示；未知 ID tab 不展示日期。
