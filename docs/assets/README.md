# 首页视觉资源

本目录是研究仓库 README 的自包含 SVG 页头、入口卡片、静态技术徽章与识别路径。SVG 不使用外部字体、图片、脚本或自动统计服务。图片链接直接指向本仓库 Raw 文件，CI 徽章仍读取实际工作流。

- `header.svg`：项目名称与研究主题，不包含模型效果或成果承诺。
- `shenzhen.svg`：全市来源覆盖，清洗记录数对应 `scopes/shenzhen/summary/coverage.json`。
- `luohu.svg`：罗湖清洗样本与小区数，对应 `scopes/shenzhen/summary/district_coverage.csv`。
- `readiness.svg`：17个补充候选及0个已接受项目空间样本，对应 `scopes/luohu/outputs/project_readiness_20261013/summary.json`。不是全区完整名录。
- `workflow.svg`：已执行的覆盖、片区诊断与资料审计，以及待核定的空间身份和正式项目识别。
- `workflow-mobile.svg`：同一识别路径的窄屏布局，不改变步骤和证据状态。
- `python.svg`、`spatial.svg`、`research.svg`：环境、方法领域与进行中状态，不代表认证、依赖锁定或开放许可。

真实事件研究图继续引用原封存 PNG，不重新估计或修改图中结果。引用来源表和研究边界保留在首页文本中，确保图片之外也能阅读。

维护时运行公开仓库校验，核对 SVG 中的数量与来源摘要。资料版本改变时应手动核对首页，不将代码测试通过解释为因果识别通过。布局参考 EconML 与 PyFixest 的项目定位、图形结果、复现和文档组织；只借鉴层级，不复制素材或结论。
