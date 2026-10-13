# Code_Revision / 当前研究代码

当前可维护代码保留原运行路径，避免移动后破坏输入、测试和输出依赖。本目录提供清晰导航，不再复制一套可能漂移的代码。

## 完整中文分类

| 分类 | 包含的处理工作 |
| --- | --- |
| [01 数据获取与清洗](01_数据获取与清洗/README.md) | 分区下载、附件校验、全市清洗与覆盖统计 |
| [02 空间与住宅身份](02_空间与住宅身份/README.md) | 罗湖POI、坐标诊断、名称歧义、地址支持与基期证据 |
| [03 价格回归与诊断](03_价格回归与诊断/README.md) | 片区DID、动态路径、支持度及影响点敏感性 |
| [04 材料归档与文献](04_材料归档与文献/README.md) | 数据打包、PPT/报告归档、参考文献提取 |
| [05 测试与核验](05_测试与核验/README.md) | 自动测试、目录及数值核验 |
| [06 原始代码与第三方](06_原始代码与第三方/README.md) | 原执行快照、固定版本坐标数学实现与许可 |

每个脚本说明包含中文用途、输入、输出和运行条件。完整列表见[代码用途索引CSV](代码用途索引.csv)与[机器可读分类](code_catalog.json)。自动核验会检查所有Git跟踪Python文件是否登记，防止新代码遗漏说明。

## 推荐运行顺序

先下载并核验公开数据，解压所需输入。全市统计可独立运行；罗湖价格流程先执行主DID，再执行支持与影响点检验。空间流程先筛选POI，再诊断坐标，最后复核身份；地址支持先于基期证据分流。代码测试无需运行全量数据流程。

**身份复核的全量流程尚有额外输入缺口**：`review_luohu_poi_ambiguity_20261012.py`需要小区原坐标登记表，现有Release未包含该表。原坐标网及图纸叠加结果目前公开的是成果和检查测试，相关本地生产脚本尚未全部纳入本公开目录；不宣称所有空间结果可一键重建。

| 任务 | 当前入口 |
| --- | --- |
| 全市清洗与分区统计 | [build_citywide_summary.py](../scopes/shenzhen/scripts/build_citywide_summary.py) |
| 罗湖片区DID | [run_price_did_audit_20261003.py](../scopes/luohu/scripts/run_price_did_audit_20261003.py) |
| 住宅POI筛选 | [build_luohu_residential_poi_20261012.py](../scopes/luohu/scripts/build_luohu_residential_poi_20261012.py) |
| 坐标诊断 | [diagnose_poi_coordinate_frames_20261012.py](../scopes/luohu/scripts/diagnose_poi_coordinate_frames_20261012.py) |
| 地址线索成交支持 | [audit_mutoulong_candidate_support.py](../scopes/luohu/scripts/audit_mutoulong_candidate_support.py) |
| 基期存在证据分流 | [review_residential_baseline.py](../scopes/luohu/scripts/review_residential_baseline.py) |
| 数据下载与核验 | [download_data.py](../scripts/download_data.py) |

当前版本相对于原执行代码增加公开输入路径、分区导航及资料检查；模型结果的变化必须通过真实重估另行记录，不以目录整理代替研究进展。
