# Evaluating Context Expansion after Evidence Extraction in Multi-Hop Question Answering

Research artifacts for Yeo-Chan Yoon, Artificial Intelligence Department, Jeju National University. Correspondence: ycyoon@jejunu.ac.kr.

This repository contains an empirical evaluation of evidence retention, context expansion and expansion priority. It is a research manuscript artifact, not a claim of an accepted publication or general state-of-the-art performance.

## Status and interpretation

The development study evaluates 480 questions, two readers, three allowances and seven priority rules, with seed, closed-book, full-context and LLMLingua-2 baselines. Its linked-minus-window average is +0.8333 EM percentage points (descriptive 95% interval −0.9375 to +2.6389). Simpler link ablations are competitive; the necessity of every priority tier is not established.

The separate confirmation reserves 1,500 questions each from HotpotQA train, 2Wiki dev and MuSiQue answerable train. These are internal held-out questions, not official hidden-test results. One primary contrast was fixed before outcomes: the per-question EM difference between linked and window, averaged over both readers and all three allowances, with equal dataset weights. All other contrasts are descriptive. The primary EM difference is **+0.6333 percentage points** (95% paired bootstrap CI **+0.1593 to +1.0926**; two-sided randomization **p = 0.0088099**). Dataset-average differences are +0.3333 HotpotQA, +0.1778 2Wiki and +1.3889 MuSiQue.

Linked minus seed is **−0.1074 EM points** (95% interval −0.6852 to +0.4815); window minus seed is **−0.7407** (−1.3222 to −0.1593). The three allowance-specific linked-minus-window estimates are −0.40, +0.80 and +1.50 points. These decompositions are descriptive. Retaining the seed remains essential as a comparator.

The selected HotpotQA sample contains **329 easy, 940 medium and 231 hard** questions. Restricting HotpotQA to hard questions, while retaining the other two datasets and equal dataset weights, gives **+0.1134** points (−0.7250 to +0.9742). The mixed-difficulty primary result cannot be generalized to the official hard-only population.

A post hoc follow-up evaluates all 4,500 questions again with deduplicated full context, two targeted ablations and an archived relevance-score priority, alongside repeated original anchors: **162,000 records**. These comparisons reuse the test questions and are not independent confirmation. All differences below average both readers, all allowances where relevant and equal dataset weights.

| Descriptive EM contrast | Difference (points) | 95% paired interval |
|---|---:|---:|
| Linked − window | +0.5778 | [+0.1037, +1.0407] |
| Linked − seed | −0.1148 | [−0.6963, +0.4852] |
| Seed − unique full blocks | +1.5889 | [+0.6556, +2.5333] |
| Unique − repeated full blocks | +0.2889 | [−0.2556, +0.8333] |
| Linked − no first priority | +0.3630 | [−0.0148, +0.7370] |
| Linked − seed-only link | −0.2222 | [−0.5407, +0.0926] |
| Linked − relevance-score priority | −0.7111 | [−1.2482, −0.1778] |
| Relevance-score priority − seed | +0.5963 | [−0.0593, +1.2519] |

The seed-versus-unique-full-context contrast differs by reader: Qwen −0.4444 [−1.5778, +0.6889], Llama +3.6222 [+2.4222, +4.8444]. Thus neither a universal advantage for extracting nor general title-link superiority is established. Native input diagnostics also distinguish title coverage from sentence/word coverage, exact repeated additions, and identifier versus title token costs. The 64–71% identifier share of header increments at allowance 256 applies to the evaluated long-hash rendering.

The 72,000 repeated anchor conditions differ from the original execution in 1,531 answer strings, 220 EM scores and 540 F1 scores. Follow-up comparisons use contemporaneous outputs. The original primary result and original released predictions are preserved.

## Larger reader and compact-rendering intervention

A second descriptive experiment reuses the same 4,500 questions and adds **229,500 condition records**. Qwen2.5-14B-Instruct evaluates seed, deduplicated full context and all three expansion priorities at all three allowances (49,500 records). Qwen7 and Llama8 compare original and compact renderings contemporaneously (180,000 records). This is post hoc; it is not a new independent confirmatory test.

All 45,000 common Qwen7/Qwen14 seed and expansion inputs have identical prompt hashes and native lengths, despite being reconstructed with their respective pinned tokenizers. The 14B checkpoint was selected before these predictions after a planned 72B deployment could not obtain sufficient shared GPU memory. This is a twice-size within-family check, not evidence for behavior at 70B scale. The original plan and resource amendment are retained.

