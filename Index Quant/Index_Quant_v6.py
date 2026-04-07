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
                      'SX5E Index', 'DAX Index', 'CAC Index','NKY Index','S5SFTW Index','S5TECH Index',	'S5SSEQX Index']


pr = pd.read_excel(oppor, sheet_name=0, parse_dates=True)
pr = pr[pr['date'] >= "2013-01-01"]
bd = pd.read_excel(Index, sheet_name=14, parse_dates=True)
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
#opm_us = pd.read_excel(oppor, sheet_name=8, parse_dates=True)
#opm_us = opm_us[opm_us['date'] >= "2013-01-01"]
#opm_us = opm_us.fillna(0)
#cap_us = pd.read_excel(oppor, sheet_name=7, parse_dates=True)
#cap_us = cap_us[cap_us['date'] >= "2013-01-01"]
#cap_us = cap_us.fillna(0)
roe_us = pd.read_excel(oppor, sheet_name=10, parse_dates=True)
roe_us = roe_us[roe_us['date'] >= "2013-01-01"]
roe_us = roe_us.fillna(0)
pe_us = pd.read_excel(oppor, sheet_name=3, parse_dates=True)
pe_us = pe_us[pe_us['date'] >= "2013-01-01"]
pe_us = pe_us.fillna(0)
pe_index = pd.read_excel(Index, sheet_name=3, parse_dates=True)
pe_index = pe_index[pe_index['date'] >= "2013-01-01"]
#peg_us = pd.read_excel(oppor, sheet_name=4, parse_dates=True)
#peg_us = peg_us[peg_us['date'] >= "2013-01-01"]
#peg_us = peg_us.fillna(0)

senti_us = pd.read_excel(oppor, sheet_name=13, parse_dates=True)
senti_us = senti_us[senti_us['date'] >= "2013-01-01"]  # 자체 date 열 사용
senti_us = senti_us.fillna(0)

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

us_eps_surprise = pd.read_excel(factset, sheet_name=7, parse_dates=True, skiprows=1)
us_eps_surprise.columns = rename_columns(us_eps_surprise.columns)
us_eps_surprise['date'] = pd.to_datetime(us_eps_surprise['date'])

sales_fact_us = pd.read_excel(factset, sheet_name=3, parse_dates=True, skiprows=1)
sales_fact_us.columns = rename_columns(sales_fact_us.columns)
sales_fact_us['date'] = pd.to_datetime(sales_fact_us['date'])

#opmargin_fact_us = pd.read_excel(factset, sheet_name=4, parse_dates=True, skiprows=1)
#opmargin_fact_us.columns = rename_columns(opmargin_fact_us.columns)
#opmargin_fact_us['date'] = pd.to_datetime(opmargin_fact_us['date'])

#evebit_fact_us = pd.read_excel(factset, sheet_name=5, parse_dates=True, skiprows=1)
#evebit_fact_us.columns = rename_columns(evebit_fact_us.columns)
#evebit_fact_us['date'] = pd.to_datetime(evebit_fact_us['date'])

#frcash_fact_us = pd.read_excel(factset, sheet_name=6, parse_dates=True, skiprows=1)
#frcash_fact_us.columns = rename_columns(frcash_fact_us.columns)
#frcash_fact_us['date'] = pd.to_datetime(frcash_fact_us['date'])

#revision_fact_us = pd.read_excel(factset_revision, sheet_name=1, parse_dates=True, skiprows=1)
#revision_fact_us.columns = rename_columns(revision_fact_us.columns)
#revision_fact_us['date'] = pd.to_datetime(revision_fact_us['date'])

#revision_fact_sales_us = pd.read_excel(factset_revision, sheet_name=2, parse_dates=True, skiprows=1)
#revision_fact_sales_us.columns = rename_columns(revision_fact_sales_us.columns)
#revision_fact_sales_us['date'] = pd.to_datetime(revision_fact_sales_us['date'])


eps_fact_Index = pd.read_excel(factset_Index, sheet_name=1).loc[2:]
eps_fact_Index.columns = factset_Index_list
eps_fact_Index['date'] = pd.to_datetime(eps_fact_Index['date'])

sales_fact_Index = pd.read_excel(factset_Index, sheet_name=2, parse_dates=True).loc[2:]
sales_fact_Index.columns = factset_Index_list
sales_fact_Index['date'] = pd.to_datetime(sales_fact_Index['date'])

fcf_fact_Index = pd.read_excel(factset_Index, sheet_name=3, parse_dates=True).loc[2:]
fcf_fact_Index.columns = factset_Index_list
fcf_fact_Index['date'] = pd.to_datetime(fcf_fact_Index['date'])

revision_fact_Index = pd.read_excel(factset_Index, sheet_name=4, parse_dates=True).loc[2:]
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
#opm_res = pd.read_excel(Index, sheet_name=8, parse_dates=True)
#opm_res = opm_res[fcf_res['date'] >= "2013-01-01"]
Index_list = pr_res.columns

pr_bd = bd[['date']].merge(pr, on='date', how='left')
pr_res_bd = bd[['date']].merge(pr_res, on='date', how='left')
eps_res_bd = bd[['date']].merge(eps_res, on='date', how='left')
sales_res_bd = bd[['date']].merge(sales_res, on='date', how='left')
fcf_res_bd = bd[['date']].merge(fcf_res, on='date', how='left')
#opm_res_bd = bd[['date']].merge(opm_res, on='date', how='left')
sales_us_bd = bd[['date']].merge(sales_us, on='date', how='left')
eps_us_bd = bd[['date']].merge(eps_us, on='date', how='left')
#cap_us_bd = bd[['date']].merge(cap_us, on='date', how='left')

#opm_us_bd = bd[['date']].merge(opm_us, on='date', how='left')
# ltg_us_bd = bd[['date']].merge(ltg_us, on = 'date', how='left')
roe_us_bd = bd[['date']].merge(roe_us, on='date', how='left')
pe_us_bd = bd[['date']].merge(pe_us, on='date', how='left')
#peg_us_bd = bd[['date']].merge(peg_us, on='date', how='left')
pe_index_bd = bd[['date']].merge(pe_index, on='date', how='left')
#eps_fact_us_bd = bd[['date']].merge(eps_fact_us, on='date', how='left')
#sales_fact_us_bd = bd[['date']].merge(sales_fact_us, on='date', how='left')
#revision_fact_us_bd = bd[['date']].merge(revision_fact_us, on='date', how='left')
#revision_fact_sales_us_bd = bd[['date']].merge(revision_fact_sales_us, on='date', how='left')
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

st_list = ['SPX Index','NDX Index','DJI Index','RTY Index',
               'SX5E Index','DAX Index','CAC Index','NKY Index','BM7P Index','BAI Index','UKX Index','SHCOMP Index','HSI Index']

china_eq = ['SHCOMP Index','HSI Index']
glb_eq = ['MSFT US Equity', 'AAPL US Equity', 'NVDA US Equity', 'AMZN US Equity', 'META US Equity',
                'TSLA US Equity', 'GOOGL US Equity','ORCL US Equity', 'PLTR US Equity', 'CRM US Equity','NFLX US Equity', 'SAP US Equity','AVGO US Equity',
          'JPM US Equity', 'XOM US Equity', 'UNH US Equity', 'MA US Equity', 'JNJ US Equity','WMT US Equity',
           'KO US Equity', 'PG US Equity', 'GE US Equity', 'NEE US Equity','MC FP Equity','SU FP Equity','OR FP Equity','SIE GR Equity','TTE FP Equity','SAN FP Equity',
          'ALV GR Equity','DTE GR Equity','RHM GR Equity','BABA US Equity', 'TCEHY US Equity', 'BIDU US Equity']



df_eps_filt   = eps_res.set_index('date').loc[:, eps_res.columns.intersection(glb_eq)].reset_index().copy()
df_eps_filt_2 =  eps_us.set_index('date').loc[:, eps_us.columns.intersection(glb_eq)].reset_index().copy()

df1 = df_eps_filt.set_index('date').copy()
df2 = df_eps_filt_2.set_index('date').copy()

# 공통 컬럼(티커) 찾기
common_columns = df1.columns.intersection(df2.columns)

# df2에서 중복 컬럼 제거
df2_unique = df2.drop(columns=common_columns)

# 두 데이터프레임 합치기
df_eps = pd.concat([df1, df2_unique], axis=1).reset_index()

df_sales_filt   = sales_res.set_index('date').loc[:, sales_res.columns.intersection(glb_eq)].reset_index().copy()
df_sales_filt_2 =  sales_us.set_index('date').loc[:, sales_us.columns.intersection(glb_eq)].reset_index().copy()

df1 = df_sales_filt.set_index('date').copy()
df2 = df_sales_filt_2.set_index('date').copy()

# 공통 컬럼(티커) 찾기
common_columns = df1.columns.intersection(df2.columns)

# df2에서 중복 컬럼 제거
df2_unique = df2.drop(columns=common_columns)

# 두 데이터프레임 합치기
df_sales = pd.concat([df1, df2_unique], axis=1).reset_index()



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
        if factor_score.nunique() <=1 or forward_returns.nunique() <=1:
            ic = np.nan
            p_value = np.nan
        else:
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

            # 순위 상관계수 계싼
            if factor.nunique() <= 1 or future_returns.nunique() <= 1:
                ic = np.nan
            else:
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

def load_data(data_dir, st_list):
    eps_data = eps_growth_nor(eps_res_bd.set_index('date')[st_list].shift(1),252,252*3).fillna(0)
    sales_data = eps_growth_nor(sales_res_bd.set_index('date')[st_list].shift(1), 252, 252*3).fillna(0)
    fcf_data = eps_growth_nor(fcf_res_bd.set_index('date')[st_list].shift(1), 252, 252*3).fillna(0)

    eps_data = eps_data.loc["2016-01-01":]
    sales_data = sales_data.loc["2016-01-01":]
    fcf_data = fcf_data.loc["2016-01-01":]

    price_data = pr_res_bd.set_index('date')[st_list]
    daily_returns = price_data.pct_change().fillna(0)
    return eps_data, sales_data, fcf_data, daily_returns, price_data

