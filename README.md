# Title-Linked Source Completion under Native Token Caps

Research artifacts for Yeo-Chan Yoon, Artificial Intelligence Department, Jeju National University. Correspondence: ycyoon@jejunu.ac.kr.

This repository evaluates a deterministic, seed-preserving context expansion rule. It is a research manuscript artifact, not a claim of an accepted publication or general state-of-the-art performance.

## Status and interpretation

The development study evaluates 480 questions, two readers, three allowances and seven priority rules, with seed, closed-book, full-context and LLMLingua-2 baselines. Its linked-minus-window average is +0.8333 EM percentage points (descriptive 95% interval −0.9375 to +2.6389). Simpler link ablations are competitive; the necessity of every priority tier is not established.

The separate confirmation reserves 1,500 questions each from HotpotQA train, 2Wiki dev and MuSiQue answerable train. These are internal held-out questions, not official hidden-test results. One primary contrast was fixed before outcomes: the per-question EM difference between linked and window, averaged over both readers and all three allowances, with equal dataset weights. All other contrasts are descriptive. The primary EM difference is **+0.6333 percentage points** (95% paired bootstrap CI **+0.1593 to +1.0926**; two-sided randomization **p = 0.0088099**). Dataset-average differences are +0.3333 HotpotQA, +0.1778 2Wiki and +1.3889 MuSiQue.

The average differences from seed, full context and LLMLingua-2 are **−0.1074**, **+1.8259** and **+9.8000** EM points, respectively. The seed interval is −0.6852 to +0.4815: expanding the seed has no established average benefit. All three Llama allowance estimates fall below its seed score. The positive primary result supports a narrow advantage over proximity expansion, not a general recommendation to add context. Other comparisons remain descriptive.

## What is included

- `code/native_completion.py`: the actual scientific functions, extracted unchanged from the evaluated implementation, with portable model loading. All 20,160 development priority prompts and selected-ID sequences match the original implementation.
- `code/build_inputs.py`: reconstruction from frozen corpus IDs and seed selections. It verifies source text/title hashes before creating prompts.
- `code/compressor.py`: official LLMLingua-2 native-cap calibration, including exact per-question classifier memoization.
- `code/reader.py`: reader calls to a user-supplied local vLLM endpoint; failures remain failures. It never replaces successful wrong answers.
- `code/metrics.py` and `musique_metrics.py`: the frozen answer parser and benchmark scoring conventions.
- `code/recompute.py`: full macro scores, paired bootstrap intervals, corrected/worsened counts and the single confirmation randomization test, directly from the supplied question-level predictions/scores.
- `data/*_questions.jsonl.gz`: benchmark IDs, local grouping IDs and source splits; no original benchmark passages.
- `data/*_contexts.jsonl.gz`: ordered corpus slots, exact title/text hashes, ranks/scores and seed IDs. Repeated slots are intentional.
- `data/*_input_metadata.jsonl.gz`: expected prompt hashes, native caps, selected segment IDs and compressor calibration traces, without corpus text.
- `data/*_predictions.jsonl.gz`: every condition's generated answer, score, prompt/output size and failure flag. Development has 26,880 rows; confirmation has 117,000 rows.
- `protocols/`: pre-outcome plan, model revisions, sampling rules, provenance and validation results.

Original benchmark text, Wikipedia corpus, model weights, private endpoints, credentials and inference caches are not redistributed. The portable workflow reproduces selection, prompts, reader replay and statistics **conditional on the supplied frozen retrieval slots and seed selections**. It does not rebuild the 21-million-passage dense/BM25 indexes or reproduce the adaptive upstream search from scratch. The manuscript supplies the controller and selector prompts and all material settings; frozen slots avoid silently changing that upstream realization.

## Recompute the reported statistics

Use Python 3.11 with NumPy and pandas. These commands require no model, GPU or benchmark download:

```bash
python -m pip install -r requirements-statistics.txt
OPENBLAS_NUM_THREADS=1 python code/recompute.py --study dev --out dev-recomputed.json
OPENBLAS_NUM_THREADS=1 python code/recompute.py --study test --out test-recomputed.json
```

`episode_id` is the sorting/grouping identifier: preserve it when reproducing the fixed Monte Carlo stream. Each question is resampled as one unit with its six paired reader/allowance results. Confidence intervals are not six independent replications. The randomization test assumes paired-label exchangeability. It is not an assumption-free test of arbitrary equal means.

## Resolve IDs and independently check answer scoring

`code/prepare_questions.py` accepts the exact upstream JSON/JSONL or HotpotQA parquet files and verifies every normalized question hash. Parquet loading additionally requires `pyarrow`. For the confirmation set:

