from typing import List, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import os
import pickle


# Streamlit 설정은 가장 먼저 호출해야 합니다.
st.set_page_config(layout="wide")
st.title('Portfolio Performance Dashboard')

# 데이터 디렉토리 설정
data_dir = 'C:/Users/westl/PycharmProjects/pythonProject/venv_vf/Index Quant'  # 실제 데이터 디렉토리 경로로 수정 필요

# 데이터 로드
try:
    #benchmark_cum_returns = pd.read_csv(os.path.join(data_dir, 'benchmark_cum_returns.csv'), index_col=0,
    #                                    parse_dates=True)
    us_eps_fwd_3m = pd.read_csv(os.path.join(data_dir, 'eps_3m.csv'), index_col=0, parse_dates=True)
    eps_res_bd = pd.read_csv(os.path.join(data_dir, "index_eps.csv"), index_col=0, parse_dates=True, date_format='%Y-%m-%d').dropna()
    eps_res_bd_sec = pd.read_csv(os.path.join(data_dir, "index_sec_eps.csv"), index_col=0, parse_dates=True, date_format='%Y-%m-%d').dropna()
    euro_eps_res_bd_sec = pd.read_csv(os.path.join(data_dir, "euro_sec_eps.csv"), index_col=0, parse_dates=True, date_format='%Y-%m-%d').dropna()

    index_fcf_fwd_3m = pd.read_csv(os.path.join(data_dir, 'fcf_3m.csv'), index_col=0, parse_dates=True)
    us_sales_fwd_3m = pd.read_csv(os.path.join(data_dir, 'sales_3m.csv'), index_col=0, parse_dates=True)
    pe_index_bd = pd.read_csv(os.path.join(data_dir, 'pe_index_bd.csv'), index_col=0, parse_dates=True, date_format='%Y-%m-%d').dropna()
    us_eps_fwd_3m_sec = pd.read_csv(os.path.join(data_dir, 'eps_3m_sec.csv'), index_col=0, parse_dates=True)
    index_fcf_fwd_3m_sec = pd.read_csv(os.path.join(data_dir, 'fcf_3m_sec.csv'), index_col=0, parse_dates=True)
    us_sales_fwd_3m_sec = pd.read_csv(os.path.join(data_dir, 'sales_3m_sec.csv'), index_col=0, parse_dates=True)
    pe_index_bd_sec = pd.read_csv(os.path.join(data_dir, 'pe_index_bd_sec.csv'), index_col=0, parse_dates=True,
                              date_format='%Y-%m-%d').dropna()

    euro_eps_fwd_3m_sec = pd.read_csv(os.path.join(data_dir, 'euro_eps_3m_sec.csv'), index_col=0, parse_dates=True)
    euro_fcf_fwd_3m_sec = pd.read_csv(os.path.join(data_dir, 'euro_fcf_3m_sec.csv'), index_col=0, parse_dates=True)
    euro_sales_fwd_3m_sec = pd.read_csv(os.path.join(data_dir, 'euro_sales_3m_sec.csv'), index_col=0, parse_dates=True)
    pe_euro_bd_sec = pd.read_csv(os.path.join(data_dir, 'euro_pe_index_bd_sec.csv'), index_col=0, parse_dates=True,
                              date_format='%Y-%m-%d').dropna()


    us_eps_fwd_1y = pd.read_csv(os.path.join(data_dir, 'eps_1y.csv'), index_col=0, parse_dates=True)
    index_fcf_fwd_1y = pd.read_csv(os.path.join(data_dir, 'fcf_1y.csv'), index_col=0, parse_dates=True)
    us_sales_fwd_1y = pd.read_csv(os.path.join(data_dir, 'sales_1y.csv'), index_col=0, parse_dates=True)
    #pe_index_bd = pd.read_csv(os.path.join(data_dir, 'pe_index_bd.csv'), index_col=0, parse_dates=True, date_format='%Y-%m-%d')
    us_eps_fwd_1y_sec = pd.read_csv(os.path.join(data_dir, 'eps_1y_sec.csv'), index_col=0, parse_dates=True)
    index_fcf_fwd_1y_sec = pd.read_csv(os.path.join(data_dir, 'fcf_1y_sec.csv'), index_col=0, parse_dates=True)
    us_sales_fwd_1y_sec = pd.read_csv(os.path.join(data_dir, 'sales_1y_sec.csv'), index_col=0, parse_dates=True)

    euro_eps_fwd_1y_sec = pd.read_csv(os.path.join(data_dir, 'euro_eps_1y_sec.csv'), index_col=0, parse_dates=True)
    euro_fcf_fwd_1y_sec = pd.read_csv(os.path.join(data_dir, 'euro_fcf_1y_sec.csv'), index_col=0, parse_dates=True)
    euro_sales_fwd_1y_sec = pd.read_csv(os.path.join(data_dir, 'euro_sales_1y_sec.csv'), index_col=0, parse_dates=True)

    glb_eq_eps_3m = pd.read_csv(os.path.join(data_dir, 'glb_eq_eps_3m.csv'), index_col=0, parse_dates=True)
    glb_eq_eps_1y = pd.read_csv(os.path.join(data_dir, 'glb_eq_eps_1y.csv'), index_col=0, parse_dates=True)
    glb_eq_sales_3m = pd.read_csv(os.path.join(data_dir, 'glb_eq_sales_3m.csv'), index_col=0, parse_dates=True)
    glb_eq_sales_1y = pd.read_csv(os.path.join(data_dir, 'glb_eq_sales_1y.csv'), index_col=0, parse_dates=True)




    actual_cum_returns = pd.read_csv(os.path.join(data_dir, 'actual_cum_returns.csv'), index_col=0, parse_dates=True)
    actual_cum_returns_overlay = pd.read_csv(os.path.join(data_dir, 'actual_cum_returns_overlay.csv'), index_col=0, parse_dates=True)
    actual_cum_returns_eps_overlay = pd.read_csv(os.path.join(data_dir, 'actual_cum_returns_eps_overlay.csv'), index_col=0, parse_dates=True)
    actual_cum_returns_combined_overlay = pd.read_csv(os.path.join(data_dir, 'actual_cum_returns_combined_overlay.csv'), index_col=0, parse_dates=True)
    actual_cum_returns_growth = pd.read_csv(os.path.join(data_dir, 'actual_cum_returns_growth.csv'), index_col=0, parse_dates=True)
    actual_cum_returns_momentum = pd.read_csv(os.path.join(data_dir, 'actual_cum_returns_momentum.csv'), index_col=0, parse_dates=True)
    annual_returns = pd.read_csv(os.path.join(data_dir, 'annual_returns.csv'), index_col=0)
    performance_decomposition_df = pd.read_csv(os.path.join(data_dir, 'performance_decomposition_df.csv'), index_col=0)
    recent_6m_weights = pd.read_csv(os.path.join(data_dir, 'recent_6m_weights.csv'), index_col=0, parse_dates=True)
    #tracking_error_daily = pd.read_csv(os.path.join(data_dir, 'tracking_error_daily.csv'), index_col=0,
    #                                   parse_dates=True)
    #alpha_df = pd.read_csv(os.path.join(data_dir, 'alpha_df.csv'), index_col=0)
    scores = pd.read_csv(os.path.join(data_dir, 'scores.csv'), index_col=0, parse_dates=True)
    annual_ic_total = pd.read_csv(os.path.join(data_dir, 'annual_ic_total.csv'), index_col=0)
    annual_ic_factors_df = pd.read_csv(os.path.join(data_dir, 'annual_ic_factors.csv'), index_col=0)
    #rolling_ir = pd.read_csv(os.path.join(data_dir, 'rolling_ir.csv'), index_col=0)
    comparison_df = pd.read_csv(os.path.join(data_dir, 'comparison_df.csv'), index_col=0)
    decay_total = pd.read_csv(os.path.join(data_dir, 'decay_total.csv'), index_col=0)
    decay_factors_df = pd.read_csv(os.path.join(data_dir, 'decay_factors_df.csv'), index_col=0)
    actual_cum_returns_new = pd.read_csv(os.path.join(data_dir, 'actual_cum_returns_new.csv'), index_col=0, parse_dates=True)
    monthly_factor_weights = pd.read_csv(os.path.join(data_dir, 'monthly_factor_weights.csv'), index_col=0, parse_dates=True)
    results_df = pd.read_csv(os.path.join(data_dir, 'results_df.csv'), index_col=0, parse_dates=True, date_format='%Y-%m-%d')
    overlay_recent_3y_weights = pd.read_csv(os.path.join(data_dir, 'overlay_recent_3y_weights.csv'), index_col=0, parse_dates=True)
    overlay_recent_partial_weights = pd.read_csv(os.path.join(data_dir, 'overlay_recent_partial_weights.csv'), index_col=0, parse_dates=True)
    eps_overlay_recent_3y_weights = pd.read_csv(os.path.join(data_dir, 'eps_overlay_recent_3y_weights.csv'), index_col=0, parse_dates=True)
    eps_overlay_recent_partial_weights = pd.read_csv(os.path.join(data_dir, 'eps_overlay_recent_partial_weights.csv'), index_col=0, parse_dates=True)
    combined_overlay_recent_3y_weights = pd.read_csv(os.path.join(data_dir, 'combined_overlay_recent_3y_weights.csv'), index_col=0, parse_dates=True)
    combined_overlay_recent_partial_weights = pd.read_csv(os.path.join(data_dir, 'combined_overlay_recent_partial_weights.csv'), index_col=0, parse_dates=True)
    combined_overlay_recent_eps_weights = pd.read_csv(os.path.join(data_dir, 'combined_overlay_recent_eps_weights.csv'), index_col=0, parse_dates=True)
    combined_overlay_recent_momentum_weights = pd.read_csv(os.path.join(data_dir, 'combined_overlay_recent_momentum_weights.csv'), index_col=0, parse_dates=True)
    growth_3y_weights = pd.read_csv(os.path.join(data_dir, 'Growth_weights.csv'), index_col=0, parse_dates=True)
    momentum_3y_weights = pd.read_csv(os.path.join(data_dir, 'Momentum_weights.csv'), index_col=0, parse_dates=True)


except FileNotFoundError as e:
    st.error(f"파일을 찾을 수 없습니다: {e}")
    st.stop()

# 추가 데이터 로드
with open(os.path.join(data_dir, 'factor_scores.pkl'), 'rb') as f:
    factor_scores = pickle.load(f)

with open(os.path.join(data_dir, 'quarterly_group_stocks.pkl'), 'rb') as f:
    quarterly_group_stocks = pickle.load(f)

with open(os.path.join(data_dir, 'quarterly_rebalance_dates.pkl'), 'rb') as f:
    quarterly_rebalance_dates = pickle.load(f)

with open(os.path.join(data_dir, 'monthly_rebalance_dates.pkl'), 'rb') as f:
    monthly_rebalance_dates = pickle.load(f)

with open(os.path.join(data_dir, 'monthly_group_stocks.pkl'), 'rb') as f:
    monthly_group_stocks = pickle.load(f)


# ─────────────────── Helper–공용Fundamenta섹션 ───────────────────

def load_csv(name:str, **kw):
    return pd.read_csv(os.path.join(DATA_DIR, name), index_col=0, parse_dates=True, **kw)

PERIODS = {"0M":0, "1M":21, "2M":42, "3M":63}                       ### <<< NEW

from typing import Union, List, Optional


