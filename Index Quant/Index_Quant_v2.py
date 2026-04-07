import pandas as pd
import numpy as np
import os
import cvxpy as cp
from tqdm import tqdm
import pickle

import pandas as pd

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from scipy.stats import norm
from datetime import timedelta, date
import scipy.stats as stats
import pandas as pd
import numpy as np
import matplotlib.cm
import datetime
from jupyter_dash import JupyterDash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from scipy.optimize import minimize

# import dash_core_components as dcc
# import dash_html_components as html
from dash import html
from dash import dcc
# For PCA
from statsmodels.multivariate import pca

# For regressions
import statsmodels.api as sm

# For plotting and formatting the plots
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtkr
import matplotlib.dates as mdts
import matplotlib.text as txt
import adjustText

from scipy.stats import zscore
from numpy import log as ln
from tqdm import tqdm
from sklearn.covariance import LedoitWolf
import scipy.optimize as sco
import plotly.express as px
import cvxpy as cp
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import re
import os
import cvxpy as cp
from tqdm import tqdm
import pickle
import scipy.stats as stats

def zscore(data):
    mean = np.mean(data)
    std = np.std(data)
    z_score = [(y - mean) / std for y in data]
    return z_score


def scale_zscore(z):
    return np.clip(z, -5, 5)


def cal_mtum2(returns, window1, window2):
    pr_mtum_all = pd.DataFrame()
    # Index_beta = pd.DataFrame()

    # assets = len(returns.columns)
    number = len(returns.index) - 252

    for j in range(number):
        retunrs_xts = returns.set_index('date').iloc[j:252 + 1 + j, ]
        pr_mtum = retunrs_xts.pct_change(periods=window1).iloc[-1:, ]
        pr_mtum_1m = retunrs_xts.pct_change(periods=window2).iloc[-1:, ]
        pr_mtum_data = pr_mtum - pr_mtum_1m
        pr_mtum_all = pd.concat([pr_mtum_data, pr_mtum_all], axis=0)

    pr_mtum_score = pr_mtum_all.reset_index().sort_values(by='date').set_index('date')
    # beta_data = model_beta_all.iloc[:,(model_beta_all.columns != 'const')]
    return pr_mtum_score


def eps_growth_nor(eps, window1, window2):
    eps_gr = eps.pct_change(periods=window1).fillna(0)
    eps_list = eps.columns
    eps_gr_tbl = eps_gr.reset_index().melt(id_vars='date', var_name='Index', value_name='growth')
    Q1 = eps_gr_tbl['growth'].quantile(0.10)
    Q3 = eps_gr_tbl['growth'].quantile(0.90)
    IQR = Q3 - Q1
    lower_bound = Q1 - 2.0 * IQR
    upper_bound = Q3 + 2.0 * IQR
    eps_gr_tbl['cap_growth'] = np.where(eps_gr_tbl['growth'] > upper_bound, upper_bound,
                                        np.where(eps_gr_tbl['growth'] < lower_bound, lower_bound, eps_gr_tbl['growth']))
    eps_gr = eps_gr_tbl[['date', 'Index', 'cap_growth']].pivot(index='date', columns='Index', values='cap_growth')[
        eps_list]
    eps_gr_mean = eps_gr.rolling(window=window2).mean()
    eps_gr_std = eps_gr.rolling(window=window2).std()
    eps_gr_tbl = (eps_gr - eps_gr_mean) / eps_gr_std
    eps_gr_tbl = eps_gr_tbl.apply(scale_zscore)

    return eps_gr_tbl


def revision_growth(eps, window1, window2):
    # eps_gr = eps.pct_change(periods=window1).fillna(0)
    eps_list = eps.columns
    eps_gr_tbl = eps.reset_index().melt(id_vars='date', var_name='Index', value_name='growth')
    Q1 = eps_gr_tbl['growth'].quantile(0.10)
    Q3 = eps_gr_tbl['growth'].quantile(0.90)
    IQR = Q3 - Q1
    lower_bound = Q1 - 2.0 * IQR
    upper_bound = Q3 + 2.0 * IQR
    eps_gr_tbl['cap_growth'] = np.where(eps_gr_tbl['growth'] > upper_bound, upper_bound,
                                        np.where(eps_gr_tbl['growth'] < lower_bound, lower_bound, eps_gr_tbl['growth']))
    eps_gr = eps_gr_tbl[['date', 'Index', 'cap_growth']].pivot(index='date', columns='Index', values='cap_growth')[
        eps_list]
    eps_gr_mean = eps_gr.rolling(window=window2).mean()
    eps_gr_std = eps_gr.rolling(window=window2).std()
    eps_gr_tbl = (eps_gr - eps_gr_mean) / eps_gr_std
    eps_gr_tbl = eps_gr_tbl.apply(scale_zscore)

    return eps_gr_tbl


def mtm_growth(eps, window2):
    eps_gr = eps.fillna(0)
    eps_gr_mean = eps_gr.rolling(window=window2).mean()
    eps_gr_std = eps_gr.rolling(window=window2).std()
    eps_gr_tbl = (eps_gr - eps_gr_mean) / eps_gr_std
    eps_gr_tbl = eps_gr_tbl.apply(scale_zscore)

    return eps_gr_tbl


def vol_normal(eps, window1, window2):
    eps_gr = eps.fillna(0)
    eps_gr = eps_gr.rolling(window=window1).std()
    eps_gr_mean = eps_gr.rolling(window=window2).mean()
    eps_gr_std = eps_gr.rolling(window=window2).std()
    eps_gr_tbl = (eps_gr - eps_gr_mean) / eps_gr_std
    eps_gr_tbl = eps_gr_tbl.apply(scale_zscore)

    return eps_gr_tbl


def eps_growth_mtm(eps):
    eps_1y = eps.diff(periods=252).iloc[-1:, :].reset_index().melt(id_vars='date', var_name='Index',
                                                                   value_name='1y').iloc[:, 1:]
    eps_6m = eps.diff(periods=21 * 6).iloc[-1:, :].reset_index().melt(id_vars='date', var_name='Index',
                                                                      value_name='6m').iloc[:, 1:]
    eps_3m = eps.diff(periods=62).iloc[-1:, :].reset_index().melt(id_vars='date', var_name='Index',
                                                                  value_name='3m').iloc[:, 1:]
    eps_1m = eps.diff(periods=21).iloc[-1:, :].reset_index().melt(id_vars='date', var_name='Index',
                                                                  value_name='1m').iloc[:, 1:]
    eps_tbl = eps_1m.merge(eps_3m, on='Index', how='left').merge(eps_1y, on='Index', how='left').merge(
        eps_6m, on='Index', how='left')
    # eps_tbl['diff'] = eps_tbl.grow - eps_tbl.v1
    eps_tbl = eps_tbl[['Index', '1y', '6m', '3m', '1m']]
    return eps_tbl


def eps_growth_mtm2(eps, window1):
    eps_1y = eps.pct_change(periods=252).iloc[-1:, :].reset_index().melt(id_vars='date', var_name='Index',
                                                                         value_name='1y').iloc[:, 1:]
    eps_6m = eps.pct_change(periods=21 * 6).iloc[-1:, :].reset_index().melt(id_vars='date', var_name='Index',
                                                                            value_name='1m').iloc[:, 1:]
    eps_1m = eps.pct_change(periods=21).iloc[-1:, :].reset_index().melt(id_vars='date', var_name='Index',
                                                                        value_name='1m').iloc[:, 1:]
    eps_3m = eps.pct_change(periods=62).iloc[-1:, :].reset_index().melt(id_vars='date', var_name='Index',
                                                                        value_name='3m').iloc[:, 1:]
    eps_tbl = eps_1m.merge(eps_3m, on='Index', how='left').merge(eps_1y, on='Index', how='left').merge(
        eps_6m, on='Index', how='left')
    # eps_tbl['diff'] = eps_tbl.grow - eps_tbl.v1
    eps_tbl = eps_tbl[['Index', '1y', '6m', '3m', '1m']]
    return eps_tbl


import plotly.io as pio

pio.renderers.default = "browser"
CHART_THEME = 'plotly_white'


def plot_mtm(data):
    # Plotly part
    fig_data = go.Figure()
    fig_data.layout.template = CHART_THEME
    fig_data.add_trace(go.Bar(
        x=data.reset_index().Index,
        y=(data['1m']).round(2),
        name='1m mtm'))
    fig_data.add_trace(go.Bar(
        x=data.reset_index().Index,
        y=(data['3m']).round(2),
        name='3m mtm'))
    fig_data.add_trace(go.Bar(
        x=data.reset_index().Index,
        y=(data['1y']).round(2),
        name='1y mtm'))
    # fig_data.add_trace(go.Bar(
    #  x=data.reset_index().Index,
    #  y=(data['total']).round(2),
    #  name='total mtm'))

    fig_data.update_layout(barmode='group')
    fig_data.layout.height = 450
    fig_data.update_layout(margin=dict(t=50, b=50, l=25, r=25))
    fig_data.update_layout(
        xaxis_tickfont_size=12,
        yaxis=dict(
            title='% change',
            titlefont_size=13,
            tickfont_size=12,
        ))

    fig_data.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99))

    return fig_data.show()


def plot_mtm_tbl(data):
    # Plotly part
    fig_data = go.Figure()
    fig_data.layout.template = CHART_THEME
    fig_data.add_trace(go.Bar(
        x=data.reset_index().Index,
        y=(data['1m']).round(2),
        name='1m mtm'))
    fig_data.add_trace(go.Bar(
        x=data.reset_index().Index,
        y=(data['3m']).round(2),
        name='3m mtm'))
    fig_data.add_trace(go.Bar(
        x=data.reset_index().Index,
        y=(data['1y']).round(2),
        name='1y'))
    # fig_data.add_trace(go.Bar(
    #  x=data.reset_index().Index,
    #  y=(data['total']).round(2),
    #  name='total mtm'))

    fig_data.update_layout(barmode='group')
    fig_data.layout.height = 450
    fig_data.update_layout(margin=dict(t=50, b=50, l=25, r=25))
    fig_data.update_layout(
        xaxis_tickfont_size=12,
        yaxis=dict(
            title='% change',
            titlefont_size=13,
            tickfont_size=12,
        ))

    fig_data.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99))

    return fig_data


def plot_timeline(data, Name):
    # Plotly part
    chart_data = go.Figure()

    for column in data.columns:
        chart_data.add_trace(go.Scatter(x=data.index, y=data[column], mode='lines', name=column))

    chart_data.layout.template = CHART_THEME
    chart_data.layout.height = 750
    chart_data.update_layout(
        margin=dict(t=100, b=100, l=50, r=50),
        xaxis_tickfont_size=12,
        yaxis=dict(
            title=Name,
            titlefont_size=14,
            tickfont_size=12
        )
    )

    chart_data.show()


def cal_momentum(series, window):
    """
    Calculate momentum of a series.

    Parameters:
        series (pd.Series): Input series.
        window (int): Window size for momentum calculation.

    Returns:
        pd.Series: Momentum of the series.
    """
    # return series.rolling(window).mean()
    return series.ewm(window).mean() * 2 - (series.ewm(window).mean()).ewm(window).mean()


Index = "C:/Users/westl/PycharmProjects/pythonProject/Index.xlsx"
oppor = "C:/Users/westl/PycharmProjects/pythonProject/S&P500.xlsx"
factset = "C:/Users/westl/PycharmProjects/pythonProject/D_Factset.xlsx"
factset_revision = "C:/Users/westl/PycharmProjects/pythonProject/D_Revision_SPX.xlsx"
factset_Index = "C:/Users/westl/PycharmProjects/pythonProject/D_Index_Factset.xlsx"
p_s = "C:/Users/westl/PycharmProjects/pythonProject/personal score_index.xlsx"

factset_Index_list = ['date', 'SPX Index', 'NDX Index', 'DJI Index', 'RTY Index', 'R_value', 'R_growth',
                      'S5TELS Index', 'S5CONS Index', 'S5COND Index', 'S5ENRS Index', 'S5FINL Index', 'S5HLTH Index',
                      'S5INDU Index', 'S5INFT Index', 'S5MATR Index', 'S5UTIL Index',
                      'SX5E Index', 'DAX Index', 'CAC Index','NKY Index']

pr = pd.read_excel(oppor, sheet_name=0, parse_dates=True)
pr = pr[pr['date'] >= "2013-01-01"]
bd = pd.read_excel(Index, sheet_name=12, parse_dates=True)
bd = bd[bd['date'] >= "2013-01-01"]

# 오늘 날짜 설정 (실제 오늘 날짜를 사용하려면 pd.Timestamp.today().normalize() 사용)
today = pd.Timestamp.today().normalize()  # 또는 pd.Timestamp.today().normalize()

# 마지막 인덱스와 값 가져오기
last_index = bd['Ticker'].iloc[-1]
last_value = bd['SPX Index'].iloc[-1]

# 새로운 행 생성
new_row = {
    'date': today,
    'Ticker': 'SPX Index',
    'SPX Index': last_value
}

new_row = pd.DataFrame([new_row])

# DataFrame에 새로운 행 추가
bd = pd.concat([bd, new_row], ignore_index=True)

eps_us = pd.read_excel(oppor, sheet_name=1, parse_dates=True)
eps_us = eps_us[eps_us['date'] >= "2013-01-01"]
equity_list = eps_us.columns
sales_us = pd.read_excel(oppor, sheet_name=2, parse_dates=True)
sales_us = sales_us[sales_us['date'] >= "2013-01-01"]
# ltg_us = pd.read_excel(oppor, sheet_name=24,parse_dates=True)
# ltg_us = ltg_us[ltg_us['date']>="2013-01-01"]
# ltg_us = ltg_us.fillna(0)
opm_us = pd.read_excel(oppor, sheet_name=8, parse_dates=True)
opm_us = opm_us[opm_us['date'] >= "2013-01-01"]
opm_us = opm_us.fillna(0)
cap_us = pd.read_excel(oppor, sheet_name=7, parse_dates=True)
cap_us = cap_us[cap_us['date'] >= "2013-01-01"]
cap_us = cap_us.fillna(0)
roe_us = pd.read_excel(oppor, sheet_name=10, parse_dates=True)
roe_us = roe_us[roe_us['date'] >= "2013-01-01"]
roe_us = roe_us.fillna(0)
pe_us = pd.read_excel(oppor, sheet_name=3, parse_dates=True)
pe_us = pe_us[pe_us['date'] >= "2013-01-01"]
pe_us = pe_us.fillna(0)
pe_index = pd.read_excel(Index, sheet_name=3, parse_dates=True)
pe_index = pe_index[pe_index['date'] >= "2013-01-01"]
peg_us = pd.read_excel(oppor, sheet_name=4, parse_dates=True)
peg_us = peg_us[peg_us['date'] >= "2013-01-01"]
peg_us = peg_us.fillna(0)

p_s_index = pd.read_excel(p_s, sheet_name=0, parse_dates=True)
p_s_index['date'] = pd.to_datetime(p_s_index['date'])
manual_scores_df = p_s_index.copy()


# 열 이름 변환 함수 정의
def rename_columns(columns):
    # 첫 번째 열 이름을 'date'로 변경
    new_columns = []
    for col_name in columns:
        # col_name이 문자열일 때만 변환 적용
        if isinstance(col_name, str) and col_name.strip():
            new_col_name = re.sub(r'-US\^', ' US Equity', col_name)
            new_columns.append(new_col_name)
        else:
            # 문자열이 아니거나 공백일 경우 'date'로 처리
            new_columns.append('date')
    return new_columns


eps_fact_us = pd.read_excel(factset, sheet_name=2, parse_dates=True, skiprows=1)
eps_fact_us.columns = rename_columns(eps_fact_us.columns)
eps_fact_us['date'] = pd.to_datetime(eps_fact_us['date'])

