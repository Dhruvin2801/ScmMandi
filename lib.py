"""Shared theme, data loaders and UI primitives for the ColdLens dashboard."""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "data"

# Palette adapted from the MandiLens design system.
C = {
    "canvas": "#dde0da",
    "frame": "#f2f3ef",
    "surface": "#ffffff",
    "surface_soft": "#f7f8f5",
    "surface_quiet": "#eef0eb",
    "ink": "#172019",
    "ink_soft": "#303b31",
    "muted": "#596359",
    "faint": "#687268",
    "line": "#dde1d8",
    "line_strong": "#cbd1c5",
    "leaf": "#8fc642",
    "leaf_dark": "#3f6f25",
    "leaf_soft": "#eaf5da",
    "turmeric": "#f0dc35",
    "turmeric_soft": "#fff9ca",
    "mango": "#f1a45b",
    "mango_soft": "#fff0e0",
    "primary": "#536f59",
    "primary_strong": "#385141",
    "secondary": "#91a294",
    "range": "#d9c88f",
    "range_soft": "#f2ecdc",
    "clay": "#c58b68",
    "grid": "#e4e9e2",
    "danger": "#b95845",
    "danger_soft": "#fbe9e4",
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Noto Sans', system-ui, sans-serif;
    color: {C['ink']};
}}
.stApp {{ background: {C['frame']}; }}
section[data-testid="stSidebar"] {{
    background: {C['surface_soft']};
    border-right: 1px solid {C['line']};
}}
#MainMenu, footer {{ visibility: hidden; }}
.block-container {{ padding-top: 2.2rem; max-width: 1180px; }}

h1, h2, h3 {{ color: {C['ink']}; font-weight: 600; letter-spacing: -0.01em; }}
h1 {{ font-size: 1.9rem; }}
h2 {{ font-size: 1.3rem; margin-top: 1.6rem; }}
h3 {{ font-size: 1.05rem; }}

.masthead {{
    background: {C['surface']};
    border: 1px solid {C['line']};
    border-radius: 14px;
    padding: 1.5rem 1.7rem;
    margin-bottom: 1.3rem;
}}
.masthead h1 {{ margin: 0 0 .35rem 0; }}
.masthead p {{ color: {C['muted']}; margin: 0; font-size: .95rem; line-height: 1.5; }}

.card {{
    background: {C['surface']};
    border: 1px solid {C['line']};
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    margin-bottom: .85rem;
}}
.kpi {{
    background: {C['surface']};
    border: 1px solid {C['line']};
    border-radius: 12px;
    padding: 1rem 1.1rem;
    height: 100%;
}}
.kpi .label {{
    color: {C['faint']}; font-size: .72rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: .06em; margin-bottom: .3rem;
}}
.kpi .value {{ color: {C['primary_strong']}; font-size: 1.55rem; font-weight: 700; line-height: 1.15; }}
.kpi .sub {{ color: {C['muted']}; font-size: .78rem; margin-top: .25rem; }}

.pill {{
    display: inline-block; padding: .16rem .6rem; border-radius: 999px;
    font-size: .72rem; font-weight: 600; margin-right: .3rem;
}}
.pill-good {{ background: {C['leaf_soft']}; color: {C['leaf_dark']}; }}
.pill-warn {{ background: {C['turmeric_soft']}; color: #7a6a00; }}
.pill-bad  {{ background: {C['danger_soft']}; color: {C['danger']}; }}
.pill-neutral {{ background: {C['surface_quiet']}; color: {C['muted']}; }}

.note {{
    background: {C['surface_soft']};
    border-left: 3px solid {C['secondary']};
    border-radius: 0 8px 8px 0;
    padding: .75rem 1rem; margin: .6rem 0;
    color: {C['ink_soft']}; font-size: .88rem; line-height: 1.55;
}}
.note-warn {{ background: {C['mango_soft']}; border-left-color: {C['mango']}; }}
.caption {{ color: {C['faint']}; font-size: .78rem; font-style: italic; margin-top: .3rem; }}

div[data-testid="stMetricValue"] {{ color: {C['primary_strong']}; }}
.stButton>button {{
    background: {C['primary']}; color: #fff; border: none;
    border-radius: 8px; font-weight: 600; padding: .45rem 1.1rem;
}}
.stButton>button:hover {{ background: {C['primary_strong']}; color: #fff; }}
.stDataFrame {{ border: 1px solid {C['line']}; border-radius: 10px; }}
</style>
"""

PLOTLY_LAYOUT = dict(
    font=dict(family="Noto Sans, system-ui, sans-serif", size=12, color=C["ink"]),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=C["surface"],
    xaxis=dict(gridcolor=C["grid"], zerolinecolor=C["line_strong"]),
    yaxis=dict(gridcolor=C["grid"], zerolinecolor=C["line_strong"]),
    margin=dict(l=10, r=10, t=42, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    hoverlabel=dict(bgcolor=C["surface"], font_size=12),
)


def setup(title: str) -> None:
    st.set_page_config(page_title=f"{title} · ColdLens", page_icon="🌾", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)


def masthead(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="masthead"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def kpi(label: str, value: str, sub: str = "") -> None:
    st.markdown(
        f'<div class="kpi"><div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'<div class="sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def note(text: str, warn: bool = False) -> None:
    cls = "note note-warn" if warn else "note"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def caption(text: str) -> None:
    st.markdown(f'<div class="caption">{text}</div>', unsafe_allow_html=True)


def pill(text: str, kind: str = "neutral") -> str:
    return f'<span class="pill pill-{kind}">{text}</span>'


@st.cache_data(show_spinner=False)
def load(name: str) -> pd.DataFrame:
    if name == "master":
        return pd.read_csv(DATA / "master_monthly.csv.gz")
    return pd.read_csv(DATA / f"{name}.csv")


def sidebar_footer() -> None:
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<div style='font-size:.76rem;color:{C['faint']};line-height:1.5'>"
        "<b>ColdLens</b><br>Post-harvest supply chain decision support.<br><br>"
        "AGMARKNET daily mandi records, 1,421,838 observations, "
        "six southern states, Jul 2024 – Jul 2026.<br><br>"
        "Information only. Not trading, procurement or financial advice."
        "</div>",
        unsafe_allow_html=True,
    )
