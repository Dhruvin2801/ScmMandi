"""ColdLens — landing page."""

import plotly.graph_objects as go
import streamlit as st

from lib import C, PLOTLY_LAYOUT, caption, kpi, load, masthead, note, setup, sidebar_footer

setup("Home")
sidebar_footer()

masthead(
    "ColdLens",
    "Where cold-chain capacity pays, when moving produce is worth it, and how much "
    "of the price signal actually reaches the farmer — built on 1.42 million official "
    "market-day records across six southern states.",
)

d = load("districts")
c = load("corridors")
band = load("emissions_band")

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi("Annual post-harvest loss", "Rs 8,860 cr", "Observed volumes at observed prices")
with k2:
    kpi("Districts robustly viable", "22", "of 84, under every plausible assumption")
with k3:
    kpi("Reliable trade corridors", "11", "of 46, profitable in 80%+ of months")
with k4:
    kpi("Emissions in lost food", "795k t CO₂e", "95% from growing, not moving")

st.markdown("## The argument in one page")

note(
    "India is usually said to lack cold storage. It has roughly 8,815 facilities holding "
    "about 402 lakh metric tonnes, and around 70% of that serves potato alone. The gap is "
    "one of <b>allocation</b>, not of aggregate volume — and alongside it sits an "
    "information problem that no amount of concrete will fix."
)

left, right = st.columns([1, 1])

with left:
    st.markdown("### Cold-chain viability follows crop mix")
    det = load("districts_det")
    fig = go.Figure()
    for viable, colour, name in [
        (True, C["primary"], "Viable"),
        (False, C["danger"], "Not viable"),
    ]:
        s = det[det.viable == viable]
        fig.add_trace(
            go.Scatter(
                x=s.perish_pct,
                y=s.npv_lakh / 100,
                mode="markers",
                name=name,
                marker=dict(size=8, color=colour, opacity=0.8),
                hovertemplate="%{customdata[0]}<br>Perishable %{x:.1f}%"
                "<br>NPV Rs %{y:,.0f} cr<extra></extra>",
                customdata=s[["district"]].values,
            )
        )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=330,
        xaxis_title="Perishable share of district volume (%)",
        yaxis_title="NPV (Rs crore)",
    )
    st.plotly_chart(fig, use_container_width=True)
    caption(
        "Every district that fails does so for one reason: near-zero perishable volume. "
        "A paddy-and-cotton district has nothing for a cold store to preserve."
    )

with right:
    st.markdown("### Emissions come from growing, not moving")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=["Embedded emissions"],
            x=[759091],
            orientation="h",
            name="Production (95.4%)",
            marker_color=C["primary"],
        )
    )
    fig.add_trace(
        go.Bar(
            y=["Embedded emissions"],
            x=[36236],
            orientation="h",
            name="Transport (4.6%)",
            marker_color=C["range"],
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT, height=330, barmode="stack", xaxis_title="tonnes CO₂e per year"
    )
    st.plotly_chart(fig, use_container_width=True)
    caption(
        f"Central estimate {band.total.iloc[1]:,.0f} t CO₂e/yr "
        f"(range {band.total.iloc[0]:,.0f}–{band.total.iloc[2]:,.0f}). "
        "Preventing spoilage is roughly twenty times the lever that re-routing is."
    )

st.markdown("## Five findings")

findings = [
    (
        "Loss is concentrated, not uniform",
        "Rs 8,860 crore a year across six states, heavily weighted toward a few "
        "perishable commodities and a few high-volume districts. A targeted "
        "intervention is both cheaper and more effective than a uniform one.",
    ),
    (
        "Viability tracks crop mix, not district size",
        "Of 84 districts, 22 are viable under every plausible assumption and 17 under "
        "none. The 17 failures all share a perishable share of essentially zero.",
    ),
    (
        "Markets are connected, but slowly",
        "Between 77% and 94% of perishable market pairs share a long-run price "
        "equilibrium — but shocks take 3–5 days to travel. For a crop that spoils in "
        "days, that information arrives after the decision has been forced.",
    ),
    (
        "Movement pays over short distances only",
        "Corridor viability falls from about 42% under 400 km to a quarter or less "
        "beyond 700 km, once freight is charged at the correct rate for the crop and "
        "transit spoilage is costed.",
    ),
    (
        "Glut months punish those who cannot wait",
        "Semi-perishables lose 13.3% against their annual average when supply peaks; "
        "storables lose 2.1%. An administered floor price shields the paddy grower in "
        "exactly the months the onion grower has no protection.",
    ),
]
for i, (head, body) in enumerate(findings, 1):
    st.markdown(
        f'<div class="card"><b>{i}. {head}</b>'
        f'<div style="color:{C["muted"]};font-size:.9rem;margin-top:.35rem;'
        f'line-height:1.55">{body}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("## What is on this site")
nav = [
    ("Market Explorer", "Prices, arrivals and reporting quality by state and commodity."),
    ("Cold-Chain Siting", "District-level viability with probabilities, not flags."),
    ("Trade Corridors", "Which routes pay, how reliably, and what the bad month looks like."),
    ("Market Integration", "Cointegration, transmission lag and variance amplification."),
    ("Sustainability", "Emissions embedded in lost produce, quantified with a range."),
    ("Simulator", "Run the investment and corridor models on your own numbers."),
    ("Data & Method", "Sources, validity flags, assumptions and what is not claimed."),
]
cols = st.columns(2)
for i, (name, desc) in enumerate(nav):
    with cols[i % 2]:
        st.markdown(
            f'<div class="card"><b>{name}</b>'
            f'<div style="color:{C["muted"]};font-size:.85rem;margin-top:.25rem">{desc}</div></div>',
            unsafe_allow_html=True,
        )

note(
    "Observed data, model estimates and your own assumptions are kept separate throughout. "
    "Every figure traces to a documented source, and the limits of the data are stated "
    "on the Data &amp; Method page rather than left implicit.",
)