def render_fundamental_section_enhanced(title: str, eps_3m: pd.DataFrame, fcf_3m: pd.DataFrame, sales_3m: pd.DataFrame,
                                        eps_1y: pd.DataFrame = None, fcf_1y: pd.DataFrame = None,
                                        sales_1y: pd.DataFrame = None,
                                        universe: List[str] = None, default: Optional[List[str]] = None,
                                        use_sales_instead_of_fcf: bool = False):
    """
    Enhanced visualization function with:
    - Timeline tab
    - Time Progression tab (with arrows showing movement)
    - Both 3-month and 1-year change rate analysis
    - Special case for Global Equities: show only one chart
    - Added 2-week data point
    - Special handling for Banks sector in European data
    """
    if eps_1y is None:
        eps_1y = eps_3m  # If 1Y data not provided, use 3M data as fallback
    if fcf_1y is None:
        fcf_1y = fcf_3m
    if sales_1y is None:
        sales_1y = sales_3m

    st.header(title)
    tickers = st.multiselect("Select Tickers", universe, default=default or universe[:5], key=title)
    if not tickers:
        st.info("Please select at least one ticker.");
        return

    # Determine which data series to show (FCF or Sales)
    if use_sales_instead_of_fcf:
        secondary_data_3m = sales_3m
        secondary_data_1y = sales_1y
        secondary_label = "Sales"
    else:
        secondary_data_3m = fcf_3m
        secondary_data_1y = fcf_1y
        secondary_label = "FCF"

    # Special handling for Banks sector - set FCF to 0 for "Banks" in European data
    is_european_data = "European" in title and not use_sales_instead_of_fcf
    if is_european_data:
        # Make a deep copy to avoid modifying original data
        secondary_data_3m = secondary_data_3m.copy()
        secondary_data_1y = secondary_data_1y.copy()

        # If "Banks" is in the dataframe or in the tickers, ensure it has values of 0
        if "Banks" in secondary_data_3m.columns:
            secondary_data_3m["Banks"] = 0
        if "Banks" in secondary_data_1y.columns:
            secondary_data_1y["Banks"] = 0

    tab_tl, tab_tp = st.tabs(["Timeline", "Time Progression"])

    # ── Timeline (unchanged)
    with tab_tl:
        days = st.slider("Look‑back window (days)", 60, 252 * 3, 252, 30, key=title + "tl")
        end_dt = eps_3m.index.max();
        start_dt = end_dt - pd.Timedelta(days=days)
        eps_f = eps_3m.loc[start_dt:end_dt, tickers];

        # Ensure all selected tickers exist in secondary data
        available_tickers = [t for t in tickers if t in secondary_data_3m.columns]
        missing_tickers = [t for t in tickers if t not in secondary_data_3m.columns]

        # Add missing tickers with zeros if necessary
        for ticker in missing_tickers:
            if ticker == "Banks" and is_european_data:
                # Create a column of zeros for Banks
                secondary_data_3m[ticker] = 0

        secondary_f = secondary_data_3m.loc[start_dt:end_dt, tickers]

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            subplot_titles=(f"Forward EPS 3‑M Chg", f"Forward {secondary_label} 3‑M Chg"))
        for t in tickers:
            fig.add_trace(go.Scatter(x=eps_f.index, y=eps_f[t], name=f"{t} EPS"), row=1, col=1)
            fig.add_trace(go.Scatter(x=secondary_f.index, y=secondary_f[t], name=f"{t} {secondary_label}",
                                     line=dict(dash='dot'), showlegend=False), row=2, col=1)
        for r in (1, 2):
            fig.add_hline(y=0, line_dash='dash', line_color='gray', row=r, col=1)
        fig.update_yaxes(tickformat='.1%')
        fig.update_layout(height=550, template='plotly_white', legend_orientation='h')
        st.plotly_chart(fig, use_container_width=True)

    # ── Time Progression - showing arrows between time periods
    with tab_tp:
        # Define time periods - Added 2w ago
        periods = {"Now": 0, "2w ago": 10, "1m ago": 21, "2m ago": 42, "3m ago": 63}
        period_colors = {
            'Now': '#1f77b4',  # Blue
            '2w ago': '#9467bd',  # Purple (added for 2w)
            '1m ago': '#ff7f0e',  # Orange
            '2m ago': '#2ca02c',  # Green
            '3m ago': '#d62728'  # Red
        }

        # Allow user to select between 3M and 1Y view - with unique key
        time_scale = st.radio("Select Time Scale",
                              ["3-Month Change", "1-Year Change"],
                              horizontal=True,
                              key=f"{title}_time_scale")  # Add unique key using title

        # Choose appropriate datasets based on selected time scale
        if time_scale == "3-Month Change":
            eps_data = eps_3m
            secondary_data = secondary_data_3m
            tertiary_data = sales_3m
            value_range = [-0.1, 0.1]  # Narrower range for 3M
            title_suffix = "(3M → Now)"
        else:  # 1-Year Change
            eps_data = eps_1y
            secondary_data = secondary_data_1y
            tertiary_data = sales_1y
            value_range = [-0.25, 0.25]  # Wider range for 1Y
            title_suffix = "(1Y → Now)"

        # Create dataframes to store time progression data
        eps_progression = pd.DataFrame(index=tickers)
        secondary_progression = pd.DataFrame(index=tickers)
        tertiary_progression = pd.DataFrame(index=tickers)  # For Sales data regardless of primary choice

        # Fill with data from different time periods
        for lbl, lag in periods.items():
            idx = -1 - lag if lag else -1

            # For each ticker, extract values (with special handling for Banks)
            for ticker in tickers:
                # EPS data
                if ticker in eps_data.columns:
                    eps_progression.loc[ticker, lbl] = eps_data.iloc[idx][ticker]
                else:
                    eps_progression.loc[ticker, lbl] = 0  # Default to 0 if missing

                # Secondary data (FCF or Sales)
                if ticker in secondary_data.columns:
                    secondary_progression.loc[ticker, lbl] = secondary_data.iloc[idx][ticker]
                elif ticker == "Banks" and is_european_data:
                    secondary_progression.loc[ticker, lbl] = 0  # Set to 0 for Banks in European data
                else:
                    secondary_progression.loc[ticker, lbl] = 0  # Default to 0 if missing

                # Tertiary data (always Sales)
                if ticker in tertiary_data.columns:
                    tertiary_progression.loc[ticker, lbl] = tertiary_data.iloc[idx][ticker]
                else:
                    tertiary_progression.loc[ticker, lbl] = 0  # Default to 0 if missing

        # Custom color palette for tickers to ensure they're distinguishable
        ticker_colors = {}
        for i, ticker in enumerate(tickers):
            ticker_colors[ticker] = px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]

        # For Global Equities, we only show one chart (EPS vs Sales)
        if use_sales_instead_of_fcf:
            # Create a single chart with full width
            fig = go.Figure()

            # Reference lines
            fig.add_trace(go.Scatter(
                x=[value_range[0], value_range[1]],
                y=[value_range[0], value_range[1]],
                mode='lines',
                line=dict(color='gray', dash='dash'),
                showlegend=False,
                name='Reference Line')
            )
            fig.add_hline(y=0, line_dash='dot', line_color='lightgray')
            fig.add_vline(x=0, line_dash='dot', line_color='lightgray')

            # Add period indicators first (create a separate legend group for periods)
            for period, color in period_colors.items():
                fig.add_trace(go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    marker=dict(size=10, color=color),
                    name=f"Period: {period}",
                    legendgroup="periods",
                    legendgrouptitle=dict(text="Time Periods")
                ))

            # Add traces for each ticker showing the movement path - in a separate legend group
            for ticker in tickers:
                # Get data points for all time periods
                periods_list = list(periods.keys())
                eps_values = eps_progression.loc[ticker].values
                secondary_values = secondary_progression.loc[ticker].values

                # Draw lines connecting the points (from oldest to newest)
                fig.add_trace(go.Scatter(
                    x=eps_values[::-1],  # Reversed to show oldest to newest
                    y=secondary_values[::-1],
                    mode='lines+markers',
                    line=dict(color=ticker_colors[ticker], width=2),
                    marker=dict(size=8, color=[period_colors[p] for p in periods_list[::-1]]),
                    name=ticker,
                    legendgroup="tickers",
                    legendgrouptitle=dict(text="Tickers")
                ))

                # Add arrows between consecutive points to show direction
                for i in range(len(periods_list) - 1, 0, -1):
                    # Draw arrow from older point to newer point
                    older_idx = i
                    newer_idx = i - 1
                    fig.add_annotation(
                        x=eps_values[newer_idx],
                        y=secondary_values[newer_idx],
                        ax=eps_values[older_idx],
                        ay=secondary_values[older_idx],
                        xref="x", yref="y",
                        axref="x", ayref="y",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor=ticker_colors[ticker],
                        opacity=0.8
                    )

                # Add ticker label at the most recent point (0M)
                fig.add_trace(go.Scatter(
                    x=[eps_values[0]],
                    y=[secondary_values[0]],
                    mode='text',
                    text=[ticker],
                    textposition='top center',
                    textfont=dict(color=ticker_colors[ticker]),
                    showlegend=False,
                    legendgroup="tickers"
                ))

            fig.update_layout(
                title=f"EPS vs {secondary_label} Time Progression {title_suffix}",
                xaxis_title='EPS chg',
                yaxis_title=f'{secondary_label} chg',
                xaxis=dict(tickformat='.1%', range=value_range),
                yaxis=dict(tickformat='.1%', range=value_range),
                template='plotly_white',
                height=550,
                hovermode='closest',
                # Improved legend configuration to prevent text overlap
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    itemsizing="constant",
                    font=dict(size=10),
                    borderwidth=1,
                    tracegroupgap=10,  # Add gap between legend groups
                    groupclick="toggleitem"  # Click behavior
                )
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            # For non-global equities, show two side-by-side charts as before
            c1, c2 = st.columns(2)

            # EPS vs Secondary Metric (FCF or Sales) Progression - with arrows
            with c1:
                fig = go.Figure()

                # Reference lines
                fig.add_trace(go.Scatter(
                    x=[value_range[0], value_range[1]],
                    y=[value_range[0], value_range[1]],
                    mode='lines',
                    line=dict(color='gray', dash='dash'),
                    showlegend=False,
                    name='Reference Line')
                )
                fig.add_hline(y=0, line_dash='dot', line_color='lightgray')
                fig.add_vline(x=0, line_dash='dot', line_color='lightgray')

                # Add period indicators first (create a separate legend group for periods)
                for period, color in period_colors.items():
                    fig.add_trace(go.Scatter(
                        x=[None], y=[None],
                        mode='markers',
                        marker=dict(size=10, color=color),
                        name=f"Period: {period}",
                        legendgroup="periods",
                        legendgrouptitle=dict(text="Time Periods")
                    ))

                # Add traces for each ticker showing the movement path - in a separate legend group
                for ticker in tickers:
                    # Get data points for all time periods
                    periods_list = list(periods.keys())
                    eps_values = eps_progression.loc[ticker].values
                    secondary_values = secondary_progression.loc[ticker].values

                    # Draw lines connecting the points (from oldest to newest)
                    fig.add_trace(go.Scatter(
                        x=eps_values[::-1],  # Reversed to show oldest to newest
                        y=secondary_values[::-1],
                        mode='lines+markers',
                        line=dict(color=ticker_colors[ticker], width=2),
                        marker=dict(size=8, color=[period_colors[p] for p in periods_list[::-1]]),
                        name=ticker,
                        legendgroup="tickers",
                        legendgrouptitle=dict(text="Tickers")
                    ))

                    # Add arrows between consecutive points to show direction
                    for i in range(len(periods_list) - 1, 0, -1):
                        # Draw arrow from older point to newer point
                        older_idx = i
                        newer_idx = i - 1
                        fig.add_annotation(
                            x=eps_values[newer_idx],
                            y=secondary_values[newer_idx],
                            ax=eps_values[older_idx],
                            ay=secondary_values[older_idx],
                            xref="x", yref="y",
                            axref="x", ayref="y",
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1,
                            arrowwidth=2,
                            arrowcolor=ticker_colors[ticker],
                            opacity=0.8
                        )

                    # Add ticker label at the most recent point (0M)
                    fig.add_trace(go.Scatter(
                        x=[eps_values[0]],
                        y=[secondary_values[0]],
                        mode='text',
                        text=[ticker],
                        textposition='top center',
                        textfont=dict(color=ticker_colors[ticker]),
                        showlegend=False,
                        legendgroup="tickers"
                    ))

                fig.update_layout(
                    title=f"EPS vs {secondary_label} Time Progression {title_suffix}",
                    xaxis_title='EPS chg',
                    yaxis_title=f'{secondary_label} chg',
                    xaxis=dict(tickformat='.1%', range=value_range),
                    yaxis=dict(tickformat='.1%', range=value_range),
                    template='plotly_white',
                    height=550,
                    hovermode='closest',
                    # Improved legend configuration to prevent text overlap
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        itemsizing="constant",
                        font=dict(size=10),
                        borderwidth=1,
                        tracegroupgap=10,  # Add gap between legend groups
                        groupclick="toggleitem"  # Click behavior
                    )
                )

                st.plotly_chart(fig, use_container_width=True)

            # In the second column, show EPS vs Sales
            with c2:
                tertiary_label = "Sales"

                fig = go.Figure()

                # Reference lines
                fig.add_trace(go.Scatter(
                    x=[value_range[0], value_range[1]],
                    y=[value_range[0], value_range[1]],
                    mode='lines',
                    line=dict(color='gray', dash='dash'),
                    showlegend=False,
                    name='Reference Line')
                )
                fig.add_hline(y=0, line_dash='dot', line_color='lightgray')
                fig.add_vline(x=0, line_dash='dot', line_color='lightgray')

                # Add traces for each ticker showing the movement path
                for ticker in tickers:
                    # Get data points for all time periods
                    periods_list = list(periods.keys())
                    eps_values = eps_progression.loc[ticker].values
                    tertiary_values = tertiary_progression.loc[ticker].values

                    # Draw lines connecting the points (from oldest to newest)
                    fig.add_trace(go.Scatter(
                        x=eps_values[::-1],  # Reversed to show oldest to newest
                        y=tertiary_values[::-1],
                        mode='lines+markers',
                        line=dict(color=ticker_colors[ticker], width=2),
                        marker=dict(size=8, color=[period_colors[p] for p in periods_list[::-1]]),
                        name=ticker,
                        showlegend=True  # Show legend for consistency with first chart
                    ))

                    # Add arrows between consecutive points to show direction
                    for i in range(len(periods_list) - 1, 0, -1):
                        # Draw arrow from older point to newer point
                        older_idx = i
                        newer_idx = i - 1
                        fig.add_annotation(
                            x=eps_values[newer_idx],
                            y=tertiary_values[newer_idx],
                            ax=eps_values[older_idx],
                            ay=tertiary_values[older_idx],
                            xref="x", yref="y",
                            axref="x", ayref="y",
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1,
                            arrowwidth=2,
                            arrowcolor=ticker_colors[ticker],
                            opacity=0.8
                        )

                    # Add ticker label at the most recent point
                    fig.add_trace(go.Scatter(
                        x=[eps_values[0]],
                        y=[tertiary_values[0]],
                        mode='text',
                        text=[ticker],
                        textposition='top center',
                        textfont=dict(color=ticker_colors[ticker]),
                        showlegend=False
                    ))

                # Add period indicators for the second chart
                for period, color in period_colors.items():
                    fig.add_trace(go.Scatter(
                        x=[None], y=[None],
                        mode='markers',
                        marker=dict(size=10, color=color),
                        name=f"Period: {period}",
                        legendgroup="periods2",
                        showlegend=False  # Don't duplicate period legend
                    ))

                fig.update_layout(
                    title=f"EPS vs {tertiary_label} Time Progression {title_suffix}",
                    xaxis_title='EPS chg',
                    yaxis_title=f'{tertiary_label} chg',
                    xaxis=dict(tickformat='.1%', range=value_range),
                    yaxis=dict(tickformat='.1%', range=value_range),
                    template='plotly_white',
                    height=550,
                    hovermode='closest',
                    # Make legend layout consistent with first chart
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        itemsizing="constant",
                        font=dict(size=10),
                        borderwidth=1
                    )
                )

                st.plotly_chart(fig, use_container_width=True)



