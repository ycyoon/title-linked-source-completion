"""Independent dataframe recomputation of larger-reader and rendering contrasts."""
import argparse,gzip,json
from pathlib import Path
import pandas as pd
from recompute_followup import bootstrap,BUDGETS,DATASETS
BASE={'seed','compact_seed','unique20'}

def compute(rows):
    frame=pd.DataFrame(rows);assert len(frame)==229500 and not frame.duplicated(['episode_id','reader','allowance','arm']).any()
    ids={d:sorted(frame.loc[frame.dataset==d,'episode_id'].unique()) for d in DATASETS};assert all(len(x)==1500 for x in ids.values())
    specs=[];columns=[]
    for metric in ['em','f1']:
        wide=frame.pivot(index='episode_id',columns=['reader','allowance','arm'],values=metric)
        def col(r,b,arm):return wide[r,0 if arm in BASE else b,arm]
        for b in [0]+BUDGETS:
            bb=BUDGETS if b==0 else [b]
            for left,right in [('linked','seed'),('window','seed'),('rerank','seed'),('linked','window'),('rerank','linked'),('seed','unique20'),('linked','unique20'),('rerank','unique20')]:
                if (left,right)==('seed','unique20') and b:continue
                specs.append(dict(metric=metric,reader='qwen14',allowance=b,kind='large_reader',left=left,right=right))
                columns.append(pd.concat([col('qwen14',x,left)-col('qwen14',x,right) for x in bb],axis=1).mean(axis=1))
            for reader in ['average','qwen7','llama8']:
                rr=['qwen7','llama8'] if reader=='average' else [reader]
                for prefix in ['','compact_']:
                    for left,right in [('linked','seed'),('window','seed'),('rerank','seed'),('linked','window'),('rerank','linked')]:
                        left,right=prefix+left,prefix+right
                        specs.append(dict(metric=metric,reader=reader,allowance=b,kind='within_rendering',left=left,right=right))
                        columns.append(pd.concat([col(r,x,left)-col(r,x,right) for r in rr for x in bb],axis=1).mean(axis=1))
                for arm in ['seed','linked','window','rerank']:
                    if arm=='seed' and b:continue
                    delta=pd.concat([col(r,x,'compact_'+arm)-col(r,x,arm) for r in rr for x in bb],axis=1).mean(axis=1)
                    specs.append(dict(metric=metric,reader=reader,allowance=b,kind='rendering_change',left='compact_'+arm,right=arm));columns.append(delta)
                    if arm!='seed':
                        seed_delta=pd.concat([col(r,0,'compact_seed')-col(r,0,'seed') for r in rr],axis=1).mean(axis=1)
                        specs.append(dict(metric=metric,reader=reader,allowance=b,kind='expansion_interaction',left='compact_'+arm,right=arm));columns.append(delta-seed_delta)
            for arm in ['linked','window','rerank']:
                deltas=[(col('qwen14',x,arm)-col('qwen14',0,'seed'))-(col('qwen7',x,arm)-col('qwen7',0,'seed')) for x in bb]
                specs.append(dict(metric=metric,reader='qwen14_minus_qwen7',allowance=b,kind='reader_interaction',left=arm,right='seed'));columns.append(pd.concat(deltas,axis=1).mean(axis=1))
    values=pd.concat(columns,axis=1);effects=[]
    for scope,groups in [('all',[ids[d] for d in DATASETS])]+[(d,[ids[d]]) for d in DATASETS]:
        mean,ci=bootstrap([values.loc[g].to_numpy() for g in groups])
        effects.extend(s|dict(scope=scope,estimate_pp=float(mean[j]),low95=float(ci[0,j]),high95=float(ci[1,j])) for j,s in enumerate(specs))
    cells=frame.groupby(['dataset','reader','arm','allowance'])[['em','f1','prompt_tokens','output_tokens']].mean().reset_index();cells[['em','f1']]*=100
    macro=cells.groupby(['reader','arm','allowance'])[['em','f1','prompt_tokens','output_tokens']].mean().reset_index()
    return dict(effects=effects,macro=macro.to_dict('records'),cells=cells.to_dict('records'),scope='Post hoc reused-question analysis, unadjusted intervals; not independent confirmation.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--predictions',type=Path,default=Path(__file__).resolve().parents[1]/'data/rendering_predictions.jsonl.gz');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    with gzip.open(a.predictions,'rt') as f:rows=[json.loads(l) for l in f]
    result=compute(rows);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'records':len(rows),'effects':len(result['effects'])}))
