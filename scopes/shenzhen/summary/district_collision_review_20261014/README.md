# 行政区别名冲突逐组核查

198条来源记录构成99组同日、同用途、同标准化行政区的冲突，日期集中在2022-05-10至2022-08-09。95组套数和面积均不同，4组套数相同但面积不同，没有数值完全相同的组。

因此不能按名称别名重复直接去重，也不能把两行相加作为标准区总量。原ID与原区名仍保留在此前冲突原行表；本目录只对冲突分类，没有选择来源版本，没有改变此前月度结果。

后续[全市合计场景对账](../alias_scenario_review_20261014/README.md)发现：70个冲突日期—用途组中，两类区名记录相加全部吻合全市套数面积，择一则全部不吻合。这新增了内部可加性依据；上段的限制指不能未经来源核定接受正式主口径，不是断言两类记录数学上不可相加。

文件：collision_group_classification.csv列每组来源ID、区名、数值上下界和分类；collision_district_summary.csv按区和类别汇总；summary.json记录输入哈希与日期范围。来源是否反映修订、不同登记口径或其他原因仍未知，需要原提供者说明；ID大小不代表版本优先级。

复现脚本见[classify_district_collisions.py](../../scripts/classify_district_collisions.py)。本轮只分析行政区成交量与面积，不涉及逐小区价格或项目因果效应。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [collision_district_summary.csv](collision_district_summary.csv)

区名冲突按行政区和类别汇总的数量与日期范围。

### [collision_group_classification.csv](collision_group_classification.csv)

同日同用途区名冲突逐组数值分类与来源ID，不决定合并版本。

### [summary.json](summary.json)

所在分析批次的输入哈希、统计数量和研究状态。


<!-- generated-file-guide:end -->
