# Task 002: Data Ingestion & Profiling

**For:** Codex (execution steps below)
**Prerequisite (User — do this BEFORE handing this file to Codex):**
1. Confirm Task 001 has been completed and verified (folder structure, venv, `.gitignore` all working — see Task 001's testing steps if unsure).
2. Confirm the three data files are sitting in `data/` locally:
   - `cross_border_payments.xlsx`
   - `trade_finance.xlsx`
   - `transactional_banking.xlsx`
   (adjust exact filenames below if yours differ slightly — check before running)
3. Confirm the `__MACOSX` folder is still present in `data/` (it's leftover zip-extraction junk, not real data) — Codex will remove it as part of this task, you don't need to do this manually.
4. This task does not require your teammate's data dictionary to exist yet — Codex will do its own first-pass schema/quality inspection independently. If/when your teammate's dictionary is ready, it can be reconciled against this task's output afterward, but isn't a blocker.

---

## Why?

Every downstream phase — sector grouping, financial research tiering, wallet estimation, gap ranking — depends on one thing existing first: a clean, reliable picture of what Syn Bank's internal data says each client is currently doing across the three product pillars (Transactional Banking, Cross-Border/FX, Trade Finance).

This phase also produces something the *next* phase needs directly: a **ranked table of clients by total captured activity**, which is how Phase 3 decides which ~15–20 clients get the deep-dive "Tier 1" financial research treatment versus the lighter "Tier 2" treatment. Getting the aggregation logic right here avoids compounding errors through every later phase.

One technical wrinkle worth calling out: `transactional_banking.xlsx` is ~383MB with ~1 million rows. Reading that repeatedly with `pandas.read_excel()` on every run would be slow and painful during development — this task converts it to a faster format once, up front.

---

## Steps for Codex

### 1. Clean up `data/`
- Delete the `__MACOSX` folder and its contents entirely — this is macOS zip-extraction metadata, not real data, and will break any code that tries to iterate over "all files in `data/`".
- Confirm the three expected files remain: `cross_border_payments.xlsx`, `trade_finance.xlsx`, `transactional_banking.xlsx`. If any filename differs from this, note the actual name found and use it consistently throughout.

### 2. Add `openpyxl` to `requirements.txt`
`pandas.read_excel()` needs this to read `.xlsx` files — it isn't in the current `requirements.txt` from Task 001. Add it, then re-run `pip install -r requirements.txt` (this task's testing section will double check this installs cleanly).

### 3. Convert to a faster format (one-time, cached)
Write a small script `src/convert_raw_data.py` that:
- Reads each of the three `.xlsx` files once
- Writes each out as a Parquet file into `data/processed/` (e.g. `data/processed/transactional_banking.parquet`), preserving all columns and dtypes
- Skips re-conversion if the Parquet file already exists and is newer than the source `.xlsx` (so this doesn't waste minutes every time it's re-run during development)
- Add `data/processed/` to `.gitignore` as well — it's still derived from confidential data and must never be committed, same as `data/` itself

All subsequent scripts in this project should read from `data/processed/*.parquet`, not the raw `.xlsx` files directly — parquet loads are dramatically faster, especially for the 1M-row file.

### 4. Build the schema/quality inspection pass
In `src/ingest.py`, write a function that, for each of the three datasets, reports:
- Row count, column list, and dtypes
- Null/missing value counts per column
- Number of unique `entity_id` values (should be 50, or close to it — flag if not)
- Date range covered (min/max of the `date` column)
- Any obviously malformed rows (e.g. negative values in a column that should always be positive, dates outside a sane range, duplicate `transaction_id`/`instrument_id`)

Print this as a readable summary when the script is run — this becomes your first-pass data profiling, standing in for the teammate's data dictionary until/unless it exists.

### 5. Build the per-client aggregation
This is the core output of this phase. In `src/ingest.py` (or a new `src/aggregate.py`), produce a single table with one row per client (`entity_id`, `entity_name`, `sector`), and the following columns:

- **Cross-border/FX activity captured**: sum of `value_zar` from `cross_border_payments`, grouped by `entity_id` (consider whether `direction` should be summed separately or netted — use absolute value summed by default unless there's a clear reason not to, and note the choice made)
- **Trade finance activity captured**: sum of `value_zar` from `trade_finance`, grouped by `entity_id`
- **Transactional banking activity captured**: sum of `amount_zar` from `transactional_banking`, grouped by `entity_id`
- **Total captured activity**: sum of the three pillar columns above

Handle the join carefully: some clients may not appear in all three datasets (e.g. a client with no trade finance activity at all) — these should show `0`, not be dropped or produce `NaN`.

### 6. Produce the ranked output Phase 3 needs
Sort the per-client aggregation table by **Total captured activity**, descending. Save this as `outputs/client_activity_ranking.csv`. This is a direct input to Phase 3's Tier 1/Tier 2 split — don't skip saving it even though this task doesn't use it further itself.

### 7. Update the README
Per the standing instruction already in `README.md`: tick Phase 2's subtask checkboxes, flip Phase 2's status in the Build Phases summary table to ✅ Done once this task's testing has been confirmed passing by the user, and append a dated entry to the Progress Log describing what was built (mention the parquet conversion and the ranking output specifically, since those are new artifacts other phases depend on).

### 8. Commit
Commit the new `src/` files, the `.gitignore` update, and `requirements.txt` update. Do **not** commit anything under `data/` or `data/processed/` — confirm `git status` is clean of both before committing (see Testing section, this is critical).

---

## Testing Instructions (for you, the User — verify before moving to Task 003)

1. **Cleanup check**: confirm `data/__MACOSX` no longer exists, and the three source `.xlsx` files are still present and untouched.
2. **Install check**: run `pip install -r requirements.txt` and confirm `openpyxl` installs without error.
3. **Conversion check**: run `python src/convert_raw_data.py` and confirm three `.parquet` files appear in `data/processed/`. Run it a second time immediately after — it should skip re-conversion and finish near-instantly the second time (confirming the "skip if already converted" logic works).
4. **Profiling output check**: run the schema/quality inspection script and read through the printed summary for all three datasets. Sanity-check by eye:
   - Does the number of unique `entity_id` values look right (~50)?
   - Do the null-value counts make sense (e.g. `memo` might legitimately have nulls, but `value_zar` shouldn't)?
   - Does the date range look plausible (not decades in the future/past)?
5. **Aggregation check**: open `outputs/client_activity_ranking.csv` and confirm:
   - Exactly one row per unique client (no duplicates)
   - No negative totals
   - The top few rows (highest activity) are clients you'd intuitively expect to be large/active, and this ranking will directly become your Tier 1 list next phase — so worth a genuine sanity look, not just a mechanical check
   - Spot-check one client by hand: pick one `entity_id`, manually filter/sum its transactions in Excel across all three source files, and confirm it matches the script's output for that client
6. **Gitignore check — repeat this, it matters even more now**: run `git status` and confirm neither `data/` contents nor `data/processed/` contents show up as trackable. Only code files should appear.

### If something breaks (debugging steps)
- If `pandas.read_excel()` fails or hangs on `transactional_banking.xlsx`: confirm `openpyxl` actually installed (check `pip show openpyxl`), and confirm you're not accidentally trying to load it without the parquet conversion step — loading the raw xlsx repeatedly is expected to be slow, that's exactly why Step 3 exists.
- If unique `entity_id` count isn't ~50: check whether the same client appears under slightly different `entity_id` formatting (e.g. leading zeros, whitespace) across the three files — this is a common real-world data issue and would need a normalization step before aggregating.
- If the per-client totals don't match your manual spot-check: check whether `direction` (debit/credit) is being handled consistently — this is the most likely source of a mismatch, since summing signed values vs absolute values gives different totals.
- If Parquet writing fails: confirm `pyarrow` or `fastparquet` is available (add `pyarrow` to `requirements.txt` if pandas complains about a missing engine).

---

## Next Task
Once all testing checks above pass, move to **Task 003 — Client Sector Grouping & Research Tiering**.
