"""Archive selected official redevelopment evidence and Sanjiu plan attachments."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import urljoin

from bs4 import BeautifulSoup

SOURCES = [
    ('sanjiu_plan', 'https://www.szlh.gov.cn/lhqzfhjsj/gkmlpt/content/12/12593/post_12593231.html', ['2026年', '第一批']),
    ('mutoulong_return', 'https://www.szlh.gov.cn/zwgk/zcjd/2025/jd2025nzfgzbg/zcyw/content/post_12083256.html', ['木头龙', '首批业主收房回迁']),
    ('luohu_2026_half', 'https://www.sz.gov.cn/szzt2010/wgkzl/jggk/lsqkgk/content/post_12916257.html', ['第一幼儿园', '5月23日']),
    ('luofang_adjustment', 'https://www.szlh.gov.cn/lhqzfhjsj/gkmlpt/content/12/12906/post_12906896.html', ['计划调整', '2026']),
    ('huafubei_permit', 'https://www.sz.gov.cn/szzt2010/wgkzl/glgk/jgxxgk/gtzy/content/post_12661761.html', ['B308-0071', '4403042026GG0015686']),
    ('qingyi_land', 'https://www.sz.gov.cn/szzt2010/wgkzl/glgk/jgxxgk/gtzy/content/post_12213096.html', ['A006-0942', '6542.5']),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    args.archive.mkdir(parents=True, exist_ok=True)
    rows = []

    def fetch(sid, url, tokens=()):
        suffix = '.pdf' if url.endswith('.pdf') else '.html'
        path = args.archive / (sid + suffix)
        row = {'source_id': sid, 'url': url, 'status': 'failed'}
        try:
            if not path.exists():
                tmp = path.with_suffix('.download')
                r = subprocess.run(['curl.exe', '--fail', '--location', '--silent', '--show-error',
                                    '--max-time', '25', '--max-filesize', '15000000', '-o', str(tmp), url],
                                   capture_output=True, timeout=30)
                if r.returncode:
                    raise RuntimeError(r.stderr.decode(errors='replace'))
                tmp.rename(path)
            body = path.read_bytes()
            if suffix == '.pdf':
                assert body.startswith(b'%PDF')
            else:
                soup = BeautifulSoup(body, 'html.parser')
                text = soup.get_text('\n', strip=True)
                assert all(token in ''.join(text.split()) for token in tokens)
                path.with_suffix('.txt').write_text(text, encoding='utf-8')
            row.update(status='archived', bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
            if sid == 'sanjiu_plan':
                row['attachments'] = [{'title': a.get_text(strip=True), 'url': urljoin(url, a['href'])}
                                      for a in soup.find_all('a', href=True) if '.pdf' in a['href']]
        except Exception as exc:
            row['error'] = str(exc)
        rows.append(row)
        return row

    for sid, url, tokens in SOURCES:
        row = fetch(sid, url, tokens)
        if sid == 'sanjiu_plan' and row['status'] == 'archived':
            for i, link in enumerate(row.get('attachments', [])[:2], 1):
                fetch('sanjiu_attachment_' + str(i), link['url'])
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps({'sources': rows, 'original_pages_not_republished': True},
                                        ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(rows, ensure_ascii=False))


if __name__ == '__main__':
    main()
