# 05 / 测试与核验

测试、文件校验与公开目录完整性。

这里按用途导航到真实代码，不复制或移动当前执行文件。

## [test_luohu_poi_identity_review.py](../../scopes/luohu/tests/test_luohu_poi_identity_review.py)

**用途：**测试地址限定词处理并保护分期、楼栋和院区

**输入：**名称样例

**输出：**unittest结果

**运行条件：**不读取真实POI

路径：`scopes/luohu/tests/test_luohu_poi_identity_review.py`

## [test_luohu_residential_poi.py](../../scopes/luohu/tests/test_luohu_residential_poi.py)

**用途：**测试住宅类别、商业混合与入口分类

**输入：**名称/类别样例

**输出：**unittest结果

**运行条件：**不验证坐标或行政区数据质量

路径：`scopes/luohu/tests/test_luohu_residential_poi.py`

## [build_code_catalog.py](../../scripts/build_code_catalog.py)

**用途：**为全部Git跟踪Python文件生成中文分类说明与完整索引

**输入：**Git索引及本脚本用途映射

**输出：**Code_Revision六类README、CSV和JSON

**运行条件：**在git add之后运行；新脚本未登记会明确失败

路径：`scripts/build_code_catalog.py`

## [document_all_folders.py](../../scripts/document_all_folders.py)

**用途：**为所有Git跟踪目录补齐中文README及逐文件用途，保留已有说明

**输入：**Git索引、中文代码分类JSON及文件用途映射

**输出：**每个目录的README.md和子目录导航

**运行条件：**先更新代码分类，再生成目录说明；未知文件用途会失败

路径：`scripts/document_all_folders.py`

## [validate_public_repository.py](../../scripts/validate_public_repository.py)

**用途：**检查Git跟踪文件、原件哈希、链接、聚合数值和代码分类覆盖

**输入：**当前Git索引、来源清单与封存结果

**输出：**终端PASS或异常

**运行条件：**在git add之后运行；不重估模型

路径：`scripts/validate_public_repository.py`

## [test_candidate_composition.py](../../tests/test_candidate_composition.py)

**用途：**验证前段、过渡和后段正确分离

**输入：**季度样例

**输出：**unittest结果

**运行条件：**无需真实数据

路径：`tests/test_candidate_composition.py`

## [test_candidate_support.py](../../tests/test_candidate_support.py)

**用途：**测试过渡季度分离、无成交小区保留和重复交易拒绝

**输入：**程序内小型测试表

**输出：**unittest结果

**运行条件：**数据无关测试

路径：`tests/test_candidate_support.py`

## [test_daily_market_coverage.py](../../tests/test_daily_market_coverage.py)

**用途：**测试缺月保留为空与重复日期拒绝

**输入：**临时日汇总样例

**输出：**unittest结果

**运行条件：**不读取真实数据

路径：`tests/test_daily_market_coverage.py`

## [test_district_collisions.py](../../tests/test_district_collisions.py)

**用途：**测试相同数值、面积不同和双字段不同的冲突分类

**输入：**两行数值样例

**输出：**unittest结果

**运行条件：**无需真实数据

路径：`tests/test_district_collisions.py`

## [test_download_data.py](../../tests/test_download_data.py)

**用途：**测试下载哈希、已有文件保护、路径限制与包内核验

**输入：**临时测试文件

**输出：**unittest结果

**运行条件：**无需真实数据或网络

路径：`tests/test_download_data.py`

## [test_mutoulong_image_comparison.py](../../tests/test_mutoulong_image_comparison.py)

**用途：**核对图像拟合与留出点分离、保存的像素误差

**输入：**已归档图纸比对CSV/JSON

**输出：**unittest结果

**运行条件：**不验证地理配准

路径：`tests/test_mutoulong_image_comparison.py`

## [test_mutoulong_native_grid.py](../../tests/test_mutoulong_native_grid.py)

**用途：**校验45点编号、哈希、鞋带面积与未配准状态

**输入：**已归档原坐标网CSV/JSON

**输出：**unittest结果

**运行条件：**不确认CRS、轴序或真实单位

路径：`tests/test_mutoulong_native_grid.py`

## [test_project_readiness.py](../../tests/test_project_readiness.py)

**用途：**测试事件晚于截止、区间跨截止及日期缺失等情况

**输入：**日期区间样例

**输出：**unittest结果

**运行条件：**无需真实数据

路径：`tests/test_project_readiness.py`

## [test_residential_baseline.py](../../tests/test_residential_baseline.py)

**用途：**测试平台成交与建成年代的证据分流逻辑

**输入：**程序内日期与年份样例

**输出：**unittest结果

**运行条件：**不证明住宅身份

路径：`tests/test_residential_baseline.py`

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。


<!-- generated-file-guide:end -->
