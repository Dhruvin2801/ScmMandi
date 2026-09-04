"""Cold-chain siting — district viability with probabilities."""

import plotly.graph_objects as go
import streamlit as st

from lib import C, PLOTLY_LAYOUT, caption, kpi, load, masthead, note, setup, sidebar_footer

setup("Cold-Chain Siting")
sidebar_footer()
masthead(
    "Cold-Chain Siting",
    "Where a cold store would repay its capital, district by district. Each result is a "
    "probability drawn from 10,000 simulations, not a single yes-or-no verdict.",
)

d = load("districts")
mat = d[d.scale == "Material"]

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi("Robust", f"{int((d.p_viable >= 99.9).sum())}", "viable in ≥99.9% of runs")
with k2:
    kpi("Uncertain", f"{int(((d.p_viable > 5) & (d.p_viable < 95)).sum())}", "the ones a flag would hide")
with k3:
    kpi("Never viable", f"{int((d.p_viable <= 0.1).sum())}", "all have ~0% perishable share")
with k4:
    kpi("Material scale", f"{len(mat)}", "≥25,000 t/yr perishable")

note(
    "A single-point model reported 67 of 84 districts viable, which reads as though 67 are "
    "equally safe bets. They are not. Only 22 survive every plausible combination of "
    "assumptions, and eight sit in a band where the answer genuinely depends on which "
    "assumptions turn out right."
)

st.sidebar.header("Filters")
sel_states = st.sidebar.multiselect("States", sorted(d.state.unique()), default=sorted(d.state.unique()))
only_material = st.sidebar.checkbox("Material scale only", value=True)
view = d[d.state.isin(sel_states)]
if only_material:
    view = view[view.scale == "Material"]

st.markdown("## Probability of viability")
v = view.sort_values("p_viable")
colours = [
    C["primary"] if p >= 95 else (C["turmeric"] if p >= 60 else C["danger"])
    for p in v.p_viable
]
fig = go.Figure(
    go.Bar(
        x=v.p_viable, y=v.district, orientation="h", marker_color=colours,
        hovertemplate="%{y}<br>P(viable) %{x:.1f}%<extra></extra>",
    )
)
fig.add_vline(x=95, line_dash="dash", line_color=C["ink_soft"], line_width=1)
fig.add_vline(x=60, line_dash="dot", line_color=C["muted"], line_width=1)
fig.update_layout(
    **PLOTLY_LAYOUT, height=max(320, 22 * len(v)),
    xaxis_title="Probability of viability (%)", yaxis_title="",
)
st.plotly_chart(fig, use_container_width=True)
caption("Dashed line marks the 95% robust threshold; dotted line marks 60%.")

st.markdown("## Viability follows crop mix, not scale")
fig = go.Figure(
    go.Scatter(
        x=view.perish_pct, y=view.p_viable, mode="markers",
        marker=dict(
            size=(view.annual_perish_t.clip(lower=1) ** 0.32) / 3 + 6,
            color=view.p_viable, colorscale=[[0, C["danger"]], [0.6, C["turmeric"]], [1, C["primary"]]],
            showscale=False, line=dict(width=0.5, color="white"),
        ),
        text=view.district,
        hovertemplate="%{text}<br>Perishable %{x:.1f}%<br>P(viable) %{y:.1f}%<extra></extra>",
    )
)
fig.update_layout(
    **PLOTLY_LAYOUT, height=380,
    xaxis_title="Perishable share of district volume (%)",
    yaxis_title="Probability of viability (%)",
)
st.plotly_chart(fig, use_container_width=True)
caption("Marker size is annual perishable tonnage. The failures sit entirely at the left edge — no perishables, nothing to preserve.")

st.markdown("## District results")
tbl = view[[
    "state", "district", "perish_pct", "annual_perish_t", "p_viable",
    "npv_p05", "npv_p50", "npv_p95", "payback_p50", "decision",
]].copy()
tbl.columns = [
    "State", "District", "Perishable %", "Annual perishable t", "P(viable) %",
    "NPV 5th pct", "NPV median", "NPV 95th pct", "Payback (yrs)", "Decision",
]
st.dataframe(tbl.sort_values("P(viable) %", ascending=False), use_container_width=True, hide_index=True)
caption("NPV figures in Rs lakh. The 5th percentile is the bad case — where it falls below zero, the investment can lose money.")

unc = d[(d.p_viable > 5) & (d.p_viable < 95)].sort_values("annual_perish_t", ascending=False)
if not unc.empty:
    st.markdown("## The uncertain districts")
    note(
        f"<b>{unc.iloc[0].district}</b> is the clearest case. It handles "
        f"{unc.iloc[0].annual_perish_t:,.0f} tonnes of perishable produce a year at a "
        f"{unc.iloc[0].perish_pct:.1f}% perishable share, and a single-point model marks it viable "
        f"without qualification. The simulation puts viability at {unc.iloc[0].p_viable:.1f}% with a "
        f"5th-percentile NPV of Rs {unc.iloc[0].npv_p05:,.0f} lakh. There is a real, if small, set of "
        "circumstances in which the largest facility in the study loses money — worth knowing before "
        "the capital is committed.",
        warn=True,
    )
    u = unc[["state", "district", "perish_pct", "annual_perish_t", "p_viable", "npv_p05", "npv_p50"]].copy()
    u.columns = ["State", "District", "Perishable %", "Annual perishable t", "P(viable) %", "NPV 5th pct", "NPV median"]
    st.dataframe(u, use_container_width=True, hide_index=True)

st.markdown("## Does screening by crop mix actually pay?")
p = load("portfolio")
c1, c2 = st.columns([2, 1])
with c1:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=p.strategy, y=p.npv_p50_cr, name="Median NPV", marker_color=C["primary"],
        error_y=dict(type="data", symmetric=False,
                     array=p.npv_p95_cr - p.npv_p50_cr, arrayminus=p.npv_p50_cr - p.npv_p05_cr,
                     color=C["ink_soft"], width=6),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=320, yaxis_title="Portfolio NPV (Rs crore)", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    caption("Same Rs 1,411 crore deployed two ways. Error bars span the 5th to 95th percentile.")
with c2:
    kpi("Expected advantage", "Rs 1,300 cr", "of screening over uniform")
    st.write("")
    kpi("Confidence", "98.6%", "of simulated futures favour screening")
    st.write("")
    kpi("95% interval", "Rs 116–2,692 cr", "lower bound still positive")

st.markdown("## Which assumption drives the answer")
t = load("tornado").sort_values("abs_influence")
fig = go.Figure(go.Bar(
    x=t.correlation_with_NPV, y=t.assumption, orientation="h",
    marker_color=[C["primary"] if v > 0 else C["danger"] for v in t.correlation_with_NPV],
))
fig.update_layout(**PLOTLY_LAYOUT, height=300, xaxis_title="Correlation with portfolio NPV", yaxis_title="")
st.plotly_chart(fig, use_container_width=True)
note(
    "The result is far more sensitive to how accurately national loss rates transfer to these "
    "districts (0.690) than to what a cold store actually costs to build (−0.071). Better cost "
    "estimates would barely move the answer; district-level loss measurement would move it a "
    "great deal. If one further dataset could be collected, that is the one."
)
