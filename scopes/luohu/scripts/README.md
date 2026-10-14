# scopes/luohu/scripts / 中文说明

罗湖数据处理、身份诊断、片区估计与样本检查。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [audit_candidate_composition.py](audit_candidate_composition.py)

用途：按候选小区和时期检查面积、电梯、建成年代及楼层成交构成

输入：--sample、--transactions、--baseline输入；原成交哈希校验

输出：--output新目录的四份构成CSV与摘要

运行条件：不估计政策效应，不自动判定楼栋或剔除样本

### [audit_mutoulong_candidate_support.py](audit_mutoulong_candidate_support.py)

用途：统计三条道路地址线索小区的事件前后成交支持

输入：--sample、--coverage、--matches、--supplement四个CSV

输出：--output指定的新目录；621小区表及道路线索支持

运行条件：所有参数显式传入；拒绝覆盖已有输出；不定义项目处理组

### [audit_official_residential_names.py](audit_official_residential_names.py)

用途：从封存官方参考价格PDF提取表格，精确核对20个罗湖住宅名称并检查新增地址附件

输入：--roster、--queue、--huandao、--yangguang四份本地原件

输出：--output新目录的名称旁证、地址证据CSV和摘要

运行条件：需要PyMuPDF；参考价格不是成交价，名录旁证不接受楼栋坐标

### [build_luohu_residential_poi_20261012.py](build_luohu_residential_poi_20261012.py)

用途：按行政代码440303筛选POI，区分住宅主体、楼栋与出入口并连接同名小区

输入：原成交CSV、POI ZIP、解压SHP组件及既有回归摘要

输出：20261012_luohu_residential_poi/CSV、GPKG和摘要

运行条件：需配置环境变量与原组件目录；不接受坐标系

### [build_project_readiness.py](build_project_readiness.py)

用途：将已核定事件区间与交易截止日比较，整理17个项目准备状态

输入：项目线索、事件证据CSV与全市覆盖摘要

输出：--output新目录的准备表及摘要

运行条件：不补日期、不接受项目处理组，区分年度区间与具体事件

### [build_residential_review_queue.py](build_residential_review_queue.py)

用途：连接20个小区的地址、年代、成交支持和建筑假设，生成待人工核查清单

输入：--leads、--baseline、--support、--addresses、--atlas五份CSV

输出：--output新目录的逐小区CSV、摘要和中文README

运行条件：核对图像哈希；按成交笔数排序但不纳入样本、不接受住宅或坐标

### [check_price_did_influence_20261003.py](check_price_did_influence_20261003.py)

用途：逐小区、逐比较商圈留出及差异线性趋势敏感性

输入：analysis_sample.csv及主回归估计函数

输出：影响点CSV、趋势表、动态比较和影响图

运行条件：在主回归之后运行；不是正式项目ATT

### [check_price_did_support_20261003.py](check_price_did_support_20261003.py)

用途：检查前后交易支持，重估支持样本和伪事件诊断

输入：主回归生成的analysis_sample.csv及估计函数

输出：支持表、敏感性表、季度协方差及诊断摘要

运行条件：在主回归之后运行；会更新结果目录

### [collect_building_identity_evidence.py](collect_building_identity_evidence.py)

用途：取得官方楼栋标识线索并记录来源哈希，不推断楼栋与年代对应

输入：--archive本地原页目录、--output新的公开摘要目录

输出：楼栋线索CSV及JSON；原HTML仅存本地

运行条件：需联网curl；记录失败；不认证住宅、不拆样本

### [collect_redevelopment_plan_sources.py](collect_redevelopment_plan_sources.py)

用途：获取拆除重建项目官方计划与进展原件，三九计划附件单独归档

输入：--archive本地原件目录、--manifest公开来源清单

输出：六份正文与两附件下载记录、哈希和失败状态

运行条件：需联网curl；不自动认定开工或未来回迁

### [diagnose_candidate_footprints.py](diagnose_candidate_footprints.py)

用途：将20个住宅线索的三种坐标假设与供应建筑候选比较，保留所有50米候选

输入：--transactions封存成交CSV、--footprints候选GPKG、--leads地址线索表

输出：--output三种定位假设计数、全部50米候选及摘要

运行条件：不选最近建筑，不确认底层坐标、不计算项目距离

### [diagnose_poi_coordinate_frames_20261012.py](diagnose_poi_coordinate_frames_20261012.py)

用途：比较住宅与POI的九种坐标口径组合

输入：成交CSV、同名候选连接、固定版本坐标实现

输出：双端诊断CSV及摘要

运行条件：先运行POI筛选；一致性不是测量精度

### [extract_luohu_building_candidates.py](extract_luohu_building_candidates.py)

用途：用供应罗湖区界按声明CRS筛选建筑轮廓，保留原几何和属性，不认证住宅

输入：--buildings全市建筑SHP、--districts区界SHP、--output新目录

输出：候选GPKG、属性CSV、层数频数和来源哈希摘要

运行条件：跳过无效源几何并记录数量；边界和坐标均待独立验证

### [render_footprint_review_atlas.py](render_footprint_review_atlas.py)

用途：渲染20个住宅线索的三坐标假设审查图并核对既有候选计数

输入：--transactions原CSV、--footprints候选GPKG、--leads线索、--support既有60条诊断

输出：--output PNG图册、中文README和索引哈希

运行条件：每面板独立中心，图中编号为源行；无影像、无已接受楼栋或项目距离

### [review_jingji_name_bridge.py](review_jingji_name_bridge.py)

用途：核查京基东方华都与东方华都大厦的同门牌名称关联，汇总原成交字段及既有时期构成

输入：--transactions、--roster、--full、--short、--composition五份原件或既有证据

输出：--output新目录的名称证据、字段频数、时期构成和中文说明

运行条件：同门牌旁证不接受楼栋身份，保留街道差异，不重估效应

### [review_luohu_poi_ambiguity_20261012.py](review_luohu_poi_ambiguity_20261012.py)

用途：复核同名位置歧义、地址限定词、门点与主体线索

输入：--base指定公开派生POI目录，--transactions指定原成交CSV；按封存哈希校验并重建坐标登记

输出：--output指定新目录；身份候选、分流与摘要

运行条件：拒绝覆盖既有目录；--skip-official-fetch可离线复现，官方来源另行核验；不接受住宅位置

### [review_residential_baseline.py](review_residential_baseline.py)

用途：按最早成交及平台建成年代分流基期存在证据

输入：--sample、--coverage、--leads三个CSV

输出：--output指定的新目录；基期证据CSV与摘要

运行条件：先完成地址支持核查；不是官方竣工认证

### [run_price_did_audit_20261003.py](run_price_did_audit_20261003.py)

用途：运行罗湖商圈代理双向固定效应DID和季度动态模型

输入：SHENZHEN_TRANSACTION_CSV环境变量指定成交CSV

输出：outputs/price_did_audit_20261003/样本、回归、图和摘要

运行条件：需原交易数据；写入既有结果目录，先备份或用独立克隆运行


<!-- generated-file-guide:end -->