sales_fact_us = pd.read_excel(factset, sheet_name=3, parse_dates=True, skiprows=1)
sales_fact_us.columns = rename_columns(sales_fact_us.columns)
sales_fact_us['date'] = pd.to_datetime(sales_fact_us['date'])

revision_fact_us = pd.read_excel(factset_revision, sheet_name=1, parse_dates=True, skiprows=1)
revision_fact_us.columns = rename_columns(revision_fact_us.columns)
revision_fact_us['date'] = pd.to_datetime(revision_fact_us['date'])

revision_fact_sales_us = pd.read_excel(factset_revision, sheet_name=2, parse_dates=True, skiprows=1)
revision_fact_sales_us.columns = rename_columns(revision_fact_sales_us.columns)
revision_fact_sales_us['date'] = pd.to_datetime(revision_fact_sales_us['date'])


eps_fact_Index = pd.read_excel(factset_Index, sheet_name=0, parse_dates=True).loc[2:]
eps_fact_Index.columns = factset_Index_list
eps_fact_Index['date'] = pd.to_datetime(eps_fact_Index['date'])

sales_fact_Index = pd.read_excel(factset_Index, sheet_name=1, parse_dates=True).loc[2:]
sales_fact_Index.columns = factset_Index_list
sales_fact_Index['date'] = pd.to_datetime(sales_fact_Index['date'])

fcf_fact_Index = pd.read_excel(factset_Index, sheet_name=2, parse_dates=True).loc[2:]
fcf_fact_Index.columns = factset_Index_list
fcf_fact_Index['date'] = pd.to_datetime(fcf_fact_Index['date'])

revision_fact_Index = pd.read_excel(factset_Index, sheet_name=3, parse_dates=True).loc[2:]
revision_fact_Index.columns = factset_Index_list
revision_fact_Index['date'] = pd.to_datetime(revision_fact_Index['date'])

#revision_fact_sales_Index = pd.read_excel(factset_Index, sheet_name=4, parse_dates=True).loc[2:]
#revision_fact_sales_Index.columns = factset_Index_list
#revision_fact_sales_Index['date'] = pd.to_datetime(revision_fact_sales_Index['date'])

pr_res = pd.read_excel(Index, sheet_name=0, parse_dates=True)
pr_res = pr_res[pr_res['date'] >= "2013-01-01"]
eps_res = pd.read_excel(Index, sheet_name=1, parse_dates=True)
eps_res = eps_res[eps_res['date'] >= "2013-01-01"]
sales_res = pd.read_excel(Index, sheet_name=2, parse_dates=True)
sales_res = sales_res[sales_res['date'] >= "2013-01-01"]
fcf_res = pd.read_excel(Index, sheet_name=5, parse_dates=True)
fcf_res = fcf_res[fcf_res['date'] >= "2013-01-01"]
opm_res = pd.read_excel(Index, sheet_name=8, parse_dates=True)
opm_res = opm_res[fcf_res['date'] >= "2013-01-01"]
Index_list = pr_res.columns

pr_bd = bd[['date']].merge(pr, on='date', how='left')
pr_res_bd = bd[['date']].merge(pr_res, on='date', how='left')
eps_res_bd = bd[['date']].merge(eps_res, on='date', how='left')
sales_res_bd = bd[['date']].merge(sales_res, on='date', how='left')
fcf_res_bd = bd[['date']].merge(fcf_res, on='date', how='left')
opm_res_bd = bd[['date']].merge(opm_res, on='date', how='left')
sales_us_bd = bd[['date']].merge(sales_us, on='date', how='left')
eps_us_bd = bd[['date']].merge(eps_us, on='date', how='left')
cap_us_bd = bd[['date']].merge(cap_us, on='date', how='left')
opm_us_bd = bd[['date']].merge(opm_us, on='date', how='left')
# ltg_us_bd = bd[['date']].merge(ltg_us, on = 'date', how='left')
roe_us_bd = bd[['date']].merge(roe_us, on='date', how='left')
pe_us_bd = bd[['date']].merge(pe_us, on='date', how='left')
peg_us_bd = bd[['date']].merge(peg_us, on='date', how='left')
pe_index_bd = bd[['date']].merge(pe_index, on='date', how='left')
eps_fact_us_bd = bd[['date']].merge(eps_fact_us, on='date', how='left')
sales_fact_us_bd = bd[['date']].merge(sales_fact_us, on='date', how='left')
revision_fact_us_bd = bd[['date']].merge(revision_fact_us, on='date', how='left')
revision_fact_sales_us_bd = bd[['date']].merge(revision_fact_sales_us, on='date', how='left')
eps_fact_Index_bd = bd[['date']].merge(eps_fact_Index, on='date', how='left')
sales_fact_Index_bd = bd[['date']].merge(sales_fact_Index, on='date', how='left')
revision_fact_Index_bd = bd[['date']].merge(revision_fact_Index, on='date', how='left')


def calculate_rolling_beta(stock_returns, market_returns, window):
    rolling_covariance = stock_returns.rolling(window=window).cov(market_returns)
    market_variance = market_returns.rolling(window=window).var()
    rolling_beta = rolling_covariance / market_variance
    return rolling_beta


def beta_tracking(returns, factors, rolling_window):
    rolling_beta_data = {}
    total_beta_df = pd.DataFrame()
    # number = len(returns.index) - (21 * month) + 1

    # Fill NaN values in returns with 0
    returns = returns.fillna(0)
    factors = factors.fillna(0)

    for i in tqdm(range(len(returns.columns))):
        aligned_returns = pd.DataFrame()
        aligned_returns = pd.concat([returns, factors], axis=1).dropna()
        stock_returns = aligned_returns.iloc[:, i]
        market_returns = aligned_returns.iloc[:, -1]

        # Calculate rolling beta
        rolling_beta = calculate_rolling_beta(stock_returns, market_returns, rolling_window)
        rolling_beta_data[returns.columns[i]] = rolling_beta

        # Convert the rolling beta data to a DataFrame
        rolling_beta_df = pd.DataFrame(rolling_beta_data)

    return rolling_beta_df



Index_eps_uni_tbl = eps_growth_nor(eps_fact_Index_bd.set_index('date'), 252, 252 * 3).fillna(0)


us_eps_tbl_uni_gr = eps_growth_mtm(us_eps_uni_tbl)
us_eps_tbl_uni_index = us_eps_tbl_uni_gr.copy()
us_eps_tbl_uni_index = us_eps_tbl_uni_index.set_index('Index')

us_eps_ai_fact_tbl_gr = eps_growth_mtm(us_eps_ai_fact_tbl)
us_eps_ai_tbl_fact_index = us_eps_ai_fact_tbl_gr.copy()
us_eps_ai_tbl_fact_index = us_eps_ai_tbl_fact_index.set_index('Index')

us_eps_ai_tbl_gr = eps_growth_mtm(us_eps_ai_tbl.reset_index(), 1)
us_eps_ai_tbl_index = us_eps_ai_tbl_gr.copy()
us_eps_ai_tbl_index = us_eps_ai_tbl_index.set_index('Index')

us_eps_tbl_gr_v2 = eps_growth_mtm2(eps_res_bd[factset_list])
us_eps_tbl_v2_index = us_eps_tbl_gr_v2.copy()
us_eps_tbl_v2_index = us_eps_tbl_v2_index.set_index('Index')

us_sales_tbl_gr = eps_growth_mtm(us_sales_tbl.reset_index(), 1)
us_sales_tbl_index = us_sales_tbl_gr.copy()
us_sales_tbl_index = us_sales_tbl_index.set_index('Index')

us_sales_ai_tbl_gr = eps_growth_mtm(us_sales_ai_tbl.reset_index(), 1)
us_sales_ai_tbl_index = us_sales_ai_tbl_gr.copy()
us_sales_ai_tbl_index = us_sales_ai_tbl_index.set_index('Index')

opm_us_gr = mtm_growth(opm_us_bd.set_index('date')[AI_list], 252 * 3)

Index_revision = revision_growth(revision_fact_Index.set_index('date'), 252, 252 * 3)
Index_revision_tbl = cal_momentum(Index_revision, 63).loc["2016-01-01":]
plot_timeline(Index_revision_tbl.loc["2022-01-01":], "Index Revision Graph")
# us_sales_tbl_v2_gr = eps_growth_mtm(us_sales_tbl_v2.reset_index(),1,3)
# us_sales_tbl_v2_index = us_sales_tbl_v2_gr.copy()
# us_sales_tbl_v2_index = us_sales_tbl_v2_index.set_index('Index')


plot_mtm(us_eps_tbl_uni_index)
plot_mtm(us_eps_tbl_v2_index)
# plot_mtm(us_eps_tbl_v2_index)
plot_timeline(us_eps_tbl, 'US Equity EPS Growth')
plot_timeline(us_eps_uni_tbl.loc["2016-01-01":], 'US Equity EPS Growth')
plot_timeline(us_eps_uni_tbl_5y.loc["2016-01-01":], 'US Equity EPS Growth')
plot_timeline(us_sales_uni_tbl.loc["2016-01-01":], 'US Equity Sales Growth')

plot_timeline(Index_eps_uni_tbl.loc["2018-01-01":], 'Index EPS Growth')

plot_timeline(us_eps_ai_fact_tbl.loc["2016-01-01":], 'US Equity EPS Growth')
plot_timeline(us_sales_ai_fact_tbl.loc["2016-01-01":], 'US Equity Sales Growth')
plot_timeline(us_revision_eq_tbl.loc["2018-01-01":], 'US Equity Revision Moving Average')
plot_timeline(opm_us_gr.loc["2016-01-01":], 'US Equity OP_Margin Growth')


# ===============================================================================================


def get_last_trading_day(year, quarter, daily_returns):
    # 분기 마지막 달
    end_month = 3 * quarter
    # 분기 마지막 날 계산
    end_date = pd.Timestamp(year=year, month=end_month, day=1) + pd.offsets.MonthEnd(0)
    # 분기 마지막 날이 거래일인지 확인, 아니면 그 이전 거래일을 찾음
    trading_days = daily_returns.loc[:end_date].index
    if len(trading_days) == 0:
        return None
    return trading_days[-1]


# 필요한 함수들 정의 (예: eps_growth_nor, revision_growth, cal_momentum, plot_timeline)
def create_quarterly_group_stocks(score_ranks, daily_returns, st_list):
    quarterly_group_stocks = {}
    quarterly_rebalance_dates = {}  # 분기별 리밸런싱 날짜 저장
    years = daily_returns.index.year.unique()

    for year in years:
        for quarter in [1, 2, 3, 4]:
            # 분기의 시작과 끝 날짜 정의
            start_month = 3 * (quarter - 1) + 1
            end_month = start_month + 2
            start_date = pd.Timestamp(year=year, month=start_month, day=1)
            end_date = pd.Timestamp(year=year, month=end_month, day=1) + pd.offsets.MonthEnd(0)

            # 해당 분기의 날짜 인덱스 추출
            quarter_dates = daily_returns.loc[start_date:end_date].index

            if len(quarter_dates) == 0:
                print(f"No data for {year}-Q{quarter}")
                continue

            # quarter_dates 중 score_ranks에 존재하는 날짜만 선택
            valid_quarter_dates = quarter_dates.intersection(score_ranks.index)
            if len(valid_quarter_dates) == 0:
                print(f"No valid score ranks for {year}-Q{quarter}")
                continue

            # 해당 분기의 평균 순위 계산
            avg_ranks = score_ranks.loc[valid_quarter_dates].mean().sort_values()

            # 상위, 중위, 하위 그룹으로 분할
            num_stocks = len(st_list)
            tercile = num_stocks // 3

            high_rank = avg_ranks.index[:tercile]
            mid_rank = avg_ranks.index[tercile:2 * tercile]
            low_rank = avg_ranks.index[2 * tercile:]

            # 키를 'YYYY-QX' 형식으로 설정
            key = f"{year}-Q{quarter}"

            quarterly_group_stocks[key] = {
                'Top': list(high_rank),
                'Middle': list(mid_rank),
                'Bottom': list(low_rank)
            }

            # 리밸런싱 날짜 계산 및 저장
            last_trading_day = get_last_trading_day(year, quarter, daily_returns)
            if last_trading_day:
                quarterly_rebalance_dates[key] = last_trading_day
            else:
                print(f"No trading days found for {year}-Q{quarter}")

    return quarterly_group_stocks, quarterly_rebalance_dates


def create_monthly_group_stocks(score_ranks, daily_returns, st_list):
    monthly_group_stocks = {}
    monthly_rebalance_dates = {} # 월별 리밸런싱 날짜 저장
    years = daily_returns.index.year.unique()

    for year in years:
        for month in range(1,13):
            # 월의 시작과 끝 날짜 정의
            start_date = pd.Timestamp(year = year, month = month, day = 1)
            end_date = start_date + pd.offsets.MonthEnd(0)

            # 해당 월의 날짜 인덱스 추출
            month_dates = daily_returns.loc[start_date:end_date].index

            if len(month_dates) == 0:
                print(f"No data for {year}-{month:02d}")
                continue

            # month_dates 중 score_ranks에 존재하는 날짜만 선택
            valid_month_dates = month_dates.intersection(score_ranks.index)
            if len(valid_month_dates) == 0:
                print(f"No valid score ranks for {year}-{month:02d}")
                continue

            # 해당 월의 평균 순위 계산
            avg_ranks = score_ranks.loc[valid_month_dates].mean().sort_values()

            # 상위,중위,하위 그룹으로 분할
            num_stocks = len(st_list)
            tercile = num_stocks // 3

            high_rank = avg_ranks.index[:tercile]
            mid_rank = avg_ranks.index[tercile:2 * tercile]
            low_rank = avg_ranks.index[2*tercile:]

            # 키를 'YYYY-MM' 형식으로 설정
            key = f"{year}-{month:02d}"

            monthly_group_stocks[key] = {
                'Top': list(high_rank),
                'Middle': list(mid_rank),
                'Bottom': list(low_rank)
            }

            # 리밸런싱 날짜 계산 및 저장
            # 월말 날짜를 리밸런싱 날짜로 사용
            trading_days_in_month = daily_returns.loc[start_date:end_date].index
            if len(trading_days_in_month) > 0:
                last_trading_day = trading_days_in_month[-1]
                monthly_rebalance_dates[key] = last_trading_day
            else:
                print(f"No trading days found for {year}-{month:02d}")

    return monthly_group_stocks, monthly_rebalance_dates


def calculate_ic(scores, daily_returns, rebalance_dates, st_list):
    ic_values = []
    ic_pvalues = []
    ic_dates = []

    for i in range(len(rebalance_dates) -1):
        date = rebalance_dates[i]
        next_date = rebalance_dates[i + 1]

        # 현재 리밸런싱 날짜의 팩터 스코어
        factor_score = scores.loc[date]

        # 다음 리밸런싱 날짜까지의 전진 수익률 계산
        forward_returns = daily_returns.loc[date:next_date].iloc[1:].sum()

        # 팩터 스코어와 전진 수익률의 종목 정렬 맞추기
        common_stocks = factor_score.index.intersection(forward_returns.index)
        factor_score = factor_score[common_stocks]
        forward_returns = forward_returns[common_stocks]

        # 순위 상관계수 계산(Spearman Correlation)
        ic, p_value = stats.spearmanr(factor_score, forward_returns)

        ic_values.append(ic)
        ic_pvalues.append(p_value)
        ic_dates.append(date)

        # 결과를 데이터프레임으로 저장
        ic_df = pd.DataFrame({
            'IC': ic_values,
            'p-value': ic_pvalues
        }, index = ic_dates)

        # 평균 IC와 표준편차 계산
        mean_ic = np.mean(ic_values)
        std_ic = np.std(ic_values)

    print(f"Mean IC: {mean_ic:.4f}, Standard Deviation of IC: {std_ic:.4f}")

    return ic_df

