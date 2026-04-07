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


senti_us = pd.read_excel(oppor, sheet_name=13, parse_dates=True)
senti_us = senti_us[senti_us['date'] >= "2013-01-01"]  # 자체 date 열 사용
senti_us = senti_us.fillna(0)

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

pr_res = pd.read_excel(Index, sheet_name=0, parse_dates=True)
pr_res = pr_res[pr_res['date'] >= "2013-01-01"]
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
senti_us_bd = bd[['date']].merge(senti_us, on='date', how='left')

peg_us_bd = bd[['date']].merge(peg_us, on='date', how='left')


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
    'BIDU US Equity',
    'BRK/B US Equity'
]


# Simple global progress tracking
class GlobalProgress:
    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time

    def update(self, step=1, force=False):
        self.current_step += step
        current_time = time.time()

        # Only update display if 0.5 second has passed since last update (reduces overhead)
        if force or (current_time - self.last_update_time) >= 0.5:
            percent = min(100, int(self.current_step * 100 / self.total_steps))
            elapsed = current_time - self.start_time

            # Estimate remaining time
            if self.current_step > 0:
                remaining = (elapsed / self.current_step) * (self.total_steps - self.current_step)
                time_str = f" | Elapsed: {elapsed:.1f}s | Remaining: {remaining:.1f}s"
            else:
                time_str = f" | Elapsed: {elapsed:.1f}s"

            # Create progress bar
            bar_length = 30
            filled_length = int(bar_length * self.current_step / self.total_steps)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)

            # Print progress
            sys.stdout.write(f"\rProgress: [{bar}] {percent}%{time_str}")
            sys.stdout.flush()
            self.last_update_time = current_time

    def finish(self):
        self.update(0, force=True)
        sys.stdout.write('\n')
        sys.stdout.flush()


# Global progress tracker instance (will be initialized in main)
progress = None

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

def create_benchmark_portfolio(cap_data, date, top_n=80, excluded_tickers=EXCLUDED_TICKERS):
    """벤치마크 포트폴리오 생성 함수 완전 재작성"""
    try:
        # 날짜는 단일 값이 아니라 데이터프레임의 한 열이므로 필터링 방식 변경
        date_data = cap_data[cap_data['date'] == date]

        if date_data.empty:
            print(f"경고: {date}에 대한 시가총액 데이터가 없습니다.")
            return {}

        # 시가총액 데이터 가져오기
        # 날짜 열 제외한 모든 열 선택
        cap_values = date_data.drop(columns=['date'])

        if cap_values.empty or cap_values.shape[0] == 0:
            print(f"경고: {date}에 대한 유효한 시가총액 데이터가 없습니다.")
            return {}

        # 첫 번째 행을 시리즈로 변환
        market_caps = cap_values.iloc[0]

        # 제외 티커 제거
        market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

        if market_caps.empty:
            print(f"경고: 제외 티커 제거 후 남은 시가총액 데이터가 없습니다.")
            return {}

        # 시가총액 기준 상위 N개 주식 선택
        top_stocks = market_caps.sort_values(ascending=False).head(top_n)
        top_stocks = top_stocks.dropna()

        if top_stocks.empty:
            print(f"경고: 상위 {top_n}개 주식 선택 결과가 비어 있습니다.")
            return {}

        total_cap = top_stocks.sum()
        if total_cap <= 0:
            print(f"경고: 총 시가총액이 0 이하입니다.")
            return {}

        # 시가총액 가중치 계산
        weights = top_stocks / total_cap
        weights = weights.round(4)

        return weights.to_dict()
    except Exception as e:
        print(f"벤치마크 포트폴리오 생성 중 오류: {e}")
        return {}

def create_individual_metric_portfolio(metric_data, benchmark_weights, ascending=True, n_quantiles=5):
    """
    Create a long-short portfolio for an individual metric.

    Parameters:
    -----------
    metric_data : pd.Series
        Series containing metric values for each stock
    benchmark_weights : dict
        Dictionary of benchmark weights by stock
    ascending : bool
        If True, lower values are better (e.g., PE ratio). If False, higher values are better (e.g., ROE)
    n_quantiles : int
        Number of quantiles to divide the stocks into

    Returns:
    --------
    adjusted_weights : dict
        Dictionary of adjusted weights for this metric portfolio
    quantiles : pd.Series
        Series of quantile assignments for each stock
    """

    # Filter to stock in the benchmark
    metric_filtered = metric_data[metric_data.index.isin(benchmark_weights.keys())]

    # Classfy into quantiles
    metric_quantiles = quantile_classify(metric_filtered, n_quantiles, ascending=ascending)

    # Define weight adjustments by quantile
    adjustment_factors = {
        1:0.1,
        2:0.05,
        3:0,
        4:-0.05,
        5:-0.1
    }

    # Create equal weight within each quantile
    weights = {}
    stocks_per_quantile = {}

    # Count stocks in each quantile
    for q in range(1, n_quantiles + 1):
        stocks_in_q = sum(metric_quantiles == q)
        stocks_per_quantile[q] = stocks_in_q

    # Calculate per stock weights within each quantile
    for stock, quantile in metric_quantiles.items():
        if not pd.isna(quantile) and stocks_per_quantile[quantile] > 0:
            weights[stock] = adjustment_factors[quantile] / stocks_per_quantile[quantile]

    # Verify that weights sum to approximately zero (market neutral)
    weight_sum = sum(weights.values())
    if abs(weight_sum) > 1e-10:  # Allow for small floating point errors
        # Distribute the difference evenly across all stocks
        adjustment = weight_sum / len(weights)
        for stock in weights:
            weights[stock] -= adjustment

    # Round to 4 decimal places
    weights = {k: round(v, 4) for k, v in weights.items()}

    return weights, metric_quantiles

