# QSI Research Import (review branch only)

This directory is a **research staging area**, not a production or sellable strategy catalog.

- Historical QSI-056..080 records were transcribed from prior daily reports in the conversation; the full QSI-001..055 archive is unavailable.
- `index.json` is **PROVISIONAL**, and null AUM/performance means not verified, not zero.
- QSI-060 is related to the pre-existing `strategy_index.yaml` ETF Mispricing Arbitrage entry. Review before accepting as distinct.
- Existing root files and `strategy_index.yaml` were not modified.
- The supplied Python file is a five-function numerical research primitive, **not** an IPCA training engine, backtest, trade executor or validated alpha.
- Daily automation should compare both IDs and mechanism keys against this index **and** the legacy strategy index, then create a new dated branch, never push to main or auto-merge.
- Review scholarly links, GitHub repository licenses, point-in-time data and transaction costs before commercialization.

## Workflow

1. Generate 5 new distinct candidate records with paper links and provenance.
2. Read `qsi/index.json` and `strategy_index.yaml`; reject duplicate ID/mechanism and flag conceptual overlap.
3. Create `qsi/daily/YYYY-MM-DD.md`, an index delta, and research-only Python code with synthetic tests.
4. Commit only to a new `qsi/daily-YYYY-MM-DD` branch and optionally open a **draft** PR.
5. Never modify the default branch, deploy, trade, or publish commercial products without separate approval.
