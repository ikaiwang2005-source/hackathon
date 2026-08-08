# Syn Bank Share of Wallet Intelligence Engine

**Standard Bank x Stellenbosch University Data Science Hackathon — 2026**

An intelligence engine that estimates how much of a corporate client's total banking
business Syn Bank actually captures — and where the biggest revenue opportunities are
hiding in the gap.

---

## The Problem

Syn Bank is a fictional South African corporate and investment bank with 50 JSE-listed
clients across mining, retail, manufacturing, financial services, consumer goods, and
infrastructure. It is not — and never is — the sole bank for any of them. Corporate
clients spread their banking activity across multiple providers for reasons ranging
from risk management to pricing tension to product specialisation.

That creates a real commercial blind spot: Syn Bank can see exactly what happens on
its own books, but it has no direct visibility into how much banking business a client
is doing *elsewhere*. Without that, a relationship banker has no way to know whether a
client is fully served or whether a competitor is quietly capturing millions in trade
finance, FX, or lending business that Syn Bank should be pitching for.

This project builds that visibility.

## What This Project Does

For each of the 50 clients, we answer three questions:

1. **What is this client's total banking wallet?** — estimated from the client's
   public financial profile (revenue, foreign exposure, debt, trade activity), because
   a company's financial shape implies roughly how much banking activity it should be
   generating across all providers, not just Syn Bank.
2. **How much of that wallet does Syn Bank currently capture?** — measured directly
   from Syn Bank's internal transaction, SWIFT, and trade finance data.
3. **Where's the gap, and how big is it?** — the difference between estimated total
   wallet and Syn Bank's captured share, broken down by product pillar (Transactional
   Banking, Global Markets, Investment Banking), is the opportunity. We rank these
   gaps across all 50 clients to surface where a coverage banker should focus next.

A GenAI layer then turns those ranked, structured results into plain-English client
briefings — the kind of one-page note a banker could actually bring into a client
meeting, rather than a spreadsheet of numbers.

## Team

| Name | Background |
|---|---|
| [Your Name] | Mechatronic Engineering |
| [Teammate Name] | Electrical Engineering |

Neither of us came into this with a finance background. The approach below was
deliberately chosen to lean on transparent, defensible logic rather than deep domain
modelling — every estimate traces back to a clear, statable assumption.

## The Process

**Starting point.** The brief hands you most of the methodology if you read it
closely: financial statement signals map to banking needs in fairly intuitive ways —
inventory and cost of sales imply trade finance needs, foreign revenue implies FX
hedging demand, debt schedules imply lending or capital markets opportunity. The
project is really an exercise in turning that mapping into a consistent, repeatable
pipeline across 50 clients, rather than inventing a new banking model from scratch.

**Design decisions along the way:**
- We chose **sector-and-size clustering with benchmark ratios** over a full regression
  model. It's easier to defend to judges ("this client is priced like other mining
  companies of similar size, based on real JSE comparables") than a black-box
  prediction, and it fit a ~9-day build timeline for a two-person team.
- We chose to **benchmark against real JSE-listed companies' public financials**
  rather than invented numbers, so the sector ratios driving our wallet estimates are
  grounded in something real, even though Syn Bank's own client list is fictional.
- We chose **Streamlit** over other dashboard options (Grafana was considered and
  ruled out — it's built for infrastructure/time-series monitoring, not this kind of
  business drill-down dashboard) because it's fast to build in pure Python and
  deploys free to a public URL, which also satisfies the hackathon's "link to code"
  and "reproducible environment" requirements in one step.
- We chose the **Gemini API** for the GenAI layer for its free tier, keeping the
  project reproducible for anyone re-running it without needing a paid key.
- Confidential Syn Bank data was **never committed to git** — it lives in a local,
  gitignored `data/` folder throughout the build, per the hackathon's confidentiality
  rules.

## Build Phases

Quick-reference summary — see the detailed breakdown below for subtasks, who owns what, and the checkpoint at the end of each phase.

