"""Replay priority methods from frozen slots/seed IDs and separately obtained corpus."""
import argparse,gzip,json
from pathlib import Path
from native_completion import *


def read(path):
 opener=gzip.open if str(path).endswith('.gz') else open
 with opener(path,'rt') as f:return [json.loads(line) for line in f if line.strip()]


def collect_corpus(path,wanted):
 out={}
 with open(path) as f:
  for line in f:
   row=line.rstrip('\n').split('\t',2)
   if not row or not row[0].isdigit():continue
   pid='wiki:'+row[0]
   if pid in wanted:
    def unquote(text):
     text=text.strip();return text[1:-1].replace('""','"') if len(text)>1 and text[0]==text[-1]=='"' else text
    out[pid]=dict(pid=pid,text=unquote(row[1]),title=unquote(row[2]))
   if len(out)==len(wanted):break
 assert len(out)==len(wanted),'Missing corpus IDs'
 return out


def main():
 p=argparse.ArgumentParser();p.add_argument('--contexts',required=True);p.add_argument('--questions',required=True,help='JSONL with dataset, source_id, question');p.add_argument('--corpus',required=True,help='DPR psgs_w100.tsv, decompressed');p.add_argument('--out',required=True);p.add_argument('--reader',choices=list(READERS),required=True);p.add_argument('--arm',choices=ARMS,default='linked');p.add_argument('--allowance',type=int,choices=BUDGETS,default=256);a=p.parse_args()
 contexts=read(a.contexts);questions={(r['dataset'],r['source_id']):r['question'] for r in read(a.questions)}
 corpus=collect_corpus(a.corpus,{s['pid'] for r in contexts for s in r.get('slots',[])})
 tok=reader_tokenizer(a.reader)
 with open(a.out,'w') as out:
  for r in contexts:
   question=questions[r['dataset'],r['source_id']]
   if not r['upstream_ok']:
    value=dict(prompt=prompt(tok,question,[]),upstream_failure=True)
   else:
    raw=[corpus[s['pid']]|{k:s[k] for k in ['pid','rank','score']} for s in r['slots']]
    assert all(digest(d['text'])==s['text_sha256'] and digest(d['title'])==s['title_sha256'] for d,s in zip(raw,r['slots']))
    ranked=[raw[i:i+5] for i in range(0,20,5)];_,units=sources(ranked)
    seed=dict(selection=dict(selected=r['seed_ids'],valid=r['seed_valid']))
    seed['documents']=render(raw,units,r['seed_ids']) if r['seed_valid'] else [visible(d,shared_tokenizer()) for d in raw]
    if r['seed_valid']:value=expand(question,ranked,seed,tok,a.allowance,a.arm)
    else:value=dict(prompt=prompt(tok,question,seed['documents']),upstream_failure=False,invalid_seed=True)
   value.update(episode_id=r['episode_id'],reader=a.reader,arm=a.arm,allowance=a.allowance)
   out.write(json.dumps(value,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
