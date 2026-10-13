# Code_Revision / 当前研究代码

当前可维护代码保留原运行路径，避免移动后破坏输入、测试和输出依赖。本目录提供清晰导航，不再复制一套可能漂移的代码。

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