def calculate_ic_annual(scores, daily_returns, rebalance_dates, st_list):
    ic_values = []
    ic_dates = []

    for i in range(len(rebalance_dates)-1):
        date = rebalance_dates[i]
        next_date = rebalance_dates[i + 1]

        # 현재 리밸런싱 날짜의 팩터 스코어
        factor_score = scores.loc[date]

        # 다음 리밸런싱 날짜까지의 전진 수익률 계산
        forward_returns = daily_returns.loc[date:next_date].iloc[1:].sum()

        # 팩터 스코어와 전진 수익률위 종목 정렬 맞추기
        common_stocks = factor_score.index.intersection(forward_returns.index)
        factor_score = factor_score[common_stocks]
        forward_returns = forward_returns[common_stocks]

        # 순위 상관계수 계싼
        ic, _ = stats.spearmanr(factor_score, forward_returns)

        ic_values.append(ic)
        ic_dates.append(date)

    # 결과 데이터프레임 저장
    ic_df = pd.DataFrame({'IC' : ic_values}, index = ic_dates)
    ic_df.index = pd.to_datetime(ic_df.index)

    # 연도별 평균 IC 계산
    ic_df['Year'] = ic_df.index.year
    annual_ic = ic_df.groupby('Year')['IC'].mean()

    return annual_ic

periods_days = {
    '1M': 21,
    '3M': 63,
    '6M': 126,
    '1Y': 252,
    '3Y': 756,
    '5Y': 1260,
    'YTD': 'YTD'
}

def calculate_period_returns(cum_returns, periods):
    period_returns = {}
    last_date = cum_returns.index[-1]
    for period in periods:
        if period == 'YTD':
            # 현재 연도의 첫 번째 거래일 찾기
            current_year = last_date.year
            current_year_data = cum_returns.loc[cum_returns.index.year == current_year]
            if not current_year_data.empty:
                start_date = current_year_data.index[0]
            else:
                # 해당 연도의 데이터가 없는 경우 계산 건너뜁니다.
                continue
        else:
            start_idx = max(0, len(cum_returns) - period)
            start_date = cum_returns.index[start_idx]
        start_value = cum_returns.loc[start_date]
        end_value = cum_returns.iloc[-1]
        period_return = (end_value - start_value) / start_value
        period_returns[period] = period_return
    return period_returns

def calculate_rolling_ir(actual_returns, benchmark_returns, window):
    # window : Rolling 기간(영업일 기준)
    excess_returns = actual_returns - benchmark_returns
    rolling_mean = excess_returns.rolling(window = window).mean()*252
    rolling_std = excess_returns.rolling(window = window).std()* np.sqrt(252)
    rolling_ir = (rolling_mean / rolling_std)
    return rolling_ir

def calculate_factor_decay(factor_scores, daily_returns, max_lag, rebalance_dates):

    ic_decay={}

    for lag in range(1, max_lag + 1):
        ic_values = []

        for date in rebalance_dates:
            if date not in factor_scores.index:
                continue

           # 팩터스코어
            factor = factor_scores.loc[date]

            # 미래 수익률
            future_returns = daily_returns.shift(-lag).loc[date]
            if future_returns.isnull().any():
                continue

            # 종목 일치시키기
            common_stocks = factor.index.intersection(future_returns.index)
            factor = factor[common_stocks]
            future_returns = future_returns[common_stocks]

            # 순위 상관계수
            ic, _ = stats.spearmanr(factor, future_returns)
            ic_values.append(ic)

        # 평균 IC 계산
        mean_ic = np.nanmean(ic_values)
        ic_decay[lag] = mean_ic

    decay_df = pd.DataFrame.from_dict(ic_decay, orient='index', columns=['Mean_IC'])
    decay_df.index.name = 'Lag'
    return decay_df

def assign_scores_from_ranks(returns_df):
    scores_df = pd.DataFrame(index=returns_df.index, columns = returns_df.columns)
    labels = [-0.5,0,1.5]
    for date in returns_df.index:
        returns = returns_df.loc[date]
        returns.dropna()
        if returns.empty:
            continue
        # 순위를 기반으로 점수 부여
        try:
            scores = pd.qcut(returns.rank(method='first'), q = 3, labels=labels)
            scores_df.loc[date, returns.index] = scores
        except ValueError:
            # 고유한 값이 충분하지 않은 경우, 중앙값인 0으로 점수 부여
            scores_df.loc[date, returns.index] = 0
            # 점수를 float 형태로 변환
    scores_df = scores_df.astype(float)
    return scores_df


def calculate_weekly_ic(factor_scores, d_r, st_list):
    """
    Calculate the weekly Information Coefficient (IC) for each factor.

    Parameters:
    - factor_scores: dict of DataFrames containing factor scores, indexed by date with tickers as columns.
    - d_r: DataFrame of daily returns, indexed by date with tickers as columns.
    - st_list: list of tickers to include in the IC calculation.

    Returns:
    - weekly_ic_df: DataFrame containing weekly IC values for each factor.
    """

    # 1. 날짜 인덱스 정렬 및 공통 구간 추출
    common_dates = factor_scores[next(iter(factor_scores))].index.intersection(d_r.index)
    d_r = d_r.loc[common_dates]
    for factor_name in factor_scores:
        factor_scores[factor_name] = factor_scores[factor_name].loc[common_dates]

    # 2. 주간 수익률 계산 (금요일 기준 주간 수익률)
    weekly_returns = d_r.shift(1).resample('W').apply(lambda x: (1 + x).prod() - 1)

    # 3. 팩터 스코어를 주간 단위로 리샘플 (마지막 날의 스코어 사용)
    factor_scores_weekly = {}
    for factor_name, scores_df in factor_scores.items():
        # 주간 그룹화하여 각 주의 마지막 영업일의 팩터 스코어 선택
        scores_df_weekly = scores_df.resample('W').last()
        factor_scores_weekly[factor_name] = scores_df_weekly

    # 4. 주간 IC 계산
    weekly_ic_df = pd.DataFrame(index=weekly_returns.index)
    for factor_name, scores_df_weekly in factor_scores_weekly.items():
        ic_list = []
        for date in weekly_returns.index:
            factor_scores = scores_df_weekly.loc[date]
            next_return = weekly_returns.shift(-1).loc[date]

            # 결측치 제거 및 유효한 티커 선택
            valid_tickers = factor_scores.dropna().index.intersection(next_return.dropna().index).intersection(st_list)

            if len(valid_tickers) < 2:
                ic = np.nan
            else:
                # 유효한 티커의 팩터 스코어와 수익률 추출
                factor_scores_valid = factor_scores.loc[valid_tickers]
                return_valid = next_return.loc[valid_tickers]

                # 상수값 여부 확인
                if factor_scores_valid.nunique() <= 1 or return_valid.nunique() <= 1:
                    ic = np.nan
                else:
                    ic = factor_scores_valid.corr(return_valid, method='spearman')
            ic_list.append(ic)
        weekly_ic_df[factor_name] = ic_list

    return weekly_ic_df


#for factor, df in factor_scores.items():
#    df.fillna(0, inplace=True)

#f_s = factor_scores.copy()
#d_r = daily_returns.copy()
#aa = f_s_weekly.copy()
#bb = {}
#for factor_name, scores_df in aa.items():
#    # 주간 그룹화하여 각 주의 마지막 영업일의 팩터 스코어 선택
#    scores_df_weekly = scores_df.mean()
#    bb[factor_name] = scores_df_weekly


def calculate_factor_weights(ic_df, window):

    # 특정 팩터 제외한 IC 데이터프레임 생성
    ic_df_ex_p_s = ic_df.drop(columns=['p_s'], errors='ignore')
    # 지수 이동 평균을 사용하여 시간 가중 평균 계산
    factor_ic_avg = ic_df_ex_p_s.ewm(span=window, adjust=False).mean()

    # 각 날짜별로 팩터 IC 순위 계산(내림차순: 높은 IC가 높은 순위)
    factor_ranks = factor_ic_avg.rank(axis=1, method='first', ascending=False)

    # 순위에 따른 가중치 매핑
    rank_to_weight = { 1: 1.05, 2:1.025, 3:1.0, 4:0.975, 5:0.95}

    # 각 날짜별로 가중치 정규화
    factor_weights = factor_ranks.replace(rank_to_weight)

    # 결측치 처리
    factor_weights = factor_weights.fillna(0)

    return factor_weights

def calculate_annualized_return(portfolio_returns):
    cumulative_return = (1 + portfolio_returns).prod() -1
    num_years = len(portfolio_returns) / 252
    annualized_return = ( 1+ cumulative_return) ** (1 / num_years) -1
    return annualized_return

def calculate_annualized_volatility(portfolio_returns):
    return portfolio_returns.std() * np.sqrt(252)
#portfolio_returns = returns
#asset_returns = daily_returns
#score = scores_new.copy()

def calculate_periodic_ic(scores, asset_returns, rebalance_dates):

    ic_list = []
    period_dates = []

    # 스코어와 수익률의 인덱스와 열 맞추기
    scores, asset_returns = scores.align(asset_returns, join='inner', axis=1)

    # 이미 사전에 shift되어있음
    shifted_scores = scores

    for i in range(len(rebalance_dates)-1):
        start_date = rebalance_dates[i]
        end_date = rebalance_dates[i + 1]

        # 리밸런싱 날짜의 스코어
        if start_date in shifted_scores.index:
            scores_at_start = shifted_scores.loc[start_date]
        else:
            ic_list.append(np.nan)
            period_dates.append(start_date)
            continue

        # 해당기간의 수익률 데이터 선택
        period_returns = asset_returns.loc[start_date:end_date]

        # period_returns가 Series인 경우 DataFrame으로 변환
        if isinstance(period_returns, pd.Series):
            period_returns = period_returns.to_frame().T

        # 자산별로 기간 동안의 누적 수익률 계산
        cum_returns = period_returns.apply(lambda x: (1+x).prod()-1, axis=0)

        # 유효한 자산 선택
        valid = scores_at_start.notnull() & cum_returns.notnull()
        valid_assets = valid[valid].index

        if len(valid_assets) > 1:
            x = scores_at_start.loc[valid_assets]
            y = cum_returns.loc[valid_assets]

            x_rank = x.rank()
            y_rank = y.rank()

            # 분산이 0인지 확인
            if x_rank.std(ddof=0) == 0 or y_rank.std(ddof=0) == 0:
                ic = np.nan
            else:
                ic = x_rank.corr(y_rank, method='pearson')
        else:
            ic = np.nan

        ic_list.append(ic)
        period_dates.append(start_date)

    ic_df = pd.DataFrame({'IC': ic_list}, index=period_dates)
    return ic_df

def aggregate_monthly_ic(ic_df):
    ic_df.index = pd.to_datetime(ic_df.index)
    monthly_ic = ic_df.resample('M').mean()
    return monthly_ic

def calculate_annualized_ic(monthly_ic):
    mean_ic = monthly_ic['IC'].mean()
    annualized_ic = mean_ic *12
    return annualized_ic



def calculate_annualized_ir(portfolio_returns, benchmark_returns):
    excess_returns = portfolio_returns - benchmark_returns
    tracking_error = excess_returns.std() * np.sqrt(252)
    annualized_excess_return = calculate_annualized_return(excess_returns)
    ir = annualized_excess_return / tracking_error
    return ir

def calculate_ewma_covariance(returns, span=65):
    ewm_returns = returns.ewm(span=span).mean()
    deviation = returns - ewm_returns
    ewm_cov = deviation.ewm(span=span).cov()
    cov_matrix = ewm_cov.iloc[-len(returns.columns):]
    cov_matrix = cov_matrix.values.reshape(len(returns.columns), len(returns.columns))
    return cov_matrix

def assign_growth_groups(growth_series):
    """
    증가율 시리즈를 받아서 5개 그룹으로 나누고, 각 자산에 해당 그룹 번호를 반환합니다.
    그룹 번호는 1~5이며, 1이 가장 높은 증가율 그룹입니다.
    """
    # 결측치 제거
    valid_growth = growth_series.dropna()
    # 증가율 기준으로 자산들을 5분위로 분할
    quantiles = valid_growth.quantile([1/3, 2/3])
    groups = pd.Series(index=growth_series.index, dtype=int)
    for asset in growth_series.index:
        value = growth_series[asset]
        if pd.isna(value):
            groups[asset] = np.nan
        elif value <= quantiles[1/3]:
            groups[asset] = 3 # 가장 낮은 그룹
        elif value <= quantiles[2/3]:
            groups[asset] = 2
        else:
            groups[asset] = 1 # 가장 높은 그륩
    return groups

# 새로운 score_adjustments 정의
score_adjustments_eps = {1: 2.0, 2: 1.0, 3: -0.5}
score_adjustments_sales = {1: 1.5, 2: 0.5, 3: -1.0}
score_adjustments_revision_chg = {1: 1.5, 2: 0.5, 3: -1.0}


