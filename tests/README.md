# tests / 中文说明

数据无关测试及已归档中间成果一致性测试。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [test_alias_scenarios.py](test_alias_scenarios.py)

用途：测试相加型冲突与缺失全市合计拒绝

输入：程序内行政区总量样例

输出：unittest结果

运行条件：内部对账不证明来源口径

### [test_alias_use_totals.py](test_alias_use_totals.py)

用途：测试分用途合计、总计缺失和重复类别拒绝

输入：程序内用途示例

输出：unittest结果

运行条件：无需真实数据

### [test_candidate_composition.py](test_candidate_composition.py)

用途：验证前段、过渡和后段正确分离

输入：季度样例

输出：unittest结果

运行条件：无需真实数据

### [test_candidate_footprints.py](test_candidate_footprints.py)

用途：验证重叠轮廓全部保留和缓冲范围外对象排除

输入：测试多边形与点

输出：unittest结果

运行条件：不是实际地理精度测试

### [test_candidate_support.py](test_candidate_support.py)

用途：测试过渡季度分离、无成交小区保留和重复交易拒绝

输入：程序内小型测试表

输出：unittest结果

运行条件：数据无关测试

### [test_daily_market_coverage.py](test_daily_market_coverage.py)

用途：测试缺月保留为空与重复日期拒绝

输入：临时日汇总样例

输出：unittest结果

运行条件：不读取真实数据

### [test_district_collisions.py](test_district_collisions.py)

用途：测试相同数值、面积不同和双字段不同的冲突分类

输入：两行数值样例

输出：unittest结果

运行条件：无需真实数据

### [test_download_data.py](test_download_data.py)

用途：测试下载哈希、已有文件保护、路径限制与包内核验

输入：临时测试文件

输出：unittest结果

运行条件：无需真实数据或网络

### [test_monthly_alias_sensitivity.py](test_monthly_alias_sensitivity.py)

用途：验证缺月为空、重复来源拒绝和相加记录的观测日计数

输入：月度聚合样例

输出：unittest结果

运行条件：无需真实数据

### [test_mutoulong_image_comparison.py](test_mutoulong_image_comparison.py)

用途：核对图像拟合与留出点分离、保存的像素误差

输入：已归档图纸比对CSV/JSON

输出：unittest结果

运行条件：不验证地理配准

### [test_mutoulong_native_grid.py](test_mutoulong_native_grid.py)

用途：校验45点编号、哈希、鞋带面积与未配准状态

输入：已归档原坐标网CSV/JSON

输出：unittest结果

运行条件：不确认CRS、轴序或真实单位

### [test_official_residential_names.py](test_official_residential_names.py)

用途：测试名称精确匹配、行政区限制及重复官方条目拒绝

输入：程序内名录样例

输出：unittest结果

运行条件：不认证楼栋和住宅用途

### [test_project_readiness.py](test_project_readiness.py)

用途：测试事件晚于截止、区间跨截止及日期缺失等情况

输入：日期区间样例

输出：unittest结果

运行条件：无需真实数据

### [test_residential_baseline.py](test_residential_baseline.py)

用途：测试平台成交与建成年代的证据分流逻辑

输入：程序内日期与年份样例

输出：unittest结果

运行条件：不证明住宅身份

### [test_residential_review_queue.py](test_residential_review_queue.py)

用途：验证20个线索完整保留、待确认状态及不完整或重复证据拒绝

输入：已归档五份证据CSV

输出：unittest结果

运行条件：不验证真实地理身份


<!-- generated-file-guide:end -->
