---
title: "Baseline and priority-ablation follow-up"
date: "11 November 2026"
---

# Scope and execution

All 480 development questions (240 HotpotQA and 240 2Wiki), two readers, and 28 conditions per reader/question were completed. These questions were already used in development. The matrix was fixed before the new reader outcomes; this is exploratory follow-up, not independent confirmation. Every comparison for a reader/question used the same recorded replica. Greedy decoding used temperature 0, seed 42 and at most 96 output tokens. Repeated prompts were cached within the recorded reader/replica profile. All valid empty or length-stopped answers remain in the scores.

The audit reports 19,778 unique requests, 7,102 cached records, 0 failed records, 1 length-stopped records and 0 empty answers. All 26,880 prompts satisfy the context limit; all budgeted prompts satisfy the native reader cap. The priority methods retain every seed segment and add no partial source segments.

# Fresh seed and uncompressed baselines

| reader   | arm                   |    em |    f1 |   prompt_tokens |   output_tokens |
|:---------|:----------------------|------:|------:|----------------:|----------------:|
| llama8   | Closed book           | 21.25 | 29.51 |          130.32 |            6.71 |
| llama8   | 20 visible excerpts   | 31.25 | 41.95 |         3377.63 |            6.15 |
| llama8   | 20 full source blocks | 31.25 | 41.62 |         3387.79 |            6.10 |
| llama8   | Seed                  | 36.04 | 46.36 |          294.93 |            5.55 |
| qwen7    | Closed book           | 21.04 | 27.47 |          108.61 |            5.57 |
| qwen7    | 20 visible excerpts   | 36.25 | 47.24 |         3604.29 |            5.30 |
| qwen7    | 20 full source blocks | 36.25 | 47.62 |         3615.32 |            5.37 |
| qwen7    | Seed                  | 35.21 | 45.72 |          291.89 |            5.91 |

![All main context conditions; labels mark added-token allowances.](development_budget_accuracy.pdf){width=100%}

\newpage

# Full priority and compression matrix

Each cell is EM / F1, in percent. Allowance b is added to the full native seed prompt length, including instructions, titles, identifiers and question. It is not a source-body-only budget. Source segments follow the existing punctuation-based splitter over 100-word DPR blocks; they are not guaranteed complete linguistic sentences.

## Qwen2.5-7B

| Method                  | +128          | +256          | +512          |
|:------------------------|:--------------|:--------------|:--------------|
| Title-linked            | 35.62 / 46.12 | 38.12 / 48.91 | 37.50 / 48.45 |
| Window                  | 35.83 / 46.65 | 35.21 / 46.82 | 36.46 / 47.85 |
| First segment, no link  | 35.42 / 46.09 | 35.83 / 46.27 | 36.46 / 47.23 |
| Link, no first priority | 37.08 / 47.30 | 35.83 / 46.77 | 38.75 / 49.47 |
| Question-only link      | 36.25 / 46.94 | 36.88 / 47.87 | 37.71 / 49.27 |
| Seed-only link          | 35.83 / 46.34 | 37.71 / 48.99 | 38.33 / 49.31 |
| Random addition         | 34.79 / 44.77 | 34.58 / 44.17 | 34.38 / 46.05 |
| LLMLingua-2             | 24.79 / 31.87 | 25.00 / 34.52 | 27.29 / 35.84 |

## Llama3.1-8B

| Method                  | +128          | +256          | +512          |
|:------------------------|:--------------|:--------------|:--------------|
| Title-linked            | 36.25 / 47.23 | 35.83 / 46.31 | 39.58 / 50.18 |
| Window                  | 37.29 / 47.73 | 37.50 / 48.06 | 35.62 / 46.16 |
| First segment, no link  | 35.83 / 45.80 | 36.04 / 45.56 | 34.17 / 44.80 |
| Link, no first priority | 37.50 / 48.52 | 37.92 / 49.08 | 37.08 / 48.17 |
| Question-only link      | 35.83 / 46.83 | 36.25 / 47.31 | 37.08 / 48.47 |
| Seed-only link          | 36.88 / 47.36 | 36.46 / 46.92 | 38.33 / 48.64 |
| Random addition         | 35.83 / 46.60 | 33.96 / 44.33 | 32.50 / 42.81 |
| LLMLingua-2             | 28.12 / 36.72 | 28.54 / 37.46 | 28.54 / 38.13 |

