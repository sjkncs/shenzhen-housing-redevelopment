"""Build Chinese file-level guides in every tracked directory; preserve existing prose."""
import json
import os
from pathlib import Path, PurePosixPath
import subprocess

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- generated-file-guide:start -->'
END = '<!-- generated-file-guide:end -->'
PURPOSE = {
    'review_atlas_index.csv': '住宅审查图册的小区名称、成交支持、文件名与图像哈希索引。',
    'coordinate_hypothesis_footprint_support.csv': '住宅原坐标三种假设的落入建筑与50米候选计数，不选楼栋。',
    'all_50m_footprint_candidates.csv': '三种地图坐标假设下全部50米候选轮廓，不按最近点接受身份。',
    'reported_floor_counts.csv': '供应建筑候选的原Floor频数，不解释为已核实层数或高度。',
    'original_label_use_reconciliation.csv': '各原始区名按日的全部与分用途对账，不合并区名或推断渠道。',
    'label_type_check_summary.csv': '短名称和带区后缀名称各自用途合计检查汇总。',
    'luohu_monthly_alias_sensitivity.csv': '罗湖月度隔离与相加口径对照，显示套数面积及观测日差异。',
    'affected_months.csv': '区名口径改变已报告套数或面积的月份，非政策效应。',
    'alias_scenario_city_checks.csv': '同日同用途区名三种候选合并方式与全市总量的差异，不是已接受规则。',
    'alias_scenario_summary.csv': '短名优先、后缀优先及两类相加的内部对账汇总。',
    'collision_group_classification.csv': '同日同用途区名冲突逐组数值分类与来源ID，不决定合并版本。',
    'collision_district_summary.csv': '区名冲突按行政区和类别汇总的数量与日期范围。',
    'normalized_name_collision_rows.csv': '行政区名称标准化后同日同用途发生冲突的原行，隔离不择一或重复加总。',
    'luohu_daily_residential_open_data.csv': '由分页开放平台快照核验出的罗湖住宅日度套数面积，保留原字段和标准化区名。',
    'district_monthly_residential_open_data.csv': '分页开放平台快照的各区月度住宅成交套数与面积，不是价格数据。',
    'luohu_monthly_reported_coverage.csv': '罗湖住宅各月已报告套数面积与日覆盖，不把缺报日补零。',
    'luohu_absent_calendar_dates.csv': '整个来源日期区间内没有罗湖住宅行的日期，不代表零成交。',
    'residential_district_reconciliation.csv': '全市住宅与已报告各区合计比较，标出未出现的行政区。',
    'luohu_daily_residential_market.csv': '罗湖住宅按日成交套数与面积汇总，补充市场背景但不是小区价格面板。',
    'district_use_coverage.csv': '行政区—用途的日期、成交套数和面积覆盖统计。',
    'court_project_scope.csv': '法院平台管理人公告所列三个建设宗地及面积版本冲突，不是测绘验收成果。',
    'registration_status_evidence.csv': '官方首次登记状态答复，保留月份与楼栋范围缺口，不替代交付事件。',
    'parcel_name_crosswalk.csv': '官方项目名称与建设宗地一对多连接，完整拆除几何仍未接受。',
    'phased_event_timeline.csv': '木头龙行政许可、施工阶段、回迁和配套计划分开的事件证据区间。',
    'event_evidence.csv': '有来源的实际或行政事件区间，明确精度和分期用途，不填预测回迁日。',
    'project_readiness.csv': '17个候选项目的事件、交易窗口、类型与空间身份准备状态。',
    'project_claims.csv': '用户AI项目线索逐条复核，对象类型、已有证据和未核实预测分开记录。',
    'building_label_evidence.csv': '官方楼栋或大厦标识线索、原页哈希及未接受的年代对应状态。',
    'period_composition.csv': '逐候选逐时期的成交笔数、面积、电梯、年代和价格描述统计。',
    'reported_year_composition.csv': '逐候选逐时期的建成年代计数与占比，不能代替楼栋识别。',
    'floor_band_composition.csv': '逐候选逐时期的原楼层标签频率，不代表统一实际高度。',
    'pre_post_composition.csv': '双段有成交者的属性构成差异，不是价格因果效应。',
    'official_address_evidence.csv': '三个重点候选的官方地址证据、来源哈希与尚未确认的住宅/坐标状态。',
    'checks.yml': 'GitHub自动检查配置：安装依赖、运行测试并核验公开目录。',
    'code_catalog.json': '全部Python代码的分类、用途、输入、输出和运行条件，供完整性检查读取。',
    '代码用途索引.csv': '供Excel/GitHub查看的逐脚本中文用途索引。',
    'artifact_manifest.json': '报告、PPT和原代码快照的大小与SHA-256，用于证明副本未改写。',
    'extraction_manifest.json': '参考文献提取来源、报告哈希、条目和DOI数量；不是真实性审核。',
    'report_bibliography.csv': '28条参考文献原文、DOI和未重新核验状态的检索表。',
    'report_bibliography.md': '完整参考文献阅读版，保留原报告顺序及DOI入口。',
    'DATA_RELEASE_MANIFEST.json': '公开数据附件与罗湖包内文件的大小、哈希和下载URL。',
    'DATA_ACCESS.md': '公开数据下载、来源、字段、许可和信息可定位性说明。',
    'PUBLICATION.md': '公开范围、授权记录、版本历史和第三方许可说明。',
    'REPRODUCTION.md': '环境、输入路径、下载、重估步骤及未齐备依赖。',
    'RESEARCH_DESIGN.md': '研究问题、片区模型、事件设定和正式项目识别计划。',
    'COORDINATE_CONVERTER_REVIEW.md': '桌面坐标程序静态检查，区分互联网地图坐标与地方测量坐标。',
    'all_621_community_support.csv': '621个小区的前段、过渡、后段成交和缺失季度统计。',
    'road_address_leads_support.csv': '三条道路的20个地址线索及成交支持，不是项目处理组。',
    'road_leads_quarter_support.csv': '道路线索集合每季度成交笔数与小区数。',
    'baseline_evidence.csv': '20个候选的最早成交、平台建成年代及冲突线索，不认证竣工。',
    'main_did.csv': '实际片区DID系数、标准误、p值与区间，非正式项目ATT。',
    'event_study.csv': '季度动态系数和区间；参照2019Q4。',
    'event_study_covariance.csv': '动态系数协方差，用于联合检验和跨期比较。',
    'event_study.png': '真实片区动态结果与95%区间图，保留显著事件前差异。',
    'quarter_support.csv': '按季度及商圈处理标签的成交支持统计。',
    'did_support_sensitivity.csv': '不同观测支持与伪事件设定下的实际回归结果。',
    'dynamic_period_contrasts.csv': '选定时段动态响应汇总与对比，仍属片区比较。',
    'linear_trend_sensitivity.csv': '加入差异线性趋势的敏感性结果，不自动修复识别。',
    'independent_verification.json': '已有回归数值核对记录；不等于独立外部因果验证。',
    'run_summary.json': '样本数量、事件窗口、固定效应、事件前检验和未决问题。',
    'summary.json': '所在分析批次的输入哈希、统计数量和研究状态。',
    'coverage.json': '全市清洗数量、时间覆盖和来源哈希。',
    'district_coverage.csv': '清洗后十个行政区的交易、小区和日期覆盖汇总。',
    'source_manifest.json': '官方原件下载成功/失败记录、来源URL及成功原件哈希。',
    'coordinate_evidence_followup.md': '官方坐标材料检索结论、已下载原件及缺口。',
    'coordinate_records_request.md': '尚未发送的官方边界成果与坐标依据申请草稿。',
    'coordinates.csv': '官方J1—J45原表数值转录，不是经纬度。',
    'source_grid_rings.csv': '两个原坐标网工作环的WKT、面积数值和拓扑统计。',
    'source_grid_preview.png': '未配准原坐标网图形预览，不代表现实地图朝向。',
    'audit.json': '原坐标转录哈希、拓扑检查与未确认坐标状态。',
    'image_points.csv': '人工目视角点与fit/check角色，在固定参考图像素空间内。',
    'pixel_correspondence_checks.csv': '每个角点的图像比对误差，单位为参考图像素。',
    'comparison.json': '图纸仿射比对参数、拟合/留出误差和来源哈希。',
    'official_image_overlay.png': '官方拆除图与原坐标网叠加，仅为图纸形态比对。',
    'LICENSE': '固定版本第三方坐标数学实现的原始许可文本。',
    '核验摘要.json': '第三方实现的固定提交、哈希及诊断用途说明。',
}
CONTEXT = {
    '.github': '仓库自动化入口，子目录workflows保存实际检查任务。',
    '.github/workflows': '自动测试工作流；不联网运行交易估计，不认证项目识别。',
    'scripts': '仓库维护、下载、材料归档及完整性检查工具。',
    'tests': '数据无关测试及已归档中间成果一致性测试。',
    'docs': '研究设计、数据来源、复现与公开范围的主题说明。',
    'scopes': '全市数据基础与罗湖案例分开存放；先选择研究范围。',
    'scopes/shenzhen/scripts': '全市清洗与区级覆盖汇总代码。',
    'scopes/shenzhen/summary': '真实来源清洗汇总，不是全市政策效应。',
    'scopes/luohu/scripts': '罗湖数据处理、身份诊断、片区估计与样本检查。',
    'scopes/luohu/tests': '罗湖名称限定词、住宅类别及门点规则的测试。',
    'scopes/luohu/outputs': '已运行的罗湖结果，按批次分开，注意正式项目识别仍待完成。',
    'scopes/luohu/data': '空间来源和固定版本第三方实现，大数据从Release下载。',
    'scopes/luohu/data/supplied_gdata_intake': '用户供应资料处理链的目录，保留版本身份。',
    'scopes/luohu/data/supplied_gdata_intake/20261011': '20261011供应资料批次的坐标数学实现与来源线索。',
    'scopes/luohu/data/supplied_gdata_intake/20261011/building_rar': '建筑资料处理相关的坐标假设工具，非建筑归属成果。',
    'scopes/luohu/data/supplied_gdata_intake/20261011/building_rar/coordinate_hypotheses': '地图坐标候选转换实现及许可，不转换深圳地方测量坐标。',
    'Code_Original/20261012_snapshot': '原执行代码的封存快照，不在此修改或直接跨机器运行。',
    'scopes/luohu/project_registry/mutoulong': '木头龙官方范围、坐标原表、图纸比对和资料请求记录。',
    'scopes/luohu/project_registry/mutoulong/coordinate_sources': '官方坐标依据下载台账，原件和失败路径状态分开记载。',
}


