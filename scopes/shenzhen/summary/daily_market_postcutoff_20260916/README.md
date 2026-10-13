# 罗湖日度住宅市场汇总

本目录来自用户提供的“二手房成交信息（按日统计）”压缩包。它只有行政区、用途、日期、成交套数和成交面积，不含小区ID、单套价格、坐标或户型属性。

本文件实际覆盖2025-12-05至2026-09-14，其中罗湖住宅记录覆盖2025-12-06至2026-09-14；它没有补齐2024-04-26至2025-12-05的空档。

因此它可以补充2024年4月之后罗湖住宅市场的总量与面积走势，作为市场背景或共同冲击描述；不能连接木头龙周边住宅，不能做价格DID、项目ATT或距离异质性分析。该数据不替换原有小区级逐笔成交文件。

运行：

```powershell
python scopes/shenzhen/scripts/summarize_daily_market.py --zip /path/to/daily.zip --output scopes/shenzhen/summary/daily_market_postcutoff_20260916
```

输出`luohu_daily_residential_market.csv`为罗湖住宅日汇总，`district_use_coverage.csv`为区—用途覆盖，`summary.json`记录日期、哈希及字段缺口。来源压缩包原始SHA-256和日期范围必须以运行摘要为准。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [district_use_coverage.csv](district_use_coverage.csv)

行政区—用途的日期、成交套数和面积覆盖统计。

### [luohu_daily_residential_market.csv](luohu_daily_residential_market.csv)

罗湖住宅按日成交套数与面积汇总，补充市场背景但不是小区价格面板。

### [summary.json](summary.json)

所在分析批次的输入哈希、统计数量和研究状态。


<!-- generated-file-guide:end -->
