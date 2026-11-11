---
title: "Independent native-cap confirmation"
date: "11 November 2026"
---

# Primary result

Linked minus window, averaged over both readers and all three allowances: **+0.6333 EM percentage points**, 95% question-paired bootstrap interval **[+0.1593, +1.0926]**. The single fixed two-sided question-clustered sign-flip test gives **p = 0.008810** (880 extreme draws in 100,000; plus-one Monte Carlo correction).

The sample was reserved before outcomes: 1,500 HotpotQA train, 1,500 2Wiki dev and 1,500 MuSiQue answerable train questions. All prior normalized questions and MuSiQue decomposition identifiers were excluded; selected MuSiQue questions share no decomposition IDs. This is an internal held-out evaluation, not an official hidden-test submission or evidence of pretraining decontamination.

The estimand assigns equal weight to datasets, readers and allowances. Questions are the independent resampling units; the six comparisons are kept together. Alpha was 0.05. There was no efficacy stopping, replacement, optional sample extension, favorable-budget selection or method change. Other contrasts and cells below are descriptive. The sign-flip test assumes paired-label exchangeability; a nonsignificant result does not prove zero effect.

| Dataset   |   Average EM difference (pp) |
|:----------|-----------------------------:|
| hotpot    |                         0.33 |
| 2wiki     |                         0.18 |
| musique   |                         1.39 |

# Baseline comparisons

| Comparator     | EM difference [95% interval]   | F1 difference [95% interval]   |
|:---------------|:-------------------------------|:-------------------------------|
| Window         | +0.63 [+0.16, +1.09]           | +0.79 [+0.35, +1.22]           |
| Seed           | -0.11 [-0.69, +0.48]           | +0.20 [-0.36, +0.76]           |
| 20 full blocks | +1.83 [+1.03, +2.63]           | +1.75 [+1.00, +2.51]           |
| 20 excerpts    | +1.96 [+1.17, +2.76]           | +1.98 [+1.22, +2.73]           |
| Closed book    | +15.94 [+14.78, +17.12]        | +18.59 [+17.42, +19.79]        |
| LLMLingua-2    | +9.80 [+8.87, +10.71]          | +11.31 [+10.45, +12.19]        |

The baseline is reused in each budget contrast when it has no allowance. Intervals preserve that pairing; repeated baseline appearances do not increase the sample size. Learned compression uses one official MeetingBank checkpoint and input-only native-cap calibration.
\newpage

# Complete macro scores

## Qwen2.5-7B-Instruct

| arm            |   allowance |    em |    f1 |   prompt_tokens |   output_tokens |
|:---------------|------------:|------:|------:|----------------:|----------------:|
| Closed book    |           0 | 19.29 | 25.49 |          109.89 |            5.86 |
| 20 excerpts    |           0 | 34.18 | 43.17 |         3561.14 |            5.58 |
| 20 full blocks |           0 | 34.42 | 43.57 |         3572.06 |            5.60 |
| Seed           |           0 | 34.31 | 42.87 |          285.65 |            5.89 |
| Title-linked   |         128 | 33.73 | 42.57 |          410.33 |            5.94 |
| LLMLingua-2    |         128 | 22.47 | 28.59 |          394.52 |            5.07 |
| Window         |         128 | 34.13 | 42.79 |          407.59 |            6.00 |
| Title-linked   |         256 | 35.18 | 44.15 |          538.14 |            5.79 |
| LLMLingua-2    |         256 | 24.76 | 32.09 |          522.41 |            5.04 |
| Window         |         256 | 34.02 | 42.78 |          534.48 |            5.82 |
| Title-linked   |         512 | 35.58 | 44.44 |          793.16 |            5.65 |
| LLMLingua-2    |         512 | 27.20 | 35.38 |          778.21 |            5.09 |
| Window         |         512 | 34.04 | 42.74 |          789.51 |            5.76 |

## Llama-3.1-8B-Instruct

