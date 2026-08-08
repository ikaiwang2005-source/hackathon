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
| 2 | Data ingestion & profiling — load and aggregate Syn Bank's internal datasets | ⬜ Not started |
| 3 | Client clustering — group the 50 clients by sector and size | ⬜ Not started |
| 4 | Benchmark sourcing — pull real JSE-listed comparable financials, derive sector ratios | ⬜ Not started |
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
- [ ] Load all three internal datasets, validate schema against the brief
- [ ] Handle missing/malformed rows
- [ ] Aggregate per-client, per-pillar "activity currently captured by Syn Bank"
- [ ] Teammate's data dictionary reviewed and merged into `docs/`

**🔲 Checkpoint 2 — Data ingestion**
- Run the ingestion script end-to-end without errors
- Print/inspect the aggregated per-client table — confirm all 50 clients appear, no
  duplicate client IDs, totals per pillar look sane (no negative sums, no impossible
  outliers)
- Confirm the data dictionary matches what the code actually parses (column names,
  types) — mismatches here are a common source of silent bugs later

---

### Phase 3 — Client clustering

**Owner:** You (clustering code)
**Teammate task:** Compile a clean **client reference table** — client ID, name,
sector, and any size indicator (revenue bracket, employee count, etc.) available from
the provided data — into a single tidy sheet. This is manual organisation work, not
coding, and is a direct input to the clustering step.

Subtasks:
- [ ] Teammate's client reference table finalised
- [ ] Cluster the 50 clients by sector + size
- [ ] Sanity-check cluster sizes (avoid clusters of 1, which can't produce a
      meaningful benchmark ratio)

**🔲 Checkpoint 3 — Clustering**
- Print cluster assignments for all 50 clients — manually eyeball a handful per
  cluster to confirm they make intuitive sense (e.g. mining companies aren't
  clustered with retail companies)
- Confirm every cluster has at least 3 members (single-member clusters can't be
  reliably benchmarked)

---

### Phase 4 — Benchmark sourcing

**Owner:** Teammate (primary — this phase is research-heavy and code-light, a good
fit given the workload split)
**Your task:** Build the loader/ratio-calculation code that turns whatever the
teammate collects into usable per-cluster benchmark ratios.

Teammate subtasks:
- [ ] For each cluster, identify 2–3 real JSE-listed companies of similar sector/size
      (annual reports, JSE SENS, company IR pages — sources suggested in the brief)
- [ ] Pull key financials for each: revenue, COGS, foreign revenue %, debt levels
- [ ] Record everything in a shared spreadsheet with sources cited (needed for the
      methodology writeup and to satisfy the brief's citation requirement)

Your subtasks:
- [ ] Derive sector-typical ratios from the teammate's data (fee intensity, trade
      finance intensity, FX hedging ratio, lending ratio) — ideally as a range
      (low/base/high), not a single point value

**🔲 Checkpoint 4 — Benchmarks**
- Confirm every cluster has at least 2 comparable companies with sourced financials
- Spot-check 2–3 derived ratios against publicly known industry norms (e.g. does the
  trade finance intensity for mining look reasonable compared to what's publicly
  reported about SA mining sector banking activity?) — flag anything that looks wildly
  off before it propagates downstream

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
