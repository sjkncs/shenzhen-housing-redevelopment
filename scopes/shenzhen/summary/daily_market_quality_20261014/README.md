# 日度市场汇总质量与月度覆盖

本轮只核查用户日汇总ZIP内部一致性；没有取得数据提供者对缺行、统计口径或导出范围的独立说明，不将其称为完整官方普查。

## 已检查结果

原CSV为10,000行，区—用途—日期无重复键；罗湖住宅有276个日观测，整个源区间2025-12-05至2026-09-14内缺8天。只有2026年1、3、5、7、8月每个日历日都有记录；月度输出保留观测日和缺日数，不把缺行填0。

280个有全市住宅记录的日期，已报告各区的成交套数合计与全市相同，面积合计在0.05平方米的数值容差内一致。其中163天未出现全部十个区的住宅行，虽然已报告合计吻合，仍不能独立认定每个缺区都是零成交；需要原提供者统计说明。

恰为10,000行可能与导出上限有关，但未取得分页或导出说明，不判定已经截断或一定完整。边界月份本来就只有部分来源日期，即使内部没有额外缺行也不能说是完整月份。

## 使用方式

`luohu_monthly_reported_coverage.csv`为实际已报告月度总量，并显示日历覆盖；`luohu_absent_calendar_dates.csv`列来源内缺行日期；`residential_district_reconciliation.csv`逐日保留对账差值与缺区。月度总量可作描述，比较不同月份时须先说明覆盖条件，不用于木头龙价格DID或构造小区成交。

复现脚本见[audit_daily_market_coverage.py](../../scripts/audit_daily_market_coverage.py)。它拒绝重复键、负数、缺失数字和非整数成交套数，输出新目录，不改原文件。内部对账通过不验证实际交易是否全量，不确认成交/登记日期口径。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [luohu_absent_calendar_dates.csv](luohu_absent_calendar_dates.csv)

整个来源日期区间内没有罗湖住宅行的日期，不代表零成交。

### [luohu_monthly_reported_coverage.csv](luohu_monthly_reported_coverage.csv)

罗湖住宅各月已报告套数面积与日覆盖，不把缺报日补零。

### [residential_district_reconciliation.csv](residential_district_reconciliation.csv)

全市住宅与已报告各区合计比较，标出未出现的行政区。

### [summary.json](summary.json)

所在分析批次的输入哈希、统计数量和研究状态。


<!-- generated-file-guide:end -->
