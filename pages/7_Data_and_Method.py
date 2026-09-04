"""Data, method, assumptions and limitations."""

import streamlit as st

from lib import C, caption, kpi, load, masthead, note, setup, sidebar_footer

setup("Data & Method")
sidebar_footer()
masthead(
    "Data & Method",
    "Every source, every assumption, and everything this study does not claim. "
    "Read this before quoting any figure from the site.",
)

m = load("master")
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi("Daily records", "1,421,838", "Jul 2024 – Jul 2026")
with k2:
    kpi("Markets", "2,347", "across 167 districts")
with k3:
    kpi("Commodities", "19", "six southern states")
with k4:
    kpi("Monthly rows", f"{len(m):,}", "market-commodity-month")

st.markdown("## Sources")
st.dataframe(
    {
        "Source": [
            "AGMARKNET (Directorate of Marketing and Inspection)",
            "National Horticulture Board / cold-chain agency",
            "National post-harvest loss study",
            "Commodity price support schedule",
            "Commercial freight rate schedules",
            "Global logistics emissions framework",
            "FAO farm-gate emission intensities",
            "Open meteorological archive",
        ],
        "Contribution": [
            "Daily prices, arrivals, variety and market identity — the primary dataset",
            "Cold storage capacity, facility counts, scheme cost norms",
            "Commodity-wise post-harvest loss percentages",
            "Minimum support prices as the administered benchmark",
            "Full-truck-load rates for dry and refrigerated movement",
            "Emission factors for road freight (0.101 dry, 0.135 refrigerated kg CO₂e/t-km)",
            "Farm-gate emission intensity for paddy and cereals",
            "Rainfall and temperature at market locations",
        ],
    },
    use_container_width=True, hide_index=True,
)

st.markdown("## Validity flags")
note(
    "Raw market data is uneven. Rather than delete inconvenient records, every exclusion is "
    "flagged and filtered per analysis, so it stays visible and reversible. No row was deleted."
)
tot = len(m)
rows = []
for flag, meaning in [
    ("price_basis_comparable", "Price quoted on a comparable physical basis"),
    ("valid_for_value", "Usable for volume-times-price valuation"),
    ("institution_comparable", "Market institution comparable across states"),
]:
    if flag in m.columns:
        passing = int(m[flag].sum())
        rows.append({"Flag": flag, "Meaning": meaning, "Rows passing": f"{passing:,}",
                     "Rows flagged": f"{tot-passing:,}", "% passing": f"{100*passing/tot:.1f}%"})
st.dataframe(rows, use_container_width=True, hide_index=True)

st.markdown("### Why Kerala is excluded from cross-state comparison")
note(
    "Kerala — along with Jammu &amp; Kashmir and Manipur — never enacted a state agricultural "
    "produce marketing law. It has no regulated mandi system; produce is marketed through private "
    "collection shops near producing centres and through a state horticulture council. Prices "
    "reported from those outlets sit close to retail rather than at wholesale auction level.",
    warn=True,
)
st.dataframe(
    {"Commodity": ["Tomato", "Onion", "Potato"],
     "Karnataka (APMC wholesale)": ["Rs 15.37/kg", "Rs 19.66/kg", "Rs 19.46/kg"],
     "Kerala (collection shop)": ["Rs 42.82/kg", "Rs 36.99/kg", "Rs 38.61/kg"],
     "Ratio": ["2.8×", "1.9×", "2.0×"]},
    use_container_width=True, hide_index=True,
)
caption("A two- to three-fold gap between neighbouring states is not arbitrage; it is a difference in what is being priced. Kerala remains fully included in within-state and volume analysis.")

st.markdown("### Why varieties are matched")
note(
    "Corridor analysis initially compared commodity prices across states without controlling for "
    "variety, producing apparent banana gaps near Rs 39/kg. Banana is Nendra Bale in Kerala, "
    "Besrai in Tamil Nadu, Khandesh in Maharashtra and Elakki Bale in Karnataka — different "
    "products at genuinely different price levels. Corridors now require the same variety at both "
    "ends, with at least twenty observations a month over twelve months."
)

st.markdown("## Key assumptions")
st.dataframe(
    {"Parameter": ["Cold store capital cost", "Cold store operating cost",
                   "Share of loss preventable", "Facility utilisation",
                   "Discount rate / asset life", "Dry freight rate",
                   "Refrigerated freight rate", "Road circuity factor"],
     "Value": ["Rs 8,000/tonne", "Rs 1,400/tonne/yr", "0.60", "0.70",
               "10% over 15 years", "Rs 2.5 / 3.5 / 5.0 per t-km",
               "Rs 3.0 / 4.5 / 6.0 per t-km", "1.25"],
     "Stress-tested": ["6,000–11,000", "1,000–1,900", "0.45–0.75", "no",
                       "no", "yes, as a band", "yes, as a band", "1.15–1.35"]},
    use_container_width=True, hide_index=True,
)
caption("Road distances are modelled as straight-line distance between district headquarters × 1.25 circuity, validated against a published long corridor (1,336 km computed vs 1,270–1,470 km published).")

st.markdown("## What this study does not claim")
st.dataframe(
    {"Quantity": ["Lead time", "Inventory turnover", "Fill rate",
                  "Strict demand-amplification ratio", "Vehicle routing",
                  "Farm yield and production", "Procurement contracts and trader margins"],
     "Why not": ["Market records carry no order timestamps",
                 "Requires stock levels; market data records flow, not stock",
                 "Requires orders placed against orders met; auction data has neither",
                 "Requires order variance across echelons; a related measure is reported instead and labelled as such",
                 "No route, vehicle or consignment data",
                 "The study begins at the mandi gate by design",
                 "Not disclosed in public market data"]},
    use_container_width=True, hide_index=True,
)

st.markdown("## Known limitations")
for lim in [
    "Loss rates are national averages applied to regional volumes. District-level rates are not published by any source — and the sensitivity analysis shows this is the single input the results depend on most.",
    "The farmer-share result rests on a comparatively small retail price sample and is indicative rather than precise.",
    "Findings cover six southern states. No figure here should be quoted as a national estimate.",
    "Distances are modelled from straight-line distance and a circuity factor, validated on one long corridor.",
    "The two longest haul-distance bands contain few corridors. The trend direction is reliable; those individual percentages are not.",
    "Simulated probabilities depend on the assumed input distributions, which are documented judgements about uncertainty rather than measurements of it. The corridor simulation is stronger here because its dominant input, the price spread, is resampled from observed history rather than assumed.",
    "A hold-or-sell model was attempted and withdrawn. Three defensible formulations gave materially different answers on the same data; a result that depends that heavily on method choice is not a finding.",
    "Kerala is excluded from cross-state price comparison because its market institution differs, not because its data is wrong. Within Kerala, its prices are valid.",
]:
    st.markdown(
        f'<div class="card" style="padding:.7rem 1rem;font-size:.88rem;color:{C["ink_soft"]}">{lim}</div>',
        unsafe_allow_html=True,
    )

note(
    "This is a post-harvest supply chain decision framework, not a full farm-to-fork study. The "
    "missing blocks — procurement, contracting, reverse logistics, formal forecasting — need data "
    "that mandi records do not hold. They are declared as scope limits rather than filled with "
    "estimates."
)
