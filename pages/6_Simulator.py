"""Simulator — three working tools: two calculators and a live Monte Carlo."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from lib import C, PLOTLY_LAYOUT, caption, kpi, masthead, note, setup, sidebar_footer

setup("Simulator")
sidebar_footer()
masthead(
    "Decision Support Tools",
    "The chain has a transaction layer but no decision-support layer. These three tools are a "
    "small demonstration of what that missing layer looks like. Nothing you enter leaves your "
    "browser session.",
)

tab1, tab2, tab3 = st.tabs([
    "① Cold-chain investment",
    "② Corridor movement",
    "③ Live Monte Carlo",
])

# ══════════════════════════════════════ TOOL 1 — COLD CHAIN
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

    cap = thru * hold / util
    capex = cap * capex_t / 1e5
    opex = cap * opex_t / 1e5
    ben = lossv * rec * psh
    net = ben - opex
    af = (1 - (1 + disc) ** -life) / disc
    npv = net * af - capex
    pay = capex / net if net > 0 else float("inf")

    st.markdown("### Result")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        kpi("Capacity required", f"{cap:,.0f} t", f"capex Rs {capex:,.0f} lakh")
    with m2:
        kpi("Net annual benefit", f"Rs {net:,.0f} lakh", f"opex Rs {opex:,.0f} lakh/yr")
    with m3:
        kpi("Net present value", f"Rs {npv:,.0f} lakh", f"over {life} years at {disc:.0%}")
    with m4:
        kpi("Payback period", f"{pay:,.2f} yrs" if np.isfinite(pay) else "never", "on net annual benefit")

    viable = npv > 0 and np.isfinite(pay) and pay < life
    v_txt = ("INVEST — the facility repays its capital within the asset life."
             if viable else "REJECT — the facility does not clear the hurdle.")
    st.markdown(
        f'<div class="card"><span class="pill {"pill-good" if viable else "pill-bad"}">Verdict</span> '
        f'{v_txt}</div>',
        unsafe_allow_html=True,
    )
    if psh < 0.05:
        note("With almost no perishable volume the benefit collapses regardless of how cheap the "
             "facility is. This is exactly why 17 districts fail: there is nothing to preserve.", warn=True)
    note("Benefit = annual loss value × recoverable share × perishable share. Capacity = throughput × "
         "held share ÷ utilisation. NPV = (benefit − opex) × annuity factor − capex.")

# ══════════════════════════════════════ TOOL 2 — CORRIDOR
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

    st.markdown("### Result")
    n1, n2, n3, n4 = st.columns(4)
    with n1:
        kpi("Gross spread", f"Rs {gross:,.0f}/t", f"{days:.2f} transit days")
    with n2:
        kpi("Freight", f"Rs {freight:,.0f}/t", f"at Rs {rate:.1f}/t-km")
    with n3:
        kpi("Transit spoilage", f"Rs {spoil:,.0f}/t", f"Rs {spk:.3f} per km")
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
                             line=dict(color=C["primary"], width=3),
                             fill="tozeroy", fillcolor="rgba(45,106,79,0.10)"))
    fig.add_hline(y=0, line_color=C["ink_soft"], line_width=1)
    fig.add_vline(x=km, line_dash="dot", line_color=C["accent"], line_width=2,
                  annotation_text="your haul", annotation_position="top")
    fig.update_layout(**PLOTLY_LAYOUT, height=350,
                      xaxis_title="Haul distance (km)", yaxis_title="Net margin (Rs/tonne)")
    st.plotly_chart(fig, use_container_width=True)
    note("Spoilage is a variable cost, not a fixed one: a longer haul means more transit days and "
         "therefore more spoilage. The break-even solves for the distance at which the price gap "
         "equals freight per km <i>plus</i> spoilage per km.")

# ══════════════════════════════════════ TOOL 3 — MONTE CARLO
with tab3:
    st.markdown("### Why simulate")
    note("A single answer tells you whether a district is viable under your best guess. A simulation "
         "tells you what a manager actually needs to know: <b>how likely</b> is it to be viable, given "
         "that none of the inputs is known exactly? Each run draws every assumption from a range "
         "around your entry.")

    st.markdown("### District profile")
    s1, s2, s3 = st.columns(3)
    with s1:
        m_thru = st.number_input("Annual perishable throughput (t)", 0, 5_000_000, 400_000, 10_000, key="mthru")
    with s2:
        m_loss = st.number_input("Annual value of loss (Rs lakh)", 0, 200_000, 9_000, 500, key="mloss")
    with s3:
        m_psh = st.slider("Perishable share", 0.0, 1.0, 0.90, 0.01, key="mpsh")

    st.markdown("### Uncertainty ranges")
    u1, u2, u3, u4 = st.columns(4)
    with u1:
        r_rec = st.slider("Recoverable share", 0.10, 0.95, (0.45, 0.75), 0.05)
        r_cap = st.slider("Capex (Rs/t)", 3000, 20000, (6000, 11000), 500)
    with u2:
        r_opx = st.slider("Opex (Rs/t/yr)", 500, 4000, (1000, 1900), 100)
        r_utl = st.slider("Utilisation", 0.3, 1.0, (0.55, 0.85), 0.05)
    with u3:
        r_hld = st.slider("Held share", 0.02, 0.30, (0.06, 0.16), 0.01)
        r_dsc = st.slider("Discount rate", 0.04, 0.20, (0.07, 0.14), 0.01)
    with u4:
        r_lmu = st.slider("Loss-rate multiplier", 0.4, 1.8, (0.60, 1.50), 0.05)
        runs = st.select_slider("Simulation runs", [1000, 5000, 10000], 5000)

    if st.button("Run simulation", type="primary"):
        rng = np.random.default_rng()
        n = int(runs)
        u = rng.uniform
        r_ = u(*r_rec, n)
        cx = u(*r_cap, n)
        ox = u(*r_opx, n)
        ut = u(*r_utl, n)
        hd = u(*r_hld, n)
        ds = u(*r_dsc, n)
        lm = u(*r_lmu, n)
        life = 15

        cap_s = m_thru * hd / ut
        capex_s = cap_s * cx / 1e5
        opex_s = cap_s * ox / 1e5
        net_s = m_loss * lm * r_ * m_psh - opex_s
        af_s = (1 - (1 + ds) ** -life) / ds
        npv_s = net_s * af_s - capex_s
        pay_s = np.where(net_s > 1e-9, capex_s / np.maximum(net_s, 1e-9), np.inf)
        via = (npv_s > 0) & (pay_s < life) & (m_thru > 0)
        p = 100 * via.mean()

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi("Probability viable", f"{p:.1f}%", f"{n:,} runs")
        with k2:
            kpi("Bad case (5th pct)", f"Rs {np.percentile(npv_s,5):,.0f} L", "net present value")
        with k3:
            kpi("Median", f"Rs {np.median(npv_s):,.0f} L", "net present value")
        with k4:
            kpi("Good case (95th pct)", f"Rs {np.percentile(npv_s,95):,.0f} L", "net present value")

        fig = go.Figure(go.Histogram(
            x=npv_s, nbinsx=60, marker_color=C["primary"],
            marker_line_color="white", marker_line_width=0.5,
        ))
        fig.add_vline(x=0, line_color=C["danger"], line_width=2.5,
                      annotation_text="break-even", annotation_position="top")
        fig.update_layout(**PLOTLY_LAYOUT, height=350,
                          xaxis_title="Net present value (Rs lakh)", yaxis_title="Number of runs")
        st.plotly_chart(fig, use_container_width=True)
        caption("Area to the left of the red line is the share of futures in which the facility loses money.")

        if p >= 95:
            verdict, kind = "INVEST — robust. Viable in almost every plausible future.", "pill-good"
        elif p >= 60:
            verdict, kind = "INVEST — conditional. Viable in most futures, but the downside is real.", "pill-warn"
        else:
            verdict, kind = "REJECT — fails in too many plausible futures.", "pill-bad"
        st.markdown(f'<div class="card"><span class="pill {kind}">Verdict</span> {verdict}</div>',
                    unsafe_allow_html=True)

        st.markdown("##### Spread of outcomes")
        st.dataframe({
            "Statistic": ["Worst run", "5th percentile", "Median", "Mean", "95th percentile", "Best run"],
            "Net present value (Rs lakh)": [
                f"{npv_s.min():,.0f}", f"{np.percentile(npv_s,5):,.0f}", f"{np.median(npv_s):,.0f}",
                f"{npv_s.mean():,.0f}", f"{np.percentile(npv_s,95):,.0f}", f"{npv_s.max():,.0f}"],
        }, use_container_width=True, hide_index=True)

        note("Run it again and the answer will move slightly — that movement <b>is</b> the uncertainty. "
             "For a strong district the verdict never changes; for a marginal one it flickers between "
             "bands. The stable 10,000-iteration figures for every district are on the Cold-Chain Siting page.")
    else:
        note("Set the ranges above and press <b>Run simulation</b>. The defaults match the "
             "10,000-iteration run reported in the project.")
