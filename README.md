<p align="center">
  <img src="https://raw.githubusercontent.com/sjkncs/shenzhen-housing-redevelopment/main/docs/assets/header.svg" width="100%" alt="Shenzhen Housing Redevelopment / 深圳住宅拆除重建与周边既有住宅价格研究" />
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/sjkncs/shenzhen-housing-redevelopment/main/docs/assets/python.svg" alt="Python 3.11" />
  <img src="https://raw.githubusercontent.com/sjkncs/shenzhen-housing-redevelopment/main/docs/assets/spatial.svg" alt="Spatial data / GIS" />
  <img src="https://raw.githubusercontent.com/sjkncs/shenzhen-housing-redevelopment/main/docs/assets/research.svg" alt="Research in progress" />
  <a href="https://github.com/sjkncs/shenzhen-housing-redevelopment/actions/workflows/checks.yml"><img src="https://github.com/sjkncs/shenzhen-housing-redevelopment/actions/workflows/checks.yml/badge.svg" alt="Research checks: data-independent tests and public-file validation" /></a>
</p>

<p align="center">
  <a href="docs/RESEARCH_DESIGN.md">Research Design / 研究设计</a> ·
  <a href="docs/REPRODUCTION.md">Reproduce / 复现</a> ·
  <a href="docs/DATA_ACCESS.md">Data / 数据</a> ·
  <a href="README_replication.md">Archive / 研究归档</a> ·
  <a href="https://github.com/sjkncs/shenzhen-housing-redevelopment/issues">Discuss / 讨论</a>
</p>

**When redevelopment changes a neighborhood, how do nearby existing-home prices respond?** This ongoing project connects Shenzhen transaction coverage, a Luohu area-level diagnostic and preparation for project-boundary identification.

**拆除重建如何影响周边既有住宅价格？** 关注响应时点、施工成本与长期收益，以及空间条件如何改变价格变化。采用“全市数据基础 → 罗湖片区诊断 → 木头龙项目识别”的收敛路径，各层证据分别管理。

> **Current boundary / 当前边界：** 数据覆盖和片区诊断已执行；项目坐标、拆除边界与住宅空间归属仍待独立核定。已有事后系数不能解释为木头龙项目因果效应，正式项目 ATT 与机制检验尚未完成。

## Explore / 研究入口

<p>
  <a href="scopes/shenzhen/README.md"><img src="https://raw.githubusercontent.com/sjkncs/shenzhen-housing-redevelopment/main/docs/assets/shenzhen.svg" width="280" alt="Shenzhen source coverage: 132,774 cleaned platform transactions, not an official census or a citywide causal estimate" /></a>
  <a href="scopes/luohu/README.md"><img src="https://raw.githubusercontent.com/sjkncs/shenzhen-housing-redevelopment/main/docs/assets/luohu.svg" width="280" alt="Luohu diagnostics: 16,199 cleaned transactions across 621 communities; area-proxy DID, not project ATT" /></a>
  <a href="scopes/luohu/outputs/project_readiness_20261013/README.md"><img src="https://raw.githubusercontent.com/sjkncs/shenzhen-housing-redevelopment/main/docs/assets/readiness.svg" width="280" alt="Identification gate: 17 supplementary candidate leads, zero accepted project spatial treatment samples" /></a>
</p>

<details>
<summary>Scope, sample & observation windows / 样本与观察窗口</summary>

| | Shenzhen / 全市 | Luohu / 罗湖 |
| :--- | :--- | :--- |
| 用途 | 来源覆盖、规则清洗、行政区汇总 | 住宅身份线索、片区诊断与项目准备 |
| 交易样本 | 原始 139,514 条；清洗后 132,774 条 | 清洗后 16,199 条，621 个小区 |
| 来源时间 | 2010-01-01 至 2024-04-25 | 清洗样本至 2024-04-24；回归窗口 2017—2023 年 |
| 已执行 | 区级覆盖、市场统计内部对账与口径敏感性 | 片区代理 DID、动态路径与样本支持检验 |
| 未完成 | 全市更新因果效应 | 正式项目归属、项目 ATT、距离衰减与机制估计 |

交易样本来自用户提供的平台文件，**不是深圳官方成交普查**。全市覆盖与较新的行政区日度市场汇总是不同来源和粒度，不能拼成项目附近的价格面板。核验值见[全市覆盖 JSON](scopes/shenzhen/summary/coverage.json)与[分区表](scopes/shenzhen/summary/district_coverage.csv)。