def create_growth_metrics(data_dict, date, top_n=80, excluded_tickers=EXCLUDED_TICKERS):
    cap_date = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date].drop(columns==['date'])

    # Get market caps and remove excluded tickers
    market_caps = cap_date.iloc[0]
    market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

    # Select top N stocks by market cap
    top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

    growth_metrics = {}

    # 1. Forward EPS 12m/3m growth
    if 'eps_fact_us_bd' in data_dict:
        eps_dates = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] <= date]['date']
        if not eps_dates.empty:
            current_date = eps_dates.max()
            eps_current = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] == current_date].iloc[0][top_stocks]

            # 3-month growth
            three_month_ago = current_date - pd.DateOffset(months=3)
            eps_3m_dates = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] <= three_month_ago]['date']
            if not eps_3m_dates.empty:
                eps_3m_date = eps_3m_dates.max()
                eps_3m_ago = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] == eps_3m_date].iloc[0][top_stocks]
                eps_growth_3m = (eps_current - eps_3m_ago) / eps_3m_ago.abs().replace(0, np.nan)
                growth_metrics['eps_growth'] = eps_growth_3m.fillna(0)

            # 12-month growth
            tweleve_month_ago = current_date - pd.DateOffset(months=12)
            eps_12m_dates = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] <= tweleve_month_ago]['date']
            if not eps_12m_dates.empty:
                eps_12m_date = eps_12m_dates.max()
                eps_12m_ago = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] == eps_12m_date].iloc[0][top_stocks]
                eps_growth_12m = (eps_current - eps_12m_ago) / eps_12m_ago.abs().replace(0, np.nan)
                growth_metrics['eps_growth_12m'] = eps_growth_12m.fillna(0)

    # 2. Forward Sales 12m growth
    if 'sales_fact_us_bd' in data_dict:
        sales_dates = data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] <= date]['date']
        if not sales_dates.empty:
            current_date = sales_dates.max()
            sales_current = data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] == current_date].iloc[0][top_stocks]

            # 12-month growth
            tweleve_month_ago = current_date = pd.DateOffset(months=12)
            sales_12m_dates = data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] <= tweleve_month_ago]['date']
            if not sales_12m_dates.empty:
                sales_12m_date = sales_12m_dates.max()
                sales_12m_ago = data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] == sales_12m_date].iloc[0][top_stocks]
                sales_growth_12m = (sales_current - sales_12m_ago) / sales_12m_ago.abs().replace(0,np.nan)
                growth_metrics['sales_growth_12m'] = sales_growth_12m.fillna(0)

    # 3. EPS Revision
    if 'revision_fact_eps_bd' in data_dict:
        eps_rev_dates = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= date]['date']
        if not eps_rev_dates.empty:
            current_date = eps_rev_dates.max()
            eps_revision = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] == current_date].iloc[0][top_stocks]
            growth_metrics['eps_revision'] = eps_revision.fillna(0)

    # 4. Sales Revision
    if 'revision_fact_sales_bd' in data_dict:
        sales_rev_dates = data_dict['revision_fact_sales_bd'][data_dict['revision_fact_sales_bd']['date'] < date]['date']
        if not sales_rev_dates.empty:
            current_date = sales_rev_dates.max()
            sales_revision = data_dict['revision_fact_sales_bd'][data_dict['revision_fact_sales_bd']['date'] == current_date].iloc[0][top_stocks]
            growth_metrics['sales_revision'] = sales_revision.fillna(0)

    # 5. EPS Surprise
    if 'ue_eps_surprise_bd' in data_dict:
        surprise_dates = data_dict['us_eps_surprise_bd'][data_dict['us_eps_surprise_bd']['date'] <= date]['date']
        if not surprise_dates.empty:
            current_date = surprise_dates.max()
            eps_surprise = data_dict['us_eps_surprise_bd'][data_dict['us_eps_surprise)bd']['date'] == current_date].iloc[0][top_stocks]
            growth_metrics['eps_surprise'] = eps_surprise.fillna(0)

    return growth_metrics

def create_value_metrics(data_dict, data, top_n=80, excluded_tickers=EXCLUDED_TICKERS):
    cap_date = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date].drop(columns=['date'])

    # Get market caps and remove excluded tickers
    market_caps = cap_date.iloc[0]
    market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

    # Select top N stocks by market cap
    top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

    # Calculate value metrics for each stock
    value_metrics = {}

    # 1. Forward P/E
    if 'pe_us' in data_dict:
        pe_dates = data_dict['pe_us'][data_dict['pe_us']['date'] <= date]['date']
        if not pe_dates.empty:
            current_date = pe.dates.max()
            pe_ratio = data_dict['pe_us'][data_dict['pe_us']['date'] == current_date].iloc[0][top_stocks]
            value_metrics['pe_ratio'] = pe_ratio.fillna(0)

    # 2. Forward P/B
    if 'pb_us' in data_dict:
        pb_dates = data_dict['pb_us'][data_dict['pb_us']['date'] <= date]['date']
        if not pb_dates.empty:
            current_date = pb_dates.max()
            pb_ratio = data_dict['pb_us'][data_dict['pb_us']['date'] == current_date].iloc[0][top_stocks]
            value_metrics['pb_ratio'] = pb_ratio.fillna(0)

    # 3. Forward EV/Ebitda
    if 'evebit_fact_us_bd' in data_dict:
        evebit_dates = data_dict['evebit_fact_us_bd'][data_dict['evebit_fact_us_bd']['date']<= date]['date']
        if not evebit_dates.empty:
            current_date = evebit_dates.max()
            evebitda = data_dict['evebit_fact_us_bd'][data_dict['evebit_fact_us_bd']['date'] == current_date].iloc[0][top_stocks]
            value_metrics['ev_ebitda'] = evebitda.fillna(0)

    return value_metrics

def create_momentum_metrics(data_dict, date, top_n=80, excluded_tickers = EXCLUDED_TICKERS):
    cap_date = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date].drop(columns = ['date'])

    # Get market caps and remove excluded tickers
    market_caps = cap_date.iloc[0]
    market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

    # Select top N stocks by market cap
    top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

    # Calculate momentum metrics for each stock
    momentum_metrics = {}

    # Get price data for calculations
    if 'pr_bd' in data_dict:
        price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= date]['date']

        if not price_dates.empty:
            current_date = price_dates.max()
            current_price = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= current_date].iloc[0][top_stocks]

            # 1-month ago price
            one_month_ago = current_date - pd.DateOffset(months=1)
            month_price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= one_month_ago]['date']
            if not month_price_dates.empty:
                month_date = month_price_dates.max()
                month_price = data_dict['pr_bd'][data_dict['pr_bd']['date'] == month_date].iloc[0][top_stocks]
                mom_1m = (current_price / month_price) - 1
                momentum_metrics['mom_1m'] = mom_1m.fillna(0)

            # 3-month ago price
            three_month_ago = current_date - pd.DateOffset(months=3)
            three_month_price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= three_month_ago]['date']
            if not three_month_price_dates.empty:
                three_month_date = three_month_price_dates.max()
                three_month_price = data_dict['pr_bd'][data_dict['pr_bd']['date'] == three_month_date].iloc[0][top_stocks]
                mom_3m = (current_price / three_month_price) - 1
                momentum_metrics['mom_3m'] = mom_3m.fillna(0)

            # 12-month ago price
            tweleve_month_ago = current_date = pd.DateOffset(months=12)
            year_price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= tweleve_month_ago]['date']
            if not year_price_dates.empty:
                year_date = year_price_dates.max()
                year_price = data_dict['pr_bd'][data_dict['pr_bd']['date'] == year_date].iloc[0][top_stocks]
                mom_12m = (current_price / year_price) - 1
                momentum_metrics['mom_12m'] = mom_12m.fillna(0)

                # 12-month return excluding most recent omonth
                if 'month_price' in locals():
                    mom_12m_ex1m = (month_price / year_price) - 1
                    momentum_metrics['mom_12m_ex1m'] = mom_12m_ex1m.fillna(0)

    # EPS Revision 3-month change
    if 'revision_fact_eps_bd' in data_dict:
        eps_rev_dates = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= date]['date']
        if not eps_rev_dates.empty:
            current_date = eps_Rev_dates.max()
            current_revision = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= date]['date']
            if not eps_rev_dates.empty:
                current_date = eps_rev_dates.max()
                current_revision = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] == current_date].iloc[0][top_stocks]

                three_month_ago = current_date - pd.DateOffset(months=3)
                three_month_rev_dates = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= three_month_ago]['date']
                if not three_month_rev_dates.empty:
                    three_month_date = three_month_rev_dates.max()
                    three_month_revision = data_dict['revision_fact_eps_bd'][data_dict]['revision_fact_eps_bd']['date'] == three_month_date.iloc[0][top_stocks]
                    eps_rev_3m_change = current_revision - three_month_revision
                    momentum_metrics['eps_rev_3m_change'] = eps_rev_3m_change.fillna(0)

        return momentum_metrics

