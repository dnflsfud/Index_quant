import bisect

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
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from scipy.stats import zscore
from tqdm import tqdm
import os
import re

Index = "C:/Users/westl/PycharmProjects/pythonProject/Index.xlsx"
oppor = "C:/Users/westl/PycharmProjects/pythonProject/S&P500.xlsx"
factset = "C:/Users/westl/PycharmProjects/pythonProject/D_Factset.xlsx"
factset_revision = "C:/Users/westl/PycharmProjects/pythonProject/D_Revision_SPX.xlsx"
factset_Index = "C:/Users/westl/PycharmProjects/pythonProject/D_Index_Factset.xlsx"

pr = pd.read_excel(oppor, sheet_name=0, parse_dates=True)
pr = pr[pr['date'] >= "2013-01-01"]
bd = pd.read_excel(Index, sheet_name=13, parse_dates=True)
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
peg_us = pd.read_excel(oppor, sheet_name=4, parse_dates=True)
peg_us = peg_us[peg_us['date'] >= "2013-01-01"]
peg_us = peg_us.fillna(0)
pb_us = pd.read_excel(oppor, sheet_name=11, parse_dates=True)
pb_us = pb_us[pe_us['date'] >= "2013-01-01"]
pb_us = pb_us.fillna(0)

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

us_sales_surprise = pd.read_excel(factset, sheet_name=8, parse_dates=True, skiprows=1)
us_sales_surprise.columns = rename_columns(us_sales_surprise.columns)
us_sales_surprise['date'] = pd.to_datetime(us_sales_surprise['date'])


sales_fact_us = pd.read_excel(factset, sheet_name=3, parse_dates=True, skiprows=1)
sales_fact_us.columns = rename_columns(sales_fact_us.columns)
sales_fact_us['date'] = pd.to_datetime(sales_fact_us['date'])

opmargin_fact_us = pd.read_excel(factset, sheet_name=4, parse_dates=True, skiprows=1)
opmargin_fact_us.columns = rename_columns(opmargin_fact_us.columns)
opmargin_fact_us['date'] = pd.to_datetime(opmargin_fact_us['date'])

evebit_fact_us = pd.read_excel(factset, sheet_name=5, parse_dates=True, skiprows=1)
evebit_fact_us.columns = rename_columns(evebit_fact_us.columns)
evebit_fact_us['date'] = pd.to_datetime(evebit_fact_us['date'])

frcash_fact_us = pd.read_excel(factset, sheet_name=6, parse_dates=True, skiprows=1)
frcash_fact_us.columns = rename_columns(frcash_fact_us.columns)
frcash_fact_us['date'] = pd.to_datetime(frcash_fact_us['date'])

revision_fact_us = pd.read_excel(factset_revision, sheet_name=1, parse_dates=True, skiprows=1)
revision_fact_us.columns = rename_columns(revision_fact_us.columns)
revision_fact_us['date'] = pd.to_datetime(revision_fact_us['date'])

revision_fact_sales_us = pd.read_excel(factset_revision, sheet_name=2, parse_dates=True, skiprows=1)
revision_fact_sales_us.columns = rename_columns(revision_fact_sales_us.columns)
revision_fact_sales_us['date'] = pd.to_datetime(revision_fact_sales_us['date'])


#Bloomberg
pr_bd = bd[['date']].merge(pr, on='date', how='left')
pr_res_bd = bd[['date']].merge(pr_res, on='date', how='left') # SPX Index 포함
#sales_us_bd = bd[['date']].merge(sales_us, on='date', how='left')
#eps_us_bd = bd[['date']].merge(eps_us, on='date', how='left')
cap_us_bd = bd[['date']].merge(cap_us, on='date', how='left')
pb_us_bd = bd[['date']].merge(pb_us, on='date', how='left')
#opm_us_bd = bd[['date']].merge(opm_us, on='date', how='left')
# ltg_us_bd = bd[['date']].merge(ltg_us, on = 'date', how='left')
roe_us_bd = bd[['date']].merge(roe_us, on='date', how='left')
pe_us_bd = bd[['date']].merge(pe_us, on='date', how='left')
#peg_us_bd = bd[['date']].merge(peg_us, on='date', how='left')


#Factset
us_eps_surprise_bd = bd[['date']].merge(us_eps_surprise, on='date', how='left')
us_sales_surprise_bd = bd[['date']].merge(us_sales_surprise, on='date', how='left')
opmargin_fact_us_bd = bd[['date']].merge(opmargin_fact_us, on='date', how='left')
evebit_fact_us_bd = bd[['date']].merge(evebit_fact_us, on='date', how='left')
fcf_fact_us_bd = bd[['date']].merge(frcash_fact_us, on='date', how='left')
eps_fact_us_bd = bd[['date']].merge(eps_fact_us, on='date', how='left')
sales_fact_us_bd = bd[['date']].merge(sales_fact_us, on='date', how='left')
revision_fact_eps_bd = bd[['date']].merge(revision_fact_us, on='date', how='left')
revision_fact_sales_bd = bd[['date']].merge(revision_fact_sales_us, on='date', how='left')

