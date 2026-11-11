"""Post hoc deduplicated context and archived-score expansion controls."""
import native_completion as n

ARMS=n.ARMS+['rerank','seed','raw20','unique20']

def construct(question,ranked,seed,tokenizer,allowance,arm):
    raw,units=n.sources(ranked)
    keys=seed['selection']['selected']
    seed_tokens=n.count(tokenizer,question,seed['documents'])
    if arm in ['seed','raw20','unique20']:
        if arm=='seed':docs=seed['documents']
        else:
            docs=[];seen=set()
            for d in raw:
                if arm=='unique20' and d['pid'] in seen:continue
                seen.add(d['pid'])
                docs.append(n.visible(d,n.shared_tokenizer())|dict(text=d['text'],text_tokens=len(n.shared_tokenizer().encode(d['text'],add_special_tokens=False))))
        return dict(documents=docs,prompt=n.prompt(tokenizer,question,docs),prompt_tokens=n.count(tokenizer,question,docs),seed_tokens=seed_tokens,arm=arm,allowance=0)
    valid=bool(seed['selection']['valid'] and keys)
    if not valid:
        return dict(documents=seed['documents'],prompt=n.prompt(tokenizer,question,seed['documents']),prompt_tokens=seed_tokens,
                    seed_tokens=seed_tokens,seed_ids=keys,selected_ids=keys,native_cap=seed_tokens+allowance,unspent_tokens=allowance,arm=arm,allowance=allowance)
    if arm in n.ARMS:return n.expand(question,ranked,seed,tokenizer,allowance,arm)
    assert arm=='rerank'
    def priority(k):
        i,j,*_=units[k]
        distances=[abs(j-units[s][1]) for s in keys if units[s][0]==i]
        return (-float(raw[i]['score']),min(distances) if distances else 1000000,i,j)
    cap=seed_tokens+allowance;selected=list(keys)
    for k in sorted((k for k in units if k not in keys),key=priority):
        if n.count(tokenizer,question,n.render(raw,units,selected+[k]))<=cap:selected.append(k)
    docs=n.render(raw,units,selected);actual=n.count(tokenizer,question,docs)
    return dict(documents=docs,prompt=n.prompt(tokenizer,question,docs),prompt_tokens=actual,seed_tokens=seed_tokens,
                native_cap=cap,unspent_tokens=cap-actual,seed_ids=keys,selected_ids=selected,arm=arm,allowance=allowance)
