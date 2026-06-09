# 数据源可行性 — 详细评估

本文件记录 2026-06-10 的完整调研结论，供后续设计参考。

## Football-Data.co.uk

| 指标 | 结论 |
|---|---|
| markets | 1X2 ✅ AH ✅ OU ✅ |
| opening odds | ✅（周五下午收集=预开盘，字段如 B365H） |
| closing odds | ✅（2005/06 起，字段后缀 C，如 B365CH） |
| AH line | ✅（BbAHh / AHh） |
| OU line | ✅（Bb>2.5 / Bb<2.5，OU 2.5 为主） |
| 覆盖年份 | 1993~2026（31 季） |
| 覆盖联赛 | 22 欧洲 + 16 全球主流联赛 |
| 格式 | CSV |
| 成本 | 免费 |
| 质量 | HIGH |

**局限**：只有单线 OU/AH 平均价，非多 bookmaker 全量多线；Pinnacle 2025-07 后不稳定。

## The Odds API

| 指标 | 结论 |
|---|---|
| markets | 1X2 (h2h) ✅ / AH (spreads) ❌ / OU (totals) ❌ |
| opening/closing | 历史快照端点 ✅，2020-06 起 5-10min 粒度 |
| 成本 | 免费 500 次/月；历史付费 $30+/月 |
| 质量 | MEDIUM（足球缺少 AH/OU） |

**用途**：补充 2020+ 1X2 movement 验证。

## api-football

| 指标 | 结论 |
|---|---|
| markets | 1X2 ✅ AH ✅ OU ✅ BTTS ✅ DC ✅ 1H ✅ |
| opening/closing | ❌ 无 native 字段 |
| 历史 | ❌ 历史比赛赔率=空 |
| 质量 | MEDIUM（当前赛季好，无回溯） |

**用途**：当前赛季赔率 poll。

## 综合结论

可行。最佳组合：
- Football-Data 做核心历史回测
- The Odds API 做 1X2 movement 交叉验证
- api-football 做实时 poll 原型
