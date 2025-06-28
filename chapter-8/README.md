# Chapter 8 – Data Collection, Transformation & Export

This chapter walks through a **three-stage pipeline** for compliance evidence:

| Stage | File | What it does |
|-------|------|-------------|
| 1 | `aws_data_fetcher.py` | Connects to AWS APIs (Security Hub, Config, CloudTrail) and **pulls raw JSON** evidence. All calls are read-only. |
| 2 | `pandas_transformer.py` | Uses `pandas` to **flatten, cleanse, and enrich** the raw JSON into analysis-ready DataFrames. |
| 3 | `report_exporter.py` | Saves the DataFrames to **CSV or nicely-formatted Excel** files so auditors can review them offline. |

## Quickstart

```bash
pip install boto3 pandas xlsxwriter
python aws_data_fetcher.py  # or import the functions in your own script
```

Each module is heavily commented so that even readers new to Python, AWS, or
pandas can follow along. Check the docstrings at the top of every file for a
beginner-friendly overview.