def plot_pe_bands_plotly(data):
    """
    Plotly 버전으로 구현한 P/E multiple 밴드 그래프
    - data: P/E 정보가 들어있는 pandas DataFrame
    - return: Plotly Figure
    """

    # 혹시 timestamp 컬럼이 있다면 제거
    timestamp_cols = [col for col in data.columns
                      if all(isinstance(val, pd.Timestamp) for val in data[col])]
    data_numeric = data.drop(columns=timestamp_cols)

    # 분위수 계산 (10%, 25%, 50%, 75%, 90%)
    quantiles = data_numeric.quantile([0.1, 0.25, 0.5, 0.75, 0.9])

    # 가장 최신 행(최근 P/E)
    recent_pe = data_numeric.iloc[-1]
    # 최소값, 최대값
    lowest_pe = data_numeric.min()
    highest_pe = data_numeric.max()

    # Bar 그릴 때 높이(height) = (최댓값 - 최솟값)
    height = highest_pe - lowest_pe

    # DEMA(1개월) 계산 함수 (예: 30일=대략 60개 row 사용하여 span=32 정도로)
    def dema(series, span):
        ema1 = series.ewm(span=span, adjust=False).mean()
        ema2 = ema1.ewm(span=span, adjust=False).mean()
        return 2 * ema1 - ema2

    # 각 컬럼별로 최근 N=60개의 row로 DEMA 계산 후, 마지막 값만 뽑기
    dema_1_month = data_numeric.iloc[-21]
    #dema_1_month = data_numeric.apply(lambda x: dema(x[-60:], span=32).iloc[-1])

    # X축용 인덱스(정수)
    bar_x_positions = np.arange(len(lowest_pe.index))

    # Plotly Figure 생성
    fig = go.Figure()

    # (1) 바 차트: min -> max 구간을 SkyBlue 색상으로
    fig.add_trace(
        go.Bar(
            x=bar_x_positions,  # X축: 정수 위치
            y=height,  # 실제 바 높이는 (최대값 - 최소값)
            base=lowest_pe,  # 바가 시작될 y값(최솟값)
            marker_color="skyblue",
            width=0.3,
            name="P/E Range (Low to High)",
            opacity=0.7
        )
    )
    # 미리 이름과 색상, 분위수 레벨을 정의
    percentile_info = [
        {"label": "10th Percentile", "color": "black", "level": 0.1},
        {"label": "25th Percentile", "color": "red", "level": 0.25},
        {"label": "50th Percentile (Median)", "color": "green", "level": 0.5},
        {"label": "75th Percentile", "color": "blue", "level": 0.75},
        {"label": "90th Percentile", "color": "purple", "level": 0.9},
    ]

    # (2) 분위수 라인: 10%, 25%, 50%, 75%, 90%
    #    - Matplotlib에서는 plot()으로 라인을 그렸지만,
    #    - Plotly에서는 shape 혹은 scatter로 그릴 수 있습니다.
    #    여기서는 shape(line)로 그립니다.
    for i, equity in enumerate(recent_pe.index):
        x_left, x_right = i - 0.2, i + 0.2

        for idx, pinfo in enumerate(percentile_info):
            q_value = quantiles.loc[pinfo["level"], equity]
            show_legend_flag = (i == 0)

            fig.add_trace(
                go.Scatter(
                    x=[x_left, x_right],
                    y=[q_value, q_value],
                    mode="lines",
                    line=dict(color=pinfo["color"], width=2),
                    name=pinfo["label"] if show_legend_flag else None,
                    # hovertemplate 옵션을 통해 마우스 오버 시 표시될 내용 정의
                    hovertemplate=(
                        f"<b>{equity}</b><br>"
                        f"{pinfo['label']}: {q_value:.2f}<extra></extra>"
                    ),
                    showlegend=show_legend_flag,
                )
            )

    # (3) 최근 P/E 점 찍기 (검정색 동그라미), + text 표시
    fig.add_trace(
        go.Scatter(
            x=bar_x_positions,
            y=recent_pe,
            mode='markers+text',
            text=[f"{val:.2f}" for val in recent_pe],  # 데이터 라벨
            textposition="top center",
            marker=dict(color='black', size=12),
            name="Latest P/E",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Latest P/E: %{y:.2f}<extra></extra>"
            ),
        )
    )

    # (4) 1-Month DEMA 점 찍기 (빨간 별 모양)
    fig.add_trace(
        go.Scatter(
            x=bar_x_positions,
            y=dema_1_month,
            mode='markers',
            marker=dict(color='red', size=14, symbol='star'),  # 별 모양
            name="1-Month Ago",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "DEMA: %{y:.2f}<extra></extra>"
            ),
        )
    )

    # (5) 화살표(Annotation)로 DEMA -> Latest P/E 연결
    for i, equity in enumerate(recent_pe.index):
        fig.add_annotation(
            x=bar_x_positions[i],  # 화살표 도착 지점
            y=recent_pe[i],
            ax=bar_x_positions[i],  # 화살표 시작 지점
            ay=dema_1_month[i],
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="grey",
            opacity=0.5,
            standoff=2,
            startstandoff=2,
        )

    # 레이아웃 설정
    fig.update_layout(
        title="Fwd P/E Multiple Range with Quantile Data, 1-Month DEMA, and Latest P/E",
        xaxis_title="Equity Assets",
        yaxis_title="Fwd P/E Multiple",
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01),
        width=1000,
        height=600,
    )

    # X축 레이블: bar_x_positions를 실제 equity 종목명으로 치환
    fig.update_xaxes(
        tickmode='array',
        tickvals=bar_x_positions,
        ticktext=lowest_pe.index
    )

    # Y축 최대/최소도 적절히 설정(10% 정도 여유)
    y_max = max(highest_pe) * 1.1
    fig.update_yaxes(range=[0, 50])

    # 그리드 보이게
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)

    return fig
def create_fundamental_scatter_plot(data1, data2, st_list, data1_name, data2_name):

    # 스캐터 플롯 설정
    fig = go.Figure()


    # Add data points
    for asset in st_list:
        fig.add_trace(
            go.Scatter(
                x=[data1[asset]],
                y=[data2[asset]],
                mode="markers+text",
                text=[asset],
                textposition="top center",
                name=asset,
                marker=dict(size=10),
            )
        )

    # y=x 점선 추가
    fig.add_trace(
        go.Scatter(
            x=[-0.25, 0.25],
            y=[-0.25, 0.25],
            mode="lines",
            line=dict(color="gray", width=2, dash="dash"),
            name="y = x",
            showlegend=False
        )
    )

    # x축 0% 점선 추가
    fig.add_trace(
        go.Scatter(
            x=[0, 0],
            y=[-0.2, 0.2],
            mode="lines",
            line=dict(color="lightgray", width=1, dash="dot"),
            name="x = 0%",
            showlegend=False
        )
    )

    # y축 0% 점선 추가
    fig.add_trace(
        go.Scatter(
            x=[-0.2, 0.2],
            y=[0, 0],
            mode="lines",
            line=dict(color="lightgray", width=1, dash="dot"),
            name="y = 0%",
            showlegend=False
        )
    )

    # 레이아웃 설정
    fig.update_layout(
        title="Fundamental Analysis",
        xaxis_title=f"{data1_name} 3m Chg",
        yaxis_title=f"{data2_name} 3m Chg",
        xaxis=dict(tickformat=".2%", range=[-0.25, 0.25]),
        yaxis=dict(tickformat=".2%", range=[-0.25, 0.25]),
        hovermode="closest",
        template="plotly_white",
        height=600
    )

    return fig

def create_fundamental_scatter_plot_year(data1, data2, st_list, data1_name, data2_name):

    # 스캐터 플롯 설정
    fig = go.Figure()


    # Add data points
    for asset in st_list:
        fig.add_trace(
            go.Scatter(
                x=[data1[asset]],
                y=[data2[asset]],
                mode="markers+text",
                text=[asset],
                textposition="top center",
                name=asset,
                marker=dict(size=10),
            )
        )

    # y=x 점선 추가
    fig.add_trace(
        go.Scatter(
            x=[-0.5, 0.5],
            y=[-0.5, 0.5],
            mode="lines",
            line=dict(color="gray", width=2, dash="dash"),
            name="y = x",
            showlegend=False
        )
    )

    # x축 0% 점선 추가
    fig.add_trace(
        go.Scatter(
            x=[0, 0],
            y=[-0.2, 0.2],
            mode="lines",
            line=dict(color="lightgray", width=1, dash="dot"),
            name="x = 0%",
            showlegend=False
        )
    )

    # y축 0% 점선 추가
    fig.add_trace(
        go.Scatter(
            x=[-0.2, 0.2],
            y=[0, 0],
            mode="lines",
            line=dict(color="lightgray", width=1, dash="dot"),
            name="y = 0%",
            showlegend=False
        )
    )

    # 레이아웃 설정
    fig.update_layout(
        title="Fundamental Analysis",
        xaxis_title=f"{data1_name} 1Y Chg",
        yaxis_title=f"{data2_name} 1Y Chg",
        xaxis=dict(tickformat=".2%", range=[-0.5, 0.5]),
        yaxis=dict(tickformat=".2%", range=[-0.5, 0.5]),
        hovermode="closest",
        template="plotly_white",
        height=600
    )

    return fig

import numpy as np
import plotly.graph_objects as go


def plot_eps_pe_growth(eps: pd.DataFrame, pe: pd.DataFrame, stocks: list):
    """Forward EPS & P/E growth (3 M vs 1 M) ─ 인덱스별 스택 + 인라인 합계 표시"""

    # ─────────────────────────── 1│변화율 계산
    def pct(df, period):
        return (df.iloc[-1] - df.iloc[-period]) / df.iloc[-period] * 100

    eps3, pe3 = pct(eps, 63), pct(pe, 63)
    eps1, pe1 = pct(eps, 21), pct(pe, 21)
    sum3, sum1 = eps3 + pe3, eps1 + pe1

    # EPS와 PE 부호가 반대인지 확인
    opposite_sign3 = (eps3 * pe3 < 0).values
    opposite_sign1 = (eps1 * pe1 < 0).values

    # ── 2│바 위치 설정 - 정확히 붙어있도록 ──────────────────────────
    n = len(stocks)
    centers = np.arange(n)
    bar_width = 0.35  # 바 너비

    # 바가 정확히 붙어있도록 오프셋 계산
    left_bar_center = -bar_width / 2  # 왼쪽 바의 중심
    right_bar_center = bar_width / 2  # 오른쪽 바의 중심

    fig = go.Figure()

    # ── 3 M 바 그래프 추가 ──
    for i, (eps_val, pe_val, is_opposite) in enumerate(zip(eps3.values, pe3.values, opposite_sign3)):
        # EPS 3M 바
        fig.add_trace(go.Bar(
            x=[centers[i]],
            y=[eps_val],
            name='EPS (3 M)' if i == 0 else None,
            marker_color='skyblue',
            width=bar_width,
            offset=left_bar_center - bar_width / 2,  # 왼쪽 바의 왼쪽 경계
            showlegend=i == 0
        ))

        # P/E 3M 바
        if is_opposite:
            # 부호가 반대면 별도 바로 표시
            fig.add_trace(go.Bar(
                x=[centers[i]],
                y=[pe_val],
                name='P/E (3 M)' if i == 0 else None,
                marker_color='lightcoral',
                width=bar_width,
                offset=left_bar_center - bar_width / 2,  # 왼쪽 바의 왼쪽 경계
                showlegend=i == 0
            ))
        else:
            # 부호가 같으면 스택으로 표시
            fig.add_trace(go.Bar(
                x=[centers[i]],
                y=[pe_val],
                name='P/E (3 M)' if i == 0 else None,
                marker_color='lightcoral',
                width=bar_width,
                base=eps_val,  # EPS 위에 스택
                offset=left_bar_center - bar_width / 2,  # 왼쪽 바의 왼쪽 경계
                showlegend=i == 0
            ))

    # ── 1 M 바 그래프 추가 ──
    for i, (eps_val, pe_val, is_opposite) in enumerate(zip(eps1.values, pe1.values, opposite_sign1)):
        # EPS 1M 바
        fig.add_trace(go.Bar(
            x=[centers[i]],
            y=[eps_val],
            name='EPS (1 M)' if i == 0 else None,
            marker_color='lightgreen',
            width=bar_width,
            offset=right_bar_center - bar_width / 2,  # 오른쪽 바의 왼쪽 경계 (중심에서 반너비 뺌)
            showlegend=i == 0
        ))

        # P/E 1M 바
        if is_opposite:
            # 부호가 반대면 별도 바로 표시
            fig.add_trace(go.Bar(
                x=[centers[i]],
                y=[pe_val],
                name='P/E (1 M)' if i == 0 else None,
                marker_color='orange',
                width=bar_width,
                offset=right_bar_center - bar_width / 2,  # 오른쪽 바의 왼쪽 경계
                showlegend=i == 0
            ))
        else:
            # 부호가 같으면 스택으로 표시
            fig.add_trace(go.Bar(
                x=[centers[i]],
                y=[pe_val],
                name='P/E (1 M)' if i == 0 else None,
                marker_color='orange',
                width=bar_width,
                base=eps_val,  # EPS 위에 스택
                offset=right_bar_center - bar_width / 2,  # 오른쪽 바의 왼쪽 경계
                showlegend=i == 0
            ))

    # ── 합계 ● - 각 바 그래프 정중앙에 위치 ──
    # 3M 바 그래프 중앙에 검은 점 배치
    fig.add_trace(go.Scatter(
        x=[c + left_bar_center for c in centers],  # 왼쪽 바 정중앙
        y=sum3.values,
        mode='markers',
        marker=dict(color='black', size=8),
        showlegend=False
    ))

    # 1M 바 그래프 중앙에 검은 점 배치
    fig.add_trace(go.Scatter(
        x=[c + right_bar_center for c in centers],  # 오른쪽 바 정중앙
        y=sum1.values,
        mode='markers',
        marker=dict(color='black', size=8),
        showlegend=False
    ))

    # 합계 텍스트 - 각 바 위에 표시
    for bar_center, sums in [(left_bar_center, sum3), (right_bar_center, sum1)]:
        text_offset = np.array([4 if v >= 0 else -4 for v in sums.values])
        fig.add_trace(go.Scatter(
            x=[c + bar_center for c in centers],
            y=sums.values + text_offset,
            mode='text',
            text=[f'{v:.1f}%' for v in sums.values],
            textfont=dict(color='white', size=16),
            showlegend=False
        ))

    # ─────────────────────────── 3│레이아웃 - 가독성 향상
    fig.update_layout(
        barmode='overlay',
        bargap=0.15,
        title='Forward EPS & P/E Growth (3 M vs 1 M)',
        xaxis=dict(
            tickmode='array',
            tickvals=centers,
            ticktext=stocks,
            tickangle=-45,
            title_standoff=15
        ),
        yaxis=dict(
            title='Growth (%)',
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.3)',
            zerolinewidth=1.5
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.2)'
        ),
        template='plotly_dark',
        width=max(1000, 75 * n),
        height=500,
        plot_bgcolor='rgba(0,0,0,0.2)',
        margin=dict(t=50, b=80, l=70, r=40)
    )

    # 그리드 라인 추가
    fig.update_yaxes(
        showgrid=True,
        gridwidth=0.5,
        gridcolor='rgba(255,255,255,0.1)'
    )

    # 주석 추가 (별도의 바 그래프 설명)
    fig.add_annotation(
        x=0.01,
        y=0.98,
        xref="paper",
        yref="paper",
        text="EPS와 P/E 부호가 반대인 경우: 별도 바 표시",
        showarrow=False,
        font=dict(size=10, color="white"),
        bgcolor="rgba(0,0,0,0.5)",
        bordercolor="white",
        borderwidth=1,
        borderpad=4,
        align="left"
    )

    return fig