</details>

## Evidence Preview / 实证诊断

<p>
  <img src="https://raw.githubusercontent.com/sjkncs/shenzhen-housing-redevelopment/main/scopes/luohu/outputs/price_did_audit_20261003/event_study.png" width="100%" alt="Actual Luohu area-proxy event-study estimates with 95% confidence intervals; reference quarter 2019Q4; missing treated observations in 2021Q4 are not interpolated" />
</p>

*真实罗湖片区代理事件研究，95% 置信区间，参照期 2019Q4；2021Q4 的处理组交易缺失不插值。*

比较来源中的翠竹商圈与罗湖其他商圈，住房特征调整后的主模型使用 **10,867 笔交易、607 个小区**。事后交互系数为 **0.1606**，相对差异约 **17.42%**（95% 区间 11.62%—23.52%）。这是当前片区设定的估计，不是项目因果结论。

**事件前联合检验 F = 12.325，p ≈ 3.94 × 10⁻²¹。** 当前设定存在明显事件前变化；单一处理商圈的共同冲击也不能仅靠小区聚类解决。项目边界、比较组、同期冲击和提前预期仍须核验。

[基准回归表](scopes/luohu/outputs/price_did_audit_20261003/main_did.csv) · [动态系数 CSV](scopes/luohu/outputs/price_did_audit_20261003/event_study.csv) · [执行摘要与推断边界](scopes/luohu/outputs/price_did_audit_20261003/run_summary.json)

## Latest Audits / 最新核验

| Date | Audit / 入口 | What It Establishes / 结论边界 |
| :--- | :--- | :--- |
| 2026-10-14 | [罗湖月度别名敏感性](scopes/shenzhen/summary/luohu_monthly_alias_sensitivity_20261014/README.md) | 区名口径仅影响 2022 年 5—7 月；两种口径都非完整日历月份。不是市场增长或政策影响。 |
| 2026-10-14 | [区名三场景与全市合计对账](scopes/shenzhen/summary/alias_scenario_review_20261014/README.md) | 两类原行相加在 70 个可对账组全部吻合；是内部可加性证据，合并含义尚未得到来源方确认。 |
| 2026-10-14 | [日度市场质量与覆盖](scopes/shenzhen/summary/daily_market_quality_20261014/README.md) | 缺日与缺区保留，不补零；汇总量不能替代周边既有住宅价格。 |
| 2026-10-13 | [项目准备与观察窗口](scopes/luohu/outputs/project_readiness_20261013/README.md) | 17 个补充项目线索不构成已验收样本；当前已接受的项目空间处理样本为 0。 |
| 2026-10-13 | [既有住宅基期证据](scopes/luohu/outputs/mutoulong_baseline_review_20261013/README.md) | 交易年代与平台建成年代是线索，不认证竣工、住宅身份或处理归属。 |

核验日期是对应证据批次，不表示未来所有版本都自动完成同一检查。统计、来源、输入哈希和局限详见各目录。

## Research Path / 识别路径

<p align="center">
  <img src="https://raw.githubusercontent.com/sjkncs/shenzhen-housing-redevelopment/main/docs/assets/workflow-mobile.svg" width="360" alt="Executed: source coverage, Luohu diagnostic and support audits. Pending: verified coordinates and boundaries, existing-home spatial assignment, then project effects and mechanisms." />
</p>

[横向识别路径图](docs/assets/workflow.svg) · [详细研究设计](docs/RESEARCH_DESIGN.md)

木头龙是当前主案例。最初六个指定候选包括木头龙、金钻豪园、三九花园、广场北、红岗花园与第一幼儿园宿舍楼；它们不同于后续登记的 17 个补充项目线索，两者均不是全区完整名录或已接受的处理组。

<details>
<summary>Next research gates / 后续研究关口</summary>

- [x] 区分全市数据基础与罗湖片区研究，保留真实回归及事件前诊断。
- [x] 按行政代码筛选罗湖 POI，保留分期、院区、楼栋和多坐标歧义。
- [x] 登记项目事件证据、住宅基期线索，开展市场汇总的覆盖和口径审计。
- [ ] 确认木头龙主环坐标依据与施工分期，独立核验拆除红线及住宅空间归属。
- [ ] 构造比较样本，检验同期政策、共同冲击与提前预期。
- [ ] 资料充分后再估计正式项目效应、动态路径、距离衰减与机制。

