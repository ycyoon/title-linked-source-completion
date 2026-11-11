"""Joint compact-ID/exact-source deduplication intervention; no label access."""
from native_completion import normalize_question,shared_tokenizer,sources,prompt,count,visible


def identity(raw,units,k):
    i,j,start,end,_=units[k]
    return raw[i]['pid'],start,end


def compact(raw,units,keys):
    first={}
    for i,d in enumerate(raw):
        if d['pid'] in first:
            old=raw[first[d['pid']]];assert (old['title'],old['text'])==(d['title'],d['text'])
        else:first[d['pid']]=i
    selected={}
    for k in keys:selected.setdefault(identity(raw,units,k),k)
    docs=[];tok=shared_tokenizer()
    for pid,i in first.items():
        chosen=sorted((k for ident,k in selected.items() if ident[0]==pid),key=lambda k:units[k][2])
        if not chosen:continue
        text=' '.join(units[k][4] for k in chosen)
        docs.append(visible(raw[i],tok)|dict(pid='P'+str(i+1),text=text,text_tokens=len(tok.encode(text,add_special_tokens=False)),
            source_spans=[dict(start=units[k][2],end=units[k][3],sentence_id=k) for k in chosen]))
    return docs


def fallback(raw,docs):
    first={}
    for i,d in enumerate(raw):first.setdefault(d['pid'],i)
    seen={};result=[]
    for d in docs:
        pid=d['corpus_pid']
        if pid in seen:assert (d['text'],d['title'])==seen[pid]
        else:
            seen[pid]=(d['text'],d['title']);result.append(d|dict(pid='P'+str(first[pid]+1)))
    return result


def intervention(question,ranked,seed,tok,b,arm):
    raw,units=sources(ranked);keys=seed['selection']['selected'];valid=bool(seed['selection']['valid'] and keys)
    base=compact(raw,units,keys) if valid else fallback(raw,seed['documents'])
    seed_tokens=count(tok,question,base);original_seed_tokens=count(tok,question,seed['documents']);cap=original_seed_tokens+b
    selected=list(keys);seen={identity(raw,units,k) for k in keys}
    normalized=' '+normalize_question(question+' '+' '.join(units[k][4] for k in keys))+' '
    linked={i for i,d in enumerate(raw) if (len(normalize_question(d['title']).split())>=2 or len(normalize_question(d['title']))>=4) and ' '+normalize_question(d['title'])+' ' in normalized}
    def priority(k):
        i,j,*_=units[k];dist=[abs(j-units[s][1]) for s in keys if units[s][0]==i]
        window=(min(dist) if dist else 1000000,i,j)
        if arm=='window':return window
        if arm=='rerank':return (-float(raw[i]['score']),*window)
        assert arm=='linked'
        return (0 if i in linked and j==0 else 1 if i in linked else 2,*window)
    if valid and arm!='seed':
        for k in sorted((k for k in units if k not in keys),key=priority):
            ident=identity(raw,units,k)
            if ident in seen:continue
            if count(tok,question,compact(raw,units,selected+[k]))<=cap:selected.append(k);seen.add(ident)
    docs=compact(raw,units,selected) if valid else base
    actual=count(tok,question,docs)
    if arm!='seed':assert actual<=cap
    return dict(arm='compact_'+arm,allowance=b,documents=docs,prompt=prompt(tok,question,docs),prompt_tokens=actual,seed_tokens=seed_tokens,
        original_seed_tokens=original_seed_tokens,native_cap=cap if arm!='seed' else None,unspent_tokens=cap-actual if arm!='seed' else None,
        seed_ids=keys,selected_ids=selected,seed_valid=valid,rendering='compact',unique_selected_segments=len(seen),unique_seed_segments=len({identity(raw,units,k) for k in keys}))


from functools import lru_cache
import native_completion as n
from followup_inputs import construct as original_construct,ARMS as ORIGINAL_ARMS
READERS=n.READERS|{'qwen14':('Qwen/Qwen2.5-14B-Instruct','cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8',[151645,151643])}
ARMS=ORIGINAL_ARMS+['compact_seed','compact_linked','compact_window','compact_rerank']

@lru_cache(maxsize=3)
def reader_tokenizer(reader):
    if reader in n.READERS:return n.reader_tokenizer(reader)
    from transformers import AutoTokenizer
    repo,revision,_=READERS[reader]
    return AutoTokenizer.from_pretrained(repo,revision=revision)

def construct(question,ranked,seed,tokenizer,allowance,arm):
    if arm.startswith('compact_'):
        return intervention(question,ranked,seed,tokenizer,0 if arm=='compact_seed' else allowance,arm.removeprefix('compact_'))
    return original_construct(question,ranked,seed,tokenizer,allowance,arm)
