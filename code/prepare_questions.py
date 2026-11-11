"""Resolve release IDs against separately downloaded benchmark distributions."""
import argparse,gzip,json
from pathlib import Path
from native_completion import digest,normalize_question

def records(path):
 p=Path(path)
 if p.suffix=='.parquet':
  import pandas as pd
  return pd.read_parquet(p).to_dict('records')
 with open(p) as f:
  first=f.read(1);f.seek(0)
  return json.load(f) if first=='[' else [json.loads(line) for line in f if line.strip()]

def main():
 p=argparse.ArgumentParser();p.add_argument('--ids',required=True);p.add_argument('--source',action='append',required=True,help='dataset=path; repeat for parquet shards');p.add_argument('--questions',required=True);p.add_argument('--labels',required=True);a=p.parse_args()
 with gzip.open(a.ids,'rt') as f:ids=[json.loads(line) for line in f]
 wanted={(r['dataset'],r['source_id']):r for r in ids};found={}
 for source in a.source:
  dataset,path=source.split('=',1)
  for r in records(path):
   key=dataset,r.get('id',r.get('_id'))
   if key not in wanted:continue
   identity=wanted[key];assert digest(normalize_question(r['question']))==identity['group_id']
   if dataset=='2wiki':gold=r['golden_answers'] # Exact FlashRAG distribution, including aliases.
   elif dataset=='musique':gold=list(dict.fromkeys([r['answer']]+r['answer_aliases']))
   else:gold=[r['answer']]
   found[key]=(identity|dict(question=r['question']),identity|dict(gold_answers=gold))
 assert found.keys()==wanted.keys(),f'Missing {len(wanted.keys()-found.keys())} IDs; verify source splits/distributions'
 with open(a.questions,'w') as questions,open(a.labels,'w') as labels:
  for identity in ids:
   q,l=found[identity['dataset'],identity['source_id']]
   questions.write(json.dumps(q,ensure_ascii=False)+'\n');labels.write(json.dumps(l,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