def calculate_factors(dates, st_list, eps_data, sales_data, fcf_data, daily_returns, price_data):

    factor_scores = {
        'eps_growth' : pd.DataFrame(index=dates, columns=st_list),
        'sales_growth' : pd.DataFrame(index=dates, columns=st_list),
        'fcf_growth' : pd.DataFrame(index=dates, columns = st_list),
        'mom_12m' : pd.DataFrame(index=dates, columns = st_list),
        'mom_3m' : pd.DataFrame(index=dates, columns = st_list),
        'p_s' : pd.DataFrame(index=dates, columns = st_list)
    }

    momentum_252d_raw = price_data.pct_change(252).shift(1).dropna()
    momentum_63d_raw = price_data.pct_change(252).shift(1).dropna()
    momentum_252d = revision_growth(momentum_252d_raw, window1=0, window2=252*3)
    momentum_63d = revision_growth(momentum_63d_raw, window1=0, window2=252*3)
    mom_12m_scores = assign_scores_from_ranks(momentum_252d_raw)
    mom_3m_scores = assign_scores_from_ranks(momentum_63d_raw)

    # Forward EPS/Sales/FCF 3개월 증가율 계산
    us_eps_fwd = eps_res_bd.set_index('date')[st_list]
    us_sales_fwd = sales_res_bd.set_index('date')[st_list]
    index_fcf_fwd = fcf_res_bd.set_index('date')[st_list]
    us_eps_fwd_3m = us_eps_fwd.pct_change(periods=62).fillna(0)
    us_sales_fwd_3m = us_sales_fwd.pct_change(periods=62).fillna(0)
    index_fcf_fwd_3m = index_fcf_fwd.pct_change(periods=62).fillna(0)

    trend_period_1m = 21
    trend_period_3m = 63

    # Save the data for analyzing trend
    eps_values = eps_data.copy()
    sales_values = sales_data.copy()
    fcf_values = fcf_data.copy()
    momentum_12m_values = momentum_252d_raw.copy()
    momentum_3m_values = momentum_63d_raw.copy()

    scores = pd.DataFrame(index=dates, columns=st_list)

    for date_idx, date in tqdm(enumerate(dates), total=len(dates), desc="Calculating factor scores with trends"):
        if date in eps_data.index:
            eps_vals = eps_data.loc[date].values.astype(float)
            sales_vals = sales_data.loc[date].values.astype(float)
            fcf_vals = fcf_data.loc[date].values.astype(float)

            if date in momentum_252d.index and date in momentum_63d.index:
                mom_12m_val = mom_12m_scores.loc[date].values
                mom_3m_val = mom_3m_scores.loc[date].values
            else:
                mom_12m_val = np.zeros(len(st_list))
                mom_3m_val = np.zeros(len(st_list))

            # Initial Scores
            factor_scores['eps_growth'].loc[date] = eps_vals * 0.01
            factor_scores['sales_growth'].loc[date] = sales_vals * 0.01
            factor_scores['fcf_growth'].loc[date] = fcf_vals * 0.01
            factor_scores['mom_12m'].loc[date] = mom_12m_val
            factor_scores['mom_3m'].loc[date] = mom_3m_val
            factor_scores['p_s'].loc[date] = 0

            # Forward 3개월 증가율 가져오기
            if date in us_eps_fwd_3m.index and date in us_sales_fwd_3m.index and date in index_fcf_fwd_3m.index:
                eps_growth_3m = us_eps_fwd_3m.loc[date]
                sales_growth_3m = us_sales_fwd_3m.loc[date]
                fcf_growth_3m = index_fcf_fwd_3m.loc[date]
            else:
                eps_growth_3m = pd.Series(index=st_list)
                sales_growth_3m = pd.Series(index=st_list)
                fcf_growth_3m = pd.Series(index=st_list)

            # 그룹화
            eps_growth_groups = assign_growth_groups(eps_growth_3m)
            sales_growth_groups = assign_growth_groups(sales_growth_3m)
            fcf_growth_groups = assign_growth_groups(fcf_growth_3m)

            eps_score_adjustments = eps_growth_groups.map(score_adjustments_eps).reindex(st_list).fillna(0)
            sales_score_adjustments = sales_growth_groups.map(score_adjustments_sales).reindex(st_list).fillna(0)
            fcf_score_adjustments = fcf_growth_groups.map(score_adjustments_sales).reindex(st_list).fillna(0)

            # Adjustments based on Forward Score
            for i, ticker in enumerate(st_list):
                factor_scores['eps_growth'].loc[date, ticker] += eps_score_adjustments[ticker]
                factor_scores['sales_growth'].loc[date, ticker] += sales_score_adjustments[ticker]
                factor_scores['fcf_growth'].loc[date, ticker] += fcf_score_adjustments[ticker]

            base_score = factor_scores['eps_growth'].loc[date].astype(float) \
                         + factor_scores['sales_growth'].loc[date].astype(float) \
                         + factor_scores['fcf_growth'].loc[date].astype(float) \
                         + factor_scores['mom_12m'].loc[date].astype(float) \
                         + factor_scores['mom_3m'].loc[date].astype(float) \
                         + factor_scores['p_s'].loc[date].astype(float).fillna(0)
            total_score = base_score.copy()

            # Trend analaysis logic
            if date_idx >= trend_period_3m:
                for i, ticker in enumerate(st_list):
                    eps_score = factor_scores['eps_growth'].loc[date, ticker]
                    sales_score = factor_scores['sales_growth'].loc[date, ticker]
                    fcf_score = factor_scores['fcf_growth'].loc[date, ticker]
                    mom_12m_score = factor_scores['mom_12m'].loc[date, ticker]
                    mom_3m_score = factor_scores['mom_3m'].loc[date, ticker]

                    # EPS 추세
                    eps_recent_3m = eps_values[ticker].iloc[date_idx - trend_period_3m:date_idx].dropna().astype(float)
                    eps_recent_1m = eps_values[ticker].iloc[date_idx - trend_period_1m:date_idx].dropna().astype(float)
                    if len(eps_recent_3m) >= 2 and len(eps_recent_1m) > 2:
                        eps_slope_3m = np.polyfit(np.arange(len(eps_recent_3m)),eps_recent_3m.values,1 )[0]
                        eps_slope_1m = np.polyfit(np.arange(len(eps_recent_1m)),eps_recent_1m.values, 1)[0]
                        if eps_slope_3m <0 and eps_slope_1m > 0.005:
                            eps_score += 3.0
                        if eps_slope_3m > 0.015:
                            eps_score += 1.0
                        if eps_score < 0 and eps_slope_1m > 0.005:
                            eps_score += 0.25

                    # Sales 추세
                    sales_recent_3m = sales_values[ticker].iloc[date_idx - trend_period_3m:date_idx].dropna().astype(float)
                    sales_recent_1m = sales_values[ticker].iloc[date_idx - trend_period_1m:date_idx].dropna().astype(float)
                    if len(sales_recent_3m) >= 2 and len(sales_recent_1m) >= 2:
                        sales_slope_3m = np.polyfit(np.arange(len(sales_recent_3m)), sales_recent_3m.values,1)[0]
                        sales_slope_1m = np.polyfit(np.arange(len(sales_recent_1m)), sales_recent_1m.values, 1)[0]
                        if sales_slope_3m < 0 and sales_slope_1m > 0.005:
                            sales_score += 2.0
                        if sales_slope_3m > 0.015:
                            sales_score += 0.5
                        if sales_score < 0 and sales_slope_1m > 0.005:
                            sales_score += 0.25

                    # FcF 추세
                    fcf_recent_3m = fcf_values[ticker].iloc[date_idx - trend_period_3m:date_idx].dropna().astype(float)
                    fcf_recent_1m = fcf_values[ticker].iloc[date_idx - trend_period_1m:date_idx].dropna().astype(float)
                    if len(fcf_recent_3m) >= 2 and len(fcf_recent_1m) >= 2:
                        fcf_slope_3m = np.polyfit(np.arange(len(fcf_recent_3m)), fcf_recent_3m.values,1)[0]
                        fcf_slope_1m = np.polyfit(np.arange(len(fcf_recent_1m)), fcf_recent_1m.values,1)[0]
                        if fcf_slope_3m < 0 and fcf_slope_1m > 0.005:
                            fcf_score += 2.0
                        if fcf_slope_3m > 0.015:
                            fcf_score += 0.5
                        if fcf_score < 0 and fcf_slope_1m > 0.005:
                            fcf_score += 0.25

                    # 12개월 모멘텀 추세
                    mom_12m_recent_3m = momentum_12m_values[ticker].iloc[date_idx - trend_period_3m:date_idx].dropna().astype(float)
                    mom_12m_recent_1m = momentum_12m_values[ticker].iloc[date_idx - trend_period_1m:date_idx].dropna().astype(float)
                    if len(mom_12m_recent_3m) >= 2 and len(mom_12m_recent_1m) >= 2:
                        mom_12m_slope_3m = np.polyfit(np.arange(len(mom_12m_recent_3m)), mom_12m_recent_3m.values,1)[0]
                        mom_12m_slope_1m = np.polyfit(np.arange(len(mom_12m_recent_1m)), mom_12m_recent_1m.values,1)[0]
                        if mom_12m_slope_3m < 0 and mom_12m_slope_1m > 0:
                            mom_12m_score += 2.0
                        if mom_12m_slope_3m > 0.01:
                            mom_12m_score += 0.25
                        if mom_12m_slope_3m < mom_12m_slope_1m and mom_12m_slope_1m > 0.01:
                            mom_12m_score += 0.25

                        # 3개월 모멘텀 추세
                        mom_3m_recent_3m = momentum_3m_values[ticker].iloc[date_idx - trend_period_3m:date_idx].dropna().astype(float)
                        mom_3m_recent_1m = momentum_3m_values[ticker].iloc[date_idx - trend_period_1m:date_idx].dropna().astype(float)
                        if len(mom_3m_recent_3m) >= 2 and len(mom_3m_recent_1m) >= 2:
                            mom_3m_slope_3m = np.polyfit(np.arange(len(mom_3m_recent_3m)), mom_3m_recent_3m.values, 1)[0]
                            mom_3m_slope_1m = np.polyfit(np.arange(len(mom_3m_recent_1m)), mom_3m_recent_1m.values, 1)[0]
                            if mom_12m_slope_3m <0 and mom_12m_slope_1m > 0.005:
                                mom_3m_score += 2.0
                            if mom_3m_slope_3m > 0.01:
                                mom_3m_score += 0.25
                            if mom_3m_slope_3m < mom_3m_slope_1m and mom_3m_slope_1m > 0.01:
                                mom_3m_score += 0.25

                        # 수정된 스코어 반영
                        factor_scores['eps_growth'].loc[date, ticker] = eps_score
                        factor_scores['sales_growth'].loc[date, ticker] = sales_score
                        factor_scores['fcf_growth'].loc[date, ticker] = fcf_score
                        factor_scores['mom_12m'].loc[date, ticker] = mom_12m_score
                        factor_scores['mom_3m'].loc[date, ticker] = mom_3m_score

                    # total_score 업데이트
                    total_score[ticker] = eps_score + sales_score + fcf_score + mom_12m_score + mom_3m_score

            scores.loc[date] = total_score
        else:

            if date_idx > 0:
                scores.loc[date] = scores.iloc[date_idx - 1]
                for f in factor_scores:
                    factor_scores[f].loc[date] = factor_scores[f].iloc[date_idx - 1]
            else:
                scores.loc[date] = np.zeros(len(st_list))
                for f in factor_scores:
                    factor_scores[f].loc[date] = np.zeros(len(st_list))

    return factor_scores, scores

