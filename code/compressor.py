"""Native-cap calibration for the official LLMLingua-2 MeetingBank checkpoint."""
import hashlib
import torch
from llmlingua import PromptCompressor
from huggingface_hub import snapshot_download
from native_completion import READ_SYSTEM,READ_USER,chat,count,render_documents,visible,sources

REPO='microsoft/llmlingua-2-xlm-roberta-large-meetingbank'
REVISION='ebaba9b0e874dadd3003ffcff828e4397e568089'

def load_compressor():
 path=snapshot_download(REPO,revision=REVISION)
 model=PromptCompressor(model_name=path,device_map='cuda',use_llmlingua2=True,model_config={'local_files_only':True,'trust_remote_code':False,'torch_dtype':torch.float32},llmlingua2_config={'max_batch_size':20})
 model.model.eval();return model

def compress(question,ranked,seed,tokenizers,compressor):
 """Return all six calibrated prompts; cache exact classifier tensors per question."""
 original_forward=compressor.model.forward;cache={}
 def cached_forward(*args,**kwargs):
  assert not args and all(torch.is_tensor(v) for v in kwargs.values())
  key=tuple((k,tuple(v.shape),str(v.dtype),hashlib.sha256(v.detach().cpu().numpy().tobytes()).hexdigest()) for k,v in sorted(kwargs.items()))
  if key not in cache:cache[key]=original_forward(**kwargs)
  return cache[key]
 compressor.model.forward=cached_forward
 try:
  raw,_=sources(ranked);docs=[visible(d,tokenizers['qwen7'])|{'text':d['text']} for d in raw];evidence=render_documents(docs);candidates={}
  def candidate(target):
   if target not in candidates:candidates[target]=compressor.compress_prompt_llmlingua2(evidence,target_token=target,use_context_level_filter=False,force_tokens=['\n'],drop_consecutive=False)['compressed_prompt']
   return candidates[target]
  origin=compressor.get_token_length(evidence,use_oai_tokenizer=True);rows=[]
  for reader,tokenizer in tokenizers.items():
   seed_tokens=count(tokenizer,question,seed['documents'])
   def native(text):
    p=chat(tokenizer,READ_SYSTEM,READ_USER.format(question=question,evidence=text,reasoning='(not supplied)'))
    return p,len(tokenizer.encode(p,add_special_tokens=False))
   for allowance in [128,256,512]:
    cap=seed_tokens+allowance;low,high=1,origin;best=None;trials=[]
    text=candidate(1);p,actual=native(text);trials.append(dict(target=1,native_tokens=actual))
    if actual<=cap:best=(actual,p,text,1)
    assert best is not None
    for _ in range(10):
     if low>high:break
     target=(low+high)//2;text=candidate(target);p,actual=native(text);trials.append(dict(target=target,native_tokens=actual))
     if actual<=cap:
      if actual>best[0]:best=(actual,p,text,target)
      low=target+1
     else:high=target-1
    actual,p,text,target=best
    rows.append(dict(reader=reader,arm='llmlingua2',allowance=allowance,prompt=p,prompt_tokens=actual,seed_tokens=seed_tokens,native_cap=cap,unspent_tokens=cap-actual,compressed_evidence=text,compressor_target=target,calibration=trials))
  return rows
 finally:compressor.model.forward=original_forward