| arm            |   allowance |    em |    f1 |   prompt_tokens |   output_tokens |
|:---------------|------------:|------:|------:|----------------:|----------------:|
| Closed book    |           0 | 17.22 | 23.49 |          131.53 |            6.75 |
| 20 excerpts    |           0 | 30.29 | 39.03 |         3336.45 |            5.94 |
| 20 full blocks |           0 | 30.31 | 39.08 |         3346.34 |            5.96 |
| Seed           |           0 | 34.29 | 42.90 |          289.83 |            5.27 |
| Title-linked   |         128 | 33.56 | 42.17 |          414.87 |            5.47 |
| LLMLingua-2    |         128 | 21.91 | 29.08 |          401.19 |            4.76 |
| Window         |         128 | 33.96 | 42.59 |          412.60 |            5.44 |
| Title-linked   |         256 | 33.82 | 42.74 |          542.66 |            5.59 |
| LLMLingua-2    |         256 | 24.00 | 31.42 |          528.90 |            4.96 |
| Window         |         256 | 33.38 | 42.19 |          539.87 |            5.56 |
| Title-linked   |         512 | 33.29 | 42.41 |          797.71 |            5.61 |
| LLMLingua-2    |         512 | 26.02 | 34.04 |          784.84 |            5.00 |
| Window         |         512 | 31.82 | 40.64 |          795.08 |            5.64 |

\newpage

# Dataset-level scores

## Qwen2.5-7B-Instruct / hotpot

| arm            |   allowance |    em |    f1 |
|:---------------|------------:|------:|------:|
| Closed book    |           0 | 24.73 | 31.06 |
| 20 excerpts    |           0 | 50.80 | 60.39 |
| 20 full blocks |           0 | 51.20 | 60.77 |
| Seed           |           0 | 50.93 | 59.38 |
| Title-linked   |         128 | 50.60 | 59.51 |
| LLMLingua-2    |         128 | 31.40 | 40.39 |
| Window         |         128 | 51.20 | 59.88 |
| Title-linked   |         256 | 52.00 | 61.09 |
| LLMLingua-2    |         256 | 36.27 | 46.36 |
| Window         |         256 | 51.53 | 60.47 |
| Title-linked   |         512 | 52.47 | 61.23 |
| LLMLingua-2    |         512 | 41.40 | 51.50 |
| Window         |         512 | 51.80 | 60.26 |

## Qwen2.5-7B-Instruct / 2wiki

| arm            |   allowance |    em |    f1 |
|:---------------|------------:|------:|------:|
| Closed book    |           0 | 25.87 | 30.84 |
| 20 excerpts    |           0 | 31.00 | 39.22 |
| 20 full blocks |           0 | 31.20 | 39.78 |
| Seed           |           0 | 32.07 | 39.83 |
| Title-linked   |         128 | 30.87 | 39.00 |
| LLMLingua-2    |         128 | 25.20 | 28.26 |
| Window         |         128 | 32.40 | 40.25 |
| Title-linked   |         256 | 33.13 | 41.22 |
| LLMLingua-2    |         256 | 25.60 | 29.41 |
| Window         |         256 | 31.40 | 39.21 |
| Title-linked   |         512 | 33.73 | 42.33 |
| LLMLingua-2    |         512 | 25.53 | 30.69 |
| Window         |         512 | 31.60 | 39.85 |

## Qwen2.5-7B-Instruct / musique

| arm            |   allowance |    em |    f1 |
|:---------------|------------:|------:|------:|
| Closed book    |           0 |  7.27 | 14.57 |
| 20 excerpts    |           0 | 20.73 | 29.89 |
| 20 full blocks |           0 | 20.87 | 30.17 |
| Seed           |           0 | 19.93 | 29.39 |
| Title-linked   |         128 | 19.73 | 29.21 |
| LLMLingua-2    |         128 | 10.80 | 17.12 |
| Window         |         128 | 18.80 | 28.24 |
| Title-linked   |         256 | 20.40 | 30.13 |
| LLMLingua-2    |         256 | 12.40 | 20.51 |
| Window         |         256 | 19.13 | 28.67 |
| Title-linked   |         512 | 20.53 | 29.77 |
| LLMLingua-2    |         512 | 14.67 | 23.94 |
| Window         |         512 | 18.73 | 28.10 |

\newpage

## Llama-3.1-8B-Instruct / hotpot

