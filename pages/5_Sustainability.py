"""Sustainability — emissions embedded in lost produce."""

import plotly.graph_objects as go
import streamlit as st

from lib import C, PLOTLY_LAYOUT, caption, kpi, load, masthead, note, setup, sidebar_footer

setup("Sustainability")
sidebar_footer()
masthead(
    "Sustainability",
    "Produce that spoils has already consumed fertiliser, water, land and fuel. This page "
    "puts a number on that embedded footprint rather than describing it.",
)

band = load("emissions_band")
em = load("emissions")

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi("Embedded emissions", f"{band.total.iloc[1]/1000:,.0f}k t CO₂e", "per year, central estimate")
with k2:
    kpi("From production", "95.4%", "not from transport")
with k3:
    kpi("External climate cost", "Rs 602 cr", "at USD 86/t social cost of carbon")
with k4:
    kpi("Produce lost", "1.34m t", "worth Rs 2,816 crore")

note(
    "<b>The ratio is the finding.</b> About 95% of the emissions embedded in lost food come from "
    "growing it, only about 5% from moving it. A logistics intervention that re-routes produce "
    "addresses the smaller share; one that prevents the spoilage addresses all of it. As an "
    "emissions lever, loss prevention is roughly twenty times more powerful than route "
    "optimisation — so any sustainability programme starting with transport efficiency is "
    "starting at the small end of the problem."
)

c1, c2 = st.columns([1, 1])
with c1:
    st.markdown("### Growing against moving")
    fig = go.Figure()
    fig.add_trace(go.Bar(y=["Embedded"], x=[759091], orientation="h",
                         name="Production", marker_color=C["primary"]))
    fig.add_trace(go.Bar(y=["Embedded"], x=[36236], orientation="h",
                         name="Transport", marker_color=C["range"]))
    fig.update_layout(**PLOTLY_LAYOUT, height=300, barmode="stack", xaxis_title="tonnes CO₂e per year")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("### Sensitivity to assumptions")
    fig = go.Figure(go.Bar(
        x=["Low", "Central", "High"], y=band.total,
        marker_color=[C["range"], C["primary"], C["secondary"]],
        text=[f"{v/1000:,.0f}k" for v in band.total], textposition="outside",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=300, yaxis_title="tonnes CO₂e per year")
    st.plotly_chart(fig, use_container_width=True)

caption(
    "The paddy (1.0 kg CO₂e/kg) and cereal (0.2) intensities are official FAO farm-gate figures. "
    "Vegetable, fruit, oilseed and spice intensities come from life-cycle assessment literature "
    "and are not single official values, so every total is reported as a range rather than a point."
)

st.markdown("## Where the emissions sit")
e = em.sort_values("total_co2e", ascending=True).tail(10)
fig = go.Figure()
fig.add_trace(go.Bar(y=e.commodity, x=e.prod_co2e / 1000, orientation="h",
                     name="Production", marker_color=C["primary"]))
fig.add_trace(go.Bar(y=e.commodity, x=e.trans_co2e / 1000, orientation="h",
                     name="Transport", marker_color=C["range"]))
fig.update_layout(**PLOTLY_LAYOUT, height=400, barmode="stack",
                  xaxis_title="thousand tonnes CO₂e per year", yaxis_title="")
st.plotly_chart(fig, use_container_width=True)

note(
    "Onion alone accounts for about 338,000 tonnes CO₂e a year — 42% of the regional total — "
    "because it combines very large lost tonnage with a moderate emission intensity. Paddy is "
    "second despite far smaller lost tonnage, because rice cultivation is emission-intensive per "
    "kilogram. Neither is what a purely commercial ranking would pick first, which is exactly why "
    "the emissions view is worth computing separately."
)

st.markdown("## What loss reduction would avoid")
red = st.slider("Reduction in post-harvest loss (%)", 0, 50, 10, 5)
central = band.total.iloc[1]
a1, a2, a3 = st.columns(3)
with a1:
    kpi("Emissions avoided", f"{central*red/100:,.0f} t", "CO₂e per year")
with a2:
    kpi("Climate cost avoided", f"Rs {central*red/100*86*88/1e7:,.0f} cr", "per year")
with a3:
    kpi("Produce saved", f"{1.34e6*red/100/1000:,.0f}k t", f"worth Rs {2816*red/100:,.0f} crore")

st.markdown("## The social side")
note(
    "Sustainability in a supply chain has a social dimension alongside the environmental one. "
    "The farmer receives roughly 29.9% of the final tomato price, with about 65.9% captured at "
    "retail. For onion the pattern inverts and the farmer share rises to about 69.6% — the "
    "difference is durability. Onion tolerates handling and delay, so the grower can wait for a "
    "better price; tomato cannot wait at all. A chain that captures two-thirds of the value of a "
    "tomato downstream of the person who grew it is not sustainable in the social sense, however "
    "efficiently it moves the tomato."
)
caption("The farmer-share figures rest on a comparatively small retail price sample and are indicative rather than precise. See Data & Method.")
