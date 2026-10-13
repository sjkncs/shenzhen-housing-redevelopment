# 01 / 数据获取与清洗

下载、输入校验、全市清洗与覆盖统计。

这里按用途导航到真实代码，不复制或移动当前执行文件。

## [audit_daily_market_coverage.py](../../scopes/shenzhen/scripts/audit_daily_market_coverage.py)

**用途：**检查日汇总重复键、缺失日期、月度覆盖与全市区级合计一致性

**输入：**--zip日成交ZIP、--output新目录

**输出：**罗湖月度覆盖、缺失日期、区级对账及摘要

**运行条件：**不补零、不把区级成交面积当价格；完整日覆盖不证明官方普查完整

路径：`scopes/shenzhen/scripts/audit_daily_market_coverage.py`

## [audit_paged_open_data.py](../../scopes/shenzhen/scripts/audit_paged_open_data.py)

**用途：**核验政府开放平台分页JSON哈希，合并并标准化行政区，生成深圳/罗湖月度住宅市场总量

**输入：**--pages分页JSON目录、--audit原分页哈希审计

**输出：**--output罗湖日度与区月度CSV及摘要

**运行条件：**只处理行政区总量，不含价格/小区/坐标，不用于项目DID

路径：`scopes/shenzhen/scripts/audit_paged_open_data.py`

## [build_citywide_summary.py](../../scopes/shenzhen/scripts/build_citywide_summary.py)

**用途：**清洗全市平台交易，统计行政区覆盖

**输入：**--input指定原始成交CSV

**输出：**scopes/shenzhen/summary/区级CSV和JSON

**运行条件：**需先下载交易包并解压；不会输出逐套记录

路径：`scopes/shenzhen/scripts/build_citywide_summary.py`

## [summarize_daily_market.py](../../scopes/shenzhen/scripts/summarize_daily_market.py)

**用途：**从按日行政区汇总中提取罗湖住宅成交套数和面积，补足市场背景截止日后的总量走势

**输入：**--zip用户提供的日汇总ZIP，必须含所属区/用途/日期/套数/面积字段

**输出：**罗湖日汇总、区—用途覆盖和摘要

**运行条件：**不含小区ID、价格、坐标，不能用于项目DID或价格回归

路径：`scopes/shenzhen/scripts/summarize_daily_market.py`

## [download_data.py](../../scripts/download_data.py)

**用途：**按全市或罗湖下载公开数据，核验SHA-256；不自动解压

**输入：**Release清单；可选已有下载文件

**输出：**data/raw/downloads/中的已核验附件

**运行条件：**可直接运行；默认联网下载

路径：`scripts/download_data.py`

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。


<!-- generated-file-guide:end -->
