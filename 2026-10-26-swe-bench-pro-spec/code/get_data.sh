#!/bin/sh
# Downloads the three public datasets into ../raw/ (run from code/).
set -e
mkdir -p ../raw && cd ../raw
curl -sL -o v1.parquet https://huggingface.co/api/datasets/ScaleAI/SWE-bench_Pro/parquet/v1/test/0.parquet
curl -sL -o v2.parquet https://huggingface.co/api/datasets/ScaleAI/SWE-bench_Pro/parquet/default/test/0.parquet
curl -sL -o pv.jsonl https://huggingface.co/datasets/opencompass/SWEBench-Pro-Verified/resolve/main/swebench_pro_verified.jsonl
curl -sL -o verified.parquet https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified/resolve/main/data/test-00000-of-00001.parquet
