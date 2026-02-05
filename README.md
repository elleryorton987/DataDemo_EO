# DataDemo_EO

This repository contains a small workflow to summarize the `je_samples.xlsx` journal entry export.

## What the workflow does

Running the analysis script will generate an `outputs/` folder containing:

- `summary.json`: machine-readable stats for each sheet.
- `summary.md`: a human-readable overview.
- `*_numeric_describe.csv`: numeric descriptive statistics per sheet.
- `*_missing_values.csv`: missing value counts per column.

## Run locally

```bash
python -m pip install -r requirements.txt
python scripts/analyze_je_samples.py
```

## Run in GitHub Actions

The `JE Sample Analysis` workflow runs automatically on pushes that touch the input Excel file, the analysis script, or the workflow itself. It also supports manual runs via **Actions → JE Sample Analysis → Run workflow**. The outputs are uploaded as an artifact named `je-sample-outputs`.