def create_low_vol_metrics(data_dict, date, top_n=80, excluded_tickers=EXCLUDED_TICKERS):
    cap_date - data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date].drop(columns=['date'])

    market_caps = cap_date.iloc[0]
    market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

    top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

    vol_metrics = {}

    if 'pr_bd' in data_dict:
        three_years_ago = date - pd.DateOffset(years=3)
        price_data = data_dict['pr_bd'][(data_dict['pr_bd']['date'] >= three_years_ago) &
                                         (data_dict['pr_bd']['date'] <= date)]

    if not price_data.empty:
        returns = price_data.set_index('date').pct_change().dropna()

        last_3m = returns.iloc[-63:]
        vol_3m = last_3m[top_stocks].std() * np.sqrt(252)
        vol_metrics['vol_3m'] = vol_3m.fillna(vol_3m.median())

        # Calculate 3-year beta with spx
        if 'SPX Index' in returns.columns:
            stock_returns = returns[top_stocks]
            market_returns = returns['SPX Index']

            # Calculate beta for stock
            betas = {}
            for stock in top_stocks:
                if stock in stock_returns.columns:
                    cov = stock_returns[stock].cov(market_returns)
                    var = market_returns.var()
                    beta = cov / var if var != 0 else np.nan
                    betas[stock] = beta

            beta_3y = pd.Series(betas)
            vol_metrics['beta_3y'] = beta_3y.fillna(beta_3y.median())

    return vol_metrics

def create_quality_metrics(data_dict, date, top_n=80, excluded_tickers=EXCLUDED_TICKERS):
    cap_date = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date].drop(columns=['date'])

    market_caps = cap_date.iloc[0]
    market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

    top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

    quality_metrics = {}

    # 1. Forward ROE
    if 'roe_us' in data_dict:
        roe_dates = data_dict['roe_us'][data_dict['roe_us']['date'] <= date]['date']
        if not roe_dates.empty:
            current_date = roe_dates.max()
            roe = data_dict['roe_us'][data_dict['roe_us']['date'] == current_date].iloc[0][top_stocks]
            quality_metrics['roe'] = roe.fillna(0)

    # 2. Forward Gross Margin
    if 'gross_margin_us' in data_dict:
        gm_dates = data_dict['gross_margin_us'][data_dict['gross_margin_us']['date'] <= date]['date']
        if not gm_dates.empty:
            current_date = gm_dates.max()
            gross_margin = data_dict['gross_margin_us'][data_dict['gross_margin_us']['date'] == current_date].iloc[0][top_stocks]

    # 3. Operating Margin
    if 'opmargin_fact_us_bd' in data_dict:
        opm_dates = data_dict['opmargin_fact_us_bd'][data_dict['opmargin_fact_us_bd']['date'] <= date]['date']
        if not opm_dates.empty:
            currnet_date = opm_dates.max()
            op_margin = data_dict['opmargin_fact_us_bd'][data_dict['opmargin_fact_us_bd']['date'] == current_date].iloc[0][top_stocks]
            quality_metrics['opmargin'] = op_margin.fillna(0)

    # 4. Forward FCF 12m Change
    if 'fcf_fact_us_bd' in data_dict:
        fcf_dates = data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] <= date]['date']
        if not fcf_dates.empty:
            current_date = fcf_dates.max()
            current_fcf = data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] == current_date].iloc[0][top_stocks]

            twelve_month_ago = current_date - pd.DateOffset(months=12)
            fcf_12m_dates = data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] <= twelve_month_ago]['date']
            if not fcf_12m_dates.empty:
                fcf_12m_date = fcf_12m_dates.max()
                year_ago_fcf = data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] == fcf_12m_date].iloc[0][top_stocks]
                fcf_growth_12m = (current_fcf - year_ago_fcf) / year_ag_fcf.abs().replace(0, np.nan)
                quality_metrics['fcf_growth_12m'] = fcf_growth_12m.fillna(0)

    return quality_metrics

def create_sentiment_metrics(data_dict, date, top_n=80, excluded_tickers = EXCLUDED_TICKERS):
    cap_date = data_dict['cap_us_bd'][data_dict['cap_us_bd'] == date].drop(columns=['date'])

    market_caps = cap_date.iloc[0]
    market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

    top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

    sentiment_metrics = {}

    # Add sentiment data if available (already processed as 7-day rolling sum)
    if 'senti_us_bd' in data_dict:
        senti_dates = data_dict['senti_us_bd'][data_dict['senti_us_bd']['date'] <= date]['date']
        if not senti_dates.empty:
            current_date = senti_dates.max()
            sentiment = data_dict['senti_us_bd'][data_dict['senti_us_bd']['date'] == current_date].iloc[0][top_stocks]
            sentiment_metrics['sentiment'] = sentiment.fillna(sentiment.median())

    return sentiment_metrics

def create_metric_portfolios(data_dict, date, benchmark_weights, excluded_tickers=EXCLUDED_TICKERS):
    """Create portfolios for each individual metric."""
    # Dictionary to store portfolios for each metric
    metric_portfolios = {}
    metric_quantiles = {}

    # Get all metrics by category
    growth_metrics = create_growth_metrics(data_dict, date, excluded_tickers=excluded_tickers)
    value_metrics = create_value_metrics(data_dict, date, excluded_tickers=excluded_tickers)
    momentum_metrics = create_momentum_metrics(data_dict, date, excluded_tickers=excluded_tickers)
    low_vol_metrics = create_low_vol_metrics(data_dict, date, excluded_tickers=excluded_tickers)
    quality_metrics = create_quality_metrics(data_dict, date, excluded_tickers=excluded_tickers)
    sentiment_metrics = create_sentiment_metrics(data_dict, date, excluded_tickers=excluded_tickers)

    # Create portfolios for growth metrics (higher values are better)
    for metric_name, metric_data in growth_metrics.items():
        weights, quantiles = create_individual_metric_portfolio(
            metric_data, benchmark_universe, ascending=False
        )
        metric_portfolios[metric_name] = weights
        metric_quantiles[metric_name] = quantiles

    # Create portfolios for value metrics (lower values are better)
    for metric_name, metric_data in value_metrics.items():
        weights, quantiles = create_individual_metric_portfolio(
            metric_data, benchmark_universe, ascending=True
        )
        metric_portfolios[metric_name] = weights
        metric_quantiles[metric_name] = quantiles

    # Create portfolios for momentum metrics (higher values are better)
    for metric_name, metric_data in momentum_metrics.items():
        weights, quantiles = create_individual_metric_portfolio(
            metric_data, benchmark_universe, ascending=False
        )
        metric_portfolios[metric_name] = weights
        metric_quantiles[metric_name] = quantiles

    # Create portfolios for low volatility metrics (lower values are better)
    for metric_name, metric_data in low_vol_metrics.items():
        weights, quantiles = create_individual_metric_portfolio(
            metric_data, benchmark_universe, ascending=True
        )
        metric_portfolios[metric_name] = weights
        metric_quantiles[metric_name] = quantiles

    # Create portfolios for quality metrics (higher values are better)
    for metric_name, metric_data in quality_metrics.items():
        weights, quantiles = create_individual_metric_portfolio(
            metric_data, benchmark_universe, ascending=False
        )
        metric_portfolios[metric_name] = weights
        metric_quantiles[metric_name] = quantiles

    # Create portfolios for sentiment metrics (higher values are better)
    for metric_name, metric_data in sentiment_metrics.items():
        weights, quantiles = create_individual_metric_portfolio(
            metric_data, benchmark_universe, ascending=False
        )
        metric_portfolios[metric_name] = weights
        metric_quantiles[metric_name] = quantiles

    return metric_portfolios, metric_quantiles

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
            eps_current = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] == current_date].iloc[0][top_stocks]

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
            growth_metrics['sales_revision'] = data_dict['revision_fact_sales_bd'][data_dict['revision_fact_sales_bd']['date'] == current_date.iloc[0]][top_stocks]

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
    cap_date = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date].drop(columns=['date'])

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

