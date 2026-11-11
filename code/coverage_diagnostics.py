"""Native-input diagnostic definitions; obtain benchmark annotations separately.

coverage(documents, gold, answers) expects gold["text"] title/text pairs and
sentence-level gold["facts"] pairs (empty for MuSiQue). parts requires TOK
mapping reader names to pinned tokenizers. Corpus/version mismatch limits
lexical coverage; it is not semantic support recall.
"""
from collections import defaultdict
import numpy as np
from native_completion import normalize_question, chat, READ_SYSTEM, READ_USER
TOK={}

def contains(text,phrase):return bool(phrase) and ' '+phrase+' ' in ' '+text+' '

def coverage(docs,gold,answers):
    by_title=defaultdict(list)
    for d in docs:by_title[normalize_question(d['title'])].append(normalize_question(d['text']))
    titles={normalize_question(t) for t,_ in gold['text']}
    observed_titles=set(by_title)
    assert titles
    word_recall=[]
    for title,text in gold['text']:
        expected=set(normalize_question(text or '').split())
        observed=set(' '.join(by_title[normalize_question(title)]).split())
        if expected:word_recall.append(len(expected&observed)/len(expected))
    facts=gold['facts']
    present=[s is not None and any(contains(t,normalize_question(s)) for t in by_title[normalize_question(title)]) for title,s in facts]
    boolean=all(normalize_question(a) in ['yes','no'] for a in answers)
    return dict(title_recall=len(titles&observed_titles)/len(titles),all_titles=int(titles<=observed_titles),
        support_word_type_recall=float(np.mean(word_recall)),
        fact_recall=float(np.mean(present)) if facts else None,facts_present=sum(present),facts_total=len(facts),unresolved_facts=sum(s is None for _,s in facts),fact_mask=present,
        answer_body=None if boolean else int(any(contains(t,normalize_question(a)) for values in by_title.values() for t in values for a in answers)),boolean_answer=boolean)

def parts(question,docs,reader):
    tok=TOK[reader]
    def count(kind):
        headers={'body':lambda d:'','empty':lambda d:'[] \n','id':lambda d:f"[{d['pid']}] \n",'title':lambda d:f"[] {d['title']}\n",'full':lambda d:f"[{d['pid']}] {d['title']}\n"}
        evidence=''.join(headers[kind](d)+d['text']+'\n' for d in docs)
        text=chat(tok,READ_SYSTEM,READ_USER.format(question=question,evidence=evidence,reasoning='(not supplied)'))
        return len(tok.encode(text,add_special_tokens=False))
    c={kind:count(kind) for kind in ['body','empty','id','title','full']}
    result=dict(total=c['full'],body=c['body'],structure=c['empty']-c['body'],
        identifier=.5*((c['id']-c['empty'])+(c['full']-c['title'])),
        title=.5*((c['title']-c['empty'])+(c['full']-c['id'])))
    assert abs(result['body']+result['structure']+result['identifier']+result['title']-result['total'])<1e-9
    return result
