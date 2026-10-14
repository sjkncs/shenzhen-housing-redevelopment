# scopes/shenzhen/scripts / 中文说明

全市清洗与区级覆盖汇总代码。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [audit_daily_market_coverage.py](audit_daily_market_coverage.py)

用途：检查日汇总重复键、缺失日期、月度覆盖与全市区级合计一致性

输入：--zip日成交ZIP、--output新目录

输出：罗湖月度覆盖、缺失日期、区级对账及摘要

运行条件：不补零、不把区级成交面积当价格；完整日覆盖不证明官方普查完整

### [audit_paged_open_data.py](audit_paged_open_data.py)

用途：核验政府开放平台分页JSON哈希，合并并标准化行政区，生成深圳/罗湖月度住宅市场总量

输入：--pages分页JSON目录、--audit原分页哈希审计

输出：--output罗湖日度与区月度CSV及摘要

运行条件：只处理行政区总量，不含价格/小区/坐标，不用于项目DID

### [build_citywide_summary.py](build_citywide_summary.py)

用途：清洗全市平台交易，统计行政区覆盖

输入：--input指定原始成交CSV

输出：scopes/shenzhen/summary/区级CSV和JSON

运行条件：需先下载交易包并解压；不会输出逐套记录

### [classify_district_collisions.py](classify_district_collisions.py)

用途：逐组比较标准化区名冲突的套数、面积与来源ID

输入：--input区名冲突CSV、--output新目录

输出：逐组分类、区级汇总与摘要

运行条件：不选择版本、不合并原行、不更新原月度统计

### [reconcile_district_alias_scenarios.py](reconcile_district_alias_scenarios.py)

用途：比较短区名、带区后缀区名及两类相加三种假设与同日全市套数面积合计

输入：--source历史接口合并CSV、--collisions冲突行表

输出：--output三种对账场景及摘要

运行条件：仅诊断不选择合并规则，不修改月度统计

### [summarize_daily_market.py](summarize_daily_market.py)

用途：从按日行政区汇总中提取罗湖住宅成交套数和面积，补足市场背景截止日后的总量走势

输入：--zip用户提供的日汇总ZIP，必须含所属区/用途/日期/套数/面积字段

输出：罗湖日汇总、区—用途覆盖和摘要

运行条件：不含小区ID、价格、坐标，不能用于项目DID或价格回归


<!-- generated-file-guide:end -->
