"""Read prepared prompts with a local OpenAI-compatible vLLM endpoint."""
import argparse,json,time
from pathlib import Path
import requests
from native_completion import READERS

def main():
 p=argparse.ArgumentParser();p.add_argument('--inputs',required=True);p.add_argument('--endpoint',required=True);p.add_argument('--model',required=True);p.add_argument('--out',required=True);a=p.parse_args()
 assert not Path(a.out).exists(),'Keep original outputs; choose a new output file'
 with open(a.inputs) as source,open(a.out,'w') as out:
  for line in source:
   r=json.loads(line);record={k:r[k] for k in ['episode_id','reader','arm','allowance']};record['failure']=bool(r.get('upstream_failure'))
   if record['failure']:record['raw_answer']=''
   else:
    payload=dict(model=a.model,prompt=r['prompt'],temperature=0,seed=42,max_tokens=96,stop_token_ids=READERS[r['reader']][2],add_special_tokens=False)
    errors=[]
    for attempt in range(3):
     try:
      response=requests.post(a.endpoint.rstrip('/')+'/completions',json=payload,timeout=180);response.raise_for_status();value=response.json()
      record.update(raw_answer=value['choices'][0]['text'],finish_reason=value['choices'][0]['finish_reason'],usage=value['usage']);break
     except requests.RequestException as error:
      errors.append(str(error))
      if attempt==2:record.update(failure=True,raw_answer='')
      else:time.sleep(attempt+1)
    record['errors']=errors
   out.write(json.dumps(record,ensure_ascii=False)+'\n');out.flush()
if __name__=='__main__':main()
