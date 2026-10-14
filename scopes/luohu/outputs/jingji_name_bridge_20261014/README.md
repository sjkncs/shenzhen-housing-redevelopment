# 京基东方华都名称与住宅记录核查

## 本轮证据

平台称“京基东方华都”；官方住宅小区参考价表第7页、序号291称“东方华都大厦”，街道记为东门。教育设立公告以“京基东方华都大厦”关联文锦中路2063号裙楼；物业检查页以“东方华都”关联同门牌地下室。

**判断：同门牌的名称关联旁证成立，逐套住宅与具体楼栋对应关系仍待核定。** 官方名录没有门牌；本轮没有建立无歧义的官方物业编号链。因此保留上一轮14个完全同名结果，不将名称关联计入第15个精确匹配。

## 平台数据与现有窗口

封存原文件按小区ID筛出149条，日期2011-01-20至2024-03-21。全部记录的用途均以平台原字段为准，不升级为官方用途认定。字段频数见CSV。

既有清洗窗口为118笔，前段76、过渡季度7、后段35。直接引用既有构成表，未重估因果效应。原149条与窗口118笔的时间范围和筛选条件不同，不能混用。

原文件建成年代2005年148条、2006年1条。没有楼栋编号证据，不能据此将交易拆成不同楼栋或分期。

## 行政归属与后续

平台商圈原字段为螺岭，不能当作街道。名录和物业页记东门；既有2021年卫生检查机构地址记翠竹。保留原文差异，不按多数票或商圈强改行政归属，也不以裙楼经营、泳池或地下室记录认定整栋商业或住宅用途。

接下来需取得可对应住宅主体的官方物业/楼栋编号、独立地理位置或宗地资料，再检验与平台小区ID的连接；当前不指定建筑轮廓、不计算项目边界距离、不分配处理组。

## 来源与运行

[official_roster](https://www.sz.gov.cn/attachment/0/749/749839/8545776.pdf)：PDF第7页，序号291
[full_name_address](https://www.szlh.gov.cn/lhjyjdds/gkmlpt/content/11/11008/post_11008298.html)：2023-11-28设立公告的办学地址段
[short_name_address](https://www.szlh.gov.cn/zwgk/ssjygkzl/content/post_9931859.html)：2022-07-05物业检查页，同一表格行

[既有2021年地址记录](https://www.szlh.gov.cn/zwfw/yljk/tzgg/content/post_10111558.html)仅用于说明未解决的街道差异。

脚本`scopes/luohu/scripts/review_jingji_name_bridge.py`：`--transactions`封存原成交CSV，`--roster`官方参考价原PDF，`--full`教育公告HTML，`--short`物业检查HTML，`--composition`既有时期构成CSV，`--output`新目录。

依赖pandas、BeautifulSoup、PyMuPDF。校验原成交及名录哈希；要求门牌和名称出现在同一段或表格行；原网页保留本地，公开证据表只提供来源、定位和哈希。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [jingji_existing_period_composition.csv](jingji_existing_period_composition.csv)

从既有构成表摘录该小区118笔窗口成交的前段、过渡与后段构成，不重估效应。

### [jingji_name_bridge_evidence.csv](jingji_name_bridge_evidence.csv)

京基东方华都的官方名录、带前缀和不带前缀门牌名称关联来源及哈希，不接受楼栋。

### [jingji_source_field_counts.csv](jingji_source_field_counts.csv)

按指定小区ID汇总原149条成交的用途、年代、建筑类型与商圈字段频数，非官方认定。

### [summary.json](summary.json)

所在分析批次的输入哈希、统计数量和研究状态。


<!-- generated-file-guide:end -->
