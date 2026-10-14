# 区名冲突与全市总量三场景对账

本轮从已核验的历史接口合并CSV读取冲突日原行，针对70个日期—用途组分别比较短区名优先、带区后缀优先、两种区名均计入三个假设。计数需精确相同，面积容差0.05平方米；没有回填缺区或缺日。

| 假设 | 可对账组数 | 同时吻合套数与面积 |
| --- | --- | --- |
| 短区名优先 | 70 | 0 |
| 带区后缀优先 | 70 | 0 |
| 两类原行相加 | 70 | 70 |

相加最大套数差为0，最大面积差约3.64×10⁻¹²平方米（浮点误差）。这是强的内部可加性线索，说明不能只依据标准化后同键而将记录视为重复，并反对盲目择一。数据提供者是否按渠道、登记类别或其他规则拆开记载，仍未知；不据对账宣称确认了分组含义或官方普查完整性。

此前“不能把两行相加”的表述应理解为在口径未核定前不能接受正式合并规则，本轮进一步发现相加能保持全市总量。既有月度隔离表不修改，读者不得把它标为完整月总量；后续如采用相加，需要明确标为内部对账支持的敏感性口径，而非来源核实后的主口径。

文件：alias_scenario_city_checks.csv为逐日逐用途对账，alias_scenario_summary.csv为假设汇总，summary.json含输入哈希、容差和未接受状态。脚本[reconcile_district_alias_scenarios.py](../../scripts/reconcile_district_alias_scenarios.py)不更改源文件或月度表。合并输入CSV及历史分页原件尚未进入公开Release，当前复现仍需该历史快照输入。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [alias_scenario_city_checks.csv](alias_scenario_city_checks.csv)

同日同用途区名三种候选合并方式与全市总量的差异，不是已接受规则。

### [alias_scenario_summary.csv](alias_scenario_summary.csv)

短名优先、后缀优先及两类相加的内部对账汇总。

### [summary.json](summary.json)

所在分析批次的输入哈希、统计数量和研究状态。


<!-- generated-file-guide:end -->
