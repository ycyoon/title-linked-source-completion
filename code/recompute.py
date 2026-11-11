"""Recompute all macro scores, paired intervals and the single test contrast."""
import argparse,gzip,json
from pathlib import Path
import numpy as np
import pandas as pd

READERS=['qwen7','llama8'];BUDGETS=[128,256,512]
BASELINES=['seed','closed_book','excerpt20','raw20']

def load(path):
 with gzip.open(path,'rt') as f:return [json.loads(line) for line in f]

def sign_flip(values,draws=100000,seed=20261111):
 values=np.asarray(values,dtype=np.int32);observed=abs(int(values.sum()));rng=np.random.default_rng(seed);extreme=0
 for start in range(0,draws,256):
  signs=(2*rng.integers(0,2,size=(min(256,draws-start),len(values)),dtype=np.int8)-1).astype(np.int32)
  extreme+=int((np.abs(signs@values)>=observed).sum())
 return dict(p=(extreme+1)/(draws+1),extreme=extreme,draws=draws,seed=seed,observed_integer_sum=int(values.sum()))

def compute(rows,study):
 datasets=['hotpot','2wiki']+(['musique'] if study=='test' else [])
 comps=['window']+(['first_no_link','no_first_priority','question_only','seed_only','random'] if study=='dev' else [])+['llmlingua2']+BASELINES
 frame=pd.DataFrame(rows);metrics=['em','f1','prompt_tokens','output_tokens','unspent_tokens']
 cells=frame.groupby(['reader','allowance','arm','dataset'])[metrics].mean().reset_index();cells[['em','f1']]*=100
 macro=cells.groupby(['reader','allowance','arm'])[metrics].mean().reset_index()
 by={tuple(r[k] for k in ['episode_id','reader','allowance','arm']):r for r in rows}
 ids={d:sorted({r['episode_id'] for r in rows if r['dataset']==d}) for d in datasets}
 pairs=[(r,b,arm) for r in READERS for b in BUDGETS for arm in comps];contrasts=[];aggregate=[];primary=None
 for metric in ['em','f1']:
  arrays=[np.array([[by[e,r,b,'linked'][metric]-by[e,r,0 if arm in BASELINES else b,arm][metric] for r,b,arm in pairs] for e in ids[d]]) for d in datasets]
  estimates=sum(a.mean(axis=0) for a in arrays)/len(datasets);rng=np.random.default_rng(20261111);boot=np.zeros((10000,len(pairs)))
  for a in arrays:
   # Preserve the original generator calls for each study.
   chunk=250 if study=='test' else 10000
   for start in range(0,10000,chunk):
    weights=rng.multinomial(len(a),np.full(len(a),1/len(a)),size=min(chunk,10000-start))
    boot[start:start+len(weights)]+=(weights@a)/(len(datasets)*len(a))
  ci=np.quantile(boot,[.025,.975],axis=0)*100
  for j,(reader,b,arm) in enumerate(pairs):
   contrasts.append(dict(reader=reader,allowance=b,comparator=arm,metric=metric,estimate_pp=float(100*estimates[j]),low95=float(ci[0,j]),high95=float(ci[1,j]),wins=sum(int((a[:,j]>0).sum()) for a in arrays),losses=sum(int((a[:,j]<0).sum()) for a in arrays),ties=sum(int((a[:,j]==0).sum()) for a in arrays)))
  for arm in comps:
   js=[j for j,p in enumerate(pairs) if p[2]==arm];bs=boot[:,js].mean(axis=1)*100
   row=dict(comparator=arm,metric=metric,estimate_pp=float(100*estimates[js].mean()),low95=float(np.quantile(bs,.025)),high95=float(np.quantile(bs,.975)));aggregate.append(row)
   if study=='test' and arm=='window' and metric=='em':
    counts=np.concatenate([a[:,js].sum(axis=1) for a in arrays]);assert np.all(counts==np.rint(counts))
    primary=row|dict(test=sign_flip(counts.astype(np.int32)),per_dataset_pp={d:float(100*a[:,js].mean()) for d,a in zip(datasets,arrays)})
 return dict(primary=primary,aggregate=aggregate,contrasts=contrasts,macro=macro.astype(object).where(pd.notna(macro),None).to_dict('records'),cells=cells.astype(object).where(pd.notna(cells),None).to_dict('records'))

def main():
 p=argparse.ArgumentParser();p.add_argument('--study',choices=['dev','test'],required=True);p.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[1]/'data');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 result=compute(load(a.data/(a.study+'_predictions.jsonl.gz')),a.study);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['primary'] or result['aggregate']))
if __name__=='__main__':main()