| Phase | Description | Status |
|---|---|---|
| 1 | Project scaffolding — repo structure, venv, `.gitignore`, environment setup | ✅ Done |
| 2 | Data ingestion & profiling — load and aggregate Syn Bank's internal datasets | 🟨 In progress |
| 3 | Client sector grouping & research tiering — group by known sector, split clients into Tier 1/Tier 2 by activity | ⬜ Not started |
| 4 | Real financial data sourcing — LLM-extracted financials for Tier 1, lightweight revenue lookup for Tier 2 | ⬜ Not started |
| 5 | Wallet estimation — apply sector ratios to estimate each client's total banking wallet | ⬜ Not started |
| 6 | Share-of-wallet & gap calculation — compare estimated wallet to Syn Bank's captured activity, rank opportunities | ⬜ Not started |
| 7 | GenAI briefing generator — turn ranked results into banker-readable client briefings | ⬜ Not started |
| 8 | Streamlit dashboard — portfolio view, client drill-down, opportunity heatmap, briefing panel | ⬜ Not started |
| 9 | Deployment & submission packaging — public dashboard link, 1-page PDF summary, presentation deck | ⬜ Not started |
| 10 (stretch) | Engagement timing signals — flag clients with upcoming debt maturities or trade finance expiries as near-term opportunities | ⬜ Not started |

### Ownership model

This is a two-person team. One of us (Mechatronic Engineering) is carrying most of the
core pipeline and code; the Electrical Engineering teammate is delegated well-scoped,
self-contained tasks each phase that don't require deep coding — research, data
review, QA, and content work. Each phase below states who owns what.

---

### Phase 1 — Project scaffolding ✅

**Owner:** You (core build)

- [x] Repo structure (`data/`, `notebooks/`, `src/`, `dashboard/`, `docs/tasks/`, `outputs/`)
- [x] `.gitignore` protecting confidential CSVs
- [x] `requirements.txt`, `.env.example`
- [x] README created

**✅ Checkpoint 1 — passed.** Folder structure verified, venv installs cleanly, `.gitignore`
confirmed to hide a real CSV from `git status`, README renders correctly on GitHub.

---

### Phase 2 — Data ingestion & profiling

**Owner:** You (pipeline code)
**Teammate task:** Read through the three provided datasets (transactional ledger,
SWIFT payments, trade finance) and produce a short **data dictionary** — one page
listing every column, what it means, and any oddities noticed (missing values, odd
formats, inconsistent client naming). This doesn't require code; it can be done by
opening the CSVs in Excel/Google Sheets and documenting what's there. This dictionary
directly feeds the ingestion code and saves back-and-forth later.

Subtasks:
- [x] Load all three internal datasets, validate schema against the brief
- [x] Handle missing/malformed rows
- [x] Aggregate per-client, per-pillar "activity currently captured by Syn Bank"
- [x] Add client spot-check and dataset coverage verification script
- [ ] Teammate's data dictionary reviewed and merged into `docs/`

**🔲 Checkpoint 2 — Data ingestion**
- Run the ingestion script end-to-end without errors
- Print/inspect the aggregated per-client table — confirm all 50 clients appear, no
  duplicate client IDs, totals per pillar look sane (no negative sums, no impossible
  outliers)
- Confirm the data dictionary matches what the code actually parses (column names,
  types) — mismatches here are a common source of silent bugs later

---

### Phase 3 — Client sector grouping & research tiering

**Owner:** You (code)
**Teammate task:** None required for this phase — light enough to do solo now that
sector is a known field rather than something to infer.

> **Design note:** the 50 clients turned out to be real, named companies (e.g.
> Pepkor, MTN, NEPI) with `sector` already provided as a column in the raw data.
> This replaces the originally-planned clustering algorithm — no need to infer
> sector/size groupings statistically when sector is already known directly.