EXCLUDED_TICKERS = [
    'SAP US Equity',
    'BABA US Equity',
    'TCEHY US Equity',
    'BIDU US Equity'
]


def compute_returns(prices, window=1):
    return prices.pct_change(window)

def compute_volatility(returns, window=63):
    return returns.rolling(window=window).std()*np.sqrt(252)

def compute_beta(returns, market_returns, window=252*3):
    covariance = returns.rolling(window=window).cov(market_returns)
    market_variance = market_returns.rolling(window=window).var()
    return covariance / market_variance

def compute_sharpe_ratio(returns, risk_free_rate=0.00, window=252):
    excess_returns = returns - risk_free_rate/252
    return (excess_returns.rolling(window=window).mean() * 252) / (returns.rolling(window=window).std() * np.sqrt(252))

def remove_excluded_tickers(data):
    """Remove excluded tickers from a Series or DataFrame."""
    if isinstance(data, pd.Series):
        return data[~data.index.isin(EXCLUDED_TICKERS)]
    elif isinstance(data, pd.DataFrame):
        return data.loc[~data.index.isin(EXCLUDED_TICKERS)]
    else:
        return data


def quantile_classify(data, n_quantiles=5, ascending=True):
    return data.rank(method='first', ascending=ascending).apply(
        lambda x: pd.qcut(x, n_quantiles, labels=False, duplicates='drop') + 1
    )

def calculate_ic(factor_scores, forward_returns):
    return pd.Series(factor_scores).corr(forward_returns, method='spearman')

# Portfolio Construction Functions

def create_benchmark_portfolio(cap_data, date, top_n=80, excluded_tickers = EXCLUDED_TICKERS):
    cap_data = cap_data[cap_data['date'] == date].drop(columns=['date'])

    if cap_data.empty:
        print(f"Warning: No market cap data available for {date}, using closest available date")
        # Find closest date
        available_dates = cap_data['date']
        closest_date = available_dates[available_dates <= date].max()
        if pd.isna(closest_date):
            closest_date = available_dates.min()
        cap_date = cap_data[cap_data['date'] == closest_date].drop(columns=['date'])


    # Fist row of data contains market caps for all stocks
    market_caps = cap_data.iloc[0]

    #Remove excluded tickers
    market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]
    # Select Top n stocks by market cap
    top_stocks = market_caps.sort_values(ascending=False).head(top_n)
    top_stocks = top_stocks.dropna()

    total_cap = top_stocks.sum()
    weights = top_stocks / total_cap

    weights = weights.round(4)

    return weights.to_dict()

def create_growth_portfolio(data_dict, date, top_n=80, excluded_tickers = EXCLUDED_TICKERS):
    cap_date = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date].drop(columns=['date'])

    market_caps = cap_date.iloc[0]
    market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

    top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

    # Calculate growth metrics for each stock
    growth_metrics = pd.DataFrame(index=top_stocks)

    # 1. Forward EPS 12m/3m growth
    if 'eps_fact_us_bd' in data_dict:
        eps_dates = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] <= date]['date']
        if not eps_dates.empty:
            current_date = eps_dates.max()
            eps_current = date_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] == current_date].iloc[0][top_stocks]

            # 12-month growth
            twelve_month_ago = current_date - pd.DateOffset(months=3)
            eps_12m_dates = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] <= twelve_month_ago]['date']
            if not eps_12m_dates.empty:
                eps_12m_date = eps_12m_dates.max()
                eps_12m_ago = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] == eps_12m_date].iloc[0][
                    top_stocks]
                growth_metrics['eps_growth_12m'] = (eps_current - eps_12m_ago) / eps_12m_ago.abs().replace(0, np.nan)


            # 3-month growth
            three_month_ago = current_date - pd.DateOffset(months=3)
            eps_3m_dates = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] <= three_month_ago]['date']
            if not eps_3m_dates.empty:
                eps_3m_date = eps_3m_dates.max()
                eps_3m_ago = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] == eps_3m_date].iloc[0][top_stocks]
                growth_metrics['eps_growth_3m'] = (eps_current - eps_3m_ago) / eps_3m_ago.abs().replace(0, np.nan)

    # 2. Forward Sales 12m growth
    if 'sales_fact_us_bd' in data_dict:
        sales_dates = data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] <= date]['date']
        if not sales_dates.empty:
            current_date = sales_dates.max()
            sales_current = data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] == current_date].iloc[0][top_stocks]

            # 12 month growth
            twelve_month_ago = current_date - pd.DateOffset(months=12)
            sales_12m_dates = data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] <= twelve_month_ago]['date']
            if not sales_12m_dates.empty:
                sales_12m_date = sales_12m_dates.max()
                sales_12m_ago = data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] == sales_12m_date].iloc[0][top_stocks]
                growth_metrics['sales_growth_12m'] = (sales_current - sales_12m_ago) / sales_12m_ago.abs().replace(0, np.nan)


    # 3. EPS Revision
    if 'revision_fact_eps_bd' in data_dict:
        eps_rev_dates = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= date]['date']
        if not eps_rev_dates.empty:
            current_date = eps_rev_dates.max()
            growth_metrics['eps_revision'] = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] == current_date].iloc[0][top_stocks]

    # 4. Sales Revision
    if 'revision_fact_sales_bd' in data_dict:
        sales_rev_dates = data_dict['revision_fact_sales_bd'][data_dict['revision_fact_sales_bd']['date'] <= date]['date']
        if not sales_rev_dates.empty:
            current_date = sales_rev_dates.max()
            growth_metrics['sales_revision'] = data_dict['revisioin_fact_sales_bd'][data_dict['revision_fact_sales_bd']['date'] == current_date.iloc[0]][top_stocks]

    # 5. PEG Ratio(inverse)
    if 'peg_us' in data_dict:
        peg_dates = data_dict['peg_us'][data_dict['peg_us']['date'] <= date]['date']
        if not peg_dates.empty:
            current_date = peg_dates.max()
            peg_current = data_dict['peg_us'][data_dict['peg_us']['date'] == current_date].iloc[0][top_stocks]
            growth_metrics['peg_inverse'] = 1 / peg_current

    # 6. EPS Surprise
    if 'us_eps_surprise_bd' in data_dict:
        surprise_dates = data_dict['us_eps_surprise_bd'][data_dict['us_eps_surprise_bd']['date'] <= date]['date']
        if not surprise_dates.empty:
            current_date = surprise_dates.max()
            growth_metrics['eps_surprise'] = data_dict['us_eps_surprise_bd'][data_dict['us_eps_surprise_bd']['date'] == current_date].iloc[0][top_stocks]

    # Fill NaN values with median
    growth_metrics = growth_metrics.apply(lambda x: x.fillna(x.median()), axis=0)

    # Create quantile scores for each individual metric(10 quantile)
    quantile_metrics = pd.DataFrame(index=growth_metrics.index)
    for col in growth_metrics.columns:
        # Higher values are better growth metrics
        quantile_metrics[col] = quantile_classify(growth_metrics[col], n_quantiles=10, ascending=False)

    # Calculate average quantile score
    growth_avg_score = quantile_metrics.mean(axis=1)

    # Classify into final 5 score
    growth_quantiles = quantile_classify(growth_avg_score, n_quantiles=5, ascending=False)

    return growth_quantiles, growth_avg_score, quantile_metrics

