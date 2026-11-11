"""Recompute paired decompositions directly from the 4,500-row score table."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from recompute import sign_flip
from recompute_followup import bootstrap, READERS, BUDGETS, DATASETS


def compute(frame):
    assert len(frame) == 4500 and frame.episode_id.is_unique
    frame = frame.set_index('episode_id').sort_index()
    ids = {d: frame.index[frame.dataset == d].tolist() for d in DATASETS}
    assert all(len(v) == 1500 for v in ids.values())
    hard = frame.index[(frame.dataset == 'hotpot') & (frame.hotpot_level == 'hard')].tolist()
    assert len(hard) == 231
    descriptors, vectors = [], []
    for metric in ['em', 'f1']:
        for left, right in [('linked', 'window'), ('linked', 'seed'), ('window', 'seed')]:
            for reader in ['average'] + READERS:
                for b in [0] + BUDGETS:
                    rr = READERS if reader == 'average' else [reader]
                    bb = BUDGETS if b == 0 else [b]
                    deltas = [frame[f'{r}.{left}.b{x}.{metric}'] -
                              frame[f'{r}.{right}.b{0 if right == "seed" else x}.{metric}']
                              for r in rr for x in bb]
                    vectors.append(pd.concat(deltas, axis=1).mean(axis=1))
                    descriptors.append(dict(metric=metric, contrast=left+'-'+right, reader=reader, allowance=b))
    values = pd.concat(vectors, axis=1)
    scopes = [('all', [ids[d] for d in DATASETS])] + [(d, [ids[d]]) for d in DATASETS]
    scopes += [('hotpot_hard', [hard]), ('all_hotpot_hard', [hard, ids['2wiki'], ids['musique']])]
    effects = []
    for scope, groups in scopes:
        mean, ci = bootstrap([values.loc[g].to_numpy() for g in groups])
        effects += [d | dict(scope=scope, questions=sum(map(len, groups)), estimate_pp=float(mean[j]),
                            low95=float(ci[0, j]), high95=float(ci[1, j])) for j, d in enumerate(descriptors)]
    ordered = [e for d in DATASETS for e in ids[d]]
    integer = np.rint(values.loc[ordered, 24].to_numpy()*6).astype(np.int32)
    assert descriptors[24] == dict(metric='em', contrast='window-seed', reader='average', allowance=0)
    changes, descriptors = [], []
    for reader in ['average'] + READERS:
        rr = READERS if reader == 'average' else [reader]
        for hi, lo in [(256, 128), (512, 256), (512, 128)]:
            delta = [(frame[f'{r}.linked.b{hi}.em']-frame[f'{r}.window.b{hi}.em']) -
                     (frame[f'{r}.linked.b{lo}.em']-frame[f'{r}.window.b{lo}.em']) for r in rr]
            changes.append(pd.concat(delta, axis=1).mean(axis=1))
            descriptors.append(dict(reader=reader, high_allowance=hi, low_allowance=lo))
    values = pd.concat(changes, axis=1)
    mean, ci = bootstrap([values.loc[ids[d]].to_numpy() for d in DATASETS])
    trends = [d | dict(estimate_pp=float(mean[j]), low95=float(ci[0, j]), high95=float(ci[1, j]))
              for j, d in enumerate(descriptors)]
    return dict(effects=effects, allowance_changes=trends, window_seed_descriptive_test=sign_flip(integer))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--scores', type=Path, default=Path(__file__).resolve().parents[1]/'data/confirmatory_question_scores.csv')
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    args.out.write_text(json.dumps(compute(pd.read_csv(args.scores)), indent=2)+'\n')
