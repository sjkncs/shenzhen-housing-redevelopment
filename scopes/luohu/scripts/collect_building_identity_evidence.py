"""Archive official building-label leads; never infer year-to-building mappings."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess

from bs4 import BeautifulSoup

SOURCES = [
    ('taining_2019', '泰宁花园', 'https://www.szlh.gov.cn/qgbmxxgkml/qwsjkj/ywgz/ssjgk/content/post_5057633.html',
     ['泰宁花园', 'A、B、C栋'], 'A、B、C栋；裙楼酒店记录', '官方公示含2019年检查记录，不认证住宅竣工'),
    ('hualiwest_2026', '华丽西村', 'https://www.szlh.gov.cn/lhqwsjkj/gkmlpt/content/12/12627/post_12627024.html',
     ['华丽西村4号大厦', '华丽路1021号'], '4号大厦', '2026年托育评估页面，不倒推基期用途'),
    ('jingji_2021', '京基东方华都', 'https://www.szlh.gov.cn/zwfw/yljk/tzgg/content/post_10111558.html',
     ['东方华都大厦', '文锦中路2063号'], '大厦四楼', '2021年公共场所记录，无竣工或分期信息'),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new output directory')
    args.archive.mkdir(parents=True, exist_ok=True)
    rows = []
    for sid, name, url, tokens, label, scope in SOURCES:
        row = {'source_id': sid, 'candidate_name': name, 'url': url,
               'building_label_lead': label, 'evidence_scope': scope,
               'status': 'failed', 'year_building_mapping_verified': False,
               'residential_identity_accepted': False, 'treatment_assigned': False}
        try:
            path = args.archive / (sid + '.html')
            if not path.exists():
                temporary = path.with_suffix('.download')
                result = subprocess.run(['curl.exe', '--fail', '--location', '--silent', '--show-error',
                                         '--max-time', '25', '--max-filesize', '5000000', '-o', str(temporary), url],
                                        capture_output=True, timeout=30)
                if result.returncode:
                    raise RuntimeError(result.stderr.decode(errors='replace'))
                temporary.rename(path)
            raw = path.read_bytes()
            text = BeautifulSoup(raw, 'html.parser').get_text('\n', strip=True)
            assert all(token in ''.join(text.split()) for token in tokens), 'Expected labels absent'
            path.with_suffix('.txt').write_text(text, encoding='utf-8')
            row.update(status='archived_labels_checked', bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        except Exception as exc:
            row['error'] = str(exc)
        rows.append(row)
    args.output.mkdir(parents=True)
    with (args.output / 'building_label_evidence.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=sorted(set().union(*(r.keys() for r in rows))))
        writer.writeheader()
        writer.writerows(rows)
    summary = {'sources': rows, 'archived_n': sum(r['status'] == 'archived_labels_checked' for r in rows),
               'construction_year_mapping_accepted_n': 0, 'sample_split_performed': False,
               'raw_pages_publicly_republished': False}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