\newpage

# Six-condition average differences

Title-linked minus each comparator, averaged equally over both readers and all three allowances, then equally across datasets. The seed and uncompressed comparator scores are reused in each of the six paired differences; questions, not model calls, are the resampling units. Intervals are 95% descriptive intervals from 10,000 stratified paired bootstrap draws (seed 20261111). No new significance threshold or favorable-budget selection is applied.

| Comparator              | EM difference [95% interval]   | F1 difference [95% interval]   |
|:------------------------|:-------------------------------|:-------------------------------|
| Window                  | +0.83 [-0.94, +2.64]           | +0.65 [-1.07, +2.38]           |
| First segment, no link  | +1.53 [-0.07, +3.19]           | +1.91 [+0.37, +3.53]           |
| Link, no first priority | -0.21 [-1.70, +1.28]           | -0.35 [-1.75, +1.04]           |
| Question-only link      | +0.49 [-0.83, +1.81]           | +0.08 [-1.16, +1.37]           |
| Seed-only link          | -0.10 [-1.25, +1.04]           | -0.06 [-1.07, +0.90]           |
| Random addition         | +2.81 [+0.97, +4.72]           | +3.08 [+1.27, +4.92]           |
| LLMLingua-2             | +10.10 [+7.12, +13.16]         | +12.11 [+9.19, +14.99]         |
| Seed                    | +1.53 [-0.38, +3.51]           | +1.83 [+0.01, +3.68]           |
| Closed book             | +16.01 [+12.08, +19.93]        | +19.38 [+15.39, +23.36]        |
| 20 visible excerpts     | +3.40 [+0.80, +6.04]           | +3.27 [+0.82, +5.78]           |
| 20 full source blocks   | +3.40 [+0.80, +6.04]           | +3.25 [+0.84, +5.68]           |

# Cost and compressor controls

The shared four-search controller consumes a mean 5991.57 generation-input tokens and 137.17 output tokens per question. The seed selector adds 3930.29 input and 32.75 output tokens. These upstream costs are excluded from the reader-token plot, so a short reader context alone does not establish end-to-end savings. The uncompressed baseline can omit the selector; closed book can omit retrieval and all upstream generation. LLMLingua-2 does not use the seed content, but its experimental cap is defined from seed length and therefore depends on seed computation in this protocol.

The official LLMLingua-2 package (0.2.2) and Microsoft XLM-RoBERTa-large MeetingBank checkpoint were used in float32 evaluation mode. All 20 full source blocks, with the same rendered headers, were compressed. Only newline tokens were forced; context filtering was disabled. An input-length-only target search retained the largest feasible candidate observed within one minimum-target check and ten bisection steps; no final text trimming was used. Across 480 questions, classifier forward calls totaled 480; the deterministic forward cache served 15,225 additional uses over 15,701 compression targets. Summed per-question compressor work time was 703.17 seconds across four parallel shards. This is not a controlled latency benchmark.

# Interpretation boundary

The new baselines and ablations assess whether the title-link rule adds value beyond seed extraction, generic context expansion, and learned token compression. Any favorable cell remains a development result. A single separately fixed average contrast on fresh questions is needed before describing an independently confirmed accuracy improvement. Original held-out comparisons and all unfavorable development cells remain part of the evidence.

# Reproduction artifacts

The accompanying CSV files contain every dataset/reader/allowance score, paired corrected/worsened/tied counts, all 132 metric contrasts and 22 aggregate contrasts. The machine-readable audit records input-budget, source-span and request checks. Independent validation recomputed all 112 macro metric values and all 132 paired estimates and transition counts directly from question-level outputs.
