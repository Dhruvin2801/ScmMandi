"""Simulator — investment and corridor models on your own numbers."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from lib import C, PLOTLY_LAYOUT, caption, kpi, load, masthead, note, setup, sidebar_footer

setup("Simulator")
sidebar_footer()
masthead(
    "Simulator",
    "Run the cold-chain and corridor models on your own assumptions. Nothing you enter "
    "leaves your browser session.",
)

tab1, tab2 = st.tabs(["Cold-chain investment", "Corridor movement"])

# ---------------------------------------------------------------- cold chain
with tab1:
    st.markdown("### District profile")
    c1, c2, c3 = st.columns(3)
    with c1:
        thru = st.number_input("Annual perishable throughput (tonnes)", 0, 5_000_000, 400_000, 10_000)
    with c2:
        lossv = st.number_input("Annual value of loss (Rs lakh)", 0, 200_000, 9_000, 500)
    with c3:
        psh = st.slider("Perishable share of district volume", 0.0, 1.0, 0.90, 0.01)

    st.markdown("### Economic assumptions")
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        capex_t = st.number_input("Capex (Rs/tonne)", 1000, 30_000, 8_000, 500)
        util = st.slider("Utilisation", 0.3, 1.0, 0.70, 0.05)
    with d2:
        opex_t = st.number_input("Opex (Rs/tonne/yr)", 200, 6_000, 1_400, 100)
        hold = st.slider("Held share of throughput", 0.02, 0.30, 0.10, 0.01)
    with d3:
        rec = st.slider("Recoverable share of loss", 0.1, 0.95, 0.60, 0.05)
        disc = st.slider("Discount rate", 0.04, 0.20, 0.10, 0.01)
    with d4:
        life = st.number_input("Facility life (years)", 5, 30, 15, 1)
        runs = st.select_slider("Simulation runs", [1000, 5000, 10000], 5000)

    cap = thru * hold / util
    capex = cap * capex_t / 1e5
    opex = cap * opex_t / 1e5
    ben = lossv * rec * psh
    net = ben - opex
    af = (1 - (1 + disc) ** -life) / disc
    npv = net * af - capex
    pay = capex / net if net > 0 else float("inf")

    st.markdown("### Point estimate")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        kpi("Capacity", f"{cap:,.0f} t", f"capex Rs {capex:,.0f} lakh")
    with m2:
        kpi("Net annual benefit", f"Rs {net:,.0f} lakh", f"opex Rs {opex:,.0f} lakh/yr")
    with m3:
        kpi("NPV", f"Rs {npv:,.0f} lakh", f"over {life} years at {disc:.0%}")
    with m4:
        kpi("Payback", f"{pay:,.2f} yrs" if np.isfinite(pay) else "never", "on net annual benefit")

    st.markdown("### Simulation")
    note(
        "The point estimate above answers: is this viable under your best guess? The simulation "
        "answers the more useful question: how likely is it to be viable, given that none of these "
        "inputs is known exactly? Each run draws every assumption from a range around your entry."
    )
    if st.button("Run simulation", type="primary"):
        rng = np.random.default_rng()
        n = int(runs)
        r_ = np.clip(rng.normal(rec, 0.10, n), 0.05, 0.98)
        cx = rng.triangular(capex_t * 0.75, capex_t, capex_t * 1.375, n)
        ox = rng.triangular(opex_t * 0.71, opex_t, opex_t * 1.36, n)
        ut = np.clip(rng.normal(util, 0.08, n), 0.3, 0.98)
        hd = np.clip(rng.normal(hold, 0.02, n), 0.02, 0.35)
        ds = np.clip(rng.normal(disc, 0.015, n), 0.04, 0.22)
        lm = np.clip(rng.normal(1.0, 0.20, n), 0.4, 1.7)
        cap_s = thru * hd / ut
        capex_s = cap_s * cx / 1e5
        opex_s = cap_s * ox / 1e5
        net_s = lossv * lm * r_ * psh - opex_s
        af_s = (1 - (1 + ds) ** -life) / ds
        npv_s = net_s * af_s - capex_s
        pay_s = np.where(net_s > 1e-9, capex_s / np.maximum(net_s, 1e-9), np.inf)
        via = (npv_s > 0) & (pay_s < life) & (thru > 0)
        p = 100 * via.mean()

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            kpi("Probability viable", f"{p:.1f}%", f"{n:,} runs")
        with s2:
            kpi("Bad case (5th pct)", f"Rs {np.percentile(npv_s,5):,.0f} lakh", "NPV")
        with s3:
            kpi("Median", f"Rs {np.median(npv_s):,.0f} lakh", "NPV")
        with s4:
            kpi("Good case (95th pct)", f"Rs {np.percentile(npv_s,95):,.0f} lakh", "NPV")

        fig = go.Figure(go.Histogram(
            x=npv_s, nbinsx=60,
            marker_color=C["primary"], marker_line_color="white", marker_line_width=0.4,
        ))
        fig.add_vline(x=0, line_color=C["danger"], line_width=2)
        fig.update_layout(**PLOTLY_LAYOUT, height=330,
                          xaxis_title="Net present value (Rs lakh)", yaxis_title="Runs")
        st.plotly_chart(fig, use_container_width=True)
        caption("The red line marks break-even. Area to its left is the share of futures in which the facility loses money.")

        if p >= 95:
            verdict, kind = "INVEST — robust. Viable in almost every plausible future.", "pill-good"
        elif p >= 60:
            verdict, kind = "INVEST — conditional. Viable in most futures, but the downside is real.", "pill-warn"
        else:
            verdict, kind = "REJECT — fails in too many plausible futures.", "pill-bad"
        st.markdown(f'<div class="card"><span class="pill {kind}">Verdict</span> {verdict}</div>',
                    unsafe_allow_html=True)

        if psh < 0.05:
            note("With almost no perishable volume, the benefit collapses regardless of how cheap "
                 "the facility is. This is why 17 districts fail: there is nothing to preserve.", warn=True)

# ---------------------------------------------------------------- corridor
with tab2:
    st.markdown("### The movement")
    e1, e2, e3 = st.columns(3)
    with e1:
        po = st.number_input("Price at origin (Rs/quintal)", 100, 50_000, 1_537, 50)
        km = st.number_input("Road distance (km)", 10, 3_000, 315, 25)
    with e2:
        pdd = st.number_input("Price at destination (Rs/quintal)", 100, 50_000, 2_644, 50)
        lr = st.slider("Post-harvest loss rate (%)", 0.5, 30.0, 11.6, 0.5)
    with e3:
        per = st.selectbox("Crop type", ["High", "Semi", "Storable"])
        rate = st.slider("Freight rate (Rs/tonne-km)", 1.5, 8.0,
                         4.5 if per == "High" else 3.5, 0.1)

    div = 30 if per == "High" else 90
    gross = (pdd - po) * 10
    days = max(1.0, km / 500)
    spoil = pdd * 10 * (lr / 100) * days / div
    freight = rate * km
    netm = gross - freight - spoil
    spk = pdd * 10 * (lr / 100) / (500 * div)
    be_lin = gross / (rate + spk)
    be = be_lin if be_lin >= 500 else max(0.0, min((gross - pdd * 10 * (lr / 100) / div) / rate, 500))

    n1, n2, n3, n4 = st.columns(4)
    with n1:
        kpi("Gross spread", f"Rs {gross:,.0f}/t", f"{days:.2f} transit days")
    with n2:
        kpi("Freight", f"Rs {freight:,.0f}/t", f"at Rs {rate:.1f}/t-km")
    with n3:
        kpi("Spoilage", f"Rs {spoil:,.0f}/t", f"Rs {spk:.3f} per km")
    with n4:
        kpi("Net margin", f"Rs {netm:,.0f}/t", "after freight and spoilage")

    st.markdown(
        f'<div class="card"><span class="pill {"pill-good" if netm>0 else "pill-bad"}">Verdict</span> '
        f'{"MOVE — the margin survives freight and spoilage." if netm>0 else "DO NOT MOVE — costs exceed the price gap."}'
        f' &nbsp;·&nbsp; Break-even haul distance <b>{be:,.0f} km</b></div>',
        unsafe_allow_html=True,
    )

    dist = np.linspace(0, max(1200, km * 1.6), 400)
    dd = np.maximum(1, dist / 500)
    curve = gross - rate * dist - pdd * 10 * (lr / 100) * dd / div
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dist, y=curve, mode="lines", name="Net margin",
                             line=dict(color=C["primary"], width=2.5)))
    fig.add_hline(y=0, line_color=C["ink_soft"], line_width=1)
    fig.add_vline(x=km, line_dash="dot", line_color=C["clay"], line_width=1.5,
                  annotation_text="your haul", annotation_position="top")
    fig.update_layout(**PLOTLY_LAYOUT, height=340,
                      xaxis_title="Haul distance (km)", yaxis_title="Net margin (Rs/tonne)")
    st.plotly_chart(fig, use_container_width=True)
    note(
        "Spoilage is a variable cost, not a fixed one: a longer haul means more transit days and "
        "therefore more spoilage. The break-even distance solves for where the price gap equals "
        "freight per km <i>plus</i> spoilage per km. Treating spoilage as fixed overstates the "
        "break-even — by about 84 km on the default corridor."
    )
