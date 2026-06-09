# M1_MARKET_BIAS_ENGINE

**Market Bias / 开盘-临场赔率偏差研究**

## 项目定位

独立于 V3 / V4 的新研究项目。

- **不是** V3 / V4 的扩展或升级
- **不**复用 V3 / V4 代码目录
- **不**修改旧仓库（v2_football_quant）的任何文件
- **不**移动旧系统数据
- **当前阶段只做数据源验证和蓝图设计**
- **不产生推荐、不写 official、不接 QQ、不接 pending**

## 数据源策略

| 优先级 | 数据源 | 用途 |
|---|---|---|
| P0 | Football-Data.co.uk | 历史回测主源：26 赛季 AH/OU/1X2 opening+closing，免费 |
| P1 | The Odds API | 2020+ 历史 1X2 movement 验证（免费 500 次/月） |
| P2 | api-football | 当前赛季赔率 poll snapshot |

详见 [`docs/data_sources.md`](docs/data_sources.md)。

## 目录结构

```
m1_market_bias_engine/
├── README.md          ← 本文件
├── docs/              ← 数据源调研、方案蓝图、设计文档
├── config/            ← 数据集路径、API key 引用、研究参数
├── data/
│   ├── raw/           ← 原始下载数据（Football-Data CSV 等）
│   └── processed/     ← 清洗后特征数据
├── src/               ← 后续特征工程代码（当前为空）
├── tests/             ← 单元测试（当前为空）
├── scripts/           ← 数据下载、预处理脚本
└── reports/           ← 研究输出、图表、验证报告
```

## 研究目标

1. 验证开盘赔率（opening）→ 临场赔率（closing/market）偏差是否能作为有效特征
2. 构建 AH（Asian Handicap）和 OU（Over/Under）偏差的定量分析框架
3. 与 Football-Data 历史赛果关联，验证 bias → 赛果的统计显著性

## 纪律

- 本仓库不产生任何实盘推荐
- 本仓库数据不流入 V3/V4 系统
- 不接 QQ 消息推送
- 不修改旧系统
- 不跨项目耦合
