"""Generate Chinese documentation for every tracked Python file, without importing it."""
import csv
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    '01_数据获取与清洗': '下载、输入校验、全市清洗与覆盖统计。',
    '02_空间与住宅身份': '行政区POI筛选、坐标假设及住宅身份线索。',
    '03_价格回归与诊断': '片区DID、动态估计、样本支持与敏感性。',
    '04_材料归档与文献': '公开材料复制、参考文献提取与数据打包。',
    '05_测试与核验': '测试、文件校验与公开目录完整性。',
    '06_原始代码与第三方': '原执行快照和固定版本第三方数学实现。',
}
SPECS = {
    'summarize_daily_market.py': ('01', '从按日行政区汇总中提取罗湖住宅成交套数和面积，补足市场背景截止日后的总量走势', '--zip用户提供的日汇总ZIP，必须含所属区/用途/日期/套数/面积字段', '罗湖日汇总、区—用途覆盖和摘要', '不含小区ID、价格、坐标，不能用于项目DID或价格回归'),
    'build_project_readiness.py': ('02', '将已核定事件区间与交易截止日比较，整理17个项目准备状态', '项目线索、事件证据CSV与全市覆盖摘要', '--output新目录的准备表及摘要', '不补日期、不接受项目处理组，区分年度区间与具体事件'),
    'test_project_readiness.py': ('05', '测试事件晚于截止、区间跨截止及日期缺失等情况', '日期区间样例', 'unittest结果', '无需真实数据'),
    'collect_redevelopment_plan_sources.py': ('02', '获取拆除重建项目官方计划与进展原件，三九计划附件单独归档', '--archive本地原件目录、--manifest公开来源清单', '六份正文与两附件下载记录、哈希和失败状态', '需联网curl；不自动认定开工或未来回迁'),
    'collect_building_identity_evidence.py': ('02', '取得官方楼栋标识线索并记录来源哈希，不推断楼栋与年代对应', '--archive本地原页目录、--output新的公开摘要目录', '楼栋线索CSV及JSON；原HTML仅存本地', '需联网curl；记录失败；不认证住宅、不拆样本'),
    'audit_candidate_composition.py': ('03', '按候选小区和时期检查面积、电梯、建成年代及楼层成交构成', '--sample、--transactions、--baseline输入；原成交哈希校验', '--output新目录的四份构成CSV与摘要', '不估计政策效应，不自动判定楼栋或剔除样本'),
    'test_candidate_composition.py': ('05', '验证前段、过渡和后段正确分离', '季度样例', 'unittest结果', '无需真实数据'),
    'document_all_folders.py': ('05', '为所有Git跟踪目录补齐中文README及逐文件用途，保留已有说明', 'Git索引、中文代码分类JSON及文件用途映射', '每个目录的README.md和子目录导航', '先更新代码分类，再生成目录说明；未知文件用途会失败'),
    'download_data.py': ('01', '按全市或罗湖下载公开数据，核验SHA-256；不自动解压', 'Release清单；可选已有下载文件', 'data/raw/downloads/中的已核验附件', '可直接运行；默认联网下载'),
    'build_citywide_summary.py': ('01', '清洗全市平台交易，统计行政区覆盖', '--input指定原始成交CSV', 'scopes/shenzhen/summary/区级CSV和JSON', '需先下载交易包并解压；不会输出逐套记录'),
    'build_luohu_residential_poi_20261012.py': ('02', '按行政代码440303筛选POI，区分住宅主体、楼栋与出入口并连接同名小区', '原成交CSV、POI ZIP、解压SHP组件及既有回归摘要', '20261012_luohu_residential_poi/CSV、GPKG和摘要', '需配置环境变量与原组件目录；不接受坐标系'),
    'diagnose_poi_coordinate_frames_20261012.py': ('02', '比较住宅与POI的九种坐标口径组合', '成交CSV、同名候选连接、固定版本坐标实现', '双端诊断CSV及摘要', '先运行POI筛选；一致性不是测量精度'),
    'review_luohu_poi_ambiguity_20261012.py': ('02', '复核同名位置歧义、地址限定词、门点与主体线索', '--base指定公开派生POI目录，--transactions指定原成交CSV；按封存哈希校验并重建坐标登记', '--output指定新目录；身份候选、分流与摘要', '拒绝覆盖既有目录；--skip-official-fetch可离线复现，官方来源另行核验；不接受住宅位置'),
    'audit_mutoulong_candidate_support.py': ('02', '统计三条道路地址线索小区的事件前后成交支持', '--sample、--coverage、--matches、--supplement四个CSV', '--output指定的新目录；621小区表及道路线索支持', '所有参数显式传入；拒绝覆盖已有输出；不定义项目处理组'),
    'review_residential_baseline.py': ('02', '按最早成交及平台建成年代分流基期存在证据', '--sample、--coverage、--leads三个CSV', '--output指定的新目录；基期证据CSV与摘要', '先完成地址支持核查；不是官方竣工认证'),
    'run_price_did_audit_20261003.py': ('03', '运行罗湖商圈代理双向固定效应DID和季度动态模型', 'SHENZHEN_TRANSACTION_CSV环境变量指定成交CSV', 'outputs/price_did_audit_20261003/样本、回归、图和摘要', '需原交易数据；写入既有结果目录，先备份或用独立克隆运行'),
    'check_price_did_support_20261003.py': ('03', '检查前后交易支持，重估支持样本和伪事件诊断', '主回归生成的analysis_sample.csv及估计函数', '支持表、敏感性表、季度协方差及诊断摘要', '在主回归之后运行；会更新结果目录'),
    'check_price_did_influence_20261003.py': ('03', '逐小区、逐比较商圈留出及差异线性趋势敏感性', 'analysis_sample.csv及主回归估计函数', '影响点CSV、趋势表、动态比较和影响图', '在主回归之后运行；不是正式项目ATT'),
    'prepare_authorized_data_release.py': ('04', '打包全市来源与14份罗湖派生文件并校验包内哈希', '--private-tree及三份源附件、--output', '罗湖ZIP及docs/DATA_RELEASE_MANIFEST.json', '维护者归档工具；需要完整输入；会重写指定输出包和清单'),
    'organize_research_archive.py': ('04', '复制PPT、历史报告及六份原执行代码，生成归档清单与复现HTML', '--private-archive指定已有私有整理目录', 'Draft、PPT、Code_Original及归档JSON、HTML', '维护者工具；保留已有副本字节；会重建初始归档清单，新增版本后不能盲目重跑'),
    'archive_report_references.py': ('04', '存档指定报告，提取28条参考文献和DOI入口', '--report DOCX与--ppt PPTX', 'Draft原件、References Markdown/CSV和来源JSON', '维护者工具；当前期待28条，不是文献真实性核验'),
    'validate_public_repository.py': ('05', '检查Git跟踪文件、原件哈希、链接、聚合数值和代码分类覆盖', '当前Git索引、来源清单与封存结果', '终端PASS或异常', '在git add之后运行；不重估模型'),
    'build_code_catalog.py': ('05', '为全部Git跟踪Python文件生成中文分类说明与完整索引', 'Git索引及本脚本用途映射', 'Code_Revision六类README、CSV和JSON', '在git add之后运行；新脚本未登记会明确失败'),
    'test_candidate_support.py': ('05', '测试过渡季度分离、无成交小区保留和重复交易拒绝', '程序内小型测试表', 'unittest结果', '数据无关测试'),
    'test_download_data.py': ('05', '测试下载哈希、已有文件保护、路径限制与包内核验', '临时测试文件', 'unittest结果', '无需真实数据或网络'),
    'test_mutoulong_image_comparison.py': ('05', '核对图像拟合与留出点分离、保存的像素误差', '已归档图纸比对CSV/JSON', 'unittest结果', '不验证地理配准'),
    'test_mutoulong_native_grid.py': ('05', '校验45点编号、哈希、鞋带面积与未配准状态', '已归档原坐标网CSV/JSON', 'unittest结果', '不确认CRS、轴序或真实单位'),
    'test_residential_baseline.py': ('05', '测试平台成交与建成年代的证据分流逻辑', '程序内日期与年份样例', 'unittest结果', '不证明住宅身份'),
    'test_luohu_poi_identity_review.py': ('05', '测试地址限定词处理并保护分期、楼栋和院区', '名称样例', 'unittest结果', '不读取真实POI'),
    'test_luohu_residential_poi.py': ('05', '测试住宅类别、商业混合与入口分类', '名称/类别样例', 'unittest结果', '不验证坐标或行政区数据质量'),
    'implementation.py': ('06', '固定版本eviltransform地图坐标数学实现', '经纬度测试点；注意函数纬度/经度参数顺序', '转换候选点', '第三方BSD许可随附；不是深圳地方测量坐标转换'),
}


