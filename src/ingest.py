"""Profile and aggregate Syn Bank internal activity datasets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
RANKING_OUTPUT = OUTPUTS_DIR / "client_activity_ranking.csv"

SANE_MIN_DATE = pd.Timestamp("2000-01-01")
SANE_MAX_DATE = pd.Timestamp.today().normalize() + pd.DateOffset(years=1)


@dataclass(frozen=True)
class DatasetConfig:
    name: str
    parquet_name: str
    id_column: str
    value_column: str
    required_columns: tuple[str, ...]


DATASETS = (
    DatasetConfig(
        name="cross_border_payments",
        parquet_name="cross_border_payments.parquet",
        id_column="transaction_id",
        value_column="value_zar",
        required_columns=(
            "transaction_id",
            "entity_id",
            "entity_name",
            "sector",
            "date",
            "direction",
            "value_zar",
        ),
    ),
    DatasetConfig(
        name="trade_finance",
        parquet_name="trade_finance.parquet",
        id_column="instrument_id",
        value_column="value_zar",
        required_columns=(
            "instrument_id",
            "entity_id",
            "entity_name",
            "sector",
            "date",
            "tenor_days",
            "value_zar",
        ),
    ),
    DatasetConfig(
        name="transactional_banking",
        parquet_name="transactional_banking.parquet",
        id_column="transaction_id",
        value_column="amount_zar",
        required_columns=(
            "transaction_id",
            "entity_id",
            "entity_name",
            "sector",
            "date",
            "direction",
            "amount_zar",
        ),
    ),
)


def read_processed_dataset(config: DatasetConfig) -> pd.DataFrame:
    parquet_path = PROCESSED_DIR / config.parquet_name
    if not parquet_path.exists():
        raise FileNotFoundError(
            f"Missing {parquet_path.relative_to(PROJECT_ROOT)}. "
            "Run `python src/convert_raw_data.py` first."
        )
    return pd.read_parquet(parquet_path)


def validate_required_columns(df: pd.DataFrame, config: DatasetConfig) -> None:
    missing = sorted(set(config.required_columns) - set(df.columns))
    if missing:
        raise ValueError(f"{config.name} is missing required columns: {', '.join(missing)}")


def find_malformed_rows(df: pd.DataFrame, config: DatasetConfig) -> list[str]:
    issues: list[str] = []

    values = pd.to_numeric(df[config.value_column], errors="coerce")
    negative_values = int((values < 0).sum())
    unparsable_values = int(values.isna().sum() - df[config.value_column].isna().sum())
    if negative_values:
        issues.append(f"{negative_values} negative {config.value_column} values")
    if unparsable_values:
        issues.append(f"{unparsable_values} unparsable {config.value_column} values")

    dates = pd.to_datetime(df["date"], errors="coerce")
    bad_dates = int(dates.isna().sum())
    out_of_range_dates = int(((dates < SANE_MIN_DATE) | (dates > SANE_MAX_DATE)).sum())
    if bad_dates:
        issues.append(f"{bad_dates} unparsable dates")
    if out_of_range_dates:
        issues.append(
            f"{out_of_range_dates} dates outside {SANE_MIN_DATE.date()} to {SANE_MAX_DATE.date()}"
        )

    duplicate_ids = int(df[config.id_column].duplicated().sum())
    if duplicate_ids:
        issues.append(f"{duplicate_ids} duplicate {config.id_column} values")

    if "tenor_days" in df.columns:
        tenor = pd.to_numeric(df["tenor_days"], errors="coerce")
        negative_tenor = int((tenor < 0).sum())
        if negative_tenor:
            issues.append(f"{negative_tenor} negative tenor_days values")

    return issues


def profile_dataset(df: pd.DataFrame, config: DatasetConfig) -> dict[str, object]:
    validate_required_columns(df, config)
    dates = pd.to_datetime(df["date"], errors="coerce")
    return {
        "name": config.name,
        "rows": len(df),
        "columns": list(df.columns),
        "dtypes": {column: str(dtype) for column, dtype in df.dtypes.items()},
        "null_counts": df.isna().sum().astype(int).to_dict(),
        "unique_entity_ids": int(df["entity_id"].nunique(dropna=True)),
        "date_min": dates.min(),
        "date_max": dates.max(),
        "malformed_rows": find_malformed_rows(df, config),
    }


def print_profile(profile: dict[str, object]) -> None:
    print(f"\n=== {profile['name']} ===")
    print(f"Rows: {profile['rows']:,}")
    print(f"Unique entity_id values: {profile['unique_entity_ids']}")
    print(f"Date range: {profile['date_min']} to {profile['date_max']}")

    print("Columns and dtypes:")
    for column in profile["columns"]:
        print(f"  - {column}: {profile['dtypes'][column]}")

    print("Null counts:")
    for column, count in profile["null_counts"].items():
        if count:
            print(f"  - {column}: {count:,}")
    if not any(profile["null_counts"].values()):
        print("  - none")

    malformed_rows = profile["malformed_rows"]
    print("Potential malformed rows:")
    if malformed_rows:
        for issue in malformed_rows:
            print(f"  - {issue}")
    else:
        print("  - none detected")


def aggregate_pillar(
    df: pd.DataFrame,
    value_column: str,
    output_column: str,
) -> pd.DataFrame:
    values = pd.to_numeric(df[value_column], errors="coerce").fillna(0).abs()
    prepared = df.assign(_activity_value=values)
    return (
        prepared.groupby("entity_id", as_index=False)["_activity_value"]
        .sum()
        .rename(columns={"_activity_value": output_column})
    )


def build_client_reference(frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    refs = []
    for df in frames:
        refs.append(df[["entity_id", "entity_name", "sector"]].dropna(subset=["entity_id"]))
    return (
        pd.concat(refs, ignore_index=True)
        .drop_duplicates(subset=["entity_id"], keep="first")
        .sort_values("entity_id")
        .reset_index(drop=True)
    )


def build_client_activity_ranking(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    clients = build_client_reference(frames.values())
    cross_border = aggregate_pillar(
        frames["cross_border_payments"],
        "value_zar",
        "cross_border_fx_activity_captured_zar",
    )
    trade = aggregate_pillar(
        frames["trade_finance"],
        "value_zar",
        "trade_finance_activity_captured_zar",
    )
    transactional = aggregate_pillar(
        frames["transactional_banking"],
        "amount_zar",
        "transactional_banking_activity_captured_zar",
    )

    ranking = clients.merge(cross_border, on="entity_id", how="left")
    ranking = ranking.merge(trade, on="entity_id", how="left")
    ranking = ranking.merge(transactional, on="entity_id", how="left")

    pillar_columns = [
        "cross_border_fx_activity_captured_zar",
        "trade_finance_activity_captured_zar",
        "transactional_banking_activity_captured_zar",
    ]
    ranking[pillar_columns] = ranking[pillar_columns].fillna(0)
    ranking["total_captured_activity_zar"] = ranking[pillar_columns].sum(axis=1)

    return ranking.sort_values("total_captured_activity_zar", ascending=False).reset_index(drop=True)


def main() -> None:
    frames: dict[str, pd.DataFrame] = {}
    for config in DATASETS:
        df = read_processed_dataset(config)
        frames[config.name] = df
        print_profile(profile_dataset(df, config))

    ranking = build_client_activity_ranking(frames)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    ranking.to_csv(RANKING_OUTPUT, index=False)

    print("\n=== Aggregation ===")
    print("Cross-border/FX uses the sum of absolute value_zar by client, not net direction.")
    print("Trade finance uses the sum of absolute value_zar by client.")
    print("Transactional banking uses the sum of absolute amount_zar by client.")
    print(f"Saved {len(ranking):,} client rows to {RANKING_OUTPUT.relative_to(PROJECT_ROOT)}")
    print("\nTop 10 clients by total captured activity:")
    print(ranking.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