项目首批回迁记录只给出 2024 年度区间，跨越交易来源截止日，不能填年中日期替代实际事件。该限制不意味着木头龙没有施工后价格观察。

</details>

## Reproduce / 复现入口

数据无关测试与公开汇总核验：

```bash
git clone https://github.com/sjkncs/shenzhen-housing-redevelopment.git
cd shenzhen-housing-redevelopment
python -m pip install -r requirements.txt
python -m unittest discover -s scopes/luohu/tests -p "test_luohu_*.py"
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_public_repository.py
```

**CI 通过不等于因果识别通过。** 工作流不下载原始数据、不重估模型，也不认证坐标或项目样本。重估请在独立副本中配置有权使用的输入，详见[复现指南](docs/REPRODUCTION.md)。当前依赖清单不是封存环境锁文件。

<details>
<summary>Data download & verification / 数据下载与校验</summary>

```bash
python scripts/download_data.py --scope luohu
python scripts/download_data.py --scope shenzhen
python scripts/download_data.py --scope all --verify-only
```

下载工具默认不解压、不覆盖已有文件；附件校验 SHA-256，罗湖 ZIP 内 14 份文件逐项核验。全市 POI 的 DBF 解压约 2.15 GB，请按需下载。

[公开 Release](https://github.com/sjkncs/shenzhen-housing-redevelopment/releases/tag/data-snapshot-20261012) · [来源与访问条件](docs/DATA_ACCESS.md) · [附件和文件哈希清单](docs/DATA_RELEASE_MANIFEST.json)

数据公开是所有者授权的共享，不等于来源方授予开放许可。交易文件未经匿名化，不应用于识别业主或联系住户。

</details>

## Archive / 资料导航

| Entry / 入口 | Contents / 内容 |
| :--- | :--- |
| [Current Code](Code_Revision/README.md) · [用途索引](Code_Revision/代码用途索引.csv) | 当前脚本的用途、输入、输出和运行条件 |
| [Dataset](Dataset/README.md) · [Logfiles](Logfiles/README.md) | 数据来源、下载与逐文件哈希 |
| [Research Design](docs/RESEARCH_DESIGN.md) · [References](References/README.md) | 研究设计、文献和官方资料线索 |
| [Draft](Draft/README.md) · [PPT](PPT/README.md) | 开题阶段报告和演示文稿，不是最终论文 |

<details>
<summary>Full repository map / 完整目录与归档说明</summary>

```text
scopes/shenzhen/   全市覆盖、行政区汇总及口径审计
scopes/luohu/      片区诊断、项目线索、空间核验与测试
docs/              研究设计、数据访问与复现
scripts/           数据下载、归档与公开文件核验
Code_Original/     历史执行代码快照，不作为默认入口
Code_Revision/     当前代码导航
Dataset/           数据说明与 Release 入口
Draft/             开题阶段报告
Logfiles/          文件哈希和核验记录
PPT/               指定开题演示文稿
References/        文献和官方资料索引
```

[研究复现说明](README_replication.md) · [HTML 说明](README_replication.html) · [历史代码](Code_Original/README.md) · [AGENTS.md](AGENTS.md) · [CLAUDE.md](CLAUDE.md)

报告和 PPT 按所有者要求公开，保留原作者信息；其中研究范围尚未全部同步到木头龙单案例设计。本次首页优化不修改这些原件。任务书、导师反馈和其他个人材料仍不公开。

</details>

## Discuss & Cite / 交流与引用

欢迎提出来源纠错、坐标核验和识别设计建议。[Issues](https://github.com/sjkncs/shenzhen-housing-redevelopment/issues) · [提交记录](https://github.com/sjkncs/shenzhen-housing-redevelopment/commits/main) · [Stars](https://github.com/sjkncs/shenzhen-housing-redevelopment/stargazers) · [Star History](https://www.star-history.com/#sjkncs/shenzhen-housing-redevelopment&Date)。请勿在 Issue 上传个人住宅记录或未经授权的数据库，不绘制虚构增长曲线。

这是进行中的研究，**不是已发表论文**。引用时请注明仓库 URL、提交号与访问日期；不存在可引用的论文 DOI。第三方坐标数学实现固定到 `googollee/eviltransform` 提交 `03ba58d92dfda57f8a1635f3805483c8fc10bd77`，原 LICENSE 保留。项目整体及第三方数据没有统一开源许可，详见[公开说明](docs/PUBLICATION.md)。
