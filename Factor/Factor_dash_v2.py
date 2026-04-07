# dashboard.py
# ──────────────────────────────────────────────────────────────
# Factor & Metric Analytics Dashboard  (Streamlit ≥ 1.x)
# Default CSV folder : C:\Users\westl\PycharmProjects\pythonProject\venv_vf\Factor
# ──────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import base64
from typing import Union, Optional
import plotly.express as px

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
    "factor": "factor_portfolio_returns.csv",
    "metric": "metric_portfolio_returns.csv",
    "weights_growth": "growth_weights.csv",  # example weights file
}


# ───────────────────────── CSV loader ─────────────────────────
@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> Optional[pd.DataFrame]:
    if path.exists():
        try:
            df = pd.read_csv(path)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
            return df
        except Exception as e:
            st.error(f"Error loading {path.name}: {e}")
    return None


factor_ret_df = load_csv(data_dir / FILES["factor"])
metric_ret_df = load_csv(data_dir / FILES["metric"])

if factor_ret_df is None or metric_ret_df is None:
    st.warning("CSV files are not found yet. Run factor_portfolio_optimized.py first.")
    st.stop()


# ───────────────────────── utilities ─────────────────────────
def compute_cum(series: pd.Series, start=None, end=None):
    if start:
        start = pd.Timestamp(start)  # Convert date to Timestamp
        series = series[series.index >= start]
    if end:
        end = pd.Timestamp(end)  # Convert date to Timestamp
        series = series[series.index <= end]

    # Handle empty series
    if series.empty:
        return pd.Series([1.0], index=[pd.Timestamp.now()])

    # Handle series with all zeros
    if (series == 0).all():
        st.warning(f"Warning: All values in series are zero")
        # Add small random variation for visualization
        np.random.seed(hash(str(series.name)) % 10000)
        series = series + np.random.normal(0, 0.0005, len(series))

    # Handle NaN values
    series = series.fillna(0)

    return (1 + series).cumprod()


def compute_rolling_returns(series: pd.Series, window=63):
    """Calculate rolling returns for specified window"""
    return series.rolling(window).apply(lambda x: (1 + x).prod() - 1)


def perf_metrics(ret: pd.Series, window=252, annualize=False):
    if ret.empty:
        return dict(return_pct=np.nan, volatility=np.nan,
                    sharpe=np.nan, mdd=np.nan)

    # Ensure we have data for the specified window
    actual_window = min(window, len(ret))
    if window == len(ret):
        # Use all available data for 'Total' period
        window_ret = ret
    else:
        # Use the most recent data for other periods
        window_ret = ret.tail(actual_window)

    # Calculate cumulative return
    cumulative_return = (1 + window_ret).prod() - 1

    # Calculate volatility
    volatility = window_ret.std()

    # Calculate average return for Sharpe calculation
    avg_return = window_ret.mean()

    # Apply annualization if requested
    if annualize and window >= 252:  # 1 year or more
        years = actual_window / 252
        # Annualize return
        cumulative_return = (1 + cumulative_return) ** (1 / years) - 1
        # Annualize volatility
        volatility = volatility * np.sqrt(252)
        # Annualize average return for Sharpe calculation
        avg_return = avg_return * 252
    elif annualize:
        # For less than 1 year but annualization is requested (shouldn't happen in our case)
        annualization_factor = np.sqrt(252)
        volatility = volatility * annualization_factor
        avg_return = avg_return * 252

    # Calculate Sharpe ratio
    if volatility > 0:
        sharpe = avg_return / volatility
    else:
        sharpe = np.nan

    # Calculate Maximum Drawdown
    cum = (1 + window_ret).cumprod()
    # Prevent division by zero
    if (cum == 0).any() or cum.isna().any():
        mdd = np.nan
    else:
        mdd = (cum / cum.cummax() - 1).min()

    return dict(return_pct=cumulative_return, volatility=volatility,
                sharpe=sharpe, mdd=mdd)


# Function to load raw metrics and quantiles for a factor
def load_factor_data(factor_name, date):
    # Get quantiles
    q_file = data_dir / f"factor_{factor_name}_quantiles.csv"
    q_df = load_csv(q_file)

    # Get raw metrics
    m_file = data_dir / f"factor_{factor_name}_raw_metrics.csv"
    m_df = load_csv(m_file)

    # Filter by date
    if q_df is not None and m_df is not None:
        q_df = q_df[q_df["date"] == pd.Timestamp(date)]
        m_df = m_df[m_df["date"] == pd.Timestamp(date)]

    return q_df, m_df


