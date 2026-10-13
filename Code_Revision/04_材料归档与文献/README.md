# 04 / 材料归档与文献

公开材料复制、参考文献提取与数据打包。

这里按用途导航到真实代码，不复制或移动当前执行文件。

## [archive_report_references.py](../../scripts/archive_report_references.py)

**用途：**存档指定报告，提取28条参考文献和DOI入口

**输入：**--report DOCX与--ppt PPTX

**输出：**Draft原件、References Markdown/CSV和来源JSON

**运行条件：**维护者工具；当前期待28条，不是文献真实性核验

路径：`scripts/archive_report_references.py`

## [organize_research_archive.py](../../scripts/organize_research_archive.py)

**用途：**复制PPT、历史报告及六份原执行代码，生成归档清单与复现HTML

**输入：**--private-archive指定已有私有整理目录

**输出：**Draft、PPT、Code_Original及归档JSON、HTML

**运行条件：**维护者工具；保留已有副本字节；会重建初始归档清单，新增版本后不能盲目重跑

路径：`scripts/organize_research_archive.py`

## [prepare_authorized_data_release.py](../../scripts/prepare_authorized_data_release.py)

**用途：**打包全市来源与14份罗湖派生文件并校验包内哈希

**输入：**--private-tree及三份源附件、--output

**输出：**罗湖ZIP及docs/DATA_RELEASE_MANIFEST.json

**运行条件：**维护者归档工具；需要完整输入；会重写指定输出包和清单

路径：`scripts/prepare_authorized_data_release.py`
