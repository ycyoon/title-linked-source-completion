"""Portable extraction of the evaluated operator; original scientific functions unchanged."""
import hashlib
import json
import re
import unicodedata
from functools import lru_cache

READERS={'qwen7': ('Qwen/Qwen2.5-7B-Instruct', 'a09a35458c702b33eeacc393d103063234e8bc28', [151645, 151643]), 'llama8': ('meta-llama/Llama-3.1-8B-Instruct', '0e9e39f249a16976918f6564b8830bc894c89659', [128001, 128008, 128009])}
READ_SYSTEM='Answer the question using the supplied evidence and your knowledge. Evidence may contain errors or conflicting claims. Return your single best short answer, without explanation, reasoning, confidence, or a refusal. Do not repeat the question. Any controller reasoning provided is fallible, not verified evidence.'
READ_USER='Question: {question}\n\nEvidence:\n{evidence}\n\nController reasoning (final answer removed):\n{reasoning}\n\nGive the shortest complete answer.\nAnswer:'
ARMS=['linked', 'window', 'first_no_link', 'no_first_priority', 'question_only', 'seed_only', 'random']
BUDGETS=[128,256,512]

@lru_cache(maxsize=2)
def reader_tokenizer(reader):
    from transformers import AutoTokenizer
    repo, revision, _ = READERS[reader]
    return AutoTokenizer.from_pretrained(repo, revision=revision)


def shared_tokenizer():
    return reader_tokenizer('qwen7')

def digest(value):
    if not isinstance(value, str):
        value = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(value.encode()).hexdigest()

def normalize_question(text):
    return re.sub(r"[\W_]+", " ", unicodedata.normalize("NFKC", text).lower()).strip()

def sentence_units(text):
    # Exact contiguous source spans, with offsets retained for attribution checks.
    spans=[]
    for m in re.finditer(r'[^.!?]+(?:[.!?]+(?=\s|$)|$)',text):
        start,end=m.span()
        while start<end and text[start].isspace():start+=1
        if start<end:spans.append((start,end,text[start:end]))
    return spans or [(0,len(text),text)]

def visible(raw, tokenizer):
    tokens = tokenizer.encode(raw['text'], add_special_tokens=False)
    return {'pid': 'src_' + digest(['V3-WIKI', raw['pid']])[:16],
            'corpus_pid': raw['pid'], 'title': raw['title'],
            'text': tokenizer.decode(tokens[:192], skip_special_tokens=True),
            'rank': raw['rank'], 'score': raw['score'],
            'original_tokens': len(tokens), 'text_tokens': min(len(tokens), 192)}

def sources(ranked):
    raw=[d for h in ranked for d in h[:5]];units={}
    for i,d in enumerate(raw):
        for j,(start,end,text) in enumerate(sentence_units(d['text'])):
            units[f'P{i+1}S{j+1}']=(i,j,start,end,text)
    return raw,units

def render(raw,units,keys):
    tok=shared_tokenizer();chosen=set(keys);docs=[]
    for i,d in enumerate(raw):
        parts=[(k,u) for k,u in units.items() if k in chosen and u[0]==i]
        if not parts:continue
        text=' '.join(u[4] for _,u in parts)
        docs.append(visible(d,tok)|{'text':text,'text_tokens':len(tok.encode(text,add_special_tokens=False)),
                       'source_spans':[{'start':u[2],'end':u[3],'sentence_id':k} for k,u in parts]})
    return docs

def render_documents(documents):
    return ''.join(f"[{d['pid']}] {d['title']}\n{d['text']}\n" for d in documents)

def chat(tokenizer, system, user):
    if 'mistral' in tokenizer.name_or_path.lower():
        messages = [{'role':'user','content':system + '\n\n' + user}]
    else:messages = [{'role':'system','content':system},{'role':'user','content':user}]
    return tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)

def prompt(tokenizer,question,docs):
    return chat(tokenizer,READ_SYSTEM,READ_USER.format(question=question,evidence=render_documents(docs),reasoning='(not supplied)'))

def count(tokenizer,question,docs):
    return len(tokenizer.encode(prompt(tokenizer,question,docs),add_special_tokens=False))

def expand(question, ranked, seed, tokenizer, allowance, arm):
    assert arm in ARMS and allowance in BUDGETS
    raw, units = sources(ranked)
    keys = seed['selection']['selected']
    assert seed['selection']['valid'] and keys
    assert render(raw, units, keys) == seed['documents']
    retained = ' '.join(units[k][4] for k in keys)
    text = question if arm == 'question_only' else retained if arm == 'seed_only' else question + ' ' + retained
    text = ' ' + normalize_question(text) + ' '
    linked = {i for i, d in enumerate(raw)
              if ((len(normalize_question(d['title']).split()) >= 2 or len(normalize_question(d['title'])) >= 4)
                  and ' ' + normalize_question(d['title']) + ' ' in text)}

    def priority(k):
        i, j, *_ = units[k]
        distances = [abs(j - units[s][1]) for s in keys if units[s][0] == i]
        window = (min(distances) if distances else 1000000, i, j)
        if arm == 'window': return window
        if arm == 'random': return (digest(['V26-RANDOM-20261111', question, k]),)
        if arm == 'first_no_link': return (0 if j == 0 else 1, *window)
        if arm == 'no_first_priority': return (0 if i in linked else 1, *window)
        return (0 if i in linked and j == 0 else 1 if i in linked else 2, *window)

    seed_tokens = count(tokenizer, question, seed['documents'])
    cap = seed_tokens + allowance; selected = list(keys)
    for k in sorted((k for k in units if k not in keys), key=priority):
        if count(tokenizer, question, render(raw, units, selected + [k])) <= cap:
            selected.append(k)
    docs = render(raw, units, selected)
    actual = count(tokenizer, question, docs)
    assert actual <= cap and set(keys) <= set(selected)
    assert all((s['start'], s['end']) == tuple(units[s['sentence_id']][2:4]) for d in docs for s in d['source_spans'])
    return dict(documents=docs, prompt=prompt(tokenizer, question, docs), prompt_tokens=actual,
                seed_tokens=seed_tokens, native_cap=cap, allowance=allowance, arm=arm,
                seed_ids=keys, selected_ids=selected, linked_passages=sorted(linked),
                added_segments=len(selected)-len(keys), unspent_tokens=cap-actual)