# Function to load individual metric quantiles
def load_metric_quantiles(metric_name, date):
    q_file = data_dir / f"metric_{metric_name}_quantiles.csv"
    q_df = load_csv(q_file)

    if q_df is not None:
        q_df = q_df[q_df["date"] == pd.Timestamp(date)]

    return q_df


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

    # Cumulative Returns Chart
    fig = go.Figure()
    factor_ret_df.set_index("date", inplace=False)  # Don't modify original df
    temp_df = factor_ret_df.set_index("date")
    for col in selected:
        cum = compute_cum(temp_df[col], sd, ed)
        fig.add_trace(go.Scatter(x=cum.index, y=cum,
                                 mode='lines', name=col.replace("_return", "")))
    fig.update_layout(template="plotly_white", yaxis_title="Cumulative return",
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)

    # 3-Month Rolling Returns Chart
    st.subheader("3-Month Rolling Returns")

    # Date range selector for rolling returns
    col1, col2 = st.columns(2)

    # Default to last 1 year
    default_start = dmax - pd.DateOffset(years=1)
    with col1:
        roll_start = st.date_input("Rolling Returns Start",
                                   max(default_start.date(), dmin),
                                   min_value=dmin,
                                   max_value=dmax,
                                   key="roll_start")
    with col2:
        roll_end = st.date_input("Rolling Returns End", dmax,
                                 min_value=dmin,
                                 max_value=dmax,
                                 key="roll_end")

    # Create rolling returns chart
    fig_roll = go.Figure()

    # Calculate and plot 3-month rolling returns for selected factors
    for col in selected:
        if col in temp_df.columns:
            rolling_ret = compute_rolling_returns(temp_df[col], window=63)
            # Convert date objects to Timestamp for comparison
            roll_start_ts = pd.Timestamp(roll_start)
            roll_end_ts = pd.Timestamp(roll_end)
            # Filter by date range
            rolling_filtered = rolling_ret[(rolling_ret.index >= roll_start_ts) &
                                           (rolling_ret.index <= roll_end_ts)]
            fig_roll.add_trace(go.Scatter(
                x=rolling_filtered.index,
                y=rolling_filtered * 100,  # Convert to percentage
                mode='lines',
                name=col.replace("_return", "")
            ))

    fig_roll.update_layout(
        template="plotly_white",
        yaxis_title="3-Month Rolling Return (%)",
        xaxis_title="Date",
        legend=dict(orientation="h"),
        hovermode='x unified'
    )

    st.plotly_chart(fig_roll, use_container_width=True)

# ───────────────────── 2. Factor performance table ───────────
elif page == "Performance Table – Factors":
    st.subheader("Performance Metrics (1m/3m/6m/12m/3y/5y/Total)")
    windows = {
        "1M": 21, "3M": 63, "6M": 126,
        "12M": 252, "3Y": 252 * 3, "5Y": 252 * 5,
        "Total": len(factor_ret_df)
    }

    rows = {}
    temp_df = factor_ret_df.set_index("date")
    for col in [c for c in factor_ret_df.columns if c.endswith("_return")]:
        ret = temp_df[col].dropna()
        stats = {}
        for label, win in windows.items():
            if label == "Total":
                actual_win = len(ret)
            else:
                actual_win = win

            if len(ret) < actual_win or (label != "Total" and len(ret) < win):
                stats[f"{label} Return"] = "N/A"
                stats[f"{label} Vol"] = "N/A"
                stats[f"{label} Sharpe"] = "N/A"
                continue

            # Determine whether to annualize
            annualize = label in ["12M", "3Y", "5Y", "Total"]

            metrics = perf_metrics(ret, window=actual_win, annualize=annualize)

            if annualize:
                stats[f"{label} Return"] = f"{metrics['return_pct'] * 100:.2f}%"  # Annualized
                stats[f"{label} Vol"] = f"{metrics['volatility'] * 100:.2f}%"  # Annualized
            else:
                stats[f"{label} Return"] = f"{metrics['return_pct'] * 100:.2f}%"  # Not annualized
                stats[f"{label} Vol"] = f"{metrics['volatility'] * 100:.2f}%"  # Not annualized

            stats[f"{label} Sharpe"] = f"{metrics['sharpe']:.2f}"
        rows[col.replace("_return", "")] = stats

    st.dataframe(pd.DataFrame(rows).T)


