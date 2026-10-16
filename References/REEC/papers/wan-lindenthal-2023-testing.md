# Testing machine learning systems in real estate

DOI: 10.1111/1540-6229.12416

作者（Crossref）：Wayne Xinwei Wan; Thies Lindenthal

期刊：Real Estate Economics。日期字段保留在目录中；Crossref日期可能与出版社首次上线日和卷期年份不同，引用前按正式卷期复核。

来源：[出版社 / DOI](https://doi.org/10.1111/1540-6229.12416)。核对日期：2026-10-16。

## 核对范围

正文关键章节核对。Publisher sections 1, 3.2, 4.1 and footnotes 6-10; not every appendix or numerical result audited。

不是全篇精读完成，也不是代码或结果复现完成。

## 来源支持的内容

以建筑年代分类和 AVM 图像分类为例，将领域预期、对象检测与 LIME 区域解释结合。验证分数是解释区域中某类对象的面积占比，再除以对象在整图的占比，得到面积校正比率。来源：第3.2节，公式1-3。 [Testing machine learning systems in real estate](https://doi.org/10.1111/1540-6229.12416)

## 我们的审读判断

我们的审读判断：比率大于1只表示相对面积的解释富集，不能证明正确的因果证据；检测误差、对象面积很小和解释参数都可能影响比率。论文明确不以通常经济学意义的内外部有效性为目标。

## 对深圳项目的迁移提案

项目迁移提案：分别对围挡、步行界面和服务入口做独立标签；比较概念区域与等面积非概念区域遮挡，并检查错配、过时与缺失影像。价格任务里的汽车可能是财富代理，不应一律视为应忽略对象。

## 原创分析图设计

原创图：每类概念的定位质量、面积校正证据富集和成对遮挡损失并列；同时展示空间留出结果。禁止把显著富集命名为更新机制已证实。 这里只规定图的证据与表达，不复制原论文图片，不声称已完成实验。

## 复现资产与缺口

Publisher footnotes link LIME and TensorFlow object-detection libraries. These are component libraries, not a verified complete paper replication package; no repository revision or license audit completed.

原论文完整运行命令、数据版本、种子、硬件、指标容差和实际复现值均未核定；不能填为默认值或把深圳原型测试当作论文复现。
