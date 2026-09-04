"""Market integration and variance amplification."""

import plotly.graph_objects as go
import streamlit as st

from lib import C, PLOTLY_LAYOUT, caption, kpi, load, masthead, note, setup, sidebar_footer

setup("Market Integration")
sidebar_footer()
masthead(
    "Market Integration",
    "Whether markets share a common price, how fast a shock travels between them, and why "
    "storable crops swing far more in volume than perishable ones.",
)

co = load("coint")
gr = load("granger")
m = co.drop(columns=["granger_pct"], errors="ignore").merge(
    gr[["commodity", "granger_pct", "median_lag_days"]], on="commodity", how="left"
)

k1, k2, k3 = st.columns(3)
with k1:
    kpi("Tomato market pairs cointegrated", "93.7%", "long-run equilibrium exists")
with k2:
    kpi("Median transmission lag", "3–5 days", "longer than perishable shelf life")
with k3:
    kpi("Paddy pairs cointegrated", "11.9%", "floor price anchors each market")

note(
    "<b>The deficit is temporal, not structural.</b> An earlier version of this analysis used "
    "same-day correlation, found it near zero, and concluded markets were not integrated. That "
    "was wrong — same-day correlation cannot detect a long-run relationship. Cointegration shows "
    "perishable markets <i>are</i> connected. What is missing is speed: a price signal that takes "
    "four to five days to arrive is useless to a farmer holding a crop that spoils in days."
)

st.markdown("## Integration by commodity")
v = m.sort_values("coint_pct")
fig = go.Figure()
fig.add_trace(go.Bar(y=v.commodity, x=v.coint_pct, orientation="h",
                     name="Cointegrated pairs (%)", marker_color=C["primary"]))
fig.add_trace(go.Bar(y=v.commodity, x=v.granger_pct, orientation="h",
                     name="Granger-causal pairs (%)", marker_color=C["secondary"]))
fig.update_layout(**PLOTLY_LAYOUT, height=400, barmode="group", xaxis_title="% of market pairs", yaxis_title="")
st.plotly_chart(fig, use_container_width=True)
caption("Engle-Granger cointegration at the 5% level across the 25 densest markets per commodity; Granger causality on log first differences at lags 1–5.")

t = m[["commodity", "n_markets", "pairs", "coint_pct", "granger_pct", "median_lag_days"]].copy()
t.columns = ["Commodity", "Markets", "Pairs tested", "Cointegrated %", "Granger-causal %", "Median lag (days)"]
st.dataframe(t.sort_values("Cointegrated %", ascending=False), use_container_width=True, hide_index=True)

note(
    "Storables invert the pattern for a good reason. Paddy shows cointegration in only 11.9% of "
    "pairs not because its markets are broken, but because an administered floor price anchors "
    "each market independently. When a floor sets the level, markets have no need to move together."
)

st.markdown("## Variance amplification")
bw = load("bullwhip").sort_values("median_amp")
cmap = {"Storable": C["primary"], "Semi": C["secondary"], "High": C["range"]}
fig = go.Figure(go.Bar(
    y=bw.commodity, x=bw.median_amp, orientation="h",
    marker_color=[cmap.get(p, C["secondary"]) for p in bw.perishability],
    hovertemplate="%{y}<br>Amplification %{x:.2f}<extra></extra>",
))
fig.add_vline(x=1, line_dash="dash", line_color=C["ink_soft"], line_width=1)
fig.update_layout(**PLOTLY_LAYOUT, height=400,
                  xaxis_title="CV(arrivals) ÷ CV(price)", yaxis_title="")
st.plotly_chart(fig, use_container_width=True)

c1, c2, c3 = st.columns(3)
with c1:
    kpi("Storable", "7.72", "volume swings ~8× more than price")
with c2:
    kpi("Semi-perishable", "2.11", "moderate amplification")
with c3:
    kpi("High-perishable", "1.31", "volume tracks price")

note(
    "Amplification appears exactly where storage is possible. A storable crop can be held back "
    "and released in batches, so arrivals swing violently against a stable price. A perishable "
    "crop must clear the market regardless, so its arrivals simply track it. This is batching and "
    "forward buying observed in field data — a cause of demand distortion, measured, rather than a "
    "magnitude approximated. The strict ratio needs order data across echelons, which mandi "
    "records do not contain, and is therefore not claimed."
)

st.markdown("## Glut months")
g = load("glut").sort_values("glut_price_vs_average_pct")
fig = go.Figure(go.Bar(
    y=g.commodity, x=g.glut_price_vs_average_pct, orientation="h",
    marker_color=[C["danger"] if v < -2 else (C["primary"] if v > 2 else C["secondary"])
                  for v in g.glut_price_vs_average_pct],
))
fig.add_vline(x=0, line_color=C["ink_soft"], line_width=1)
fig.update_layout(**PLOTLY_LAYOUT, height=380,
                  xaxis_title="Price in peak-supply months vs annual average (%)", yaxis_title="")
st.plotly_chart(fig, use_container_width=True)
note(
    "Semi-perishables lose 13.3% on average when supply peaks; storables lose 2.1%. A floor price "
    "protects the paddy grower in exactly the months the onion grower has no protection. Tomato is "
    "the exception at +12.6% — its arrivals peak alongside strong demand rather than in a glut, a "
    "reminder that a high-arrival month is not automatically a distress month."
)