The compact rendering uses short stable `P{first_original_slot}` identifiers, merges sections with the same exact corpus passage ID, and renders each `(corpus_id,start,end)` segment once. All distinct seed segments survive; priority is still evaluated over the original slots, with no tier removal. Both renderings share the **same absolute original-seed-plus-allowance cap**. Header savings can admit additional segments. Each rendering has its own seed control. Identifiers, repetitions and merged sections form one joint intervention, not separately identified effects.

In `rendering_effects.csv`, allowance 0 denotes averaging allowances 128/256/512; in input metadata and level-score tables, allowance 0 identifies an unexpanded baseline. The `expansion_interaction` rows are paired rendering changes after subtracting the corresponding seed change. The `reader_interaction` rows compare Qwen14-minus-Qwen7 expansion benefits on identical input text.

All entries below are EM percentage-point differences with descriptive, unadjusted 95% paired intervals. Equal dataset weights and all three allowances are used. “Paired change” subtracts each rendering's own seed contrast, not two independently estimated intervals.

| Policy         | Qwen14 − seed              | Compact − compact seed, original readers   | Paired change in expansion benefit   |
|:---------------|:---------------------------|:-------------------------------------------|:-------------------------------------|
| Window         | +1.3630 [+0.6889, +2.0519] | -1.1926 [-1.8148, -0.5704]                 | -0.5111 [-1.0185, -0.0111]           |
| Linked         | +1.4889 [+0.8148, +2.1704] | -0.2778 [-0.9148, +0.3704]                 | -0.2111 [-0.7630, +0.3407]           |
| Score priority | +2.1259 [+1.3852, +2.8667] | +0.0111 [-0.7000, +0.7333]                 | -0.5963 [-1.1333, -0.0593]           |

Qwen14 seed minus unique full context is -3.0889 [-4.1111, -2.0667]. Compact minus original seed, averaged over the two original readers, is +0.3000 [-0.1222, +0.7222]. Every reader, allowance, dataset and F1 contrast, including unfavorable and imprecise cells, is provided in `data/rendering_effects.csv`. These descriptive intervals do not establish equivalence or multiplicity-controlled discovery.

Input-only validation confirms every distinct seed segment is preserved and compact inputs have no exact repeated segments. At allowance 256, linked expansion admits about 12.0–12.1 distinct additions instead of 6.6–7.1. Original successful responses are retained across an operational queue-depth increase and identity-hash memoization; no answer was selected for replacement. The immutable scientific inputs, decoding, assigned replica and original primary outcome remain unchanged.

Portable reconstruction matches all **139,500 added-condition prompts**, lengths and selections. Independent public scoring verifies all **229,500 predictions** against separately resolved labels, and the independent dataframe implementation reproduces all aggregate scores and contrasts. Complete verification reports and model settings are in `protocols/rendering_*`.

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
- `data/*_predictions.jsonl.gz`: every condition's generated answer, score, prompt/output size and failure flag. Development has 26,880 rows; confirmation has 117,000 rows; the first post hoc follow-up has 162,000 rows; the larger-reader/rendering experiment has 229,500 rows.
- `data/confirmatory_question_scores.csv`: 4,500 question-level rows with original EM/F1 scores, benchmark IDs, splits and HotpotQA difficulty.
- `code/followup_inputs.py`: exact-passage deduplication and archived-score expansion, plus the unchanged targeted ablations. All 90,000 added-condition prompts, token lengths and selected IDs match the original follow-up implementation.
- `code/rendering_inputs.py`: the joint compact intervention and pinned Qwen14 tokenizer; `code/recompute_rendering.py` independently recomputes its complete paired statistics.
- `code/coverage_diagnostics.py`: lexical coverage and exact full-prompt header decomposition functions; benchmark annotations must be obtained separately. Native diagnostic definitions and all per-question/aggregate outputs are included.
- `protocols/`: pre-outcome plan, model revisions, sampling rules, provenance and validation results. The follow-up protocol is explicitly post hoc; it does not replace the confirmatory plan.

Original benchmark text, Wikipedia corpus, model weights, private endpoints, credentials and inference caches are not redistributed. The portable workflow reproduces selection, prompts, reader replay and statistics **conditional on the supplied frozen retrieval slots and seed selections**. It does not rebuild the 21-million-passage dense/BM25 indexes or reproduce the adaptive upstream search from scratch. The manuscript supplies the controller and selector prompts and all material settings; frozen slots avoid silently changing that upstream realization.

## Recompute the reported statistics

Use Python 3.11 with NumPy and pandas. These commands require no model, GPU or benchmark download:

```bash
python -m pip install -r requirements-statistics.txt
OPENBLAS_NUM_THREADS=1 python code/recompute.py --study dev --out dev-recomputed.json
OPENBLAS_NUM_THREADS=1 python code/recompute.py --study test --out test-recomputed.json
OPENBLAS_NUM_THREADS=1 python code/recompute_followup.py --out followup-recomputed.json
OPENBLAS_NUM_THREADS=1 python code/recompute_decomposition.py --out decompositions.json
OPENBLAS_NUM_THREADS=1 python code/recompute_score_vs_seed.py --out score-vs-seed.csv
OPENBLAS_NUM_THREADS=1 python code/recompute_rendering.py --out rendering-recomputed.json
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
python code/verify_scores.py --predictions data/followup_predictions.jsonl.gz --labels labels.jsonl
python code/verify_scores.py --predictions data/rendering_predictions.jsonl.gz --labels labels.jsonl
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

Repeat for `window`, both readers and allowances 128/256/512. The same command supports `seed`, `raw20` and `unique20` with allowance 0, and `rerank`, `no_first_priority` and `seed_only` with each native allowance. `unique20` retains the first occurrence of each exact corpus passage ID in source order; it does not merge same-title or overlapping passages. `rerank` sorts by the archived passage score against the retrieval subquery that generated the slot, then seed proximity, slot and segment. These scores are not newly computed sentence scores or calibrated across subqueries. Development additionally uses `first_no_link`, `no_first_priority`, `question_only`, `seed_only` and `random`. `native_completion.render`, `visible`, `prompt`, and `compressor.compress` expose the seed, excerpt, full-block and learned-compressor input construction. Empty evidence defines closed book. For LLMLingua-2, pass both pinned tokenizers, the frozen ranked slots and seed to `compressor.compress`; it returns all six reader/allowance inputs.

For the added experiment, `--reader qwen14` supports the same original policies and `unique20`; the original readers additionally use `compact_seed` (allowance 0), `compact_window`, `compact_linked` and `compact_rerank`. The compact budget remains based on the original seed.

Reader settings: vLLM 0.11.2, bfloat16, tensor parallelism 1, eager execution, initialization seed 0, maximum model length 16,384, maximum 8 sequences, 4,096 batched tokens, 2 GiB KV cache for Qwen7/Llama8 and 4 GiB for Qwen14. The additional experiment increased client queue depth from 8 to 32 questions per replica while keeping the server sequence limit at 8; identical frozen-identity hashes are memoized. Stored successful answers are retained across operational resumes. Requests use temperature 0, seed 42, maximum 96 tokens, native stop IDs and `add_special_tokens=False`. Put every condition for a reader/question on the same replica. Zero-temperature decoding can still vary with hardware or scheduling; the stored predictions are the recorded realization used in the paper.

## Data and model sources

- HotpotQA: https://hotpotqa.github.io/ ; HF snapshot `1908d6afbbead072334abe2965f91bd2709910ab` of `hotpotqa/hotpot_qa`.
- 2WikiMultiHopQA: https://github.com/Alab-NII/2wikimultihop ; evaluated IDs and aliases use [FlashRAG dev](https://huggingface.co/datasets/RUC-NLPIR/FlashRAG_datasets/blob/bcafb8dd07d453be3cbeeeb3f78be1841bddf92c/2wikimultihopqa/dev.jsonl), revision `bcafb8dd07d453be3cbeeeb3f78be1841bddf92c`; these IDs differ from the original distribution.
- MuSiQue: https://github.com/StonyBrookNLP/musique ; answerable v1.0, mirrored snapshot `c8f4f8c9465fb69d31a8eae894c3fd509c4ca321` of `dgslibisey/MuSiQue`.
- DPR Wikipedia: https://huggingface.co/datasets/facebook/wiki_dpr ; 20 December 2018, 21,015,324 nonoverlapping 100-word blocks. Exact selected-block hashes are supplied.
- Reader and compressor checkpoint identities: `protocols/models.json` and `protocols/rendering_models.json`.
- Official LLMLingua-2 implementation: https://github.com/microsoft/LLMLingua (package 0.2.2).

The splitter is a punctuation regex, not a linguistic sentence splitter. Blocks may begin or end mid-sentence, and the regex omits some text near internal punctuation. The evaluated implementation preserves these limitations; changing the splitter creates a different method. No selected source segment is character-trimmed in the native-cap study.

## Scope of reproduction and reuse

The release retains unfavorable and failed outputs, all fixed budgets, and preliminary diagnostic evidence. It does not imply pretraining decontamination, a necessary role for every priority tier, or total compute savings: the controller and language-model seed selector have substantial costs. Third-party benchmark, model and evaluator terms remain those of their original providers. See `THIRD_PARTY.md` for evaluator attribution. No new license over third-party content is asserted.
