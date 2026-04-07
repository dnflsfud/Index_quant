# dashboard.py
# ──────────────────────────────────────────────────────────────
# Factor & Metric Analytics Dashboard  (Streamlit ≥ 1.x)
# Default CSV folder : C:\Users\westl\PycharmProjects\pythonProject\venv\Factor
# ──────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import base64
from typing import Union, Optional  # 이 줄 추가


st.set_page_config(page_title="Factor & Metric Dashboard",
                   page_icon="📊", layout="wide")

st.title("📊 Factor & Metric Analytics Dashboard")

# ───────────────────────── Default path ───────────────────────
DEFAULT_DIR = Path(r"C:\Users\westl\PycharmProjects\pythonProject\venv_vf\Factor")

st.sidebar.header("📂 Result-CSV Folder")
data_dir = Path(st.sidebar.text_input("Folder path", value=str(DEFAULT_DIR)))

if not data_dir.exists():
    st.sidebar.error("❌ Folder does not exist.")
    st.stop()

# Required file names
FILES = {
    "factor":          "factor_portfolio_returns.csv",
    "metric":          "metric_portfolio_returns.csv",
    "weights_growth":  "growth_weights.csv",          # example weights file
    # quantile files are assumed to be named like 'factor_growth_quantiles.csv'
}

# ───────────────────────── CSV loader ─────────────────────────
@st.cache_data(show_spinner=False)
@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> Optional[pd.DataFrame]:  # 또는 Union[pd.DataFrame, None]
    if path.exists():
        try:
            df = pd.read_csv(path)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
            return df
        except Exception as e:
            st.error(f"Error loading {path.name}: {e}")
    return None

factor_ret_df  = load_csv(data_dir / FILES["factor"])
metric_ret_df  = load_csv(data_dir / FILES["metric"])

if factor_ret_df is None or metric_ret_df is None:
    st.warning("CSV files are not found yet. Run factor_run.py first.")
    st.stop()

# ───────────────────────── utilities ─────────────────────────
def compute_cum(series: pd.Series, start=None, end=None):
    if start:
        start = pd.Timestamp(start)  # date를 timestamp로 변환
        series = series[series.index >= start]
    if end:
        end = pd.Timestamp(end)  # date를 timestamp로 변환
        series = series[series.index <= end]
    return (1 + series).cumprod()

def perf_metrics(ret: pd.Series, window=252):
    if ret.empty:
        return dict(ann_return=np.nan, ann_vol=np.nan,
                    sharpe=np.nan, mdd=np.nan)
    ann_return = (1 + ret).prod() ** (252/len(ret)) - 1
    ann_vol    = ret.std() * np.sqrt(252)
    sharpe     = ann_return / ann_vol if ann_vol else np.nan
    cum = (1+ret).cumprod()
    mdd = (cum / cum.cummax() - 1).min()
    return dict(ann_return=ann_return, ann_vol=ann_vol,
                sharpe=sharpe, mdd=mdd)

# ───────────────────────── navigation ────────────────────────
page = st.sidebar.radio("Choose page", [
    "Cumulative Performance – Factors",
    "Performance Table – Factors",
    "Factor Quantile Constituents",
    "Cumulative Performance – Metrics",
    "Performance Table – Metrics"
])

# ───────────────────── 1. Cumulative factor perf ─────────────
if page == "Cumulative Performance – Factors":
    st.subheader("Cumulative Returns of Factor Portfolios")

    factor_cols = [c for c in factor_ret_df.columns if c.endswith("_return")]
    selected = st.multiselect("Select factors", options=factor_cols,
                              default=factor_cols[:6])

    dmin, dmax = factor_ret_df["date"].min().date(), factor_ret_df["date"].max().date()
    c1, c2 = st.columns(2)
    with c1:
        sd = st.date_input("Start date", dmin, dmin, dmax)
    with c2:
        ed = st.date_input("End date", dmax, dmin, dmax)

    fig = go.Figure()
    factor_ret_df.set_index("date", inplace=True)
    for col in selected:
        cum = compute_cum(factor_ret_df[col], sd, ed)
        fig.add_trace(go.Scatter(x=cum.index, y=cum,
                                 mode='lines', name=col.replace("_return","")))
    fig.update_layout(template="plotly_white", yaxis_title="Cumulative return",
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)

