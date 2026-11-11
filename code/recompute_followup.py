"""Recompute every post hoc contrast from released question-level predictions."""
import argparse,gzip,json
from pathlib import Path
import numpy as np
import pandas as pd

READERS=['qwen7','llama8'];BUDGETS=[128,256,512];DATASETS=['hotpot','2wiki','musique']
BASELINES={'seed','raw20','unique20'}

def bootstrap(groups):
    means=np.mean([a.mean(axis=0) for a in groups],axis=0)*100
    samples=np.zeros((10000,len(means)));rng=np.random.default_rng(20261111)
    for a in groups:
        for start in range(0,10000,200):
            weights=rng.multinomial(len(a),np.full(len(a),1/len(a)),size=min(200,10000-start))
            samples[start:start+len(weights)]+=weights@a/(len(groups)*len(a))
    return means,np.quantile(samples,[.025,.975],axis=0)*100

def compute(rows):
    frame=pd.DataFrame(rows)
    assert len(frame)==162000 and not frame.duplicated(['episode_id','reader','allowance','arm']).any()
    ids={d:sorted(frame.loc[frame.dataset==d,'episode_id'].unique()) for d in DATASETS}
    assert all(len(v)==1500 for v in ids.values())
    specs=[];columns=[]
    for metric in ['em','f1']:
        wide=frame.pivot(index='episode_id',columns=['reader','allowance','arm'],values=metric)
        for reader in ['average']+READERS:
            conditions=[(b,'linked',arm) for b in [0]+BUDGETS for arm in ['window','seed','raw20','unique20','no_first_priority','seed_only','rerank']]
            conditions += [(0,'seed','unique20'),(0,'seed','raw20'),(0,'unique20','raw20'),(0,'window','seed')]
            for b,left,right in conditions:
                selected_readers=READERS if reader=='average' else [reader]
                selected_budgets=BUDGETS if b==0 else [b]
                deltas=[]
                for rr in selected_readers:
                    for bb in selected_budgets:
                        deltas.append(wide[rr,0 if left in BASELINES else bb,left]-wide[rr,0 if right in BASELINES else bb,right])
                columns.append(pd.concat(deltas,axis=1).mean(axis=1))
                specs.append(dict(metric=metric,reader=reader,allowance=b,left=left,right=right))
    allvalues=pd.concat(columns,axis=1)
    arrays=[allvalues.loc[ids[d]].to_numpy() for d in DATASETS];effects=[]
    for scope,groups in [('all',arrays)]+[(d,[a]) for d,a in zip(DATASETS,arrays)]:
        mean,bounds=bootstrap(groups)
        for j,spec in enumerate(specs):effects.append(spec|dict(scope=scope,estimate_pp=float(mean[j]),low95=float(bounds[0,j]),high95=float(bounds[1,j])))
    cells=frame.groupby(['dataset','reader','arm','allowance'])[['em','f1','prompt_tokens','output_tokens']].mean().reset_index()
    cells[['em','f1']]*=100
    macro=cells.groupby(['reader','arm','allowance'])[['em','f1','prompt_tokens','output_tokens']].mean().reset_index()
    return dict(effects=effects,macro=macro.to_dict('records'),cells=cells.to_dict('records'),scope='Post hoc descriptive follow-up; no independent confirmatory significance claim.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--predictions',type=Path,default=Path(__file__).resolve().parents[1]/'data/followup_predictions.jsonl.gz');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    with gzip.open(a.predictions,'rt') as f:rows=[json.loads(l) for l in f]
    result=compute(rows);a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'records':len(rows),'effects':len(result['effects']),'recomputed':True}))

if __name__=='__main__':main()
