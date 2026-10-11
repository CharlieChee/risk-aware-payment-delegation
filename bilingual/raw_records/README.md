# Retained primary trial records

The four compressed JSONL shards contain all 800 retained DeepSeek low/high
Direct/Set trials on the 200-task primary benchmark. Each entry includes the
saved request, provider response, observation, evaluation, source hashes, and
a link to the corresponding English task. Original prompt and response text
is preserved here alongside the bilingual materials. Personal paths are
sanitized and listed in `sanitized_fields`.

```bash
python scripts/verify_raw_records.py
```

Read a shard with Python's `gzip.open(path, "rt", encoding="utf-8")` and parse
each line as JSON. `manifest.json` lists the cohort sizes, hashes, and outcomes.