def create_value_portfolio(data_dict, date, top_n=80, excluded_tickers = EXCLUDED_TICKERS):
    cap_date = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date].drop(columns=['date'])

    market_caps = cap_date.iloc[0]
    market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]
    top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

    # Calcualte value metrics for each stock
    value_metrics = pd.DataFrame(index=top_stocks)

    # 1. Forwad P/E
    if 'pe_us' in data_dict:
        pe_dates = data_dict['pe_us'][data_dict['pe_us']['date'] <= date]['date']
        if not pe_dates.empty:
            current_date = pe_dates.max()
            value_metrics['pe'] = data_dict['pe_us'][data_dict['pe_us']['date'] == current_date].iloc[0][top_stocks]

    # 2. Forwad P/B
    if 'pb_us' in data_dict:
        pb_dates = data_dict['pb_us'][data_dict['pb_us']['date'] <= date]['date']
        if not pb_dates.empty:
            current_date = pb_dates.max()
            value_metrics['pb'] = data_dict['pb_us'][data_dict['pb_us']['date'] == current_date].iloc[0][top_stocks]

    # 3. Forward EV/EBITDA
    if 'evebit_fact_us_bd' in data_dict:
        evebit_dates = data_dict['evebit_fact_us_bd'][data_dict['evebit_fact_us_bd']['date'] <= date]['date']
        if not evebit_dates.empty:
            current_date = evebit_dates.max()
            value_metrics['evebitda'] = data_dict['evebit_fact_us_bd'][data_dict['evebit_fact_us_bd']['date'] == current_date].iloc[0][top_stocks]

    # Fill NaN values with median
    value_metrics = value_metrics.apply(lambda x:x.fillna(0), axis=0)

    # Create quantile scores for each individual metric(10 quantiles)
    quantile_metrics = pd.DataFrame(index=value_metrics.index)
    for cor in value_metrics.columns:
        # lower values are better for value metrics
        quantile_metrics[col] = quantile_classify(value_metrics[col], n_quantiles=10, ascending=True)

    # Calculate average quantile score
    value_avg_score = quantile_metrics.mean(axis=1)

    # Classify into final 5 quantiles
    value_quantiles = quantile_classify(value_avg_score, n_quantiles=5, ascending=False)

    return value_quantiles, value_avg_score, quantile_metrics