def main():
    # 데이터 파일 경로 설정
    data_dir = 'C:/Users/westl/PycharmProjects/pythonProject/venv/Index Quant'
    # 종목 리스트
    st_list = ['SPX Index','NDX Index','DJI Index','RTY Index',
               'SX5E Index','DAX Index','CAC Index','NKY Index','BM7P Index']

    # 데이터 로드 및 전처리
    #us_eps_st_tbl = eps_growth_nor(eps_uni_bd.set_index('date')[st_list].shift(1), 252, 252 * 3).fillna(0)
    #us_sales_st_tbl = eps_growth_nor(sales_uni_bd.set_index('date')[st_list].shift(1), 252, 252 * 3).fillna(0)
    #us_revision_st_raw = revision_fact_us_bd.merge(revision_fact_Index[['date', 'SPX Index', 'NDX Index']], on='date',
    #                                               how='left')
    #us_opm_st = eps_growth_nor(opm_uni_bd.set_index('date')[st_list].shift(1), 252, 252 * 3).fillna(0)


    us_eps_st_tbl = eps_growth_nor(eps_res_bd.set_index('date')[st_list].shift(1), 252, 252 * 3).fillna(0)
    us_sales_st_tbl = eps_growth_nor(sales_res_bd.set_index('date')[st_list].shift(1), 252, 252 * 3).fillna(0)
    index_fcf_st_tbl = eps_growth_nor(fcf_res_bd.set_index('date')[st_list].shift(1), 252, 252 * 3).fillna(0)
    #us_revision_st_raw = revision_fact_us_bd.merge(revision_fact_Index[['date', 'SPX Index', 'NDX Index']], on='date',
    #                                               how='left')
    #us_opm_st = eps_growth_nor(opm_uni_bd.set_index('date')[st_list].shift(1), 252, 252 * 3).fillna(0)

    us_eps_fwd = eps_res_bd.set_index('date')[st_list].shift(1)
    us_sales_fwd = sales_res_bd.set_index('date')[st_list].shift(1)
    index_fcf_fwd = fcf_res_bd.set_index('date')[st_list].shift(1)
    us_eps_fwd_3m = us_eps_fwd.pct_change(periods=62).fillna(0)
    us_sales_fwd_3m = us_sales_fwd.pct_change(periods=62).fillna(0)
    index_fcf_fwd_3m = index_fcf_fwd.pct_change(periods=62).fillna(0)

    # 마지막 두 개의 행의 인덱스를 가져옵니다.
    #last_idx = revision_fact_Index_bd.index[-1]
    #prev_idx = revision_fact_Index_bd.index[-2]

    # 'date' 컬럼을 제외한 나머지 컬럼 리스트를 가져옵니다.
    #columns_to_fill = us_revision_st_raw.columns.difference(['date'])

    # 마지막 행의 NaN 값을 이전 행의 값으로 대체합니다.
    #us_revision_st_raw.loc[last_idx, columns_to_fill] = us_revision_st_raw.loc[last_idx, columns_to_fill].fillna(
    #    us_revision_st_raw.loc[prev_idx, columns_to_fill])

    #us_revision = us_revision_st_raw.set_index('date')[st_list].shift(1)
    #us_revision_st = revision_growth(revision_fact_Index_bd.set_index('date')[st_list].shift(1), 252, 252 * 3).fillna(0)
    #us_revision_st_tbl = cal_momentum(us_revision_st, 63)

    #us_revision_sales = revision_fact_sales_us_bd.set_index('date')[st_list].shift(1)
    #us_revision_sales_st = revision_growth(revision_fact_sales_us_bd.set_index('date')[st_list].shift(1), 252, 252 * 3).fillna(0)
    #us_revision_sales_st_tbl = cal_momentum(us_revision_sales_st, 63)

    #us_revision_3m = us_revision.diff(periods=63)
    #us_revision_3m_sales = us_revision_sales.diff(periods=63)

    #us_opm_st_tbl = cal_momentum(us_opm_st, 63)


    us_eps_st_tbl = us_eps_st_tbl.copy().loc["2016-01-01":]
    us_sales_st_tbl = us_sales_st_tbl.copy().loc["2016-01-01":]
    #us_opm_st_tbl = us_opm_st_tbl.copy().loc["2016-01-01":]
    index_fcf_st_tbl = index_fcf_st_tbl.copy().loc["2016-01-01":]
    #us_revision_st_tbl = us_revision_st_tbl.copy().loc["2016-01-01":]
    #us_revision_sales_st_tbl = us_revision_sales_st_tbl.copy().loc["2016-01-01":]


    plot_timeline(us_eps_st_tbl, "Quant Strategy EPS")
    plot_timeline(us_sales_st_tbl, "Quant Strategy Sales")
    plot_timeline(index_fcf_st_tbl, "Quant Strategy Free Cashflow")
    #plot_timeline(us_revision_st_tbl, "Quant Strategy Revision")


    pr_bd_st_tbl = pr_res_bd.set_index('date')[st_list]

    # 일별 리턴 계산
    daily_returns = pr_bd_st_tbl.pct_change().fillna(0)

    # 날짜 설정
    start_date = '2015-01-01'  # 가격 데이터의 시작 날짜를 2015년으로 조정
    end_date = daily_returns.index.max()
    fundamental_start_date = us_eps_st_tbl.index.min()

    # 모멘텀 지표 계산 (12개월, 3개월 수익률을 일수로 변환하여 계산)
    momentum_252d_raw = pr_bd_st_tbl.pct_change(252).shift(1).dropna()
    momentum_63d_raw = pr_bd_st_tbl.pct_change(63).shift(1).dropna()

    # 모멘텀 지표 표준화
    momentum_252d = revision_growth(momentum_252d_raw, window1=0, window2=252 * 3)
    momentum_63d = revision_growth(momentum_63d_raw, window1=0, window2=252 * 3)

    # 모멘텀 팩터 점수 계산
    mom_12m_scores = assign_scores_from_ranks(momentum_252d_raw)
    mom_3m_scores = assign_scores_from_ranks(momentum_63d_raw)


    # 스코어 저장용 데이터프레임 초기화
    dates = daily_returns.loc[fundamental_start_date:].index
    scores = pd.DataFrame(index=dates, columns=st_list)

    # 추세 분석에 활용할 지표 값 저장용 데이터프레임
    eps_values = pd.DataFrame(index=dates, columns=st_list)
    sales_values = pd.DataFrame(index=dates, columns=st_list)
    fcf_values = pd.DataFrame(index=dates, columns=st_list)
    #revision_values = pd.DataFrame(index=dates, columns=st_list)
    momentum_12m_values = pd.DataFrame(index=dates, columns=st_list)
    momentum_3m_values = pd.DataFrame(index=dates, columns=st_list)
    #revision_last = pd.DataFrame(index=dates, columns=st_list)
    #revision_sales = pd.DataFrame(index=dates, columns=st_list)
    #revision_sales_last = pd.DataFrame(index=dates, columns=st_list)


    # 추세 분석 기간 설정 (최근 20일)
    trend_period_1m = 21
    trend_period_3m = 63

    # 거래비용 설정 (예: 0.1%)
    transaction_cost_rate = 0.001

    # 리밸런싱 주기 설정 (예: 월말 리밸런싱)
    if not isinstance(dates, pd.DatetimeIndex):
        dates = pd.to_datetime(dates)
    rebalance_dates = pd.to_datetime(dates.to_series().resample('M').last().dropna().values)

    # 포트폴리오 비중 저장용 데이터프레임 초기화
    benchmark_weights = pd.DataFrame(index=dates, columns=st_list)
    actual_weights = pd.DataFrame(index=dates, columns=st_list)

    # 이전 비중 초기화 (초기에는 동일 비중)
    prev_benchmark_weight = pd.Series(1 / len(st_list), index=st_list)
    prev_actual_weight = pd.Series(1 / len(st_list), index=st_list)

    # 누적 거래비용 초기화
    benchmark_transaction_costs = pd.Series(0, index=dates)
    actual_transaction_costs = pd.Series(0, index=dates)

    # Initialize variavles for the new portfolio with overlay
    actual_weights_overlay = pd.DataFrame(index=dates, columns=st_list)
    overlay_weights_df = pd.DataFrame(0, index=dates, columns=st_list)
    prev_actual_weight_overlay = pd.Series(1/len(st_list), index=st_list)
    actual_transaction_costs_overlay = pd.Series(0, index=dates)

    # Initialize variavles for the new portfolio with eps_overlay
    actual_weights_eps_overlay = pd.DataFrame(index=dates, columns=st_list)
    eps_overlay_weights_df = pd.DataFrame(0, index=dates, columns=st_list)
    prev_actual_weight_eps_overlay = pd.Series(1 / len(st_list), index=st_list)
    actual_transaction_costs_eps_overlay = pd.Series(0, index=dates)

    # Initialize variables for the combined overlay portfolio
    actual_weights_combined_overlay = pd.DataFrame(index=dates, columns=st_list)
    overlay_weights_combined_df = pd.DataFrame(0, index=dates, columns=st_list)
    overlay_weights_eps_combined_df = pd.DataFrame(0, index=dates, columns=st_list)
    overlay_weights_momentum_combined_df = pd.DataFrame(0, index=dates, columns=st_list)
    prev_actual_weight_combined_overlay = pd.Series(1 / len(st_list), index=st_list)
    actual_transaction_costs_combined_overlay = pd.Series(0, index=dates)

    # Initialize variables for the Growth portfolio
    actual_weights_growth = pd.DataFrame(index=dates, columns=st_list)
    prev_actual_weight_growth = pd.Series(1/len(st_list), index=st_list)
    actual_transaction_costs_growth = pd.Series(0, index=dates)

    # Initialize variables for the momentum portfolio
    actual_weights_momentum = pd.DataFrame(index=dates, columns=st_list)
    prev_actual_weight_momentum = pd.Series(1/ len(st_list), index=st_list)
    actual_transaction_costs_momentum = pd.Series(0, index=dates)

    # Initialize variables for the overlay portfolios
    overlay_total_weight = 0.05
    combined_overlay_total_weight = 0.10

    # 각 요소별 스코어 저장용 데이터프레임 생성
    factor_scores = {
        'eps_growth': pd.DataFrame(index=dates, columns=st_list),
        'sales_growth': pd.DataFrame(index=dates, columns=st_list),
     #   'revision_ratio': pd.DataFrame(index=dates, columns=st_list),
        'fcf_growth' : pd.DataFrame(index=dates, columns=st_list),
        'mom_12m': pd.DataFrame(index=dates, columns=st_list),
        'mom_3m': pd.DataFrame(index=dates, columns=st_list),
        'p_s': pd.DataFrame(index=dates, columns=st_list)
    }

    # 매뉴얼 가산점 로드
    manual_scores_df = p_s_index.fillna(0)

    # 메인 루프: 각 날짜에 대해 포트폴리오 구성 및 거래비용 계산
    for date_idx, date in tqdm(enumerate(dates), total=len(dates)):
        # 스코어 계산
        if date in us_eps_st_tbl.index:
            # 지표들
            eps_growth = us_eps_st_tbl.loc[date].values.astype(float)
            sales_growth = us_sales_st_tbl.loc[date].values.astype(float)
        #    revision_ratio = us_revision_st_tbl.loc[date].values.astype(float)
        #    revision_rate = us_revision.loc[date].values.astype(float)
            fcf_growth = index_fcf_st_tbl.loc[date].values.astype(float)


            # 모멘텀 지표들
            mom_12m = momentum_252d.loc[date].values
            mom_3m = momentum_63d.loc[date].values
            mom_12m_rank = mom_12m_scores.loc[date].values
            mom_3m_rank = mom_3m_scores.loc[date].values

            # 결측치 처리
            mom_12m = np.nan_to_num(mom_12m)
            mom_3m = np.nan_to_num(mom_3m)

            # 지표 값 저장 (추세 분석을 위해)
            eps_values.loc[date] = eps_growth
            sales_values.loc[date] = sales_growth
        #    revision_values.loc[date] = revision_ratio
        #    revision_last.loc[date] = revision_rate
            fcf_values.loc[date] = fcf_growth
            momentum_12m_values.loc[date] = mom_12m
            momentum_3m_values.loc[date] = mom_3m

            # Forward EPS/Sales 3개월 증가율 가져오기
            if date in us_eps_fwd_3m.index and date in us_sales_fwd_3m.index:
                eps_growth_3m = us_eps_fwd_3m.loc[date]
                sales_growth_3m = us_sales_fwd_3m.loc[date]
         #       eps_revision = us_revision.loc[date]
                fcf_growth_3m = index_fcf_fwd_3m.loc[date]
         #       eps_revision_chg = us_revision_3m.loc[date]

            else:
                eps_growth_3m = pd.Series(index=st_list)
                sales_growth_3m = pd.Series(index=st_list)


            # EPS 증가율 기반 그룹 뷴류
            eps_growth_groups = assign_growth_groups(eps_growth_3m)
         #   eps_revision_groups = assign_growth_groups(eps_revision)
         #   eps_revision_chg_groups = assign_growth_groups(eps_revision_chg)

            # Sales 증가율 기반 그룹 분류
            sales_growth_groups = assign_growth_groups(sales_growth_3m)
            fcf_growth_groups = assign_growth_groups(fcf_growth_3m)


            # 그룹 번호에 따라 스코어 조정 값 매핑
            eps_score_adjustments = eps_growth_groups.map(score_adjustments_eps).reindex(st_list).fillna(0)
          #  eps_score_revision_adjustments = eps_revision_groups.map(score_adjustments_eps).reindex(st_list).fillna(0)
          #  eps_score_revision_chg_adjustments = eps_revision_chg_groups.map(score_adjustments_revision_chg).reindex(st_list).fillna(0)
            sales_score_adjustments = sales_growth_groups.map(score_adjustments_sales).reindex(st_list).fillna(0)
            fcf_growth_adjustments = fcf_growth_groups.map(score_adjustments_sales).reindex(st_list).fillna(0)
            #sales_score_revision_chg_adjustments = sales_revision_chg_groups.map(score_adjustments_revision_chg).reindex(st_list).fillna(0)

            # 각 팩터별 스코어를 초기화합니다.(표준화 스코어 영향력 최소화)
            factor_scores['eps_growth'].loc[date] = eps_growth*0.01
            factor_scores['sales_growth'].loc[date] = sales_growth*0.01
           # factor_scores['revision_ratio'].loc[date] = revision_ratio*0.01
            factor_scores['fcf_growth'].loc[date] = fcf_growth*0.01
            factor_scores['mom_12m'].loc[date] = mom_12m_rank
            factor_scores['mom_3m'].loc[date] = mom_3m_rank

            # 스코어 조정 적용
            for i, ticker in enumerate(st_list):
                factor_scores['eps_growth'].loc[date, ticker] += eps_score_adjustments[ticker]
                factor_scores['sales_growth'].loc[date, ticker] += sales_score_adjustments[ticker]
            #    factor_scores['revision_ratio'].loc[date, ticker] += eps_score_revision_adjustments[ticker]
            #    factor_scores['revision_ratio'].loc[date, ticker] += eps_score_revision_chg_adjustments[ticker]
                factor_scores['fcf_growth'].loc[date, ticker] += fcf_growth_adjustments[ticker]

            # total_score를 각 팩터 스코어의 합으로 초기화합니다.
            total_score = (
                factor_scores['eps_growth'].loc[date].astype(float)
                + factor_scores['sales_growth'].loc[date].astype(float)
            #    + factor_scores['revision_ratio'].loc[date].astype(float)
                + factor_scores['fcf_growth'].loc[date].astype(float)
                + factor_scores['mom_12m'].loc[date].astype(float)
                + factor_scores['mom_3m'].loc[date].astype(float)
            )

            # 최근 trend_period 기간의 추세를 이용하여 하단에서 상방으로 전환 여부 확인
            if date_idx >= trend_period_3m:
                for i, ticker in enumerate(st_list):
                    # 각 팩터별 가산점 변수를 초기화합니다.
                    eps_score = factor_scores['eps_growth'].loc[date, ticker]
                    sales_score = factor_scores['sales_growth'].loc[date, ticker]
            #        revision_score = factor_scores['revision_ratio'].loc[date, ticker]
                    fcf_score = factor_scores['fcf_growth'].loc[date, ticker]
                    mom_12m_score = factor_scores['mom_12m'].loc[date, ticker]
                    mom_3m_score = factor_scores['mom_3m'].loc[date, ticker]

                    # EPS 성장률 추세 분석
                    eps_recent_3m = eps_values[ticker].iloc[date_idx - trend_period_3m:date_idx].astype(
                        float).dropna()
                    eps_recent_1m = eps_values[ticker].iloc[date_idx - trend_period_1m:date_idx].astype(
                        float).dropna()
                    if len(eps_recent_3m) >= 2 and len(eps_recent_1m) > 2:
                        eps_slope_3m = np.polyfit(np.arange(len(eps_recent_3m)), eps_recent_3m.values, 1)[0]
                        eps_slope_1m = np.polyfit(np.arange(len(eps_recent_1m)), eps_recent_1m.values, 1)[0]

                        # 추가 조건
                        if eps_slope_3m < 0 and eps_slope_1m > 0.005:
                            eps_score += 3.0

                        #if eps_slope_3m < eps_slope_1m:
                        #    eps_score += 0.25

                        if eps_slope_3m > 0.015:
                            eps_score += 1.0

                        # 첫 번째 조건을 만족하지 않는 경우에만 추가 조건 적용
                        if eps_growth[i] < 0 and eps_slope_1m > 0.005:
                            eps_score += 0.25

                    # Sales 성장률 추세 분석
                    sales_recent_3m = sales_values[ticker].iloc[date_idx - trend_period_3m:date_idx].astype(
                        float).dropna()
                    sales_recnet_1m = sales_values[ticker].iloc[date_idx - trend_period_1m:date_idx].astype(
                        float).dropna()
                    if len(sales_recent_3m) >= 2 and len(sales_recnet_1m) >= 2:
                        sales_slope_3m = np.polyfit(np.arange(len(sales_recent_3m)), sales_recent_3m.values, 1)[0]
                        sales_slope_1m = np.polyfit(np.arange(len(sales_recnet_1m)), sales_recnet_1m.values, 1)[0]

                        # 첫 번째 조건
                        if sales_slope_3m < 0 and sales_slope_1m > 0.005:
                            sales_score += 2.0

                        #if sales_slope_3m < sales_slope_1m :
                        #    sales_score += 0.25

                        if sales_slope_3m > 0.015:
                            sales_score += 0.5

                        # 첫 번째 조건을 만족하지 않는 경우에만 추가 조건 적용
                        if sales_growth[i] < 0 and sales_slope_1m > 0.005:
                            sales_score += 0.25  # 펀더멘털 값을 0으로 설정

                    # Revision Ratio 추세 분석
                    #revision_recent_3m = revision_values[ticker].iloc[date_idx - trend_period_3m:date_idx].astype(
                    #    float).dropna()
                    #revision_recent_1m = revision_values[ticker].iloc[date_idx - trend_period_1m:date_idx].astype(
                    #    float).dropna()
                    #revision_last_value = revision_last[ticker].iloc[date_idx]
                    #if len(revision_recent_3m) >= 2 and len(revision_recent_1m) >= 2:
                    #    revision_slope_3m = \
                    #        np.polyfit(np.arange(len(revision_recent_3m)), revision_recent_3m.values, 1)[0]
                    #    revision_slope_1m = \
                    #        np.polyfit(np.arange(len(revision_recent_1m)), revision_recent_1m.values, 1)[0]

                    #    if revision_slope_3m < 0 and revision_slope_1m > 0.005:
                    #        revision_score += 2.5

                    #    if revision_slope_3m > 0.02:
                    #        revision_score += 1.0

                    #    if revision_slope_3m < -0.02:
                    #        revision_score -= 0.5

                        #if revision_slope_3m < revision_slope_1m and revision_slope_1m > 0.025:
                        #    revision_score += 0.5

                    #    if revision_ratio[i] < 0 and revision_slope_1m > 0.005:
                    #       revision_score += 0.25

                    #    if revision_last_value >= 65:
                    #        revision_score += 0.25

                    #    if revision_last_value >= 85:
                    #        revision_score += 0.25

                    #    if revision_last_value < -75:
                    #        revision_score -= 0.25

                    # Fcf growth Ratio 추세 분석
                    fcf_recent_3m = fcf_values[ticker].iloc[date_idx - trend_period_3m:date_idx].astype(
                        float).dropna()
                    fcf_recnet_1m = fcf_values[ticker].iloc[date_idx - trend_period_1m:date_idx].astype(
                        float).dropna()
                    if len(fcf_recent_3m) >= 2 and len(fcf_recnet_1m) >= 2:
                        fcf_slope_3m = np.polyfit(np.arange(len(fcf_recent_3m)), fcf_recent_3m.values, 1)[0]
                        fcf_slope_1m = np.polyfit(np.arange(len(fcf_recnet_1m)), fcf_recnet_1m.values, 1)[0]

                        # 첫 번째 조건
                        if fcf_slope_3m < 0 and fcf_slope_1m > 0.005:
                            fcf_score += 2.0

                        #if sales_slope_3m < sales_slope_1m :
                        #    sales_score += 0.25

                        if fcf_slope_3m > 0.015:
                            fcf_score += 0.5

                        # 첫 번째 조건을 만족하지 않는 경우에만 추가 조건 적용
                        if fcf_growth[i] < 0 and fcf_slope_1m > 0.005:
                            fcf_score += 0.25  # 펀더멘털 값을 0으로 설정

                    # 12개월 모멘텀 추세 분석
                    mom_12m_recent_3m = momentum_12m_values[ticker].iloc[
                                        date_idx - trend_period_3m:date_idx].astype(float).dropna()
                    mom_12m_recent_1m = momentum_12m_values[ticker].iloc[
                                        date_idx - trend_period_1m:date_idx].astype(float).dropna()
                    if len(mom_12m_recent_3m) >= 2 and len(mom_12m_recent_1m) >= 2:
                        mom_12m_slope_3m = \
                            np.polyfit(np.arange(len(mom_12m_recent_3m)), mom_12m_recent_3m.values, 1)[0]
                        mom_12m_slope_1m = \
                            np.polyfit(np.arange(len(mom_12m_recent_1m)), mom_12m_recent_1m.values, 1)[0]

                        if mom_12m_slope_3m < 0 and mom_12m_slope_1m > 0.005:
                            mom_12m_score += 2.0

                        if mom_12m_slope_3m > 0.01:
                            mom_12m_score += 0.25

                        # if mom_12m_slope_3m < -0.01:
                        #    mom_12m_score -= 0.25

                        # if mom_12m_slope_1m > 0.005:
                        #    mom_12m_score += 0.25

                        if mom_12m_slope_3m < mom_12m_slope_1m and mom_12m_slope_1m > 0.01:
                            mom_12m_score += 0.250

                        #if mom_12m_rank[i] < 0 and mom_12m_slope_1m > 0:
                        #    mom_12m_score += 0.25

                    # 3개월 모멘텀 추세 분석
                    mom_3m_recent_3m = momentum_3m_values[ticker].iloc[date_idx - trend_period_3m:date_idx].astype(
                        float).dropna()
                    mom_3m_recent_1m = momentum_3m_values[ticker].iloc[date_idx - trend_period_1m:date_idx].astype(
                        float).dropna()
                    if len(mom_3m_recent_3m) >= 2 and len(mom_3m_recent_1m) >= 2:
                        mom_3m_slope_3m = np.polyfit(np.arange(len(mom_3m_recent_3m)), mom_3m_recent_3m.values, 1)[
                            0]
                        mom_3m_slope_1m = np.polyfit(np.arange(len(mom_3m_recent_1m)), mom_3m_recent_1m.values, 1)[
                            0]

                        if mom_3m_slope_3m < 0 and mom_3m_slope_1m > 0.005:
                            mom_3m_score += 2.0  # 가점 부여

                        if mom_3m_slope_3m > 0.01:
                            mom_3m_score += 0.25

                        # if mom_3m_slope_3m < -0.01:
                        #    mom_3m_score -= 0.25

                        # if mom_3m_slope_1m > 0.005:
                        #    mom_3m_score += 0.25

                        if mom_3m_slope_3m < mom_3m_slope_1m and mom_3m_slope_1m > 0.01:
                            mom_3m_score += 0.25

                        #if mom_3m_rank[i] < 0 and mom_3m_slope_1m > 0:
                        #    mom_3m_score += 0.250

                    # 팩터 스코어 업데이트
                    factor_scores['eps_growth'].loc[date, ticker] = eps_score
                    factor_scores['sales_growth'].loc[date, ticker] = sales_score
                    #factor_scores['revision_ratio'].loc[date, ticker] = revision_score
                    factor_scores['fcf_growth'].loc[date, ticker] = fcf_score
                    factor_scores['mom_12m'].loc[date, ticker] = mom_12m_score
                    factor_scores['mom_3m'].loc[date, ticker] = mom_3m_score

                    # total_score 업데이트
                    total_score[ticker] = (
                            eps_score +
                            sales_score +
                            #revision_score +
                            fcf_score + mom_12m_score + mom_3m_score
                    )
            else:
                # 충분한 데이터가 없는 경우, 가산점 없이 현재 팩터 스코어로 진행
                for i, ticker in enumerate(st_list):
                    # 팩터 스코어는 이미 위에서 초기화되었으므로 추가 작업 필요 없음
                    pass  # 아무 작업도 하지 않음

            # 스코어 저장
            scores.loc[date] = total_score

        else:
            # 펀더멘털 데이터가 없는 경우, 모든 팩터 스코어와 total_score를 이전 값으로 설정
            if date_idx > 0:
                scores.loc[date] = scores.iloc[date_idx - 1]
                for factor in factor_scores:
                    factor_scores[factor].loc[date] = factor_scores[factor].iloc[date_idx - 1]
            else:
                # 초기 날짜의 경우 0으로 설정
                scores.loc[date] = np.zeros(len(st_list))
                for factor in factor_scores:
                    factor_scores[factor].loc[date] = np.zeros(len(st_list))

        # 리밸런싱 날짜인 경우 포트폴리오 비중 계산
        if date in rebalance_dates:

            # 'date' 컬럼을 인덱스로 설정합니다.
            #manual_scores_df.set_index('date', inplace=True)
            Re_dates = pd.DataFrame(rebalance_dates, columns = ['date'])
            manual_scores_df_tbl = Re_dates.merge(manual_scores_df, on = 'date', how = 'left').fillna(0).set_index('date')

            # 임의의 가산점 적용
            if date in manual_scores_df_tbl.index:
                manual_scores_today = manual_scores_df_tbl.loc[date]

                manual_scores_dict = manual_scores_today.to_dict()

                # factor_scores['p_s']
                for ticker, score in manual_scores_dict.items():
                    if ticker in st_list:
                        factor_scores['p_s'].loc[date, ticker] = score

            # total_score를 각 팩터 스코어의 합으로 계산합니다.
            total_score = (
                factor_scores['eps_growth'].loc[date].astype(float)
                + factor_scores['sales_growth'].loc[date].astype(float)
            #    + factor_scores['revision_ratio'].loc[date].astype(float)
                + factor_scores['fcf_growth'].loc[date].astype(float)
                + factor_scores['mom_12m'].loc[date].astype(float)
                + factor_scores['mom_3m'].loc[date].astype(float)
                + factor_scores['p_s'].loc[date].astype(float).fillna(0)  # 'p_s' 항목 포함
            )

            # 스코어 저장
            scores.loc[date] = total_score


            # 벤치마크 포트폴리오: 동일 비중
            benchmark_weight = pd.Series(1 / len(st_list), index=st_list)

            # 실제 포트폴리오 구성
            # 기대 수익률 추정 (스코어를 기반으로)
            expected_returns = scores.loc[date].astype(float)
            expected_returns = expected_returns - expected_returns.min()
            if expected_returns.max() >0 :
                expected_returns = expected_returns / expected_returns.max()

            # 과거 252일 수익률로 공분산 행렬 계산 (데이터가 충분한 경우)
            if date_idx >= 252:
                historical_returns = daily_returns.iloc[date_idx - 252:date_idx]
            else:
                historical_returns = daily_returns.iloc[:date_idx]

            # historical_returns의 차원 확인
            print(f"Date: {date}, historical_returns shape: {historical_returns.shape}")

            # 공분산 행렬 계산
            cov_matrix = calculate_ewma_covariance(historical_returns, span=252)

            # cov_matrix의 차원 확인
            print(f"Date: {date}, cov_matrix shape: {cov_matrix.shape}")

            # cov_matrix에 NaN 값이 있으면 0으로 대체
            cov_matrix = np.nan_to_num(cov_matrix)

            # 변수정의
            w = cp.Variable(len(st_list))
            benchmark_w = benchmark_weight.values  # 수정된 부분

            # 트래킹 에러 한도 설정 (연간 기준을 일간으로 변환)
            TE_limit_annual = 0.075
            TE_limit_daily = TE_limit_annual / np.sqrt(252)

            # 목적 함수: 기대 수익률 최대화
            objective = cp.Maximize(expected_returns.values @ w)
            risk_aversion = 1
            #objective = cp.Maximize(expected_returns.values @ w - risk_aversion * cp.quad_form(w, cov_matrix))

            # 트래킹 에러 계산을 위한 표현식
            tracking_error = cp.quad_form(w - benchmark_w, cov_matrix)

            # 포트폴리오 변동성 계산을 위한 표현식
            portfolio_variance = cp.quad_form(w, cov_matrix)

            # 제약 조건 리스트 초기화
            constraints = []

            # 턴오버 제약 조건 추가
            prev_weights = prev_actual_weight.values
            turnover_limit = 0.30
            #constraints += [cp.norm(w - prev_weights, 1) <= turnover_limit]

            # 개별 자산의 최대 비중 제한 설정
            max_weight = 0.50
            min_weight = -0.40
            #constraints += [w <= max_weight]

            bm7p_index = st_list.index('BM7P Index')

            # 제약조건
            constraints += [
                cp.sum(w) == 0,  # 총 비중의 합이 0이 되도록 설정
                w >= min_weight,  # 각 자산의 최소 비중 설정 (공매도 허용)
                w <= max_weight,  # 각 자산의 최대 비중 설정
                w[bm7p_index] >= 0,
                w[bm7p_index] <= 0.10,
                #tracking_error <= TE_limit_daily ** 2
                portfolio_variance <= 0.10 ** 2
            ]


            # 최적화 문제 정의 및 해결
            prob = cp.Problem(objective, constraints)
            prob.solve(solver=cp.ECOS, max_iters=10000, verbose=True)

            # 결과 저장
            if w.value is not None:
                actual_weight = pd.Series(w.value, index=st_list)
            else:
                # 최적화 실패 시 이전 비중 사용
                actual_weight = prev_actual_weight

            # 거래비용 계산
            # 벤치마크 포트폴리오 거래비용
            benchmark_trading = np.abs(benchmark_weight - prev_benchmark_weight)
            benchmark_cost = (benchmark_trading * transaction_cost_rate).sum()
            benchmark_transaction_costs.loc[date] = benchmark_cost

            # 실제 포트폴리오 거래비용
            actual_trading = np.abs(actual_weight - prev_actual_weight)
            actual_cost = (actual_trading * transaction_cost_rate).sum()
            actual_transaction_costs.loc[date] = actual_cost

            # 이전 비중 업데이트
            prev_benchmark_weight = benchmark_weight
            prev_actual_weight = actual_weight

            # For the overlay portfolio, we start with actual_weight
            actual_weight_overlay = actual_weight.copy()
            actual_weight_eps_overlay = actual_weight.copy()
            # For the combined overlay portfolio, start with actual_weight
            actual_weight_combined_overlay = actual_weight.copy()

            # Identify the top 3 stocks based on 3month momentum
            if date in momentum_63d_raw.index:
                # Get the momentum values
                momentum_values = momentum_63d_raw.loc[date]

                # Ensure momentum_values is a Series with index as stock tickers
                if not isinstance(momentum_values, pd.Series):
                    momentum_values = pd.Series(momentum_values, index=st_list)


                # Sort stocks by momentym in descending order
                top3_stocks = momentum_values.sort_values(ascending=False).head(3).index.tolist()

                # Weights to overlay
                overlay_weights_values = [0.025, 0.015, 0.01]

                # Multiply all weights by 0.95
                #actual_weight_overlay *= 0.95

                # Add overlay weights to top 3 stocks
                for stock, overlay_weight in zip(top3_stocks, overlay_weights_values):
                    actual_weight_overlay[stock] += overlay_weight
                    # Store the overlayed weight
                    overlay_weights_df.loc[date, stock] = overlay_weight

                # Ensure weights sum to 1
                # actual_weight_overlay /= actual_weight_overlay.sum()
            else:
                pass

            # Compute transaction costs for overlay portfollio
            actual_trading_overlay = np.abs(actual_weight_overlay - prev_actual_weight_overlay)
            actual_cost_overlay = (actual_trading_overlay * transaction_cost_rate).sum()
            actual_transaction_costs_overlay.loc[date] = actual_cost_overlay

            # Update previous weights
            prev_actual_weight_overlay = actual_weight_overlay


            # Identify the top 3 stocks based on 3months forward EPS Growth
            if date in us_eps_fwd_3m.index:
                # Get the EPS growth values for the date
                eps_growth_values = us_eps_fwd_3m.loc[date]

                # Ensure that eps_growth_values is a Series with stock tickers as index
                if not isinstance(eps_growth_values, pd.Series):
                    eps_growth_values = pd.Series(eps_growth_values, index=st_list)

                # Drop Nan Values
                eps_growth_values = eps_growth_values.dropna()

                # Sort stocks by EPS growth is descending order and get the top 3 tickers
                top3_stocks = eps_growth_values.sort_values(ascending=False).head(3).index.tolist()

                # Weights to overlay
                overlay_weights_values = [0.025,0.015,0.01]
                #actual_weight_eps_overlay *= 0.95

                # Add overlay weights to top 3 stocks
                for i, stock in enumerate(top3_stocks):
                    eps_overlay_weight = overlay_weights_values[i]
                    actual_weight_eps_overlay[stock] += eps_overlay_weight
                    # Store the overlayed weight
                    eps_overlay_weights_df.loc[date, stock] = eps_overlay_weight

                # Ensure weights sum to 1
                #actual_weight_eps_overlay /= actual_weight_eps_overlay.sum()
            else:
                pass

            # Comppute transaction costs for overlay portfolio
            actual_trading_eps_overlay = np.abs(actual_weight_eps_overlay - prev_actual_weight_eps_overlay)
            actual_cost_eps_overlay = (actual_trading_eps_overlay * transaction_cost_rate).sum()
            actual_transaction_costs_eps_overlay.loc[date] = actual_cost_eps_overlay

            # Update previous weights
            prev_actual_weight_eps_overlay = actual_weight_eps_overlay



            # Reduce base portfolio weight to 90%
            #actual_weight_combined_overlay *= 0.90

            # Initialize variables to store overlay weights for EPS and Momentum
            overlay_weights_eps = pd.Series(0, index=st_list)
            overlay_weights_momentum = pd.Series(0, index=st_list)

            # Momentum Overlay
            if date in momentum_63d_raw.index:
                # Get the momentum values
                momentum_values = momentum_63d_raw.loc[date]

                # Ensure that momentum_value is a Series with stock tickers as index
                if not isinstance(momentum_values, pd.Series):
                    momentum_values = pd.Series(momentum_values, index=st_list)

                # Drop Nan Values
                momentum_values = momentum_values.dropna()

                # Sort stocks by momentum in descending order and get the top 3 tickers
                top3_momentum_stocks = momentum_values.sort_values(ascending=False).head(3).index.tolist()

                # Weights to overlay for momentum
                overlay_weights_momentum_values = [0.025,0.015,0.01]

                # Add overlay weights to top 3 momentum stocks
                for i, stock in enumerate(top3_momentum_stocks):
                    overlay_weight = overlay_weights_momentum_values[i]
                    actual_weight_combined_overlay[stock] += overlay_weight
                    overlay_weights_combined_df.loc[date, stock] += overlay_weight # Accumulate overlay weights
                    overlay_weights_momentum_combined_df.loc[date, stock] += overlay_weight

            # EPS Overlay
            if date in us_eps_fwd_3m.index:
                # Get the EPS growth values for the date
                eps_growth_values = us_eps_fwd_3m.loc[date]

                # Ensure that eps_growth_Values is a Series with stock tickers as index
                if not isinstance(eps_growth_values,  pd.Series):
                    eps_growth_values = pd.Series(eps_growth_values, index=st_list)

                # Drop NaN Values
                eps_growth_values = eps_growth_values.dropna()

                # Sore stocks by EPS growth in descending order and get the top 3 tickers
                top3_eps_stocks = eps_growth_values.sort_values(ascending=False).head(3).index.to_list()

                # Weights to overlay for EPS
                overlay_weights_eps_values = [0.025, 0.015, 0.01]

                # Add overlay weights to top 3 EPS growth stocks
                for i, stock in enumerate(top3_eps_stocks):
                    overlay_weight = overlay_weights_eps_values[i]
                    actual_weight_combined_overlay[stock] += overlay_weight
                    overlay_weights_combined_df.loc[date, stock] += overlay_weight
                    overlay_weights_eps_combined_df.loc[date, stock] += overlay_weight

            # Ensure weights sum to 1
            #actual_weight_combined_overlay /= actual_weight_combined_overlay.sum()

            # Compute transaction costs for combined overlay portfolio
            actual_trading_combined_overlay = np.abs(actual_weight_combined_overlay - prev_actual_weight_combined_overlay)
            actual_cost_combined_overlay = (actual_trading_combined_overlay * transaction_cost_rate).sum()
            actual_transaction_costs_combined_overlay.loc[date] = actual_cost_combined_overlay

            # Update previous weights
            prev_actual_weight_combined_overlay = actual_weight_combined_overlay

            # ======== Growth Portfolio===================
            total_score_growth = (
                factor_scores['eps_growth'].loc[date].astype(float)
                + factor_scores['sales_growth'].loc[date].astype(float)
                + factor_scores['fcf_growth'].loc[date].astype(float)
                #+ factor_scores['revision_sales'].loc[date].astype(float)
            )

            # Normalize the scores
            expected_returns_growth = total_score_growth - total_score_growth.min()
            if expected_returns_growth.max() > 0:
                expected_returns_growth = expected_returns_growth / expected_returns_growth.max()

            # Optimize the growth portfolio
            w_growth = cp.Variable(len(st_list))
            objective_growth = cp.Maximize(expected_returns_growth.values @ w_growth)

            max_weight = 0.50
            min_weight = -0.40

            # 포트폴리오 변동성 계산을 위한 표현식
            portfolio_variance = cp.quad_form(w_growth, cov_matrix)

            bm7p_index = st_list.index('BM7P Index')

            # Constraints
            constraints_growth = [
                cp.sum(w_growth) == 0,
                #w_growth >= 0,
                w_growth <= max_weight,
                w_growth >= min_weight,
                w_growth[bm7p_index] <= 0.1,
                w_growth[bm7p_index] >= 0,

                #cp.norm(w_growth - prev_actual_weight_growth.values, 1) <= turnover_limit,
                portfolio_variance <= 0.10 ** 2
            ]


            # Solve the optimization problem
            prob_growth = cp.Problem(objective_growth, constraints_growth)
            prob_growth.solve(solver=cp.ECOS, max_iters=10000, verbose=False)

            # Store the weights
            if w_growth.value is not None:
                actual_weight_growth = pd.Series(w_growth.value, index=st_list)
            else:
                actual_weight_growth = prev_actual_weight_growth

            # Compute transaction costs
            actual_trading_growth = np.abs(actual_weight_growth - prev_actual_weight_growth)
            actual_cost_growth = (actual_trading_growth * transaction_cost_rate).sum()
            actual_transaction_costs_growth.loc[date] = actual_cost_growth

            # Update previous weights
            prev_actual_weight_growth = actual_weight_growth


            #==================Momentum Portfolio=============================

            # Calculate total_score_momentum using momentum factors
            total_score_momentum = (
                factor_scores['mom_12m'].loc[date].astype(float)
                + factor_scores['mom_3m'].loc[date].astype(float)
            )

            # Normalize the scores
            expected_returns_momentum = total_score_momentum - total_score_momentum.min()
            if expected_returns_momentum.max() > 0:
                expected_returns_momentum = expected_returns_momentum / expected_returns_momentum.max()

            # Optimize the momentum portfolio
            w_momentum = cp.Variable(len(st_list))
            objective_momentum = cp.Maximize(expected_returns_momentum.values @ w_momentum)

            # 포트폴리오 변동성 계산을 위한 표현식
            portfolio_variance = cp.quad_form(w_momentum, cov_matrix)
            bm7p_index = st_list.index('BM7P Index')

            # Constraints
            constraints_momentum = [
                cp.sum(w_momentum) == 0,
                #w_momentum >= 0,
                w_momentum <= max_weight,
                w_momentum >= min_weight,
                w_momentum[bm7p_index] >= 0,
                w_momentum[bm7p_index] <= 0.10,
                #cp.norm(w_momentum - prev_actual_weight_momentum.values, 1) <= turnover_limit,
                portfolio_variance <= 0.10 ** 2
            ]


            # Solve the optimization problem
            prob_momentum = cp.Problem(objective_momentum, constraints_momentum)
            prob_momentum.solve(solver = cp.ECOS, max_iters=10000, verbose=False)

            # Store the weights
            if w_momentum.value is not None:
                actual_weight_momentum = pd.Series(w_momentum.value, index=st_list)
            else:
                actual_weight_momentum = prev_actual_weight_momentum


            # Compute transaction costs
            actual_trading_momentum = np.abs(actual_weight_momentum - prev_actual_weight_momentum)
            actual_cost_momentum = (actual_trading_growth * transaction_cost_rate).sum()
            actual_transaction_costs_momentum.loc[date] = actual_cost_momentum

            # Update previous weights
            prev_actual_weight_momentum = actual_weight_momentum


        else:
            # 리밸런싱 날짜가 아닌 경우
            # 벤치마크 포트폴리오 비중 업데이트: 전일 비중과 수익률을 반영
            benchmark_weight = prev_benchmark_weight * (1 + daily_returns.loc[date])
            benchmark_weight = benchmark_weight / benchmark_weight.sum()
            prev_benchmark_weight = benchmark_weight

            # 실제 포트폴리오 비중 업데이트: 전일 비중과 수익률을 반영
            actual_weight = prev_actual_weight * (1 + daily_returns.loc[date])
            actual_weight = actual_weight / (actual_weight.sum()+1)
            prev_actual_weight = actual_weight

            # 거래비용 없음
            benchmark_transaction_costs.loc[date] = 0
            actual_transaction_costs.loc[date] = 0

            # On non-rebalancing dates, update weights based on returns
            actual_weight_overlay = prev_actual_weight_overlay * (1+daily_returns.loc[date])
            actual_weight_overlay = actual_weight_overlay / (actual_weight_overlay.sum()+1)
            prev_actual_weight_overlay = actual_weight_overlay

            # No transaction cost
            actual_transaction_costs_overlay.loc[date] = 0

            actual_weight_eps_overlay = prev_actual_weight_overlay * (1 + daily_returns.loc[date])
            actual_weight_eps_overlay = actual_weight_eps_overlay / (actual_weight_eps_overlay.sum()+1)
            prev_actual_weight_eps_overlay = actual_weight_eps_overlay

            # No transaction cost in eps overlay
            actual_transaction_costs_eps_overlay.loc[date] = 0

            actual_weight_combined_overlay = prev_actual_weight_combined_overlay * (1 + daily_returns.loc[date])
            actual_weight_combined_overlay = actual_weight_combined_overlay / (1+actual_weight_combined_overlay.sum())
            prev_actual_weight_combined_overlay = actual_weight_combined_overlay

            actual_transaction_costs_combined_overlay.loc[date] = 0

            # Update Growth Portfolio weights based on reutrns
            actual_weight_growth = prev_actual_weight_growth * (1+ daily_returns.loc[date])
            actual_weight_growth = actual_weight_growth / (actual_weight_growth.sum()+1)
            prev_actual_weight_growth = actual_weight_growth

            # No transaction cost
            actual_transaction_costs_growth.loc[date] = 0

            # Update Momentum Portfolio weights based on weights
            actual_weight_momentum = prev_actual_weight_momentum * (1+daily_returns.loc[date])
            actual_weight_momentum = actual_weight_momentum / (1+actual_weight_momentum.sum())
            prev_actual_weight_momentum =actual_weight_momentum

            # No transaction cost
            actual_transaction_costs_momentum.loc[date] = 0



        # 포트폴리오 비중 저장
        benchmark_weights.loc[date] = benchmark_weight
        actual_weights.loc[date] = actual_weight
        actual_weights_overlay.loc[date] = actual_weight_overlay
        actual_weights_eps_overlay.loc[date] = actual_weight_eps_overlay
        actual_weights_combined_overlay.loc[date] = actual_weight_combined_overlay
        actual_weights_growth.loc[date] = actual_weight_growth
        actual_weights_momentum.loc[date] = actual_weight_momentum

    # 포트폴리오 수익률 계산
    benchmark_portfolio_returns = (benchmark_weights.shift(1) * daily_returns.loc[dates]).sum(
        axis=1) - benchmark_transaction_costs
    actual_portfolio_returns = (actual_weights.shift(1) * daily_returns.loc[dates]).sum(
        axis=1) - actual_transaction_costs
    actual_portfolio_returns_overlay = (actual_weights_overlay.shift(1) * daily_returns.loc[dates]).sum(axis=1) - actual_transaction_costs_overlay
    actual_portfolio_returns_eps_overlay = (actual_weights_eps_overlay.shift(1) * daily_returns.loc[dates]).sum(axis=1) - actual_transaction_costs_eps_overlay
    actual_portfolio_returns_combined_overlay = (actual_weights_combined_overlay.shift(1) * daily_returns.loc[dates]).sum(axis=1) - actual_transaction_costs_combined_overlay
    actual_portfolio_returns_growth = ((actual_weights_growth.shift(1) * daily_returns.loc[dates]).sum(axis=1) - actual_transaction_costs_growth)
    actual_portfolio_returns_momentum = ((actual_weights_momentum.shift(1) * daily_returns.loc[dates]).sum(axis=1) - actual_transaction_costs_momentum)

    # 누적 수익률 계산
    benchmark_cum_returns = (1 + benchmark_portfolio_returns).cumprod() - 1
    actual_cum_returns = (1 + actual_portfolio_returns).cumprod() - 1
    spx_cum_returns = (1 + pr_res_bd[['SPX Index']].loc["2016-01-01":].pct_change(periods=1)).cumprod() - 1
    actual_cum_returns_overlay = (1 + actual_portfolio_returns_overlay).cumprod() - 1
    actual_cum_returns_eps_overlay = (1 + actual_portfolio_returns_eps_overlay).cumprod() - 1
    actual_cum_returns_combined_overlay = (1 + actual_portfolio_returns_combined_overlay).cumprod() -1
    actual_cum_returns_growth = (1 + actual_portfolio_returns_growth).cumprod() - 1
    actual_cum_returns_momentum = (1 + actual_portfolio_returns_momentum).cumprod() - 1


    # 성과 분해를 위한 데이터 계산
    # 각 자산의 기여도 계산
    benchmark_contributions = (benchmark_weights.shift(1) * daily_returns.loc[dates])
    actual_contributions = (actual_weights.shift(1) * daily_returns.loc[dates])

    # 스코어 순위 계산
    score_ranks = scores.rank(axis=1, ascending=False)

    # 연도별 성과 기여도 비교를 위한 데이터프레임 생성
    performance_decomposition = {}

    years = daily_returns.loc[dates].index.year.unique()

    for year in years:
        year_idx = daily_returns.loc[dates].index.year == year
        year_dates = daily_returns.loc[dates].index[year_idx]

        # 벤치마크 포트폴리오
        bm_contrib = benchmark_contributions.loc[year_dates].sum()
        # 실제 포트폴리오
        act_contrib = actual_contributions.loc[year_dates].sum()

        # 해당 연도의 평균 스코어 순위
        avg_ranks = score_ranks.loc[year_dates].mean().sort_values()

        # 상위, 중위, 하위 등수 그룹화 (등분할)
        num_stocks = len(st_list)
        tercile = num_stocks // 3

        high_rank = avg_ranks.index[:tercile]
        mid_rank = avg_ranks.index[tercile:2 * tercile]
        low_rank = avg_ranks.index[2 * tercile:]

        # 기여도 합산
        bm_high = bm_contrib[high_rank].sum()
        bm_mid = bm_contrib[mid_rank].sum()
        bm_low = bm_contrib[low_rank].sum()

        act_high = act_contrib[high_rank].sum()
        act_mid = act_contrib[mid_rank].sum()
        act_low = act_contrib[low_rank].sum()

        # 결과 저장
        performance_decomposition[year] = {
            'Benchmark_Top': bm_high,
            'Benchmark_Middle': bm_mid,
            'Benchmark_Bottom': bm_low,
            'Actual_Top': act_high,
            'Actual_Middle': act_mid,
            'Actual_Bottom': act_low
        }

    # 성과 분해 결과를 데이터프레임으로 변환
    performance_decomposition_df = pd.DataFrame(performance_decomposition).T

    # 최근 6개월의 월말 날짜 추출
    recent_6m_dates = rebalance_dates[-55:]

    # Monthly weights for overlay portfolio
    overlay_monthly_weights = actual_weights_overlay.loc[rebalance_dates]
    overlay_partial_weights = overlay_weights_df.loc[rebalance_dates]
    eps_overlay_monthly_weights = actual_weights_eps_overlay.loc[rebalance_dates]
    eps_overlay_partial_weights = eps_overlay_weights_df.loc[rebalance_dates]
    combined_overlay_monthly_weights = actual_weights_combined_overlay.loc[rebalance_dates]
    combined_overlay_partial_weights = overlay_weights_combined_df.loc[rebalance_dates]
    combined_overlay_eps_weights = overlay_weights_eps_combined_df.loc[rebalance_dates]
    combined_overlay_momentum_weights = overlay_weights_momentum_combined_df.loc[rebalance_dates]
    growth_weights = actual_weights_growth.loc[rebalance_dates]
    momentum_weights = actual_weights_momentum.loc[rebalance_dates]

    # 최근 6개월의 실제 포트폴리오 비중 추출
    recent_6m_weights = actual_weights.loc[recent_6m_dates]
    overlay_recent_3y_weights = overlay_monthly_weights.loc[recent_6m_dates]
    overlay_recent_partial_weights = overlay_partial_weights.loc[recent_6m_dates]
    eps_overlay_recent_3y_weights = eps_overlay_monthly_weights.loc[recent_6m_dates]
    eps_overlay_recent_partial_weights = eps_overlay_partial_weights.loc[recent_6m_dates]
    combined_overlay_recent_3y_weights = combined_overlay_monthly_weights.loc[recent_6m_dates]
    combined_overlay_recent_partial_weights = combined_overlay_partial_weights.loc[recent_6m_dates]
    combined_overlay_recent_eps_weights = combined_overlay_eps_weights.loc[recent_6m_dates]
    combined_overlay_recent_momentum_weights = combined_overlay_momentum_weights.loc[recent_6m_dates]
    growth_3y_weights = growth_weights.loc[recent_6m_dates]
    momentum_3y_weights = momentum_weights.loc[recent_6m_dates]

    # 일별 포트폴리오 수익률 차이 계산

    #return_diff = actual_portfolio_returns - benchmark_portfolio_returns
    #return_diff_overlay = actual_portfolio_returns_overlay - benchmark_portfolio_returns
    #return_diff_eps_overlay = actual_portfolio_returns_eps_overlay - benchmark_portfolio_returns
    #return_diff_combined_overlay = actual_portfolio_returns_combined_overlay - benchmark_portfolio_returns
    #return_diff_growth = actual_portfolio_returns_growth - benchmark_portfolio_returns
    #return_diff_momentum = actual_portfolio_returns_momentum - benchmark_portfolio_returns

    # 누적 트래킹 에러 계산 (연율화)
    #_daily = return_diff.rolling(window=252).std() * np.sqrt(252)
    #tracking_error_daily_overlay = return_diff_overlay.rolling(window=252).std() * np.sqrt(252)
    #tracking_error_daily_eps_overlay = return_diff_eps_overlay.rolling(window=252).std() * np.sqrt(252)
    #tracking_error_daily_combined_overlay = return_diff_combined_overlay.rolling(window=252).std() * np.sqrt(252)
    #tracking_error_daily_growth = return_diff_growth.rolling(window=252).std() * np.sqrt(252)
    #tracking_error_daily_momentum = return_diff_momentum.rolling(window=252).std() * np.sqrt(252)

    # Combine one Dataframe
    #tracking_error_df = pd.DataFrame({
    #    'Model' : tracking_error_daily,
    #    'Mom_Overlay': tracking_error_daily_overlay,
    #    'Eps_Overlay': tracking_error_daily_eps_overlay,
    #    'Combined_Overlay': tracking_error_daily_combined_overlay,
    #    'Growth': tracking_error_daily_growth,
    #    'Momentum': tracking_error_daily_momentum
    #})

    # 분기별 그룹화 및 리밸런싱 날짜 계산
    quarterly_group_stocks, quarterly_rebalance_dates = create_quarterly_group_stocks(score_ranks, daily_returns,
                                                                                      st_list)


    # 전체 팩터 디케이
    decay_total = calculate_factor_decay(scores, daily_returns, 63, rebalance_dates)

    # 개별 팩터에 대한 디케이 분석
    decay_factors = {}
    for factor_name, factor_data in factor_scores.items():
        decay = calculate_factor_decay(factor_data, daily_returns, 63, rebalance_dates)
        decay_factors[factor_name] = decay

    decay_factors_df = pd.DataFrame({factor_name: df['Mean_IC'] for factor_name, df in decay_factors.items()})
    decay_factors_df.index.name = 'Lag'

    #for factor_name, factor_data in factor_scores.items():
    #    factor_scores.fillna(0, inplace=True)
    # NaN 값을 0으로 대체

    # NaN 값을 0으로 대체
    for factor_name, df in factor_scores.items():
        df.fillna(0, inplace=True)

    #factor_scores = factor_scores.fillna(0)

    # 팩터 스코어와 일별 수익률을 사용하여 주간 IC 계산
    weekly_ic_df = calculate_weekly_ic(factor_scores, daily_returns, st_list)

    # 새로운 포트폴리오의 스코어 저장용 데이터프레임 초기화
    scores_new = pd.DataFrame(index=dates, columns=st_list)

    # 새로운 포트폴리오의 포트폴리오 비중 저장용 데이터프레임 초기화
    actual_weights_new = pd.DataFrame(index=dates, columns=st_list)

    # 새로운 포트폴리오의 이전 비중 초기화
    prev_actual_weight_new = pd.Series(1 / len(st_list), index=st_list)

    # 새로운 포트폴리오의 거래비용 저장용 시리즈 초기화
    actual_transaction_costs_new = pd.Series(0, index=dates)

    # 팩터 가중치 저장용 데이터프레임 초기화
    factor_weights = pd.DataFrame(index=dates, columns=factor_scores.keys())

    # `p_s` 팩터의 고정 가중치 설정
    p_s_weight = 1.0  # 원하는 고정 가중치 값으로 설정하십시오

    # 메인 루프
    for date_idx, date in tqdm(enumerate(dates), total=len(dates)):
        # 리밸런싱 날짜인 경우 팩터 가중치 계산 및 적용
        if date in rebalance_dates:
            # 해당 날짜의 가장 가까운 주간 IC 날짜 찾기
            ic_dates = weekly_ic_df.index[weekly_ic_df.index <= date]
            if len(ic_dates) == 0:
                continue
            ic_date = ic_dates[-1]

            # 지난 3개월간의 팩터별 IC의 시간 가중 평균값 계산
            ic_end_idx = weekly_ic_df.index.get_loc(ic_date)
            if ic_end_idx >= 12: # 주간 데이터이므로 약 12주가 3개월
                ic_window = weekly_ic_df.iloc[ic_end_idx - 12:ic_end_idx]
            else:
                ic_window = weekly_ic_df.iloc[:ic_end_idx]

            if len(ic_window) == 0:
                # 사용할 수 있는 IC 데이터가 없는 경우, 고정 가중치 사용
                factor_names = [factor for factor in factor_scores.keys() if factor != 'p_s']
                equal_weight = 1 / len(factor_names) # p_s팩터 제외하면 5개 팩터, 동일 비중 가정시 0.2씩
                factor_weight = pd.Series(equal_weight, index=factor_names)
            else:
                # 팩터 가중치 계산 (`p_s` 제외)
                factor_weight_df = calculate_factor_weights(ic_window, window=12)
                # p_s제외
                factor_weight = factor_weight_df.iloc[-1]

            # 팩터 가중치에 'p_s' 팩터 고정 가중치 추가
            factor_weight['p_s'] = p_s_weight
            factor_weights.loc[date] = factor_weight

            # 팩터 가중치를 적용해서 total_score_new 계산
            total_score_new = pd.Series(0, index=st_list, dtype=float)

            # 'p_s' 팩터 제외한 팩터들의 리스트
            factor_names = [factor for factor in factor_scores.keys() if factor != 'p_s']

            # 팩터 가중치를 적용하여 나머지 팩터들의 스코어를 합산
            for factor_name in factor_names:
                factor_score = factor_scores[factor_name].loc[date].astype(float)
                weight = factor_weight.get(factor_name,0)
                total_score_new += factor_score * weight


            # 스코어 저장
            scores_new.loc[date] = total_score_new

            # 실제 포트폴리오 구성 (새로운 포트폴리오)
            expected_returns_new = scores_new.loc[date].astype(float)
            expected_returns_new = expected_returns_new - expected_returns_new.min()
            if expected_returns_new.max() >0 :
                expected_returns_new = expected_returns_new / expected_returns_new.max()


            # 변수정의
            w_new = cp.Variable(len(st_list))
            benchmark_w = benchmark_weights.loc[date].values # 벤치마크 비중

            # 공분산 행렬 계산 추가
            if date_idx >= 252:
                historical_returns = daily_returns.iloc[date_idx - 252:date_idx]
            else:
                historical_returns = daily_returns.iloc[:date_idx]

            cov_matrix = calculate_ewma_covariance(historical_returns, span=65)
            cov_matrix = np.nan_to_num(cov_matrix)

            # 트레킹 에러 계산 위한 표현식
            tracking_error = cp.quad_form(w_new - benchmark_w, cov_matrix)

            # 목적 함수: 기대 수익률 최대화
            objective_new = cp.Maximize(expected_returns_new.values @ w_new)
            risk_aversion = 1  # 리스크 회피 계수 설정
            #objective_new = cp.Maximize(expected_returns_new.values @ w_new - risk_aversion * cp.quad_form(w_new, cov_matrix))

            # 제약 조건 리스트 초기화
            constraints_new = []

            # 포트폴리오 변동성 계산을 위한 표현식
            portfolio_variance = cp.quad_form(w_new, cov_matrix)

            # 턴오버 제약 조건 추가
            prev_weights = prev_actual_weight_new
            turnover_limit = 0.30
            #constraints_new += [cp.norm(w_new - prev_weights, 1) <= turnover_limit]


            bm7p_index = st_list.index('BM7P Index')


            # 개별 자산의 최대 비중 제한 설정
            max_weight = 0.50
            min_weight = -0.40

            constraints_new += [
                cp.sum(w) == 0,  # 총 비중의 합이 0이 되도록 설정
                w_new >= min_weight,  # 각 자산의 최소 비중 설정 (공매도 허용)
                w_new <= max_weight,  # 각 자산의 최대 비중 설정
                w_new[bm7p_index] >= 0,
                w_new[bm7p_index] <= 0.10,
                portfolio_variance <= 0.10 ** 2  # 포트폴리오 변동성을 10%로 제한
            ]

            # 최적화 문제 정의 및 해결
            prob_new = cp.Problem(objective_new, constraints_new)
            prob_new.solve(solver=cp.ECOS, max_iters=10000, verbose=False)

            # 결과 저장
            if w_new.value is not None:
                actual_weight_new = pd.Series(w_new.value, index=st_list)
            else:
                # 최적화 실패 시 이전 비중 사용
                actual_weight_new = prev_actual_weight_new

            # 거래비용 계산
            actual_trading_new = np.abs(actual_weight_new - prev_actual_weight_new)
            actual_cost_new = (actual_trading_new * transaction_cost_rate).sum()
            actual_transaction_costs_new.loc[date] = actual_cost_new

            # 이전 비중 업데이트
            prev_actual_weight_new = actual_weight_new

        else:
            # 리밸런싱 날짜가 아닌 경우
            # 새로운 포트폴리오 비중 업데이트
            actual_weight_new = prev_actual_weight_new * (1 + daily_returns.loc[date])
            actual_weight_new = actual_weight_new / (actual_weight_new.sum()+1)
            prev_actual_weight_new = actual_weight_new

            # 거래비용 없음
            actual_transaction_costs_new.loc[date] = 0

        # 포트폴리오 비중 저장
        actual_weights_new.loc[date] = actual_weight_new

    # 새로운 포트폴리오 수익률 계산
    actual_portfolio_returns_new = (actual_weights_new.shift(1) * daily_returns.loc[dates]).sum(axis=1) - actual_transaction_costs_new

    # 누적 수익률 계산
    actual_cum_returns_new = (1 + actual_portfolio_returns_new).cumprod()-1

    # 새로운 포트폴리오 기간별 수익률 계산
    new_portfolio_period_returns = calculate_period_returns(actual_cum_returns_new, periods_days.values())
    overlay_portfolio_period_returns = calculate_period_returns(actual_cum_returns_overlay, periods_days.values())
    eps_overlay_portfolio_period_returns = calculate_period_returns(actual_cum_returns_eps_overlay, periods_days.values())
    combined_overlay_portfolio_period_returns = calculate_period_returns(actual_cum_returns_combined_overlay, periods_days.values())
    growth_portfolio_period_returns = calculate_period_returns(actual_cum_returns_growth, periods_days.values())
    momentum_portfolio_period_returns = calculate_period_returns(actual_cum_returns_momentum, periods_days.values())

    # 기존 결과 데이터프레임에 새로운 포트폴리오 수익률 추가
    periods_labels = list(periods_days.keys())
    new_returns_list = [new_portfolio_period_returns[periods_days[label]] for label in periods_labels]
    overlay_returns_list = [overlay_portfolio_period_returns[periods_days[label]] for label in periods_labels]
    eps_overlay_returns_list = [eps_overlay_portfolio_period_returns[periods_days[label]] for label in periods_labels]
    combined_overlay_returns_list = [combined_overlay_portfolio_period_returns[periods_days[label]] for label in periods_labels]
    growth_returns_list = [growth_portfolio_period_returns[periods_days[label]] for label in periods_labels]
    momentum_returns_list = [momentum_portfolio_period_returns[periods_days[label]] for label in periods_labels]

    # IC 계산
    ic_df = calculate_ic(scores, daily_returns, rebalance_dates, st_list)

    # IC 계산 저장
    ic_df.to_csv(os.path.join(data_dir, 'ic_result.csv'))

    # 개별 팩터에 대한 IC 계산
    ic_results_factors = {}

    for factor_name, factor_data in factor_scores.items():
        ic_df_factor = calculate_ic(factor_data, daily_returns, rebalance_dates, st_list)
        ic_results_factors[factor_name] = ic_df_factor
        # 평균 IC 출력
        mean_ic = ic_df_factor['IC'].mean()
        print(f"Factor: {factor_name}, Mean IC: {mean_ic:.4f}")
        ic_df_factor.to_csv(os.path.join(data_dir, f'ic_results_{factor_name}.csv'))

    # 전체 포트폴리오에 대한 연도별 평균 IC 계산
    annual_ic_total = calculate_ic_annual(scores, daily_returns, rebalance_dates, st_list)
    annual_ic_total.to_csv(os.path.join(data_dir, 'annual_ic_total.csv'))

    # 개별 팩터에 대한 연도별 평균 IC 계산
    annual_ic_factors = {}

    for factor_name, factor_data in factor_scores.items():
        annual_ic = calculate_ic_annual(factor_data, daily_returns, rebalance_dates, st_list)
        annual_ic_factors[factor_name] = annual_ic

    # 연도별 팩터별 평균 IC를 데이터프레임으로 변환
    annual_ic_factors_df = pd.DataFrame(annual_ic_factors)
    annual_ic_factors_df = annual_ic_factors_df.fillna(0)
    annual_ic_factors_df.to_csv(os.path.join(data_dir, 'annual_ic_factors.csv'))


    # 기존 comparison_df에 새로운 포트폴리오 수익률 컬럼 추가
    actual_period_returns = calculate_period_returns(actual_cum_returns, periods_days.values())

    periods_labels = list(periods_days.keys())
    actual_returns_list = [actual_period_returns[periods_days[label]] for label in periods_labels]

    actual_returns_list = [actual_period_returns[periods_days[label]] for label in periods_labels]
    comparison_df = pd.DataFrame({
        'Periods' : periods_labels,
        'Actual Portfolio Return' : actual_returns_list
    #    'Benchmark Portfolio Return' : benchmark_returns_list
    })
    comparison_df['Actual Portfolio Return'] = comparison_df['Actual Portfolio Return'].apply(lambda x: f"{x * 100:.2f}%")

    comparison_df['New Portfolio Return'] = new_returns_list
    comparison_df['Mom Overlay Portfolio Return'] = overlay_returns_list
    comparison_df['EPS Overlay Portfolio Return'] = eps_overlay_returns_list
    comparison_df['Combined Overlay Portfolio Return'] = combined_overlay_returns_list
    comparison_df['Growth Portfolio Return'] = growth_returns_list
    comparison_df['Momentum Portfolio Return'] = momentum_returns_list
    comparison_df['New Portfolio Return'] = comparison_df['New Portfolio Return'].apply(lambda x: f"{x * 100:.2f}%")
    comparison_df['Mom Overlay Portfolio Return'] = comparison_df['Mom Overlay Portfolio Return'].apply(lambda x: f"{x * 100:.2f}%")
    comparison_df['EPS Overlay Portfolio Return'] = comparison_df['EPS Overlay Portfolio Return'].apply(lambda x:f"{x * 100:.2f}%")
    comparison_df['Combined Overlay Portfolio Return'] = comparison_df['Combined Overlay Portfolio Return'].apply(
        lambda x: f"{x * 100:.2f}%")
    comparison_df['Growth Portfolio Return'] = comparison_df['Growth Portfolio Return'].apply(
        lambda x: f"{x * 100:.2f}%")
    comparison_df['Momentum Portfolio Return'] = comparison_df['Momentum Portfolio Return'].apply(
        lambda x: f"{x * 100:.2f}%")


    # 포트폴리오별 지표 계산
    portfolios = {
        #'Benchmark' : benchmark_portfolio_returns,
        'Model' : actual_portfolio_returns,
        'Adaptive Model' : actual_portfolio_returns_new,
        'Mom Overlay Model' : actual_portfolio_returns_overlay,
        'EPS Overlay Model' : actual_portfolio_returns_eps_overlay,
        'Combined Overlay Model' : actual_portfolio_returns_combined_overlay,
        'Growth Portfolio' : actual_portfolio_returns_growth,
        'Momentum Portfolio' : actual_portfolio_returns_momentum

    }

    results = {}

    for name, returns in portfolios.items():
        annual_return = calculate_annualized_return(returns)
        annual_volatility = calculate_annualized_volatility(returns)
        annual_sharpe = annual_return / annual_volatility
        results[name] = {
            'Annualized Return' : annual_return,
            'Annualized Volatility' : annual_volatility,
            'Annualized Sharpe Ratio' : annual_sharpe
        #    'Annualized IC' : annual_ic,
        #    'Annualized IR' : annual_ir
        }

    # 결과를 데이터프레임으로 변환
    results_df = pd.DataFrame(results).T

    # 월별 팩터 조정 비율
    monthly_factor_weights = factor_weights.resample('M').last()

    # 연도별 수익률 계산
    actual_annual_returns = actual_portfolio_returns.groupby(actual_portfolio_returns.index.year).apply(
        lambda x: (1 + x).prod() - 1)

    actual_annual_returns_new = actual_portfolio_returns_new.groupby(actual_portfolio_returns_new.index.year).apply(
        lambda x: (1 + x).prod() -1)

    actual_annual_returns_overlay = actual_portfolio_returns_overlay.groupby(actual_portfolio_returns_overlay.index.year).apply(
        lambda x: (1 + x).prod() -1)
    actual_annual_returns_eps_overlay = actual_portfolio_returns_eps_overlay.groupby(actual_portfolio_returns_eps_overlay.index.year).apply(
        lambda x: (1 + x).prod() -1)
    actual_annual_returns_combined_overlay = actual_portfolio_returns_combined_overlay.groupby(actual_portfolio_returns_combined_overlay.index.year).apply(
        lambda x: (1 + x).prod()-1)
    actual_annual_returns_growth = actual_portfolio_returns_growth.groupby(actual_portfolio_returns_growth.index.year).apply(
        lambda x: (1 + x).prod()-1)
    actual_annual_returns_momentum = actual_portfolio_returns_momentum.groupby(actual_portfolio_returns_momentum.index.year).apply(
        lambda x: (1 + x).prod()-1)


    # 연도별 수익률 비교 테이블
    annual_returns = pd.DataFrame({
        #'Benchmark': benchmark_annual_returns,
        'Actual': actual_annual_returns,
        'Adaptive Actual' : actual_annual_returns_new,
        'Mom Overlay(5%)': actual_annual_returns_overlay,
        'EPS Overlay(5%)' : actual_annual_returns_eps_overlay,
        'Combined Pverlay(10%)' : actual_annual_returns_combined_overlay,
        'Growth' : actual_annual_returns_growth,
        'Momentum' : actual_annual_returns_momentum
    })


    # 필요한 데이터 저장
    #benchmark_cum_returns.to_csv(os.path.join(data_dir, 'benchmark_cum_returns.csv'))
    actual_cum_returns.to_csv(os.path.join(data_dir, 'actual_cum_returns.csv'))
    actual_cum_returns_new.to_csv(os.path.join(data_dir, 'actual_cum_returns_new.csv'))
    actual_cum_returns_overlay.to_csv(os.path.join(data_dir, 'actual_cum_returns_overlay.csv'))
    actual_cum_returns_eps_overlay.to_csv(os.path.join(data_dir, 'actual_cum_returns_eps_overlay.csv'))
    actual_cum_returns_combined_overlay.to_csv(os.path.join(data_dir,'actual_cum_returns_combined_overlay.csv'))
    actual_cum_returns_growth.to_csv(os.path.join(data_dir, 'actual_cum_returns_growth.csv'))
    actual_cum_returns_momentum.to_csv(os.path.join(data_dir, 'actual_cum_returns_momentum.csv'))
    annual_returns.to_csv(os.path.join(data_dir, 'annual_returns.csv'))
    performance_decomposition_df.to_csv(os.path.join(data_dir, 'performance_decomposition_df.csv'))
    recent_6m_weights.to_csv(os.path.join(data_dir, 'recent_6m_weights.csv'))
    overlay_recent_3y_weights.to_csv(os.path.join(data_dir, 'overlay_recent_3y_weights.csv'))
    eps_overlay_recent_3y_weights.to_csv(os.path.join(data_dir, 'eps_overlay_recent_3y_weights.csv'))
    overlay_recent_partial_weights.to_csv(os.path.join(data_dir, 'overlay_recent_partial_weights.csv'))
    eps_overlay_recent_partial_weights.to_csv(os.path.join(data_dir, 'eps_overlay_recent_partial_weights.csv'))
    combined_overlay_recent_3y_weights.to_csv(os.path.join(data_dir, 'combined_overlay_recent_3y_weights.csv'))
    combined_overlay_recent_partial_weights.to_csv(os.path.join(data_dir, 'combined_overlay_recent_partial_weights.csv'))
    combined_overlay_recent_eps_weights.to_csv(os.path.join(data_dir, 'combined_overlay_recent_eps_weights.csv'))
    combined_overlay_recent_momentum_weights.to_csv(os.path.join(data_dir, 'combined_overlay_recent_momentum_weights.csv'))
    growth_3y_weights.to_csv(os.path.join(data_dir, 'Growth_weights.csv'))
    momentum_3y_weights.to_csv(os.path.join(data_dir, 'Momentum_weights.csv'))
    #tracking_error_df.to_csv(os.path.join(data_dir, 'tracking_error_daily.csv'))
    #alpha_df.to_csv(os.path.join(data_dir, 'alpha_df.csv'))
    comparison_df.to_csv(os.path.join(data_dir, 'comparison_df.csv'))
    decay_total.to_csv(os.path.join(data_dir, 'decay_total.csv'))
    decay_factors_df.to_csv(os.path.join(data_dir, 'decay_factors_df.csv'))
    results_df.to_csv(os.path.join(data_dir,'results_df.csv'))
    monthly_factor_weights.to_csv(os.path.join(data_dir,'monthly_factor_weights.csv'))
    scores.to_csv(os.path.join(data_dir,'scores.csv'))


    # 데이터 저장
    with open(os.path.join(data_dir, 'quarterly_group_stocks.pkl'), 'wb') as f:
        pickle.dump(quarterly_group_stocks, f)

    with open(os.path.join(data_dir, 'quarterly_rebalance_dates.pkl'), 'wb') as f:
        pickle.dump(quarterly_rebalance_dates, f)

    # 각 요소별 스코어 저장
    with open(os.path.join(data_dir, 'factor_scores.pkl'), 'wb') as f:
        pickle.dump(factor_scores, f)

    print("Data processing completed and files are saved.")

    # 월별 그룹화 및 리밸런싱 날짜 계산
    monthly_group_stocks, monthly_rebalance_dates = create_monthly_group_stocks(score_ranks, daily_returns, st_list)

    # 데이터 저장
    with open(os.path.join(data_dir, 'monthly_group_stocks.pkl'), 'wb') as f:
        pickle.dump(monthly_group_stocks, f)

    with open(os.path.join(data_dir, 'monthly_rebalance_dates.pkl'), 'wb') as f:
        pickle.dump(monthly_rebalance_dates, f)