def plot_eps_pe_growth_v2(eps, pe, st_list):
    # Calcualte the growth rates
    def calculate_growth(df, period):
        return (df.iloc[-1] - df.iloc[-period]) / df.iloc[-period] * 100

    eps_growth_3month = calculate_growth(eps, 63)
    eps_growth_1month = calculate_growth(eps, 21)
    pe_growth_3month = calculate_growth(pe, 63)
    pe_growth_1month = calculate_growth(pe, 21)

    # Prepare data for the plot
    stocks = eps.columns
    growth_data = []

    for stock in stocks:
        growth_data.append((stock, '3 Month', eps_growth_3month[stock], pe_growth_3month[stock]))
        growth_data.append((stock, '1 Month', eps_growth_1month[stock], pe_growth_1month[stock]))

    growth_df = pd.DataFrame(growth_data, columns=['Stock', 'Period', 'EPS Growth', 'PE Growth'])

    fig = go.Figure()
    colors = ['skyblue', 'lightgreen']
    pe_colors = ['lightcoral', 'orange']
    bar_width = 0.35
    space_between_stocks = 1.5

    # Calculate positions
    positions = np.arange(len(stocks)) * (2 * bar_width + space_between_stocks)

    for idx, period in enumerate(growth_df['Period'].unique()):
        period_data = growth_df[growth_df['Period'] == period]
        bar_positions = positions + idx * bar_width

        # Plot EPS Growth bars
        fig.add_trace(go.Bar(
            x=bar_positions,
            y=period_data['EPS Growth'],
            name=f'EPS Growth ({period})',
            marker_color=colors[idx],
            width=bar_width,
            offset=0,
        ))

        # Plot P/E growth bars seperately for positive and negative values
        for i, (x, eps, pe) in enumerate(zip(bar_positions, period_data['EPS Growth'], period_data['PE Growth'])):
            if pe >= 0:
                fig.add_trace(go.Bar(
                    x=[x],
                    y=[pe],
                    base=[max(0, eps)],
                    marker_color=pe_colors[idx],
                    width=bar_width,
                    name=f'PE Growth ({period})' if i == 0 else "",
                    offset=0,
                    showlegend=False if i != 0 else True,
                ))
            else:
                fig.add_trace(go.Bar(
                    x=[x],
                    y=[pe],
                    base=[0],
                    marker_color=pe_colors[idx],
                    width=bar_width,
                    name=f'PE Growth ({period})' if i == 0 else "",
                    offset=0,
                    showlegend=False if i != 0 else True,

                ))

            # Plot the sum EPS and PE growth as circles with numbers
            total_growth = eps + pe
            fig.add_trace(go.Scatter(
                x=[x],
                y=[total_growth],
                mode='markers+text',
                text=[f'{total_growth:.1f}%'],
                textposition='top center' if total_growth >= 0 else 'bottom center',
                marker=dict(color='black', size=10),
                showlegend=False,
            ))

    # Customize the plot
    fig.update_layout(
        title='Forward EPS and P/E Growth for 3 Month and 1 Month',
        xaxis_title='Stocks',
        yaxis_title='Growth (%)',
        xaxis=dict(
            tickmode='array',
            tickvals=positions + bar_width / 2,
            ticktext=stocks,
            tickangle=-45,
        ),
        barmode='overlay',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        bargap=0.4,
        bargroupgap=0.2,
    )

    return fig

def plot_fwd_metrics_timeline(eps_data, fcf_data, tickers, last_n_days=252*3):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import pandas as pd

    # Filter data for the last year
    end_date = eps_data.index.max()
    start_date = end_date - pd.Timedelta(days=last_n_days)

    eps_filtered = eps_data.loc[start_date:end_date]
    fcf_filtered = fcf_data.loc[start_date:end_date]

    # Create subplots
    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=('Forward EPS 3-Month Change', 'Forward FCF 3-Month Change'))

    # Add treaces for EPS
    for ticker in tickers:
        fig.add_trace(
            go.Scatter(
                x=eps_filtered.index,
                y=eps_filtered[ticker],
                name=f"{ticker} - EPS",
                line=dict(width=2),
                legendgroup=ticker,
            ),
            row=1, col=1
        )

    # Add traces for FCF
    for ticker in tickers:
        fig.add_trace(
            go.Scatter(
                x=fcf_filtered.index,
                y=fcf_filtered[ticker],
                name=f"{ticker} - FCF",
                line=dict(width=2, dash='dot'),
                legendgroup=ticker,
                showlegend=False
            ),
        row=2, col=1
        )

    # Add a zero line to both plots
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray", row=1, col=1)
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray", row=2, col=1)

    # Update layout
    fig.update_layout(
        title='Forward EPS and FCF 3-Month Change (Last Year)',
        height=800,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template='plotly_white'
    )

    # Update y-axes to show percentages
    fig.update_yaxes(tickformat='.2%', title_text='Change (%)', row=1, col=1)
    fig.update_yaxes(tickformat='.2%', title_text='Change (%)', row=2, col=1)

    # Update x-axis
    fig.update_xaxes(title_text='Date', row=2, col=1)

    return fig

# 종목 리스트 (main.py에서 사용한 것과 동일하게 설정)
st_list = ['SPX Index', 'NDX Index', 'DJI Index', 'RTY Index',
           'SX5E Index', 'DAX Index', 'CAC Index', 'NKY Index', 'BM7P Index', 'BAI Index', 'UKX Index',
           'SHCOMP Index', 'HSI Index']

Index_sector_list = ['SPX Index', 'NDX Index', 'BAI Index', 'BM7P Index', 'B500XM7P Index',
                     'S5TELS Index', 'S5CONS Index', 'S5COND Index', 'S5ENRS Index',
                     'S5FINL Index', 'S5HLTH Index', 'S5INDU Index', 'S5INFT Index', 'S5MATR Index', 'S5UTIL Index',
                     'S5SFTW Index', 'S5TECH Index', 'S5SSEQX Index']

Index_sector = ['S&P500','NDX','BAI','M7','ex-M7','Tele-com','Con.stpls','Con.dis','Energy','Financial',
                    'Healthcare','Industrials','Info-Tech','Materials','Utilities',
                    'Tech-Software','Tech-Hard','Tech-Semi']

Euro_sector_list = ['SX5E Index','SX7P Index', 'S600FOP Index', 'SXIP Index', 'SXRP Index', 'SX8P Index', 'SXKP Index', 'SXFP Index',
                    'SXDP Index', 'SXNP Index', 'SXMP Index', 'S600PDP Index','SX86P Index','SXTP Index','SX6P Index','SXAP Index',
                    'SXPP Index','SX4P Index','S600CPP Index','S600ENP Index']

Euro_sector = ['EuroStoxx50', 'Banks', 'Food&Bev&Tob', 'Insurance', 'Retailers', 'Technology', 'Telecoms', 'Financial Ser',
               'Healthcare', 'Industrail G&S', 'Media','Per.Care & Grocery','Real Estate','Travel & Leisure','Utilities',
               'Autos and Parts','Basic Resource','Chemicals','Consum P&S','Energy']




Euro_sector_filtered = ['EuroStoxx50', 'Food&Bev&Tob', 'Insurance', 'Retailers', 'Technology', 'Telecoms', 'Financial Ser',
               'Healthcare', 'Industrail G&S', 'Media','Per.Care & Grocery','Real Estate','Travel & Leisure','Utilities',
               'Autos and Parts','Basic Resource','Chemicals','Consum P&S','Energy']

# 섹션 1: 누적 수익률 그래프
st.subheader('Cumulative Returns Comparison')

fig = go.Figure()
#fig.add_trace(go.Scatter(x=benchmark_cum_returns.index, y=benchmark_cum_returns.values.flatten(),
#                         mode='lines', name='Benchmark Portfolio'))
fig.add_trace(go.Scatter(x=actual_cum_returns.index, y=actual_cum_returns.values.flatten(),
                         mode='lines', name='Actual Portfolio'))
fig.add_trace(go.Scatter(x=actual_cum_returns_new.index, y=actual_cum_returns_new.values.flatten(),
                         mode='lines', name = 'Adaptive Actual Portfolio'))
fig.add_trace(go.Scatter(x=actual_cum_returns_overlay.index, y=actual_cum_returns_overlay.values.flatten(),
                         mode='lines', name = 'Mom Overlay Portfolio(5%)'))
fig.add_trace(go.Scatter(x=actual_cum_returns_eps_overlay.index, y=actual_cum_returns_eps_overlay.values.flatten(),
                         mode='lines', name = 'EPS Overlay Portfolio(5%)'))
fig.add_trace(go.Scatter(x=actual_cum_returns_combined_overlay.index, y=actual_cum_returns_combined_overlay.values.flatten(),
                         mode='lines', name = 'Combined Overlay Portfolio(10%)'))
fig.add_trace(go.Scatter(x=actual_cum_returns_growth.index, y=actual_cum_returns_growth.values.flatten(),
                         mode='lines', name = 'Growth Portfolio'))
fig.add_trace(go.Scatter(x=actual_cum_returns_momentum.index, y=actual_cum_returns_momentum.values.flatten(),
                         mode='lines', name = 'Momentum Portfolio'))
fig.update_layout(
    title='Cumulative Returns Comparison (After Transaction Costs)',
    xaxis_title='Date',
    yaxis_title='Cumulative Returns',
    legend_title='Portfolio',
    template='plotly_white',  # 깔끔한 배경
    height=600  # 그래프 높이 설정
)
st.plotly_chart(fig, use_container_width=True)

# 섹션 2: 연도별 수익률 테이블
st.subheader('Annual Returns Comparison')
st.dataframe(annual_returns.style.format("{:.2%}"))

# 섹션 3: 성과 분해
st.subheader('Performance Decomposition')

selected_year = st.selectbox('Select Year', sorted(performance_decomposition_df.index))
decomposition_data = performance_decomposition_df.loc[selected_year]

categories = ['Top', 'Middle', 'Bottom']
bm_values = [decomposition_data['Benchmark_Top'], decomposition_data['Benchmark_Middle'],
             decomposition_data['Benchmark_Bottom']]
act_values = [decomposition_data['Actual_Top'], decomposition_data['Actual_Middle'],
              decomposition_data['Actual_Bottom']]

fig2 = go.Figure(data=[
    go.Bar(name='Benchmark', x=categories, y=bm_values),
    go.Bar(name='Actual Portfolio', x=categories, y=act_values)
])

fig2.update_layout(
    barmode='group',
    title=f'Performance Contribution Comparison for {selected_year}',
    xaxis_title='Category',
    yaxis_title='Contribution',
    legend_title='Portfolio',
    template='plotly_white',
    height=600
)
st.plotly_chart(fig2, use_container_width=True)


# 색상 맵 정의 (인덱스와 섹터 티커에 대한 일관된 색상 할당)
def create_color_map(ticker_list):
    color_map = {}
    for i, ticker in enumerate(ticker_list):
        color_idx = i % len(px.colors.qualitative.Plotly)
        color = px.colors.qualitative.Plotly[color_idx]
        color_map[ticker] = color
    return color_map


# 인덱스 및 섹터 티커에 대한 색상 맵 생성
index_ticker_colors = create_color_map(st_list)
sector_ticker_colors = create_color_map(Index_sector)


# 타임라인 시각화 함수 수정 - 색상 매핑 추가
def plot_fwd_metrics_timeline(eps_data, fcf_data, tickers, last_n_days=252*3, color_map=None):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import pandas as pd

    # Filter data for the last year
    end_date = eps_data.index.max()
    start_date = end_date - pd.Timedelta(days=last_n_days)

    eps_filtered = eps_data.loc[start_date:end_date]
    fcf_filtered = fcf_data.loc[start_date:end_date]

    # Create subplots
    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=('Forward EPS 3-Month Change', 'Forward FCF 3-Month Change'))

    # Add traces for EPS
    for ticker in tickers:
        # 색상 맵이 제공된 경우 해당 색상 사용, 아니면 자동 할당
        line_color = color_map.get(ticker) if color_map else None

        fig.add_trace(
            go.Scatter(
                x=eps_filtered.index,
                y=eps_filtered[ticker],
                name=f"{ticker} - EPS",
                line=dict(width=2, color=line_color),
                legendgroup=ticker,
            ),
            row=1, col=1
        )

    # Add traces for FCF
    for ticker in tickers:
        # 같은 티커는 같은 색상 사용 (점선으로 구분)
        line_color = color_map.get(ticker) if color_map else None

        fig.add_trace(
            go.Scatter(
                x=fcf_filtered.index,
                y=fcf_filtered[ticker],
                name=f"{ticker} - FCF",
                line=dict(width=2, dash='dot', color=line_color),
                legendgroup=ticker,
                showlegend=False
            ),
            row=2, col=1
        )

    # Add a zero line to both plots
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray", row=1, col=1)
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray", row=2, col=1)

    # Update layout
    fig.update_layout(
        title='Forward EPS and FCF 3-Month Change (Last Year)',
        height=800,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template='plotly_white'
    )

    # Update y-axes to show percentages
    fig.update_yaxes(tickformat='.2%', title_text='Change (%)', row=1, col=1)
    fig.update_yaxes(tickformat='.2%', title_text='Change (%)', row=2, col=1)

    # Update x-axis
    fig.update_xaxes(title_text='Date', row=2, col=1)

    return fig


