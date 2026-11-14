# Prospective reader-panel test

## Scope and immutable inputs

Test the reader-capability association suggested by the three earlier readers. Those readers generated the hypotheses and are excluded from both confirmatory tests. Reuse exactly the 4,500 confirmatory questions: 1,500 each from HotpotQA, 2WikiMultiHopQA, and MuSiQue. Freeze the original 20 retrieval slots, Qwen7 seed, source rendering (`[src_<16 hex>] {title}\n{text}\n`), reader instructions, parser, normalization, aliases, and exact-match (EM) and F1 scorers. No retrieval or selector reruns, new methods, manuscript changes, or supplementary-material changes are permitted.

All new artifacts reside under V30. No evaluation inference precedes this plan's Git commit. New-reader scores remain locked until all planned inference and input/output audits pass. Do not change readers, conditions, metrics, tests, weights, or random seeds in response to outcomes. Record all deviations, failures, and retries. P9 is disabled because the user specified no API reader.

## 3.1 Reader panel

| Slot | Official model | Revision | Parameters | Family / size | TP / max length | System adapter | Stops |
|---|---|---|---:|---|---|---|---|
| P1 | meta-llama/Llama-3.3-70B-Instruct | `6f6073b423013f6a7d4d9f39144961bfbfbc386b` | 70,553,706,496 | Llama / large | 4 / 16,384 | Native system | [128001, 128008, 128009] |
| P2 | google/gemma-2-9b-it | `11c9b309abf73637e4b6f9a3fa1e92e615547819` | 9,241,705,984 | Gemma / small | 1 / 8,192 | Merged into user | [1, 107] |
| P3 | google/gemma-2-27b-it | `aaf20e6b9f4c0fcf043f6fb2a2068419086d77b0` | 27,227,128,320 | Gemma / large | 2 / 8,192 | Merged into user | [1, 107] |
| P4 | mistralai/Mistral-7B-Instruct-v0.3 | `c170c708c41dac9275d15a8fff4eca08d52bab71` | 7,248,023,552 | Mistral / small | 1 / 16,384 | Native system | [2] |
| P5 | mistralai/Mistral-Small-24B-Instruct-2501 | `9527884be6e5616bdd54de542f9ae13384489724` | 23,572,403,200 | Mistral / large | 1 / 16,384 | Native system | [2] |
| P6 | microsoft/phi-4 | `2db69c1c3e91a05d2c64a3185acfbaf36f744e25` | 14,659,507,200 | Phi / small | 1 / 16,384 | Native system | [100257, 100265] |
| P7 | Qwen/Qwen2.5-32B-Instruct | `5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd` | 32,763,876,352 | Qwen / large | 2 / 16,384 | Native system | [151645, 151643] |
| P8 | Qwen/Qwen2.5-72B-Instruct | `495f39366efef23836d0cfae4fbe635880d2be31` | 72,706,203,648 | Qwen / large | 4 / 16,384 | Native system | [151645, 151643] |

The authorized primary/fallback pairs are P1 Llama-3.3-70B-Instruct / Llama-3.1-70B-Instruct; P2 gemma-2-9b-it / gemma-3-12b-it; P3 gemma-2-27b-it / gemma-3-27b-it; P4 Mistral-7B-Instruct-v0.3 / Mistral-Nemo-Instruct-2407; P5 Mistral-Small-24B-Instruct-2501 / Mistral-Small-Instruct-2409; P6 phi-4 / Phi-3-medium-128k-instruct; P7 Qwen2.5-32B-Instruct and P8 Qwen2.5-72B-Instruct have no fallback. Official namespaces and immutable revisions appear above and in `plan.json`.

Large means at least 20 billion parameters. A primary may be replaced only for denied repository access, inability to serve unquantized bfloat16 with vLLM 0.11.2, or a model context limit below the longest native unique-full input plus 96 tokens. Cache absence and busy GPUs are not exclusions. The Gemma pair must use the same generation. Qualification uses tokenizer calculations over all 4,500 inputs and development-only checks of loading, template, stops, and client/server prompt-token agreement. No development response is compared to an answer. At least seven open readers must qualify before commitment; otherwise stop without committing. Quantization is prohibited. Increase tensor parallelism only as needed for fit and record it.

The qualified panel and configuration are fixed by this commit. Execute new readers in increasing slot order, then the existing Qwen14 closed-book addition. Do not add P9 later. An API reader would require an explicitly authorized dated snapshot and disabled reasoning, neither of which is applicable here. Changes outside these rules require stopping and reporting.

## 3.2 Conditions

