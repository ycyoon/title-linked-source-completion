"""Post hoc score-priority versus seed contrasts; no new confirmation."""
import argparse
import gzip
import json
from pathlib import Path
import pandas as pd
from recompute_followup import bootstrap, READERS, BUDGETS, DATASETS


def compute(rows):
    f = pd.DataFrame(rows)
    ids = {d: sorted(f.loc[f.dataset == d, 'episode_id'].unique()) for d in DATASETS}
    assert len(f) == 162000 and all(len(x) == 1500 for x in ids.values())
    specs, columns = [], []
    for metric in ['em', 'f1']:
        wide = f.pivot(index='episode_id', columns=['reader', 'allowance', 'arm'], values=metric)
        for reader in ['average'] + READERS:
            for b in [0] + BUDGETS:
                rr = READERS if reader == 'average' else [reader]
                bb = BUDGETS if b == 0 else [b]
                columns.append(pd.concat([wide[r, x, 'rerank']-wide[r, 0, 'seed'] for r in rr for x in bb], axis=1).mean(axis=1))
                specs.append(dict(metric=metric, reader=reader, allowance=b, left='rerank', right='seed'))
    values = pd.concat(columns, axis=1)
    effects = []
    for scope, groups in [('all', [ids[d] for d in DATASETS])] + [(d, [ids[d]]) for d in DATASETS]:
        mean, ci = bootstrap([values.loc[g].to_numpy() for g in groups])
        effects += [s | dict(scope=scope, estimate_pp=float(mean[j]), low95=float(ci[0, j]), high95=float(ci[1, j])) for j, s in enumerate(specs)]
    return effects


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--predictions', type=Path, default=Path(__file__).resolve().parents[1]/'data/followup_predictions.jsonl.gz')
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    with gzip.open(args.predictions, 'rt') as f:
        result = compute([json.loads(l) for l in f])
    pd.DataFrame(result).to_csv(args.out, index=False)
