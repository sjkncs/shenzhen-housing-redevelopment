# 住宅候选点与建筑轮廓的坐标假设检查

本轮用20个道路地址候选的原平台小区坐标，分别按原值为WGS84、GCJ-02、BD-09作诊断。建筑源暂按其EPSG:4326声明解释，仅在该假设下投影EPSG:4547计算点与轮廓的诊断关系，未接受底层地图框架。住宅每种原坐标对保留，缺失或多值不强制择一。

| 住宅原坐标假设 | 检查点数 | 有覆盖点的建筑轮廓 | 50米内有候选 |
| --- | ---: | ---: | ---: |
| BD-09 | 20 | 10 | 20 |
| GCJ-02 | 20 | 6 | 16 |
| WGS84 | 20 | 1 | 11 |

BD-09假设相对更一致，与此前POI诊断方向相符，但不能当作独立测绘认证；来源是否共享地图偏移、建筑采集时点和小区点含义仍未知。小区点可能是入口、中心或平台代表点，不必落在某个建筑内部。高覆盖率不证明对应楼栋正确，低覆盖率也不直接证明坐标错误。

保留60个诊断点方案和356条方案—建筑候选连接，50米阈值仅作人工查图线索，未以最近建筑自动接受住宅身份。重叠轮廓可保留多个，没有选中楼栋、覆盖原坐标、生成木头龙距离或新DID。

`hypothesis_distance_m`是在“建筑源声明坐标为真实WGS84”假设下的投影距离，不是已经验证的地面距离。原候选中134个跨区/触界对象也仍是供应边界下的定位候选。Floor未认证为实际层数。

文件：coordinate_hypothesis_footprint_support.csv逐小区列三种假设的覆盖与50米计数；all_50m_footprint_candidates.csv保留全部候选ID、源层数和诊断关系；summary.json记录来源哈希与未接受状态。公开CSV不包含额外业主身份或精确房号。

脚本[diagnose_candidate_footprints.py](../../scripts/diagnose_candidate_footprints.py)使用公开交易包、建筑候选Release及现有地址表，可显式配置输入；固定版本数学实现按SHA核验。本轮统计是人工审查准备，不是房屋—楼栋空间连接的最终结果。

下一步应优先对有多个覆盖轮廓、没有覆盖轮廓及位置歧义的小区检查地图代表点、楼栋名和历史影像。独立地址与测量依据优先，不按该表中距离最小的候选补填楼栋。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [all_50m_footprint_candidates.csv](all_50m_footprint_candidates.csv)

三种地图坐标假设下全部50米候选轮廓，不按最近点接受身份。

### [coordinate_hypothesis_footprint_support.csv](coordinate_hypothesis_footprint_support.csv)

住宅原坐标三种假设的落入建筑与50米候选计数，不选楼栋。

### [summary.json](summary.json)

所在分析批次的输入哈希、统计数量和研究状态。


<!-- generated-file-guide:end -->