Each new open reader receives all 4,500 questions in 12 conditions (54,000 logical records): closed_book; seed; unique_full; and window, linked, and score_priority at allowances 128, 256, and 512. The per-question order is the three unbudgeted conditions followed by ascending allowance, with window, linked, score_priority in that order. Unique-full retains only the first occurrence of each exact corpus passage ID. Closed-book reuses the confirmatory implementation, including answering the two upstream-failure questions. Context-dependent conditions retain those two questions as failures in the denominator. The three invalid-seed fallback questions follow the archived implementation.

Add only 4,500 closed-book records for the existing Qwen14. No other condition for an existing reader is regenerated. P9, if it had been authorized, would receive only the three unbudgeted conditions; it is absent from this plan.

## 3.3 Rendering, caps, decoding, and interruption recovery

Use the native chat template with system and user messages and `add_generation_prompt=True`. Only when the template rejects the system role, concatenate system instructions, one blank line, and user content as a single user turn. Record this adapter per reader. Keep the reader instructions and evidence text unchanged. For new readers, this capability-based adapter implements the task's rule rather than the archived helper's model-name heuristic; the archived helper itself is unchanged.

The complete prompt cap is `B_r(q;b)=T_r(q,S0)+b`, including titles, identifiers, instructions, and template tokens. Reuse the archived expansion operators and passage scores. Retain every seed segment, scan candidates in their fixed priority order, skip nonfitting candidates and continue, render in source order, and do not trim text. The internal archived name `rerank` is reported as `score_priority`.

Serve vLLM 0.11.2 with unquantized bfloat16, temperature 0, request seed 42, at most 96 new tokens, and server-side `add_special_tokens=false`. Stop IDs are the union of generation-config EOS IDs, tokenizer EOS, and special termination tokens in a completed native assistant turn. Record the exact IDs and tokenizer hashes. Default serving settings are maximum model length 16,384, TP=1, eager mode, at most eight sequences, 4,096 batched tokens, and model initialization seed 0. Only TP, KV cache allocation, and maximum model length for models not supporting 16,384 may differ. Complete replica configurations are in `plan.json`.

Use the 4 NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition devices of local host nlp (server 130) as the serving pool. Use the qualified tensor-parallel configuration for each reader and partition the four devices into disjoint replicas. This uses the full selected pool during evaluation while retaining the qualified hardware configuration and slot order. Qualification uses one replica and development questions three and four from the archived smoke set, preserving the earlier host's responses to questions one and two. P5 uses previously unused questions five and six after a pre-plan client/server tokenizer mismatch; its failed audit response is retained and never regenerated. Previously qualified readers undergo offline revalidation of their saved prompt hashes and token counts. The user requested migration from host 15 after its operating system was reinstalled; no evaluation inference preceded the migration. Do not infer different new readers concurrently. Each reader/question is assigned by SHA-256 of its UTF-8 episode ID modulo that reader's replica count; all conditions remain on that logical replica. Exact prompt reuse on the same replica is allowed.

Retain the archived local-server `gpu_memory_utilization=0.40` setting from V28/V29. KV cache capacity is fixed explicitly in bytes for each reader; vLLM 0.11.2 uses the utilization fraction only for its initial free-memory check when explicit KV bytes are supplied. The separate launch check requires enough free memory for the unquantized weights and working-memory allowance before starting a replica.

Persist each raw response before parsing; persist each attempt before sending; write immutable condition records with SHA-256 checksums and file/directory fsync on shared Ceph. Initial request plus at most three retries means at most four attempts across restarts. Retry only requests without a saved response, and pause for service recovery between unsuccessful attempts. Preserve empty, incorrect, length-stopped, and audit-failing saved responses. Empty responses and final failures score zero. An in-flight response that was not durably saved may need a retry. A restart preserves the logical replica and exact configuration but creates a recorded physical boot/process epoch. Conditions spanning epochs are reported; completed responses are never regenerated to obtain a single epoch. This interruption policy does not change scientific conditions or retry limits.

## 3.4 Estimands

All aggregate scores are macro EM percentages with equal one-third weights for the three datasets. For reader r: `C_r` is closed-book EM; `F_r` is unique-full EM minus seed EM; `X_r` is the mean EM of the nine expansion conditions minus seed EM. Obtain 95% percentile intervals for F, X, and their component contrasts from 10,000 dataset-stratified paired question bootstrap samples, seed 20261112. Preserve every reader and condition together within a sampled question. Use common bootstrap draws for related contrasts and between-reader comparisons.

For descriptive existing-reader results, use context-control-follow-up predictions (V28) for Llama8/Qwen7 F and X and reader/rendering predictions (V29) for Qwen14 F and X. Use confirmatory (V27) closed-book predictions for Llama8/Qwen7 C and the V30 closed-book addition for Qwen14 C. Mark these mixed executions in every relevant table.

## 3.5 Confirmatory tests

