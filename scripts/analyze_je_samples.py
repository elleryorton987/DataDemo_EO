import json
from pathlib import Path

import pandas as pd


def coerce_date_columns(frame: pd.DataFrame) -> list[str]:
    date_columns = []
    for column in frame.columns:
        if "date" in str(column).lower():
            frame[column] = pd.to_datetime(frame[column], errors="coerce")
            date_columns.append(column)
    return date_columns


def summarize_sheet(name: str, frame: pd.DataFrame, output_dir: Path) -> dict:
    date_columns = coerce_date_columns(frame)
    date_ranges = {}
    for column in date_columns:
        series = frame[column].dropna()
        date_ranges[column] = {
            "min": series.min().isoformat() if not series.empty else None,
            "max": series.max().isoformat() if not series.empty else None,
        }

    numeric_frame = frame.select_dtypes(include="number")
    numeric_describe = None
    if not numeric_frame.empty:
        numeric_describe = numeric_frame.describe().T
        numeric_describe.to_csv(output_dir / f"{name}_numeric_describe.csv")

    missing_counts = frame.isna().sum().reset_index()
    missing_counts.columns = ["column", "missing_count"]
    missing_counts.to_csv(output_dir / f"{name}_missing_values.csv", index=False)

    summary = {
        "rows": int(frame.shape[0]),
        "columns": int(frame.shape[1]),
        "column_names": [str(col) for col in frame.columns],
        "date_columns": date_columns,
        "date_ranges": date_ranges,
        "numeric_columns": [str(col) for col in numeric_frame.columns],
    }

    if numeric_describe is not None:
        summary["numeric_describe"] = numeric_describe.round(2).to_dict(orient="index")

    return summary


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    source_file = repo_root / "je_samples.xlsx"
    output_dir = repo_root / "outputs"
    output_dir.mkdir(exist_ok=True)

    excel_file = pd.ExcelFile(source_file)

    summary = {
        "source_file": source_file.name,
        "sheet_count": len(excel_file.sheet_names),
        "sheets": {},
    }

    for sheet_name in excel_file.sheet_names:
        frame = excel_file.parse(sheet_name)
        summary["sheets"][sheet_name] = summarize_sheet(sheet_name, frame, output_dir)

    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    summary_md_lines = [
        "# Journal Entry Sample Summary",
        "",
        f"**Source file:** `{summary['source_file']}`",
        f"**Sheet count:** {summary['sheet_count']}",
        "",
    ]

    for sheet_name, sheet_summary in summary["sheets"].items():
        summary_md_lines.extend(
            [
                f"## Sheet: {sheet_name}",
                f"- Rows: {sheet_summary['rows']}",
                f"- Columns: {sheet_summary['columns']}",
                f"- Date columns: {', '.join(sheet_summary['date_columns']) or 'None detected'}",
            ]
        )

        if sheet_summary["date_ranges"]:
            summary_md_lines.append("- Date ranges:")
            for column, date_range in sheet_summary["date_ranges"].items():
                summary_md_lines.append(
                    f"  - {column}: {date_range['min']} to {date_range['max']}"
                )

        numeric_columns = sheet_summary["numeric_columns"]
        summary_md_lines.append(
            f"- Numeric columns: {', '.join(numeric_columns) or 'None detected'}"
        )
        summary_md_lines.append("")

    (output_dir / "summary.md").write_text("\n".join(summary_md_lines))


if __name__ == "__main__":
    main()
