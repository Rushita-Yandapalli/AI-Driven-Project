"""
╔══════════════════════════════════════════════════════════════╗
║   FOOD PRICE VOLATILITY ANALYSIS SYSTEM — INDIA             ║
║   Streamlit Dashboard  |  Agmarknet Agricultural Data       ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os, importlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))
import analytics
importlib.reload(analytics)
from analytics import (
    load_and_preprocess, filter_df, get_price_trend,
    compute_volatility, detect_anomalies, get_seasonal_trends,
    get_commodity_seasonal, city_comparison, get_insights,
)

# ─── THEME / PALETTE ──────────────────────────────────────────
PALETTE = {
    "bg":        "#0D1117",
    "card":      "#161B22",
    "border":    "#30363D",
    "accent1":   "#F78166",   # coral-red
    "accent2":   "#79C0FF",   # sky-blue
    "accent3":   "#56D364",   # green
    "accent4":   "#D2A8FF",   # lavender
    "accent5":   "#FFA657",   # amber
    "text":      "#E6EDF3",
    "subtext":   "#8B949E",
}

PLOTLY_THEME = dict(
    plot_bgcolor  = PALETTE["bg"],
    paper_bgcolor = PALETTE["card"],
    font          = dict(color=PALETTE["text"], family="'JetBrains Mono', monospace"),
    xaxis         = dict(gridcolor=PALETTE["border"], zerolinecolor=PALETTE["border"]),
    yaxis         = dict(gridcolor=PALETTE["border"], zerolinecolor=PALETTE["border"]),
    legend        = dict(bgcolor=PALETTE["card"], bordercolor=PALETTE["border"]),
    margin        = dict(l=40, r=20, t=50, b=40),
)

# ─── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title  = "India Food Price Analytics",
    page_icon   = "🌾",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {{
    background-color: {PALETTE["bg"]};
    color: {PALETTE["text"]};
    font-family: 'Space Grotesk', sans-serif;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {PALETTE["card"]};
    border-right: 1px solid {PALETTE["border"]};
}}
[data-testid="stSidebar"] * {{ color: {PALETTE["text"]} !important; }}

/* ── Main blocks ── */
[data-testid="stAppViewContainer"] {{ background: {PALETTE["bg"]}; }}
[data-testid="block-container"] {{ padding-top: 1rem; }}

/* ── Metric cards ── */
[data-testid="stMetric"] {{
    background: {PALETTE["card"]};
    border: 1px solid {PALETTE["border"]};
    border-radius: 12px;
    padding: 1rem 1.2rem;
    transition: border-color .2s;
}}
[data-testid="stMetric"]:hover {{ border-color: {PALETTE["accent2"]}; }}
[data-testid="stMetricLabel"] {{ color: {PALETTE["subtext"]} !important; font-size:.8rem; text-transform:uppercase; letter-spacing:.07em; }}
[data-testid="stMetricValue"] {{ color: {PALETTE["text"]} !important; font-family:'JetBrains Mono',monospace; font-size:1.6rem; font-weight:700; }}
[data-testid="stMetricDelta"] {{ font-size:.75rem !important; }}

/* ── Tabs ── */
[data-testid="stTabs"] button {{
    color: {PALETTE["subtext"]} !important;
    font-weight:600;
    border-bottom: 2px solid transparent;
    transition: all .2s;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {PALETTE["accent2"]} !important;
    border-bottom-color: {PALETTE["accent2"]} !important;
}}

/* ── Selectbox & sliders ── */
.stSelectbox > div > div, .stMultiSelect > div > div {{
    background: {PALETTE["card"]} !important;
    border: 1px solid {PALETTE["border"]} !important;
    color: {PALETTE["text"]} !important;
    border-radius:8px;
}}
.stSlider > div > div {{ background: {PALETTE["border"]}; }}
.stDateInput > div > div {{
    background: {PALETTE["card"]} !important;
    border: 1px solid {PALETTE["border"]} !important;
    border-radius:8px;
    color: {PALETTE["text"]} !important;
}}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {{ border: 1px solid {PALETTE["border"]}; border-radius:10px; overflow:hidden; }}

/* ── Header banner ── */
.hero-banner {{
    background: linear-gradient(135deg, #161B22 0%, #0D1117 50%, #161B22 100%);
    border: 1px solid {PALETTE["border"]};
    border-radius:16px;
    padding: 1.5rem 2rem;
    margin-bottom:1.5rem;
    display:flex;
    align-items:center;
    gap:1.5rem;
}}
.hero-title {{
    font-family:'JetBrains Mono',monospace;
    font-size:1.7rem;
    font-weight:700;
    color:{PALETTE["text"]};
    line-height:1.2;
}}
.hero-sub {{ color:{PALETTE["subtext"]}; font-size:.9rem; margin-top:.3rem; }}

/* ── Section headers ── */
.section-header {{
    font-family:'JetBrains Mono',monospace;
    font-size:1rem;
    font-weight:700;
    color:{PALETTE["accent2"]};
    letter-spacing:.1em;
    text-transform:uppercase;
    margin: .5rem 0 1rem 0;
    border-left: 3px solid {PALETTE["accent2"]};
    padding-left:.75rem;
}}

/* ── Insight boxes ── */
.insight-box {{
    background: {PALETTE["card"]};
    border: 1px solid {PALETTE["border"]};
    border-radius: 12px;
    padding: 1.2rem;
    height: 100%;
}}
.insight-label {{ color:{PALETTE["subtext"]}; font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; }}
.insight-value {{ color:{PALETTE["text"]}; font-size:1.2rem; font-weight:700; font-family:'JetBrains Mono',monospace; margin-top:.3rem; }}
.insight-tag {{ display:inline-block; font-size:.7rem; padding:.15rem .5rem; border-radius:999px; margin-top:.4rem; font-weight:600; }}
.tag-red   {{ background:rgba(247,129,102,.15); color:{PALETTE["accent1"]}; border:1px solid {PALETTE["accent1"]}; }}
.tag-blue  {{ background:rgba(121,192,255,.12); color:{PALETTE["accent2"]}; border:1px solid {PALETTE["accent2"]}; }}
.tag-green {{ background:rgba(86,211,100,.12);  color:{PALETTE["accent3"]}; border:1px solid {PALETTE["accent3"]}; }}
.tag-amber {{ background:rgba(255,166,87,.12);  color:{PALETTE["accent5"]}; border:1px solid {PALETTE["accent5"]}; }}

/* ── Anomaly badge ── */
.anomaly-spike {{ color: {PALETTE["accent1"]}; font-weight:700; }}
.anomaly-drop  {{ color: {PALETTE["accent3"]}; font-weight:700; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width:6px; }}
::-webkit-scrollbar-track {{ background:{PALETTE["bg"]}; }}
::-webkit-scrollbar-thumb {{ background:{PALETTE["border"]}; border-radius:3px; }}

/* ── Hide Streamlit default chrome ── */
#MainMenu, footer {{ visibility:hidden; }}
.stDeployButton {{ display:none; }}
</style>
""", unsafe_allow_html=True)