H1 is the one-sided Spearman association `rho(C,F)>0` across all qualified new readers (including P9 only if present in the plan). H2 is `rho(C,X)>0` across new open readers. Exclude Llama8, Qwen7, and Qwen14 from both tests.

Use average ranks for ties and a reader-label permutation test. For n<=9 enumerate all n! permutations and compute p as the fraction whose correlation is at least the observed correlation, with tolerance 1e-12. For n>9 use 200,000 Monte Carlo permutations, seed 20261112. The fixed significance level is 0.05. Interpret H2 as confirmatory only if H1 is significant; otherwise report H2 descriptively. A constant rank vector gives an undefined correlation, reported as null with p=1 and no rejection; never remove a reader to avoid this case.

## 3.6 Decision

A is true exactly when the H1 one-sided exact p<=0.05. B is true exactly when at least one non-Qwen large open reader in slots P1, P3, or P5 has F's 95% interval lower bound strictly above zero. If none of these slots is present, B is false. `ROUTE=Q1` if both A and B are true; otherwise `ROUTE=APPLIED_INTELLIGENCE`. No sensitivity result changes this rule. `DECISION.md` contains only the values of A and B, ROUTE, and the plan commit hash, without recommendations.

## 3.7 Prespecified descriptive sensitivities

1. Within each dataset sort UTF-8 episode IDs by their SHA-256 digest; first 750 form A and remaining 750 form B. Correlate C from A with F/X from B, then swap halves.
2. Replace capability by unique-full EM from A in the split-half analysis, and repeat with the halves swapped.
3. Replace capability by log10(parameter count), open readers only.
4. Include the three existing readers in the associations, marking their mixed executions.
5. Leave out one model family at a time.
6. Report Kendall tau.
7. Repeat C, F, X, and their associations with F1.
8. Restrict HotpotQA to its 231 hard sample questions and retain equal dataset weights.
9. Report paired-bootstrap differences in F and X for adjacent family pairs: Llama8/70; small/large Gemma; small/large Mistral; Qwen7/14/32/72. Mark comparisons involving existing readers as crossing executions.
10. Report rule-specific and allowance-specific expansion-minus-seed contrasts and each reader's linked-minus-window contrast.
11. Report intervals for rho from the paired question bootstrap, with any undefined bootstrap correlations counted and disclosed.

All sensitivities are descriptive and do not enter the decision. Do not foreground favorable sensitivities if the confirmatory result is unfavorable.

## Stages, gates, outputs, and stopping

Commit `PLAN.md` and `plan.json` before evaluation inference; push only a separate `reader-panel` branch if authorized repository access permits. Preserve the public default branch and the manuscript's pinned commit. Put the plan commit hash and time in every later manifest.

Stage 1 regenerates and matches all 45,000 archived Qwen7 seed/expansion prompt hashes and rescores archived Qwen14 predictions to reproduce Table D1 EM and F1. Stop on any mismatch. Then build native inputs and audit caps, seed retention, intact spans, source order, P7/P8 equality to archived Qwen7 seed/expansion/unique-full prompt hashes and lengths, failure/fallback handling, and input+96 within maximum model length. Record mean lengths, added segments, and allowance use.

Stage 2 executes the fixed slot order and records GPU types/counts, TP, software version, replica assignments, responses, file hashes, empty/length finishes, reuse, and failures. Stop on any count or prompt-token mismatch, or when final no-response failures exceed 1% of that reader's planned logical condition records after retries; the two known upstream failures are reported separately. A transport outage pauses work without changing the panel or resetting retries.

Only after every planned reader and both audits pass may Stage 3 unlock scoring. Produce all question-level scores, `results/reader_overview.csv`, `results/tests.json`, all eleven sensitivities, and a two-panel `results/fig_capability.pdf` plotting C against F and X with intervals, family markers, and distinct existing-reader markers.

Stage 4 writes `REPORT.md` and `DECISION.md` and stops. The report includes panel/revisions, serving settings, audits, overview, tests, sensitivities, deviations, failures, and retries. State that these reused questions support a prospective test on new readers, not independent replication on new questions, and that the reader panel is not randomly sampled and same-family readers are dependent. Do not proceed to selectors, new methods, or manuscript revision.

Stop and report if fewer than seven readers qualify, an out-of-protocol panel change is needed, replay or input/output auditing fails, final failures exceed 1%, or the task genuinely conflicts with repository practice. Record interruption-related pauses separately from scientific stopping conditions.

Tokenizer construction and all scientific stages use the serving environment: Transformers 4.57.6 and tokenizers 0.22.2. A pre-plan development check exposed different tokenization under the former coordinator's Transformers 5.8.1. Its diagnostic evidence is retained. The 4,500-question tokenizer length audits were recomputed before commitment, without inference or scoring.
