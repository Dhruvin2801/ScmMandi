"""Market explorer — prices, arrivals and reporting quality."""

import plotly.graph_objects as go
import streamlit as st

from lib import C, PLOTLY_LAYOUT, caption, kpi, load, masthead, note, setup, sidebar_footer

setup("Market Explorer")
sidebar_footer()
masthead(
    "Market Explorer",
    "What was actually reported, by state and commodity. Prices are arrivals-weighted "
    "monthly means; missing reports stay missing and are never treated as zero.",
)

m = load("master")
st.sidebar.header("Filters")
states = sorted(m.state.unique())
sel_states = st.sidebar.multiselect("States", states, default=states)
coms = sorted(m[m.state.isin(sel_states)].commodity.unique())
sel_com = st.sidebar.selectbox("Commodity", coms, index=coms.index("Onion") if "Onion" in coms else 0)
strict = st.sidebar.checkbox(
    "Comparable price basis only", value=True,
    help="Excludes coconut and arecanut (whole-nut vs weight) and Kerala (no APMC Act).",
)

d = m[(m.state.isin(sel_states)) & (m.commodity == sel_com) & (m.arrivals_t > 0)]
if strict:
    d = d[d.price_basis_comparable & d.institution_comparable]

if d.empty:
    st.warning("No records match these filters. Try widening the state selection or unticking the basis filter.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi("Markets", f"{d.market.nunique():,}", f"{d.district.nunique()} districts")
with k2:
    kpi("Arrivals", f"{d.arrivals_t.sum()/1000:,.0f}k t", "over the study period")
with k3:
    wt = (d.avg_price * d.arrivals_t).sum() / d.arrivals_t.sum()
    kpi("Mean price", f"Rs {wt/100:,.2f}/kg", "arrivals-weighted")
with k4:
    kpi("Perishability", d.perishability.mode()[0], f"loss rate {d.loss_pct.iloc[0]:.1f}%")

st.markdown("## Price and arrivals over time")
g = (
    d.groupby(["month", "state"])
    .apply(
        lambda x: (x.avg_price * x.arrivals_t).sum() / x.arrivals_t.sum() / 100,
        include_groups=False,
    )
    .reset_index(name="price")
)
fig = go.Figure()
palette = [C["primary"], C["clay"], C["leaf_dark"], C["mango"], C["secondary"], C["range"]]
for i, s in enumerate(sorted(g.state.unique())):
    sub = g[g.state == s].sort_values("month")
    fig.add_trace(
        go.Scatter(x=sub.month, y=sub.price, name=s, mode="lines+markers",
                   line=dict(color=palette[i % len(palette)], width=2), marker=dict(size=5))
    )
fig.update_layout(**PLOTLY_LAYOUT, height=380, yaxis_title="Rs per kg", xaxis_title="")
st.plotly_chart(fig, use_container_width=True)
caption("Arrivals-weighted monthly mean price. Gaps indicate months with no qualifying reports.")

a = d.groupby("month").arrivals_t.sum().reset_index().sort_values("month")
fig = go.Figure(go.Bar(x=a.month, y=a.arrivals_t, marker_color=C["secondary"]))
fig.update_layout(**PLOTLY_LAYOUT, height=260, yaxis_title="tonnes", xaxis_title="")
st.plotly_chart(fig, use_container_width=True)
caption("Reported arrivals by month. Peaks mark the harvest window for this commodity.")

st.markdown("## Markets by volume")
top = (
    d.groupby(["state", "district", "market"])
    .agg(tonnes=("arrivals_t", "sum"), months=("month", "nunique"),
         price=("avg_price", "mean"))
    .reset_index()
    .sort_values("tonnes", ascending=False)
    .head(25)
)
top["Rs per kg"] = (top.price / 100).round(2)
top = top.rename(columns={"state": "State", "district": "District", "market": "Market",
                          "tonnes": "Arrivals (t)", "months": "Months reported"})
st.dataframe(
    top[["State", "District", "Market", "Arrivals (t)", "Months reported", "Rs per kg"]],
    use_container_width=True, hide_index=True,
)
caption("Months reported out of 25 is a reporting-quality signal: a market with few months is thinly covered, not necessarily inactive.")

note(
    "<b>Two exclusions worth knowing.</b> Coconut and arecanut are priced per whole nut in "
    "Karnataka and by weight in Tamil Nadu, so their prices are not comparable across states. "
    "Kerala has no APMC Act — its produce is marketed through private collection shops and the "
    "state horticulture council, so its reported prices sit near retail rather than at wholesale "
    "auction level. Both are excluded from cross-state comparison by default and can be "
    "re-included with the sidebar toggle.",
    warn=True,
)
