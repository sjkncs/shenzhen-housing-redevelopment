# 03 / 价格回归与诊断

片区DID、动态估计、样本支持与敏感性。

这里按用途导航到真实代码，不复制或移动当前执行文件。

## [audit_candidate_composition.py](../../scopes/luohu/scripts/audit_candidate_composition.py)

**用途：**按候选小区和时期检查面积、电梯、建成年代及楼层成交构成

**输入：**--sample、--transactions、--baseline输入；原成交哈希校验

**输出：**--output新目录的四份构成CSV与摘要

**运行条件：**不估计政策效应，不自动判定楼栋或剔除样本

路径：`scopes/luohu/scripts/audit_candidate_composition.py`

## [check_price_did_influence_20261003.py](../../scopes/luohu/scripts/check_price_did_influence_20261003.py)

**用途：**逐小区、逐比较商圈留出及差异线性趋势敏感性

**输入：**analysis_sample.csv及主回归估计函数

**输出：**影响点CSV、趋势表、动态比较和影响图

**运行条件：**在主回归之后运行；不是正式项目ATT

路径：`scopes/luohu/scripts/check_price_did_influence_20261003.py`

## [check_price_did_support_20261003.py](../../scopes/luohu/scripts/check_price_did_support_20261003.py)

**用途：**检查前后交易支持，重估支持样本和伪事件诊断

**输入：**主回归生成的analysis_sample.csv及估计函数

**输出：**支持表、敏感性表、季度协方差及诊断摘要

**运行条件：**在主回归之后运行；会更新结果目录

路径：`scopes/luohu/scripts/check_price_did_support_20261003.py`

## [run_price_did_audit_20261003.py](../../scopes/luohu/scripts/run_price_did_audit_20261003.py)

**用途：**运行罗湖商圈代理双向固定效应DID和季度动态模型

**输入：**SHENZHEN_TRANSACTION_CSV环境变量指定成交CSV

**输出：**outputs/price_did_audit_20261003/样本、回归、图和摘要

**运行条件：**需原交易数据；写入既有结果目录，先备份或用独立克隆运行

路径：`scopes/luohu/scripts/run_price_did_audit_20261003.py`

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。


<!-- generated-file-guide:end -->
