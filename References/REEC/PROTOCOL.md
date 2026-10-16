# 检索与逆向协议

## 检索范围

暂按Real Estate Economics检索。出版社主页 https://onlinelibrary.wiley.com/journal/15406229 。Crossref入口 https://api.crossref.org/journals/1540-6229/works 。检索日期2026-10-16。

Crossref每页1000条，cursor从星号开始，后续使用响应的next-cursor；依DOI去重。完整查询URL、取回时间、响应SHA-256与分页条数存search_manifest.json。查询仅选书目字段，不下载正文或摘要。响应哈希记录来源，不代表独立完整性认证；本轮没有上传原始响应字节。

## 筛选

关键词组完整保存在manifest：更新/拆除、邻里外部性与资本化、ML与图像、住房供给。筛选仅检查英文标题，103条不能称为103篇已确认相关论文。人工补入Houston一文，因此screening.csv为104条。

标题法会漏掉未显式提及机制的论文；会误收REIT风险、按揭或邻里人口论文。下一轮须人工检查全部目录，回溯引文与作者页面，并对非命中记录抽样审计。以journal_catalog.json和出版社目录交叉核对，不能报告当前为系统综述完成。

历史AREUEA名称、跨ISSN链接和新近Early View登记可能不完整。目录可能含未来卷期日期，应按首次公开日期核定截止时间，而非按issue日期机械排除。本轮元数据保留日期原值，不宣称所有条目均为截止日前可读全文。

## 研究卡片证据层级

metadata_only：只有目录标题/DOI；不能写研究设计细节。

publisher_abstract_verified：已核对出版社摘要；不填摘要之外的方程、控制项、聚类方案或具体样本清洗。

selected_full_text_sections_verified：核对列明的正文关键章节；不代表全文、所有附录或数值逐项复核。

replication_completed：需要数据、代码版本、许可、环境、命令、种子、容差与观察结果，当前没有条目达到这一层。

## 逐篇追加清单

核定正式题名/作者/卷期；记录来源版本；锁定结果变量、观测单元、处理与时间；列出识别假设；逐个表图追溯到数据和估计；记录负结果；验证代码许可和下载行为；只在隔离环境运行；最后填写实际复现值。缺失字段保留待核定，不用推测补全。