def create_momentum_portfolio(data_dict, date, top_n=80, excluded_tickers = EXCLUDED_TICKERS):
    cap_date = date_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date].drop(columns=['date'])

    market_caps = cap_date.iloc[0]
    market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

    top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

    # Calculate momentum metrics for each stock
    momentum_metrics = pd.DataFrame(index=top_stocks)

    # Get price data for calculation
    if 'pr_bd' in data_dict:
        price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= date]['date']

        if not price_dates.empty:
            current_date = price_dates.max()
            current_date = data_dict['pr_bd'][data_dict['pr_bd']['date'] == current_date].iloc[0][top_stocks]

            # 1-month ago price
            one_month_ago = current_date - pd.DateOffset(months=1)
            month_price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= one_month_ago]['date']
            if not month_price_dates.empty:
                month_date = month_price_dates.max()
                month_price = data_dict['pr_bd'][data_dict['pr_bd']['date'] == month_date].iloc[0][top_stocks]


            # 3-month ago price
            three_month_ago = current_date - pd.DateOffset(months=3)
            three_month_prices_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= three_month_ago]['date']
            if not three_month_prices_dates.empty:
                three_month_date = three_month_prices_dates.max()
                three_month_prie = data_dict['pr_bd'][data_dict['pr_bd']['date'] == three_month_date].iloc[0][top_stocks]
                momentum_metrics['mom_3m'] = (current_price / three_month_price) - 1

                # 12-month ago price
                twelve_month_ago = current_date - pd.DateOffset(months=12)
                year_price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= twelve_month_ago]['date']
                if not year_price_dates.empty:
                    year_date = year_price_dates.max()
                    year_price = data_dict['pr_bd'][data_dict['pr_bd']['date'] == year_date].iloc[0][top_stocks]

                    # 12-month return excluding most recent month
                    if 'month_price' in locals():
                        momentum_metrics['mom_12m_ex1m'] = (month_price / year_price) - 1

    # 3. EPS Revision 3-month change
    if 'revision_fact_eps_bd' in data_dict:
        eps_rev_dates = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= date]['date']
        if not eps_rev_dates.empty:
            current_date = eps_rev_dates.max()
            current_revision = data_dict['reviison_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] == current_date].iloc[0][top_stocks]


            three_month_ago = current_date = pd.DateOffset(months=3)
            three_month_rev_dates = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= three_month_ago]['date']
            if not three_month_rev_dates.empty:
                three_month_date = three_month_rev_dates.max()
                three_month_revision = \
                data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] == three_month_date].iloc[0][top_stocks]
                momentum_metrics['eps_rev_3m_change'] = current_revision - three_month_revision

    # Fill Nan values with median
    momentum_metrics = momentum_metrics.apply(lambda x:x.fillna(0), axis=0)

    # Create quantile scores for each individual metric(10 quantile)
    quantile_metrics = pd.DataFrame(index=momentum_metrics.index)
    for col in momentum_metrics.columns:
        # Higher values are better for momentum metrics
        quantile_metrics[col] = quantile_classify(momentum_metrics[col], n_quantiles=10, ascending=False)



    # Calculate average quantile score
    momentum_avg_score = quantile_metrics.mean(axis=1)

    # Classify into final 5 quantiles
    momentum_quantiles = quantile_classify(momentum_avg_score, n_quantiles=5, ascending=False)

    return momentum_quantiles, momentum_avg_score, quantile_metrics

def create_low_vol_portfolio(data_dict, date, top_n=80, excluded_tickers = EXCLUDED_TICKERS):
    cap_date = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date].drop(columns=['date'])

    market_caps = cap_date.iloc[0]
    market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

    top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

    # Calculate volatility metrics for each stock
    vol_metrics = pd.DataFrame(index=top_stocks)

    # Get price data for calculation
    if 'pr_bd' in data_dict:
        # Get data for the last 3 years
        three_years_ago = date - pd.DateOffset(years=3)
        price_data = data_dict['pr_bd'][(data_dict['pr_bd']['date'] >= three_years_ago) &
                                         (data_dict['pr_bd']['date'] <= date)]

        if not price_data.empty:
            # Calculate reuturns
            returns = price_data.set_index('date').pct_change().dropna()

            # Calculate 3-month volatility
            last_3m = returns.iloc[-63:]
            vol_metrics['vol_3m'] = last_3m[top_stocks].std() * np.sqrt(252)

            # Calculate 3-year beta with SPX
            if 'SPX Index' in returns.columns:
                stock_returns = returns[top_stocks]
                market_returns = returns['SPX Index']

                # Calculate beta for each stock
                betas = {}
                for stock in top_stocks:
                    if stock in stock_returns.columns:
                        cov = stock_returns[stock].cov(market_returns)
                        var = market_returns.var()
                        beta = cov / var if var != 0 else np.nan
                        betas[stock] = beta

                vol_metrics['beta_3y'] = pd.Series(betas)

    # Fill Nan values with 0
    vol_metrics = vol_metrics.apply(lambda x:x.fillna(0), axis=0)

    # Create quantile scores for each individual metric(10 quantile)
    quantile_metrics = pd.DataFrame(index=vol_metrics.index)
    for col in vol_metrics.columns:
        # Lower values are better for volatility metrics
        quantile_metrics[col] = quantile_classify(vol_metrics[col], n_quantiles=10, ascending=True)

    # Calculate average quantile score
    vol_avg_score = quantile_metrics.mean(axis=1)

    # Classify into final 5 quantiles
    vol_quantiles = quantile_classify(vol_avg_score, n_quantiles=5, ascending=False)

    return vol_quantiles, vol_avg_score, quantile_metrics