def adjust_weights_by_quantile(benchmark_weights, quantiles, adjustment_factors=[0.2,0.1,0,-0.1,-0.2]):
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
    """포트폴리오 성과 구축 함수 개선"""
    try:
        if not weights_dict:
            return pd.DataFrame(columns=['date'])

        date_range = price_data[(price_data['date'] >= start_date) & (price_data['date'] <= end_date)]['date']

        if date_range.empty:
            return pd.DataFrame(columns=['date'])

        # 모든 주식을 위한 빈 데이터프레임 생성 - 단편화 방지
        # 먼저 모든 가능한 주식 목록 생성
        all_stocks = set()
        for weights in weights_dict.values():
            all_stocks.update(weights.keys())

        # 모든 날짜와 주식을 위한 딕셔너리 초기화
        weights_by_date = {date: {stock: 0.0 for stock in all_stocks} for date in date_range}

        # 각 날짜 처리
        current_weights = None
        for date in date_range:
            # 이것이 리밸런싱 날짜인지 확인
            rebalance_index = bisect.bisect_right(sorted(list(weights_dict.keys())), date) - 1
            if rebalance_index >= 0:
                rebalance_date = sorted(list(weights_dict.keys()))[rebalance_index]
                new_weights = weights_dict[rebalance_date]

                # 리밸런싱 시간이면 현재 가중치 업데이트
                if current_weights is None or date == rebalance_date:
                    current_weights = new_weights.copy()
                # 그렇지 않으면 가격 변화에 따라 가중치 조정
                else:
                    date_idx = date_range[date_range < date].index[-1] if len(date_range[date_range < date]) > 0 else -1
                    if date_idx >= 0:
                        prev_date = date_range.iloc[date_idx]

                        # 두 날짜의 가격 가져오기
                        prev_price_data = price_data[price_data['date'] == prev_date]
                        curr_price_data = price_data[price_data['date'] == date]

                        if not prev_price_data.empty and not curr_price_data.empty:
                            prev_prices = prev_price_data.iloc[0].drop('date')
                            curr_prices = curr_price_data.iloc[0].drop('date')

                            # 각 주식의 수익률 계산
                            stocks_to_remove = []
                            for stock in list(current_weights.keys()):
                                if stock in prev_prices and stock in curr_prices and prev_prices[stock] > 0:
                                    stock_return = curr_prices[stock] / prev_prices[stock]
                                    current_weights[stock] *= stock_return
                                else:
                                    # 가격 데이터가 없는 경우 제거 리스트에 추가
                                    stocks_to_remove.append(stock)

                            # 가격 데이터가 없는 주식 제거
                            for stock in stocks_to_remove:
                                current_weights.pop(stock, None)

                            # 시장 중립 포트폴리오의 경우 합이 0이 되도록 재정규화
                            weight_sum = sum(current_weights.values()) if current_weights else 0

                            # 이것이 시장 중립 포트폴리오인지 확인 (합이 0에 가까움)
                            if abs(weight_sum) < 0.1:  # 작은 편차 허용
                                # 시장 중립성 보장을 위한 조정
                                if abs(weight_sum) > 1e-10 and current_weights:  # 유의미하게 벗어난 경우만 조정
                                    adjustment = weight_sum / len(current_weights)
                                    for stock in current_weights:
                                        current_weights[stock] -= adjustment
                            # 그렇지 않으면 롱온리 포트폴리오로 취급 (합이 1)
                            elif weight_sum > 0 and current_weights:
                                for stock in current_weights:
                                    current_weights[stock] = current_weights[stock] / weight_sum

                            # 소수점 4자리로 반올림
                            current_weights = {k: round(v, 4) for k, v in
                                               current_weights.items()} if current_weights else {}

                # 현재 날짜의 가중치 업데이트
                if current_weights:
                    for stock, weight in current_weights.items():
                        weights_by_date[date][stock] = weight

        # 데이터프레임 생성을 위한 리스트 초기화
        data_rows = []

        # 각 날짜별로 가중치 딕셔너리를 데이터프레임 행으로 변환
        for date, weights in weights_by_date.items():
            row = {'date': date}
            row.update(weights)
            data_rows.append(row)

        # 단일 데이터프레임 생성 (단편화 방지)
        result_df = pd.DataFrame(data_rows)

        return result_df
    except Exception as e:
        print(f"포트폴리오 성과 구축 중 오류: {e}")
        return pd.DataFrame(columns=['date'])

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

def calculate_performance_metrics(returns_data, windows=[21,63,126,252,756,1260]):
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