# ─── DATA LOADING (cached) ────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "../food_prices.csv")
    return load_and_preprocess(path)


@st.cache_data(show_spinner=False)
def get_anomaly_data(_df):
    return detect_anomalies(_df)


# ─── HERO BANNER ──────────────────────────────────────────────
def render_hero():
    st.markdown("""
    <div class="hero-banner">
        <span style="font-size:2.8rem">🌾</span>
        <div>
            <div class="hero-title">Food Price Volatility Analysis System</div>
            <div class="hero-sub">
                Big Data Analytics · Agmarknet Agricultural Markets · India
                &nbsp;|&nbsp; PySpark · Hive · Streamlit · Plotly
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── SIDEBAR ──────────────────────────────────────────────────
def render_sidebar(df):
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:.5rem 0 1.2rem 0;">
            <span style="font-size:2rem">🌾</span>
            <div style="font-family:'JetBrains Mono',monospace;font-size:.95rem;font-weight:700;color:{PALETTE['text']};margin-top:.3rem;">
                FOOD PRICE<br>ANALYTICS
            </div>
            <div style="color:{PALETTE['subtext']};font-size:.7rem;margin-top:.2rem;">India · Agmarknet</div>
        </div>
        <hr style="border-color:{PALETTE['border']};margin-bottom:1.2rem"/>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Filters</div>', unsafe_allow_html=True)

        all_commodities = sorted(df["commodity"].unique().tolist())
        commodity = st.multiselect("🌽 Commodities", all_commodities, default=all_commodities[:1])

        cities = ["All"] + sorted(df["city"].unique().tolist())
        city   = st.selectbox("🏙️ City / Market", cities)

        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        date_range = st.date_input(
            "📅 Date Range",
            value=(min_date, max_date),
            min_value=min_date, max_value=max_date,
        )
        start_date = date_range[0] if len(date_range) > 0 else min_date
        end_date   = date_range[1] if len(date_range) > 1 else max_date

        st.markdown(f"<hr style='border-color:{PALETTE['border']};margin:1rem 0'/>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Z-Score Threshold</div>', unsafe_allow_html=True)
        z_thresh = st.slider("Anomaly Z-Score", 1.5, 4.0, 2.0, 0.1)

        st.markdown(f"<hr style='border-color:{PALETTE['border']};margin:1rem 0'/>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Trend Frequency</div>', unsafe_allow_html=True)
        freq = st.radio("Aggregate by", ["Daily", "Monthly", "Yearly"], index=1, horizontal=True)
        freq_map = {"Daily": "D", "Monthly": "M", "Yearly": "Y"}

        st.markdown(f"""
        <hr style="border-color:{PALETTE['border']};margin:1rem 0"/>
        <div style="color:{PALETTE['subtext']};font-size:.7rem;text-align:center;line-height:1.6;">
            <b>Dataset:</b> 50,000 records<br>
            <b>Period:</b> 2020–2024<br>
            <b>Source:</b> Agmarknet (synthetic)<br>
            <b>Engine:</b> PySpark + Hive + Pandas
        </div>
        """, unsafe_allow_html=True)

    return commodity, city, start_date, end_date, z_thresh, freq_map[freq]


# ─── KPI CARDS ────────────────────────────────────────────────
def render_kpis(insights, filtered_df):
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.metric("📦 Total Records",    f"{insights['total_records']:,}")
    with c2:
        st.metric("🌽 Commodities",      insights["total_commodities"])
    with c3:
        st.metric("🏙️ Markets",         insights["total_cities"])
    with c4:
        st.metric("💰 Avg Price (₹)",    f"₹{insights['avg_price']:.2f}")
    with c5:
        st.metric("⚠️ Anomalies",        f"{insights['total_anomalies']:,}")
    with c6:
        st.metric("📊 Most Volatile",    insights["most_volatile_commodity"])


# ─── INSIGHT CARDS ─────────────────────────────────────────────
def render_insight_cards(insights):
    st.markdown('<div class="section-header">Key Insights</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    spike = insights.get("top_spike", {})

    with c1:
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-label">🔥 Most Volatile Commodity</div>
            <div class="insight-value">{insights['most_volatile_commodity']}</div>
            <span class="insight-tag tag-red">CV: {insights['most_volatile_cv']}%</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-label">🏙️ Highest Market Fluctuation</div>
            <div class="insight-value">{insights['city_highest_fluctuation']}</div>
            <span class="insight-tag tag-amber">CV: {insights['city_fluctuation_cv']}%</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        if spike:
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-label">⚠️ Highest Price Spike</div>
                <div class="insight-value">₹{spike.get('price','N/A')}</div>
                <div style="color:{PALETTE['subtext']};font-size:.78rem;margin-top:.3rem;">
                    {spike.get('commodity','')} · {spike.get('city','')}<br>
                    {spike.get('date','')}
                </div>
                <span class="insight-tag tag-red">Z-score: {spike.get('z_score','')}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-label">⚠️ Highest Price Spike</div>
                <div class="insight-value">N/A</div>
            </div>
            """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-label">📊 Total Anomalies Detected</div>
            <div class="insight-value">{insights['total_anomalies']:,}</div>
            <span class="insight-tag tag-blue">Z-score method</span>
        </div>
        """, unsafe_allow_html=True)


# ─── TAB 1: PRICE TRENDS ──────────────────────────────────────
def tab_trends(df, freq):
    st.markdown('<div class="section-header">Price Trend Over Time</div>', unsafe_allow_html=True)

    trend = get_price_trend(df, freq)
    if trend.empty:
        st.info("No data for selected filters.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["period"], y=trend["avg_price"],
        name="Avg Price",
        line=dict(color=PALETTE["accent2"], width=2),
        fill="tozeroy", fillcolor="rgba(121,192,255,0.08)",
        hovertemplate="<b>%{x}</b><br>₹%{y:.2f}<extra></extra>",
    ))
    if "ma7" in trend.columns:
        fig.add_trace(go.Scatter(
            x=trend["period"], y=trend["ma7"],
            name="7-period MA",
            line=dict(color=PALETTE["accent5"], width=1.5, dash="dot"),
            hovertemplate="MA7: ₹%{y:.2f}<extra></extra>",
        ))
    if "ma30" in trend.columns:
        fig.add_trace(go.Scatter(
            x=trend["period"], y=trend["ma30"],
            name="30-period MA",
            line=dict(color=PALETTE["accent4"], width=1.5, dash="dash"),
            hovertemplate="MA30: ₹%{y:.2f}<extra></extra>",
        ))
    fig.update_layout(
        **PLOTLY_THEME,
        title="Price Trend with Moving Averages",
        height=380,
        xaxis_title="Date",
        yaxis_title="Price (₹/Quintal)",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Mini commodity multi-line
    st.markdown('<div class="section-header" style="margin-top:1.5rem">Commodity-wise Monthly Trends</div>', unsafe_allow_html=True)
    monthly_comm = df.groupby(["year_month", "commodity"])["price"].mean().reset_index()
    monthly_comm["period"] = pd.PeriodIndex(monthly_comm["year_month"], freq="M").to_timestamp()
    monthly_comm = monthly_comm.sort_values("period")

    fig2 = px.line(
        monthly_comm, x="period", y="price", color="commodity",
        title="All Commodities — Monthly Average Price",
        labels={"price": "Price (₹)", "period": "Month"},
        color_discrete_sequence=[
            PALETTE["accent1"], PALETTE["accent2"], PALETTE["accent3"],
            PALETTE["accent4"], PALETTE["accent5"], "#58A6FF",
            "#BC8CFF", "#FF7B72", "#3FB950", "#D29922",
            "#A5D6FF", "#FF9E64",
        ],
    )
    fig2.update_layout(**PLOTLY_THEME, height=360, hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)


# ─── TAB 2: VOLATILITY ────────────────────────────────────────
def tab_volatility(df):
    st.markdown('<div class="section-header">Price Volatility Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Commodity volatility bar
    vol_comm = compute_volatility(df, "commodity")
    with col1:
        fig = px.bar(
            vol_comm, x="cv", y="commodity", orientation="h",
            title="Commodity Volatility (CV %)",
            color="cv", color_continuous_scale=["#56D364", "#FFA657", "#F78166"],
            labels={"cv": "Coeff of Variation (%)", "commodity": ""},
        )
        fig.update_layout(**PLOTLY_THEME, height=380, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # City volatility
    vol_city = compute_volatility(df, "city")
    with col2:
        fig2 = px.bar(
            vol_city.head(20), x="cv", y="city", orientation="h",
            title="City Volatility (CV %)",
            color="cv", color_continuous_scale=["#79C0FF", "#D2A8FF", "#F78166"],
            labels={"cv": "Coeff of Variation (%)", "city": ""},
        )
        fig2.update_layout(**PLOTLY_THEME, height=380, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Std dev scatter
    st.markdown('<div class="section-header" style="margin-top:1.5rem">Volatility vs Mean Price</div>', unsafe_allow_html=True)
    fig3 = px.scatter(
        vol_comm, x="mean_price", y="std_dev", size="count",
        color="cv", color_continuous_scale="RdYlGn_r",
        text="commodity",
        title="Risk-Return Map: Mean Price vs Std Dev (bubble = record count)",
        labels={"mean_price": "Mean Price (₹)", "std_dev": "Std Deviation", "cv": "CV %"},
    )
    fig3.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="#30363D")))
    fig3.update_layout(**PLOTLY_THEME, height=380)
    st.plotly_chart(fig3, use_container_width=True)

    # Table
    st.markdown('<div class="section-header" style="margin-top:1.5rem">Full Volatility Table</div>', unsafe_allow_html=True)
    st.dataframe(
        vol_comm.style.background_gradient(subset=["cv"], cmap="RdYlGn_r")
                      .format({"mean_price": "₹{:.2f}", "std_dev": "{:.2f}", "cv": "{:.2f}%",
                                "min_price": "₹{:.2f}", "max_price": "₹{:.2f}"}),
        use_container_width=True, height=320,
    )


# ─── TAB 3: ANOMALIES ─────────────────────────────────────────
def tab_anomalies(df, z_thresh):
    st.markdown('<div class="section-header">Anomaly Detection — Z-Score Method</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{PALETTE['card']};border:1px solid {PALETTE['border']};
         border-radius:10px;padding:.8rem 1rem;margin-bottom:1rem;font-size:.82rem;color:{PALETTE['subtext']};">
        <b style="color:{PALETTE['text']}">Method:</b>
        Z-score = (price − mean) / stddev, computed per (commodity, city) pair.
        Flagged when |z| &gt; <b style="color:{PALETTE['accent1']}">{z_thresh}</b>.
        🔺 Spike = price &gt; threshold &nbsp;|&nbsp; 🔻 Drop = price &lt; −threshold
    </div>
    """, unsafe_allow_html=True)

    df_z, anomalies = detect_anomalies(df, z_thresh)

    st.metric("Total Anomalies", f"{len(anomalies):,}", delta=f"Z > {z_thresh}")

    # Scatter with anomalies highlighted
    st.markdown('<div class="section-header" style="margin-top:1rem">Price Scatter — Anomalies Highlighted</div>', unsafe_allow_html=True)

    sample = df_z.sample(min(5000, len(df_z)), random_state=42)
    fig = go.Figure()
    normal = sample[~sample["is_anomaly"]]
    spikes = sample[sample["z_score"] > z_thresh]
    drops  = sample[sample["z_score"] < -z_thresh]

    fig.add_trace(go.Scatter(
        x=normal["date"], y=normal["price"],
        mode="markers", name="Normal",
        marker=dict(color="rgba(121,192,255,0.25)", size=3),
        hovertemplate="%{x}<br>₹%{y:.2f}<extra>Normal</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=spikes["date"], y=spikes["price"],
        mode="markers", name="Price Spike 🔺",
        marker=dict(color=PALETTE["accent1"], size=7, symbol="triangle-up",
                    line=dict(width=1, color="white")),
        hovertemplate="%{x}<br>₹%{y:.2f}<br>Z: %{customdata:.2f}<extra>SPIKE</extra>",
        customdata=spikes["z_score"],
    ))
    fig.add_trace(go.Scatter(
        x=drops["date"], y=drops["price"],
        mode="markers", name="Price Drop 🔻",
        marker=dict(color=PALETTE["accent3"], size=7, symbol="triangle-down",
                    line=dict(width=1, color="white")),
        hovertemplate="%{x}<br>₹%{y:.2f}<br>Z: %{customdata:.2f}<extra>DROP</extra>",
        customdata=drops["z_score"],
    ))
    fig.update_layout(**PLOTLY_THEME, height=380,
                      title="Price vs Time — Anomaly Scatter",
                      xaxis_title="Date", yaxis_title="Price (₹)")
    st.plotly_chart(fig, use_container_width=True)

    # Z-score distribution
    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.histogram(
            df_z.sample(min(5000, len(df_z)), random_state=1),
            x="z_score", nbins=60,
            title="Z-Score Distribution",
            color_discrete_sequence=[PALETTE["accent2"]],
        )
        fig2.add_vline(x=z_thresh,  line_dash="dash", line_color=PALETTE["accent1"],
                       annotation_text=f"+{z_thresh}", annotation_font_color=PALETTE["accent1"])
        fig2.add_vline(x=-z_thresh, line_dash="dash", line_color=PALETTE["accent3"],
                       annotation_text=f"-{z_thresh}", annotation_font_color=PALETTE["accent3"])
        fig2.update_layout(**PLOTLY_THEME, height=320)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        anom_comm = anomalies.groupby("commodity").size().reset_index(name="anomaly_count")
        anom_comm = anom_comm.sort_values("anomaly_count", ascending=False)
        fig3 = px.bar(
            anom_comm, x="commodity", y="anomaly_count",
            title="Anomalies per Commodity",
            color="anomaly_count",
            color_continuous_scale=["#56D364", "#FFA657", "#F78166"],
        )
        fig3.update_layout(**PLOTLY_THEME, height=320, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    # Anomaly table
    st.markdown('<div class="section-header" style="margin-top:.5rem">Top Anomalies Table</div>', unsafe_allow_html=True)
    if not anomalies.empty:
        display_cols = ["date", "commodity", "city", "price", "z_score", "spike_type"]
        anom_display = anomalies[display_cols].sort_values("z_score", key=abs, ascending=False).head(100)
        anom_display["price"] = anom_display["price"].map("₹{:.2f}".format)
        anom_display["z_score"] = anom_display["z_score"].map("{:.3f}".format)
        st.dataframe(anom_display, use_container_width=True, height=300)
    else:
        st.info("No anomalies detected with current threshold.")


# ─── TAB 4: SEASONAL ──────────────────────────────────────────
def tab_seasonal(df):
    st.markdown('<div class="section-header">Seasonal Price Patterns</div>', unsafe_allow_html=True)

    seasonal = get_seasonal_trends(df)

    fig = px.bar(
        seasonal, x="month", y="avg_price",
        title="Month-wise Average Price — All Commodities",
        color="avg_price", color_continuous_scale="Plasma",
        labels={"month": "Month", "avg_price": "Avg Price (₹)"},
    )
    fig.update_layout(**PLOTLY_THEME, height=340, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap: commodity × month
    st.markdown('<div class="section-header" style="margin-top:1.5rem">Commodity × Month Price Heatmap</div>', unsafe_allow_html=True)
    pivot = df.pivot_table(index="commodity", columns="month", values="price", aggfunc="mean")
    pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][:len(pivot.columns)]

    fig2 = px.imshow(
        pivot,
        color_continuous_scale="RdYlGn_r",
        title="Average Price Heatmap (Commodity × Month)",
        labels=dict(x="Month", y="Commodity", color="Price (₹)"),
        aspect="auto",
    )
    fig2.update_layout(**PLOTLY_THEME, height=420)
    st.plotly_chart(fig2, use_container_width=True)

    # Polar / radial seasonal per commodity
    st.markdown('<div class="section-header" style="margin-top:1.5rem">Seasonal Radar — Pick Commodity</div>', unsafe_allow_html=True)
    selected = st.selectbox("Commodity for radar chart", sorted(df["commodity"].unique()), key="radar_sel")

    comm_data = df[df["commodity"] == selected].groupby("month")["price"].mean().reset_index()
    comm_data["month_name"] = pd.to_datetime(comm_data["month"], format="%m").dt.strftime("%b")

    fig3 = go.Figure(go.Scatterpolar(
        r=comm_data["price"],
        theta=comm_data["month_name"],
        fill="toself",
        fillcolor="rgba(121,192,255,0.15)",
        line=dict(color=PALETTE["accent2"], width=2),
        name=selected,
    ))
    fig3.update_layout(
        polar=dict(
            bgcolor=PALETTE["card"],
            radialaxis=dict(gridcolor=PALETTE["border"], color=PALETTE["subtext"]),
            angularaxis=dict(gridcolor=PALETTE["border"]),
        ),
        paper_bgcolor=PALETTE["card"],
        font=dict(color=PALETTE["text"]),
        title=f"Seasonal Price Pattern — {selected}",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ─── TAB 5: CITY COMPARISON ───────────────────────────────────
def tab_city_comparison(df):
    st.markdown('<div class="section-header">City / Market Comparison</div>', unsafe_allow_html=True)

    comp = city_comparison(df)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            comp, x="avg_price", y="city", orientation="h",
            color="avg_price", color_continuous_scale="Blues",
            title="Average Price by City",
            labels={"avg_price": "Avg Price (₹)", "city": ""},
        )
        fig.update_layout(**PLOTLY_THEME, height=500, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            comp, x="cv", y="city", orientation="h",
            color="cv", color_continuous_scale="RdYlGn_r",
            title="Price Volatility by City (CV %)",
            labels={"cv": "Coeff of Variation (%)", "city": ""},
        )
        fig2.update_layout(**PLOTLY_THEME, height=500, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Commodity × City pivot heatmap
    st.markdown('<div class="section-header" style="margin-top:1.5rem">Commodity × City Price Matrix</div>', unsafe_allow_html=True)
    pivot_cc = df.pivot_table(index="commodity", columns="city", values="price", aggfunc="mean")
    fig3 = px.imshow(
        pivot_cc,
        color_continuous_scale="Viridis",
        title="Average Price Matrix — Commodity vs City",
        labels=dict(x="City", y="Commodity", color="Price (₹)"),
        aspect="auto",
    )
    fig3.update_layout(**PLOTLY_THEME, height=450)
    st.plotly_chart(fig3, use_container_width=True)

    # City selection for price distribution
    st.markdown('<div class="section-header" style="margin-top:1.5rem">City Price Distribution</div>', unsafe_allow_html=True)
    sel_cities = st.multiselect("Select Cities to Compare", sorted(df["city"].unique()), default=sorted(df["city"].unique())[:5])
    if sel_cities:
        city_data = df[df["city"].isin(sel_cities)]
        fig4 = px.box(
            city_data, x="city", y="price", color="city",
            title="Price Distribution per City (Box Plot)",
            labels={"price": "Price (₹)", "city": "City"},
            color_discrete_sequence=[
                PALETTE["accent1"], PALETTE["accent2"], PALETTE["accent3"],
                PALETTE["accent4"], PALETTE["accent5"],
            ],
        )
        fig4.update_layout(**PLOTLY_THEME, height=380, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)



# ─── TAB 6: COMMODITY COMPARISON ──────────────────────────────
def tab_commodity_comparison(df_full, city, start_date, end_date):
    st.markdown('<div class="section-header">Commodity Comparison Analysis</div>', unsafe_allow_html=True)

    # Local filter for commodities (ignoring global commodity filter)
    df_base = filter_df(df_full, None, city, start_date, end_date)
    
    all_commodities = sorted(df_base["commodity"].unique().tolist())
    default_sel = all_commodities[:3] if len(all_commodities) >= 3 else all_commodities
    
    sel_commodities = st.multiselect("Select Commodities to Compare", all_commodities, default=default_sel)
    
    if not sel_commodities:
        st.info("Select at least one commodity to compare.")
        return

    comp_df = df_base[df_base["commodity"].isin(sel_commodities)]

    # 1. Price Trend Comparison
    st.markdown('<div class="section-header" style="margin-top:1.5rem">Price Trends Comparison</div>', unsafe_allow_html=True)
    trend_data = comp_df.groupby(["year_month", "commodity"])["price"].mean().reset_index()
    trend_data["period"] = pd.PeriodIndex(trend_data["year_month"], freq="M").to_timestamp()
    trend_data = trend_data.sort_values("period")

    fig1 = px.line(
        trend_data, x="period", y="price", color="commodity",
        title="Monthly Average Price Comparison",
        labels={"price": "Price (₹)", "period": "Month"},
        color_discrete_sequence=[
            PALETTE["accent1"], PALETTE["accent2"], PALETTE["accent3"],
            PALETTE["accent4"], PALETTE["accent5"], "#58A6FF",
        ],
    )
    fig1.update_layout(**PLOTLY_THEME, height=400, hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)

    # 2. Box Plot Distribution
    with col1:
        st.markdown('<div class="section-header" style="margin-top:1.5rem">Price Distribution</div>', unsafe_allow_html=True)
        fig2 = px.box(
            comp_df, x="commodity", y="price", color="commodity",
            title="Price Range & Spread",
            labels={"price": "Price (₹)", "commodity": ""},
            color_discrete_sequence=[
                PALETTE["accent1"], PALETTE["accent2"], PALETTE["accent3"],
                PALETTE["accent4"], PALETTE["accent5"],
            ],
        )
        fig2.update_layout(**PLOTLY_THEME, height=400, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # 3. Volatility Comparison
    with col2:
        st.markdown('<div class="section-header" style="margin-top:1.5rem">Volatility Comparison (CV %)</div>', unsafe_allow_html=True)
        vol_data = compute_volatility(comp_df, "commodity")
        fig3 = px.bar(
            vol_data, x="cv", y="commodity", orientation="h",
            color="cv", color_continuous_scale=["#56D364", "#FFA657", "#F78166"],
            title="Relative Price Risk (Coefficient of Variation)",
            labels={"cv": "CV (%)", "commodity": ""},
        )
        fig3.update_layout(**PLOTLY_THEME, height=400, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    # 4. Correlation Heatmap (if enough data)
    if len(sel_commodities) > 1:
        st.markdown('<div class="section-header" style="margin-top:1.5rem">Price Correlation Matrix</div>', unsafe_allow_html=True)
        pivot_corr = comp_df.pivot_table(index="year_month", columns="commodity", values="price", aggfunc="mean")
        corr_matrix = pivot_corr.corr()
        
        fig4 = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            title="Commodity Price Correlation (Monthly)",
            labels=dict(color="Correlation"),
            aspect="auto",
        )
        fig4.update_layout(**PLOTLY_THEME, height=450)
        st.plotly_chart(fig4, use_container_width=True)


# ─── TAB 7: RAW DATA ──────────────────────────────────────────

def tab_raw_data(df):
    st.markdown('<div class="section-header">Raw / Processed Dataset</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Columns", df.shape[1])
    c3.metric("Date Range", f"{df['date'].min().date()} → {df['date'].max().date()}")
    c4.metric("Commodities", df["commodity"].nunique())

    st.markdown(f"<hr style='border-color:{PALETTE['border']};margin:.8rem 0'/>", unsafe_allow_html=True)

    col_filter = st.multiselect(
        "Select columns to display",
        df.columns.tolist(),
        default=["date", "commodity", "city", "price", "Min_Price", "Max_Price", "avg_price", "State", "year", "month"],
    )
    n_rows = st.slider("Rows to preview", 50, 1000, 200, 50)

    display = df[col_filter].head(n_rows).copy()
    if "price" in display.columns:
        display["price"] = display["price"].map("₹{:.2f}".format)
    if "avg_price" in display.columns:
        display["avg_price"] = display["avg_price"].map("₹{:.2f}".format)

    st.dataframe(display, use_container_width=True, height=420)

    # Describe
    st.markdown('<div class="section-header" style="margin-top:1rem">Statistical Summary</div>', unsafe_allow_html=True)
    num_cols = df[["price", "Min_Price", "Max_Price", "avg_price"]].describe().T
    st.dataframe(num_cols.style.format("{:.2f}"), use_container_width=True)


# ─── MAIN APP ─────────────────────────────────────────────────
def main():
    with st.spinner("🌾 Loading and processing data..."):
        df_full = load_data()

    render_hero()
    commodity, city, start_date, end_date, z_thresh, freq = render_sidebar(df_full)

    # Apply filters
    df = filter_df(df_full, commodity, city, start_date, end_date)

    if df.empty:
        st.error("⚠️ No data for the selected filters. Please adjust.")
        return

    # Anomalies on filtered data
    _, anomalies = detect_anomalies(df, z_thresh)
    insights = get_insights(df, anomalies)

    # KPIs
    render_kpis(insights, df)

    st.markdown(f"<div style='margin:.8rem 0'/>", unsafe_allow_html=True)

    # Insight cards
    render_insight_cards(insights)

    st.markdown(f"<div style='margin:1.5rem 0'/>", unsafe_allow_html=True)

    # Main tabs
    tabs = st.tabs([
        "📈 Price Trends",
        "📊 Volatility",
        "⚠️ Anomalies",
        "🌡️ Seasonal",
        "🏙️ City Comparison",
        "⚖️ Commodity Comparison",
        "🗄️ Raw Data",
    ])

    with tabs[0]: tab_trends(df, freq)
    with tabs[1]: tab_volatility(df)
    with tabs[2]: tab_anomalies(df, z_thresh)
    with tabs[3]: tab_seasonal(df)
    with tabs[4]: tab_city_comparison(df)
    with tabs[5]: tab_commodity_comparison(df_full, city, start_date, end_date)
    with tabs[6]: tab_raw_data(df)


if __name__ == "__main__":
    main()
# --- End of File ---
