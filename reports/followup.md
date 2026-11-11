---
title: "Context expansion: descriptive follow-up and input diagnostics"
author: "Yeo-Chan Yoon"
date: "11 November 2026"
---

## Scope and main findings

The follow-up reuses all 4,500 internally held-out questions from the completed confirmatory study. It is post hoc and supplies no new independent confirmation. The original fixed primary result remains +0.6333 exact-match percentage points (95% paired interval [0.1593, 1.0926], two-sided randomization p = 0.009). It compares title-linked with proximity expansion across both readers, all three allowances and equally weighted datasets.

Added controls weaken a title-link superiority claim. An expansion ordered by archived relevance scores exceeds title linking by 0.71 points. Seed retention exceeds deduplicated full context by 1.59 points overall, but that contrast is −0.44 for Qwen and +3.62 for Llama. The simple ablations remain competitive. Relevance-score expansion versus seed is +0.60 [−0.06, +1.25], so defeating title linking does not establish an average benefit of expansion.

## Complete-matrix contrasts

All rows below are descriptive within the follow-up execution. Intervals resample questions within each dataset (10,000 draws, seed 20261111), with equal dataset weights; budgets/readers are paired within questions, not independent replicates. No multiplicity-controlled follow-up discoveries are claimed.

| Contrast                                  |   EM difference | 95% interval     |
|:------------------------------------------|----------------:|:-----------------|
| Linked − Window                           |           0.578 | [+0.104, +1.041] |
| Linked − Seed                             |          -0.115 | [-0.696, +0.485] |
| Linked − Repeated full blocks             |           1.763 | [+0.959, +2.570] |
| Linked − Unique full blocks               |           1.474 | [+0.685, +2.259] |
| Linked − No first priority                |           0.363 | [-0.015, +0.737] |
| Linked − Seed-only link                   |          -0.222 | [-0.541, +0.093] |
| Linked − Score priority                   |          -0.711 | [-1.248, -0.178] |
| Seed − Unique full blocks                 |           1.589 | [+0.656, +2.533] |
| Seed − Repeated full blocks               |           1.878 | [+0.933, +2.822] |
| Unique full blocks − Repeated full blocks |           0.289 | [-0.256, +0.833] |
| Window − Seed                             |          -0.693 | [-1.274, -0.119] |

All dataset, reader and allowance cells, including unfavorable comparisons, are in the accompanying CSV files. The three allowances are 128, 256 and 512 tokens above the complete native seed prompt. The unique full-context control retains the first occurrence of each exact corpus passage identifier. Score priority uses archived BGE passage scores against the retrieval subquery, followed by seed proximity and fixed source order; it does not use fresh segment scores. The two ablations are unchanged no-first-priority and seed-only linking.

## Difficulty and paired decomposition

The original linked-minus-window differences at allowances 128, 256 and 512 are −0.40 [−1.03, +0.22], +0.80 [+0.11, +1.46] and +1.50 [+0.83, +2.17]. The paired difference between 512 and 128 is +1.90 [+1.04, +2.76]; 512 versus 256 is +0.70 [−0.04, +1.48]. Window minus seed is −0.74 [−1.32, −0.16]. These decompositions are post hoc.

HotpotQA contains 329 easy, 940 medium and 231 hard questions. Its hard-only linked-minus-window contrast is −1.23 [−3.46, +1.08]. Averaging the hard subset with unchanged 2Wiki and MuSiQue samples, retaining equal dataset weights, gives +0.11 [−0.72, +0.97]. This imprecise sensitivity prevents treating the mixed-difficulty estimate as official hard-only benchmark performance. The 4,500-row question score file permits independent recomputation.

## Native-input diagnostics

Coverage is measured on all 4,500 original native-cap inputs, retaining two upstream failures as absent evidence. Title recall, strict same-title sentence containment, non-Boolean answer presence, and same-title support word-type recall are distinct measures. MuSiQue supplies paragraph labels, so sentence recall is undefined. One invalid HotpotQA supporting-sentence index remains absent in the recall denominator. Higher title coverage does not consistently imply higher sentence coverage, answer presence or accuracy.

At allowance 256, Qwen's added 252.60 tokens comprise 167.67 body, 16.62 title, 60.65 identifier and 7.65 scaffolding tokens. Llama's 252.95 comprise 178.72 body, 18.44 title, 47.21 identifier and 8.58 scaffolding tokens. Components use exact full-prompt tokenization and average the two title/identifier insertion orders. Hash identifiers account for 71% and 64% of header increments under this rendering; these are not intrinsic costs of title linking.

The twenty slots contain 13.41 unique corpus passages on average. At allowance 256, 18.6% of Qwen and 20.1% of Llama added segments repeat an already selected exact corpus segment; within tier 0 these shares are 28.0% and 30.9%. Cost/repetition means condition on 4,498 successful upstream questions, with invalid-seed fallbacks retained. All budgets and per-question diagnostics are supplied.

## Execution and independent verification

All 162,000 records completed: 117,559 unique requests, 44,369 cache hits and 72 dependent failures from two original upstream failures. There were zero reader failures, retry errors or empty answers; all 17 length-stopped outputs were retained. Every condition for a reader/question used the same assigned replica. All ten owned launch groups are stopped and logs archived.

Among 72,000 repeated anchor conditions, 1,531 answer strings, 220 EM scores and 540 F1 scores changed from the original execution. The original primary estimate is preserved; added-method comparisons use contemporaneous outputs. In the preliminary 480-question study, 95 raw answers, 15 EM and 33 F1 scores changed over 5,760 identical prompts, explaining the +0.66 versus +0.83 estimates.

Independent public code reproduced all 162,000 scores from separately resolved benchmark labels and matched 3,792 statistical values within 1e-10. A separate recomputation directly from the 4,500-row score file matched 2,205 decomposition values and the window-minus-seed randomization result. Portable input reconstruction matched all 90,000 added-condition prompt hashes, lengths and selections. The original scientific outputs are preserved.

Code and versioned artifacts: <https://github.com/ycyoon/title-linked-source-completion>. The portable workflow reconstructs downstream inputs and statistics conditional on frozen retrieval slots and seeds; it does not rebuild the full retrieval indexes. Original benchmark/corpus text and model weights must be obtained separately.