def optimize_portfolio(expected_returns, cov_matrix, st_list, prev_weights, transaction_cost_rate = 0.001, china_restriction = True):

    w = cp.Variable(len(st_list))
    x = cp.Variable(len(st_list))
    max_weight = 0.35
    min_weight = -0.20

    bm7p_index = st_list.index('BM7P Index')
    bai_index = st_list.index('BAI Index')

    china_indices = []
    if china_restriction:
        china_indices = [st_list.index(eq) for eq in china_eq if eq in st_list]

    portfolio_variance = cp.quad_form(w, cov_matrix)

    constraints = [
        cp.sum(x) == 1,  # x의 합은 1
        -x <= w,  # -x <= w
        w <= x,  # w <= x
        0 <= cp.sum(w),
        cp.sum(w) <= 0.1,
        w >= min_weight,
        w <= max_weight,
        w[bm7p_index] >= 0,
        w[bai_index] >= 0,
        (w[bm7p_index] + w[bai_index]) <= 0.15,
        portfolio_variance <= 0.10 ** 2
    ]

    # Add constraints for China equities - max 2% for long positions
    if china_restriction:
        for idx in china_indices:
            # We need to constrain only when position is long
            # Since we can't directly use conditional constraints in CVXPY,
            # we'll apply a general constraint and post-process
            constraints.append(w[idx] <= 0.02)

    objective = cp.Maximize(expected_returns.values @ w)
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.ECOS, max_iters=10000, verbose=False)

    if w.value is not None:
        new_weights = pd.Series(w.value, index=st_list)

        # Post-processing: ensure China equities are at most 2% if long (only if restriction applies)
        if china_restriction:
            for eq in china_eq:
                if eq in new_weights.index and new_weights[eq] > 0 and new_weights[eq] > 0.02:
                    new_weights[eq] = 0.02
    else:
        new_weights = prev_weights.copy()

    return new_weights


def apply_eps_oeverlay(actual_weight, us_eps_fwd_3m, date, st_list, overlay_total_weight, prev_actual_weight_eps_overlay, transaction_cost_rate, overlay_weights_eps):

    actual_weight_eps_overlay = actual_weight.copy()
    overlay_position_eps = pd.Series(0.0, index=st_list, dtype = float)
    actual_transaction_costs_eps_overlay = 0

    if date in us_eps_fwd_3m.index:
        eps_growth_values = us_eps_fwd_3m.loc[date]
        top3_eps_stocks = eps_growth_values.sort_values(ascending=False).head(3).index.tolist()
        overlay_weights_proportions = [0.5, 0.3, 0.2]
        for stock, proportion in zip(top3_eps_stocks, overlay_weights_proportions):
            overlay_position_eps[stock] = proportion * overlay_total_weight
            actual_weight_eps_overlay[stock] += overlay_position_eps[stock]

        overlay_weights_eps.loc[date] = overlay_position_eps
        trading_eps_overaly = np.abs(actual_weight_eps_overlay - prev_actual_weight_eps_overlay)
        cost_eps_overlay = (trading_eps_overaly * transaction_cost_rate).sum()
        actual_transaction_costs_eps_overlay = cost_eps_overlay
        prev_actual_weight_eps_overlay = actual_weight_eps_overlay.copy()
    else:
        overlay_weights_eps.loc[date] = 0.0
        prev_actual_weight_eps_overlay = actual_weight.copy()

    return actual_weight_eps_overlay, prev_actual_weight_eps_overlay, actual_transaction_costs_eps_overlay

