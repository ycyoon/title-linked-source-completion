import collections
import re
import string

def normalize_answer(value):
    text = str(value).lower()
    text = "".join(c for c in text if c not in string.punctuation)
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())

def token_f1(prediction, target, hotpot=False):
    p, g = normalize_answer(prediction), normalize_answer(target)
    if hotpot and (p in {"yes", "no", "noanswer"} or g in {"yes", "no", "noanswer"}) and p != g:
        return 0.0
    pp, gg = p.split(), g.split()
    overlap = sum((collections.Counter(pp) & collections.Counter(gg)).values())
    if not overlap:
        return 0.0
    precision, recall = overlap / len(pp), overlap / len(gg)
    return 2 * precision * recall / (precision + recall)

def extract_answer(raw, lenient=False):
    """One gold-independent rule for every answer route, fixed before inference."""
    raw = (raw or '').strip()
    complete = re.findall(r'<answer>(.*?)</answer>',raw,flags=re.S)
    if complete:answer = complete[-1].strip()
    elif '<answer>' in raw:answer = ''  # Unclosed structured answer is malformed.
    elif raw.endswith('</answer>'):answer = raw[:-len('</answer>')].strip()
    else:answer = raw
    if lenient:
        box = re.findall(r'\\boxed\{([^{}]+)\}',answer)
        if box:answer = box[-1]
        else:
            lines = [line.strip() for line in answer.splitlines() if line.strip()]
            answer = lines[-1] if lines else ''
            answer = re.sub(r'^(?:the\s+)?(?:final\s+)?answer\s*(?:is\s*:?|:)\s*','',answer,flags=re.I)
            answer = answer.strip('"\u201c\u201d`* ')
    return answer

def score(raw, gold_answers, dataset, failed=False):
    from musique_metrics import compute_exact, compute_f1
    answer = extract_answer(raw)
    if failed or not answer:
        return {'em': 0.0, 'f1': 0.0}
    if dataset == 'musique':
        return {'em': float(max(compute_exact(g, answer) for g in gold_answers)),
                'f1': float(max(compute_f1(g, answer) for g in gold_answers))}
    return {'em': float(any(normalize_answer(answer) == normalize_answer(g) for g in gold_answers)),
            'f1': max(token_f1(answer, g, hotpot=dataset == 'hotpot') for g in gold_answers)}
