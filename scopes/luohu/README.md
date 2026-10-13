# Luohu / 罗湖案例与空间核验

本目录将罗湖实证与全市来源汇总分开。木头龙是优先主案例，其他指定项目只是潜在比较与项目档案线索。

| 内容 | 文件位置 | 状态 |
| --- | --- | --- |
| 基准片区代理DID | `outputs/price_did_audit_20261003/main_did.csv` | 已运行，不等于正式项目ATT |
| 动态路径及事件前检验 | 同目录`event_study.csv`、`run_summary.json` | 已运行；事件前变化显著 |
| 支持度、时间切点与线性趋势敏感性 | 同目录诊断表 | 已运行，不能修复所有混杂 |
| POI筛选与限定词保护 | `scripts/`与`tests/` | 类别、名称逻辑已测试 |
| 六个指定候选项目 | [project_registry](project_registry/README.md) | 每个项目的阶段须分别核定 |
| 木头龙J1—J45转录及原坐标网拓扑 | [45点资料](project_registry/mutoulong/native_grid_2019/README.md) | 已转录、检查，尚未地理配准 |
| 相关道路住宅线索与成交支持 | [20个地址线索](outputs/mutoulong_address_support_20261013/README.md) | 366笔窗口内成交；不是项目处理样本 |
| 红线归属、正式项目效应与机制 | 尚无对应结果表 | 待完成 |

清洗交易16,199条、621个小区；主回归10,867条、607个小区，动态模型11,231条、610个小区。不同数量由时间窗口与过渡季度处理产生，不是数据冲突。

罗湖POI行政代码为440303，共66,278条；住宅相关类别候选2,803条含出入口与楼栋。源文件声明EPSG:3857，并不独立证明底层地图坐标口径。名称吻合与较短点对距离不是完成空间归属的证据。

罗湖分析样本、POI候选和GPKG已在[luohu-derived-data.zip](https://github.com/sjkncs/shenzhen-housing-redevelopment/releases/download/data-snapshot-20261012/luohu-derived-data.zip)公开。代码目录保留模型汇总，大数据单独下载。回归数学逻辑保留，公开适配只改目录、输入路径与必要建目录逻辑。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

## 子目录导航

- [data](data/README.md)：空间来源和固定版本第三方实现，大数据从Release下载。
- [outputs](outputs/README.md)：已运行的罗湖结果，按批次分开，注意正式项目识别仍待完成。
- [project_registry](project_registry/README.md)：详见子目录中文说明。
- [scripts](scripts/README.md)：罗湖数据处理、身份诊断、片区估计与样本检查。
- [tests](tests/README.md)：罗湖名称限定词、住宅类别及门点规则的测试。

<!-- generated-file-guide:end -->
