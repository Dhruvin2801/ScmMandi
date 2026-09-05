"""Shared theme, data loaders and UI primitives for the ColdLens dashboard."""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "data"

# Green palette — matches the project workbook and slide deck.
C = {
    "frame": "#F1F8F3",
    "surface": "#FFFFFF",
    "surface_soft": "#EAF4EC",
    "card": "#DCEEE1",
    "card_deep": "#C9E5D1",
    "ink": "#12251A",
    "ink_soft": "#22402E",
    "muted": "#4E6B58",
    "faint": "#6B8574",
    "line": "#C3E0CB",
    "line_strong": "#A5D2B1",
    "band": "#1B4332",
    "primary": "#2D6A4F",
    "primary_strong": "#1B4332",
    "accent": "#52B788",
    "leaf": "#74C69D",
    "leaf_soft": "#B7E4C7",
    "secondary": "#95C7A6",
    "range": "#B7D9C2",
    "turmeric": "#E9C46A",
    "clay": "#C08552",
    "grid": "#DCEBE1",
    "danger": "#B0553F",
    "danger_soft": "#F7E4DE",
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Noto Sans', system-ui, sans-serif;
    color: {C['ink']};
}}
.stApp {{
    background:
      radial-gradient(1200px 500px at 12% -8%, {C['card']} 0%, rgba(255,255,255,0) 60%),
      {C['frame']};
}}
section[data-testid="stSidebar"] {{
    background: {C['surface_soft']};
    border-right: 1px solid {C['line']};
}}
section[data-testid="stSidebar"] * {{ color: {C['ink_soft']}; }}
#MainMenu, footer {{ visibility: hidden; }}
.block-container {{ padding-top: 2.0rem; max-width: 1200px; }}

h1, h2, h3 {{ color: {C['band']}; font-weight: 600; letter-spacing: -0.01em; }}
h1 {{ font-size: 1.95rem; }}
h2 {{ font-size: 1.3rem; margin-top: 1.7rem; }}
h3 {{ font-size: 1.05rem; }}

.masthead {{
    background: linear-gradient(135deg, {C['band']} 0%, {C['primary']} 100%);
    border-radius: 14px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.4rem;
    border-left: 5px solid {C['accent']};
}}
.masthead h1 {{ margin: 0 0 .4rem 0; color: #FFFFFF; }}
.masthead p {{ color: {C['leaf_soft']}; margin: 0; font-size: .95rem; line-height: 1.55; }}

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
    border-top: 4px solid {C['primary']};
    border-radius: 10px;
    padding: .95rem 1.05rem;
    height: 100%;
}}
.kpi .label {{
    color: {C['faint']}; font-size: .70rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .07em; margin-bottom: .3rem;
}}
.kpi .value {{ color: {C['primary']}; font-size: 1.6rem; font-weight: 700; line-height: 1.15; }}
.kpi .sub {{ color: {C['muted']}; font-size: .78rem; margin-top: .25rem; }}

.pill {{
    display: inline-block; padding: .18rem .65rem; border-radius: 999px;
    font-size: .72rem; font-weight: 700; margin-right: .35rem;
}}
.pill-good {{ background: {C['leaf_soft']}; color: {C['band']}; }}
.pill-warn {{ background: #FBF0D4; color: #7A5E14; }}
.pill-bad  {{ background: {C['danger_soft']}; color: {C['danger']}; }}
.pill-neutral {{ background: {C['card']}; color: {C['ink_soft']}; }}

.note {{
    background: {C['card']};
    border-left: 4px solid {C['primary']};
    border-radius: 0 8px 8px 0;
    padding: .8rem 1.05rem; margin: .65rem 0;
    color: {C['ink_soft']}; font-size: .89rem; line-height: 1.6;
}}
.note-warn {{ background: #FBF3DF; border-left-color: {C['turmeric']}; }}
.caption {{ color: {C['faint']}; font-size: .78rem; font-style: italic; margin-top: .3rem; }}

div[data-testid="stMetricValue"] {{ color: {C['primary']}; }}
.stButton>button {{
    background: {C['primary']}; color: #fff; border: none;
    border-radius: 8px; font-weight: 600; padding: .5rem 1.2rem;
}}
.stButton>button:hover {{ background: {C['band']}; color: #fff; }}
.stDataFrame {{ border: 1px solid {C['line']}; border-radius: 10px; }}

.stTabs [data-baseweb="tab-list"] {{ gap: .4rem; border-bottom: 1px solid {C['line']}; }}
.stTabs [data-baseweb="tab"] {{
    background: {C['card']}; border-radius: 8px 8px 0 0;
    padding: .55rem 1.1rem; font-weight: 600; color: {C['ink_soft']};
}}
.stTabs [aria-selected="true"] {{ background: {C['primary']} !important; color: #FFFFFF !important; }}
</style>
"""

PLOTLY_LAYOUT = dict(
    font=dict(family="Noto Sans, system-ui, sans-serif", size=12, color=C["ink"]),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=C["surface"],
    xaxis=dict(gridcolor=C["grid"], zerolinecolor=C["line_strong"]),
    yaxis=dict(gridcolor=C["grid"], zerolinecolor=C["line_strong"]),
    margin=dict(l=10, r=10, t=44, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    hoverlabel=dict(bgcolor=C["surface"], font_size=12),
    colorway=[C["primary"], C["leaf"], C["accent"], C["secondary"], C["range"], C["clay"]],
)


def setup(title: str) -> None:
    st.set_page_config(page_title=f"{title} · ColdLens", page_icon="🌿", layout="wide")
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
        f"<div style='font-size:.76rem;color:{C['muted']};line-height:1.55'>"
        f"<b style='color:{C['band']}'>ColdLens</b><br>Post-harvest supply chain decision support.<br><br>"
        "AGMARKNET daily mandi records, 1,421,838 observations, "
        "six southern states, Jul 2024 – Jul 2026.<br><br>"
        "Information only. Not trading, procurement or financial advice."
        "</div>",
        unsafe_allow_html=True,
    )  
@st.cache_data
def load_data():
    return pd.read_csv("data/master_monthly.csv.gz")
