"""Trade corridors — which routes pay, and how reliably."""

import plotly.graph_objects as go
import streamlit as st

from lib import C, PLOTLY_LAYOUT, caption, kpi, load, masthead, note, setup, sidebar_footer

setup("Trade Corridors")
sidebar_footer()
masthead(
    "Trade Corridors",
    "Whether moving produce between states is worth it, once freight is charged at the "
    "right rate for the crop and transit spoilage is costed. Price spreads are resampled "
    "from observed monthly history, not assumed.",
)

c = load("corridors")
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi("Reliable", f"{int((c.p_profitable >= 80).sum())}", "profitable in ≥80% of months")
with k2:
    kpi("Marginal", f"{int(((c.p_profitable >= 50) & (c.p_profitable < 80)).sum())}", "positive on average only")
with k3:
    kpi("Unreliable", f"{int((c.p_profitable < 50).sum())}", "lose money more often than not")
with k4:
    kpi("Median margin", f"Rs {c[c.p_profitable>=80].net_p50.median():,.0f}/t", "on reliable corridors")

note(
    "A corridor profitable in 55% of months is not a route to build a business on. Separating "
    "the genuinely reliable routes from those with merely a positive average is the whole point "
    "of reporting a probability rather than a single margin."
)

st.sidebar.header("Filters")
minp = st.sidebar.slider("Minimum probability of profit (%)", 0, 100, 0, 5)
sel_type = st.sidebar.multiselect("Crop type", sorted(c.perishability.unique()), default=sorted(c.perishability.unique()))
view = c[(c.p_profitable >= minp) & (c.perishability.isin(sel_type))]

st.markdown("## Risk against return")
fig = go.Figure(go.Scatter(
    x=view.p_profitable, y=view.net_p50, mode="markers",
    marker=dict(
        size=11,
        color=[C["primary"] if p >= 80 else (C["turmeric"] if p >= 50 else C["danger"]) for p in view.p_profitable],
        line=dict(width=0.5, color="white"),
    ),
    text=[f"{r.commodity} · {r.origin} → {r.destination}" for _, r in view.iterrows()],
    customdata=view[["road_km", "net_p05"]].values,
    hovertemplate="%{text}<br>%{customdata[0]:,.0f} km<br>P(profit) %{x:.1f}%"
                  "<br>Median Rs %{y:,.0f}/t<br>Bad month Rs %{customdata[1]:,.0f}/t<extra></extra>",
))
fig.add_vline(x=80, line_dash="dash", line_color=C["ink_soft"], line_width=1)
fig.add_vline(x=50, line_dash="dot", line_color=C["muted"], line_width=1)
fig.add_hline(y=0, line_color=C["line_strong"], line_width=1)
fig.update_layout(**PLOTLY_LAYOUT, height=390,
                  xaxis_title="Probability of profit (%)", yaxis_title="Median net margin (Rs/tonne)")
st.plotly_chart(fig, use_container_width=True)
caption("Top right is what you want: high probability and a healthy median margin.")

st.markdown("## Viability falls with distance")
bands = [("<400", 0, 400), ("400–700", 400, 700), ("700–1,000", 700, 1000), (">1,000", 1000, 99999)]
rows = []
for lab, lo, hi in bands:
    s = c[(c.road_km >= lo) & (c.road_km < hi)]
    if len(s):
        rows.append((lab, len(s), 100 * (s.p_profitable >= 50).mean()))
fig = go.Figure(go.Bar(
    x=[r[0] for r in rows], y=[r[2] for r in rows],
    marker_color=C["primary"], text=[f"n={r[1]}" for r in rows], textposition="outside",
))
fig.update_layout(**PLOTLY_LAYOUT, height=300, xaxis_title="Haul distance (km)",
                  yaxis_title="% of corridors profitable in most months")
st.plotly_chart(fig, use_container_width=True)
caption("Counts above each bar. The two longest bands hold few corridors, so the trend direction is reliable but the individual percentages are not precise.")

st.markdown("## The bad month matters more than the average")
top = c.nlargest(10, "p_profitable").sort_values("net_p05")
fig = go.Figure()
fig.add_trace(go.Bar(y=[f"{r.commodity[:12]} {r.origin[:4]}→{r.destination[:4]}" for _, r in top.iterrows()],
                     x=top.net_p50, orientation="h", name="Median month", marker_color=C["secondary"]))
fig.add_trace(go.Bar(y=[f"{r.commodity[:12]} {r.origin[:4]}→{r.destination[:4]}" for _, r in top.iterrows()],
                     x=top.net_p05, orientation="h", name="Bad month (5th pct)", marker_color=C["primary"]))
fig.add_vline(x=0, line_color=C["ink_soft"], line_width=1)
fig.update_layout(**PLOTLY_LAYOUT, height=380, barmode="overlay", xaxis_title="Net margin (Rs/tonne)", yaxis_title="")
st.plotly_chart(fig, use_container_width=True)
note(
    "Two corridors with similar averages can carry very different risk. Brinjal from Karnataka "
    "to Tamil Nadu still nets over Rs 10,000 a tonne in its worst 5% of months. Green chilli on "
    "the same route swings to a loss of about Rs 5,000 despite succeeding 88% of the time. Only "
    "the distribution shows this."
)

st.markdown("## All corridors")
t = view[["commodity", "variety", "perishability", "origin", "destination", "road_km",
          "p_profitable", "net_p05", "net_p50", "net_p95", "expected_net", "months"]].copy()
t.columns = ["Commodity", "Variety", "Type", "Origin", "Destination", "Road km",
             "P(profit) %", "Bad month", "Median", "Good month", "Expected", "Months"]
st.dataframe(t.sort_values("P(profit) %", ascending=False), use_container_width=True, hide_index=True)
caption("Margins in Rs per tonne. Corridors are variety-matched — the same variety must be traded at both ends, since banana in Kerala is a different product from banana in Maharashtra.")
