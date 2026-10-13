# 复现指南

## 无原始数据核验

Python 3.11下安装`requirements.txt`，运行README中的测试和公开文件检查。依赖表不是封存环境锁文件；测试验证筛选逻辑与文件口径，不证明因果识别成立。

## 全市覆盖

`python scripts/download_data.py --scope luohu`下载并核验罗湖包，`--scope shenzhen`下载三份全市来源。默认写入被Git忽略的`data/raw/downloads/`，可用`--directory`指定位置。`--verify-only`仅检查已有文件，不联网。已有文件校验失败会报错而不是覆盖；工具不自动解压，避免原POI约2.15 GB的DBF意外占用空间。RAR只核验整个附件哈希，不宣称检查了内部文件。

将有权限使用的交易CSV传入`scopes/shenzhen/scripts/build_citywide_summary.py --input`。该脚本只输出行政区覆盖与来源哈希，不输出交易明细。源SHA-256为`b56310294f8b0288eba66c9852353c0339d4e9ba10fc0dadbcfa17ffad63bd22`。

## 罗湖重估

所需全市来源及罗湖派生文件可从[公开Release](https://github.com/sjkncs/shenzhen-housing-redevelopment/releases/tag/data-snapshot-20261012)下载。先按[校验清单](DATA_RELEASE_MANIFEST.json)核对哈希，再解压并配置输入。文件公开不改变坐标接受状态或因果识别结论。

在独立工作副本中运行，避免覆盖封存结果：

```powershell
$env:SHENZHEN_TRANSACTION_CSV = 'D:/authorized-data/transactions.csv'
python scopes/luohu/scripts/run_price_did_audit_20261003.py
python scopes/luohu/scripts/check_price_did_support_20261003.py
python scopes/luohu/scripts/check_price_did_influence_20261003.py
```

输出写入`scopes/luohu/outputs/price_did_audit_20261003/`。主脚本会生成`analysis_sample.csv`，它被Git忽略，不应随提交公开。

POI流程需设置`SHENZHEN_POI_ZIP`并将源组件按脚本所需路径放入`scopes/luohu/data/supplied_gdata_intake/20261011/poi_luohu/source_components/`。运行顺序为筛选、双端坐标诊断、身份歧义复核。坐标数学实现仅用于假设比较，不直接接受转换规则。第三方代码按固定提交和SHA核验，原许可保留。

GitHub Actions仅安装依赖、运行数据无关测试与公开文件/口径检查，不访问私有交易数据，不重估模型，也不宣称通过因果识别测试。