| arm            |   allowance |    em |    f1 |
|:---------------|------------:|------:|------:|
| Closed book    |           0 | 24.73 | 31.70 |
| 20 excerpts    |           0 | 45.67 | 54.43 |
| 20 full blocks |           0 | 45.47 | 54.24 |
| Seed           |           0 | 50.93 | 59.35 |
| Title-linked   |         128 | 48.80 | 57.70 |
| LLMLingua-2    |         128 | 32.13 | 41.86 |
| Window         |         128 | 49.20 | 58.04 |
| Title-linked   |         256 | 48.93 | 58.41 |
| LLMLingua-2    |         256 | 35.47 | 44.78 |
| Window         |         256 | 49.00 | 57.83 |
| Title-linked   |         512 | 49.13 | 58.60 |
| LLMLingua-2    |         512 | 39.40 | 49.36 |
| Window         |         512 | 47.20 | 56.31 |

## Llama-3.1-8B-Instruct / 2wiki

| arm            |   allowance |    em |    f1 |
|:---------------|------------:|------:|------:|
| Closed book    |           0 | 19.47 | 25.65 |
| 20 excerpts    |           0 | 26.40 | 34.13 |
| 20 full blocks |           0 | 26.53 | 34.27 |
| Seed           |           0 | 32.67 | 40.63 |
| Title-linked   |         128 | 32.00 | 39.74 |
| LLMLingua-2    |         128 | 21.93 | 26.07 |
| Window         |         128 | 34.07 | 41.66 |
| Title-linked   |         256 | 32.33 | 40.50 |
| LLMLingua-2    |         256 | 22.67 | 27.58 |
| Window         |         256 | 32.20 | 40.25 |
| Title-linked   |         512 | 30.73 | 39.30 |
| LLMLingua-2    |         512 | 23.73 | 28.84 |
| Window         |         512 | 30.07 | 38.00 |

## Llama-3.1-8B-Instruct / musique

| arm            |   allowance |    em |    f1 |
|:---------------|------------:|------:|------:|
| Closed book    |           0 |  7.47 | 13.13 |
| 20 excerpts    |           0 | 18.80 | 28.54 |
| 20 full blocks |           0 | 18.93 | 28.72 |
| Seed           |           0 | 19.27 | 28.73 |
| Title-linked   |         128 | 19.87 | 29.07 |
| LLMLingua-2    |         128 | 11.67 | 19.31 |
| Window         |         128 | 18.60 | 28.08 |
| Title-linked   |         256 | 20.20 | 29.31 |
| LLMLingua-2    |         256 | 13.87 | 21.91 |
| Window         |         256 | 18.93 | 28.51 |
| Title-linked   |         512 | 20.00 | 29.33 |
| LLMLingua-2    |         512 | 14.93 | 23.91 |
| Window         |         512 | 18.20 | 27.61 |

\newpage

# Execution and costs

| Check                            |   Count |
|:---------------------------------|--------:|
| questions                        |    4500 |
| records                          |  117000 |
| failures                         |      48 |
| upstream_failed_records          |      48 |
| reader_failed_records            |       0 |
| length_stops                     |      21 |
| empty_answers                    |       0 |
| cache_hits                       |   10848 |
| unique_requests                  |  106104 |
| record_summed_attempt_errors     |       0 |
| same_backend_per_question_reader |    True |

Upstream token means over the 4,498 completed upstream questions: controller input 5946.06, controller output 140.83, seed-selector input 3854.81, selector output 32.26. Failed-search work is not represented in these conditional means. Reader compression does not establish full-pipeline savings; uncompressed answering can omit the selector and closed-book answering can omit all upstream computation.

Compressor classifier forwards: 4,498; exact-forward cache uses: 143,294; candidate targets: 147,788. Summed question work time: 9254.39 seconds, across four concurrent workers; this is not a controlled latency benchmark.

# Verification and interpretation

Independent validation recomputed all 52 macro EM/F1 values and 72 paired contrast estimates with corrected/worsened/tied counts from the original question-level records. The primary integer difference sum is checked separately. All 117,000 outputs remain in the analysis, including failed, empty and length-stopped records.

Interpret practical usefulness against seed, uncompressed context and the learned compressor as well as the primary window contrast. The development ablations did not establish that first-segment priority or question-side links are necessary. A favorable average does not establish universal reader/budget improvement, broad state-of-the-art performance or an optimal deployment policy. A failed confirmation must not be presented as established accuracy improvement merely because a secondary comparator is easier to beat.
