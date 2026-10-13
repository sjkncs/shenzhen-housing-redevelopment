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

## [diagnose_poi_coordinate_frames_20261012.py](../../scopes/luohu/scripts/diagnose_poi_coordinate_frames_20261012.py)

**用途：**比较住宅与POI的九种坐标口径组合

**输入：**成交CSV、同名候选连接、固定版本坐标实现

**输出：**双端诊断CSV及摘要

**运行条件：**先运行POI筛选；一致性不是测量精度

路径：`scopes/luohu/scripts/diagnose_poi_coordinate_frames_20261012.py`

## [review_luohu_poi_ambiguity_20261012.py](../../scopes/luohu/scripts/review_luohu_poi_ambiguity_20261012.py)

**用途：**复核同名位置歧义、地址限定词、门点与主体线索

**输入：**POI候选、覆盖、18个异常诊断及小区原始坐标登记表

**输出：**20261012_luohu_poi_identity_review/线索与来源记录

**运行条件：**依赖额外登记表data/acquisition/community_matching/20260926T081831338704Z/深圳小区身份与原始坐标.csv，当前Release未含该表；不能直接全量复现

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