def save_results_to_csv(results, output_dir='factor_portfolio_output'):
    """결과를 CSV로 저장하는 함수 개선"""
    try:
        if not results:
            print("저장할 결과가 없습니다.")
            return

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 1. 포트폴리오 가중치 저장
        # 1.1 팩터 포트폴리오 가중치
        if 'portfolio_values' in results:
            for portfolio_type, weights_dict in results['portfolio_values'].items():
                if not weights_dict.empty:
                    weights_dict.to_csv(f"{output_dir}/{portfolio_type}_weights.csv", index=False)

        # 1.2 개별 지표 포트폴리오 가중치
        if 'metric_portfolio_values' in results and results['metric_portfolio_values']:
            for metric_name, weights_dict in results['metric_portfolio_values'].items():
                if not weights_dict.empty:
                    weights_dict.to_csv(f"{output_dir}/metric_{metric_name}_weights.csv", index=False)

        # 2. 일별 포트폴리오 수익률 저장
        # 2.1 팩터 포트폴리오 수익률
        if ('portfolio_returns' in results and results['portfolio_returns'] and
                'benchmark' in results['portfolio_returns']):

            factor_returns_df = pd.DataFrame({'date': results['portfolio_returns']['benchmark']['date']})
            for portfolio_type, returns_data in results['portfolio_returns'].items():
                if 'return' in returns_data.columns:
                    factor_returns_df[f'{portfolio_type}_return'] = returns_data['return']

            factor_returns_df.to_csv(f"{output_dir}/factor_portfolio_returns.csv", index=False)

        # 2.2 개별 지표 포트폴리오 수익률
        if 'metric_portfolio_returns' in results and results['metric_portfolio_returns']:
            try:
                # 안전하게 첫 번째 지표 포트폴리오 수익률 가져오기
                metric_keys = list(results['metric_portfolio_returns'].keys())
                if metric_keys:
                    first_metric = metric_keys[0]
                    first_returns = results['metric_portfolio_returns'][first_metric]

                    if isinstance(first_returns, pd.DataFrame) and 'date' in first_returns.columns:
                        metric_returns_df = pd.DataFrame({'date': first_returns['date']})

                        # 모든 지표의 수익률 추가
                        for metric_name, returns_data in results['metric_portfolio_returns'].items():
                            if isinstance(returns_data, pd.DataFrame) and 'return' in returns_data.columns:
                                metric_returns_df[f'{metric_name}_return'] = returns_data['return']

                        metric_returns_df.to_csv(f"{output_dir}/metric_portfolio_returns.csv", index=False)
                    else:
                        print("경고: 첫 번째 지표 포트폴리오 수익률 데이터가 올바른 형식이 아닙니다.")
                else:
                    print("경고: 지표 포트폴리오 수익률이 비어 있습니다.")
            except Exception as e:
                print(f"지표 포트폴리오 수익률 저장 중 오류: {e}")

        # 3. 성능 지표 저장
        # 3.1 팩터 성능 지표
        if 'performance_metrics' in results and results['performance_metrics']:
            factor_metrics_dict = {}

            for portfolio_type, metrics in results['performance_metrics'].items():
                for metric_name, value in metrics.items():
                    if metric_name not in factor_metrics_dict:
                        factor_metrics_dict[metric_name] = {}
                    factor_metrics_dict[metric_name][portfolio_type] = value

            if factor_metrics_dict:
                factor_metrics_df = pd.DataFrame(factor_metrics_dict)
                factor_metrics_df.to_csv(f"{output_dir}/factor_performance_metrics.csv")

        # 3.2 개별 지표 성능 지표
        if 'metric_performance_metrics' in results and results['metric_performance_metrics']:
            metric_performance_dict = {}

            for metric_name, metrics in results['metric_performance_metrics'].items():
                for metric_window, value in metrics.items():
                    if metric_window not in metric_performance_dict:
                        metric_performance_dict[metric_window] = {}
                    metric_performance_dict[metric_window][metric_name] = value

            if metric_performance_dict:
                metric_performance_df = pd.DataFrame(metric_performance_dict)
                metric_performance_df.to_csv(f"{output_dir}/metric_performance_metrics.csv")

        # 4. IC 결과 저장
        if 'factor_ic' in results:
            for factor_type, ic_list in results['factor_ic'].items():
                if ic_list:
                    ic_df = pd.DataFrame(ic_list)
                    ic_df.to_csv(f"{output_dir}/{factor_type}_ic.csv", index=False)

        # 5. 팩터 분위 저장
        if 'factor_quantiles' in results:
            for factor_type, quantiles_dict in results['factor_quantiles'].items():
                if not quantiles_dict:
                    continue

                # 모든 분위를 하나의 데이터프레임으로 결합
                all_dates = []
                all_stocks = []
                all_quantiles = []

                for date, quantile_series in quantiles_dict.items():
                    for stock, quantile in quantile_series.items():
                        all_dates.append(date)
                        all_stocks.append(stock)
                        all_quantiles.append(quantile)

                if all_dates:  # 비어있지 않은 경우에만 저장
                    quantiles_df = pd.DataFrame({
                        'date': all_dates,
                        'stock': all_stocks,
                        'quantile': all_quantiles
                    })
                    quantiles_df.to_csv(f"{output_dir}/{factor_type}_quantiles.csv", index=False)

        # 6. 개별 지표 분위 저장
        if 'metric_quantiles' in results and results['metric_quantiles']:
            for metric_name, quantiles_dict in results['metric_quantiles'].items():
                if not quantiles_dict:
                    continue

                # 모든 분위를 하나의 데이터프레임으로 결합
                all_dates = []
                all_stocks = []
                all_quantiles = []

                for date, quantile_series in quantiles_dict.items():
                    for stock, quantile in quantile_series.items():
                        all_dates.append(date)
                        all_stocks.append(stock)
                        all_quantiles.append(quantile)

                if all_dates:  # 비어있지 않은 경우에만 저장
                    quantiles_df = pd.DataFrame({
                        'date': all_dates,
                        'stock': all_stocks,
                        'quantile': all_quantiles
                    })
                    quantiles_df.to_csv(f"{output_dir}/metric_{metric_name}_quantiles.csv", index=False)

        # 7. 제외된 티커 목록 저장
        pd.DataFrame({'excluded_tickers': EXCLUDED_TICKERS}).to_csv(f"{output_dir}/excluded_tickers.csv", index=False)

        # 8. 요약 성능 비교 테이블 생성
        # 8.1 팩터 성능 요약
        if 'performance_metrics' in results and results['performance_metrics']:
            factor_perf_summary = pd.DataFrame(index=results['performance_metrics'].keys())

            for period in [21, 63, 126, 252]:  # 1M, 3M, 6M, 1Y
                returns_col = f"{period}d_return"
                sharpe_col = f"{period}d_sharpe"

                factor_perf_summary[f"{period}d_Return"] = [
                    results['performance_metrics'][portfolio].get(returns_col, np.nan)
                    for portfolio in factor_perf_summary.index
                ]

                factor_perf_summary[f"{period}d_Sharpe"] = [
                    results['performance_metrics'][portfolio].get(sharpe_col, np.nan)
                    for portfolio in factor_perf_summary.index
                ]

            factor_perf_summary.to_csv(f"{output_dir}/factor_performance_summary.csv")

        # 8.2 지표 성능 요약
        if 'metric_performance_metrics' in results and results['metric_performance_metrics']:
            metric_perf_summary = pd.DataFrame(index=results['metric_performance_metrics'].keys())

            for period in [21, 63, 126, 252]:  # 1M, 3M, 6M, 1Y
                returns_col = f"{period}d_return"
                sharpe_col = f"{period}d_sharpe"

                metric_perf_summary[f"{period}d_Return"] = [
                    results['metric_performance_metrics'][metric].get(returns_col, np.nan)
                    for metric in metric_perf_summary.index
                ]

                metric_perf_summary[f"{period}d_Sharpe"] = [
                    results['metric_performance_metrics'][metric].get(sharpe_col, np.nan)
                    for metric in metric_perf_summary.index
                ]

            metric_perf_summary.to_csv(f"{output_dir}/metric_performance_summary.csv")

        print(f"결과가 {output_dir}/ 디렉토리에 저장되었습니다.")
    except Exception as e:
        print(f"결과 저장 중 오류: {e}")

