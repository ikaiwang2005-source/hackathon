"""Spot-check client aggregation totals and dataset coverage."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd

from ingest import (
    DATASETS,
    PROJECT_ROOT,
    RANKING_OUTPUT,
    aggregate_pillar,
    build_client_reference,
    read_processed_dataset,
)


PILLAR_COLUMNS = {
    "cross_border_payments": "cross_border_fx_activity_captured_zar",
    "trade_finance": "trade_finance_activity_captured_zar",
    "transactional_banking": "transactional_banking_activity_captured_zar",
}
TOTAL_COLUMN = "total_captured_activity_zar"
TOLERANCE_ZAR = 0.01


def format_zar(value: float) -> str:
    return f"{value:,.2f}"


def load_frames() -> dict[str, pd.DataFrame]:
    return {config.name: read_processed_dataset(config) for config in DATASETS}


def compute_entity_totals(entity_id: str, frames: dict[str, pd.DataFrame]) -> dict[str, float]:
    totals: dict[str, float] = {}
    print(f"\n=== Entity spot check: {entity_id} ===")

    for config in DATASETS:
        df = frames[config.name]
        filtered = df[df["entity_id"] == entity_id]
        output_column = PILLAR_COLUMNS[config.name]

        if filtered.empty:
            total = 0.0
        else:
            aggregated = aggregate_pillar(filtered, config.value_column, output_column)
            total = float(aggregated[output_column].iloc[0]) if not aggregated.empty else 0.0

        totals[output_column] = total
        print(f"{config.name}:")
        print(f"  Rows: {len(filtered):,}")
        print(f"  Computed {output_column}: {format_zar(total)}")

    totals[TOTAL_COLUMN] = sum(totals[column] for column in PILLAR_COLUMNS.values())
    print(f"Computed total: {format_zar(totals[TOTAL_COLUMN])}")
    return totals


def load_ranking_row(entity_id: str) -> pd.Series:
    if not RANKING_OUTPUT.exists():
        raise FileNotFoundError(
            f"Missing {RANKING_OUTPUT.relative_to(PROJECT_ROOT)}. Run `python src/ingest.py` first."
        )

    ranking = pd.read_csv(RANKING_OUTPUT)
    matching = ranking[ranking["entity_id"] == entity_id]
    if matching.empty:
        raise ValueError(f"{entity_id} was not found in {RANKING_OUTPUT.relative_to(PROJECT_ROOT)}")
    if len(matching) > 1:
        raise ValueError(f"{entity_id} appears {len(matching)} times in the ranking output")
    return matching.iloc[0]


def print_saved_comparison(entity_id: str, computed: dict[str, float]) -> None:
    saved = load_ranking_row(entity_id)

    print("\n=== Saved ranking comparison ===")
    mismatches: list[str] = []
    for column in [*PILLAR_COLUMNS.values(), TOTAL_COLUMN]:
        computed_value = float(computed[column])
        saved_value = float(saved[column])
        delta = computed_value - saved_value
        verdict = "MATCH" if math.isclose(computed_value, saved_value, abs_tol=TOLERANCE_ZAR) else "MISMATCH"
        if verdict == "MISMATCH":
            mismatches.append(column)

        print(
            f"{column}: computed={format_zar(computed_value)} "
            f"saved={format_zar(saved_value)} delta={format_zar(delta)} {verdict}"
        )

    print("\nVerdict:", "MATCH" if not mismatches else f"MISMATCH ({', '.join(mismatches)})")


def run_entity_spot_check(entity_id: str) -> None:
    frames = load_frames()
    computed = compute_entity_totals(entity_id, frames)
    print_saved_comparison(entity_id, computed)


def run_coverage_check() -> None:
    frames = load_frames()
    reference = build_client_reference(frames.values())
    reference_ids = set(reference["entity_id"])

    print("\n=== Dataset coverage check ===")
    print(f"Full client reference size: {len(reference):,}")

    for config in DATASETS:
        df = frames[config.name]
        present_ids = set(df["entity_id"].dropna().unique())
        absent_ids = sorted(reference_ids - present_ids)

        print(f"\n{config.name}:")
        print(f"  Unique entity_id count: {len(present_ids):,}")
        if not absent_ids:
            print("  Absent clients: none")
            continue

        print(f"  Absent clients: {len(absent_ids):,}")
        absent = reference[reference["entity_id"].isin(absent_ids)].sort_values("entity_id")
        for row in absent.itertuples(index=False):
            print(f"    - {row.entity_id}: {row.entity_name} ({row.sector})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify per-client aggregation totals or dataset coverage."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--entity-id", help="Client entity_id to spot-check, for example E11")
    mode.add_argument(
        "--coverage-check",
        action="store_true",
        help="List per-dataset entity_id coverage and absent clients",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.coverage_check:
        run_coverage_check()
    else:
        run_entity_spot_check(args.entity_id)


if __name__ == "__main__":
    main()
