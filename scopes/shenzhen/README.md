# Shenzhen / 全市数据基础

本范围用于全市来源覆盖与清洗汇总，不输出全市拆除重建效应。原始数据是用户提供的平台成交文件；没有代表全市总体的抽样设计保证。

实际汇总：139,514条原始记录，132,774条满足规则，6,740条被排除；清洗样本跨2010-01-01至2024-04-25。罗湖保留16,199条、621个小区，与片区执行摘要一致。

公开文件：[coverage.json](summary/coverage.json)、[district_coverage.csv](summary/district_coverage.csv)。只包含行政区汇总，不包含个体地址、坐标、交易URL或逐套价格。

```bash
python scopes/shenzhen/scripts/build_citywide_summary.py --input /path/to/authorized_transactions.csv
```

筛选普通住宅、商品房、有效成交日期和小区ID、正面积与价格、0—120年房龄、有效电梯标签、无挂牌晚于成交情况，以及总价与单价乘面积差异不超过2%。缺失挂牌日期不因该项单独剔除；此规则与封存片区代码一致，不能解释为全部信息无缺失。

全市原始交易、POI与建筑源压缩包已在[公开Release](https://github.com/sjkncs/shenzhen-housing-redevelopment/releases/tag/data-snapshot-20261012)提供。来源、字段与校验值见[下载说明](../../docs/DATA_ACCESS.md)。文件覆盖不意味着已接受坐标、年份或建筑身份。