if __name__ == "__main__":
    main()

growth_factors = ['eps_growth', 'sales_growth', 'revision_ratio', 'revision_sales']
momentum_factors = ['mom_12m', 'mom_3m']

# 스코어 저쟝용 데이터프레임 추가
scores_growth = pd.DataFrame(index=dates, columns=st_list)
scores_mom = pd.DataFrame(index=dates, columns=st_list)

# Growth 팩터 포트폴리오 루프
for date_idx, date in tqdm(enumerate(dates), total=len(dates)):
    # 팩터 스코어 계산
    if date in us_eps_st_tbl.index:
        # 각 팩터별 스코어를 가져옵니다.
        for factor in growth_factors:
            factor_scores[factor].loc[date] = factor_scores[factor].loc[date].astype(float)
        # Total_score_growth 계산
        total_score_growth = sum(factor_scores[factor].loc[date] for factor in growth_factors)

        # 스코어 저장
        scores_growth.loc[date] = total_score_growth
    else:
        # 펀더멘털 데이터가 없는 경우
        if date_idx > 0:
            scores_growth.loc[date] = scores_growth.iloc[date_idx - 1]
        else:
            scores_growth.loc[date] = np.zeros(len(st_list))

for date_idx, date in tqdm(enumerate(dates), total=len(dates)):
    # 팩터 스코어 계산
    if date in us_eps_st_tbl.index:
        # 각 팩터별 스코어 가져오기
        for factor in momentum_factors:
            factor_scores[factor].loc[date] = factor_scores[factor].loc[date].astype(float)
        # total_score_mom 계산
        total_score_mom = sum(factor_scores[factor].loc[date] for factor in momentum_factors)

        # 스코어 저장
        scores_mom.loc[date] = total_score_mom
    else:
        # 펀더멘털 데이터가 없는 경우
        if date_idx > 0:
            scores_mom.loc[date] = scores_mom.iloc[date_idx - 1]
        else:
            scores_mom[date] = np.zeros(len(st_list))

