"""Compare sourced event intervals with data coverage, without accepting treatment."""
import argparse
import json
from pathlib import Path

import pandas as pd


def window_status(lower, upper, cutoff):
    if pd.isna(lower) or pd.isna(upper):
        return '事件日期待核'
    start, end, last = map(pd.Timestamp, [lower, upper, cutoff])
    if start > end:
        raise ValueError('Event interval reversed')
    if start > last:
        return '事件在交易截止后，无现有事后观测'
    if end > last:
        return '事件区间跨交易截止，不能确认事后观测'
    return '全市来源时间覆盖事件后，仍需项目附近成交支持'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new output directory')
    root = Path(__file__).resolve().parents[3]
    base = root / 'scopes/luohu/project_registry/expansion_review_20261013'
    claims = pd.read_csv(base / 'project_claims.csv', keep_default_na=False)
    events = pd.read_csv(base / 'event_evidence.csv')
    coverage = json.loads((root / 'scopes/shenzhen/summary/coverage.json').read_text())
    rows = []
    for record in claims.to_dict('records'):
        event = events[events.project_name.eq(record['project_name'])]
        assert len(event) <= 1
        if event.empty:
            kind, lower, upper, scope = '暂无可入表事件', None, None, '不从预测回迁年份推断实际事件'
        else:
            item = event.iloc[0]
            kind, lower, upper, scope = item.event_type, item.date_lower, item.date_upper, item.source_scope
        status = window_status(lower, upper, coverage['last_date'])
        priority = ('优先核定主案例边界与分期' if record['project_name'] == '木头龙' else
                    '优先核定旧住宅及分期' if '旧住宅' in record['subject_type'] else
                    '单列制度或原址类型后再比较')
        rows.append({'district': record['district'], 'project_name': record['project_name'],
                     'subject_type': record['subject_type'], 'sourced_event_type': kind,
                     'event_lower': lower, 'event_upper': upper, 'event_scope': scope,
                     'source_transaction_cutoff': coverage['last_date'], 'observation_status': status,
                     'research_priority': priority, 'approved_project_sample': False,
                     'project_geometry_verified': False, 'local_post_transactions_verified': False})
    result = pd.DataFrame(rows)
    args.output.mkdir(parents=True)
    result.to_csv(args.output / 'project_readiness.csv', index=False, encoding='utf-8-sig')
    summary = {'candidate_n': len(result), 'event_evidence_rows': len(events),
               'source_cutoff': coverage['last_date'],
               'observation_status_counts': result.observation_status.value_counts().to_dict(),
               'accepted_project_samples': 0, 'event_dates_not_imputed': True}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