def create_quality_portfolio(data_dict, date, top_n=80, excluded_tickers = EXCLUDED_TICKERS):
    cap_date = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date].drop(columns=['date'])

    # Get market caps and remove excluded tickers
    market_caps = cap_date.iloc[0]
    market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

    # Select top N stocks by market cap
    top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()
    # Calculate quality metrics for each stock
    quality_metrics = pd.DataFrame(index=top_stocks)

    # 1. Forward ROE
    if 'roe_us' in data_dict:
        roe_dates = data_dict['roe_us'][data_dict['roe_us']['date'] <= date]['date']
        if not roe_dates.empty:
            current_date = roe.dates.max()
            quality_metrics['roe'] = data_dict['roe_us'][data_dict['roe_us']['date'] == current_date].iloc[0][top_stocks]

    # 2. Forward Gross Margin
    if 'gross_margin_us' in data_dict:
        gm_dates = data_dict['gross_margin_us'][data_dict['groww_margin_us']['date'] <= date]['date']
        if not gm_dates.empty:
            current_date = gm_dates.max()
            quality_metrics['gross_margin'] = data_dict['gross_margin_us'][data_dict['gross_margin_us']['date'] == current_date]

    # 3. Operating Margin
    if 'opmargin_fact_us_bd' in data_dict:
        opm_dates = data_dict['opmargin_fact_us_bd'][data_dict['opmargin_fact_us_bd']['date'] <= date]['date']
        if not opm_dates.empty:
            current_date = opm_dates.max()
            quality_metrics['op_margin'] = data_dict['opmargin_fact_us_bd'][data_dict['opmargin_fact_us_bd']['date'] == current_date].iloc[0][top_stocks]

    # 4. Forward FCF 12m Change
    if 'fcf_fact_us_bd' in data_dict:
        fcf_dates = data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] <= date]['date']
        if not fcf_dates.empty:
            current_date = fcf_dates.max()
            current_fcf = data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] == current_date].iloc[0][top_stocks]

            tweleve_month_ago = current_date - pd.DateOffset(months=12)
            fcf_12m_dates = data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] <= tweleve_month_ago]['date']
            if not fcf_12m_dates.empty:
                fcf_12m_date = fcf_12m_dates.max()
                year_aga_fcf = data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] == fcf_12m_date].iloc[0][top_stocks]
                quality_metrics['fcf_growth_12m'] = (current_fcf - year_aga_fcf) / year_aga_fcf.replace(0, np.nan)


    # Fill 0 values with median
    quality_metrics = quality_metrics.apply(lambda x:x.fillna(0), axis=0)

    # Create quantile scores for each individual metric(10 quantiles)
    quantile_metrics = pd.DataFrame(index=quality_metrics.index)
    for col in quality_metrics.columns:
        # Higher values are better for quality metrics
        quantile_metrics[col] = quantile_classify(quantile_metrics[col], n_quantiles=10, ascending=False)

    # Calculate average quantile score
    quality_avg_score = quantile_metrics.mean(axis=1)

    # Classify into final 5 quantiles
    quality_quantiles = quantile_classify(quality_avg_score, n_quantiles=5, ascending=False)

    return quality_quantiles, quality_avg_score, quantile_metrics

def adjust_weights_by_quantile(benchmark_weights, quantiles, adjustment_factors=[0.2,0.1,0,-0.1,-0.2])
    adjusted_weights = benchmark_weights.copy()

    # Apply adjustments based on quantiles
    for stock, quantile in quantiles.items():
        if stock in adjusted_weights and not pd.isna(quantile):
            # Quantiles are 1-based, so adjust index for 0-based list
            factor = adjustment_factors[int(quantile) -1]
            adjusted_weights[stock] = adjusted_weights[stock] * (1 + factor)

    # Scale weights to sum to 1
    total_weight = sum(adjusted_weights.values())
    for stock in adjusted_weights:
        adjusted_weights[stock] = adjusted_weights[stock] / total_weight
        # Round to 4 decimal places
        adjusted_weights[stock] = round(adjusted_weights[stock],4)

    return adjusted_weights

def build_portfolio_performance(price_data, weights_dict, start_date, end_date):
    date_range = price_data[(price_data['date'] >= start_date) & (price_data['date'] <= end_date)]['date']

    # Initialize Dataframe with dates
    portfolio_values = pd.DataFrame({'date':date_range})

    # Find rebalance dates
    rebalance_dates = sorted(list(weights_dict.keys()))

    # Process each date
    current_weights = None
    for date in date_range:
        # Check if this is a rebalance date
    rebalance_index = bisect.bisect_right(rebalance_dates, date) - 1
    if rebalance_index >= 0:
        rebalance_date = rebalance_dates[rebalance_index]
        new_weights = weights_dict[rebalance_date]

        # Update current weights if it's time to rebalace
        if current_weights in None or date == rebalance_date:
            current_weights = new_weights.copy()
        # Otherwise, adjust weights based on price changes
        else:
            prev_date_idx = date_range[date_range < date].index[-1]
            prev_date - date_range[prev_date_idx]

            # Get prices for both dates
            prev_prices = price_data[price_data['date'] == prev_date].iloc[0].drop('date')
            curr_prices = price_data[price_data['date'] == date].iloc[0].drop('date')

            # Calculate returns for each stock
            for stock in current_weights.keys():
                if stock in prev_prices and stock in curr_prices and prev_prices[stock] > 0:
                    stock_return = curr_prices[stock] / prev_prices[stock]
                    current_weights[stock] *= stock_return

            # Normalize weights to sum to 1
            total_weight = sum(current_weights.values())
            if total_weight >0:
                for stock in current_weights:
                    current_weights[stock] = current_weights[stock] / total_weight
                    current_weights[stock] = round(current_weights[stock], 4)

        # Add weights to the portfolio values
        for stock, weight in current_weights.items():
            if stock not in portfolio_values.columns:
                portfolio_values[stock] = 0
            portfolio_values.loc[portfolio_values['date'] == date, stock] = weight

    return portfolio_values

