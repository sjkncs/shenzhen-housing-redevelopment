# Research Replication / 研究复现说明

本仓库按研究归档习惯提供原始代码、当前代码、数据、报告、日志、PPT和参考资料入口，同时保留实际运行所需的scopes/与scripts/目录。全市部分是数据基础，罗湖部分是片区诊断与木头龙项目准备。

## 目录

| 顶层入口 | 用途 |
| --- | --- |
| AGENTS.md / CLAUDE.md | 智能体维护约定 |
| Code_Original | 原执行代码封存，不覆盖 |
| Code_Revision | 当前可执行代码导航 |
| Dataset | 全市与罗湖数据说明及Release下载 |
| Draft | 现有开题报告DOCX/PDF，不是最终论文 |
| Logfiles | 文件来源校验与实际CI/模型日志入口 |
| PPT | 用户指定的10.7开题报告PPT原件 |
| References | 文献与官方资料索引 |
| README_replication.html | 可本地浏览的本说明HTML版本 |

## 检查环境

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s scopes/luohu/tests -p "test_luohu_*.py"
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_public_repository.py
```

数据与下载：运行`python scripts/download_data.py --scope luohu`或`--scope shenzhen`。默认不解压、不覆盖；校验附件哈希及罗湖包内文件。输入字段与估计命令见[复现指南](docs/REPRODUCTION.md)。

## 结果解释

全市来源139,514条原始交易，经规则清洗132,774条；罗湖16,199条、621小区。片区DID主模型10,867条、607小区，动态模型11,231条、610小区。事件前差异显著，不能把显著事后系数当成木头龙因果效应。

项目坐标系、官方转换成果和住宅空间归属仍未核定。图像轮廓比对、面积接近、道路地址及成交前后覆盖均是中间证据，不是完成红线DID。住宅基期核查也以平台记载为线索，不代替官方竣工或权籍依据。

## 文件版本

PPT与报告是用户本次要求公开的现有学术材料，保留原封面、署名与备注；本次仅整理，不改稿。仍含较宽研究范围，未全部同步为当前单案例设计。任务书、导师反馈及其他个人文件不因本次请求自动公开。

原件与代码快照逐文件SHA-256见[归档清单](Logfiles/artifact_manifest.json)。代码公开可读与数据下载授权不等于第三方资料获得统一开源许可。