```bash
python code/prepare_questions.py --ids data/test_questions.jsonl.gz \
  --source hotpot=/path/to/train-00000-of-00002.parquet \
  --source hotpot=/path/to/train-00001-of-00002.parquet \
  --source 2wiki=/path/to/flashrag-2wiki-dev.jsonl \
  --source musique=/path/to/musique_ans_v1.0_train.jsonl \
  --questions questions.jsonl --labels labels.jsonl
python code/verify_scores.py --predictions data/test_predictions.jsonl.gz --labels labels.jsonl
```

For development use HotpotQA validation and the same FlashRAG 2Wiki dev distribution; MuSiQue is absent. Benchmark text and labels are generated locally from separately obtained source data.

## Reconstruct prompts and replay a reader

Obtain the datasets and pinned checkpoints separately, respecting their upstream access terms. Construct a JSONL question file with `dataset`, `source_id`, and `question`, matching the supplied IDs. Obtain and decompress the DPR `psgs_w100.tsv` file. Input reconstruction scans it once for the requested corpus IDs; no retrieval index is needed.

```bash
python -m pip install -r requirements-inference.txt
python code/build_inputs.py --contexts data/test_contexts.jsonl.gz \
  --questions questions.jsonl --corpus /path/to/psgs_w100.tsv \
  --reader qwen7 --arm linked --allowance 256 --out linked-qwen-256.jsonl
python code/reader.py --inputs linked-qwen-256.jsonl \
  --endpoint http://localhost:8000/v1 --model your-served-model --out answers.jsonl
```

Repeat for `window`, both readers and allowances 128/256/512. Development additionally uses `first_no_link`, `no_first_priority`, `question_only`, `seed_only` and `random`. `native_completion.render`, `visible`, `prompt`, and `compressor.compress` expose the seed, excerpt, full-block and learned-compressor input construction. Empty evidence defines closed book. For LLMLingua-2, pass both pinned tokenizers, the frozen ranked slots and seed to `compressor.compress`; it returns all six reader/allowance inputs.

Reader settings: vLLM 0.11.2, bfloat16, tensor parallelism 1, eager execution, initialization seed 0, maximum model length 16,384, maximum 8 sequences, 4,096 batched tokens, 2 GiB KV cache. Requests use temperature 0, seed 42, maximum 96 tokens, native stop IDs and `add_special_tokens=False`. Put every condition for a reader/question on the same replica. Zero-temperature decoding can still vary with hardware or scheduling; the stored predictions are the recorded realization used in the paper.

## Data and model sources

- HotpotQA: https://hotpotqa.github.io/ ; HF snapshot `1908d6afbbead072334abe2965f91bd2709910ab` of `hotpotqa/hotpot_qa`.
- 2WikiMultiHopQA: https://github.com/Alab-NII/2wikimultihop ; evaluated IDs and aliases use [FlashRAG dev](https://huggingface.co/datasets/RUC-NLPIR/FlashRAG_datasets/blob/bcafb8dd07d453be3cbeeeb3f78be1841bddf92c/2wikimultihopqa/dev.jsonl), revision `bcafb8dd07d453be3cbeeeb3f78be1841bddf92c`; these IDs differ from the original distribution.
- MuSiQue: https://github.com/StonyBrookNLP/musique ; answerable v1.0, mirrored snapshot `c8f4f8c9465fb69d31a8eae894c3fd509c4ca321` of `dgslibisey/MuSiQue`.
- DPR Wikipedia: https://huggingface.co/datasets/facebook/wiki_dpr ; 20 December 2018, 21,015,324 nonoverlapping 100-word blocks. Exact selected-block hashes are supplied.
- Reader and compressor checkpoint identities: `protocols/models.json`.
- Official LLMLingua-2 implementation: https://github.com/microsoft/LLMLingua (package 0.2.2).

The splitter is a punctuation regex, not a linguistic sentence splitter. Blocks may begin or end mid-sentence, and the regex omits some text near internal punctuation. The evaluated implementation preserves these limitations; changing the splitter creates a different method. No selected source segment is character-trimmed in the native-cap study.

## Scope of reproduction and reuse

The release retains unfavorable and failed outputs, all fixed budgets, and historical diagnostic evidence. It does not imply pretraining decontamination, a necessary role for every priority tier, or total compute savings: the controller and language-model seed selector have substantial costs. Third-party benchmark, model and evaluator terms remain those of their original providers. See `THIRD_PARTY.md` for evaluator attribution. No new license over third-party content is asserted.