# EPS/FCF 섹션
#available_months = sorted(monthly_rebalance_dates.keys())
st.subheader('Fudamental Analysis')

#dates = pd.to_datetime(pd.date_range(us_eps_fwd_3m.index[0],us_eps_fwd_3m.index[-1] ,freq='M'))
#ytrebalance_dates = available_months

st.title("Fundamental Anaysis 3M")
#selected_date_growth = st.selectbox('Select Date for Growth Portfolio', growth_3y_weights.index.strftime('%Y-%m-%d'))

# 날짜를 내림차순으로 정렬 (최신 날짜가 먼저 오도록)
sorted_dates_3m = sorted(growth_3y_weights.index.strftime('%Y-%m-%d'), reverse=True)

# 가장 최신 날짜를 기본값으로 선택
fun_date = st.selectbox('Select Date', sorted_dates_3m, key="selectbox_fundamental")


eps_growth_data = us_eps_fwd_3m.loc[fun_date]
fcf_growth_data = index_fcf_fwd_3m.loc[fun_date]
sales_growth_data = us_sales_fwd_3m.loc[fun_date]



# Scatter Plot 생성
col1, col2 = st.columns(2)
with col1:
    fig1 = go.Figure()
    for asset in st_list:
        fig1.add_trace(
            go.Scatter(
                x=[eps_growth_data[asset]],
                y=[fcf_growth_data[asset]],
                mode="markers+text",
                text=[asset],
                textposition="top center",
                name=asset,
                marker=dict(size=10),
            )
        )
    fig1.add_trace(
        go.Scatter(
            x=[-0.2,0.2],
            y=[-0.2,0.2],
            mode='lines',
            line=dict(color='gray', width=2, dash='dash'),
            showlegend=False
        )
    )
    fig1.update_layout(
        title="Fundamental - EPS & FCF",
        xaxis_title='Forward EPS 3m chg',
        yaxis_title='Forward FCF 3m chg',
        xaxis=dict(tickformat=".2%", range=[-0.2,0.2]),
        yaxis=dict(tickformat=".2%", range=[-0.2,0.2]),
        hovermode="closest",
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = go.Figure()
    for asset in st_list:
        fig2.add_trace(
            go.Scatter(
                x=[eps_growth_data[asset]],
                y=[sales_growth_data[asset]],
                mode="markers+text",
                text=[asset],
                textposition="top center",
                name=asset,
                marker=dict(size=10),

            )
        )
    fig2.add_trace(
        go.Scatter(
            x=[-0.2, 0.2],
            y=[-0.2, 0.2],
            mode='lines',
            line=dict(color="gray", width=2, dash="dash"),
            showlegend=False
        )
    )

    fig2.update_layout(
        title="Fundamental - Sales & EPS",
        yaxis_title="Forward Sales 3 month chg",  # x와 y 레이블을 바꿈
        xaxis_title="Forward EPS month chg",  # x와 y 레이블을 바꿈
        yaxis=dict(tickformat=".2%", range=[-0.2, 0.2]),
        xaxis=dict(tickformat=".2%", range=[-0.2, 0.2]),
        hovermode="closest",
        template="plotly_white",
        height=450
    )

    st.plotly_chart(fig2, use_container_width=True)

st.title("Fundamental Anaysis 1y")
# 날짜를 내림차순으로 정렬 (최신 날짜가 먼저 오도록)
sorted_dates_1y = sorted(growth_3y_weights.index.strftime('%Y-%m-%d'), reverse=True)

# 가장 최신 날짜를 기본값으로 선택
fun_date_1y = st.selectbox('Select Date', sorted_dates_1y, key="selectbox_fundamental_1y")

eps_growth_data_1y = us_eps_fwd_1y.loc[fun_date_1y]
fcf_growth_data_1y = index_fcf_fwd_1y.loc[fun_date_1y]
sales_growth_data_1y = us_sales_fwd_1y.loc[fun_date_1y]


# Scatter Plot 생성
col1, col2 = st.columns(2)
with col1:
    fig1 = go.Figure()
    for asset in st_list:
        fig1.add_trace(
            go.Scatter(
                x=[eps_growth_data_1y[asset]],
                y=[fcf_growth_data_1y[asset]],
                mode="markers+text",
                text=[asset],
                textposition="top center",
                name=asset,
                marker=dict(size=10),
            )
        )
    fig1.add_trace(
        go.Scatter(
            x=[-0.5,0.5],
            y=[-0.5,0.5],
            mode='lines',
            line=dict(color='gray', width=2, dash='dash'),
            showlegend=False
        )
    )
    fig1.update_layout(
        title="Fundamental - EPS & FCF",
        xaxis_title='Forward EPS 1y chg',
        yaxis_title='Forward FCF 1y chg',
        xaxis=dict(tickformat=".2%", range=[-0.75,0.75]),
        yaxis=dict(tickformat=".2%", range=[-0.75,0.75]),
        hovermode="closest",
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = go.Figure()
    for asset in st_list:
        fig2.add_trace(
            go.Scatter(
                x=[eps_growth_data_1y[asset]],
                y=[sales_growth_data_1y[asset]],
                mode="markers+text",
                text=[asset],
                textposition="top center",
                name=asset,
                marker=dict(size=10),

            )
        )
    fig2.add_trace(
        go.Scatter(
            x=[-0.75, 0.75],
            y=[-0.75, 0.75],
            mode='lines',
            line=dict(color="gray", width=2, dash="dash"),
            showlegend=False
        )
    )

    fig2.update_layout(
        title="Fundamental - Sales & EPS",
        yaxis_title="Forward Sales 1y chg",  # x와 y 레이블을 바꿈
        xaxis_title="Forward EPS 1y chg",  # x와 y 레이블을 바꿈
        yaxis=dict(tickformat=".2%", range=[-0.75, 0.75]),
        xaxis=dict(tickformat=".2%", range=[-0.75, 0.75]),
        hovermode="closest",
        template="plotly_white",
        height=450
    )

    st.plotly_chart(fig2, use_container_width=True)



render_fundamental_section_enhanced(
    "Regional Indices Fundamental (3M)",
    eps_3m=us_eps_fwd_3m,
    fcf_3m=index_fcf_fwd_3m,
    sales_3m=us_sales_fwd_3m,
    eps_1y=us_eps_fwd_1y,
    fcf_1y=index_fcf_fwd_1y,
    sales_1y=us_sales_fwd_1y,
    universe=st_list
)
#-====================US Sector Fundamental======================================


st.title("Fundamental Anaysis 3M - US Sector")
#selected_date_growth = st.selectbox('Select Date for Growth Portfolio', growth_3y_weights.index.strftime('%Y-%m-%d'))

# 날짜를 내림차순으로 정렬 (최신 날짜가 먼저 오도록)
sorted_dates_sec_3m = sorted(growth_3y_weights.index.strftime('%Y-%m-%d'), reverse=True)

# 가장 최신 날짜를 기본값으로 선택
fun_date_sec = st.selectbox('Select Date', sorted_dates_sec_3m, key="selectbox_fundamental_3m_sec")

eps_growth_data_sec = us_eps_fwd_3m_sec.loc[fun_date_sec]
fcf_growth_data_sec = index_fcf_fwd_3m_sec.loc[fun_date_sec]
sales_growth_data_sec = us_sales_fwd_3m_sec.loc[fun_date_sec]

col1, col2 = st.columns(2)
with col1:
    fig_sec1 = go.Figure()
    for asset in Index_sector:
        fig_sec1.add_trace(
            go.Scatter(
                x=[eps_growth_data_sec[asset]],
                y=[fcf_growth_data_sec[asset]],
                mode="markers+text",
                text=[asset],
                textposition="top center",
                name=asset,
                marker=dict(size=10),
            )
        )
    fig_sec1.add_trace(
        go.Scatter(
            x=[-0.2,0.3],
            y=[-0.2,0.3],
            mode='lines',
            line=dict(color='gray', width=2, dash='dash'),
            showlegend=False
        )
    )
    fig_sec1.update_layout(
        title="Fundamental - EPS & FCF",
        xaxis_title='Forward EPS 3m chg',
        yaxis_title='Forward FCF 3m chg',
        xaxis=dict(tickformat=".2%", range=[-0.2,0.3]),
        yaxis=dict(tickformat=".2%", range=[-0.2,0.3]),
        hovermode="closest",
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig_sec1, use_container_width=True)

with col2:
    fig_sec2 = go.Figure()
    for asset in Index_sector:
        fig_sec2.add_trace(
            go.Scatter(
                x=[eps_growth_data_sec[asset]],
                y=[sales_growth_data_sec[asset]],
                mode="markers+text",
                text=[asset],
                textposition="top center",
                name=asset,
                marker=dict(size=10),

            )
        )
    fig_sec2.add_trace(
        go.Scatter(
            x=[-0.2, 0.3],
            y=[-0.2, 0.3],
            mode='lines',
            line=dict(color="gray", width=2, dash="dash"),
            showlegend=False
        )
    )

    fig_sec2.update_layout(
        title="Fundamental - Sales & EPS",
        yaxis_title="Forward Sales 3 month chg",  # x와 y 레이블을 바꿈
        xaxis_title="Forward EPS 3 month chg",  # x와 y 레이블을 바꿈
        yaxis=dict(tickformat=".2%", range=[-0.2, 0.3]),
        xaxis=dict(tickformat=".2%", range=[-0.2, 0.3]),
        hovermode="closest",
        template="plotly_white",
        height=450
    )

    st.plotly_chart(fig_sec2, use_container_width=True)


st.title("Fundamental Anaysis 1Y - US Sector")
#selected_date_growth = st.selectbox('Select Date for Growth Portfolio', growth_3y_weights.index.strftime('%Y-%m-%d'))
# 날짜를 내림차순으로 정렬 (최신 날짜가 먼저 오도록)
sorted_dates_sec_1y = sorted(growth_3y_weights.index.strftime('%Y-%m-%d'), reverse=True)

# 가장 최신 날짜를 기본값으로 선택
fun_date_sec_1y = st.selectbox('Select Date', sorted_dates_sec_1y, key="selectbox_fundamental_1y_sec")


eps_growth_data_sec_1y = us_eps_fwd_1y_sec.loc[fun_date_sec_1y]
fcf_growth_data_sec_1y = index_fcf_fwd_1y_sec.loc[fun_date_sec_1y]
sales_growth_data_sec_1y = us_sales_fwd_1y_sec.loc[fun_date_sec_1y]


col1, col2 = st.columns(2)
with col1:
    fig_sec1 = go.Figure()
    for asset in Index_sector:
        fig_sec1.add_trace(
            go.Scatter(
                x=[eps_growth_data_sec_1y[asset]],
                y=[fcf_growth_data_sec_1y[asset]],
                mode="markers+text",
                text=[asset],
                textposition="top center",
                name=asset,
                marker=dict(size=10),
            )
        )
    fig_sec1.add_trace(
        go.Scatter(
            x=[-0.5,0.5],
            y=[-0.5,0.5],
            mode='lines',
            line=dict(color='gray', width=2, dash='dash'),
            showlegend=False
        )
    )
    fig_sec1.update_layout(
        title="Fundamental - EPS & FCF",
        xaxis_title='Forward EPS 1y chg',
        yaxis_title='Forward FCF 1y chg',
        xaxis=dict(tickformat=".2%", range=[-0.5,0.5]),
        yaxis=dict(tickformat=".2%", range=[-0.5,0.5]),
        hovermode="closest",
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig_sec1, use_container_width=True)

with col2:
    fig_sec2 = go.Figure()
    for asset in Index_sector:
        fig_sec2.add_trace(
            go.Scatter(
                x=[eps_growth_data_sec_1y[asset]],
                y=[sales_growth_data_sec_1y[asset]],
                mode="markers+text",
                text=[asset],
                textposition="top center",
                name=asset,
                marker=dict(size=10),

            )
        )
    fig_sec2.add_trace(
        go.Scatter(
            x=[-0.5, 0.5],
            y=[-0.5, 0.5],
            mode='lines',
            line=dict(color="gray", width=2, dash="dash"),
            showlegend=False
        )
    )

    fig_sec2.update_layout(
        title="Fundamental - Sales & EPS",
        yaxis_title="Forward Sales 1y chg",  # x와 y 레이블을 바꿈
        xaxis_title="Forward EPS 1y chg",  # x와 y 레이블을 바꿈
        yaxis=dict(tickformat=".2%", range=[-0.5, 0.5]),
        xaxis=dict(tickformat=".2%", range=[-0.5, 0.5]),
        hovermode="closest",
        template="plotly_white",
        height=450
    )

    st.plotly_chart(fig_sec2, use_container_width=True)


render_fundamental_section_enhanced(
    "US Sectors Fundamental(3M)",
    eps_3m=us_eps_fwd_3m_sec,
    fcf_3m=index_fcf_fwd_3m_sec,
    sales_3m=us_sales_fwd_3m_sec,
    eps_1y=us_eps_fwd_1y_sec,
    fcf_1y=index_fcf_fwd_1y_sec,
    sales_1y=us_sales_fwd_1y_sec,
    universe=Index_sector
)

#================Pe Multiple bands============================
st.title("Fwd P/E Multiple(3Y)")

fig_pe = plot_pe_bands_plotly(pe_index_bd.set_index('date')[st_list])

st.plotly_chart(fig_pe, use_container_width=True)

#================EPS + PE============================
st.title("EPS and PE Growth Visualization")


fig_eps_pe = plot_eps_pe_growth(eps_res_bd, pe_index_bd.set_index('date')[st_list], st_list)

st.plotly_chart(fig_eps_pe, use_container_width=True)


#================EPS + PE============================
st.title("EPS and PE Growth Sector Visualization")


fig_eps_pe = plot_eps_pe_growth(eps_res_bd_sec, pe_index_bd.set_index('date')[Index_sector_list], Index_sector_list)

st.plotly_chart(fig_eps_pe, use_container_width=True)
#=============================================================================================================================

#================US Sectors Pe Multiple bands============================
st.title("Fwd P/E Multiple(3Y)")

fig_pe_us_sec = plot_pe_bands_plotly(pe_index_bd_sec[Index_sector])

st.plotly_chart(fig_pe_us_sec, use_container_width=True)


# ================== European Sector Fundamental Analysis ==================


# ================== European Sector 3M Fundamental Analysis ==================
st.title("European Sector Fundamental Analysis 3M")

# Dates selector for Euro sector 3M
sorted_dates_euro_3m = sorted(growth_3y_weights.index.strftime('%Y-%m-%d'), reverse=True)
euro_fun_date_3m = st.selectbox('Select Date', sorted_dates_euro_3m, key="selectbox_euro_fundamental_3m")

# Get data for the selected date
euro_eps_growth_data_3m = euro_eps_fwd_3m_sec.loc[euro_fun_date_3m]
euro_fcf_growth_data_3m = euro_fcf_fwd_3m_sec.loc[euro_fun_date_3m]
euro_sales_growth_data_3m = euro_sales_fwd_3m_sec.loc[euro_fun_date_3m]

# Use the full Euro_sector list (including Banks)
col1, col2 = st.columns(2)
with col1:
    fig_euro_3m_1 = go.Figure()
    for asset in Euro_sector:
        # Check if asset exists in both datasets before adding to plot
        if asset in euro_eps_growth_data_3m.index:
            # For FCF plot, if 'Banks' doesn't have FCF data, we'll just plot EPS vs 0 for Banks
            fcf_value = euro_fcf_growth_data_3m.get(asset, 0)
            fig_euro_3m_1.add_trace(
                go.Scatter(
                    x=[euro_eps_growth_data_3m[asset]],
                    y=[fcf_value],
                    mode="markers+text",
                    text=[asset],
                    textposition="top center",
                    name=asset,
                    marker=dict(size=10),
                )
            )
    fig_euro_3m_1.add_trace(
        go.Scatter(
            x=[-0.2, 0.2],
            y=[-0.2, 0.2],
            mode='lines',
            line=dict(color='gray', width=2, dash='dash'),
            showlegend=False
        )
    )
    # Add x=0 reference line
    fig_euro_3m_1.add_trace(
        go.Scatter(
            x=[0, 0],
            y=[-0.2, 0.2],
            mode="lines",
            line=dict(color="lightgray", width=1, dash="dot"),
            name="x = 0%",
            showlegend=False
        )
    )
    # Add y=0 reference line
    fig_euro_3m_1.add_trace(
        go.Scatter(
            x=[-0.2, 0.2],
            y=[0, 0],
            mode="lines",
            line=dict(color="lightgray", width=1, dash="dot"),
            name="y = 0%",
            showlegend=False
        )
    )
    fig_euro_3m_1.update_layout(
        title="European Sectors - EPS & FCF",
        xaxis_title='Forward EPS 3m chg',
        yaxis_title='Forward FCF 3m chg',
        xaxis=dict(tickformat=".2%", range=[-0.2, 0.2]),
        yaxis=dict(tickformat=".2%", range=[-0.2, 0.2]),
        hovermode="closest",
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig_euro_3m_1, use_container_width=True)

with col2:
    fig_euro_3m_2 = go.Figure()
    for asset in Euro_sector:  # or Euro_sector_filtered if you want to exclude Banks
        # Check if asset exists in both datasets before adding to plot
        if asset in euro_eps_growth_data_3m.index and asset in euro_sales_growth_data_3m.index:
            fig_euro_3m_2.add_trace(
                go.Scatter(
                    x=[euro_eps_growth_data_3m[asset]],
                    y=[euro_sales_growth_data_3m[asset]],
                    mode="markers+text",
                    text=[asset],
                    textposition="top center",
                    name=asset,
                    marker=dict(size=10),
                )
            )
    fig_euro_3m_2.add_trace(
        go.Scatter(
            x=[-0.2, 0.2],
            y=[-0.2, 0.2],
            mode='lines',
            line=dict(color="gray", width=2, dash="dash"),
            showlegend=False
        )
    )
    # Add x=0 reference line
    fig_euro_3m_2.add_trace(
        go.Scatter(
            x=[0, 0],
            y=[-0.2, 0.2],
            mode="lines",
            line=dict(color="lightgray", width=1, dash="dot"),
            name="x = 0%",
            showlegend=False
        )
    )
    # Add y=0 reference line
    fig_euro_3m_2.add_trace(
        go.Scatter(
            x=[-0.2, 0.2],
            y=[0, 0],
            mode="lines",
            line=dict(color="lightgray", width=1, dash="dot"),
            name="y = 0%",
            showlegend=False
        )
    )
    fig_euro_3m_2.update_layout(
        title="European Sectors - Sales & EPS",
        yaxis_title="Forward Sales 3 month chg",
        xaxis_title="Forward EPS 3 month chg",
        yaxis=dict(tickformat=".2%", range=[-0.2, 0.2]),
        xaxis=dict(tickformat=".2%", range=[-0.2, 0.2]),
        hovermode="closest",
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig_euro_3m_2, use_container_width=True)

# ================== European Sector 1Y Fundamental Analysis ==================
st.title("European Sector Fundamental Analysis 1Y")

# Dates selector for Euro sector 1Y
sorted_dates_euro_1y = sorted(growth_3y_weights.index.strftime('%Y-%m-%d'), reverse=True)
euro_fun_date_1y = st.selectbox('Select Date', sorted_dates_euro_1y, key="selectbox_euro_fundamental_1y")

# Get data for the selected date
euro_eps_growth_data_1y = euro_eps_fwd_1y_sec.loc[euro_fun_date_1y]
euro_fcf_growth_data_1y = euro_fcf_fwd_1y_sec.loc[euro_fun_date_1y]
euro_sales_growth_data_1y = euro_sales_fwd_1y_sec.loc[euro_fun_date_1y]

# Create scatter plots - using full Euro_sector list including Banks
col1, col2 = st.columns(2)
with col1:
    fig_euro_1y_1 = go.Figure()
    for asset in Euro_sector:  # Use full Euro_sector list including Banks
        # Check if asset exists in EPS dataset
        if asset in euro_eps_growth_data_1y.index:
            # For FCF plot, if 'Banks' doesn't have FCF data, use 0 or another default
            fcf_value = euro_fcf_growth_data_1y.get(asset, 0)  # Use 0 if asset not in FCF data
            fig_euro_1y_1.add_trace(
                go.Scatter(
                    x=[euro_eps_growth_data_1y[asset]],
                    y=[fcf_value],
                    mode="markers+text",
                    text=[asset],
                    textposition="top center",
                    name=asset,
                    marker=dict(size=10),
                )
            )
    fig_euro_1y_1.add_trace(
        go.Scatter(
            x=[-0.5, 0.5],
            y=[-0.5, 0.5],
            mode='lines',
            line=dict(color='gray', width=2, dash='dash'),
            showlegend=False
        )
    )
    # Add x=0 reference line
    fig_euro_1y_1.add_trace(
        go.Scatter(
            x=[0, 0],
            y=[-0.5, 0.5],
            mode="lines",
            line=dict(color="lightgray", width=1, dash="dot"),
            name="x = 0%",
            showlegend=False
        )
    )
    # Add y=0 reference line
    fig_euro_1y_1.add_trace(
        go.Scatter(
            x=[-0.5, 0.5],
            y=[0, 0],
            mode="lines",
            line=dict(color="lightgray", width=1, dash="dot"),
            name="y = 0%",
            showlegend=False
        )
    )
    fig_euro_1y_1.update_layout(
        title="European Sectors - EPS & FCF",
        xaxis_title='Forward EPS 1y chg',
        yaxis_title='Forward FCF 1y chg',
        xaxis=dict(tickformat=".2%", range=[-0.5, 0.5]),
        yaxis=dict(tickformat=".2%", range=[-0.5, 0.5]),
        hovermode="closest",
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig_euro_1y_1, use_container_width=True)

with col2:
    fig_euro_1y_2 = go.Figure()
    for asset in Euro_sector:  # Use full Euro_sector list including Banks
        # Check if asset exists in EPS dataset
        if asset in euro_eps_growth_data_1y.index:
            # For Sales plot, if asset doesn't have Sales data, use 0 or another default
            sales_value = euro_sales_growth_data_1y.get(asset, 0)  # Use 0 if asset not in Sales data
            fig_euro_1y_2.add_trace(
                go.Scatter(
                    x=[euro_eps_growth_data_1y[asset]],
                    y=[sales_value],
                    mode="markers+text",
                    text=[asset],
                    textposition="top center",
                    name=asset,
                    marker=dict(size=10),
                )
            )
    fig_euro_1y_2.add_trace(
        go.Scatter(
            x=[-0.5, 0.5],
            y=[-0.5, 0.5],
            mode='lines',
            line=dict(color="gray", width=2, dash="dash"),
            showlegend=False
        )
    )
    # Add x=0 reference line
    fig_euro_1y_2.add_trace(
        go.Scatter(
            x=[0, 0],
            y=[-0.5, 0.5],
            mode="lines",
            line=dict(color="lightgray", width=1, dash="dot"),
            name="x = 0%",
            showlegend=False
        )
    )
    # Add y=0 reference line
    fig_euro_1y_2.add_trace(
        go.Scatter(
            x=[-0.5, 0.5],
            y=[0, 0],
            mode="lines",
            line=dict(color="lightgray", width=1, dash="dot"),
            name="y = 0%",
            showlegend=False
        )
    )
    fig_euro_1y_2.update_layout(
        title="European Sectors - Sales & EPS",
        yaxis_title="Forward Sales 1y chg",
        xaxis_title="Forward EPS 1y chg",
        yaxis=dict(tickformat=".2%", range=[-0.5, 0.5]),
        xaxis=dict(tickformat=".2%", range=[-0.5, 0.5]),
        hovermode="closest",
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig_euro_1y_2, use_container_width=True)


render_fundamental_section_enhanced(
    "European Sectors Fundamental(3M)",
    eps_3m=euro_eps_fwd_3m_sec,
    fcf_3m=euro_fcf_fwd_3m_sec,
    sales_3m=euro_sales_fwd_3m_sec,
    eps_1y=euro_eps_fwd_1y_sec,
    fcf_1y=euro_fcf_fwd_1y_sec,
    sales_1y=euro_sales_fwd_1y_sec,
    universe=Euro_sector
)

# ================== European Sector PE Multiple Band ==================
st.title("European Sectors Fwd P/E Multiple")

# Filter PE data to include only sectors that are in the filtered list to avoid errors
filtered_pe_data = pe_euro_bd_sec[Euro_sector]

# Create PE band visualization for European sectors
fig_pe_euro = plot_pe_bands_plotly(filtered_pe_data)
st.plotly_chart(fig_pe_euro, use_container_width=True, key="plot_pe_euro_sectors")

# ================== European Sector EPS and PE Growth Visualization ==================
st.title("European Sectors EPS and PE Growth Visualization")

# Create a copy of the PE data with the same columns as EPS data
euro_eps_columns = euro_eps_res_bd_sec.columns
euro_pe_filtered = pd.DataFrame(index=pe_euro_bd_sec.index)

# Copy data from pe_euro_bd_sec where columns exist
for col in euro_eps_columns:
    if col in pe_euro_bd_sec.columns:
        euro_pe_filtered[col] = pe_euro_bd_sec[col]
    else:
        # For missing columns (like 'Banks'), add a column of reasonable default values
        # You could use the mean of existing values or some other reasonable approach
        euro_pe_filtered[col] = pe_euro_bd_sec.mean(axis=1)

# Now use these adjusted dataframes for visualization
common_sectors = list(euro_eps_columns)

# Create EPS and PE growth visualization for European sectors
if common_sectors:
    try:
        fig_eps_pe_euro = plot_eps_pe_growth(
            euro_eps_res_bd_sec[common_sectors],
            euro_pe_filtered[common_sectors],
            common_sectors
        )
        st.plotly_chart(fig_eps_pe_euro, use_container_width=True, key="plot_eps_pe_euro_sectors")
    except Exception as e:
        st.error(f"Error creating EPS/PE growth chart: {e}")
        # Provide a more detailed error message to help diagnose the issue
        st.code(f"DataFrame shapes: EPS {euro_eps_res_bd_sec.shape}, PE {euro_pe_filtered.shape}")
        st.code(f"Common sectors: {common_sectors}")
else:
    st.warning("No common sectors found between EPS and PE datasets.")

#==============================================================================================

# 필요한 임포트문 추가
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots  # 이 임포트문이 필요합니다
import numpy as np

# ================== Global Equities Fundamental Analysis ==================
st.title("Global Equities Fundamental Analysis - 3M")

# glb_eq 리스트
glb_eq = ['MSFT US Equity', 'AAPL US Equity', 'NVDA US Equity', 'AMZN US Equity', 'META US Equity',
          'TSLA US Equity', 'GOOGL US Equity', 'ORCL US Equity', 'PLTR US Equity', 'CRM US Equity', 'NFLX US Equity',
          'SAP US Equity', 'AVGO US Equity',
          'JPM US Equity', 'XOM US Equity', 'UNH US Equity', 'MA US Equity', 'JNJ US Equity',
          'KO US Equity', 'PG US Equity', 'GE US Equity', 'NEE US Equity', 'MC FP Equity', 'SU FP Equity',
          'OR FP Equity', 'SIE GR Equity', 'TTE FP Equity', 'SAN FP Equity',
          'ALV GR Equity', 'BABA US Equity', 'TCEHY US Equity', 'BIDU US Equity']

# 기본 표시할 티커 선택 (처음 10개)
default_glb_eq = glb_eq[:10]
selected_glb_eq = st.multiselect('Select Global Equities', glb_eq, default=default_glb_eq,
                                 key="multiselect_global_eq_3m")

# 최근 3년 날짜만 필터링
current_date = pd.Timestamp.now()
three_years_ago = current_date - pd.Timedelta(days=365 * 3)
recent_dates = [date for date in glb_eq_eps_3m.index if date >= three_years_ago]

# 최신 날짜부터 내림차순으로 정렬
sorted_dates = sorted(recent_dates, reverse=True)
date_options = [date.strftime('%Y-%m-%d') for date in sorted_dates]

# 가장 최신 날짜를 기본값으로 선택
default_date = date_options[0] if date_options else None

# 날짜 선택 - 최신 날짜가 기본값으로 설정
glb_fun_date_3m = st.selectbox('Select Date', date_options, index=0, key="selectbox_global_eq_3m")

# 선택한 날짜의 데이터 추출
if selected_glb_eq:
    glb_eps_growth_data_3m = glb_eq_eps_3m.loc[glb_fun_date_3m]
    glb_sales_growth_data_3m = glb_eq_sales_3m.loc[glb_fun_date_3m]

    # 선택한 티커에 대한 데이터만 필터링
    selected_tickers = [ticker for ticker in selected_glb_eq if ticker in glb_eps_growth_data_3m.index]

    if selected_tickers:
        # 산점도 그래프 생성
        fig_glb_3m = go.Figure()

        # 각 티커를 산점도에 추가
        for ticker in selected_tickers:
            if ticker in glb_eps_growth_data_3m.index and ticker in glb_sales_growth_data_3m.index:
                fig_glb_3m.add_trace(
                    go.Scatter(
                        x=[glb_eps_growth_data_3m[ticker]],
                        y=[glb_sales_growth_data_3m[ticker]],
                        mode="markers+text",
                        text=[ticker.split()[0]],  # 티커명에서 'Equity' 부분 제거
                        textposition="top center",
                        name=ticker.split()[0],
                        marker=dict(size=10),
                    )
                )

        # y=x 참조선 추가
        fig_glb_3m.add_trace(
            go.Scatter(
                x=[-0.25, 0.25],
                y=[-0.25, 0.25],
                mode="lines",
                line=dict(color="gray", width=2, dash="dash"),
                name="y = x",
                showlegend=False
            )
        )

        # x축 0% 참조선 추가
        fig_glb_3m.add_trace(
            go.Scatter(
                x=[0, 0],
                y=[-0.2, 0.2],
                mode="lines",
                line=dict(color="lightgray", width=1, dash="dot"),
                name="x = 0%",
                showlegend=False
            )
        )

        # y축 0% 참조선 추가
        fig_glb_3m.add_trace(
            go.Scatter(
                x=[-0.2, 0.2],
                y=[0, 0],
                mode="lines",
                line=dict(color="lightgray", width=1, dash="dot"),
                name="y = 0%",
                showlegend=False
            )
        )

        # 레이아웃 설정
        fig_glb_3m.update_layout(
            title="Global Equities - EPS & Sales Growth (3M)",
            xaxis_title="Forward EPS 3M Chg",
            yaxis_title="Forward Sales 3M Chg",
            xaxis=dict(tickformat=".2%", range=[-0.25, 0.25]),
            yaxis=dict(tickformat=".2%", range=[-0.25, 0.25]),
            hovermode="closest",
            template="plotly_white",
            height=600
        )

        # 고유한 key 추가
        st.plotly_chart(fig_glb_3m, use_container_width=True, key="plotly_global_3m_scatter")
    else:
        st.warning("No data available for selected tickers.")
else:
    st.info("Please select at least one global equity ticker.")

# ================ Global Equities Fundamental Analysis 1Y ================
st.title("Global Equities Fundamental Analysis - 1Y")

# 티커 선택 위젯 (3M과 공유하지 않기 위해 새로운 키 사용)
selected_glb_eq_1y = st.multiselect('Select Global Equities', glb_eq, default=default_glb_eq,
                                    key="multiselect_global_eq_1y")

# 최근 3년 날짜만 필터링 (1Y 데이터용)
recent_dates_1y = [date for date in glb_eq_eps_1y.index if date >= three_years_ago]

# 최신 날짜부터 내림차순으로 정렬
sorted_dates_1y = sorted(recent_dates_1y, reverse=True)
date_options_1y = [date.strftime('%Y-%m-%d') for date in sorted_dates_1y]

# 가장 최신 날짜를 기본값으로 선택
default_date_1y = date_options_1y[0] if date_options_1y else None

# 날짜 선택 - 최신 날짜가 기본값으로 설정
glb_fun_date_1y = st.selectbox('Select Date', date_options_1y, index=0, key="selectbox_global_eq_1y")

# 선택한 날짜의 데이터 추출
if selected_glb_eq_1y:
    glb_eps_growth_data_1y = glb_eq_eps_1y.loc[glb_fun_date_1y]
    glb_sales_growth_data_1y = glb_eq_sales_1y.loc[glb_fun_date_1y]

    # 선택한 티커에 대한 데이터만 필터링
    selected_tickers_1y = [ticker for ticker in selected_glb_eq_1y if ticker in glb_eps_growth_data_1y.index]

    if selected_tickers_1y:
        # 산점도 그래프 생성
        fig_glb_1y = go.Figure()

        # 각 티커를 산점도에 추가
        for ticker in selected_tickers_1y:
            if ticker in glb_eps_growth_data_1y.index and ticker in glb_sales_growth_data_1y.index:
                fig_glb_1y.add_trace(
                    go.Scatter(
                        x=[glb_eps_growth_data_1y[ticker]],
                        y=[glb_sales_growth_data_1y[ticker]],
                        mode="markers+text",
                        text=[ticker.split()[0]],  # 티커명에서 'Equity' 부분 제거
                        textposition="top center",
                        name=ticker.split()[0],
                        marker=dict(size=10),
                    )
                )

        # y=x 참조선 추가
        fig_glb_1y.add_trace(
            go.Scatter(
                x=[-0.5, 0.5],
                y=[-0.5, 0.5],
                mode="lines",
                line=dict(color="gray", width=2, dash="dash"),
                name="y = x",
                showlegend=False
            )
        )

        # x축 0% 참조선 추가
        fig_glb_1y.add_trace(
            go.Scatter(
                x=[0, 0],
                y=[-0.4, 0.4],
                mode="lines",
                line=dict(color="lightgray", width=1, dash="dot"),
                name="x = 0%",
                showlegend=False
            )
        )

        # y축 0% 참조선 추가
        fig_glb_1y.add_trace(
            go.Scatter(
                x=[-0.4, 0.4],
                y=[0, 0],
                mode="lines",
                line=dict(color="lightgray", width=1, dash="dot"),
                name="y = 0%",
                showlegend=False
            )
        )

        # 레이아웃 설정
        fig_glb_1y.update_layout(
            title="Global Equities - EPS & Sales Growth (1Y)",
            xaxis_title="Forward EPS 1Y Chg",
            yaxis_title="Forward Sales 1Y Chg",
            xaxis=dict(tickformat=".2%", range=[-0.5, 0.5]),
            yaxis=dict(tickformat=".2%", range=[-0.5, 0.5]),
            hovermode="closest",
            template="plotly_white",
            height=600
        )

        # 고유한 key 추가
        st.plotly_chart(fig_glb_1y, use_container_width=True, key="plotly_global_1y_scatter")
    else:
        st.warning("No data available for selected tickers.")
else:
    st.info("Please select at least one global equity ticker.")

render_fundamental_section_enhanced(
    "Global Equities Fundamental(3M)",
    eps_3m=glb_eq_eps_3m,
    fcf_3m=pd.DataFrame(0, index=glb_eq_eps_3m.index, columns=glb_eq_eps_3m.columns),
    sales_3m=glb_eq_sales_3m,
    eps_1y=glb_eq_eps_1y,
    fcf_1y=pd.DataFrame(0, index=glb_eq_eps_1y.index, columns=glb_eq_eps_1y.columns),
    sales_1y=glb_eq_sales_1y,
    universe=glb_eq,
    use_sales_instead_of_fcf=True  # This flag makes the function use sales data instead of fcf
)


#===========================================================================================================


# 섹션 4: 최근 6개월 월말 비중
st.subheader('Actual Portfolio Weights at Month-End for the Last 6 Months')

# 날짜를 내림차순으로 정렬 (최신 날짜가 먼저 오도록)
sorted_weight_dates = sorted(recent_6m_weights.index.strftime('%Y-%m-%d'), reverse=True)

# 가장 최신 날짜를 기본값으로 선택
selected_date = st.selectbox('Select Date', sorted_weight_dates, key="selectbox_weights")
selected_weights = recent_6m_weights.loc[pd.to_datetime(selected_date)]

fig3 = px.bar(
    x=selected_weights.index,
    y=selected_weights.values,
    labels={'x': 'Ticker', 'y': 'Weight'},
    title=f'Actual Portfolio Weights on {selected_date}',
    template='plotly_white'
)
fig3.update_layout(
    xaxis_tickangle=-45,
    height=600
)
st.plotly_chart(fig3, use_container_width=True)


#===================Momentum Overlay Weights=================


import plotly.graph_objects as go

def stacked_overlay_chart(
        tickers,                       # x축
        base_w,                        # 1) Base 가중치 (np.array / pd.Series)
        overlay_dict,                  # 2) {'레전드': overlay_array, ...}
        title, colors,                 # 차트 제목, 색상 dict
        height=600):
    """
    base_w            : 1차원 배열
    overlay_dict      : {label1: arr1, label2: arr2, ...}
                        ➜ trace 순서대로 누적(base) 계산
    colors            : {label: color_code}
    """
    fig = go.Figure()

    # ─── ① Base ───
    fig.add_bar(
        x=tickers,
        y=base_w,
        name='Base Weight',
        marker_color=colors['Base Weight']
    )

    # ─── ② Overlay들 ───
    cum_base = base_w.copy()          # 누적 시작점
    for lbl, arr in overlay_dict.items():
        fig.add_bar(
            x=tickers,
            y=arr,
            base=cum_base,            # ← 핵심
            name=lbl,
            marker_color=colors[lbl]
        )
        cum_base = cum_base + arr     # 다음 Overlay의 시작점

    fig.update_layout(
        barmode='overlay',            # base=… 로 이미 쌓음
        xaxis_tickangle=-45,
        template='plotly_white',
        title=title,
        height=height
    )
    return fig


st.subheader('Momentum Overlay Portfolio Weights at Month-End for the Last 6 Months')


# Select date for visualization
# 날짜를 내림차순으로 정렬 (최신 날짜가 먼저 오도록)
sorted_overlay_dates = sorted(overlay_recent_3y_weights.index.strftime('%Y-%m-%d'), reverse=True)

# 가장 최신 날짜를 기본값으로 선택
selected_date_overlay = st.selectbox('Select Date for Overlay Portfolio', sorted_overlay_dates)
selected_weights_overlay = overlay_recent_3y_weights.loc[pd.to_datetime(selected_date_overlay)]
selected_overlay_weights = overlay_recent_partial_weights.loc[pd.to_datetime(selected_date_overlay)]

# Calculate base weights by subtracting overlay weights from total weights
base_weights_overlay = selected_weights_overlay - selected_overlay_weights

# Create a Dataframe for plotting
weights_df_overlay = pd.DataFrame({
    'Ticker'                    : st_list,
    'Base Weight'               : base_weights_overlay.values,
    'Momentum Overlay Weight(5%)': selected_overlay_weights.values
})

# wide → long
weights_df_overlay_melted = weights_df_overlay.melt(
    id_vars='Ticker',
    var_name='Weight Type',
    value_name='Weight'
)
tickers  = st_list
base_w   = base_weights_overlay.values
mom_w    = selected_overlay_weights.values

fig_overlay = stacked_overlay_chart(
    tickers=tickers,
    base_w=base_w,
    overlay_dict={'Momentum Overlay Weight(5%)': mom_w},
    title=f'Overlay Portfolio Weights on {selected_date_overlay}',
    colors={
        'Base Weight'                 : '#636EFA',  # 파랑
        'Momentum Overlay Weight(5%)' : '#EF553B'   # 주황
    }
)
st.plotly_chart(fig_overlay, use_container_width=True)
#===================EPS Overlay Weights=================

st.subheader('EPS Overlay Portfolio Weights at Month-End for the Last 6 Months')

# 날짜를 내림차순으로 정렬 (최신 날짜가 먼저 오도록)
sorted_eps_overlay_dates = sorted(eps_overlay_recent_3y_weights.index.strftime('%Y-%m-%d'), reverse=True)

# 가장 최신 날짜를 기본값으로 선택
selected_date_eps_overlay = st.selectbox('Select Date for EPS Overlay Portfolio', sorted_eps_overlay_dates)
selected_weights_eps_overlay = eps_overlay_recent_3y_weights.loc[pd.to_datetime(selected_date_eps_overlay)]
selected_eps_overlay_weights = eps_overlay_recent_partial_weights.loc[pd.to_datetime(selected_date_eps_overlay)]

# Calculate base weights by substracting overlay weights from total weights
base_weights_eps_overlay = selected_weights_eps_overlay - selected_eps_overlay_weights

# Create a dataframe for plotting
weights_df_eps_overlay = pd.DataFrame({
    'Ticker'              : st_list,
    'Base Weight'         : base_weights_eps_overlay.values,
    'EPS Overlay Weight(5%)': selected_eps_overlay_weights.values
})
eps_melted = weights_df_eps_overlay.melt(
    id_vars='Ticker',
    var_name='Weight Type',
    value_name='Weight'
)

tickers = st_list
base_w  = base_weights_eps_overlay.values
eps_w   = selected_eps_overlay_weights.values

fig_eps = stacked_overlay_chart(
    tickers=tickers,
    base_w=base_w,
    overlay_dict={'EPS Overlay Weight(5%)': eps_w},
    title=f'EPS Overlay Portfolio Weights on {selected_date_eps_overlay}',
    colors={
        'Base Weight'           : '#636EFA',
        'EPS Overlay Weight(5%)': '#00CC96'  # 초록
    }
)
st.plotly_chart(fig_eps, use_container_width=True)

#===================================Combined Portfolio Weight=================================

st.subheader('Combined Overlay Portfolio Weights at Month-End for the Last 6 Months')

# 날짜를 내림차순으로 정렬 (최신 날짜가 먼저 오도록)
sorted_combined_overlay_dates = sorted(combined_overlay_recent_3y_weights.index.strftime('%Y-%m-%d'), reverse=True)

# 가장 최신 날짜를 기본값으로 선택
selected_date_combined_overlay = st.selectbox('Select Date for Combined overlay Portfolio', sorted_combined_overlay_dates)
selected_weights_combined_overlay = combined_overlay_recent_3y_weights.loc[pd.to_datetime(selected_date_combined_overlay)]
selected_overlay_weights_combined = combined_overlay_recent_partial_weights.loc[pd.to_datetime(selected_date_combined_overlay)]

# Retrieve the overlay weights
selected_overlay_weights_eps = combined_overlay_recent_eps_weights.loc[pd.to_datetime(selected_date_combined_overlay)]
selected_overlay_weights_momentum = combined_overlay_recent_momentum_weights.loc[pd.to_datetime(selected_date_combined_overlay)]


# Calculate base weights by subtracting overlay weights from total weights
base_weights_combined_overlay = selected_weights_combined_overlay - selected_overlay_weights_combined

# Create a Dataframe for plotting
weights_df_combined_overlay = pd.DataFrame({
    'Ticker'                 : base_weights_combined_overlay.index,
    'Base Weight'            : base_weights_combined_overlay.values,
    'EPS Overlay Weight'     : selected_overlay_weights_eps.values,
    'Momentum Overlay Weight': selected_overlay_weights_momentum.values
})
combined_melted = weights_df_combined_overlay.melt(
    id_vars='Ticker',
    var_name='Weight Type',
    value_name='Weight'
)

tickers      = base_weights_combined_overlay.index
base_w       = base_weights_combined_overlay.values
eps_w        = selected_overlay_weights_eps.values
mom_w        = selected_overlay_weights_momentum.values

fig_combined = stacked_overlay_chart(
    tickers=tickers,
    base_w=base_w,
    overlay_dict={
        'EPS Overlay Weight'     : eps_w,   # ← 먼저 쌓임
        'Momentum Overlay Weight': mom_w    # ← 그 위에 추가
    },
    title=f'Combined Overlay Portfolio Weights on {selected_date_combined_overlay}',
    colors={
        'Base Weight'            : '#636EFA',
        'EPS Overlay Weight'     : '#00CC96',
        'Momentum Overlay Weight': '#EF553B'
    }
)
st.plotly_chart(fig_combined, use_container_width=True)
#===================================Growth Portfolio Weight=================================

st.subheader('Growth Portfolio Weights at Month-End for the Last 6 Months')

# 날짜를 내림차순으로 정렬 (최신 날짜가 먼저 오도록)
sorted_growth_dates = sorted(growth_3y_weights.index.strftime('%Y-%m-%d'), reverse=True)

# 가장 최신 날짜를 기본값으로 선택
selected_date_growth = st.selectbox('Select Date for Growth Portfolio', sorted_growth_dates)
selected_weights_growth = growth_3y_weights.loc[pd.to_datetime(selected_date_growth)]


fig_growth = px.bar(
    x=selected_weights_growth.index,
    y=selected_weights_growth.values,
    labels={'x': 'Ticker', 'y': 'Weight'},
    title=f'Actual Portfolio Weights on {selected_date}',
    template='plotly_white'
)
fig_growth.update_layout(
    xaxis_tickangle=-45,
    height=600
)
st.plotly_chart(fig_growth, use_container_width=True)

#===================================Momentum Portfolio Weight=================================

st.subheader('Momentum Portfolio Weights at Month-End for the Last 6 Months')

# 날짜를 내림차순으로 정렬 (최신 날짜가 먼저 오도록)
sorted_momentum_dates = sorted(momentum_3y_weights.index.strftime('%Y-%m-%d'), reverse=True)

# 가장 최신 날짜를 기본값으로 선택
selected_date_momentum = st.selectbox('Select Date for Momentum Portfolio', sorted_momentum_dates)
selected_weights_momentum = momentum_3y_weights.loc[pd.to_datetime(selected_date_momentum)]


fig_momentum = px.bar(
    x=selected_weights_momentum.index,
    y=selected_weights_momentum.values,
    labels={'x': 'Ticker', 'y': 'Weight'},
    title=f'Actual Portfolio Weights on {selected_date}',
    template='plotly_white'
)
fig_momentum.update_layout(
    xaxis_tickangle=-45,
    height=600
)
st.plotly_chart(fig_momentum, use_container_width=True)




# 섹션 6: 분기별 그룹에 포함된 주식들
st.subheader('Stocks Included in Each Group by Quarter')

# 분기별 그룹 키를 내림차순으로 정렬 (최신 분기가 먼저 오도록)
sorted_quarters = sorted(quarterly_group_stocks.keys(), reverse=True)

# 가장 최신 분기를 기본값으로 선택
selected_quarter_group = st.selectbox('Select Quarter (Stock Groups)', sorted_quarters)
group_data = quarterly_group_stocks[selected_quarter_group]

# Prepare DataFrame for Plotly
group_df = pd.DataFrame(columns=['Group', 'Ticker'])

# 동적으로 그룹을 접근
for group in ['Top', 'Middle', 'Bottom']:
    try:
        stocks = group_data[group]
        group_df = pd.concat([
            group_df,
            pd.DataFrame({'Group': group, 'Ticker': stocks})
        ], ignore_index=True)
    except KeyError:
        st.warning(f"'{group}' 그룹이 존재하지 않습니다.")
        continue

# Plotting
fig5 = px.histogram(
    group_df,
    x='Group',
    color='Ticker',
    title=f'Stocks in Each Group for {selected_quarter_group}',
    labels={'Group': 'Group', 'count': 'Number of Stocks'},
    template='plotly_white'
)
fig5.update_layout(
    bargap=0.2,
    height=600
)
st.plotly_chart(fig5, use_container_width=True)


# 섹션 : 주식 Rank 시간대 변화

score_index = pd.to_datetime(scores.index)
score_ranks = scores.rank(axis=1, ascending=False)

# 섹션: 기간선택

st.subheader('Select Time Period')
min_date = scores.index.min()
max_date = scores.index.max()

start_date = st.date_input('Start Date', value=min_date, min_value=min_date, max_value=max_date)
end_date = st.date_input('End Date', value = max_date, min_value=min_date, max_value=max_date)


# 섹션: 주식 선택
st.subheader('Select Stocks')
selected_stocks = st.multiselect('Select Stock(s)', st_list, default=st_list[0])



# 선택한 기간 동안의 데이터 필터링
filtered_ranks = score_ranks.loc[start_date : end_date, selected_stocks]

# 데이터 정렬 (날짜 순)
filtered_ranks = filtered_ranks.sort_index()

# 데이터프레임 형태로 변환 (시각화를 위해)
rank_df = filtered_ranks.reset_index().melt(id_vars='date', var_name='Stock', value_name='Rank')
rank_df.rename(columns={'date': 'Date'}, inplace=True)

# Plotly를 사용한 시각화
fig = px.line(rank_df, x='Date', y='Rank', color='Stock', markers=True,
              title='Rank Changes Over Time',
              labels={'Rank': 'Rank', 'Date': 'Date'})

fig.update_layout(yaxis=dict(autorange='reversed'))  # 순위가 1부터 시작하므로 역순으로 표시

st.plotly_chart(fig, use_container_width=True)

# 섹션 8: 리밸런싱 날짜별 요소별 스코어
st.subheader('Factor Scores by Rebalance Date')

# 리밸런싱 날짜 로드 (분기별 리밸런싱 날짜 목록)
#available_quarters = sorted(quarterly_rebalance_dates.keys())
#selected_quarter = st.selectbox('Select Quarter (e.g., "2023-Q1")', available_quarters)

available_months = sorted(monthly_rebalance_dates.keys())
# 월별 리밸런싱 날짜 키를 내림차순으로 정렬 (최신 월이 먼저 오도록)
sorted_months = sorted(monthly_rebalance_dates.keys(), reverse=True)

# 가장 최신 월을 기본값으로 선택
selected_months = st.selectbox('Select Months (e.g., "2023-01")', sorted_months)
# 선택된 분기의 리밸런싱 날짜 가져오기
selected_rebalance_date = monthly_rebalance_dates[selected_months]

# 선택된 리밸런싱 날짜로 요소별 스코어 표시
if pd.Timestamp(selected_rebalance_date) not in factor_scores['eps_growth'].index:
    st.error(f"Selected date {selected_rebalance_date.strftime('%Y-%m-%d')} is not present in factor_scores.")
else:
    # 선택한 날짜 출력 (디버깅용)
    st.write("Selected Date:", selected_rebalance_date)

    # 선택한 날짜의 각 요소별 스코어 데이터프레임 생성
    scores_df = pd.DataFrame({
        'Ticker': st_list,
        'EPS Growth Rate': factor_scores['eps_growth'].loc[selected_rebalance_date].values,
        'Sales Growth Rate': factor_scores['sales_growth'].loc[selected_rebalance_date].values,
        'Fcf Growth Rate': factor_scores['fcf_growth'].loc[selected_rebalance_date].values,
    #    'Revision Sales': factor_scores['revision_sales'].loc[selected_rebalance_date].values,
        '12m Momentum': factor_scores['mom_12m'].loc[selected_rebalance_date].values,
        '3m Momentum': factor_scores['mom_3m'].loc[selected_rebalance_date].values,
        'Manual Score (p_s)': factor_scores['p_s'].loc[selected_rebalance_date],
        'Total Score': scores.loc[selected_rebalance_date],
    })

    scores_df = scores_df.set_index('Ticker')

    st.dataframe(scores_df.style.format("{:.2f}"))


# 섹션 9 전체 포트폴리오 연도별 평균 IC

st.title('Annual Average IC Analysis')
annual_ic_total.index = annual_ic_total.index.astype(int)
annual_ic_total.columns = ['IC']
annual_ic_factors_df.index = annual_ic_factors_df.index.astype(int)

st.subheader('Annual Average IC - Total Score')
fig_total = px.line(annual_ic_total.reset_index(), x = 'Year', y = 'IC', title = 'Annual Average IC - Total Score')
fig_total.update_layout(xaxis_title='Year')
fig_total.add_hline(y = 0, line_dash = "dash", line_color = "gray")
st.plotly_chart(fig_total, use_container_width=True)


# 섹션 10 전체 포트폴리오 팩터별 연도별 평균 IC
st.subheader('Annual Average IC by Factor')
annual_ic_factors_df_reset = annual_ic_factors_df.reset_index().melt(id_vars='Year', var_name='Factor',value_name='IC')
fig_factors = px.line(annual_ic_factors_df_reset, x='Year', y='IC', color='Factor',
                      title='Annual Average IC by Factor')
fig_factors.update_layout(xaxis_title='Year')
fig_factors.add_hline(y=0, line_dash = "dash", line_color="gray")
st.plotly_chart(fig_factors, use_container_width=True)

# 섹션 11 수익률 비교 표
st.subheader('Retrun comparison')
st.table(comparison_df)


# 섹션 13 Factor Decay

st.title('Factor Decay Analysis')

# 전체 팩터 디케이 그래프
st.subheader('Factor Decay - Total Score')
fig_total = px.line(decay_total.reset_index(), x = 'Lag', y = 'Mean_IC', title='Factor Decay - Total Score')
st.plotly_chart(fig_total, use_container_width=True)

# 개별 팩터 디케이 그래프
st.subheader('Factor Decay by Factor')
decay_factors_melted = decay_factors_df.reset_index().melt(id_vars='Lag', var_name='Factor', value_name='Mean_IC')
fig_factors = px.line(decay_factors_melted, x='Lag', y='Mean_IC', color='Factor', title='Factor Decay by Factor')
st.plotly_chart(fig_factors, use_container_width=True)



# 섹션 : 주식 Rank 시간대 변화

monthly_factor_weights_index = pd.to_datetime(monthly_factor_weights.index)
monthly_factor_weights_ranks = monthly_factor_weights.rank(axis=1, ascending=False)

# 섹션: 기간선택

st.subheader('Select Time Period')
min_date = monthly_factor_weights.index.min()
max_date = monthly_factor_weights.index.max()

start_date = st.date_input('Start Date', value=min_date, min_value=min_date, max_value=max_date)
end_date = st.date_input('End Date', value = max_date, min_value=min_date, max_value=max_date)


# 섹션: 주식 선택
st.subheader('Select Stocks')
selected_stocks = st.multiselect('Select Factors(s)', monthly_factor_weights.columns, default=monthly_factor_weights.columns[0])



# 선택한 기간 동안의 데이터 필터링
filtered_ranks = monthly_factor_weights_ranks.loc[start_date : end_date, monthly_factor_weights.columns]

# 데이터 정렬 (날짜 순)
filtered_ranks = filtered_ranks.sort_index()

# 데이터프레임 형태로 변환 (시각화를 위해)
rank_df = filtered_ranks.reset_index().melt(id_vars='date', var_name='Factors', value_name='Rank')
rank_df.rename(columns={'date': 'Date'}, inplace=True)

# Plotly를 사용한 시각화
fig = px.line(rank_df, x='Date', y='Rank', color='Factors', markers=True,
              title='Rank Changes Over Time',
              labels={'Rank': 'Rank', 'Date': 'Date'})

fig.update_layout(yaxis=dict(autorange='reversed'))  # 순위가 1부터 시작하므로 역순으로 표시

st.plotly_chart(fig, use_container_width=True)


st.subheader('성과지표')
results_df['Annualized Return'] = results_df['Annualized Return'].apply(lambda x:f"{x * 100:.2f}")
results_df['Annualized Volatility'] = results_df['Annualized Volatility'].apply(lambda x:f"{x * 100:.2f}")
#results_df['Annualized IR'] = results_df['Annualized IR'].apply(lambda x:f"{x:.4f}" if pd.notnull(x) else '-')
#results_df['Annualized IC'] = results_df['Annualized IC'].apply(lambda x:f"{x:.4f}" if pd.notnull(x) else '-')

st.dataframe(results_df)