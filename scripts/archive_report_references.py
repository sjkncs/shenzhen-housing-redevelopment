"""Archive selected report and extract its bibliography without claiming verification."""
import argparse
import csv
import hashlib
import json
import re
import shutil
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--ppt', type=Path, required=True)
    args = parser.parse_args()
    with zipfile.ZipFile(args.report) as archive:
        assert archive.testzip() is None
        tree = ET.fromstring(archive.read('word/document.xml'))
    paragraphs = [''.join(t.text or '' for t in p.findall('.//w:t', NS))
                  for p in tree.findall('.//w:body/w:p', NS)]
    headings = [i for i, text in enumerate(paragraphs) if text.strip() == '参考文献']
    assert headings, 'No bibliography heading'
    entries = [text.strip() for text in paragraphs[headings[-1] + 1:] if re.match(r'^[［\[]\d+[］\]]', text.strip())]
    assert len(entries) == 28, 'Review changed reference count'
    rows = []
    for i, text in enumerate(entries, 1):
        number = int(re.match(r'^[［\[](\d+)', text).group(1))
        assert number == i
        doi = re.search(r'10\.\d{4,9}/[^\s．。]+', text)
        rows.append({'reference_number': i, 'citation_as_reported': text,
                     'doi_as_reported': doi.group(0) if doi else '',
                     'doi_url': 'https://doi.org/' + doi.group(0) if doi else '',
                     'verification_status': 'extracted_from_selected_report_not_reverified'})
    destination = ROOT / 'Draft' / args.report.name
    destination.parent.mkdir(exist_ok=True)
    if destination.exists():
        assert destination.read_bytes() == args.report.read_bytes()
    else:
        shutil.copy2(args.report, destination)
    ppt = ROOT / 'PPT/10.7开题报告.pptx'
    if ppt.read_bytes() != args.ppt.read_bytes():
        backup = ROOT / 'PPT/versions/10.7开题报告_此前归档版.pptx'
        backup.parent.mkdir(exist_ok=True)
        if backup.exists():
            assert backup.read_bytes() == ppt.read_bytes()
        else:
            shutil.copy2(ppt, backup)
        shutil.copy2(args.ppt, ppt)
    manifest_path = ROOT / 'Logfiles/artifact_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['files'] = [r for r in manifest['files'] if r['path'] not in {destination.relative_to(ROOT).as_posix(), ppt.relative_to(ROOT).as_posix()}]
    for path in [destination, ppt]:
        manifest['files'].append({'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size,
                                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    with (ROOT / 'References/report_bibliography.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = ['# 开题报告参考文献（28条）', '',
             '来源：用户最新指定的报告。顺序、作者、期刊、年份与DOI保留原文；本次为提取归档，未重新逐篇验证真实性、元数据或正文引用适用性。', '',
             '[报告原件](../Draft/' + destination.name + ') · [检索CSV](report_bibliography.csv)', '']
    for row in rows:
        lines += [row['citation_as_reported'], '']
        if row['doi_url']:
            lines += ['[DOI入口](' + row['doi_url'] + ')', '']
    (ROOT / 'References/report_bibliography.md').write_text('\n'.join(lines), encoding='utf-8')
    (ROOT / 'References/extraction_manifest.json').write_text(json.dumps({
        'source_report': destination.relative_to(ROOT).as_posix(),
        'source_report_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
        'reference_count': len(rows), 'doi_count': sum(bool(r['doi_as_reported']) for r in rows),
        'verification': 'Extraction only; not a new citation integrity audit'}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'reference_count': len(rows), 'doi_count': sum(bool(r['doi_as_reported']) for r in rows),
                      'report': destination.name, 'ppt_source_bytes_preserved': ppt.read_bytes() == args.ppt.read_bytes()}, ensure_ascii=False))


if __name__ == '__main__':
    main()