def calculate_daily_returns(price_data, weights_data):
    daily_returns = pd.DataFrame({'date': weights_data['date']})
    daily_returns['return'] = 0

    for i in range(1, len(daily_returns)):
        current_date = daily_returns['date'].iloc[i]
        prev_date = daily_returns['date'].iloc[i-1]

        # Get weights from previous day
        prev_weights = weights_data[weights_data['date'] == prev_date].drop(columns = ['date']).iloc[0]

        # Get prices for both days
        prev_prices = price_data[price_data['date'] == prev_date].drop(columns=['date']).iloc[0]
        current_prices = price_data[price_data['date'] == current_date].drop(columns=['date']).iloc[0]

        # Calculate weighted return
        portfolio_return = 0
        for stock in prev_weights.index:
            if stock in prev_prices and stock in current_prices and prev_prices[stock] > 0:
                stock_return = current_prices[stock] / prev_prices[stock] - 1
                portfolio_return += prev_weights[stock] * stock_return

        daily_returns.loc[i, 'return'] = portfolio_return

    return daily_returns

def calcuate_performance_metrics(returns_data, window=[21,63,126,252,756,1260]):
    metrics = {}

    # Ensure returns_data has sufficient history
    max_window = max(windows)
    if len(returns_data) < max_window:
        print(f"Warning: returns_data has only {len(returns_data)} days, some metrics will be NA")

    for window in windows:
        if len(returns_data) >= window:
            # Cumulative return
            cumulative_return = (1 + returns_data['return']).iloc[-window].prod() - 1
            metrics[f'{window}d_return'] = cumulative_return

            # Volatility
            volatility = returns_data['return'].iloc[-window:].std() * np.sqrt(252)
            metrics[f'{window}d_volatility'] = volatility

            # Sharpe ratio
            if volatility >0:
                avg_return = returns_data['return'].iloc[-window].mean() * 252
                sharpe = avg_return / volatility
                metrics[f'{window}d_sharpe'] = sharpe
            else:
                metrics[f'{window}d_sharpe'] = np.nan

    return metrics

