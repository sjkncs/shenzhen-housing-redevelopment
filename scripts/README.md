# scripts / 中文说明

仓库维护、下载、材料归档及完整性检查工具。

<!-- generated-file-guide:start -->
## 逐文件中文说明

文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。

### [archive_report_references.py](archive_report_references.py)

用途：存档指定报告，提取28条参考文献和DOI入口

输入：--report DOCX与--ppt PPTX

输出：Draft原件、References Markdown/CSV和来源JSON

运行条件：维护者工具；当前期待28条，不是文献真实性核验

### [build_code_catalog.py](build_code_catalog.py)

用途：为全部Git跟踪Python文件生成中文分类说明与完整索引

输入：Git索引及本脚本用途映射

输出：Code_Revision六类README、CSV和JSON

运行条件：在git add之后运行；新脚本未登记会明确失败

### [document_all_folders.py](document_all_folders.py)

用途：为所有Git跟踪目录补齐中文README及逐文件用途，保留已有说明

输入：Git索引、中文代码分类JSON及文件用途映射

输出：每个目录的README.md和子目录导航

运行条件：先更新代码分类，再生成目录说明；未知文件用途会失败

### [download_data.py](download_data.py)

用途：按全市或罗湖下载公开数据，核验SHA-256；不自动解压

输入：Release清单；可选已有下载文件

输出：data/raw/downloads/中的已核验附件

运行条件：可直接运行；默认联网下载

### [organize_research_archive.py](organize_research_archive.py)

用途：复制PPT、历史报告及六份原执行代码，生成归档清单与复现HTML

输入：--private-archive指定已有私有整理目录

输出：Draft、PPT、Code_Original及归档JSON、HTML

运行条件：维护者工具；保留已有副本字节；会重建初始归档清单，新增版本后不能盲目重跑

### [prepare_authorized_data_release.py](prepare_authorized_data_release.py)

用途：打包全市来源与14份罗湖派生文件并校验包内哈希

输入：--private-tree及三份源附件、--output

输出：罗湖ZIP及docs/DATA_RELEASE_MANIFEST.json

运行条件：维护者归档工具；需要完整输入；会重写指定输出包和清单

### [validate_public_repository.py](validate_public_repository.py)

用途：检查Git跟踪文件、原件哈希、链接、聚合数值和代码分类覆盖

输入：当前Git索引、来源清单与封存结果

输出：终端PASS或异常

运行条件：在git add之后运行；不重估模型


<!-- generated-file-guide:end -->