def backtest_portfolio(expected_returns_series, daily_returns, rebalance_dates, st_list, initial_weights=None):
    # 포트폴리오 비중 저장용 데이터프레임 초기화
    weights = pd.Dataframe(index=dates, columns=st_list)

    # 이전 비중 초기화
    if initial_weights is None:
        prev_weights = pd.Series(1/len(st_list), index=st_list)
    else:
        prev_weights = initial_weights.copy()

    # 누적 거래비용 초기화
    transaction_costs = pd.Series(0, index=dates)

    # 메인 루프
    for date_idx, date in tqdm(enumerate(dates), total=len(dates)):
        # 리밸런싱 날짜인 경우 포트폴리오 비중 계산
        if date in rebalance_dates:
            # 기대수익률 추정(스코어 기반)
            expected_returns = expected_returns - expected_returns.min()
            if expected_returns.max() > 0:
                expected_returns = expected_returns / expected_returns.max()

            # 과거 252일 수익률로 공분산 행렬 계산
            if date_idx >= 252:
                historical_returns = daily_returns.iloc[date_idx - 252:date_idx]
            else:
                historical_returns = daily_returns.iloc[:date_idx]

            # 공분산 행렬 계산
            cov_matrix = calculate_ewma_covariance(historical_returns, span=63)
            cov_matrix = np.nan_to_num(cov_matrix)



