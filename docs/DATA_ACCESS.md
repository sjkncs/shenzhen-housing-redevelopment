# 数据下载与来源

仓库所有者于2026年10月12日明确授权公开分享研究数据。全市来源原样发布，罗湖派生文件单独打包。所有者授权不等于平台或提供者另行授予了开放许可；不虚构第三方许可，不对第三方数据附加MIT或CC授权。

| 范围 | 下载 | 大小 | 内容 |
| --- | --- | --- | --- |
| 全市交易 | [shenzhen-transactions-source.zip](https://github.com/sjkncs/shenzhen-housing-redevelopment/releases/download/data-snapshot-20261012/shenzhen-transactions-source.zip) | 7.01 MB | 原始139,514条，CSV解压约61.35 MB |
| 全市POI | [shenzhen-poi-source.zip](https://github.com/sjkncs/shenzhen-housing-redevelopment/releases/download/data-snapshot-20261012/shenzhen-poi-source.zip) | 99.13 MB | 788,695个POI，Shapefile组件；DBF解压约2.15 GB |
| 全市建筑 | [shenzhen-buildings-source.rar](https://github.com/sjkncs/shenzhen-housing-redevelopment/releases/download/data-snapshot-20261012/shenzhen-buildings-source.rar) | 10.99 MB | 用户提供的建筑轮廓Shapefile |
| 罗湖派生 | [luohu-derived-data.zip](https://github.com/sjkncs/shenzhen-housing-redevelopment/releases/download/data-snapshot-20261012/luohu-derived-data.zip) | 6.56 MB | 14份CSV/GPKG及逐文件SHA-256 |

完整校验值见[DATA_RELEASE_MANIFEST.json](DATA_RELEASE_MANIFEST.json)。大数据以[Release附件](https://github.com/sjkncs/shenzhen-housing-redevelopment/releases/tag/data-snapshot-20261012)提供，克隆仓库不会自动下载。

交易字段包括成交与挂牌日期、价格、面积、楼层、小区坐标、平台房源链接及编号。未发现专门的业主姓名或联系方式字段，但组合信息及原平台链接可能定位具体房源。数据未匿名化，不应称为匿名数据集；不用于识别业主或联系住户。

POI包含名称、地址、类别和坐标；建筑数据含几何及原始属性。源坐标声明与底层地图框架不是同一回事，POI坐标口径和采集日期仍待独立确认。原POI压缩包的文件名编码可能在某些工具中显示乱码；不要因此改写几何或假定坐标。

罗湖包的`transactions/analysis_sample.csv`为片区动态模型的11,231条样本，不是全部16,199条清洗记录。`poi/`分成住宅候选和身份核验资料；GPKG包含66,278条罗湖POI和2,803条住宅/门点候选两层，不代表2,803个住宅小区。ZIP内附`FILE_MANIFEST.json`。

```powershell
Get-FileHash ./luohu-derived-data.zip -Algorithm SHA256
```

原始成交CSV哈希为`b56310294f8b0288eba66c9852353c0339d4e9ba10fc0dadbcfa17ffad63bd22`。下载后按清单核验，运行见[复现指南](REPRODUCTION.md)。

正式项目红线DID、ATT及机制结果仍待完成，公开下载不改变识别结论。含姓名学号的报告、PPT和任务书不属于本次数据Release，仍保留私有档案。来源方如提出权利或隐私问题，可通过Issue联系维护者，请勿再次贴出逐条房源或个人信息。
