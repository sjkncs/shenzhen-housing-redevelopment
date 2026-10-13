# 分页开放平台快照

本目录来自9月16日保存的深圳政府数据开放平台分页响应，而不是10,000行日汇总ZIP。10页原始JSON共96,078条，哈希由原下载审计逐页记录；日期覆盖2017-01-03至2026-09-15，罗湖住宅记录2,851条。

区名标准化后发现198行同日同用途冲突，已隔离为normalized_name_collision_rows.csv，未择一或重复加总。罗湖住宅原始2,851行中18行受影响，当前无冲突汇总保留2,833行；冲突原因及版本仍待来源核定。月度数值只代表无冲突已报告行，不是完整月总量。

字段仍只有`ID`、日期、行政区、用途、成交套数和成交面积。它比日汇总ZIP覆盖更长，但仍不包含小区、单套价格或坐标；只能用于深圳/罗湖市场总量、成交面积和时间覆盖分析，不能连接木头龙周边住宅，也不能做价格DID。

本目录公开的是分页核验汇总及逐页哈希摘要，不上传原始JSON页面。`luohu_daily_residential_open_data.csv`保留原字段加标准化行政区，`district_monthly_residential_open_data.csv`仅加总已报告行，不补缺日、不证明完整月度总量。罗湖与罗湖区的名称已标准化为罗湖，原始ZONE仍保留。

复现代码：[audit_paged_open_data.py](../../scripts/audit_paged_open_data.py)。输入依赖本地历史分页原件与下载审计，它们尚未加入公开Release；现有Release只有此前的平台交易CSV与空间资料，不能直接替代该接口的分页JSON。接口快照是2026-09-16历史版本，不代表今日接口全量；不能把单页10000行当作全量，也不能把分页总数吻合当作市场普查验证。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [district_monthly_residential_open_data.csv](district_monthly_residential_open_data.csv)

分页开放平台快照的各区月度住宅成交套数与面积，不是价格数据。

### [luohu_daily_residential_open_data.csv](luohu_daily_residential_open_data.csv)

由分页开放平台快照核验出的罗湖住宅日度套数面积，保留原字段和标准化区名。

### [normalized_name_collision_rows.csv](normalized_name_collision_rows.csv)

行政区名称标准化后同日同用途发生冲突的原行，隔离不择一或重复加总。

### [summary.json](summary.json)

所在分析批次的输入哈希、统计数量和研究状态。


<!-- generated-file-guide:end -->