def save_returns_to_csv(results, output_dir='factor_portfolio_output'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Save daily portfolio weights
    for portfolio_type, weights_dict in results['portfolio_values'].items():
        df = weights_dict
        df.to_csv(f"{output_dir}/{portfolio_type}_weights.csv", index=False)

    # 2. Save daily portfolio returns
    returns_df = pd.DataFrame({'date': results['portfolio_returns']['benchmark']['date']})
    for portfolio_type, returns_data in results['portfolio_returns'].items():
        returns_df[f'{portfolio_type}_return'] = returns_data['return']

    returns_df.to_csv(f"{output_dir}/portfolio_returns.csv", index=False)

    # 3. Save performace metrics
    metrics_dict = {}
    for portfolio_type, metrics in results['performance_metrics'].items():
        for metric_name, value in metrics.items():
            if metric_name not in metrics_dict:
                metrics_dict[metric_name] = {}
            metrics_dict[metric_name][portfolio_type] = value

    metrics_df = pd.DataFrame(metrics_dict)
    metrics_df.to_csv(f"{output_dir}/performance_metrics.csv")

    # 4. Save IC results
    for factor_type, ic_list in results['factor_ic'].items():
        if ic_list:
            ic_df = pd.DataFrame(ic_list)
            ic_df.to_csv(f"{output_dir}/{factor_type}_ic.csv", index=False)

    # 5. Save factor quantiles
    for factor_type, quantiles_dict in results['factor_quantiles'].items():
        # Combine all quantile into a single dataframe
        all_dates = []
        all_stocks = []
        all_quantiles = []

        for date, quantiles_series in quantiles_dict.items():
            for stock, quantile in quantiles_series.items():
                all_dates.append(date)
                all_stocks.append(stock)
                all_quantiles.append(quantile)

        quantiles_df = pd.DataFrame({
            'date': all_dates,
            'stock': all_stocks,
            'quantile': all_quantiles
        })

        quantiles_df.to_csv(f"{output_dir}/{factor_type}_quantiles.csv", index=False)

    # 6. Save individual metric quantiles for each factor
    for factor_type, metric_dict in results['factor_metrics'].items():
        for date, metrics_df in metric_dict.items():
            date_str = date.strftime('%Y%m%d')
            metrics_df.to_csv(f"{output_dir}/{factor_type}_metrics_{date_str}.csv")

    print(f"Results saved to {output_dir}/")

    # 7. Save the list of excluded tickers for reference
    pd.DataFrame({'excluded_tickers': EXCLUDED_TICKERS}).to_csv(f"{output_dir}/excluded_tickers.csv", index=False)

    print(f"Results saved to {output_dir}/")


# 3. Main Function

def load_data():
    """Load all data sources and prepare them for analysis."""
    # Define data dictionary
    data = {}

    # Load the data from the provided code
    data['pr_bd'] = pr_bd
    if 'pr_res_bd' in globals():
        data['pr_res_bd'] = pr_res_bd
    data['cap_us_bd'] = cap_us_bd

    # Add additional data if available
    if 'eps_us' in globals():
        data['eps_us'] = eps_fact_us_bdus
    if 'sales_us' in globals():
        data['sales_us'] = sales_fact_us_bdus
    if 'opm_us' in globals():
        data['opm_us'] = opmargin_fact_us_bdus
    if 'roe_us' in globals():
        data['roe_us'] = roe_us_bd
    if 'pe_us' in globals():
        data['pe_us'] = pe_us_bd
    if 'peg_us' in globals():
        data['peg_us'] = peg_us_bd
    if 'pb_us' in globals():
        data['pb_us'] = pb_us_bd

    # Factset data
    data['us_eps_surprise_bd'] = us_eps_surprise_bd
    data['us_sales_surprise_bd'] = us_sales_surprise_bd
    data['opmargin_fact_us_bd'] = opmargin_fact_us_bd
    data['evebit_fact_us_bd'] = evebit_fact_us_bd
    data['fcf_fact_us_bd'] = fcf_fact_us_bd
    data['eps_fact_us_bd'] = eps_fact_us_bd
    data['sales_fact_us_bd'] = sales_fact_us_bd
    data['revision_fact_eps_bd'] = revision_fact_eps_bd
    data['revision_fact_sales_bd'] = revision_fact_sales_bd

    return data


def build_factor_portfolios(data_dict, start_date, end_date, excluded_tickers=EXCLUDED_TICKERS):
    """Build all factor portfolios and track performance."""
    print(f"Building factor portfolios from {start_date} to {end_date}")

    # Initialize results
    portfolio_weights = {
        'benchmark': {},
        'growth': {},
        'value': {},
        'momentum': {},
        'low_vol': {},
        'quality': {}
    }

    factor_quantiles = {
        'growth': {},
        'value': {},
        'momentum': {},
        'low_vol': {},
        'quality': {}
    }

    factor_metrics = {
        'growth': {},
        'value': {},
        'momentum': {},
        'low_vol': {},
        'quality': {}
    }

    factor_ic = {
        'growth': [],
        'value': [],
        'momentum': [],
        'low_vol': [],
        'quality': []
    }

    # Get all dates in the range
    all_dates = data_dict['pr_bd'][(data_dict['pr_bd']['date'] >= start_date) &
                                   (data_dict['pr_bd']['date'] <= end_date)]['date']

    # Find quarter-end dates for rebalancing
    rebalance_dates = []
    for date in all_dates:
        if date.month in [3, 6, 9, 12] and date.day > 25:
            next_month = (date.replace(day=1) + pd.DateOffset(months=1)).replace(day=1)
            if (next_month - date).days <= 7:  # If within 7 days of next month
                rebalance_dates.append(date)

    print(f"Found {len(rebalance_dates)} rebalance dates")

    # Build portfolios for each rebalance date
    for rebalance_date in tqdm(rebalance_dates, desc="Building portfolios"):
        try:
            # Create benchmark portfolio
            benchmark_weights = create_benchmark_portfolio(data_dict['cap_us_bd'], rebalance_date, excluded_tickers=EXCLUDED_TICKERS)
            portfolio_weights['benchmark'][rebalance_date] = benchmark_weights

            # Create factor portfolios
            growth_quantiles, growth_scores, growth_metrics = create_growth_portfolio(data_dict, rebalance_date, excluded_tickers=EXCLUDED_TICKERS)
            value_quantiles, value_scores, value_metrics = create_value_portfolio(data_dict, rebalance_date, excluded_tickers=EXCLUDED_TICKERS)
            momentum_quantiles, momentum_scores, momentum_metrics = create_momentum_portfolio(data_dict, rebalance_date, excluded_tickers=EXCLUDED_TICKERS)
            low_vol_quantiles, low_vol_scores, low_vol_metrics = create_low_vol_portfolio(data_dict, rebalance_date, excluded_tickers=EXCLUDED_TICKERS)
            quality_quantiles, quality_scores, quality_metrics = create_quality_portfolio(data_dict, rebalance_date, excluded_tickers=EXCLUDED_TICKERS)

            # Store quantiles and metric quantiles
            factor_quantiles['growth'][rebalance_date] = growth_quantiles
            factor_quantiles['value'][rebalance_date] = value_quantiles
            factor_quantiles['momentum'][rebalance_date] = momentum_quantiles
            factor_quantiles['low_vol'][rebalance_date] = low_vol_quantiles
            factor_quantiles['quality'][rebalance_date] = quality_quantiles

            factor_metrics['growth'][rebalance_date] = growth_metrics
            factor_metrics['value'][rebalance_date] = value_metrics
            factor_metrics['momentum'][rebalance_date] = momentum_metrics
            factor_metrics['low_vol'][rebalance_date] = low_vol_metrics
            factor_metrics['quality'][rebalance_date] = quality_metrics

            # Adjust weights based on quantiles
            growth_weights = adjust_weights_by_quantile(benchmark_weights, growth_quantiles)
            value_weights = adjust_weights_by_quantile(benchmark_weights, value_quantiles)
            momentum_weights = adjust_weights_by_quantile(benchmark_weights, momentum_quantiles)
            low_vol_weights = adjust_weights_by_quantile(benchmark_weights, low_vol_quantiles)
            quality_weights = adjust_weights_by_quantile(benchmark_weights, quality_quantiles)

            # Store weights
            portfolio_weights['growth'][rebalance_date] = growth_weights
            portfolio_weights['value'][rebalance_date] = value_weights
            portfolio_weights['momentum'][rebalance_date] = momentum_weights
            portfolio_weights['low_vol'][rebalance_date] = low_vol_weights
            portfolio_weights['quality'][rebalance_date] = quality_weights

            # Calculate information coefficient for each factor
            # Find next month's returns for IC calculation
            next_month = rebalance_date + pd.DateOffset(months=1)
            next_month_dates = data_dict['pr_bd'][(data_dict['pr_bd']['date'] > rebalance_date) &
                                                  (data_dict['pr_bd']['date'] <= next_month)]['date']

            if not next_month_dates.empty:
                future_date = next_month_dates.max()
                current_prices = data_dict['pr_bd'][data_dict['pr_bd']['date'] == rebalance_date].iloc[0]
                future_prices = data_dict['pr_bd'][data_dict['pr_bd']['date'] == future_date].iloc[0]

                # Calculate returns for stocks in the benchmark
                future_returns = {}
                for stock in benchmark_weights.keys():
                    if stock in current_prices and stock in future_prices and current_prices[stock] > 0:
                        future_returns[stock] = future_prices[stock] / current_prices[stock] - 1

                # Calculate IC for each factor
                if future_returns:
                    returns_series = pd.Series(future_returns)

                    # Filter scores to include only stocks with returns
                    valid_stocks = list(set(returns_series.index) & set(growth_scores.index))
                    if valid_stocks:
                        factor_ic['growth'].append({
                            'date': rebalance_date,
                            'ic': returns_series[valid_stocks].corr(growth_scores[valid_stocks], method='spearman')
                        })

                        factor_ic['value'].append({
                            'date': rebalance_date,
                            'ic': returns_series[valid_stocks].corr(value_scores[valid_stocks], method='spearman')
                        })

                        factor_ic['momentum'].append({
                            'date': rebalance_date,
                            'ic': returns_series[valid_stocks].corr(momentum_scores[valid_stocks], method='spearman')
                        })

                        factor_ic['low_vol'].append({
                            'date': rebalance_date,
                            'ic': returns_series[valid_stocks].corr(low_vol_scores[valid_stocks], method='spearman')
                        })

                        factor_ic['quality'].append({
                            'date': rebalance_date,
                            'ic': returns_series[valid_stocks].corr(quality_scores[valid_stocks], method='spearman')
                        })
        except Exception as e:
            print(f"Error building portfolios for {rebalance_date}: {e}")

    # Calculate daily portfolio values and returns
    print("Building portfolio performance")

    portfolio_values = {}
    portfolio_returns = {}

    for portfolio_type in portfolio_weights:
        portfolio_values[portfolio_type] = build_portfolio_performance(
            data_dict['pr_bd'], portfolio_weights[portfolio_type], start_date, end_date
        )

        portfolio_returns[portfolio_type] = calculate_daily_returns(
            data_dict['pr_bd'], portfolio_values[portfolio_type]
        )

    # Calculate performance metrics
    print("Calculating performance metrics")
    performance_metrics = {}
    for portfolio_type in portfolio_returns:
        performance_metrics[portfolio_type] = calculate_performance_metrics(
            portfolio_returns[portfolio_type],
            windows=[21, 63, 126, 252, 756, 1260]  # 1M, 3M, 6M, 1Y, 3Y, 5Y
        )

    # Create result objects
    results = {
        'portfolio_weights': portfolio_weights,
        'factor_quantiles': factor_quantiles,
        'factor_metrics': factor_metrics,
        'factor_ic': factor_ic,
        'portfolio_values': portfolio_values,
        'portfolio_returns': portfolio_returns,
        'performance_metrics': performance_metrics
    }

    return results


# 4. Main Execution Code

def main():
    """Main execution function."""
    print("Loading data...")
    data_dict = load_data()

    # Define date range
    start_date = pd.Timestamp('2013-01-01')
    end_date = pd.Timestamp.today().normalize()

    print(f"Building factor portfolios from {start_date} to {end_date}")
    results = build_factor_portfolios(data_dict, start_date, end_date, excluded_tickers=EXCLUDED_TICKERS)

    print("Saving results to CSV...")
    save_results_to_csv(results)

    print("Done!")

    return results


if __name__ == "__main__":
    try:
        results = main()
        print("Factor portfolio analysis complete!")
    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback

        traceback.print_exc()