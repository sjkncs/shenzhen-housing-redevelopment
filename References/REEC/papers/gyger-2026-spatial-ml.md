# Explainable spatial machine learning for hedonic real estate modeling

DOI: 10.1111/1540-6229.70030

作者（Crossref）：Tim Gyger; Simona Hauri; Simon Bühlmann; Manuel Lehner; Jaron Schlesinger; Fabio Sigrist

期刊：Real Estate Economics。日期字段保留在目录中；Crossref日期可能与出版社首次上线日和卷期年份不同，引用前按正式卷期复核。

来源：[出版社 / DOI](https://doi.org/10.1111/1540-6229.70030)。核对日期：2026-10-16。

## 核对范围

正文关键章节核对。Publisher abstract, sections 2, 3, 4.4-4.6; tables 9, 12 and 13。

不是全篇精读完成，也不是代码或结果复现完成。

## 来源支持的内容

GPBoost 将空间高斯过程与树提升结合，以德国租赁挂牌和公寓销售挂牌数据评价预测；使用SHAP解释，并检验时间扩展窗口和随机切分。论文还比较单调约束及厚尾版本。来源：第2—4节。 [Explainable spatial machine learning for hedonic real estate modeling](https://doi.org/10.1111/1540-6229.70030)

## 我们的审读判断

我们的审读判断：空间协方差拟合不保证未见地区泛化；随机切分不能替代地理阻隔验证。挂牌价格与成交价格需区分。也不能将空间随机效应直接称为更新影响。

## 对深圳项目的迁移提案

项目迁移提案：把空间GP＋树提升列为图DL的强基线，在相同外折、样本和模态下比较；区分未来已知小区、未来未见小区和跨空间预测，不允许测试价格进入GP条件预测。

## 原创分析图设计

原创图：同折损失差及区间、残差空间相关、分区域覆盖与误差；未跑数据前只保留设计，不填示例成绩。 这里只规定图的证据与表达，不复制原论文图片，不声称已完成实验。

## 复现资产与缺口

Paper links https://github.com/fabsig/GPBoost . Library provenance is paper-linked; pinned revision, license, environment and actual replication remain unverified.

原论文完整运行命令、数据版本、种子、硬件、指标容差和实际复现值均未核定；不能填为默认值或把深圳原型测试当作论文复现。
