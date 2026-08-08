# Task 002b: Client Spot-Check Script

**For:** Codex (execution steps below)
**Prerequisite (User):** Task 002 must already be done — this task depends on `data/processed/*.parquet` and `src/ingest.py` existing.

---

## Why?

Task 002's testing instructions call for manually spot-checking a client's totals by hand in Excel — but with `transactional_banking` at ~1 million rows, doing that by eye isn't realistic. This task builds a small, reusable script that independently recomputes one client's totals directly from the processed data and prints them next to what `client_activity_ranking.csv` says, so any mismatch is immediately visible. This is also useful right now to investigate whether the low unique-`entity_id` count seen in `cross_border_payments` (20, vs an expected ~50) is a real data issue or just means most clients simply don't have cross-border activity.

---

## Steps for Codex

### 1. Create `src/spot_check.py`
Build a command-line script that:
- Takes one required argument: `--entity-id` (the client to check)
- Loads all three parquet files from `data/processed/`
- For each dataset, filters to just that `entity_id` and prints:
  - Row count in that dataset for this client
  - Sum of the relevant value column (`value_zar` or `amount_zar`), computed the same way `src/ingest.py` does it (sum of absolute values) — reuse the aggregation logic from `src/ingest.py` directly (import it) rather than reimplementing it, so the two can never silently drift out of sync
- Prints a total across all three pillars
- Then loads `outputs/client_activity_ranking.csv`, finds that same `entity_id`'s row, and prints its pillar totals and grand total side by side with the independently-computed numbers above
- Prints a clear `MATCH` or `MISMATCH` verdict by comparing the two totals (allow a tiny floating-point tolerance, e.g. within 1 cent)

### 2. Add a second mode: dataset coverage check
Add a `--coverage-check` flag (no entity-id needed) that, for each of the three datasets, prints:
- Unique `entity_id` count in that dataset
- Which entity_ids from the full 50-client reference list (built the same way `build_client_reference` does in `src/ingest.py`) are **absent** from that dataset entirely

This directly answers "is a client missing because they have no activity in that pillar, or because of a data problem" — list the actual missing entity_ids/names, don't just report a count.

### 3. Update the README
Tick this as a completed sub-item under Phase 2 in `README.md` (it's a testing/verification aid for Phase 2, not a new numbered phase) and add a one-line dated Progress Log entry noting the spot-check script was added.

### 4. Commit
Commit `src/spot_check.py` with message `feat: add client spot-check and coverage verification script`.

---

## Testing Instructions (for you, the User)

1. **Run the coverage check first** — this directly answers your current question:
   ```
   python src/spot_check.py --coverage-check
   ```
   Read the output for `cross_border_payments`. If it lists ~30 specific named clients as "absent," and those are plausible domestic-only businesses, that's likely fine — just a real absence of FX activity, not a bug. If instead it shows entity_ids that *look like* they should be there but are formatted slightly differently than in the other files (e.g. `CL001` vs `CL01` vs `cl001`), that's a real normalization bug to flag back to Task 002.

2. **Then spot-check a specific client**, e.g. one from the top of `client_activity_ranking.csv`:
   ```
   python src/spot_check.py --entity-id <paste an actual entity_id from the CSV>
   ```
   Confirm it prints `MATCH`. If it prints `MISMATCH`, note which pillar disagrees and by how much — that tells us exactly where to look (e.g. if only trade_finance mismatches, the bug is isolated to that dataset's aggregation).

3. Run the spot-check for at least 2–3 different clients, including one with a small total and one with a large total, not just the top row — a bug that only affects certain value ranges (e.g. a bug when `direction` is "credit" vs "debit") could hide behind a single test.

### If something breaks (debugging steps)
- If `--coverage-check` shows entity_ids missing across *all three* datasets (not just one), that client shouldn't be in the reference list at all — check where it's coming from.
- If a `MISMATCH` shows up: check whether it's exactly 2x off in one direction — that's a classic sign of double-counting (e.g. a duplicate row surviving the parquet conversion) or of debit/credit values cancelling incorrectly if net-summing crept in instead of absolute-value summing somewhere.

---

## Next Task
Once the coverage check and spot-checks look right (or any real issues found here are fixed), continue with Task 002's remaining testing steps, then move to **Task 003 — Client Sector Grouping & Research Tiering**.