plt.figure(figsize=(12,6))
plt.plot(benchmark_cum_returns.index, benchmark_cum_returns, label = 'Benchmark Portfolio')
plt.plot(actual_cum_returns.index, actual_cum_returns, label = 'Model Portfolio')
plt.plot(actual_cum_returns_new.index, actual_cum_returns_new, label = 'New Portfolio')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.title('Cumulative Returns Comparison')
plt.legend()
plt.grid(True)
plt.show()


# IC 시계열 그래프 그리기
plt.figure(figsize = (10,6))
plt.plot(annual_ic_total.index, annual_ic_total.values, marker = 'o', label = 'Total Score IC')
plt.axhline(y = 0, color = 'gray', linestyle = '--')
plt.title('Annual Average IC')
plt.xlabel*('Year')
plt.ylabel('Average IC')
plt.legend()
plt.grid(True)
plt.show()

# 팩터별 연도별 평균 IC 그래프
plt.figure(figsize=(12,6))
for factor_name in annual_ic_factors_df.columns:
    plt.plot(annual_ic_factors_df.index, annual_ic_factors_df[factor_name], marker = 'o', label = factor_name)
plt.axhline(y = 0, color = 'gray', linestyle = '--')
plt.title('Annual Average IC by Factor')
plt.xlabel('Year')
plt.ylabel('Average IC')
plt.legend()
plt.grid(True)
plt.show()