# ───────────────────── 2. Factor performance table ───────────
elif page == "Performance Table – Factors":
    st.subheader("Performance Metrics (1m/3m/6m/12m/3y/5y/Total)")
    windows = {
        "1M": 21, "3M": 63, "6M": 126,
        "12M": 252, "3Y": 252*3, "5Y": 252*5,
        "Total": len(factor_ret_df)
    }

    rows = {}
    factor_ret_df.set_index("date", inplace=True)
    for col in [c for c in factor_ret_df.columns if c.endswith("_return")]:
        ret = factor_ret_df[col].dropna()
        stats = {}
        for label, win in windows.items():
            metrics = perf_metrics(ret.tail(win))
            stats[f"{label} Ann.Return"] = f"{metrics['ann_return']*100:.2f}%"
            stats[f"{label} Ann.Vol"]    = f"{metrics['ann_vol']*100:.2f}%"
            stats[f"{label} Sharpe"]     = f"{metrics['sharpe']:.2f}"
        rows[col.replace("_return","")] = stats

    st.dataframe(pd.DataFrame(rows).T)

# ───────────────────── 3. Factor quantile table ──────────────
elif page == "Factor Quantile Constituents":
    st.subheader("Factor Quantile Constituents")

    factor_list = ["growth","value","momentum","low_vol","quality"]
    fac = st.selectbox("Factor", factor_list)
    qfile = data_dir / f"factor_{fac}_quantiles.csv"
    qdf = load_csv(qfile)
    if qdf is None:
        st.warning(f"{qfile.name} not found.")
    else:
        dates = sorted(qdf["date"].unique())
        dsel = st.selectbox("Date", options=dates,
                            format_func=lambda x: pd.to_datetime(x).date(),
                            index=len(dates)-1)
        show = qdf[qdf["date"]==dsel]
        for q in sorted(show["quantile"].unique()):
            with st.expander(f"Quantile {int(q)} | {len(show[show['quantile']==q])} stocks"):
                st.table(show[show["quantile"]==q][["stock","quantile"]])

# ───────────────────── 4. Cumulative metric perf ─────────────
elif page == "Cumulative Performance – Metrics":
    st.subheader("Cumulative Returns of Metric Portfolios")

    metric_cols = [c for c in metric_ret_df.columns if c.endswith("_return")]
    sel = st.multiselect("Select metrics (max 5)", metric_cols, metric_cols[:5])
    dmin, dmax = metric_ret_df["date"].min().date(), metric_ret_df["date"].max().date()
    sdate = st.date_input("Start date", dmin, dmin, dmax, key="m_start")
    edate = st.date_input("End date",   dmax, dmin, dmax, key="m_end")

    metric_ret_df.set_index("date", inplace=True)
    figm = go.Figure()
    for col in sel[:5]:
        cum = compute_cum(metric_ret_df[col], sdate, edate)
        figm.add_trace(go.Scatter(x=cum.index, y=cum, mode='lines',
                                  name=col.replace("_return","")))
    figm.update_layout(template="plotly_white", yaxis_title="Cumulative return")
    st.plotly_chart(figm, use_container_width=True)

# ───────────────────── 5. Metric performance table ───────────
else:
    st.subheader("Metric Performance Metrics")
    metric_cols = [c for c in metric_ret_df.columns if c.endswith("_return")]
    rows = {}
    metric_ret_df.set_index("date", inplace=True)
    for col in metric_cols:
        ret = metric_ret_df[col].dropna()
        stats = {}
        for label, win in {"1M":21,"3M":63,"6M":126,"12M":252,"3Y":756,"5Y":1260,"Total":len(ret)}.items():
            m = perf_metrics(ret.tail(win))
            stats[f"{label} AnnR"] = f"{m['ann_return']*100:.2f}%"
            stats[f"{label} AnnV"] = f"{m['ann_vol']*100:.2f}%"
            stats[f"{label} Sharpe"] = f"{m['sharpe']:.2f}"
        rows[col.replace("_return","")] = stats
    st.dataframe(pd.DataFrame(rows).T)
