# Research: what SWE-Bench Pro tells the agent before it starts

> The evidence behind the [X Article](https://x.com/con_golias/status/2114495930074325295) *"SWE-Bench Pro names 81% of the new functions its hidden tests
> call. The top score is now 99.4%"* by Konstantinos Gkolias (@con_golias), 26 Oct 2026.
> Data downloaded and counted on 25 Oct 2026. Everything here can be rerun in under a minute.

## The question

SWE-Bench Pro gives the agent three fields: the issue text (`problem_statement`), a list of
`requirements` and an `interface` block. The grading is done by hidden tests. **How many of the new
functions, classes and fields that the hidden tests call is the agent told about in advance, and
in which field?**

## Result

| | SWE-bench Verified | Pro v1 (731 tasks) | Pro V2 (642 tasks) |
|---|---|---|---|
| Tasks whose hidden tests call at least one new name | 19 of 500 | 353 of 731 | 326 of 642 |
| New names the tests call | 28 | 818 | 703 |
| Named in the issue text alone | 67.9% | 10.0% | 9.1% |
| Named in the full prompt (issue + requirements + interface) | 67.9% | **81.3%** | **87.8%** |
| Tasks where every such name is in the prompt | 57.9% | 75.6% | 85.3% |
| Exact strings the tests assert, in the issue alone | 45.5% | 15.4% | 9.1% |
| Exact strings the tests assert, in the full prompt | 45.5% | 55.8% | 70.1% |

Verified has no requirements or interface fields, so its two rows are the same. Its figures rest
on 28 names in 19 tasks.

Other counts quoted in the article (`other_counts.py`):

- V2 Hard subset: 90.6% of new names are in the prompt (36 tasks), against 87.2% in the rest (290).
- Median requirement bullets: 6 in v1, 7 in V2.
- Requirements longer than the issue text: 54.0% of v1 tasks, 71.2% of V2 tasks.
- Of the 102 tasks OpenCompass's SWE-Bench Pro Verified changed, Scale's V2 drops 17 and keeps 85
  (`repair_overlap.py`). Scale does not mark which kept tasks it repaired, so the overlap of the
  two audits cannot be measured beyond that.

## Method

For each task, `spec_coverage.py`:

1. collects the names the reference patch **defines** on its added lines (`def`, `func`, `class`,
   `function`, `type`, `const`, `let`, `var`);
2. keeps only names the hidden **test patch calls**;
3. drops names that also appear on a removed line of the patch (a rename or rewrite, not a new
   name), names under five characters, dunder methods, and a short list of generic words;
4. checks whether each name appears, as a whole word, in the issue text and in the full prompt.

Expected strings are string literals of 8 to 80 characters, containing a space, that the fix adds
and the hidden tests assert.

## What this does not show

- **A name is not the code.** The implementation is still the agent's job, and the Hard subset is
  just as specified as the rest yet much harder to solve.
- **It is a count with regular expressions.** It misses names introduced in ways the patterns don't
  catch, and it counts a name as given wherever it appears in the prompt. A hand check of a sample
  found genuine matches, but treat the percentages as estimates.
- **No link to pass rates.** Scale publishes aggregate scores, not results per task, so whether
  specified tasks are solved more often cannot be tested here.

## Rerun

```sh
cd code
sh get_data.sh            # downloads the public datasets into ../raw/ (not committed)
python spec_coverage.py   # writes ../data/spec_strict_per_task.csv and ../data/spec_summary.csv
python other_counts.py    # Hard vs rest, requirement length
python repair_overlap.py  # which tasks each repair changed
```

Needs Python 3 with `pandas` and `pyarrow`.

## Files

- `code/get_data.sh`: download URLs of the four public files.
- `code/spec_coverage.py`: the main count.
- `code/other_counts.py`: the remaining counts quoted in the article.
- `code/repair_overlap.py`: compares v1, V2 and SWE-Bench Pro Verified field by field.
- `data/spec_strict_per_task.csv`: one row per task (Verified, Pro v1, Pro V2).
- `data/spec_summary.csv`: the table above.

## Data sources

- `ScaleAI/SWE-bench_Pro` on Hugging Face, configs `v1` and `default` (V2). Paper: arXiv 2509.16941;
  V2 paper: arXiv 2610.24206.
- `opencompass/SWEBench-Pro-Verified` on Hugging Face. Paper: arXiv 2609.08149.
- `princeton-nlp/SWE-bench_Verified` on Hugging Face.

The datasets are not redistributed here; `get_data.sh` fetches them from their owners.