sns.set(style = "whitegrid")

#전체 팩터에 대한 디케이 그래프
plt.figure(figsize=(10,6))
plt.plot(decay_total.index, decay_total['Mean_IC'], marker = 'o', label='Total Score')
plt.title('Factor Decay - Total Score')
plt.xlabel('Lag (Days)')
plt.ylabel('Mean IC')
plt.legend()
plt.show()

plt.figure(figsize=(12, 6))
for factor_name, decay_df in decay_factors.items():
    plt.plot(decay_df.index, decay_df['Mean_IC'], marker='o', label=factor_name)
plt.title('Factor Decay by Factor')
plt.xlabel('Lag (Days)')
plt.ylabel('Mean IC')
plt.legend()
plt.show()


aaa = us_eps_uni_tbl['MSFT US Equity'].loc['2023-03-31':'2023-07-30'].astype(float).dropna()
aaa = us_revision_eq_tbl['MSFT US Equity'].iloc[-72:-9].astype(float).dropna()
aaa = us_revision_eq_tbl['NVDA US Equity'].loc['2022-04-30':'2022-08-30'].astype(float).dropna()


aaa = momentum_252d['NVDA US Equity'].iloc[-21:].astype(float).dropna()
momentum_63d['NVDA US Equity'].iloc[-21:].astype(float).dropna()
np.polyfit(np.arange(len(aaa)), aaa.values, 1)[0]

pr_st_tbl = pr_bd.merge(pr_res_bd[['date', 'SPX Index', 'NDX Index']], on='date', how='left').set_index('date')[
    st_list]

# 모멘텀 지표 계산 (12개월, 3개월 수익률을 일수로 변환하여 계산)
momentum_252 = pr_st_tbl.pct_change(252).shift(1)
momentum_63 = pr_st_tbl.pct_change(63).shift(1)

# 모멘텀 지표 표준화
momentum_252days = revision_growth(momentum_252, window1=0, window2=252 * 3)
momentum_63days = revision_growth(momentum_63, window1=0, window2=252 * 3)

bbb = momentum_252days['NVDA US Equity'].iloc[-63:].astype(float).dropna()
meta = momentum_63days['AMZN US Equity'].iloc[-73:-10].astype(float).dropna()
meta = momentum_252days['TSLA US Equity'].loc['2022-07-30':'2022-10-30'].astype(float).dropna()
meta = momentum_63days['NVDA US Equity'].loc['2022-08-30':'2022-09-30'].astype(float).dropna()


np.polyfit(np.arange(len(bbb)), bbb.values, 1)[0]
np.polyfit(np.arange(len(meta)), meta.values, 1)[0]

us_equity = eps_growth_nor(sales_uni_bd.set_index('date')[st_list].shift(1), 252, 252 * 3).fillna(0)
us_equity_slope = us_equity['MSFT US Equity'].iloc[-21:].astype(float).dropna()

np.polyfit(np.arange(len(us_equity_slope)), us_equity_slope.values, 1)[0]

momentum_63days['NVDA US Equity'].plot()
momentum_252days['NVDA US Equity'].plot()