def calculate_momentum_quantile_betas(data_dict, factor_quantiles, start_date, end_date, window=63):
    """
    모멘텀 퀀타일 포트폴리오와 SPX 지수 간의 베타를 계산합니다.
    SPX Index를 pr_res_bd에서 직접 가져오도록 수정
    """
    try:
        # 필요한 데이터 확인
        if 'pr_bd' not in data_dict or data_dict['pr_bd'].empty:
            print("오류: 가격 데이터가 없습니다.")
            return None

        # SPX Index 데이터가 있는지 확인 (pr_res_bd에서 가져옴)
        if 'pr_res_bd' not in data_dict or data_dict['pr_res_bd'].empty:
            print("오류: SPX Index 데이터를 포함하는 pr_res_bd가 없습니다.")
            return None

        # 분석 기간 동안의 가격 데이터 가져오기
        price_data = data_dict['pr_bd'][
            (data_dict['pr_bd']['date'] >= start_date) &
            (data_dict['pr_bd']['date'] <= end_date)
            ].copy()

        if price_data.empty:
            print("오류: 지정된 날짜 범위에 대한 가격 데이터가 없습니다.")
            return None

        # SPX Index 데이터가 없으면 pr_res_bd에서 가져오기
        if 'SPX Index' not in price_data.columns:
            print("SPX Index를 pr_res_bd에서 가져옵니다.")
            spx_data = data_dict['pr_res_bd'][
                (data_dict['pr_res_bd']['date'] >= start_date) &
                (data_dict['pr_res_bd']['date'] <= end_date)
                ]

            if 'SPX Index' not in spx_data.columns:
                print("오류: pr_res_bd에 SPX Index 열이 없습니다.")
                return None

            # price_data와 spx_data 병합하여 SPX Index 추가
            price_data = price_data.merge(
                spx_data[['date', 'SPX Index']],
                on='date',
                how='left'
            )

        # SPX Index가 여전히 없으면 에러 반환
        if 'SPX Index' not in price_data.columns:
            print("오류: SPX Index 데이터를 찾을 수 없습니다.")
            return None

        # 모든 주식과 SPX의 일일 수익률 계산
        price_data_pivot = price_data.set_index('date')
        returns_data = price_data_pivot.pct_change().dropna()

        # SPX 수익률 별도로 가져오기
        if 'SPX Index' not in returns_data.columns:
            print("오류: 수익률 계산 후 SPX Index 열이 없습니다.")
            return None

        spx_returns = returns_data['SPX Index']

        # 모멘텀 퀀타일이 있는지 확인
        if 'momentum' not in factor_quantiles or not factor_quantiles['momentum']:
            print("오류: 모멘텀 퀀타일 데이터가 없습니다.")
            return None

        # 리밸런싱 날짜 가져오기
        rebalance_dates = sorted(factor_quantiles['momentum'].keys())
        if not rebalance_dates:
            print("오류: 리밸런싱 날짜가 없습니다.")
            return None

        # 각 퀀타일별 베타를 저장할 데이터프레임 초기화
        all_dates = returns_data.index
        beta_df = pd.DataFrame(index=all_dates)

        # 빈 수익률로 퀀타일 포트폴리오 초기화
        for q in range(1, 6):
            beta_df[f'Momentum_Q{q}_Beta'] = np.nan

        # 각 퀀타일 포트폴리오의 수익률 계산
        quantile_returns = {q: pd.Series(index=all_dates, dtype='float64') for q in range(1, 6)}

        # 각 리밸런싱 날짜마다 주식을 퀀타일에 할당하고 수익률 계산
        for i in range(len(rebalance_dates)):
            current_date = rebalance_dates[i]

            # 다음 리밸런싱 날짜 또는 마지막 리밸런싱인 경우 end_date 사용
            if i < len(rebalance_dates) - 1:
                next_date = rebalance_dates[i + 1]
            else:
                next_date = end_date

            # 이 리밸런싱 기간의 모든 날짜 가져오기
            period_dates = [d for d in all_dates if d >= current_date and d < next_date]

            # 이 리밸런싱 날짜의 모멘텀 퀀타일 가져오기
            if current_date not in factor_quantiles['momentum']:
                print(f"경고: {current_date}에 대한 모멘텀 퀀타일 정보가 없습니다.")
                continue

            momentum_quantiles = factor_quantiles['momentum'][current_date]
            if not isinstance(momentum_quantiles, pd.Series) or momentum_quantiles.empty:
                print(f"경고: {current_date}에 대한 모멘텀 퀀타일이 비어 있거나 Series 형식이 아닙니다.")
                continue

            # 각 퀀타일의 동일 가중 수익률 계산
            for date in period_dates:
                if date in returns_data.index:
                    # 각 퀀타일에서 주식 가져오기 및 평균 수익률 계산
                    for q in range(1, 6):
                        # 이 퀀타일에 있는 주식 선택
                        stocks_in_quantile = [stock for stock, quant in momentum_quantiles.items()
                                              if quant == q and stock in returns_data.columns]

                        if stocks_in_quantile:
                            # 이 퀀타일의 동일 가중 수익률 계산
                            q_return = returns_data.loc[date, stocks_in_quantile].mean()
                            quantile_returns[q][date] = q_return

        # 각 퀀타일의 롤링 베타 계산
        for q in range(1, 6):
            # 수익률을 올바른 인덱스가 있는 Series로 변환
            q_returns = quantile_returns[q]

            if q_returns.isna().all():
                print(f"경고: 퀀타일 {q}에 대한 수익률 데이터가 없습니다.")
                continue

            # 롤링 공분산 계산 (최소 기간 요구 추가)
            rolling_cov = q_returns.rolling(window=window, min_periods=max(int(window / 2), 1)).cov(spx_returns)

            # SPX의 롤링 분산 계산 (최소 기간 요구 추가)
            rolling_var = spx_returns.rolling(window=window, min_periods=max(int(window / 2), 1)).var()

            # 0으로 나누기 방지
            mask = rolling_var > 0
            beta = pd.Series(np.nan, index=rolling_cov.index)
            beta[mask] = rolling_cov[mask] / rolling_var[mask]

            # 베타 값 할당
            beta_df[f'Momentum_Q{q}_Beta'] = beta

        # 인덱스를 재설정하여 날짜를 열로 만들기
        beta_df = beta_df.reset_index().rename(columns={'index': 'date'})

        return beta_df
    except Exception as e:
        print(f"모멘텀 퀀타일 베타 계산 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_momentum_beta_to_csv(beta_df, output_dir='factor_portfolio_output'):
    """모멘텀 퀀타일 베타를 CSV로 저장"""
    try:
        if beta_df is None or beta_df.empty:
            print("경고: 저장할 모멘텀 베타 데이터가 없습니다.")
            return

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        beta_df.to_csv(f"{output_dir}/momentum_quantile_betas.csv", index=False)
        print(f"모멘텀 퀀타일 베타가 {output_dir}/momentum_quantile_betas.csv에 저장되었습니다.")
    except Exception as e:
        print(f"모멘텀 베타 저장 중 오류: {e}")


def build_factor_portfolios(data_dict, start_date, end_date, excluded_tickers=EXCLUDED_TICKERS):
    """모든 팩터 포트폴리오를 구축하고 성과를 추적합니다."""
    print(f"{start_date}부터 {end_date}까지 팩터 포트폴리오 구축 중...")

    # 결과 초기화
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

    # 개별 지표 포트폴리오 결과 초기화
    metric_portfolio_weights = {}
    metric_quantiles = {}

    # 날짜 범위의 모든 날짜 가져오기
    all_dates = data_dict['pr_bd'][
        (data_dict['pr_bd']['date'] >= start_date) &
        (data_dict['pr_bd']['date'] <= end_date)
        ]['date']

    if all_dates.empty:
        print("오류: 지정된 날짜 범위에 대한 가격 데이터가 없습니다.")
        return None

    # 리밸런싱을 위한 분기 말 날짜 찾기
    rebalance_dates = []
    for date in all_dates:
        if date.month in [3, 6, 9, 12] and date.day > 25:
            next_month = (date.replace(day=1) + pd.DateOffset(months=1)).replace(day=1)
            if (next_month - date).days <= 7:  # 다음 달까지 7일 이내인 경우
                rebalance_dates.append(date)

    print(f"{len(rebalance_dates)}개의 리밸런싱 날짜 발견")

    # 각 리밸런싱 날짜에 대한 포트폴리오 구축
    for rebalance_date in tqdm(rebalance_dates, desc="포트폴리오 구축 중"):
        try:
            # 벤치마크 포트폴리오 생성
            benchmark_weights = create_benchmark_portfolio(
                data_dict['cap_us_bd'],
                rebalance_date,
                excluded_tickers=excluded_tickers
            )

            if not benchmark_weights:
                print(f"경고: {rebalance_date}에 대한 벤치마크 포트폴리오를 생성할 수 없습니다.")
                continue

            portfolio_weights['benchmark'][rebalance_date] = benchmark_weights

            # 팩터 포트폴리오 생성
            growth_quantiles, growth_scores, growth_metrics = create_growth_portfolio(
                data_dict, rebalance_date, excluded_tickers=excluded_tickers
            )

            value_quantiles, value_scores, value_metrics = create_value_portfolio(
                data_dict, rebalance_date, excluded_tickers=excluded_tickers
            )

            momentum_quantiles, momentum_scores, momentum_metrics = create_momentum_portfolio(
                data_dict, rebalance_date, excluded_tickers=excluded_tickers
            )

            low_vol_quantiles, low_vol_scores, low_vol_metrics = create_low_vol_portfolio(
                data_dict, rebalance_date, excluded_tickers=excluded_tickers
            )

            quality_quantiles, quality_scores, quality_metrics = create_quality_portfolio(
                data_dict, rebalance_date, excluded_tickers=excluded_tickers
            )

            # 분위수와 지표 분위수 저장
            if not growth_quantiles.empty:
                factor_quantiles['growth'][rebalance_date] = growth_quantiles
                factor_metrics['growth'][rebalance_date] = growth_metrics

            if not value_quantiles.empty:
                factor_quantiles['value'][rebalance_date] = value_quantiles
                factor_metrics['value'][rebalance_date] = value_metrics

            if not momentum_quantiles.empty:
                factor_quantiles['momentum'][rebalance_date] = momentum_quantiles
                factor_metrics['momentum'][rebalance_date] = momentum_metrics

            if not low_vol_quantiles.empty:
                factor_quantiles['low_vol'][rebalance_date] = low_vol_quantiles
                factor_metrics['low_vol'][rebalance_date] = low_vol_metrics

            if not quality_quantiles.empty:
                factor_quantiles['quality'][rebalance_date] = quality_quantiles
                factor_metrics['quality'][rebalance_date] = quality_metrics

            # 분위수에 따라 가중치 조정
            if not growth_quantiles.empty:
                growth_weights = adjust_weights_by_quantile(benchmark_weights, growth_quantiles)
                portfolio_weights['growth'][rebalance_date] = growth_weights

            if not value_quantiles.empty:
                value_weights = adjust_weights_by_quantile(benchmark_weights, value_quantiles)
                portfolio_weights['value'][rebalance_date] = value_weights

            if not momentum_quantiles.empty:
                momentum_weights = adjust_weights_by_quantile(benchmark_weights, momentum_quantiles)
                portfolio_weights['momentum'][rebalance_date] = momentum_weights

            if not low_vol_quantiles.empty:
                low_vol_weights = adjust_weights_by_quantile(benchmark_weights, low_vol_quantiles)
                portfolio_weights['low_vol'][rebalance_date] = low_vol_weights

            if not quality_quantiles.empty:
                quality_weights = adjust_weights_by_quantile(benchmark_weights, quality_quantiles)
                portfolio_weights['quality'][rebalance_date] = quality_weights

            # 개별 지표 포트폴리오 생성
            # 이는 각 개별 지표에 대한 시장 중립 롱-숏 포트폴리오를 생성합니다
            # 가중치 합이 0이 됩니다
            try:
                metric_weights, metric_quant = create_metric_portfolios(
                    data_dict, rebalance_date, benchmark_weights, excluded_tickers
                )

                # 지표 포트폴리오 가중치 및 분위수 저장
                for metric_name, weights in metric_weights.items():
                    if metric_name not in metric_portfolio_weights:
                        metric_portfolio_weights[metric_name] = {}

                    metric_portfolio_weights[metric_name][rebalance_date] = weights

                for metric_name, quantiles in metric_quant.items():
                    if metric_name not in metric_quantiles:
                        metric_quantiles[metric_name] = {}

                    metric_quantiles[metric_name][rebalance_date] = quantiles
            except Exception as e:
                print(f"개별 지표 포트폴리오 생성 중 오류: {e}")

            # 각 팩터에 대한 정보 계수 계산
            # IC 계산을 위한 다음 달 수익률 찾기
            next_month = rebalance_date + pd.DateOffset(months=1)
            next_month_dates = data_dict['pr_bd'][
                (data_dict['pr_bd']['date'] > rebalance_date) &
                (data_dict['pr_bd']['date'] <= next_month)
                ]['date']

            if not next_month_dates.empty:
                future_date = next_month_dates.max()

                # 현재 및 미래 가격 가져오기
                current_price_data = data_dict['pr_bd'][data_dict['pr_bd']['date'] == rebalance_date]
                future_price_data = data_dict['pr_bd'][data_dict['pr_bd']['date'] == future_date]

                if not current_price_data.empty and not future_price_data.empty:
                    current_prices = current_price_data.iloc[0]
                    future_prices = future_price_data.iloc[0]

                    # 벤치마크 주식의 수익률 계산
                    future_returns = {}
                    for stock in benchmark_weights.keys():
                        if (stock in current_prices and stock in future_prices and
                                current_prices[stock] > 0):
                            future_returns[stock] = future_prices[stock] / current_prices[stock] - 1

                    # 각 팩터에 대한 IC 계산
                    if future_returns:
                        returns_series = pd.Series(future_returns)

                        # 수익률이 있는 주식만 포함하도록 점수 필터링
                        if not growth_scores.empty:
                            valid_stocks = list(set(returns_series.index) & set(growth_scores.index))
                            if valid_stocks:
                                factor_ic['growth'].append({
                                    'date': rebalance_date,
                                    'ic': calculate_ic(growth_scores[valid_stocks], returns_series[valid_stocks])
                                })

                        if not value_scores.empty:
                            valid_stocks = list(set(returns_series.index) & set(value_scores.index))
                            if valid_stocks:
                                factor_ic['value'].append({
                                    'date': rebalance_date,
                                    'ic': calculate_ic(value_scores[valid_stocks], returns_series[valid_stocks])
                                })

                        if not momentum_scores.empty:
                            valid_stocks = list(set(returns_series.index) & set(momentum_scores.index))
                            if valid_stocks:
                                factor_ic['momentum'].append({
                                    'date': rebalance_date,
                                    'ic': calculate_ic(momentum_scores[valid_stocks], returns_series[valid_stocks])
                                })

                        if not low_vol_scores.empty:
                            valid_stocks = list(set(returns_series.index) & set(low_vol_scores.index))
                            if valid_stocks:
                                factor_ic['low_vol'].append({
                                    'date': rebalance_date,
                                    'ic': calculate_ic(low_vol_scores[valid_stocks], returns_series[valid_stocks])
                                })

                        if not quality_scores.empty:
                            valid_stocks = list(set(returns_series.index) & set(quality_scores.index))
                            if valid_stocks:
                                factor_ic['quality'].append({
                                    'date': rebalance_date,
                                    'ic': calculate_ic(quality_scores[valid_stocks], returns_series[valid_stocks])
                                })
        except Exception as e:
            print(f"{rebalance_date}에 대한 포트폴리오 구축 중 오류: {e}")

    # 일일 포트폴리오 가치 및 수익률 계산
    print("포트폴리오 성과 구축 중...")

    # 1. 팩터 포트폴리오
    portfolio_values = {}
    portfolio_returns = {}

    for portfolio_type in portfolio_weights:
        if portfolio_weights[portfolio_type]:
            portfolio_values[portfolio_type] = build_portfolio_performance(
                data_dict['pr_bd'], portfolio_weights[portfolio_type], start_date, end_date
            )

            if not portfolio_values[portfolio_type].empty:
                portfolio_returns[portfolio_type] = calculate_daily_returns(
                    data_dict['pr_bd'], portfolio_values[portfolio_type]
                )

    # 2. 개별 지표 포트폴리오
    metric_portfolio_values = {}
    metric_portfolio_returns = {}

    for metric_name in metric_portfolio_weights:
        if metric_portfolio_weights[metric_name]:
            metric_portfolio_values[metric_name] = build_portfolio_performance(
                data_dict['pr_bd'], metric_portfolio_weights[metric_name], start_date, end_date
            )

            if not metric_portfolio_values[metric_name].empty:
                metric_portfolio_returns[metric_name] = calculate_daily_returns(
                    data_dict['pr_bd'], metric_portfolio_values[metric_name]
                )

    # 성능 지표 계산
    print("성능 지표 계산 중...")

    # 1. 팩터 포트폴리오
    performance_metrics = {}
    for portfolio_type in portfolio_returns:
        if portfolio_returns[portfolio_type] is not None and not portfolio_returns[portfolio_type].empty:
            performance_metrics[portfolio_type] = calculate_performance_metrics(
                portfolio_returns[portfolio_type],
                windows=[21, 63, 126, 252, 756, 1260]  # 1개월, 3개월, 6개월, 1년, 3년, 5년
            )

    # 2. 개별 지표 포트폴리오
    metric_performance_metrics = {}
    for metric_name in metric_portfolio_returns:
        if metric_portfolio_returns[metric_name] is not None and not metric_portfolio_returns[metric_name].empty:
            metric_performance_metrics[metric_name] = calculate_performance_metrics(
                metric_portfolio_returns[metric_name],
                windows=[21, 63, 126, 252, 756, 1260]  # 1개월, 3개월, 6개월, 1년, 3년, 5년
            )

    # 결과 객체 생성
    results = {
        'portfolio_weights': portfolio_weights,
        'factor_quantiles': factor_quantiles,
        'factor_metrics': factor_metrics,
        'factor_ic': factor_ic,
        'portfolio_values': portfolio_values,
        'portfolio_returns': portfolio_returns,
        'performance_metrics': performance_metrics,

        # 개별 지표 포트폴리오 결과
        'metric_portfolio_weights': metric_portfolio_weights,
        'metric_quantiles': metric_quantiles,
        'metric_portfolio_values': metric_portfolio_values,
        'metric_portfolio_returns': metric_portfolio_returns,
        'metric_performance_metrics': metric_performance_metrics
    }

    return results


def load_data():
    """모든 데이터 소스를 로드하고 분석을 위해 준비합니다."""
    # 데이터 사전 정의
    data = {}

    # 제공된 코드에서 데이터 로드
    data['pr_bd'] = pr_bd
    if 'pr_res_bd' in globals():
        data['pr_res_bd'] = pr_res_bd  # SPX Index 포함
    data['cap_us_bd'] = cap_us_bd

    # 추가 데이터가 있으면 추가
    if 'eps_us' in globals():
        data['eps_us_bd'] = eps_us
    if 'sales_us' in globals():
        data['sales_us_bd'] = sales_us
    if 'opm_us' in globals():
        data['opm_us_bd'] = opm_us
    if 'roe_us' in globals():
        data['roe_us_bd'] = roe_us_bd
    if 'pe_us' in globals():
        data['pe_us_bd'] = pe_us_bd
    if 'peg_us' in globals():
        data['peg_us_bd'] = peg_us_bd
    if 'pb_us' in globals():
        data['pb_us_bd'] = pb_us_bd

    # Factset 데이터
    data['us_eps_surprise_bd'] = us_eps_surprise_bd
    data['us_sales_surprise_bd'] = us_sales_surprise_bd
    data['opmargin_fact_us_bd'] = opmargin_fact_us_bd
    data['evebit_fact_us_bd'] = evebit_fact_us_bd
    data['fcf_fact_us_bd'] = fcf_fact_us_bd
    data['eps_fact_us_bd'] = eps_fact_us_bd
    data['sales_fact_us_bd'] = sales_fact_us_bd
    data['revision_fact_eps_bd'] = revision_fact_eps_bd
    data['revision_fact_sales_bd'] = revision_fact_sales_bd

    # 7일 롤링 합을 이용한 센티먼트 데이터 추가
    if 'senti_us' in globals():
        # 먼저 데이터 병합
        senti_merged = bd[['date']].merge(senti_us, on='date', how='left')

        # 롤링 계산을 위해 날짜를 인덱스로 설정
        senti_processed = senti_merged.set_index('date')

        # 올바른 롤링 계산을 위해 날짜별로 정렬
        senti_processed = senti_processed.sort_index()

        # 7일 롤링 합 계산
        senti_rolling = senti_processed.rolling(window='7D').sum()

        # 날짜를 다시 열로 가져오기 위해 인덱스 재설정
        senti_rolling = senti_rolling.reset_index()

        data['senti_us_bd'] = senti_rolling

    return data


def validate_data_structure(data_dict):
    """데이터 구조 유효성 검증 함수"""
    issues = []

    # 필수 데이터 키 확인
    required_keys = ['pr_bd', 'cap_us_bd', 'pr_res_bd']
    for key in required_keys:
        if key not in data_dict:
            issues.append(f"필수 키 '{key}'가 데이터 사전에 없습니다.")
        elif not isinstance(data_dict[key], pd.DataFrame):
            issues.append(f"'{key}'가 DataFrame이 아닙니다.")
        elif data_dict[key].empty:
            issues.append(f"'{key}' DataFrame이 비어 있습니다.")
        elif 'date' not in data_dict[key].columns:
            issues.append(f"'{key}' DataFrame에 'date' 열이 없습니다.")

    # pr_res_bd에 SPX Index가 있는지 확인
    if 'pr_res_bd' in data_dict and isinstance(data_dict['pr_res_bd'], pd.DataFrame) and not data_dict[
        'pr_res_bd'].empty:
        if 'SPX Index' not in data_dict['pr_res_bd'].columns:
            issues.append("'pr_res_bd'에 'SPX Index' 열이 없습니다.")

    return issues


def main():
    """개선된 메인 실행 함수"""
    print("데이터 로딩 중...")
    data_dict = load_data()

    # 데이터 구조 유효성 검사
    issues = validate_data_structure(data_dict)
    if issues:
        print("데이터 구조에 문제가 있습니다:")
        for i, issue in enumerate(issues):
            print(f"{i + 1}. {issue}")

    # 날짜 범위 정의 - 2023년으로 제한
    start_date = pd.Timestamp('2013-01-01')
    end_date = pd.Timestamp('2023-12-31')

    print(f"{start_date}부터 {end_date}까지 팩터 포트폴리오 구축 중...")
    try:
        results = build_factor_portfolios(data_dict, start_date, end_date, excluded_tickers=EXCLUDED_TICKERS)

        if results is None:
            print("팩터 포트폴리오 구축에 실패했습니다.")
            return None, None

        print("모멘텀 퀀타일 베타 계산 중...")
        momentum_betas = calculate_momentum_quantile_betas(
            data_dict,
            results['factor_quantiles'],
            start_date,
            end_date
        )

        print("결과를 CSV로 저장 중...")
        save_results_to_csv(results)

        # 모멘텀 베타 별도로 저장
        if momentum_betas is not None:
            save_momentum_beta_to_csv(momentum_betas)
        else:
            print("모멘텀 베타 계산 중 오류가 발생했습니다.")

        print("완료!")
        return results, momentum_betas
    except Exception as e:
        print(f"팩터 포트폴리오 구축 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    try:
        results, momentum_betas = main()
        if results is not None:
            print("팩터 포트폴리오 분석 완료!")
        else:
            print("오류로 인해 분석이 완료되지 않았습니다.")
    except Exception as e:
        print(f"메인 실행 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()