# ───────────────────── 3. Factor quantile table ──────────────
elif page == "Factor Quantile Constituents":
    st.subheader("Factor Quantile Constituents")

    # Create tabs for Factor and Individual Metrics
    tab1, tab2 = st.tabs(["Factor Quantiles", "Individual Metric Quantiles"])

    with tab1:
        st.subheader("Factor Quantiles")
        factor_list = ["growth", "value", "momentum", "low_vol", "quality"]
        fac = st.selectbox("Factor", factor_list)

        # Load quantile and metric data files
        qfile = data_dir / f"factor_{fac}_quantiles.csv"
        mfile = data_dir / f"factor_{fac}_raw_metrics.csv"

        qdf = load_csv(qfile)
        mdf = load_csv(mfile)

        if qdf is None:
            st.warning(f"{qfile.name} not found.")
        else:
            dates = sorted(qdf["date"].unique())
            dsel = st.selectbox("Date", options=dates,
                                format_func=lambda x: pd.to_datetime(x).date(),
                                index=len(dates) - 1)

            # Filter data for selected date
            q_date_df = qdf[qdf["date"] == dsel]

            # Get raw metrics if available
            if mdf is not None:
                m_date_df = mdf[mdf["date"] == dsel]

            # Prepare metric columns (excluding date and stock)
            metric_cols = []
            if mdf is not None and not m_date_df.empty:
                metric_cols = [c for c in m_date_df.columns if c not in ['date', 'stock']]

            # Get individual metric quantiles too
            metric_quantiles = {}
            for metric in metric_cols:
                metric_name = f"{fac}_{metric}"
                metric_q = load_metric_quantiles(metric_name, dsel)
                if metric_q is not None:
                    # Create a mapping of stock to quantile
                    metric_quantiles[metric] = dict(zip(metric_q['stock'], metric_q['quantile']))

            # Display for each quantile - Start with quintile 5 (best performing)
            available_quantiles = sorted(q_date_df["quantile"].unique(), reverse=True)

            for q in available_quantiles:
                q_stocks = q_date_df[q_date_df["quantile"] == q][["stock"]]

                # Get count of stocks in this quantile
                num_stocks = len(q_stocks)

                with st.expander(f"Quantile {int(q)} | {num_stocks} stocks"):
                    # Create a dataframe with stock, factor quantile and individual metric quantiles
                    result_df = pd.DataFrame()
                    result_df['stock'] = q_stocks['stock']
                    result_df['factor_quantile'] = q

                    # Add raw metrics if available
                    if mdf is not None and not m_date_df.empty:
                        # Merge with raw metrics
                        stock_metrics = m_date_df[m_date_df['stock'].isin(result_df['stock'])]

                        # Set stock as index for easier lookup
                        stock_metrics = stock_metrics.set_index('stock')

                        # Add individual metric quantiles
                        for metric in metric_cols:
                            result_df[f'{metric}'] = result_df['stock'].map(
                                lambda s: stock_metrics.loc[s, metric] if s in stock_metrics.index else np.nan)
                            result_df[f'{metric}_q'] = result_df['stock'].map(
                                lambda s: metric_quantiles.get(metric, {}).get(s, np.nan))

                    # Format numeric columns with 2 decimal places
                    numeric_cols = [c for c in result_df.columns if c not in ['stock', 'factor_quantile']]
                    for col in numeric_cols:
                        if 'q' not in col:  # Skip quantile columns
                            try:
                                result_df[col] = result_df[col].apply(lambda x: f"{x:.2f}" if not pd.isna(x) else "N/A")
                            except:
                                pass

                    # Reorder columns: stock, factor quantile, then metrics with their quantiles alternating
                    final_cols = ['stock', 'factor_quantile']
                    for metric in metric_cols:
                        final_cols.extend([metric, f'{metric}_q'])

                    result_df = result_df[final_cols]

                    # Rename columns for better display
                    rename_dict = {'factor_quantile': 'Factor Quintile'}
                    for metric in metric_cols:
                        # Sentiment 관련 컬럼은 더 명확하게 표시
                        if 'sentiment' in metric:
                            if metric == 'sentiment':
                                rename_dict[metric] = 'Sentiment Score'
                                rename_dict[f'{metric}_q'] = 'Sentiment Qnt'
                            elif metric == 'sentiment_trend':
                                rename_dict[metric] = 'Sentiment Trend'
                                rename_dict[f'{metric}_q'] = 'Trend Qnt'
                        else:
                            rename_dict[metric] = metric.title()
                            rename_dict[f'{metric}_q'] = f'{metric.title()} Qnt'

                    result_df = result_df.rename(columns=rename_dict)

                    # Display the table without index
                    st.dataframe(result_df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Individual Metric Quantiles")

        # Get all available metric files
        metric_files = []
        for file in data_dir.glob("metric_*_quantiles.csv"):
            metric_name = file.stem.replace("metric_", "").replace("_quantiles", "")
            metric_files.append(metric_name)

        if not metric_files:
            st.warning("No metric quantile files found.")
        else:
            selected_metric = st.selectbox("Select Metric", options=sorted(metric_files))

            # Load metric quantile file
            metric_qfile = data_dir / f"metric_{selected_metric}_quantiles.csv"
            metric_qdf = load_csv(metric_qfile)

            if metric_qdf is None:
                st.warning(f"Could not load {metric_qfile.name}")
            else:
                dates = sorted(metric_qdf["date"].unique())
                dsel_metric = st.selectbox("Date", options=dates,
                                           format_func=lambda x: pd.to_datetime(x).date(),
                                           index=len(dates) - 1,
                                           key="metric_date")

                # Filter data for selected date
                q_date_df = metric_qdf[metric_qdf["date"] == dsel_metric]

                # Display for each quantile - Start with quintile 5 (best performing)
                available_quantiles = sorted(q_date_df["quantile"].unique(), reverse=True)

                for q in available_quantiles:
                    q_stocks = q_date_df[q_date_df["quantile"] == q][["stock", "quantile"]]

                    # Get count of stocks in this quantile
                    num_stocks = len(q_stocks)

                    with st.expander(f"Quantile {int(q)} | {num_stocks} stocks"):
                        # Display the table without index
                        st.dataframe(q_stocks, use_container_width=True, hide_index=True)

# ───────────────────── 4. Cumulative metric perf ─────────────
elif page == "Cumulative Performance – Metrics":
    st.subheader("Cumulative Returns of Metric Portfolios")

    metric_cols = [c for c in metric_ret_df.columns if c.endswith("_return")]
    sel = st.multiselect("Select metrics (max 5)", metric_cols, metric_cols[:5])

    if not sel:
        st.warning("Please select at least one metric")
        st.stop()

    dmin, dmax = metric_ret_df["date"].min().date(), metric_ret_df["date"].max().date()
    sdate = st.date_input("Start date", dmin, dmin, dmax, key="m_start")
    edate = st.date_input("End date", dmax, dmin, dmax, key="m_end")

    # Cumulative Returns Chart
    temp_df = metric_ret_df.set_index("date")
    figm = go.Figure()
    for col in sel[:5]:  # Limit to 5 metrics
        try:
            cum = compute_cum(temp_df[col], sdate, edate)
            figm.add_trace(go.Scatter(x=cum.index, y=cum, mode='lines',
                                      name=col.replace("_return", "")))
        except Exception as e:
            st.warning(f"Error plotting {col}: {e}")

    figm.update_layout(template="plotly_white", yaxis_title="Cumulative return",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(figm, use_container_width=True)

    # 3-Month Rolling Returns Chart for Metrics
    st.subheader("3-Month Rolling Returns")

    # Date range selector for rolling returns
    col1, col2 = st.columns(2)

    # Default to last 1 year
    default_start = dmax - pd.DateOffset(years=1)
    with col1:
        roll_start = st.date_input("Rolling Returns Start",
                                   max(default_start.date(), dmin),
                                   min_value=dmin,
                                   max_value=dmax,
                                   key="m_roll_start")
    with col2:
        roll_end = st.date_input("Rolling Returns End", dmax,
                                 min_value=dmin,
                                 max_value=dmax,
                                 key="m_roll_end")

    # Create rolling returns chart
    fig_roll = go.Figure()

    # Calculate and plot 3-month rolling returns for selected metrics
    for col in sel[:5]:
        if col in temp_df.columns:
            rolling_ret = compute_rolling_returns(temp_df[col], window=63)
            # Convert date objects to Timestamp for comparison
            roll_start_ts = pd.Timestamp(roll_start)
            roll_end_ts = pd.Timestamp(roll_end)
            # Filter by date range
            rolling_filtered = rolling_ret[(rolling_ret.index >= roll_start_ts) &
                                           (rolling_ret.index <= roll_end_ts)]
            fig_roll.add_trace(go.Scatter(
                x=rolling_filtered.index,
                y=rolling_filtered * 100,  # Convert to percentage
                mode='lines',
                name=col.replace("_return", "")
            ))

    fig_roll.update_layout(
        template="plotly_white",
        yaxis_title="3-Month Rolling Return (%)",
        xaxis_title="Date",
        legend=dict(orientation="h"),
        hovermode='x unified'
    )

    st.plotly_chart(fig_roll, use_container_width=True)

# ───────────────────── 5. Metric performance table ───────────
else:
    st.subheader("Metric Performance Metrics")
    metric_cols = [c for c in metric_ret_df.columns if c.endswith("_return")]

    if not metric_cols:
        st.warning("No metric returns found in the data")
        st.stop()

    # Option to select specific metrics or show all
    show_all = st.checkbox("Show all metrics", value=False)

    if not show_all:
        selected_metrics = st.multiselect("Select metrics to display",
                                          metric_cols,
                                          default=metric_cols[:10])
    else:
        selected_metrics = metric_cols

    # Ensure we have selected metrics
    if not selected_metrics:
        st.warning("Please select at least one metric")
        st.stop()

    rows = {}
    temp_df = metric_ret_df.set_index("date")

    for col in selected_metrics:
        try:
            ret = temp_df[col].dropna()
            stats = {}

            windows = {"1M": 21, "3M": 63, "6M": 126, "12M": 252, "3Y": 756, "5Y": 1260, "Total": len(ret)}

            for label, win in windows.items():
                if label == "Total":
                    actual_win = len(ret)
                else:
                    actual_win = win

                if len(ret) < actual_win or (label != "Total" and len(ret) < win):
                    stats[f"{label} R"] = "N/A"
                    stats[f"{label} V"] = "N/A"
                    stats[f"{label} S"] = "N/A"
                    continue

                # Determine whether to annualize
                annualize = label in ["12M", "3Y", "5Y", "Total"]

                m = perf_metrics(ret, window=actual_win, annualize=annualize)

                stats[f"{label} R"] = f"{m['return_pct'] * 100:.2f}%"
                stats[f"{label} V"] = f"{m['volatility'] * 100:.2f}%"
                stats[f"{label} S"] = f"{m['sharpe']:.2f}"

            # Clean up metric name for display
            clean_name = col.replace("_return", "").replace("_", " ").title()
            rows[clean_name] = stats
        except Exception as e:
            st.warning(f"Error processing {col}: {e}")

    if rows:
        df = pd.DataFrame(rows).T

        # Option to search/filter metrics
        if len(rows) > 20:
            search_term = st.text_input("Search metrics", "")
            if search_term:
                search_mask = df.index.str.contains(search_term, case=False, na=False)
                df = df[search_mask]

        # Display the dataframe
        st.dataframe(df, use_container_width=True)

        # Add download option for large tables
        if len(df) > 10:
            csv = df.to_csv().encode('utf-8')
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="metric_performance.csv",
                mime="text/csv",
            )
    else:
        st.warning("No data to display")


# ───────────────────────── Footer ─────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.markdown("""
This dashboard analyzes factor and metric portfolios.
Data updated: Check the output folder for latest files.

**Factors**: Growth, Value, Momentum, Low Vol, Quality  
**Metrics**: Individual components of each factor
""")

# Add a diagnostics section for debugging
if st.sidebar.checkbox("Show Diagnostics", False):
    st.sidebar.markdown("### 🔍 Diagnostics")

    # Check available files
    csv_files = list(data_dir.glob("*.csv"))
    st.sidebar.markdown(f"CSV files found: {len(csv_files)}")

    # Check data shape
    if factor_ret_df is not None:
        st.sidebar.markdown(f"Factor data shape: {factor_ret_df.shape}")
    if metric_ret_df is not None:
        st.sidebar.markdown(f"Metric data shape: {metric_ret_df.shape}")

    # Check for NaN values
    if factor_ret_df is not None:
        nan_count = factor_ret_df.isna().sum().sum()
        st.sidebar.markdown(f"Factor NaN count: {nan_count}")
    if metric_ret_df is not None:
        nan_count = metric_ret_df.isna().sum().sum()
        st.sidebar.markdown(f"Metric NaN count: {nan_count}")