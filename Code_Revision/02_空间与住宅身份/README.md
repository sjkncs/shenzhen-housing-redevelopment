# 02 / 空间与住宅身份

行政区POI筛选、坐标假设及住宅身份线索。

这里按用途导航到真实代码，不复制或移动当前执行文件。

## [audit_mutoulong_candidate_support.py](../../scopes/luohu/scripts/audit_mutoulong_candidate_support.py)

**用途：**统计三条道路地址线索小区的事件前后成交支持

**输入：**--sample、--coverage、--matches、--supplement四个CSV

**输出：**--output指定的新目录；621小区表及道路线索支持

**运行条件：**所有参数显式传入；拒绝覆盖已有输出；不定义项目处理组

路径：`scopes/luohu/scripts/audit_mutoulong_candidate_support.py`

## [build_luohu_residential_poi_20261012.py](../../scopes/luohu/scripts/build_luohu_residential_poi_20261012.py)

**用途：**按行政代码440303筛选POI，区分住宅主体、楼栋与出入口并连接同名小区

**输入：**原成交CSV、POI ZIP、解压SHP组件及既有回归摘要

**输出：**20261012_luohu_residential_poi/CSV、GPKG和摘要

**运行条件：**需配置环境变量与原组件目录；不接受坐标系

路径：`scopes/luohu/scripts/build_luohu_residential_poi_20261012.py`

## [build_project_readiness.py](../../scopes/luohu/scripts/build_project_readiness.py)

**用途：**将已核定事件区间与交易截止日比较，整理17个项目准备状态

**输入：**项目线索、事件证据CSV与全市覆盖摘要

**输出：**--output新目录的准备表及摘要

**运行条件：**不补日期、不接受项目处理组，区分年度区间与具体事件

路径：`scopes/luohu/scripts/build_project_readiness.py`

## [collect_building_identity_evidence.py](../../scopes/luohu/scripts/collect_building_identity_evidence.py)

**用途：**取得官方楼栋标识线索并记录来源哈希，不推断楼栋与年代对应

**输入：**--archive本地原页目录、--output新的公开摘要目录

**输出：**楼栋线索CSV及JSON；原HTML仅存本地

**运行条件：**需联网curl；记录失败；不认证住宅、不拆样本

路径：`scopes/luohu/scripts/collect_building_identity_evidence.py`

## [collect_redevelopment_plan_sources.py](../../scopes/luohu/scripts/collect_redevelopment_plan_sources.py)

**用途：**获取拆除重建项目官方计划与进展原件，三九计划附件单独归档

**输入：**--archive本地原件目录、--manifest公开来源清单

**输出：**六份正文与两附件下载记录、哈希和失败状态

**运行条件：**需联网curl；不自动认定开工或未来回迁

路径：`scopes/luohu/scripts/collect_redevelopment_plan_sources.py`

## [diagnose_poi_coordinate_frames_20261012.py](../../scopes/luohu/scripts/diagnose_poi_coordinate_frames_20261012.py)

**用途：**比较住宅与POI的九种坐标口径组合

**输入：**成交CSV、同名候选连接、固定版本坐标实现

**输出：**双端诊断CSV及摘要

**运行条件：**先运行POI筛选；一致性不是测量精度

路径：`scopes/luohu/scripts/diagnose_poi_coordinate_frames_20261012.py`

## [review_luohu_poi_ambiguity_20261012.py](../../scopes/luohu/scripts/review_luohu_poi_ambiguity_20261012.py)

**用途：**复核同名位置歧义、地址限定词、门点与主体线索

**输入：**--base指定公开派生POI目录，--transactions指定原成交CSV；按封存哈希校验并重建坐标登记

**输出：**--output指定新目录；身份候选、分流与摘要

**运行条件：**拒绝覆盖既有目录；--skip-official-fetch可离线复现，官方来源另行核验；不接受住宅位置

路径：`scopes/luohu/scripts/review_luohu_poi_ambiguity_20261012.py`

## [review_residential_baseline.py](../../scopes/luohu/scripts/review_residential_baseline.py)

**用途：**按最早成交及平台建成年代分流基期存在证据

**输入：**--sample、--coverage、--leads三个CSV

**输出：**--output指定的新目录；基期证据CSV与摘要

**运行条件：**先完成地址支持核查；不是官方竣工认证

路径：`scopes/luohu/scripts/review_residential_baseline.py`

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。


<!-- generated-file-guide:end -->
