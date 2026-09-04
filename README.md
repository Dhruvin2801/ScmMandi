# ColdLens

Post-harvest supply chain decision support for Indian agricultural markets.

Where cold-chain capacity pays, when moving produce between markets is worth it, and how
much of the price signal actually reaches the farmer — built on 1,421,838 official
AGMARKNET market-day records across six southern states, July 2024 to July 2026.

## Run locally

```bash
pip install -r requirements.txt
streamlit run Home.py
```

Opens at `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Push this folder to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Select the repository, set the main file to `Home.py`, and deploy.

No secrets or environment variables are needed. All data ships with the repo
(about 750 KB) so there is nothing to fetch at runtime.

## Pages

| Page | What it does |
|---|---|
| Home | Headline findings and the argument in one page |
| Market Explorer | Prices, arrivals and reporting quality by state and commodity |
| Cold-Chain Siting | District viability as a probability, not a flag |
| Trade Corridors | Which routes pay, how reliably, and what a bad month looks like |
| Market Integration | Cointegration, transmission lag, variance amplification, glut pricing |
| Sustainability | Emissions embedded in lost produce, quantified with a range |
| Simulator | Run both models on your own assumptions, with Monte Carlo |
| Data & Method | Sources, validity flags, assumptions, and what is not claimed |

## Method in brief

- **Census, not sample.** Every qualifying record in the period, so no sampling error.
- **Flags, not deletions.** Records that fail a validity test are flagged and filtered
  per analysis, never removed. Coconut and arecanut are excluded from cross-state price
  comparison (whole-nut vs weight basis); Kerala is excluded because it has no APMC Act
  and its reported prices sit near retail rather than wholesale.
- **Varieties matched.** Corridors require the same variety at both ends — banana in
  Kerala is a different product from banana in Maharashtra.
- **Probabilities, not verdicts.** Cold-chain and corridor results come from 10,000-run
  Monte Carlo simulations. Corridor price spreads are resampled from observed monthly
  history rather than assumed.

## Data

| File | Contents |
|---|---|
| `data/master_monthly.csv.gz` | 74,674 market-commodity-month rows with validity flags |
| `data/districts.csv` | Simulated district viability (84 districts) |
| `data/corridors.csv` | Simulated corridor economics (46 corridors) |
| `data/coint.csv`, `granger.csv` | Market integration tests |
| `data/bullwhip.csv`, `glut.csv` | Variance amplification and glut pricing |
| `data/emissions*.csv` | Emissions embedded in lost produce |
| `data/portfolio.csv`, `tornado.csv` | Capital allocation and sensitivity |

## Limitations

Stated in full on the Data & Method page. The most important: loss rates are national
averages applied to regional volumes, and the sensitivity analysis shows this is the
single input the results depend on most. Findings cover six southern states and should
not be quoted as national estimates.

## Licence

MIT for the code. Underlying market data is published by the Government of India;
please observe the terms of the original sources.
