"""Verify released answer scores against locally resolved benchmark labels."""
import argparse,gzip,json
from metrics import score

def main():
 p=argparse.ArgumentParser();p.add_argument('--predictions',required=True);p.add_argument('--labels',required=True);a=p.parse_args()
 with open(a.labels) as f:labels={r['episode_id']:r for r in map(json.loads,f)}
 count=0
 with gzip.open(a.predictions,'rt') as f:
  for line in f:
   r=json.loads(line);l=labels[r['episode_id']];actual=score(r['raw_answer'],l['gold_answers'],l['dataset'],r['failure'])
   assert actual=={k:r[k] for k in ['em','f1']},(r['episode_id'],r['reader'],r['arm'],r['allowance']);count+=1
 print(json.dumps(dict(verified_rows=count,all_scores_identical=True)))
if __name__=='__main__':main()
