# scopes/shenzhen/scripts / 中文说明

全市清洗与区级覆盖汇总代码。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [build_citywide_summary.py](build_citywide_summary.py)

用途：清洗全市平台交易，统计行政区覆盖

输入：--input指定原始成交CSV

输出：scopes/shenzhen/summary/区级CSV和JSON

运行条件：需先下载交易包并解压；不会输出逐套记录

### [summarize_daily_market.py](summarize_daily_market.py)

用途：从按日行政区汇总中提取罗湖住宅成交套数和面积，补足市场背景截止日后的总量走势

输入：--zip用户提供的日汇总ZIP，必须含所属区/用途/日期/套数/面积字段

输出：罗湖日汇总、区—用途覆盖和摘要

运行条件：不含小区ID、价格、坐标，不能用于项目DID或价格回归


<!-- generated-file-guide:end -->
