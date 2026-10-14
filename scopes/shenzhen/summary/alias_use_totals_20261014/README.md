# 原行政区名称的分用途合计核查

历史快照中带“区”后缀的107行涉及7个行政区，日期为2022-05-10至2022-08-09。本轮取这些后缀记录的53个原区名—日期组，并检查同日对应短名称组，不与其他日期混合。

| 记录类型 | 日组数 | 可核对 | 套数面积合计吻合 |
| --- | ---: | ---: | ---: |
| 短名称 | 53 | 53 | 53 |
| 带区后缀 | 53 | 53 | 53 |

每组将已报告住宅、商业、办公等用途与该原名称“全部”比较。套数精确核对，面积容差0.05㎡，不把缺失类别填0。这里的53个区—日期组与此前70个日期—用途组属于不同分组口径，数量不同不是冲突。

结合此前两类相加与全市一致的对账，资料更像两个各自内部自洽、共同计入全市的分组，而非简单重复或任选其一的修订版本。具体业务含义仍未知，不标注为已确认交易渠道、登记类型或可直接合并的主口径。

所有月度表保持原样，新增结果仅供口径核查。下一步需要提供者说明原区名后缀、统计日期、成交定义及缺行含义；不再仅靠更多内部拟合认定业务规则。

脚本[audit_alias_use_totals.py](../../scripts/audit_alias_use_totals.py)需历史合并CSV，仍未随公开Release提供原分页输入。original_label_use_reconciliation.csv为逐组对账，label_type_check_summary.csv为两类汇总，summary.json为来源哈希及未接受状态。公开研究价格仍需周边小区成交，不由行政区套数面积替代。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [label_type_check_summary.csv](label_type_check_summary.csv)

短名称和带区后缀名称各自用途合计检查汇总。

### [original_label_use_reconciliation.csv](original_label_use_reconciliation.csv)

各原始区名按日的全部与分用途对账，不合并区名或推断渠道。

### [summary.json](summary.json)

所在分析批次的输入哈希、统计数量和研究状态。


<!-- generated-file-guide:end -->
