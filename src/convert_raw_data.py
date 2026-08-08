"""Convert confidential raw banking data into local Parquet caches.

The raw files stay under data/ and are gitignored. Parquet outputs are also
gitignored because they are derived from the same confidential data.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

DATASETS = {
    "cross_border_payments": ("cross_border_payments.xlsx", "cross_border_payments.csv"),
    "trade_finance": ("trade_finance.xlsx", "trade_finance.csv"),
    "transactional_banking": ("transactional_banking.xlsx", "transactional_banking.csv"),
}


def find_source_file(dataset_name: str) -> Path:
    """Return the first supported source file found for a dataset."""
    for filename in DATASETS[dataset_name]:
        path = DATA_DIR / filename
        if path.exists():
            return path

    expected = ", ".join(DATASETS[dataset_name])
    raise FileNotFoundError(f"Missing source for {dataset_name}. Expected one of: {expected}")


def parquet_is_current(source_path: Path, parquet_path: Path) -> bool:
    return parquet_path.exists() and parquet_path.stat().st_mtime >= source_path.stat().st_mtime


def read_source(source_path: Path) -> pd.DataFrame:
    if source_path.suffix.lower() == ".xlsx":
        return pd.read_excel(source_path, engine="openpyxl")
    if source_path.suffix.lower() == ".csv":
        return pd.read_csv(source_path)
    raise ValueError(f"Unsupported source file type: {source_path}")


def convert_dataset(dataset_name: str) -> Path:
    source_path = find_source_file(dataset_name)
    parquet_path = PROCESSED_DIR / f"{dataset_name}.parquet"

    if parquet_is_current(source_path, parquet_path):
        print(f"Skipping {dataset_name}: {parquet_path.relative_to(PROJECT_ROOT)} is current")
        return parquet_path

    print(f"Converting {source_path.relative_to(PROJECT_ROOT)} -> {parquet_path.relative_to(PROJECT_ROOT)}")
    df = read_source(source_path)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, index=False)
    return parquet_path


def main() -> None:
    for dataset_name in DATASETS:
        convert_dataset(dataset_name)


if __name__ == "__main__":
    main()