def apply_momentum_overlay(actual_weight, momentum_63d_raw, date,st_list, overlay_total_weight, prev_actual_weight_momentum_overlay, transaction_cost_rate, overlay_weights_momentum):

    actual_weight_momentum_overlay = actual_weight.copy()
    overlay_position_momentum = pd.Series(0.0, index=st_list, dtype = float)
    actual_transaction_costs_momentum_overlay = 0

    if date in momentum_63d_raw.index:
        momentum_values = momentum_63d_raw.loc[date]
        top3_momentum_stocks = momentum_values.sort_values(ascending=False).head(3).index.tolist()
        overlay_weights_proportions = [0.5, 0.3, 0.2]
        for stock, proportion in zip(top3_momentum_stocks, overlay_weights_proportions):
            overlay_position_momentum[stock] = proportion * overlay_total_weight
            actual_weight_momentum_overlay[stock] += overlay_position_momentum[stock]

        overlay_weights_momentum.loc[date] = overlay_position_momentum
        trading_momentum_overlay = np.abs(actual_weight - prev_actual_weight_momentum_overlay)
        cost_momentum_overlay = (trading_momentum_overlay * transaction_cost_rate).sum()
        actual_transaction_costs_momentum_overlay = cost_momentum_overlay
        prev_actual_weight_momentum_overlay = actual_weight_momentum_overlay.copy()
    else:
        overlay_weights_momentum.loc[date] = 0.0
        prev_actual_weight_momentum_overlay = actual_weight.copy()

    return actual_weight_momentum_overlay, prev_actual_weight_momentum_overlay, actual_transaction_costs_momentum_overlay

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
    #dema_1_month = data_numeric.apply(lambda x: dema(x[-60:], span=32).iloc[-1])
    dema_1_month = data_numeric.iloc[-21]


    # X축용 인덱스(정수)
    bar_x_positions = np.arange(len(lowest_pe.index))

    # Plotly Figure 생성
    fig = go.Figure()

    # (1) 바 차트: min -> max 구간을 SkyBlue 색상으로
    fig.add_trace(
        go.Bar(
            x=bar_x_positions,       # X축: 정수 위치
            y=height,                # 실제 바 높이는 (최대값 - 최소값)
            base=lowest_pe,          # 바가 시작될 y값(최솟값)
            marker_color="skyblue",
            width=0.3,
            name="P/E Range (Low to High)",
            opacity=0.7
        )
    )
    # 미리 이름과 색상, 분위수 레벨을 정의
    percentile_info = [
        {"label": "10th Percentile", "color": "black",  "level": 0.1},
        {"label": "25th Percentile", "color": "red",    "level": 0.25},
        {"label": "50th Percentile (Median)", "color": "green",  "level": 0.5},
        {"label": "75th Percentile", "color": "blue",   "level": 0.75},
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
            show_legend_flag = (i==0)

            fig.add_trace(
                go.Scatter(
                    x=[x_left, x_right],
                    y=[q_value, q_value],
                    mode="lines",
                    line = dict(color=pinfo["color"], width=2),
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
            name="1-Month DEMA",
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
            ax=bar_x_positions[i], # 화살표 시작 지점
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
    fig.update_yaxes(range=[0, y_max])

    # 그리드 보이게
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)

    return fig

def plot_pe_bands_plotly_sec(data):
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
    #dema_1_month = data_numeric.apply(lambda x: dema(x[-60:], span=32).iloc[-1])
    dema_1_month = data_numeric.iloc[-21]

    # X축용 인덱스(정수)
    bar_x_positions = np.arange(len(lowest_pe.index))

    # Plotly Figure 생성
    fig = go.Figure()

    # (1) 바 차트: min -> max 구간을 SkyBlue 색상으로
    fig.add_trace(
        go.Bar(
            x=bar_x_positions,       # X축: 정수 위치
            y=height,                # 실제 바 높이는 (최대값 - 최소값)
            base=lowest_pe,          # 바가 시작될 y값(최솟값)
            marker_color="skyblue",
            width=0.3,
            name="P/E Range (Low to High)",
            opacity=0.7
        )
    )
    # 미리 이름과 색상, 분위수 레벨을 정의
    percentile_info = [
        {"label": "10th Percentile", "color": "black",  "level": 0.1},
        {"label": "25th Percentile", "color": "red",    "level": 0.25},
        {"label": "50th Percentile (Median)", "color": "green",  "level": 0.5},
        {"label": "75th Percentile", "color": "blue",   "level": 0.75},
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
            show_legend_flag = (i==0)

            fig.add_trace(
                go.Scatter(
                    x=[x_left, x_right],
                    y=[q_value, q_value],
                    mode="lines",
                    line = dict(color=pinfo["color"], width=2),
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
            name="1-Month DEMA",
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
            ax=bar_x_positions[i], # 화살표 시작 지점
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
        legend=dict(yanchor="bottom", y=0.98, xanchor="left", x=0.01),
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
    y_max = 50
    fig.update_yaxes(range=[0, y_max])

    # 그리드 보이게
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)

    return fig

from mpl_toolkits.axes_grid1.inset_locator import inset_axes

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

def plot_eps_pe_growth(eps, pe, st_list):
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


def main():
    # 데이터 파일 경로 설정
    data_dir = 'C:/Users/westl/PycharmProjects/pythonProject/venv_vf/Index Quant'
    result_dir = 'C:/Users/westl/PycharmProjects/pythonProject/venv_vf/Index Quant/result'

    # 종목 리스트
    st_list = ['SPX Index', 'NDX Index', 'DJI Index', 'RTY Index',
               'SX5E Index', 'DAX Index', 'CAC Index', 'NKY Index', 'BM7P Index', 'BAI Index', 'UKX Index',
               'SHCOMP Index', 'HSI Index']

    china_eq = ['SHCOMP Index', 'HSI Index']

    Index_sector_list = ['SPX Index', 'NDX Index','BAI Index','BM7P Index', 'B500XM7P Index',
                         'S5TELS Index', 'S5CONS Index', 'S5COND Index', 'S5ENRS Index',
                         'S5FINL Index', 'S5HLTH Index', 'S5INDU Index', 'S5INFT Index', 'S5MATR Index', 'S5UTIL Index',
                         'S5SFTW Index', 'S5TECH Index', 'S5SSEQX Index']
    Index_sector = ['S&P500','NDX','BAI','M7','ex-M7','Tele-com','Con.stpls','Con.dis','Energy','Financial',
                    'Healthcare','Industrials','Info-Tech','Materials','Utilities',
                    'Tech-Software','Tech-Hard','Tech-Semi']

    Euro_sector_list = ['SX5E Index', 'SX7P Index', 'S600FOP Index', 'SXIP Index', 'SXRP Index', 'SX8P Index',
                        'SXKP Index', 'SXFP Index',
                        'SXDP Index', 'SXNP Index', 'SXMP Index', 'S600PDP Index', 'SX86P Index', 'SXTP Index',
                        'SX6P Index', 'SXAP Index',
                        'SXPP Index', 'SX4P Index', 'S600CPP Index', 'S600ENP Index']

    Euro_sector = ['EuroStoxx50', 'Banks', 'Food&Bev&Tob', 'Insurance', 'Retailers', 'Technology', 'Telecoms',
                   'Financial Ser',
                   'Healthcare', 'Industrail G&S', 'Media', 'Per.Care & Grocery', 'Real Estate', 'Travel & Leisure',
                   'Utilities',
                   'Autos and Parts', 'Basic Resource', 'Chemicals', 'Consum P&S', 'Energy']

    glb_eq = ['MSFT US Equity', 'AAPL US Equity', 'NVDA US Equity', 'AMZN US Equity', 'META US Equity',
                'TSLA US Equity', 'GOOGL US Equity','ORCL US Equity', 'PLTR US Equity', 'CRM US Equity','NFLX US Equity', 'SAP US Equity','AVGO US Equity',
          'JPM US Equity', 'XOM US Equity', 'UNH US Equity', 'MA US Equity', 'JNJ US Equity','WMT US Equity',
           'KO US Equity', 'PG US Equity', 'GE US Equity', 'NEE US Equity','MC FP Equity','SU FP Equity','OR FP Equity','SIE GR Equity','TTE FP Equity','SAN FP Equity',
          'ALV GR Equity','DTE GR Equity','RHM GR Equity','BABA US Equity', 'TCEHY US Equity', 'BIDU US Equity']


    eps_data, sales_data, fcf_data, daily_returns, price_data = load_data(data_dir, st_list)
    fundamental_start_date = eps_data.index.min()
    dates = daily_returns.loc[fundamental_start_date:].index
    rebalance_dates = pd.to_datetime(dates.to_series().resample('M').last().dropna().values)

    momentum_252d_raw = price_data.pct_change(252).shift(1).dropna()
    momentum_63d_raw = price_data.pct_change(252).shift(1).dropna()
    momentum_252d = revision_growth(momentum_252d_raw, window1=0, window2=252 * 3)
    momentum_63d = revision_growth(momentum_63d_raw, window1=0, window2=252 * 3)
    mom_12m_scores = assign_scores_from_ranks(momentum_252d_raw)
    mom_3m_scores = assign_scores_from_ranks(momentum_63d_raw)

    # Forward EPS/Sales/FCF 3개월 증가율 계산
    us_eps_fwd = eps_res_bd.set_index('date')[st_list]
    us_sales_fwd = sales_res_bd.set_index('date')[st_list]
    index_fcf_fwd = fcf_res_bd.set_index('date')[st_list]
    index_pe_fwd = pe_index_bd.set_index('date')[st_list]
    us_eps_fwd_3m = us_eps_fwd.pct_change(periods=62).fillna(0)
    us_sales_fwd_3m = us_sales_fwd.pct_change(periods=62).fillna(0)
    index_fcf_fwd_3m = index_fcf_fwd.pct_change(periods=62).fillna(0)

    us_eps_fwd_1y = us_eps_fwd.pct_change(periods=252).fillna(0)
    us_sales_fwd_1y = us_sales_fwd.pct_change(periods=252).fillna(0)
    index_fcf_fwd_1y = index_fcf_fwd.pct_change(periods=252).fillna(0)

    us_eps_fwd_sec = eps_res_bd.set_index('date')[Index_sector_list]
    us_sales_fwd_sec = sales_res_bd.set_index('date')[Index_sector_list]
    index_fcf_fwd_sec = fcf_res_bd.set_index('date')[Index_sector_list]
    index_pe_fwd_sec = pe_index_bd.set_index('date')[Index_sector_list]
    us_eps_fwd_sec.columns = Index_sector
    us_sales_fwd_sec.columns = Index_sector
    index_fcf_fwd_sec.columns = Index_sector
    index_pe_fwd_sec.columns = Index_sector

    euro_eps_fwd_sec = eps_res_bd.set_index('date')[Euro_sector_list]
    euro_sales_fwd_sec = sales_res_bd.set_index('date')[Euro_sector_list]
    Euro_sector_list_filtered = [item for item in Euro_sector_list if item != 'SX7P Index']
    Euro_sector_filtered = [item for item in Euro_sector if item != 'Banks']

    euro_fcf_fwd_sec = fcf_res_bd.set_index('date')[Euro_sector_list_filtered]
    #euro_fcf_fwd_sec = fcf_res_bd.set_index('date')[[col for col in Euro_sector_list if col != 'SX7E Index']]
    euro_pe_fwd_sec = pe_index_bd.set_index('date')[Euro_sector_list]
    euro_eps_fwd_sec.columns = Euro_sector
    euro_sales_fwd_sec.columns = Euro_sector
    euro_fcf_fwd_sec.columns = Euro_sector_filtered
    euro_pe_fwd_sec.columns = Euro_sector


    us_eps_fwd_3m_sec = us_eps_fwd_sec.pct_change(periods=62).fillna(0)
    us_sales_fwd_3m_sec = us_sales_fwd_sec.pct_change(periods=62).fillna(0)
    index_fcf_fwd_3m_sec = index_fcf_fwd_sec.pct_change(periods=62).fillna(0)

    us_eps_fwd_1y_sec = us_eps_fwd_sec.pct_change(periods=252).fillna(0)
    us_sales_fwd_1y_sec = us_sales_fwd_sec.pct_change(periods=252).fillna(0)
    index_fcf_fwd_1y_sec = index_fcf_fwd_sec.pct_change(periods=252).fillna(0)

    euro_eps_fwd_3m_sec = euro_eps_fwd_sec.pct_change(periods=62).fillna(0)
    euro_sales_fwd_3m_sec = euro_sales_fwd_sec.pct_change(periods=62).fillna(0)
    euro_fcf_fwd_3m_sec = euro_fcf_fwd_sec.pct_change(periods=62).fillna(0)

    euro_eps_fwd_1y_sec = euro_eps_fwd_sec.pct_change(periods=252).fillna(0)
    euro_sales_fwd_1y_sec = euro_sales_fwd_sec.pct_change(periods=252).fillna(0)
    euro_fcf_fwd_1y_sec = euro_fcf_fwd_sec.pct_change(periods=252).fillna(0)

    df_eps_3m = df_eps.set_index('date').pct_change(periods=63).fillna(0)
    df_eps_1y = df_eps.set_index('date').pct_change(periods=252).fillna(0)

    df_sales_3m = df_sales.set_index('date').pct_change(periods=63).fillna(0)
    df_sales_1y = df_sales.set_index('date').pct_change(periods=252).fillna(0)

    trend_period_1m = 21
    trend_period_3m = 63

    # Save the data for analyzing trend
    eps_values = eps_data.copy()
    sales_values = sales_data.copy()
    fcf_values = fcf_data.copy()

    factor_scores, scores = calculate_factors(dates, st_list, eps_data, sales_data, fcf_data, daily_returns, price_data)



    # p_s 팩터 임의 가산점
    Re_dates = pd.DataFrame(rebalance_dates, columns = ['date'])
    manual_scores_df_tbl = Re_dates.merge(manual_scores_df, on='date', how='left').fillna(0).set_index('date')

    plot_pe_bands_plotly(pe_index_bd.set_index('date')[st_list])
    plot_pe_bands_plotly_sec(index_pe_fwd_sec)


    data1_name = 'Fwd EPS'
    data2_name = 'Fwd FCF'
    data3_name = 'Fwd Sales'


    create_fundamental_scatter_plot(us_eps_fwd_3m.iloc[-1], index_fcf_fwd_3m.iloc[-1], st_list, data1_name, data2_name)
    create_fundamental_scatter_plot(us_eps_fwd_3m.iloc[-1], us_sales_fwd_3m.iloc[-1], st_list, data1_name, data3_name)
    create_fundamental_scatter_plot(us_eps_fwd_3m_sec.iloc[-1], index_fcf_fwd_3m_sec.iloc[-1], Index_sector, data1_name, data3_name)
    create_fundamental_scatter_plot(us_eps_fwd_3m_sec.iloc[-1], us_sales_fwd_3m_sec.iloc[-1], Index_sector, data1_name, data3_name)

    create_fundamental_scatter_plot_year(us_eps_fwd_1y.iloc[-1], index_fcf_fwd_1y.iloc[-1], st_list, data1_name, data2_name)
    create_fundamental_scatter_plot_year(us_eps_fwd_1y.iloc[-1], us_sales_fwd_1y.iloc[-1], st_list, data1_name, data3_name)
    create_fundamental_scatter_plot_year(us_eps_fwd_1y_sec.iloc[-1], index_fcf_fwd_1y_sec.iloc[-1], Index_sector, data1_name,
                                    data3_name)
    create_fundamental_scatter_plot_year(us_eps_fwd_1y_sec.iloc[-1], us_sales_fwd_1y_sec.iloc[-1], Index_sector, data1_name,
                                    data3_name)

    # 초기화
    prev_actual_weight = pd.Series(0.0, index=st_list)
    prev_benchmark_weight = pd.Series(1/len(st_list), index=st_list)
    benchmark_weights = pd.DataFrame(index=dates, columns=st_list)
    actual_weights = pd.DataFrame(index=dates, columns=st_list)
    benchmark_transaction_costs = pd.Series(0, index=dates)
    actual_transaction_costs = pd.Series(0, index=dates)

    # 오버레이 관련 변수(EPS, Momentum)
    overlay_total_weight = 0.05
    transaction_cost_rate = 0.001

    prev_actual_weight_eps_overlay = pd.Series(0.0, index=st_list)
    overlay_weights_eps = pd.DataFrame(0.0, index=dates, columns=st_list)
    actual_transaction_costs_eps_overlay = pd.Series(0.0, index=dates)

    prev_actual_weight_momentum_overlay = pd.Series(0.0, index=st_list)
    overlay_weights_momentum = pd.DataFrame(0.0, index=dates, columns=st_list)
    eps_overlay_portfolio = pd.DataFrame(0.0, index=dates, columns=st_list)
    actual_transaction_costs_eps_overlay = pd.Series(0.0, index=dates)

    prev_actual_weight_momentum_overlay = pd.Series(0.0, index=st_list)
    momentum_overlay_portfolio = pd.DataFrame(0.0, index=dates, columns=st_list)

    overlay_weights_momentum = pd.DataFrame(0.0, index=dates, columns=st_list)
    actual_transaction_costs_momentum_overlay = pd.Series(0.0, index=dates)

    total_weights_eps_overlay = pd.DataFrame(0.0, index=dates, columns = st_list)
    total_weights_momentum_overlay = pd.DataFrame(0.0, index=dates, columns = st_list)

    # Combined overlay, Growth, Momentum 포트폴리오 관련 초기화
    prev_actual_weight_combined_overlay = pd.Series(0.0, index=st_list)
    total_weights_combined_overlay = pd.DataFrame(0.0, index=dates, columns=st_list)
    combined_overlay_weights_eps = pd.DataFrame(0.0, index=dates, columns = st_list)
    combined_overlay_weights_momentum = pd.DataFrame(0.0, index=dates, columns = st_list)
    combined_overlay_portfolio = pd.DataFrame(0.0, index=dates, columns = st_list)
    actual_transaction_costs_combined_overlay = pd.Series(0, index=dates)
    actual_transaction_costs_combined_eps = pd.Series(0, index=dates)
    actual_transaction_costs_combined_momentum = pd.Series(0, index=dates)

    # Growth 포트폴리오
    actual_weights_growth = pd.DataFrame(0.0, index=dates, columns = st_list)
    prev_actual_weight_growth = pd.Series(0.0, index=st_list)
    actual_transaction_costs_growth = pd.Series(0.0, index=dates)

    # Momentum 포트폴리오
    actual_weights_momentum = pd.DataFrame(0.0, index=dates, columns = st_list)
    prev_actual_weight_momentum = pd.Series(0.0, index = st_list)
    actual_transaction_costs_momentum = pd.Series(0.0, index=dates)

    # Adaptive Model 포트폴리오
    factor_weights = pd.DataFrame(index=dates, columns=factor_scores.keys())
    p_s_weight = 1.0
    scores_new = pd.DataFrame(index=dates, columns = st_list)
    actual_weights_new = pd.DataFrame(index=dates, columns=st_list)
    prev_actual_weight_new = pd.Series(0, index=st_list)
    actual_transaction_costs_new = pd.Series(0, index=dates)

    # IC 계산용
    weekly_ic_df = calculate_weekly_ic(factor_scores, daily_returns, st_list)

    # 메인 루프: 리밸런싱 시 p_s팩터 적용, 메인 포트폴리오 최적화, EPS/MOM 오버레이, Combined/Growth/Momentum 포트폴리오 최적화
    # 비리밸런싱 시 비중 업데이트, 오버레이 비중 스케일링

    # 포트폴리오별 base leverage 저장용 변수
    # base_leverage 설정
    base_leverage = 1.0

    # 각 포트폴리오별 타겟 레버리지 설정 (예시)
    # 필요하다면 리밸런싱 날 최적화 결과에 따라 업데이트할 수도 있음
    # 초기 타겟 레버리지 정의 (전략에 맞게 설정)
    base_leverage = 1.0
    eps_target_leverage = base_leverage * 0.05       # 5%
    momentum_target_leverage = base_leverage * 0.05  # 5%
    combined_target_leverage = base_leverage * 0.10  # 10%
    adaptive_target_leverage = base_leverage         # 1.0


    # PE Multiple 계산

    # 초기 벤치마크 비중 설정: 시작 시점에 동일비중 벤치마크 포트폴리오 가정
    benchmark_weight = pd.Series(1/len(st_list), index=st_list)
    prev_benchmark_weight = benchmark_weight.copy()
    actual_weight = pd.Series(0, index=st_list)
    prev_actual_weight = actual_weight.copy()

    for date_idx, date in tqdm(enumerate(dates), total = len(dates), desc='Main Loop'):
        if date in rebalance_dates:
            # p_s 팩터 적용
            if date in manual_scores_df_tbl.index:
                manual_scores_today = manual_scores_df_tbl.loc[date]
                manual_scores_dict = manual_scores_today.to_dict()
                for ticker, score in manual_scores_dict.items():
                    if ticker in st_list:
                        factor_scores['p_s'].loc[date, ticker] = score

            # p_s 적용 후 total_score 재계산
            total_score = (
                factor_scores['eps_growth'].loc[date].astype(float)
                + factor_scores['sales_growth'].loc[date].astype(float)
                + factor_scores['fcf_growth'].loc[date].astype(float)
                + factor_scores['mom_12m'].loc[date].astype(float)
                + factor_scores['mom_3m'].loc[date].astype(float)
                + factor_scores['p_s'].loc[date].astype(float)
            )
            scores.loc[date] = total_score

            # 메인 포트폴리오 최적화
            expected_returns = scores.loc[date].astype(float)
            expected_returns = expected_returns - expected_returns.min()
            if expected_returns.max() > 0 :
                expected_returns = expected_returns / expected_returns.max()

            if date_idx >= 252:
                historical_returns = daily_returns.iloc[date_idx -252:date_idx]
            else:
                historical_returns = daily_returns.iloc[:date_idx]

            cov_matrix = calculate_ewma_covariance(historical_returns, span=252)
            cov_matrix = np.nan_to_num(cov_matrix)

            actual_weight = optimize_portfolio(expected_returns, cov_matrix, st_list, prev_actual_weight, transaction_cost_rate, china_restriction=True)

            # 거래비용 계산
            benchmark_weight = pd.Series(1/len(st_list), index=st_list)
            benchmark_trading = np.abs(benchmark_weight - prev_benchmark_weight)
            benchmark_cost = (benchmark_trading * transaction_cost_rate).sum()
            benchmark_transaction_costs.loc[date] = benchmark_cost

            actual_trading = np.abs(actual_weight - prev_actual_weight)
            actual_cost = (actual_trading * transaction_cost_rate).sum()
            actual_transaction_costs.loc[date] = actual_cost
            prev_benchmark_weight = benchmark_weight
            actual_weights.loc[date] = actual_weight
            prev_actual_weight = actual_weight

            # EPS 오버레이 적용
            actual_weight_eps_overlay, prev_actual_weight_eps_overlay, eps_cost = apply_eps_oeverlay(
                actual_weight, us_eps_fwd_3m, date, st_list, overlay_total_weight, prev_actual_weight_eps_overlay, transaction_cost_rate, overlay_weights_eps
            )
            actual_transaction_costs_eps_overlay.loc[date] = eps_cost
            total_weights_eps_overlay.loc[date] = actual_weight_eps_overlay

            # Momentum 오버레이 적용
            actual_weight_momentum_overlay, prev_actual_weight_momentum_overlay, momentum_cost = apply_momentum_overlay(
                actual_weight, momentum_63d_raw, date, st_list, overlay_total_weight,
                prev_actual_weight_momentum_overlay, transaction_cost_rate, overlay_weights_momentum
            )
            actual_transaction_costs_momentum_overlay.loc[date] = momentum_cost
            total_weights_momentum_overlay.loc[date] = actual_weight_momentum_overlay


            # Growth 포트폴리오 최적화
            total_score_growth = (
                factor_scores['eps_growth'].loc[date].astype(float)
                + factor_scores['sales_growth'].loc[date].astype(float)
                + factor_scores['fcf_growth'].loc[date].astype(float)
            )

            expected_returns_growth = total_score_growth - total_score_growth.min()
            if expected_returns_growth.max() >0:
                expected_returns_growth = expected_returns_growth / expected_returns_growth.max()

            # Growth 포트폴리오 최적화
            w_growth = cp.Variable(len(st_list))
            x_growth = cp.Variable(len(st_list))
            bm7p_index = st_list.index('BM7P Index')
            bai_index = st_list.index('BAI Index')
            portfolio_variance = cp.quad_form(w_growth, cov_matrix)
            max_weight = 0.4
            min_weight = -0.25

            china_indices = [st_list.index(eq) for eq in china_eq if eq in st_list]


            constraints_growth = [
                cp.sum(x_growth) == 1,  # x의 합은 1
                -x_growth <= w_growth,  # -x <= w
                w_growth <= x_growth,  # w <= x
                0 <= cp.sum(w_growth),
                cp.sum(w_growth) <= 0.1,
                w_growth >= min_weight,
                w_growth <= max_weight,
                w_growth[bm7p_index] >= 0,
                w_growth[bai_index] >= 0,
                (w_growth[bm7p_index] + w_growth[bai_index]) <= 0.15,
                portfolio_variance <= 0.10**2
            ]

            for idx in china_indices:
                constraints_growth.append(w_growth[idx] <= 0.02)

            objective_growth = cp.Maximize(expected_returns_growth.values @ w_growth)
            prob_growth = cp.Problem(objective_growth, constraints_growth)
            prob_growth.solve(solver=cp.SCS, max_iters=10000, verbose=False)
            if w_growth.value is not None:
                actual_weight_growth_t = pd.Series(w_growth.value, index=st_list)

                # Post proecessing: ensure China equities are at most 2% if long
                for eq in china_eq:
                    if eq in actual_weight_growth_t.index and actual_weight_growth_t[eq] >0 and actual_weight_growth_t[eq] > 0.02:
                        actual_weight_growth_t[eq]=0.02
            else:
                actual_weight_growth_t = prev_actual_weight_growth


            trading_growth = np.abs(actual_weight_growth_t - prev_actual_weight_growth)
            cost_growth = (trading_growth * transaction_cost_rate).sum()
            actual_transaction_costs_growth.loc[date] = cost_growth
            prev_actual_weight_growth = actual_weight_growth_t
            actual_weights_growth.loc[date] = actual_weight_growth_t

            # Momentum 포트폴리오 최적화
            total_score_momentum = (
                factor_scores['mom_12m'].loc[date].astype(float)
                + factor_scores['mom_3m'].loc[date].astype(float)
            )

            expected_returns_momentum = total_score_momentum - total_score_momentum.min()
            if expected_returns_momentum.max() > 0:
                expected_returns_momentum = expected_returns_momentum / expected_returns_momentum.max()

            w_momentum = cp.Variable(len(st_list))
            x_momentum = cp.Variable(len(st_list))
            portfolio_variance = cp.quad_form(w_momentum, cov_matrix)
            constraints_momentum = [
                cp.sum(x_momentum) == 1,  # x의 합은 1
                -x_momentum <= w_momentum,  # -x <= w
                w_momentum <= x_momentum,  # w <= x
                0 <= cp.sum(w_momentum),
                cp.sum(w_momentum) <= 0.1,
                w_momentum >= min_weight,
                w_momentum <= max_weight,
                w_momentum[bm7p_index] >=0,
                w_momentum[bai_index] >= 0,
                (w_momentum[bm7p_index] + w_momentum[bai_index]) <= 0.15,
                portfolio_variance <= 0.10 ** 2
            ]

            for idx in china_indices:
                constraints_momentum.append(w_momentum[idx] <= 0.02)

            objective_momentum = cp.Maximize(expected_returns_momentum.values @ w_momentum)
            prob_momentum = cp.Problem(objective_momentum, constraints_momentum)
            prob_momentum.solve(solver=cp.ECOS, max_iters=10000, verbose=False)
            if w_momentum.value is not None:
                actual_weight_momentum_t = pd.Series(w_momentum.value, index=st_list)

                # Post-processing: ensure China equities are at most 2% if long
                for eq in china_eq:
                    if eq in actual_weight_momentum_t.index and actual_weight_momentum_t[eq] >0 and actual_weight_momentum_t[eq] > 0.02:
                        actual_weight_momentum_t[eq] = 0.02
            else:
                actual_weight_momentum_t = prev_actual_weight_momentum

            trading_mom = np.abs(actual_weight_momentum_t - prev_actual_weight_momentum)
            cost_mom = (trading_mom * transaction_cost_rate).sum()
            actual_transaction_costs_momentum.loc[date] = cost_mom
            prev_actual_weight_momentum = actual_weight_momentum_t
            actual_weights_momentum.loc[date] = actual_weight_momentum_t

            # Combined Overlay 포트폴리오(EPS+Momentum) 최적화
            # Combined는 base 포트폴리오 + eps overlay + momentum overlay를 합친 뒤 10% 오버레이 목표
            # 여기서는 EPS/Mom overlay 각각 5%씩 분배 가정
            actual_weight_combined_overlay = actual_weight.copy()

            overlay_weight_high = 0.025
            overlay_weight_mid = 0.015
            overlay_weight_low = 0.01

            # EPS 상위 3 종목 5% 할당
            if date in us_eps_fwd_3m.index:
                eps_values_now = us_eps_fwd_3m.loc[date].dropna()
                top3_eps = eps_values_now.sort_values(ascending=False).head(3).index
                overlay_weights_eps_values = [overlay_weight_high,overlay_weight_mid,overlay_weight_low]
                for i, stock in enumerate(top3_eps):
                    actual_weight_combined_overlay[stock] += overlay_weights_eps_values[i]
                    combined_overlay_weights_eps.loc[date, stock] +=combined_overlay_weights_eps.loc[date, stock].astype(float) + overlay_weights_eps_values[i]

            # Momentum 상위3 종목 5% 할당
            if date in momentum_63d_raw.index:
                mom_values_now = momentum_63d_raw.loc[date].dropna()
                top3_mom = mom_values_now.sort_values(ascending=False).head(3).index
                overlay_weights_mom_values = [overlay_weight_high,overlay_weight_mid,overlay_weight_low]
                for i, stock in enumerate(top3_mom):
                    actual_weight_combined_overlay[stock] += overlay_weights_mom_values[i]
                    combined_overlay_weights_momentum.loc[date, stock] += overlay_weights_mom_values[i]

            # 거래비용 계산
            trading_combined = np.abs(actual_weight_combined_overlay - (total_weights_combined_overlay.shift(1).loc[date] if date_idx > 0 else actual_weight))
            trading_combined = trading_combined.fillna(0)
            cost_combined = (trading_combined * transaction_cost_rate).sum()
            actual_transaction_costs_combined_overlay.loc[date] = cost_combined
            total_weights_combined_overlay.loc[date] = actual_weight_combined_overlay

            # Adaptive Model 최적화
            ic_dates = weekly_ic_df.index[weekly_ic_df.index <= date]
            if len(ic_dates)>0:
                ic_date = ic_dates[-1]
                ic_end_idx = weekly_ic_df.index.get_loc(ic_date)
                if ic_end_idx >= 12:
                    ic_window = weekly_ic_df.iloc[ic_end_idx - 12:ic_end_idx]
                else:
                    ic_window = weekly_ic_df.iloc[:ic_end_idx]

                if len(ic_window) == 0:
                    factor_names = [f for f in factor_scores.keys() if f!='p_s']
                    equal_weight = 1/len(factor_names)
                    factor_weight = pd.Series(equal_weight, index=factor_names)
                else:
                    factor_weight_df = calculate_factor_weights(ic_window, window=12)
                    factor_weight = factor_weight_df.iloc[-1]

                factor_weight['p_s'] = p_s_weight
                factor_weights.loc[date] = factor_weight

                total_score_new = pd.Series(0, index=st_list, dtype=float)
                factor_names = [f for f in factor_scores.keys() if f!='p_s']
                for fn in factor_names:
                    f_score = factor_scores[fn].loc[date].astype(float)
                    wgt = factor_weight.get(fn,0)
                    total_score_new += f_score * wgt
                scores_new.loc[date] = total_score_new


                expected_returns_new = scores_new.loc[date].astype(float)
                expected_returns_new = expected_returns_new - expected_returns_new.min()
                if expected_returns_new.max() > 0:
                    expected_returns_new = expected_returns_new / expected_returns_new.max()

                if date_idx >= 252:
                    historical_returns = daily_returns.iloc[date_idx - 252:date_idx]
                else:
                    historical_returns = daily_returns.iloc[:date_idx]

                cov_matrix = calculate_ewma_covariance(historical_returns, span=65)
                cov_matrix = np.nan_to_num(cov_matrix)

                w_new = cp.Variable(len(st_list))
                x_new = cp.Variable(len(st_list))
                portfolio_variance = cp.quad_form(w_new, cov_matrix)
                constraints_new = [
                    cp.sum(x_new) == 1,  # x의 합은 1
                    -x_new <= w_new,  # -x <= w
                    w_new <= x_new,  # w <= x
                    0 <= cp.sum(w_new),
                    cp.sum(w_new) <= 0.1,
                    w_new >= min_weight,
                    w_new <= max_weight,
                    w_new[bm7p_index]>=0,
                    w_new[bai_index]>=0,
                    (w_new[bm7p_index]+w_new[bai_index])<=0.15,
                    portfolio_variance<=0.10 ** 2
                ]

                for idx in china_indices:
                    constraints_new.append(w_new[idx] <= 0.02)

                objective_new = cp.Maximize(expected_returns_new.values @ w_new)
                prob_new = cp.Problem(objective_new, constraints_new)
                prob_new.solve(solver=cp.ECOS, max_iters=10000, verbose=False)
                if w_new.value is not None:
                    actual_weight_new_t = pd.Series(w_new.value, index=st_list)

                    for eq in china_eq:
                        if eq in actual_weight_new_t.index and actual_weight_new_t[eq] > 0 and actual_weight_new_t[eq] > 0.02:
                            actual_weight_new_t[eq] = 0.02
                else:
                    actual_weight_new_t = prev_actual_weight_new

                trading_new = np.abs(actual_weight_new_t - prev_actual_weight_new)
                cost_new = (trading_new * transaction_cost_rate).sum()
                actual_transaction_costs_new.loc[date] = cost_new
                prev_actual_weight_new = actual_weight_new_t
                actual_weights_new.loc[date] = actual_weight_new_t
            else:
                # IC 데이터 없음
                scores_new.loc[date] = 0
                actual_weight_new_t = prev_actual_weight_new*(1+daily_returns.loc[date])
                actual_weight_new_t = actual_weight_new_t/(actual_weight_new_t.sum()+1)
                prev_actual_weight_new = actual_weight_new_t
                actual_transaction_costs_new.loc[date] = 0
                actual_weights_new.loc[date] = actual_weight_new_t

            # 리밸런싱 시점에서 actual_weight 확정 후:
            base_leverage = actual_weight.abs().sum()
            base_leverage_mom = actual_weight_momentum_t.abs().sum()
            base_leverage_growth = actual_weight_growth_t.abs().sum()
            eps_target_leverage = actual_weight_eps_overlay.abs().sum()
            momentum_target_leverage = actual_weight_momentum_overlay.abs().sum()
            combined_target_leverage = actual_weight_combined_overlay.abs().sum()
            adaptive_target_leverage = actual_weight_new_t.abs().sum()
            benchmark_weight = pd.Series(1/len(st_list), index=st_list)

        else:

            actual_weight = prev_actual_weight * (1 + daily_returns.loc[date])
            main_abs_sum = actual_weight.abs().sum()
            main_scale = base_leverage / main_abs_sum if main_abs_sum !=0 else 1.0
            actual_weight *= main_scale
            # 비중 반올림
            actual_weight = actual_weight.round(3)
            prev_actual_weight = actual_weight
            actual_transaction_costs.loc[date] = 0

            actual_weight_momentum = prev_actual_weight_momentum * (1 + daily_returns.loc[date])
            main_abs_sum_mom = actual_weight_momentum.abs().sum()
            main_scale_mom = base_leverage_mom / main_abs_sum_mom if main_abs_sum_mom !=0 else 1.0
            actual_weight_momentum *= main_scale_mom
            # 비중 반올림
            actual_weight_momentum = actual_weight_momentum.round(3)
            prev_actual_weight_momentum = actual_weight_momentum
            actual_transaction_costs_momentum.loc[date] = 0

            actual_weight_growth = prev_actual_weight_growth * (1 + daily_returns.loc[date])
            main_abs_sum_growth = actual_weight_growth.abs().sum()
            main_scale_growth = base_leverage_growth / main_abs_sum_growth if main_abs_sum_growth !=0 else 1.0
            actual_weight_growth *= main_scale_growth
            # 비중 반올림
            actual_weight_growth = actual_weight_growth.round(3)
            prev_actual_weight_growth = actual_weight_growth
            actual_transaction_costs_growth.loc[date] = 0


            # EPS Overlay
            actual_weight_eps_overlay = prev_actual_weight_eps_overlay * (1 + daily_returns.loc[date])
            eps_abs_sum = actual_weight_eps_overlay.abs().sum()
            eps_scale = eps_target_leverage / eps_abs_sum if eps_abs_sum !=0 else 1.0
            actual_weight_eps_overlay *= eps_scale
            actual_weight_eps_overlay = actual_weight_eps_overlay.round(3)
            prev_actual_weight_eps_overlay = actual_weight_eps_overlay.copy()
            actual_transaction_costs_eps_overlay.loc[date] = 0

            overlay_position_eps = (actual_weight_eps_overlay - actual_weight).round(3)

            # Momentum Overlay
            actual_weight_momentum_overlay = prev_actual_weight_momentum_overlay * (1 + daily_returns.loc[date])
            momentum_abs_sum = actual_weight_momentum_overlay.abs().sum()
            momentum_scale = momentum_target_leverage / momentum_abs_sum if momentum_abs_sum !=0 else 1.0
            actual_weight_momentum_overlay *= momentum_scale
            actual_weight_momentum_overlay = actual_weight_momentum_overlay.round(3)
            prev_actual_weight_momentum_overlay = actual_weight_momentum_overlay.copy()
            actual_transaction_costs_momentum_overlay.loc[date] = 0

            overlay_position_momentum = (actual_weight_momentum_overlay - actual_weight).round(3)

            # Combined Overlay
            # EPS 부분
            if date_idx > 0:
                combined_overlay_eps_today = combined_overlay_weights_eps.iloc[date_idx - 1] * (
                            1 + daily_returns.loc[date])
                combined_overlay_momentum_today = combined_overlay_weights_momentum.iloc[date_idx - 1] * (
                            1 + daily_returns.loc[date])
            else:
                combined_overlay_eps_today = pd.Series(0, index=st_list)
                combined_overlay_momentum_today = pd.Series(0, index=st_list)

            # Combine EPS and Momentum overlays
            combined_current_overlay = combined_overlay_eps_today + combined_overlay_momentum_today

            # Scale the Combined overlay based on the target combined leverage
            total_portfolio_weight_prev = total_weights_combined_overlay.shift(1).loc[date] if date_idx > 0 else actual_weight
            total_portfolio_weight_prev_abs_sum = total_portfolio_weight_prev.abs().sum()

            combined_abs_sum = combined_current_overlay.abs().sum()
            combined_scale = combined_target_leverage / total_portfolio_weight_prev_abs_sum if total_portfolio_weight_prev_abs_sum != 0 else 0.0 # prevent zero division error
            combined_current_overlay *= combined_scale

            # Rounding
            combined_overlay_eps_today = (combined_current_overlay * (combined_overlay_eps_today/(combined_current_overlay+1e-8))).round(3)
            combined_overlay_momentum_today = (combined_current_overlay * (combined_overlay_momentum_today/(combined_current_overlay+1e-8))).round(3)

            actual_weight_combined_overlay = actual_weight + combined_current_overlay
            actual_weight_combined_overlay = actual_weight_combined_overlay.round(3)

            prev_actual_weight_combined_overlay = actual_weight_combined_overlay.copy()
            combined_overlay_weights_eps.loc[date] = combined_overlay_eps_today
            combined_overlay_weights_momentum.loc[date] = combined_overlay_momentum_today
            actual_transaction_costs_combined_overlay.loc[date] = 0
            total_weights_combined_overlay.loc[date] = actual_weight_combined_overlay


            # Adaptive Model
            actual_weight_new_t = prev_actual_weight_new*(1+daily_returns.loc[date])
            adaptive_abs_sum = actual_weight_new_t.abs().sum()
            adaptive_scale = adaptive_target_leverage / adaptive_abs_sum if adaptive_abs_sum !=0 else 1.0
            actual_weight_new_t *= adaptive_scale
            actual_weight_new_t = actual_weight_new_t.round(3)
            prev_actual_weight_new = actual_weight_new_t
            actual_transaction_costs_new.loc[date] = 0

            # 비중 저장
            actual_weights.loc[date] = actual_weight
            actual_weights_momentum.loc[date] = actual_weight_momentum
            actual_weights_growth.loc[date] = actual_weight_growth
            total_weights_eps_overlay.loc[date] = actual_weight_eps_overlay
            overlay_weights_eps.loc[date] = overlay_position_eps
            total_weights_momentum_overlay.loc[date] = actual_weight_momentum_overlay
            overlay_weights_momentum.loc[date] = overlay_position_momentum
            total_weights_combined_overlay.loc[date] = actual_weight_combined_overlay
            combined_overlay_weights_eps.loc[date] = combined_overlay_eps_today
            combined_overlay_weights_momentum.loc[date] = combined_overlay_momentum_today
            # combined_overlay_weights_eps, combined_overlay_weights_momentum는 전략 로직에 맞게 별도 계산 후 저장 필요
            actual_weights_new.loc[date] = actual_weight_new_t

            # 벤치마크 업데이트
            benchmark_weight = prev_benchmark_weight*(1+daily_returns.loc[date])
            benchmark_weight = benchmark_weight / benchmark_weight.sum()
            benchmark_weight = benchmark_weight.round(3)
            prev_benchmark_weight = benchmark_weight
            benchmark_transaction_costs.loc[date] = 0
            benchmark_weights.loc[date] = benchmark_weight
    # 성과분석 및 저장
    # 성과 분석 및 파일 저장
    # IC 계산, period returns, annual returns, decay, etc.
    #benchmark_portfolio_returns = (benchmark_weights.shift(1) * daily_returns.loc[dates]).sum(
       #    axis=1) - benchmark_transaction_costs

    actual_weights = actual_weights.copy().round(3)
    total_weights_momentum_overlay = total_weights_momentum_overlay.copy().round(3)
    overlay_weights_eps = overlay_weights_eps.copy().round(3)
    overlay_weights_momentum = overlay_weights_momentum.copy().round(3)
    total_weights_eps_overlay = total_weights_eps_overlay.copy().round(3)
    total_weights_combined_overlay = total_weights_combined_overlay.copy().round(3)
    actual_weights_growth = actual_weights_growth.copy().round(3)
    actual_weights_momentum = actual_weights_momentum.copy().round(3)
    combined_overlay_weights_eps = combined_overlay_weights_eps.copy().round(3)
    combined_overlay_weights_momentum = combined_overlay_weights_momentum.copy().round(3)
    actual_weights_new = actual_weights_new.copy().round(3)

    actual_portfolio_returns = (actual_weights.shift(1) * daily_returns.loc[dates]).sum(
            axis=1) - actual_transaction_costs
    actual_portfolio_returns_overlay = (total_weights_momentum_overlay.shift(1) * daily_returns.loc[dates]).sum(
            axis=1) - (actual_transaction_costs + actual_transaction_costs_momentum_overlay)
    overlay_returns_eps = (overlay_weights_eps.shift(1) * daily_returns.loc[dates]).sum(
            axis=1) - actual_transaction_costs_eps_overlay
    overlay_returns_momentum = (overlay_weights_momentum.shift(1) * daily_returns.loc[dates]).sum(
            axis=1) - actual_transaction_costs_momentum_overlay
    actual_portfolio_returns_eps_overlay = (total_weights_eps_overlay.shift(1) * daily_returns.loc[dates]).sum(
            axis=1) - (actual_transaction_costs + actual_transaction_costs_eps_overlay)
    actual_portfolio_returns_combined_overlay = (total_weights_combined_overlay.shift(1) * daily_returns.loc[
            dates]).sum(axis=1) - (actual_transaction_costs + actual_transaction_costs_combined_overlay)
    actual_portfolio_returns_growth = ((actual_weights_growth.shift(1) * daily_returns.loc[dates]).sum(
            axis=1) - actual_transaction_costs_growth)
    actual_portfolio_returns_momentum = ((actual_weights_momentum.shift(1) * daily_returns.loc[dates]).sum(
            axis=1) - actual_transaction_costs_momentum)
    portfolio_returns_combined_eps = (combined_overlay_weights_eps.shift(1) * daily_returns.loc[dates]).sum(
            axis=1) - actual_transaction_costs_combined_eps
    portfolio_returns_combined_momentum = (combined_overlay_weights_momentum.shift(1) * daily_returns.loc[
            dates]).sum(axis=1) - actual_transaction_costs_combined_momentum
    actual_portfolio_returns_new = (actual_weights_new.shift(1) * daily_returns.loc[dates]).sum(
            axis=1) - actual_transaction_costs_new

    #benchmark_cum_returns = (1 + benchmark_portfolio_returns).cumprod() - 1
    actual_cum_returns = (1 + actual_portfolio_returns).cumprod() - 1
    spx_cum_returns = (1 + pr_res_bd[['SPX Index']].loc["2016-01-01":].pct_change(periods=1)).cumprod() - 1
    actual_cum_returns_overlay = (1 + actual_portfolio_returns_overlay).cumprod() - 1
    cum_overlay_returns_momentum = (1 + overlay_returns_momentum).cumprod() - 1
    actual_cum_returns_eps_overlay = (1 + actual_portfolio_returns_eps_overlay).cumprod() - 1
    cum_overlay_returns_eps = (1 + overlay_returns_eps).cumprod() - 1
    actual_cum_returns_combined_overlay = (1 + actual_portfolio_returns_combined_overlay).cumprod() - 1
    actual_cum_returns_combined_eps = (1 + portfolio_returns_combined_eps).cumprod() - 1
    actual_cum_returns_combined_momentum = (1 + portfolio_returns_combined_momentum).cumprod() - 1
    actual_cum_returns_growth = (1 + actual_portfolio_returns_growth).cumprod() - 1
    actual_cum_returns_momentum = (1 + actual_portfolio_returns_momentum).cumprod() - 1
    actual_cum_returns_new = (1 + actual_portfolio_returns_new).cumprod() -1

    benchmark_contributions = (benchmark_weights.shift(1)*daily_returns.loc[dates])
    actual_contributions = (actual_weights.shift(1)*daily_returns.loc[dates])
    score_ranks = scores.rank(axis=1, ascending=False)

    performance_decomposition = {}
    years = daily_returns.loc[dates].index.year.unique()
    for year in years:
        year_idx = daily_returns.loc[dates].index.year == year
        year_dates = daily_returns.loc[dates].index[year_idx]
        bm_contrib = benchmark_contributions.loc[year_dates].sum()
        act_contrib = actual_contributions.loc[year_dates].sum()
        avg_ranks = score_ranks.loc[year_dates].mean().sort_values()
        num_stocks = len(st_list)
        tercile = num_stocks//3
        high_rank = avg_ranks.index[:tercile]
        mid_rank = avg_ranks.index[tercile:2*tercile]
        low_rank = avg_ranks.index[2*tercile:]
        bm_high = bm_contrib[high_rank].sum()
        bm_mid = bm_contrib[mid_rank].sum()
        bm_low = bm_contrib[low_rank].sum()
        act_high = act_contrib[high_rank].sum()
        act_mid = act_contrib[mid_rank].sum()
        act_low = act_contrib[low_rank].sum()
        performance_decomposition[year] = {
            'Benchmark_Top': bm_high,
            'Benchmark_Middle': bm_mid,
            'Benchmark_Bottom': bm_low,
            'Actual_Top': act_high,
            'Actual_Middle': act_mid,
            'Actual_Bottom': act_low
        }

    performance_decomposition_df = pd.DataFrame(performance_decomposition).T
    recent_6m_dates = rebalance_dates[-55:]
    overlay_monthly_weights = total_weights_momentum_overlay.loc[rebalance_dates]
    overlay_partial_weights = overlay_weights_momentum.loc[rebalance_dates]
    eps_overlay_monthly_weights = total_weights_eps_overlay.loc[rebalance_dates]
    eps_overlay_partial_weights = overlay_weights_eps.loc[rebalance_dates]
    combined_overlay_monthly_weights = total_weights_combined_overlay.loc[rebalance_dates]
    combined_overlay_partial_weights = combined_overlay_weights_eps.loc[rebalance_dates] + combined_overlay_weights_momentum.loc[rebalance_dates]
    combined_overlay_eps_weights = combined_overlay_weights_eps.loc[rebalance_dates]
    combined_overlay_momentum_weights = combined_overlay_weights_momentum.loc[rebalance_dates]
    growth_weights = actual_weights_growth.loc[rebalance_dates]
    momentum_weights = actual_weights_momentum.loc[rebalance_dates]

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

    quarterly_group_stocks, quarterly_rebalance_dates = create_quarterly_group_stocks(score_ranks, daily_returns, st_list)
    decay_total = calculate_factor_decay(scores, daily_returns, 63, rebalance_dates)
    decay_factors = {}
    for factor_name, factor_data in factor_scores.items():
        decay = calculate_factor_decay(factor_data, daily_returns, 63, rebalance_dates)
        decay_factors[factor_name] = decay
    decay_factors_df = pd.DataFrame({factor_name: df['Mean_IC'] for factor_name, df in decay_factors.items()})
    decay_factors_df.index.name = 'Lag'

    for factor_name, df in factor_scores.items():
        df.fillna(0, inplace=True)

    weekly_ic_df = calculate_weekly_ic(factor_scores, daily_returns, st_list)

    ic_df = calculate_ic(scores, daily_returns, rebalance_dates, st_list)
    ic_df.to_csv(os.path.join(result_dir, 'ic_result.csv'))

    ic_results_factors = {}
    for factor_name, factor_data in factor_scores.items():
        ic_df_factor = calculate_ic(factor_data, daily_returns, rebalance_dates, st_list)
        ic_results_factors[factor_name] = ic_df_factor
        mean_ic = ic_df_factor['IC'].mean()
        print(f"Factor: {factor_name}, Mean IC: {mean_ic:.4f}")
        ic_df_factor.to_csv(os.path.join(result_dir, f'ic_results_{factor_name}.csv'))

    annual_ic_total = calculate_ic_annual(scores, daily_returns, rebalance_dates, st_list)
    annual_ic_total.to_csv(os.path.join(result_dir, 'annual_ic_total.csv'))

    actual_period_returns = calculate_period_returns(actual_cum_returns, periods_days.values())
    periods_labels = list(periods_days.keys())
    actual_returns_list = [actual_period_returns[periods_days[label]] for label in periods_labels]
    comparison_df = pd.DataFrame({
        'Periods' : periods_labels,
        'Actual Portfolio Return' : actual_returns_list
    })
    comparison_df['Actual Portfolio Return'] = comparison_df['Actual Portfolio Return'].apply(lambda x:f"{x * 100:.2f}%")

    new_portfolio_period_returns = calculate_period_returns((1+actual_portfolio_returns_new).cumprod()-1, periods_days.values())
    overlay_portfolio_period_returns = calculate_period_returns(actual_cum_returns_overlay, periods_days.values())
    eps_overlay_portfolio_period_returns = calculate_period_returns(actual_cum_returns_eps_overlay, periods_days.values())
    combined_overlay_portfolio_period_returns = calculate_period_returns(actual_cum_returns_combined_overlay, periods_days.values())
    growth_portfolio_period_returns = calculate_period_returns(actual_cum_returns_growth, periods_days.values())
    momentum_portfolio_period_returns = calculate_period_returns(actual_cum_returns_momentum, periods_days.values())

    new_returns_list = [new_portfolio_period_returns[periods_days[label]]for label in periods_labels]
    overlay_returns_list = [overlay_portfolio_period_returns[periods_days[label]] for label in periods_labels]
    eps_overlay_returns_list = [eps_overlay_portfolio_period_returns[periods_days[label]] for label in periods_labels]
    combined_overlay_returns_list = [combined_overlay_portfolio_period_returns[periods_days[label]] for label in periods_labels]
    growth_overlay_returns_list = [growth_portfolio_period_returns[periods_days[label]] for label in periods_labels]
    momentum_returns_list = [momentum_portfolio_period_returns[periods_days[label]] for label in periods_labels]
    growth_returns_list = [growth_portfolio_period_returns[periods_days[label]] for label in periods_labels]

    comparison_df['New Portfolio Return'] = new_returns_list
    comparison_df['Mom Overlay Portfolio Return'] = overlay_returns_list
    comparison_df['EPS Overlay Portfolio Return'] = eps_overlay_returns_list
    comparison_df['Combined Overlay Portfolio Return'] = combined_overlay_returns_list
    comparison_df['Growth Portfolio Return'] = growth_returns_list
    comparison_df['Momentum Portfolio Return'] = momentum_returns_list
    comparison_df['New Portfolio Return'] = comparison_df['New Portfolio Return'].apply(lambda x: f"{x * 100:.2f}%")
    comparison_df['Mom Overlay Portfolio Return'] = comparison_df['Mom Overlay Portfolio Return'].apply(
        lambda x: f"{x * 100:.2f}%")
    comparison_df['EPS Overlay Portfolio Return'] = comparison_df['EPS Overlay Portfolio Return'].apply(
        lambda x: f"{x * 100:.2f}%")
    comparison_df['Combined Overlay Portfolio Return'] = comparison_df['Combined Overlay Portfolio Return'].apply(
        lambda x: f"{x * 100:.2f}%")
    comparison_df['Growth Portfolio Return'] = comparison_df['Growth Portfolio Return'].apply(
        lambda x: f"{x * 100:.2f}%")
    comparison_df['Momentum Portfolio Return'] = comparison_df['Momentum Portfolio Return'].apply(
        lambda x: f"{x * 100:.2f}%")

    portfolios = {
        'Model': actual_portfolio_returns,
        'Adaptive Model': actual_portfolio_returns_new,
        'Mom Overlay Model': actual_portfolio_returns_overlay,
        'EPS Overlay Model': actual_portfolio_returns_eps_overlay,
        'Combined Overlay Model': actual_portfolio_returns_combined_overlay,
        'Growth Portfolio': actual_portfolio_returns_growth,
        'Momentum Portfolio': actual_portfolio_returns_momentum
    }

    results = {}
    for name, returns in portfolios.items():
        annual_return = calculate_annualized_return(returns)
        annual_volatility = calculate_annualized_volatility(returns)
        annual_sharpe = annual_return / annual_volatility
        results[name] = {
            'Annualized Return': annual_return,
            'Annualized Volatility': annual_volatility,
            'Annualized Sharpe Ratio': annual_sharpe
        }

    results_df = pd.DataFrame(results).T
    monthly_factor_weights = factor_weights.resample('M').last()

    actual_annual_returns = actual_portfolio_returns.groupby(actual_portfolio_returns.index.year).apply(
        lambda x: (1 + x).prod() - 1)
    actual_annual_returns_new = actual_portfolio_returns_new.groupby(actual_portfolio_returns_new.index.year).apply(
        lambda x: (1 + x).prod() - 1)
    actual_annual_returns_overlay = actual_portfolio_returns_overlay.groupby(
        actual_portfolio_returns_overlay.index.year).apply(lambda x: (1 + x).prod() - 1)
    actual_annual_returns_eps_overlay = actual_portfolio_returns_eps_overlay.groupby(
        actual_portfolio_returns_eps_overlay.index.year).apply(lambda x: (1 + x).prod() - 1)
    actual_annual_returns_combined_overlay = actual_portfolio_returns_combined_overlay.groupby(
        actual_portfolio_returns_combined_overlay.index.year).apply(lambda x: (1 + x).prod() - 1)
    actual_annual_returns_growth = actual_portfolio_returns_growth.groupby(
        actual_portfolio_returns_growth.index.year).apply(lambda x: (1 + x).prod() - 1)
    actual_annual_returns_momentum = actual_portfolio_returns_momentum.groupby(
        actual_portfolio_returns_momentum.index.year).apply(lambda x: (1 + x).prod() - 1)

    annual_returns = pd.DataFrame({
        'Actual': actual_annual_returns,
        'Adaptive Actual': actual_annual_returns_new,
        'Mom Overlay(5%)': actual_annual_returns_overlay,
        'EPS Overlay(5%)': actual_annual_returns_eps_overlay,
        'Combined Pverlay(10%)': actual_annual_returns_combined_overlay,
        'Growth': actual_annual_returns_growth,
        'Momentum': actual_annual_returns_momentum
    })

    # 결과 저장
    us_eps_fwd_3m.to_csv(os.path.join(result_dir, "eps_3m.csv"))
    eps_res_bd.set_index('date')[st_list].to_csv(os.path.join(result_dir, "index_eps.csv"))
    eps_res_bd.set_index('date')[Index_sector_list].to_csv(os.path.join(result_dir, "index_sec_eps.csv"))
    eps_res_bd.set_index('date')[Euro_sector_list].to_csv(os.path.join(result_dir, "euro_sec_eps.csv"))

    index_fcf_fwd_3m.to_csv(os.path.join(result_dir, "fcf_3m.csv"))
    us_sales_fwd_3m.to_csv(os.path.join(result_dir, "sales_3m.csv"))
    pe_index_bd.to_csv(os.path.join(result_dir, "pe_index_bd.csv"))
    us_eps_fwd_3m_sec.to_csv(os.path.join(result_dir, "eps_3m_sec.csv"))
    index_fcf_fwd_3m_sec.to_csv(os.path.join(result_dir, "fcf_3m_sec.csv"))
    us_sales_fwd_3m_sec.to_csv(os.path.join(result_dir, "sales_3m_sec.csv"))
    euro_eps_fwd_3m_sec.to_csv(os.path.join(result_dir, "euro_eps_3m_sec.csv"))
    euro_fcf_fwd_3m_sec.to_csv(os.path.join(result_dir, "euro_fcf_3m_sec.csv"))
    euro_sales_fwd_3m_sec.to_csv(os.path.join(result_dir, "euro_sales_3m_sec.csv"))

    us_eps_fwd_1y.to_csv(os.path.join(result_dir, "eps_1y.csv"))
    index_fcf_fwd_1y.to_csv(os.path.join(result_dir, "fcf_1y.csv"))
    us_sales_fwd_1y.to_csv(os.path.join(result_dir, "sales_1y.csv"))
    pe_index_bd.to_csv(os.path.join(result_dir, "pe_index_bd.csv"))
    us_eps_fwd_1y_sec.to_csv(os.path.join(result_dir, "eps_1y_sec.csv"))
    index_fcf_fwd_1y_sec.to_csv(os.path.join(result_dir, "fcf_1y_sec.csv"))
    us_sales_fwd_1y_sec.to_csv(os.path.join(result_dir, "sales_1y_sec.csv"))
    index_pe_fwd_sec.to_csv(os.path.join(result_dir, "pe_index_bd_sec.csv"))

    euro_eps_fwd_1y_sec.to_csv(os.path.join(result_dir, "euro_eps_1y_sec.csv"))
    euro_fcf_fwd_1y_sec.to_csv(os.path.join(result_dir, "euro_fcf_1y_sec.csv"))
    euro_sales_fwd_1y_sec.to_csv(os.path.join(result_dir, "euro_sales_1y_sec.csv"))
    euro_pe_fwd_sec.to_csv(os.path.join(result_dir, "euro_pe_index_bd_sec.csv"))

    actual_cum_returns.to_csv(os.path.join(result_dir, 'actual_cum_returns.csv'))
    actual_cum_returns_new.to_csv(os.path.join(result_dir, 'actual_cum_returns_new.csv'))
    actual_cum_returns_overlay.to_csv(os.path.join(result_dir, 'actual_cum_returns_overlay.csv'))
    actual_cum_returns_eps_overlay.to_csv(os.path.join(result_dir, 'actual_cum_returns_eps_overlay.csv'))
    actual_cum_returns_combined_overlay.to_csv(os.path.join(result_dir, 'actual_cum_returns_combined_overlay.csv'))
    actual_cum_returns_growth.to_csv(os.path.join(result_dir, 'actual_cum_returns_growth.csv'))
    actual_cum_returns_momentum.to_csv(os.path.join(result_dir, 'actual_cum_returns_momentum.csv'))
    annual_returns.to_csv(os.path.join(result_dir, 'annual_returns.csv'))
    performance_decomposition_df.to_csv(os.path.join(result_dir, 'performance_decomposition_df.csv'))
    recent_6m_weights.to_csv(os.path.join(result_dir, 'recent_6m_weights.csv'))
    overlay_recent_3y_weights.to_csv(os.path.join(result_dir, 'overlay_recent_3y_weights.csv'))
    eps_overlay_recent_3y_weights.to_csv(os.path.join(result_dir, 'eps_overlay_recent_3y_weights.csv'))
    overlay_recent_partial_weights.to_csv(os.path.join(result_dir, 'overlay_recent_partial_weights.csv'))
    eps_overlay_recent_partial_weights.to_csv(os.path.join(result_dir, 'eps_overlay_recent_partial_weights.csv'))
    combined_overlay_recent_3y_weights.to_csv(os.path.join(result_dir, 'combined_overlay_recent_3y_weights.csv'))
    combined_overlay_recent_partial_weights.to_csv(
        os.path.join(result_dir, 'combined_overlay_recent_partial_weights.csv'))
    combined_overlay_recent_eps_weights.to_csv(os.path.join(result_dir, 'combined_overlay_recent_eps_weights.csv'))
    combined_overlay_recent_momentum_weights.to_csv(
        os.path.join(result_dir, 'combined_overlay_recent_momentum_weights.csv'))
    growth_3y_weights.to_csv(os.path.join(result_dir, 'Growth_weights.csv'))
    momentum_3y_weights.to_csv(os.path.join(result_dir, 'Momentum_weights.csv'))
    comparison_df.to_csv(os.path.join(result_dir, 'comparison_df.csv'))
    decay_total.to_csv(os.path.join(result_dir, 'decay_total.csv'))
    decay_factors_df.to_csv(os.path.join(result_dir, 'decay_factors_df.csv'))
    results_df.to_csv(os.path.join(result_dir, 'results_df.csv'))
    monthly_factor_weights.to_csv(os.path.join(result_dir, 'monthly_factor_weights.csv'))
    scores.to_csv(os.path.join(result_dir, 'scores.csv'))
    df_eps_3m.to_csv(os.path.join(result_dir, 'glb_eq_eps_3m.csv'))
    df_sales_3m.to_csv(os.path.join(result_dir, 'glb_eq_sales_3m.csv'))
    df_eps_1y.to_csv(os.path.join(result_dir, 'glb_eq_eps_1y.csv'))
    df_sales_1y.to_csv(os.path.join(result_dir, 'glb_eq_sales_1y.csv'))


    with open(os.path.join(result_dir, 'quarterly_group_stocks.pkl'), 'wb') as f:
        pickle.dump(quarterly_group_stocks, f)
    with open(os.path.join(result_dir, 'quarterly_rebalance_dates.pkl'), 'wb') as f:
        pickle.dump(quarterly_rebalance_dates, f)

    with open(os.path.join(result_dir, 'factor_scores.pkl'), 'wb') as f:
        pickle.dump(factor_scores, f)

    monthly_group_stocks, monthly_rebalance_dates = create_monthly_group_stocks(score_ranks, daily_returns, st_list)
    with open(os.path.join(result_dir, 'monthly_group_stocks.pkl'), 'wb') as f:
        pickle.dump(monthly_group_stocks, f)
    with open(os.path.join(result_dir, 'monthly_rebalance_dates.pkl'), 'wb') as f:
        pickle.dump(monthly_rebalance_dates, f)

    print("All processes completed. The full integrated code run successfully.")


if __name__ == "__main__":
    main()