def main():
    files = sorted(filter(None, subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')))
    catalog = {r['path']: r for r in json.loads((ROOT / 'Code_Revision/code_catalog.json').read_text(encoding='utf-8'))['files']}
    folders = {str(parent) for name in files for parent in PurePosixPath(name).parents if str(parent) != '.'}
    for folder in sorted(folders):
        directory = ROOT / folder
        page = directory / 'README.md'
        original = page.read_text(encoding='utf-8') if page.exists() else '# ' + folder + ' / 中文说明\n\n' + CONTEXT.get(folder, '本目录用途见下面的逐文件说明及子目录导航。') + '\n'
        if START in original:
            before, rest = original.split(START, 1)
            _, after = rest.split(END, 1)
            original = before.rstrip() + after
        lines = [START, '## 逐文件中文说明', '', '文件说明以当前跟踪版本为准；代码仅说明用途，不导入或执行。', '']
        for name in files:
            if str(PurePosixPath(name).parent) != folder or PurePosixPath(name).name == 'README.md':
                continue
            filename = PurePosixPath(name).name
            lines += ['### [' + filename + '](' + filename + ')', '']
            if name in catalog:
                row = catalog[name]
                lines += ['用途：' + row['purpose_zh'], '', '输入：' + row['inputs_zh'], '',
                          '输出：' + row['outputs_zh'], '', '运行条件：' + row['run_status_zh'], '']
            elif filename in PURPOSE:
                lines += [PURPOSE[filename], '']
            elif Path(filename).suffix in {'.docx', '.pdf', '.pptx'}:
                lines += ['用户指定的开题阶段原件，保留署名及版本；查看本目录原有版本说明，不作为最终论文。', '']
            elif filename.startswith('review_') and filename.endswith('.png'):
                lines += ['三种坐标假设的候选轮廓人工核查图，各面板独立中心，不认证住宅或地图位置；编号为源行序号。', '']
            elif filename.endswith('.svg'):
                lines += ['仓库首页的自包含SVG视觉资源，用于标题、范围或研究流程展示；不是新增实证图表或空间数据。', '']
            elif filename.endswith('.md'):
                lines += ['研究说明或分类导航文档；打开查看该主题用途和执行条件。', '']
            else:
                raise ValueError('Missing file explanation: ' + name)
        children = sorted(d for d in folders if str(PurePosixPath(d).parent) == folder)
        if children:
            lines += ['## 子目录导航', '']
            for child in children:
                relative = PurePosixPath(child).name
                lines += ['- [' + relative + '](' + relative + '/README.md)：' + CONTEXT.get(child, '详见子目录中文说明。')]
        lines += ['', END, '']
        page.write_text(original.rstrip() + '\n\n' + '\n'.join(lines), encoding='utf-8')
    print(json.dumps({'documented_folders': len(folders), 'python_files_explained': len(catalog)}))


if __name__ == '__main__':
    main()