def main():
    paths = subprocess.check_output(['git', 'ls-files', '-z', '*.py'], cwd=ROOT).decode().split('\0')
    rows = []
    for name in sorted(filter(None, paths)):
        base = Path(name).name
        if base not in SPECS:
            raise ValueError('Missing Chinese description: ' + name)
        group, purpose, inputs, outputs, status = SPECS[base]
        if name.startswith('Code_Original/'):
            group, status = '06', '原字节封存；有历史工作站路径，不是当前可移植入口'
        folder = next(key for key in GROUPS if key.startswith(group + '_'))
        rows.append({'category': folder, 'path': name, 'purpose_zh': purpose,
                     'inputs_zh': inputs, 'outputs_zh': outputs, 'run_status_zh': status})
    directory = ROOT / 'Code_Revision'
    with (directory / '代码用途索引.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (directory / 'code_catalog.json').write_text(json.dumps({'files': rows}, ensure_ascii=False, indent=2), encoding='utf-8')
    for group, intro in GROUPS.items():
        target = directory / group
        target.mkdir(exist_ok=True)
        lines = ['# ' + group.replace('_', ' / ', 1), '', intro, '',
                 '这里按用途导航到真实代码，不复制或移动当前执行文件。', '']
        for row in rows:
            if row['category'] != group:
                continue
            lines += ['## [' + Path(row['path']).name + '](../../' + row['path'] + ')', '',
                      '**用途：**' + row['purpose_zh'], '', '**输入：**' + row['inputs_zh'], '',
                      '**输出：**' + row['outputs_zh'], '', '**运行条件：**' + row['run_status_zh'], '',
                      '路径：`' + row['path'] + '`', '']
        (target / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'classified_python_files': len(rows), 'categories': len(GROUPS)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
