# 01 / 数据获取与清洗

下载、输入校验、全市清洗与覆盖统计。

这里按用途导航到真实代码，不复制或移动当前执行文件。

## [build_citywide_summary.py](../../scopes/shenzhen/scripts/build_citywide_summary.py)

**用途：**清洗全市平台交易，统计行政区覆盖

**输入：**--input指定原始成交CSV

**输出：**scopes/shenzhen/summary/区级CSV和JSON

**运行条件：**需先下载交易包并解压；不会输出逐套记录

路径：`scopes/shenzhen/scripts/build_citywide_summary.py`

## [download_data.py](../../scripts/download_data.py)

**用途：**按全市或罗湖下载公开数据，核验SHA-256；不自动解压

**输入：**Release清单；可选已有下载文件

**输出：**data/raw/downloads/中的已核验附件

**运行条件：**可直接运行；默认联网下载

路径：`scripts/download_data.py`
