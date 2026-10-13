# Dataset / 数据集

全市与罗湖分开组织。原始和派生大数据通过[公开Release](https://github.com/sjkncs/shenzhen-housing-redevelopment/releases/tag/data-snapshot-20261012)下载；Git只保存汇总、代码和校验清单，避免重复提交大数据。

| 范围 | 入口 | 内容 |
| --- | --- | --- |
| Shenzhen / 全市 | [全市说明](../scopes/shenzhen/README.md) | 139,514条原始交易、全市POI及建筑来源；清洗覆盖132,774条 |
| Luohu / 罗湖 | [罗湖说明](../scopes/luohu/README.md) | 16,199条清洗覆盖；公开派生包含片区动态样本、POI明细和GPKG |
| 来源与校验 | [下载说明](../docs/DATA_ACCESS.md) | 附件大小、哈希、字段、许可与解释范围 |

```bash
python scripts/download_data.py --scope luohu
python scripts/download_data.py --scope shenzhen
```

文件公开不等于住宅身份、坐标或项目因果效应已经验证。
