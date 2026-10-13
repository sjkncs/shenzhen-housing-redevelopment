# Code_Original/20261012_snapshot / 中文说明

原执行代码的封存快照，不在此修改或直接跨机器运行。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [build_luohu_residential_poi_20261012.py](build_luohu_residential_poi_20261012.py)

用途：按行政代码440303筛选POI，区分住宅主体、楼栋与出入口并连接同名小区

输入：原成交CSV、POI ZIP、解压SHP组件及既有回归摘要

输出：20261012_luohu_residential_poi/CSV、GPKG和摘要

运行条件：原字节封存；有历史工作站路径，不是当前可移植入口

### [check_price_did_influence_20261003.py](check_price_did_influence_20261003.py)

用途：逐小区、逐比较商圈留出及差异线性趋势敏感性

输入：analysis_sample.csv及主回归估计函数

输出：影响点CSV、趋势表、动态比较和影响图

运行条件：原字节封存；有历史工作站路径，不是当前可移植入口

### [check_price_did_support_20261003.py](check_price_did_support_20261003.py)

用途：检查前后交易支持，重估支持样本和伪事件诊断

输入：主回归生成的analysis_sample.csv及估计函数

输出：支持表、敏感性表、季度协方差及诊断摘要

运行条件：原字节封存；有历史工作站路径，不是当前可移植入口

### [diagnose_poi_coordinate_frames_20261012.py](diagnose_poi_coordinate_frames_20261012.py)

用途：比较住宅与POI的九种坐标口径组合

输入：成交CSV、同名候选连接、固定版本坐标实现

输出：双端诊断CSV及摘要

运行条件：原字节封存；有历史工作站路径，不是当前可移植入口

### [review_luohu_poi_ambiguity_20261012.py](review_luohu_poi_ambiguity_20261012.py)

用途：复核同名位置歧义、地址限定词、门点与主体线索

输入：POI候选、覆盖、18个异常诊断及小区原始坐标登记表

输出：20261012_luohu_poi_identity_review/线索与来源记录

运行条件：原字节封存；有历史工作站路径，不是当前可移植入口

### [run_price_did_audit_20261003.py](run_price_did_audit_20261003.py)

用途：运行罗湖商圈代理双向固定效应DID和季度动态模型

输入：SHENZHEN_TRANSACTION_CSV环境变量指定成交CSV

输出：outputs/price_did_audit_20261003/样本、回归、图和摘要

运行条件：原字节封存；有历史工作站路径，不是当前可移植入口


<!-- generated-file-guide:end -->