Subtasks:
- [ ] Group the 50 clients by their existing `sector` field, sanity-check group
      sizes (flag any sector with only 1 client — can't be benchmarked against peers)
- [ ] Using Phase 2's per-client captured-activity totals, rank all 50 clients and
      split into **Tier 1** (~top 15–20 by captured activity — get full individually-
      sourced financials in Phase 4) and **Tier 2** (remaining ~30 — get a lighter
      research treatment)

**🔲 Checkpoint 3 — Sector grouping & tiering**
- Confirm every client has exactly one sector assigned and every sector group has
  at least 2 members
- Confirm the Tier 1 / Tier 2 split list looks right — the highest-activity clients
  in Phase 2's output should be the ones in Tier 1

---

### Phase 4 — Real financial data sourcing (tiered, LLM-assisted)

**Owner:** Split — see tier breakdown below. This phase pivoted from the original
"comparable company" approach: since clients are real companies, we source each
one's *own* real public financials rather than a proxy peer's.

> **Important framing for the writeup and all deliverables:** these are real
> companies, but the banking activity data attached to them in this project is
> entirely synthetic. Every deliverable (dashboard, PDF, PPTX) must carry a clear
> disclaimer that the banking figures shown do not represent any actual relationship
> these real companies have with any bank — see the Data Confidentiality section.

**Tier 1 (~15–20 clients) — full LLM extraction:**
- **Teammate task:** For each Tier 1 client, find their most recent annual report or
  investor-relations financial summary (JSE SENS, company IR page) and save the
  source (PDF or page text) into `data/research/tier1/`.
- **Your task:** Build an LLM extraction step (Gemini) that takes each saved
  report/page and extracts structured fields: revenue, COGS, foreign revenue %, and
  debt schedule (upcoming maturities — this also feeds Phase 10's timing signals).
  Always keep the source citation alongside the extracted numbers.

**Tier 2 (~30 clients) — lightweight, revenue-only:**
- **Teammate task:** For each Tier 2 client, find just their most recent reported
  revenue figure from a quick public source (market summary/profile page) — no full
  report needed. Record in a simple spreadsheet with source.
- **Your task:** Apply Tier 1's derived sector ratios (see Phase 5) to each Tier 2
  client's real revenue to estimate their other financial inputs.

Subtasks:
- [ ] Tier 1 sources collected (teammate)
- [ ] LLM extraction pipeline built and run on Tier 1 (you)
- [ ] Tier 2 revenue figures collected (teammate)
- [ ] Sector-typical ratios derived from Tier 1 data, ready to apply to Tier 2 (you)

**🔲 Checkpoint 4 — Financial data sourcing**
- Confirm every Tier 1 client has extracted revenue, COGS, foreign revenue %, and
  debt data, each traceable to a cited source
- Spot-check 3–5 LLM-extracted values against the source document by hand — this is
  the step most likely to silently produce wrong numbers if the extraction prompt
  is loose, so don't skip this
- Confirm every Tier 2 client has at least a real, sourced revenue figure
- Confirm every sector group has enough Tier 1 members to derive a meaningful ratio
  (at least 2) — if a sector is Tier-2-only, flag it, since there's no ratio to
  extrapolate from and that sector's estimates will be weaker

---

### Phase 5 — Wallet estimation

**Owner:** You (code)
**Teammate task:** None required, but review the output table once produced (see
checkpoint) — a second set of eyes on whether the numbers look commercially sensible
is valuable even without touching the code.

Subtasks:
- [ ] Apply cluster benchmark ratios to each client's own financials
- [ ] Produce total estimated wallet per client, per pillar, as a low/base/high range
- [ ] Compute a **confidence score** per client/pillar estimate: a 0–1 average of
      (a) a normalized score for how many comparable companies backed that cluster's
      benchmark ratio, and (b) a normalized score for how tight the low–high range is
      relative to the base estimate. More comparables + a tighter range = higher
      confidence. This feeds the priority ranking in Phase 6.

**🔲 Checkpoint 5 — Wallet estimation**
- For 3–5 clients, manually recompute the wallet estimate by hand from the ratios and
  the client's financials — confirm it matches the code's output exactly
- Confirm no client has an implausible wallet size (e.g. wallet smaller than what
  Syn Bank alone already captures, which would be a contradiction)
- Confirm confidence scores fall between 0–1 and that a cluster with only 2
  comparables and a wide range scores visibly lower than one with 4+ comparables and
  a tight range — spot-check by hand on two contrasting clusters

---

### Phase 6 — Share-of-wallet, gap & priority ranking

**Owner:** You (code)
**Teammate task:** Once the ranked opportunity list exists, review the top 10 and
bottom 10 clients and write a one-paragraph plain-English note on whether the ranking
"makes sense" commercially — this feeds directly into the presentation narrative later.

Subtasks:
- [ ] Compare estimated wallet (Phase 5) vs Syn Bank's captured activity (Phase 2)
- [ ] Calculate share % and R-value gap per client, per pillar
- [ ] Compute **priority score = gap × confidence** (confidence from Phase 5) per
      client/pillar — this reframes ranking from "biggest raw gap" to "biggest gap we
      can actually be confident about," which is closer to how a banker would
      realistically triage a pipeline
- [ ] Rank all clients/pillars by priority score (keep raw gap-only ranking
      available too, for comparison in the writeup)

**🔲 Checkpoint 6 — Share-of-wallet, gap & priority**
- Confirm share % is between 0–100% for every client/pillar (a value outside that
  range means an upstream calculation error)
- Confirm the ranked opportunity list is sorted correctly and R-values sum sensibly
  back to the totals from Phase 5
- Compare the priority-score ranking against the raw-gap ranking — confirm at least
  a few clients meaningfully swap positions (if the rankings are identical, the
  confidence score isn't actually influencing anything, which means Phase 5's
  scoring needs revisiting)

---

### Phase 7 — GenAI briefing generator

**Owner:** You (integration/code)
**Teammate task:** Review generated briefings for at least 5 clients and edit for
tone/clarity — does it actually read like something a banker would want to bring into
a meeting? This is a genuinely important task and doesn't require touching the API
integration itself.

Subtasks:
- [ ] Gemini API integration, structured client data in → briefing paragraph out
- [ ] Generate briefings for at least 3 clients (brief's minimum), ideally all 50
- [ ] Teammate's tone/clarity pass on a sample completed

**🔲 Checkpoint 7 — GenAI briefings**
- Generate briefings for 3+ clients and read them end-to-end — confirm no
  hallucinated numbers (every figure in the briefing must trace back to the
  structured data that was fed in, not invented by the model)
- Confirm the API key is being read from `.env` and not hardcoded anywhere before
  any commit

---

### Phase 8 — Streamlit dashboard

**Owner:** You (build)
**Teammate task:** Act as first-pass QA — click through every view (portfolio,
client drill-down, heatmap, briefing panel) on their own machine after pulling the
latest code, and log anything confusing, broken, or unclear from a first-time user's
perspective.

Subtasks:
- [ ] Portfolio-level summary view
- [ ] Client drill-down view
- [ ] Opportunity heatmap
- [ ] AI briefing panel
- [ ] Teammate's QA pass completed and issues logged

**🔲 Checkpoint 8 — Dashboard**
- Run `streamlit run dashboard/app.py` locally and click through all four views
- Confirm the dashboard doesn't crash on any of the 50 clients (test a few, not just
  the first one)
- Teammate confirms the dashboard is usable without needing the code explained to
  them — if they're confused, a judge will be too

---

### Phase 9 — Deployment & submission packaging

**Owner:** Shared
**Teammate task:** Draft the 1-page PDF solution summary and a first pass of the
PPTX slide content (problem, approach, GenAI component, results, next steps) — this
is storytelling work, not code, and plays to complementary strengths.
**Your task:** Deploy the dashboard to Streamlit Community Cloud, final repo cleanup,
final README pass.

Subtasks:
- [ ] Deploy dashboard, confirm public link works
- [ ] 1-page PDF solution summary drafted and finalised
- [ ] PPTX presentation drafted and finalised
- [ ] Final repo review — no confidential data committed, README fully up to date
- [ ] Submission form completed with team name, members, and links

**🔲 Checkpoint 9 — Final submission**
- Open the deployed Streamlit link in an incognito/private browser window (simulates
  a judge with no prior access) — confirm it loads and works
- Re-clone the repo fresh into a new folder and run the Setup steps from scratch —
  confirm it works with zero manual fixes, since this is exactly what judges will do
- Confirm the PDF is genuinely one page and the PPTX covers all five required
  sections (problem, data/methodology, GenAI integration, findings, limitations/next
  steps)
- Double-check `git log` and `git status` one final time for any accidentally
  committed data files before submitting

---

### Phase 10 (stretch) — Engagement timing signals

**Owner:** You (code), teammate reviews output
**Note:** This is explicitly optional. The brief calls out timing/engagement signals
as a bonus area most teams won't attempt — do this only after Phases 1–9 are solid
and submission-ready. Cut without hesitation if the deadline is close.

This does **not** involve scanning real news or SENS filings — the 50 clients are
fictional, so there's nothing real to scan. It's a rules-based flag built entirely
from data already ingested in Phase 2:

Subtasks:
- [ ] Flag any client with a debt maturity falling within the next 12 months
      (from the financial statement debt schedule data) as a "refinancing
      conversation" opportunity
- [ ] Flag any client with a trade finance facility (LC/guarantee) nearing its
      tenor/expiry date (from the trade finance dataset) as a "renewal conversation"
      opportunity
- [ ] Surface both flag types in the dashboard (Phase 8) and mention them in the
      GenAI briefing (Phase 7) where relevant, e.g. "recommend engaging now — X's
      trade finance facility expires in 6 weeks"

**🔲 Checkpoint 10 — Timing signals**
- Confirm flagged clients actually have the underlying data condition true (spot
  check 3–5 by hand against the raw debt/trade finance data)
- Confirm the dashboard and any briefings mentioning a timing flag state the actual
  date/timeframe, not a vague "soon" — specificity is what makes this credible to a
  judge

## Tech Stack

- **Python** (venv + pip) for the full pipeline
- **pandas / scikit-learn** for data processing and clustering
- **Streamlit + Plotly** for the interactive dashboard
- **Google Gemini API** for the GenAI briefing generator
- **Streamlit Community Cloud** for deployment

## Project Structure

```
data/         # raw CSVs (gitignored, local only — confidential, never committed)
notebooks/    # exploratory + final reproducible analysis notebook
src/          # reusable modules: ingestion, clustering, wallet_calc, genai
dashboard/    # Streamlit app
docs/tasks/   # archive of every task spec used to build this project
outputs/      # generated charts, briefings, submission drafts
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then add your real GEMINI_API_KEY
```

## Data Confidentiality

All Syn Bank datasets are synthetic, fictional, and provided solely for this
hackathon, but are treated as confidential throughout this project. Raw data files
are never committed to this repository — see `.gitignore`.

**Real company names, fictional banking data.** The 50 clients in this dataset are
named after real, publicly-listed companies (e.g. Pepkor, MTN, NEPI). Their sector
and publicly-available financial figures (revenue, debt, etc., sourced in Phase 4)
are real. **All banking transaction, SWIFT, and trade finance activity attributed to
them in this project is entirely synthetic** and does not represent any actual
banking relationship these companies have with any real bank. Every deliverable
(dashboard, PDF summary, presentation) must display this disclaimer clearly — this
is not optional, since presenting fictional banking figures against real company
names without a clear disclaimer risks being misread as real information.

## Evaluation Alignment

This project is built with the hackathon's judging weights directly in mind:

- **Business Insight & Commercial Acumen (40%)** — the entire pipeline is oriented
  around producing a ranked, R-denominated opportunity list a banker could act on,
  not just a model output. Ranking by priority score (gap × confidence) rather than
  raw gap size mirrors how a banker would realistically triage a pipeline, and the
  optional timing-signal flags (Phase 10) point to *when* to engage, not just *who*.
- **Analytical Rigor (30%)** — clustering and benchmark ratios are grounded in real
  comparable company financials, with assumptions stated explicitly rather than
  buried in code. Every wallet estimate carries an explicit confidence score, so the
  output never overstates certainty it doesn't have.
- **Gen AI Application (20%)** — the GenAI layer narrates already-computed insights
  into a usable briefing, rather than serving as a cosmetic add-on.
- **Presentation & Storytelling (10%)** — the Streamlit dashboard and this README are
  both built to make the logic easy to follow for a non-technical audience.

## Submission Deadline

Sunday, 16 August 2026, 23:59.

## Progress Log

- **[today's date]** — Project planning complete. Approach, tech stack, and 9-phase
  build plan finalised. Repository not yet created.
- **2026-08-08** - Built Task 002 ingestion/profiling: raw CSVs convert to local
  Parquet caches, profiling flags 20 unique clients plus duplicate IDs for review,
  and `outputs/client_activity_ranking.csv` is generated for Phase 3 tiering.
- **2026-08-08** - Added a client spot-check and coverage verification script for
  validating ranking totals and investigating per-dataset client absence.
