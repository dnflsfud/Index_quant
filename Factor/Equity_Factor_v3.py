t bisect

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
import bisect
import pandas as pd
import numpy as np
import os
import time
import sys
import re
from tqdm import tqdm
from datetime import timedelta, date
import traceback

# 제외할 티커 목록
EXCLUDED_TICKERS = [
    'SAP US Equity',
    'BABA US Equity',
    'TCEHY US Equity',
    'BIDU US Equity',
    'BRK/B US Equity'
]


# 진행 상황 추적 클래스
class GlobalProgress:
    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time

    def update(self, step=1, force=False):
        self.current_step += step
        current_time = time.time()

        # 오버헤드 감소를 위해 0.5초마다만 디스플레이 업데이트
        if force or (current_time - self.last_update_time) >= 0.5:
            percent = min(100, int(self.current_step * 100 / self.total_steps))
            elapsed = current_time - self.start_time

            # 남은 시간 추정
            if self.current_step > 0:
                remaining = (elapsed / self.current_step) * (self.total_steps - self.current_step)
                time_str = f" | 경과: {elapsed:.1f}초 | 남음: {remaining:.1f}초"
            else:
                time_str = f" | 경과: {elapsed:.1f}초"

            # 진행 막대 생성
            bar_length = 30
            filled_length = int(bar_length * self.current_step / self.total_steps)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)

            # 진행 상황 출력
            sys.stdout.write(f"\r진행: [{bar}] {percent}%{time_str}")
            sys.stdout.flush()
            self.last_update_time = current_time

    def finish(self):
        self.update(0, force=True)
        sys.stdout.write('\n')
        sys.stdout.flush()


# 데이터 로드 함수
def load_data():
    """모든 데이터 소스를 로드하고 분석을 위해 준비합니다."""
    # 데이터 사전 정의
    data = {}

    # 주요 데이터 로드
    data['pr_bd'] = pr_bd
    if 'pr_res_bd' in globals():
        data['pr_res_bd'] = pr_res_bd  # SPX Index 포함
    data['cap_us_bd'] = cap_us_bd

    # 기타 데이터 로드
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
    if 'us_eps_surprise_bd' in globals():
        data['us_eps_surprise_bd'] = us_eps_surprise_bd
    if 'us_sales_surprise_bd' in globals():
        data['us_sales_surprise_bd'] = us_sales_surprise_bd
    if 'opmargin_fact_us_bd' in globals():
        data['opmargin_fact_us_bd'] = opmargin_fact_us_bd
    if 'evebit_fact_us_bd' in globals():
        data['evebit_fact_us_bd'] = evebit_fact_us_bd
    if 'fcf_fact_us_bd' in globals():
        data['fcf_fact_us_bd'] = fcf_fact_us_bd
    if 'eps_fact_us_bd' in globals():
        data['eps_fact_us_bd'] = eps_fact_us_bd
    if 'sales_fact_us_bd' in globals():
        data['sales_fact_us_bd'] = sales_fact_us_bd
    if 'revision_fact_eps_bd' in globals():
        data['revision_fact_eps_bd'] = revision_fact_eps_bd
    if 'revision_fact_sales_bd' in globals():
        data['revision_fact_sales_bd'] = revision_fact_sales_bd

    # 센티먼트 데이터 처리
    if 'senti_us' in globals():
        try:
            # 데이터 병합
            senti_merged = bd[['date']].merge(senti_us, on='date', how='left')

            # 롤링 계산을 위해 날짜를 인덱스로 설정
            senti_processed = senti_merged.set_index('date')

            # 날짜별로 정렬
            senti_processed = senti_processed.sort_index()

            # 7일 롤링 합 계산
            senti_rolling = senti_processed.rolling(window='7D').sum()

            # 날짜를 다시 열로 가져오기 위해 인덱스 재설정
            senti_rolling = senti_rolling.reset_index()

            data['senti_us_bd'] = senti_rolling
        except Exception as e:
            print(f"센티먼트 데이터 처리 중 오류: {e}")

    return data


# 데이터 구조 유효성 검증 함수
def validate_data_structure(data_dict):
    """데이터 구조의 유효성을 검증합니다."""
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


# 벤치마크 포트폴리오 생성 함수
def create_benchmark_portfolio(cap_data, date, top_n=80, excluded_tickers=None, previous_portfolio=None):
    """벤치마크 포트폴리오 생성 함수 개선"""
    if excluded_tickers is None:
        excluded_tickers = []

    try:
        # 날짜 필터링
        date_data = cap_data[cap_data['date'] == date].copy()

        if date_data.empty:
            print(f"경고: {date}에 대한 시가총액 데이터가 없습니다.")
            return {}

        # 시가총액 데이터 가져오기
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

        # 이전 포트폴리오의 모든 주식 포함 (탈락한 주식은 0 비중)
        result_weights = {}

        # 먼저 모든 이전 포트폴리오 주식을 0 비중으로 초기화
        if previous_portfolio:
            for stock in previous_portfolio:
                if stock in market_caps.index and stock not in excluded_tickers:
                    result_weights[stock] = 0.0

        # 시가총액 기준으로 선택된 주식만 실제 비중 계산
        if top_stocks.empty:
            print(f"경고: 상위 {top_n}개 주식 선택 결과가 비어 있습니다.")
            return result_weights if result_weights else {}

        total_cap = top_stocks.sum()
        if total_cap <= 0:
            print(f"경고: 총 시가총액이 0 이하입니다.")
            return result_weights if result_weights else {}

        # 시가총액 가중치 계산
        for stock, cap in top_stocks.items():
            result_weights[stock] = round(cap / total_cap, 4)

        return result_weights
    except Exception as e:
        print(f"벤치마크 포트폴리오 생성 중 오류: {e}")
        return {}


# 분위수 분류 함수
def quantile_classify(data, n_quantiles=5, ascending=True):
    """
    데이터를 분위수로 분류하는 함수 개선

    Parameters:
    -----------
    data : pd.Series
        분류할 데이터 시리즈
    n_quantiles : int
        분위수의 수
    ascending : bool
        True이면 작은 값이 더 좋음(예: PE 비율), False이면 큰 값이 더 좋음(예: ROE)

    Returns:
    --------
    pd.Series
        각 항목에 대한 분위수(1부터 n_quantiles까지)
    """
    try:
        # NaN 값 처리
        if data.isna().all():
            return pd.Series(index=data.index)

        # 데이터 포인트가 분위수보다 적을 경우
        if len(data) < n_quantiles:
            # 간단히 순위를 매기고 적절하게 조정
            ranks = data.rank(method='first', ascending=ascending)
            scaled_ranks = ((ranks - 1) / len(data) * n_quantiles).astype(int) + 1
            # 최대값이 n_quantiles를 초과하지 않도록 보장
            scaled_ranks = scaled_ranks.clip(upper=n_quantiles)
            return scaled_ranks

        # 중복 값이 있는 경우에도 작동하도록 함
        try:
            # 먼저 기본 접근 방식 시도
            ranks = data.rank(method='first', ascending=ascending)
            return pd.qcut(ranks, n_quantiles, labels=False, duplicates='drop') + 1
        except ValueError:
            # 중복 값이 너무 많을 경우, 다른 방법 시도
            # 순위를 계산하고 균등하게 분배
            ranks = data.rank(method='first', ascending=ascending)
            bins = np.linspace(ranks.min(), ranks.max() + 0.001, n_quantiles + 1)
            return pd.cut(ranks, bins=bins, labels=False, include_lowest=True) + 1
    except Exception as e:
        print(f"분위수 분류 중 오류: {e}")
        # 오류 발생 시 빈 시리즈 반환
        return pd.Series(index=data.index)


# 정보 계수 계산 함수
def calculate_ic(factor_scores, forward_returns):
    """
    팩터 점수와 미래 수익률 간의 정보 계수(IC)를 계산합니다.

    Parameters:
    -----------
    factor_scores : pd.Series
        팩터 점수
    forward_returns : pd.Series
        미래 수익률

    Returns:
    --------
    float
        스피어만 상관 계수 (정보 계수)
    """
    try:
        if factor_scores.empty or forward_returns.empty:
            print("경고: 팩터 점수 또는 미래 수익률이 비어 있습니다.")
            return np.nan

        # 두 시리즈에 공통된 인덱스만 사용
        common_indices = factor_scores.index.intersection(forward_returns.index)

        if len(common_indices) < 5:  # 최소 데이터 요구
            print(f"경고: 공통 인덱스가 {len(common_indices)}개뿐이라 IC를 계산할 수 없습니다.")
            return np.nan

        # NaN 값 제거
        factor_aligned = factor_scores[common_indices].dropna()
        returns_aligned = forward_returns[common_indices].dropna()

        # 다시 공통 인덱스로 정렬
        common_indices = factor_aligned.index.intersection(returns_aligned.index)

        if len(common_indices) < 5:
            print(f"경고: NaN 제거 후 공통 인덱스가 {len(common_indices)}개뿐이라 IC를 계산할 수 없습니다.")
            return np.nan

        factor_final = factor_aligned[common_indices]
        returns_final = returns_aligned[common_indices]

        # 스피어만 상관 계수 계산
        if factor_final.var() == 0 or returns_final.var() == 0:
            print("경고: 팩터 점수 또는 미래 수익률의 분산이 0입니다.")
            return np.nan

        ic = factor_final.corr(returns_final, method='spearman')
        return ic
    except Exception as e:
        print(f"정보 계수 계산 중 오류: {e}")
        return np.nan


# 성장 메트릭 생성 함수
def create_growth_metrics(data_dict, date, top_n=80, excluded_tickers=None):
    """성장 메트릭 생성 함수 개선"""
    if excluded_tickers is None:
        excluded_tickers = []

    try:
        if 'cap_us_bd' not in data_dict:
            print("오류: cap_us_bd가 데이터 사전에 없습니다.")
            return {}

        cap_date_df = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date]

        if cap_date_df.empty:
            print(f"오류: {date}에 대한 시가총액 데이터가 없습니다.")
            return {}

        cap_date = cap_date_df.drop(columns=['date'])

        # 시가총액 가져오기 및 제외 티커 제거
        if cap_date.empty:
            print(f"오류: {date}에 대한 시가총액 데이터가 비어 있습니다.")
            return {}

        market_caps = cap_date.iloc[0]
        market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

        # 시가총액 기준 상위 N개 주식 선택
        top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()
        if not top_stocks:
            print(f"오류: {date}에 대한 상위 {top_n}개 주식을 찾을 수 없습니다.")
            return {}

        growth_metrics = {}

        # 1. Forward EPS 12m/3m growth
        if 'eps_fact_us_bd' in data_dict:
            eps_dates = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] <= date]['date']
            if not eps_dates.empty:
                current_date = eps_dates.max()
                eps_current_df = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] == current_date]

                if not eps_current_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in eps_current_df.columns]
                    if available_stocks:
                        eps_current = eps_current_df.drop(columns=['date'], errors='ignore').iloc[0][available_stocks]

                        # 3개월 전 성장률
                        three_month_ago = current_date - pd.DateOffset(months=3)
                        eps_3m_dates = \
                        data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] <= three_month_ago]['date']
                        if not eps_3m_dates.empty:
                            eps_3m_date = eps_3m_dates.max()
                            eps_3m_ago_df = data_dict['eps_fact_us_bd'][
                                data_dict['eps_fact_us_bd']['date'] == eps_3m_date]

                            if not eps_3m_ago_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in eps_3m_ago_df.columns]
                                if common_stocks:
                                    eps_3m_ago = eps_3m_ago_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    # 0으로 나누기 오류 방지
                                    eps_growth_3m = pd.Series(0, index=common_stocks)
                                    non_zero_mask = (eps_3m_ago != 0) & (~eps_3m_ago.isna())
                                    if non_zero_mask.any():
                                        valid_for_calc = eps_3m_ago[non_zero_mask].index
                                        eps_growth_3m[valid_for_calc] = (eps_current[valid_for_calc] - eps_3m_ago[
                                            valid_for_calc]) / eps_3m_ago[valid_for_calc].abs()
                                    growth_metrics['eps_growth_3m'] = eps_growth_3m

                        # 12개월 전 성장률
                        twelve_month_ago = current_date - pd.DateOffset(months=12)
                        eps_12m_dates = \
                        data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] <= twelve_month_ago]['date']
                        if not eps_12m_dates.empty:
                            eps_12m_date = eps_12m_dates.max()
                            eps_12m_ago_df = data_dict['eps_fact_us_bd'][
                                data_dict['eps_fact_us_bd']['date'] == eps_12m_date]

                            if not eps_12m_ago_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in eps_12m_ago_df.columns]
                                if common_stocks:
                                    eps_12m_ago = eps_12m_ago_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    # 0으로 나누기 오류 방지
                                    eps_growth_12m = pd.Series(0, index=common_stocks)
                                    non_zero_mask = (eps_12m_ago != 0) & (~eps_12m_ago.isna())
                                    if non_zero_mask.any():
                                        valid_for_calc = eps_12m_ago[non_zero_mask].index
                                        eps_growth_12m[valid_for_calc] = (eps_current[valid_for_calc] - eps_12m_ago[
                                            valid_for_calc]) / eps_12m_ago[valid_for_calc].abs()
                                    growth_metrics['eps_growth_12m'] = eps_growth_12m

        # 2. Forward Sales 12m growth
        if 'sales_fact_us_bd' in data_dict:
            sales_dates = data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] <= date]['date']
            if not sales_dates.empty:
                current_date = sales_dates.max()
                sales_current_df = data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] == current_date]

                if not sales_current_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in sales_current_df.columns]
                    if available_stocks:
                        sales_current = sales_current_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks]

                        # 12개월 전 성장률
                        twelve_month_ago = current_date - pd.DateOffset(months=12)
                        sales_12m_dates = \
                        data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] <= twelve_month_ago]['date']
                        if not sales_12m_dates.empty:
                            sales_12m_date = sales_12m_dates.max()
                            sales_12m_ago_df = data_dict['sales_fact_us_bd'][
                                data_dict['sales_fact_us_bd']['date'] == sales_12m_date]

                            if not sales_12m_ago_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in sales_12m_ago_df.columns]
                                if common_stocks:
                                    sales_12m_ago = sales_12m_ago_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    # 0으로 나누기 오류 방지
                                    sales_growth_12m = pd.Series(0, index=common_stocks)
                                    non_zero_mask = (sales_12m_ago != 0) & (~sales_12m_ago.isna())
                                    if non_zero_mask.any():
                                        valid_for_calc = sales_12m_ago[non_zero_mask].index
                                        sales_growth_12m[valid_for_calc] = (sales_current[valid_for_calc] -
                                                                            sales_12m_ago[valid_for_calc]) / \
                                                                           sales_12m_ago[valid_for_calc].abs()
                                    growth_metrics['sales_growth_12m'] = sales_growth_12m

        # 3. EPS Revision
        if 'revision_fact_eps_bd' in data_dict:
            eps_rev_dates = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= date]['date']
            if not eps_rev_dates.empty:
                current_date = eps_rev_dates.max()
                eps_revision_df = data_dict['revision_fact_eps_bd'][
                    data_dict['revision_fact_eps_bd']['date'] == current_date]

                if not eps_revision_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in eps_revision_df.columns]
                    if available_stocks:
                        growth_metrics['eps_revision'] = \
                        eps_revision_df.drop(columns=['date'], errors='ignore').iloc[0][available_stocks].fillna(0)

        # 4. Sales Revision
        if 'revision_fact_sales_bd' in data_dict:
            sales_rev_dates = data_dict['revision_fact_sales_bd'][data_dict['revision_fact_sales_bd']['date'] <= date][
                'date']
            if not sales_rev_dates.empty:
                current_date = sales_rev_dates.max()
                sales_revision_df = data_dict['revision_fact_sales_bd'][
                    data_dict['revision_fact_sales_bd']['date'] == current_date]

                if not sales_revision_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in sales_revision_df.columns]
                    if available_stocks:
                        growth_metrics['sales_revision'] = \
                        sales_revision_df.drop(columns=['date'], errors='ignore').iloc[0][available_stocks].fillna(0)

        # 5. EPS Surprise
        if 'us_eps_surprise_bd' in data_dict:
            surprise_dates = data_dict['us_eps_surprise_bd'][data_dict['us_eps_surprise_bd']['date'] <= date]['date']
            if not surprise_dates.empty:
                current_date = surprise_dates.max()
                eps_surprise_df = data_dict['us_eps_surprise_bd'][
                    data_dict['us_eps_surprise_bd']['date'] == current_date]

                if not eps_surprise_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in eps_surprise_df.columns]
                    if available_stocks:
                        growth_metrics['eps_surprise'] = \
                        eps_surprise_df.drop(columns=['date'], errors='ignore').iloc[0][available_stocks].fillna(0)

        return growth_metrics
    except Exception as e:
        print(f"성장 메트릭 생성 중 오류: {e}")
        traceback.print_exc()
        return {}


# 가치 메트릭 생성 함수
def create_value_metrics(data_dict, date, top_n=80, excluded_tickers=None):
    """가치 메트릭 생성 함수 개선"""
    if excluded_tickers is None:
        excluded_tickers = []

    try:
        cap_date_df = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date]

        if cap_date_df.empty:
            print(f"오류: {date}에 대한 시가총액 데이터가 없습니다.")
            return {}

        cap_date = cap_date_df.drop(columns=['date'])

        # 시가총액 가져오기 및 제외 티커 제거
        market_caps = cap_date.iloc[0]
        market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

        # 시가총액 기준 상위 N개 주식 선택
        top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

        # 가치 지표 계산
        value_metrics = {}

        # 1. Forward P/E
        if 'pe_us_bd' in data_dict:
            pe_dates = data_dict['pe_us_bd'][data_dict['pe_us_bd']['date'] <= date]['date']
            if not pe_dates.empty:
                current_date = pe_dates.max()
                row_pe = data_dict['pe_us_bd'][data_dict['pe_us_bd']['date'] == current_date]

                if not row_pe.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in row_pe.columns]
                    if available_stocks:
                        pe_vals = row_pe.drop(columns=['date'], errors='ignore').iloc[0][available_stocks].fillna(0)
                        value_metrics['pe_ratio'] = pe_vals

        # 2. Forward P/B
        if 'pb_us_bd' in data_dict:
            pb_dates = data_dict['pb_us_bd'][data_dict['pb_us_bd']['date'] <= date]['date']
            if not pb_dates.empty:
                current_date = pb_dates.max()
                row_pb = data_dict['pb_us_bd'][data_dict['pb_us_bd']['date'] == current_date]

                if not row_pb.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in row_pb.columns]
                    if available_stocks:
                        pb_vals = row_pb.drop(columns=['date'], erros='ignore').iloc[0][available_stocks].fillna(0)
                        value_metrics['pb_ratio'] = pb_vals

        # 3. Forward EV/EBITDA
        if 'evebit_fact_us_bd' in data_dict:
            evebit_dates = data_dict['evebit_fact_us_bd'][data_dict['evebit_fact_us_bd']['date'] <= date]['date']
            if not evebit_dates.empty:
                current_date = evebit_dates.max()
                row_evebit = data_dict['evebit_fact_us_bd'][data_dict['evebit_fact_us_bd']['date'] == current_date]

                if not row_evebit.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in row_evebit.columns]
                    if available_stocks:
                        evebitda_vals = row_evebit.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks].fillna(0)
                        value_metrics['ev_ebitda'] = evebitda_vals

        return value_metrics
    except Exception as e:
        print(f"가치 지표 생성 중 오류: {e}")
        traceback.print_exc()
        return {}


# 모멘텀 메트릭 생성 함수
def create_momentum_metrics(data_dict, date, top_n=80, excluded_tickers=None):
    """모멘텀 메트릭 생성 함수 개선"""
    if excluded_tickers is None:
        excluded_tickers = []

    try:
        cap_date_df = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date]

        if cap_date_df.empty:
            print(f"오류: {date}에 대한 시가총액 데이터가 없습니다.")
            return {}

        cap_date = cap_date_df.drop(columns=['date'])

        # 시가총액 가져오기 및 제외 티커 제거
        market_caps = cap_date.iloc[0]
        market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

        # 시가총액 기준 상위 N개 주식 선택
        top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

        # 모멘텀 메트릭 계산
        momentum_metrics = {}

        # 가격 데이터로 계산
        if 'pr_bd' in data_dict:
            price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= date]['date']

            if not price_dates.empty:
                current_date = price_dates.max()
                current_price_df = data_dict['pr_bd'][data_dict['pr_bd']['date'] == current_date]

                if not current_price_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in current_price_df.columns]
                    if available_stocks:
                        current_price = current_price_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks]

                        # 1개월 전 가격
                        one_month_ago = current_date - pd.DateOffset(months=1)
                        month_price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= one_month_ago]['date']
                        if not month_price_dates.empty:
                            month_date = month_price_dates.max()
                            month_price_df = data_dict['pr_bd'][data_dict['pr_bd']['date'] == month_date]

                            if not month_price_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in month_price_df.columns]
                                if common_stocks:
                                    month_price = month_price_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    # 0으로 나누기 오류 방지
                                    mom_1m = pd.Series(index=common_stocks)
                                    for stock in common_stocks:
                                        if month_price[stock] > 0 and not pd.isna(month_price[stock]) and not pd.isna(
                                                current_price[stock]):
                                            mom_1m[stock] = (current_price[stock] / month_price[stock]) - 1
                                    momentum_metrics['mom_1m'] = mom_1m.fillna(0)

                        # 3개월 전 가격
                        three_month_ago = current_date - pd.DateOffset(months=3)
                        three_month_price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= three_month_ago][
                            'date']
                        if not three_month_price_dates.empty:
                            three_month_date = three_month_price_dates.max()
                            three_month_price_df = data_dict['pr_bd'][data_dict['pr_bd']['date'] == three_month_date]

                            if not three_month_price_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in three_month_price_df.columns]
                                if common_stocks:
                                    three_month_price = \
                                    three_month_price_df.drop(columns=['date'], errors='ignore').iloc[0][common_stocks]
                                    # 0으로 나누기 오류 방지
                                    mom_3m = pd.Series(index=common_stocks)
                                    for stock in common_stocks:
                                        if three_month_price[stock] > 0 and not pd.isna(
                                                three_month_price[stock]) and not pd.isna(current_price[stock]):
                                            mom_3m[stock] = (current_price[stock] / three_month_price[stock]) - 1
                                    momentum_metrics['mom_3m'] = mom_3m.fillna(0)

                        # 12개월 전 가격
                        twelve_month_ago = current_date - pd.DateOffset(months=12)
                        year_price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= twelve_month_ago]['date']
                        if not year_price_dates.empty:
                            year_date = year_price_dates.max()
                            year_price_df = data_dict['pr_bd'][data_dict['pr_bd']['date'] == year_date]

                            if not year_price_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in year_price_df.columns]
                                if common_stocks:
                                    year_price = year_price_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    # 0으로 나누기 오류 방지
                                    mom_12m = pd.Series(index=common_stocks)
                                    for stock in common_stocks:
                                        if year_price[stock] > 0 and not pd.isna(year_price[stock]) and not pd.isna(
                                                current_price[stock]):
                                            mom_12m[stock] = (current_price[stock] / year_price[stock]) - 1
                                    momentum_metrics['mom_12m'] = mom_12m.fillna(0)

                                    # 최근 1개월을 제외한 12개월 모멘텀
                                    if 'mom_1m' in momentum_metrics:
                                        # month_price가 존재하는 주식만 사용
                                        month_stocks = momentum_metrics['mom_1m'].index
                                        year_month_common = [s for s in common_stocks if s in month_stocks]
                                        if year_month_common:
                                            mom_12m_ex1m = pd.Series(index=year_month_common)
                                            for stock in year_month_common:
                                                if year_price[stock] > 0 and month_price[stock] > 0 and not pd.isna(
                                                        year_price[stock]) and not pd.isna(month_price[stock]):
                                                    mom_12m_ex1m[stock] = (month_price[stock] / year_price[stock]) - 1
                                            momentum_metrics['mom_12m_ex1m'] = mom_12m_ex1m.fillna(0)

        # EPS Revision 3개월 변화
        if 'revision_fact_eps_bd' in data_dict:
            eps_rev_dates = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= date]['date']
            if not eps_rev_dates.empty:
                current_date = eps_rev_dates.max()
                current_revision_df = data_dict['revision_fact_eps_bd'][
                    data_dict['revision_fact_eps_bd']['date'] == current_date]

                if not current_revision_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in current_revision_df.columns]
                    if available_stocks:
                        current_revision = current_revision_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks]

                        three_month_ago = current_date - pd.DateOffset(months=3)
                        three_month_rev_dates = \
                        data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= three_month_ago][
                            'date']
                        if not three_month_rev_dates.empty:
                            three_month_date = three_month_rev_dates.max()
                            three_month_revision_df = data_dict['revision_fact_eps_bd'][
                                data_dict['revision_fact_eps_bd']['date'] == three_month_date]

                            if not three_month_revision_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in three_month_revision_df.columns]
                                if common_stocks:
                                    three_month_revision = \
                                    three_month_revision_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    eps_rev_3m_change = current_revision[common_stocks] - three_month_revision
                                    momentum_metrics['eps_rev_3m_change'] = eps_rev_3m_change.fillna(0)

        return momentum_metrics
    except Exception as e:
        print(f"모멘텀 메트릭 생성 중 오류: {e}")
        traceback.print_exc()
        return {}


# 저변동성 메트릭 생성 함수
def create_low_vol_metrics(data_dict, date, top_n=80, excluded_tickers=None):
    """저변동성 메트릭 생성 함수 개선"""
    if excluded_tickers is None:
        excluded_tickers = []

    try:
        cap_date_df = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date]

        if cap_date_df.empty:
            print(f"오류: {date}에 대한 시가총액 데이터가 없습니다.")
            return {}

        cap_date = cap_date_df.drop(columns=['date'])

        # 시가총액 가져오기 및 제외 티커 제거
        market_caps = cap_date.iloc[0]
        market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

        # 시가총액 기준 상위 N개 주식 선택
        top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

        # 저변동성 메트릭 계산
        vol_metrics = {}

        # 가격 데이터로 계산
        if 'pr_bd' in data_dict:
            # 지난 3년간의 데이터 가져오기
            three_years_ago = date - pd.DateOffset(years=3)
            price_data = data_dict['pr_bd'][
                (data_dict['pr_bd']['date'] >= three_years_ago) &
                (data_dict['pr_bd']['date'] <= date)
                ].copy()

            if not price_data.empty:
                # 가격 데이터를 날짜로 정렬
                price_data = price_data.sort_values('date')

                # 존재하는 열만 사용
                available_stocks = [s for s in top_stocks if s in price_data.columns]
                if available_stocks:
                    # 날짜를 인덱스로 설정
                    price_data_pivot = price_data.set_index('date')

                    # 수익률 계산
                    returns = price_data_pivot[available_stocks].pct_change().dropna()

                    if not returns.empty:
                        # 지난 3개월(약 63영업일) 변동성 계산
                        if len(returns) >= 21:  # 최소 1개월 이상의 데이터가 필요
                            last_3m = min(63, len(returns))
                            valid_stocks = []
                            vol_values = {}

                            for stock in available_stocks:
                                stock_returns = returns[stock].dropna()
                                if len(stock_returns) >= last_3m / 2:  # 최소 데이터 요구
                                    vol = stock_returns.tail(last_3m).std() * np.sqrt(252)  # 연율화
                                    if not pd.isna(vol):
                                        valid_stocks.append(stock)
                                        vol_values[stock] = vol

                            if valid_stocks:
                                vol_metrics['vol_3m'] = pd.Series(vol_values)

                        # SPX Index가 있으면 베타 계산
                        if 'SPX Index' in price_data_pivot.columns:
                            market_returns = price_data_pivot['SPX Index'].pct_change().dropna()

                            # 각 주식의 베타 계산
                            betas = {}
                            for stock in available_stocks:
                                stock_returns = returns[stock].dropna()
                                if len(stock_returns) > 30:  # 최소 데이터 요구
                                    # 공통 인덱스 찾기
                                    common_index = stock_returns.index.intersection(market_returns.index)

                                    if len(common_index) > 30:
                                        stock_returns_aligned = stock_returns[common_index]
                                        market_returns_aligned = market_returns[common_index]

                                        # 공분산 및 분산 계산
                                        cov = stock_returns_aligned.cov(market_returns_aligned)
                                        var = market_returns_aligned.var()

                                        # 베타 계산 (0으로 나누기 방지)
                                        if var > 0 and not pd.isna(cov) and not pd.isna(var):
                                            beta = cov / var
                                            betas[stock] = beta

                            if betas:
                                vol_metrics['beta_3y'] = pd.Series(betas)

        return vol_metrics
    except Exception as e:
        print(f"저변동성 메트릭 생성 중 오류: {e}")
        traceback.print_exc()
        return {}


# 품질 메트릭 생성 함수
def create_quality_metrics(data_dict, date, top_n=80, excluded_tickers=None):
    """품질 메트릭 생성 함수 개선"""
    if excluded_tickers is None:
        excluded_tickers = []

    try:
        cap_date_df = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date]

        if cap_date_df.empty:
            print(f"오류: {date}에 대한 시가총액 데이터가 없습니다.")
            return {}

        cap_date = cap_date_df.drop(columns=['date'])

        # 시가총액 가져오기 및 제외 티커 제거
        market_caps = cap_date.iloc[0]
        market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

        # 시가총액 기준 상위 N개 주식 선택
        top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

        # 품질 메트릭 계산
        quality_metrics = {}

        # 1. Forward ROE
        if 'roe_us_bd' in data_dict:
            roe_dates = data_dict['roe_us_bd'][data_dict['roe_us_bd']['date'] <= date]['date']
            if not roe_dates.empty:
                current_date = roe_dates.max()
                roe_df = data_dict['roe_us_bd'][data_dict['roe_us_bd']['date'] == current_date]

                if not roe_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in roe_df.columns]
                    if available_stocks:
                        quality_metrics['roe'] = roe_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks].fillna(0)

        # 2. Operating Margin
        if 'opmargin_fact_us_bd' in data_dict:
            opm_dates = data_dict['opmargin_fact_us_bd'][data_dict['opmargin_fact_us_bd']['date'] <= date]['date']
            if not opm_dates.empty:
                current_date = opm_dates.max()
                opm_df = data_dict['opmargin_fact_us_bd'][data_dict['opmargin_fact_us_bd']['date'] == current_date]

                if not opm_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in opm_df.columns]
                    if available_stocks:
                        quality_metrics['op_margin'] = opm_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks].fillna(0)

        # 3. Forward FCF 12m Change
        if 'fcf_fact_us_bd' in data_dict:
            fcf_dates = data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] <= date]['date']
            if not fcf_dates.empty:
                current_date = fcf_dates.max()
                current_fcf_df = data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] == current_date]

                if not current_fcf_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in current_fcf_df.columns]
                    if available_stocks:
                        current_fcf = current_fcf_df.drop(columns=['date'], errors='ignore').iloc[0][available_stocks]

                        twelve_month_ago = current_date - pd.DateOffset(months=12)
                        fcf_12m_dates = \
                        data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] <= twelve_month_ago]['date']
                        if not fcf_12m_dates.empty:
                            fcf_12m_date = fcf_12m_dates.max()
                            year_ago_fcf_df = data_dict['fcf_fact_us_bd'][
                                data_dict['fcf_fact_us_bd']['date'] == fcf_12m_date]

                            if not year_ago_fcf_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in year_ago_fcf_df.columns]
                                if common_stocks:
                                    year_ago_fcf = year_ago_fcf_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    # 0으로 나누기 오류 방지
                                    fcf_growth_12m = pd.Series(index=common_stocks)
                                    for stock in common_stocks:
                                        if not pd.isna(year_ago_fcf[stock]) and not pd.isna(current_fcf[stock]) and \
                                                year_ago_fcf[stock] != 0:
                                            fcf_growth_12m[stock] = (current_fcf[stock] - year_ago_fcf[stock]) / abs(
                                                year_ago_fcf[stock])
                                    quality_metrics['fcf_growth_12m'] = fcf_growth_12m.fillna(0)

        return quality_metrics
    except Exception as e:
        print(f"품질 메트릭 생성 중 오류: {e}")
        traceback.print_exc()
        return {}


# 센티먼트 메트릭 생성 함수
def create_sentiment_metrics(data_dict, date, top_n=80, excluded_tickers=None):
    """센티먼트 메트릭 생성 함수 개선"""
    if excluded_tickers is None:
        excluded_tickers = []

    try:
        cap_date_df = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date]

        if cap_date_df.empty:
            print(f"오류: {date}에 대한 시가총액 데이터가 없습니다.")
            return {}

        cap_date = cap_date_df.drop(columns=['date'])

        # 시가총액 가져오기 및 제외 티커 제거
        market_caps = cap_date.iloc[0]
        market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

        # 시가총액 기준 상위 N개 주식 선택
        top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

        # 센티먼트 메트릭 계산
        sentiment_metrics = {}

        # 센티먼트 데이터 처리 (7일 롤링 합으로 이미 처리됨)
        if 'senti_us_bd' in data_dict:
            senti_dates = data_dict['senti_us_bd'][data_dict['senti_us_bd']['date'] <= date]['date']
            if not senti_dates.empty:
                current_date = senti_dates.max()
                sentiment_df = data_dict['senti_us_bd'][data_dict['senti_us_bd']['date'] == current_date]

                if not sentiment_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in sentiment_df.columns]
                    if available_stocks:
                        sentiment_data = sentiment_df.drop(columns=['date'], errors='ignore').iloc[0][available_stocks]
                        # 결측치를 중앙값으로 대체
                        median_val = sentiment_data.median()
                        sentiment_metrics['sentiment'] = sentiment_data.fillna(
                            median_val if not pd.isna(median_val) else 0)

        return sentiment_metrics
    except Exception as e:
        print(f"센티먼트 메트릭 생성 중 오류: {e}")
        traceback.print_exc()
        return {}


# 개별 지표 포트폴리오 생성 함수
def create_individual_metric_portfolio(metric_data, benchmark_weights, ascending=True, n_quantiles=5):
    """
    개별 메트릭에 대한 롱-숏 포트폴리오 생성

    Parameters:
    -----------
    metric_data : pd.Series
        각 주식의 메트릭 값을 담은 시리즈
    benchmark_weights : dict
        벤치마크 포트폴리오 가중치
    ascending : bool
        True이면 낮은 값이 더 좋음, False이면 높은 값이 더 좋음
    n_quantiles : int
        주식을 나눌 분위수 수

    Returns:
    --------
    tuple
        (adjusted_weights, metric_quantiles)
    """
    try:
        # 벤치마크에 있는 주식만 필터링
        benchmark_stocks = list(benchmark_weights.keys())
        metric_filtered = metric_data[metric_data.index.isin(benchmark_stocks)]

        if metric_filtered.empty:
            print("경고: 벤치마크 주식으로 필터링 후 메트릭 데이터가 비어 있습니다.")
            return {}, pd.Series()

        # NaN 값 제거
        metric_filtered = metric_filtered.dropna()
        if metric_filtered.empty:
            print("경고: NaN 값 제거 후 메트릭 데이터가 비어 있습니다.")
            return {}, pd.Series()

        # 분위수 계산
        metric_quantiles = quantile_classify(metric_filtered, n_quantiles, ascending=ascending)

        # 분위수별 조정 계수
        adjustment_factors = {
            1: 0.1,
            2: 0.05,
            3: 0,
            4: -0.05,
            5: -0.1
        }

        # 각 분위수 내 주식 수 계산
        stocks_per_quantile = {}
        for q in range(1, n_quantiles + 1):
            stocks_in_q = sum(metric_quantiles == q)
            stocks_per_quantile[q] = stocks_in_q

        # 주식별 가중치 계산
        weights = {}
        for stock, quantile in metric_quantiles.items():
            if not pd.isna(quantile) and stocks_per_quantile[quantile] > 0:
                weights[stock] = adjustment_factors[quantile] / stocks_per_quantile[quantile]

        # 누락된 주식은 0 가중치로 설정
        for stock in benchmark_stocks:
            if stock not in weights:
                weights[stock] = 0.0

        # 가중치 합이 0에 가까운지 확인 (시장 중립)
        weight_sum = sum(weights.values())
        if abs(weight_sum) > 1e-10:  # 작은 오차 허용
            # 차이를 모든 주식에 균등 분배 (0이 아닌 가중치에만)
            active_stocks = [s for s, w in weights.items() if w != 0]
            if active_stocks:
                adjustment = weight_sum / len(active_stocks)
                for stock in active_stocks:
                    weights[stock] -= adjustment

        # 4자리 소수점으로 반올림
        weights = {k: round(v, 4) for k, v in weights.items()}

        return weights, metric_quantiles
    except Exception as e:
        print(f"개별 메트릭 포트폴리오 생성 중 오류: {e}")
        traceback.print_exc()
        return {}, pd.Series()


# 메트릭 포트폴리오 생성 함수
def create_metric_portfolios(data_dict, date, benchmark_weights, excluded_tickers=None, previous_metrics=None):
    """
    모든 개별 메트릭에 대한 포트폴리오를 생성합니다.

    Parameters:
    -----------
    data_dict : dict
        데이터 사전
    date : pd.Timestamp
        현재 날짜
    benchmark_weights : dict
        벤치마크 포트폴리오 가중치
    excluded_tickers : list, optional
        제외할 티커 목록
    previous_metrics : dict, optional
        이전에 생성된 메트릭 포트폴리오 저장 사전

    Returns:
    --------
    tuple
        (metric_portfolios, metric_quantiles)
    """
    try:
        if excluded_tickers is None:
            excluded_tickers = []

        if not benchmark_weights:
            print(f"경고: {date}에 대한 벤치마크 가중치가 없습니다.")
            return {}, {}

        # 이전 메트릭이 없으면 빈 딕셔너리로 초기화
        if previous_metrics is None:
            previous_metrics = {}

        benchmark_universe = list(benchmark_weights.keys())

        # 각 범주의 메트릭 수집
        print(f"개별 메트릭 가져오기: {date}")
        growth_metrics = create_growth_metrics(data_dict, date, excluded_tickers=excluded_tickers)
        value_metrics = create_value_metrics(data_dict, date, excluded_tickers=excluded_tickers)
        momentum_metrics = create_momentum_metrics(data_dict, date, excluded_tickers=excluded_tickers)
        low_vol_metrics = create_low_vol_metrics(data_dict, date, excluded_tickers=excluded_tickers)
        quality_metrics = create_quality_metrics(data_dict, date, excluded_tickers=excluded_tickers)
        sentiment_metrics = create_sentiment_metrics(data_dict, date, excluded_tickers=excluded_tickers)

        # 포트폴리오와 분위수 초기화
        metric_portfolios = {}
        metric_quantiles = {}

        # 함수 실행 여부 확인
        metrics_created = False

        # 각 범주의 메트릭에 대한 포트폴리오 생성
        # 1. 성장 메트릭 (높은 값이 더 좋음)
        for metric_name, metric_data in growth_metrics.items():
            full_metric_name = f"growth_{metric_name}"

            # 이전 메트릭에 있던 주식들의 비중 초기화 (0으로)
            if full_metric_name in previous_metrics:
                metric_portfolios[full_metric_name] = {stock: 0.0 for stock in previous_metrics[full_metric_name]}
            else:
                metric_portfolios[full_metric_name] = {}

            if not isinstance(metric_data, pd.Series) or metric_data.empty:
                # 이전 주식 유지
                metric_quantiles[full_metric_name] = pd.Series()
                continue

            weights, quantiles = create_individual_metric_portfolio(
                metric_data, benchmark_weights, ascending=False
            )

            # 새로운 가중치로 업데이트
            for stock, weight in weights.items():
                metric_portfolios[full_metric_name][stock] = weight

            metric_quantiles[full_metric_name] = quantiles
            metrics_created = True

            # 이 메트릭의 주식들 추적
            previous_metrics[full_metric_name] = list(metric_portfolios[full_metric_name].keys())

        # 2. 가치 메트릭 (낮은 값이 더 좋음)
        for metric_name, metric_data in value_metrics.items():
            full_metric_name = f"value_{metric_name}"

            # 이전 메트릭에 있던 주식들의 비중 초기화 (0으로)
            if full_metric_name in previous_metrics:
                metric_portfolios[full_metric_name] = {stock: 0.0 for stock in previous_metrics[full_metric_name]}
            else:
                metric_portfolios[full_metric_name] = {}

            if not isinstance(metric_data, pd.Series) or metric_data.empty:
                # 이전 주식 유지
                metric_quantiles[full_metric_name] = pd.Series()
                continue

            weights, quantiles = create_individual_metric_portfolio(
                metric_data, benchmark_weights, ascending=True
            )

            # 새로운 가중치로 업데이트
            for stock, weight in weights.items():
                metric_portfolios[full_metric_name][stock] = weight

            metric_quantiles[full_metric_name] = quantiles
            metrics_created = True

            # 이 메트릭의 주식들 추적
            previous_metrics[full_metric_name] = list(metric_portfolios[full_metric_name].keys())

        # 3. 모멘텀 메트릭 (높은 값이 더 좋음)
        for metric_name, metric_data in momentum_metrics.items():
            full_metric_name = f"momentum_{metric_name}"

            # 이전 메트릭에 있던 주식들의 비중 초기화 (0으로)
            if full_metric_name in previous_metrics:
                metric_portfolios[full_metric_name] = {stock: 0.0 for stock in previous_metrics[full_metric_name]}
            else:
                metric_portfolios[full_metric_name] = {}

            if not isinstance(metric_data, pd.Series) or metric_data.empty:
                # 이전 주식 유지
                metric_quantiles[full_metric_name] = pd.Series()
                continue

            weights, quantiles = create_individual_metric_portfolio(
                metric_data, benchmark_weights, ascending=False
            )

            # 새로운 가중치로 업데이트
            for stock, weight in weights.items():
                metric_portfolios[full_metric_name][stock] = weight

            metric_quantiles[full_metric_name] = quantiles
            metrics_created = True

            # 이 메트릭의 주식들 추적
            previous_metrics[full_metric_name] = list(metric_portfolios[full_metric_name].keys())

        # 4. 저변동성 메트릭 (낮은 값이 더 좋음)
        for metric_name, metric_data in low_vol_metrics.items():
            full_metric_name = f"low_vol_{metric_name}"

            # 이전 메트릭에 있던 주식들의 비중 초기화 (0으로)
            if full_metric_name in previous_metrics:
                metric_portfolios[full_metric_name] = {stock: 0.0 for stock in previous_metrics[full_metric_name]}
            else:
                metric_portfolios[full_metric_name] = {}

            if not isinstance(metric_data, pd.Series) or metric_data.empty:
                # 이전 주식 유지
                metric_quantiles[full_metric_name] = pd.Series()
                continue

            weights, quantiles = create_individual_metric_portfolio(
                metric_data, benchmark_weights, ascending=True
            )

            # 새로운 가중치로 업데이트
            for stock, weight in weights.items():
                metric_portfolios[full_metric_name][stock] = weight

            metric_quantiles[full_metric_name] = quantiles
            metrics_created = True

            # 이 메트릭의 주식들 추적
            previous_metrics[full_metric_name] = list(metric_portfolios[full_metric_name].keys())

        # 5. 품질 메트릭 (높은 값이 더 좋음)
        for metric_name, metric_data in quality_metrics.items():
            full_metric_name = f"quality_{metric_name}"

            # 이전 메트릭에 있던 주식들의 비중 초기화 (0으로)
            if full_metric_name in previous_metrics:
                metric_portfolios[full_metric_name] = {stock: 0.0 for stock in previous_metrics[full_metric_name]}
            else:
                metric_portfolios[full_metric_name] = {}

            if not isinstance(metric_data, pd.Series) or metric_data.empty:
                # 이전 주식 유지
                metric_quantiles[full_metric_name] = pd.Series()
                continue

            weights, quantiles = create_individual_metric_portfolio(
                metric_data, benchmark_weights, ascending=False
            )

            # 새로운 가중치로 업데이트
            for stock, weight in weights.items():
                metric_portfolios[full_metric_name][stock] = weight

            metric_quantiles[full_metric_name] = quantiles
            metrics_created = True

            # 이 메트릭의 주식들 추적
            previous_metrics[full_metric_name] = list(metric_portfolios[full_metric_name].keys())

        # 6. 센티먼트 메트릭 (높은 값이 더 좋음)
        for metric_name, metric_data in sentiment_metrics.items():
            full_metric_name = f"sentiment_{metric_name}"

            # 이전 메트릭에 있던 주식들의 비중 초기화 (0으로)
            if full_metric_name in previous_metrics:
                metric_portfolios[full_metric_name] = {stock: 0.0 for stock in previous_metrics[full_metric_name]}
            else:
                metric_portfolios[full_metric_name] = {}

            if not isinstance(metric_data, pd.Series) or metric_data.empty:
                # 이전 주식 유지
                metric_quantiles[full_metric_name] = pd.Series()
                continue

            weights, quantiles = create_individual_metric_portfolio(
                metric_data, benchmark_weights, ascending=False
            )

            # 새로운 가중치로 업데이트
            for stock, weight in weights.items():
                metric_portfolios[full_metric_name][stock] = weight

            metric_quantiles[full_metric_name] = quantiles
            metrics_created = True

            # 이 메트릭의 주식들 추적
            previous_metrics[full_metric_name] = list(metric_portfolios[full_metric_name].keys())

        if not metrics_created:
            print(f"경고: {date}에 대한 유효한 메트릭이 없습니다.")

        return metric_portfolios, metric_quantiles
    except Exception as e:
        print(f"메트릭 포트폴리오 생성 중 오류: {e}")
        traceback.print_exc()
        return {}, {}


# 성장 포트폴리오 생성 함수
def create_growth_portfolio(data_dict, date, top_n=80, excluded_tickers=None):
    """성장 포트폴리오 생성 함수 개선

    이 함수는 다음을 반환합니다:
    - growth_quantiles: 각 주식이 속한 성장 분위수 (1-5)
    - growth_avg_score: 각 주식의 평균 성장 점수
    - quantile_metrics: 각 개별 지표에 대한 분위수 (1-10)
    """
    if excluded_tickers is None:
        excluded_tickers = []

    try:
        cap_date_df = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date]

        if cap_date_df.empty:
            print(f"오류: {date}에 대한 시가총액 데이터가 없습니다.")
            return pd.Series(), pd.Series(), pd.DataFrame()

        cap_date = cap_date_df.drop(columns=['date'])

        # 시가총액 가져오기 및 제외 티커 제거
        market_caps = cap_date.iloc[0]
        market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

        # 시가총액 기준 상위 N개 주식 선택
        top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

        # 각 주식의 성장 지표 계산
        growth_metrics = pd.DataFrame(index=top_stocks)

        # 1. Forward EPS 12m/3m growth
        if 'eps_fact_us_bd' in data_dict:
            eps_dates = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] <= date]['date']
            if not eps_dates.empty:
                current_date = eps_dates.max()
                eps_current_df = data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] == current_date]

                if not eps_current_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in eps_current_df.columns]
                    if available_stocks:
                        eps_current = eps_current_df.drop(columns=['date'], errors='ignore').iloc[0][available_stocks]

                        # 12개월 전 성장률
                        twelve_month_ago = current_date - pd.DateOffset(months=12)
                        eps_12m_dates = \
                        data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] <= twelve_month_ago]['date']
                        if not eps_12m_dates.empty:
                            eps_12m_date = eps_12m_dates.max()
                            eps_12m_ago_df = data_dict['eps_fact_us_bd'][
                                data_dict['eps_fact_us_bd']['date'] == eps_12m_date]

                            if not eps_12m_ago_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in eps_12m_ago_df.columns]
                                if common_stocks:
                                    eps_12m_ago = eps_12m_ago_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    eps_growth_12m = pd.Series(index=common_stocks)

                                    for stock in common_stocks:
                                        if stock in eps_12m_ago.index and stock in eps_current.index:
                                            if eps_12m_ago[stock] != 0 and not pd.isna(
                                                    eps_12m_ago[stock]) and not pd.isna(eps_current[stock]):
                                                eps_growth_12m[stock] = (eps_current[stock] - eps_12m_ago[stock]) / abs(
                                                    eps_12m_ago[stock])

                                    growth_metrics['eps_growth_12m'] = eps_growth_12m.fillna(0)

                        # 3개월 전 성장률
                        three_month_ago = current_date - pd.DateOffset(months=3)
                        eps_3m_dates = \
                        data_dict['eps_fact_us_bd'][data_dict['eps_fact_us_bd']['date'] <= three_month_ago]['date']
                        if not eps_3m_dates.empty:
                            eps_3m_date = eps_3m_dates.max()
                            eps_3m_ago_df = data_dict['eps_fact_us_bd'][
                                data_dict['eps_fact_us_bd']['date'] == eps_3m_date]

                            if not eps_3m_ago_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in eps_3m_ago_df.columns]
                                if common_stocks:
                                    eps_3m_ago = eps_3m_ago_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    eps_growth_3m = pd.Series(index=common_stocks)

                                    for stock in common_stocks:
                                        if stock in eps_3m_ago.index and stock in eps_current.index:
                                            if eps_3m_ago[stock] != 0 and not pd.isna(
                                                    eps_3m_ago[stock]) and not pd.isna(eps_current[stock]):
                                                eps_growth_3m[stock] = (eps_current[stock] - eps_3m_ago[stock]) / abs(
                                                    eps_3m_ago[stock])

                                    growth_metrics['eps_growth_3m'] = eps_growth_3m.fillna(0)

        # 2. Forward Sales 12m growth
        if 'sales_fact_us_bd' in data_dict:
            sales_dates = data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] <= date]['date']
            if not sales_dates.empty:
                current_date = sales_dates.max()
                sales_current_df = data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] == current_date]

                if not sales_current_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in sales_current_df.columns]
                    if available_stocks:
                        sales_current = sales_current_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks]

                        # 12개월 전 성장률
                        twelve_month_ago = current_date - pd.DateOffset(months=12)
                        sales_12m_dates = \
                        data_dict['sales_fact_us_bd'][data_dict['sales_fact_us_bd']['date'] <= twelve_month_ago]['date']
                        if not sales_12m_dates.empty:
                            sales_12m_date = sales_12m_dates.max()
                            sales_12m_ago_df = data_dict['sales_fact_us_bd'][
                                data_dict['sales_fact_us_bd']['date'] == sales_12m_date]

                            if not sales_12m_ago_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in sales_12m_ago_df.columns]
                                if common_stocks:
                                    sales_12m_ago = sales_12m_ago_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    sales_growth_12m = pd.Series(index=common_stocks)

                                    for stock in common_stocks:
                                        if stock in sales_12m_ago.index and stock in sales_current.index:
                                            if sales_12m_ago[stock] != 0 and not pd.isna(
                                                    sales_12m_ago[stock]) and not pd.isna(sales_current[stock]):
                                                sales_growth_12m[stock] = (sales_current[stock] - sales_12m_ago[
                                                    stock]) / abs(sales_12m_ago[stock])

                                    growth_metrics['sales_growth_12m'] = sales_growth_12m.fillna(0)

        # 3. EPS Revision
        if 'revision_fact_eps_bd' in data_dict:
            eps_rev_dates = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= date]['date']
            if not eps_rev_dates.empty:
                current_date = eps_rev_dates.max()
                eps_revision_df = data_dict['revision_fact_eps_bd'][
                    data_dict['revision_fact_eps_bd']['date'] == current_date]

                if not eps_revision_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in eps_revision_df.columns]
                    if available_stocks:
                        growth_metrics['eps_revision'] = \
                        eps_revision_df.drop(columns=['date'], errors='ignore').iloc[0][available_stocks].fillna(0)

        # 4. Sales Revision
        if 'revision_fact_sales_bd' in data_dict:
            sales_rev_dates = data_dict['revision_fact_sales_bd'][data_dict['revision_fact_sales_bd']['date'] <= date][
                'date']
            if not sales_rev_dates.empty:
                current_date = sales_rev_dates.max()
                sales_revision_df = data_dict['revision_fact_sales_bd'][
                    data_dict['revision_fact_sales_bd']['date'] == current_date]

                if not sales_revision_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in sales_revision_df.columns]
                    if available_stocks:
                        growth_metrics['sales_revision'] = \
                        sales_revision_df.drop(columns=['date'], errors='ignore').iloc[0][available_stocks].fillna(0)

        # 5. PEG Ratio(inverse)
        if 'peg_us_bd' in data_dict:
            peg_dates = data_dict['peg_us_bd'][data_dict['peg_us_bd']['date'] <= date]['date']
            if not peg_dates.empty:
                current_date = peg_dates.max()
                peg_df = data_dict['peg_us_bd'][data_dict['peg_us_bd']['date'] == current_date]

                if not peg_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in peg_df.columns]
                    if available_stocks:
                        peg_valid = peg_df.drop(columns=['date'], errors='ignore').iloc[0][available_stocks]
                        # 0으로 나누기 오류 방지
                        peg_inverse = pd.Series(index=available_stocks)
                        for stock in available_stocks:
                            if peg_valid[stock] != 0 and not pd.isna(peg_valid[stock]):
                                peg_inverse[stock] = 1 / peg_valid[stock]

                        growth_metrics['peg_inverse'] = peg_inverse.fillna(0)

        # 6. EPS Surprise
        if 'us_eps_surprise_bd' in data_dict:
            surprise_dates = data_dict['us_eps_surprise_bd'][data_dict['us_eps_surprise_bd']['date'] <= date]['date']
            if not surprise_dates.empty:
                current_date = surprise_dates.max()
                eps_surprise_df = data_dict['us_eps_surprise_bd'][
                    data_dict['us_eps_surprise_bd']['date'] == current_date]

                if not eps_surprise_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in eps_surprise_df.columns]
                    if available_stocks:
                        growth_metrics['eps_surprise'] = \
                        eps_surprise_df.drop(columns=['date'], errors='ignore').iloc[0][available_stocks].fillna(0)

        # NaN 값을 중앙값으로 채우기
        for col in growth_metrics.columns:
            if not growth_metrics[col].empty:
                median_val = growth_metrics[col].median()
                growth_metrics[col] = growth_metrics[col].fillna(median_val if not pd.isna(median_val) else 0)

        # 각 개별 지표에 대한 분위수 점수 생성(10 분위수)
        quantile_metrics = pd.DataFrame(index=growth_metrics.index)
        for col in growth_metrics.columns:
            if not growth_metrics[col].empty and not growth_metrics[col].isna().all():
                # 성장 지표는 높은 값이 더 좋음
                quantile_metrics[col] = quantile_classify(growth_metrics[col], n_quantiles=10, ascending=False)

        # 평균 분위수 점수 계산
        # 최소 1개 이상의 유효한 지표가 있어야 함
        if not quantile_metrics.empty and quantile_metrics.shape[1] > 0:
            valid_rows = ~quantile_metrics.isna().all(axis=1)
            growth_avg_score = quantile_metrics.loc[valid_rows].mean(axis=1)

            # 최종 5점 분위수로 분류
            growth_quantiles = quantile_classify(growth_avg_score, n_quantiles=5, ascending=False)

            return growth_quantiles, growth_avg_score, quantile_metrics
        else:
            print(f"경고: {date}에 대한 유효한 성장 지표 데이터가 없습니다")
            return pd.Series(), pd.Series(), pd.DataFrame()

    except Exception as e:
        print(f"성장 포트폴리오 생성 중 오류: {e}")
        traceback.print_exc()
        return pd.Series(), pd.Series(), pd.DataFrame()


# 가치 포트폴리오 생성 함수
def create_value_portfolio(data_dict, date, top_n=80, excluded_tickers=None):
    """가치 포트폴리오 생성 함수 개선

    이 함수는 다음을 반환합니다:
    - value_quantiles: 각 주식이 속한 가치 분위수 (1-5)
    - value_avg_score: 각 주식의 평균 가치 점수
    - quantile_metrics: 각 개별 지표에 대한 분위수 (1-10)
    """
    if excluded_tickers is None:
        excluded_tickers = []

    try:
        cap_date_df = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date]

        if cap_date_df.empty:
            print(f"오류: {date}에 대한 시가총액 데이터가 없습니다.")
            return pd.Series(), pd.Series(), pd.DataFrame()

        cap_date = cap_date_df.drop(columns=['date'])

        # 시가총액 가져오기 및 제외 티커 제거
        market_caps = cap_date.iloc[0]
        market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

        # 시가총액 기준 상위 N개 주식 선택
        top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

        # 각 주식의 가치 지표 계산
        value_metrics = pd.DataFrame(index=top_stocks)

        # 1. Forward P/E
        if 'pe_us_bd' in data_dict:
            pe_dates = data_dict['pe_us_bd'][data_dict['pe_us_bd']['date'] <= date]['date']
            if not pe_dates.empty:
                current_date = pe_dates.max()
                pe_df = data_dict['pe_us_bd'][data_dict['pe_us_bd']['date'] == current_date]

                if not pe_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in pe_df.columns]
                    if available_stocks:
                        value_metrics['pe'] = pe_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks].fillna(0)

        # 2. Forward P/B
        if 'pb_us_bd' in data_dict:
            pb_dates = data_dict['pb_us_bd'][data_dict['pb_us_bd']['date'] <= date]['date']
            if not pb_dates.empty:
                current_date = pb_dates.max()
                pb_df = data_dict['pb_us_bd'][data_dict['pb_us_bd']['date'] == current_date]

                if not pb_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in pb_df.columns]
                    if available_stocks:
                        value_metrics['pb'] = pb_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks].fillna(0)

        # 3. Forward EV/EBITDA
        if 'evebit_fact_us_bd' in data_dict:
            evebit_dates = data_dict['evebit_fact_us_bd'][data_dict['evebit_fact_us_bd']['date'] <= date]['date']
            if not evebit_dates.empty:
                current_date = evebit_dates.max()
                evebit_df = data_dict['evebit_fact_us_bd'][data_dict['evebit_fact_us_bd']['date'] == current_date]

                if not evebit_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in evebit_df.columns]
                    if available_stocks:
                        value_metrics['evebitda'] = evebit_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks].fillna(0)

        # NaN 값을 0으로 채우기
        for col in value_metrics.columns:
            value_metrics[col] = value_metrics[col].fillna(0)

        # 각 개별 지표에 대한 분위수 점수 생성(10 분위수)
        quantile_metrics = pd.DataFrame(index=value_metrics.index)
        for col in value_metrics.columns:
            if not value_metrics[col].empty and not value_metrics[col].isna().all():
                # 가치 지표는 낮은 값이 더 좋음
                quantile_metrics[col] = quantile_classify(value_metrics[col], n_quantiles=10, ascending=True)

        # 평균 분위수 점수 계산
        # 최소 1개 이상의 유효한 지표가 있어야 함
        if not quantile_metrics.empty and quantile_metrics.shape[1] > 0:
            valid_rows = ~quantile_metrics.isna().all(axis=1)
            value_avg_score = quantile_metrics.loc[valid_rows].mean(axis=1)

            # 최종 5점 분위수로 분류
            value_quantiles = quantile_classify(value_avg_score, n_quantiles=5, ascending=False)

            return value_quantiles, value_avg_score, quantile_metrics
        else:
            print(f"경고: {date}에 대한 유효한 가치 지표 데이터가 없습니다")
            return pd.Series(), pd.Series(), pd.DataFrame()

    except Exception as e:
        print(f"가치 포트폴리오 생성 중 오류: {e}")
        traceback.print_exc()
        return pd.Series(), pd.Series(), pd.DataFrame()


# 모멘텀 포트폴리오 생성 함수
def create_momentum_portfolio(data_dict, date, top_n=80, excluded_tickers=None):
    """모멘텀 포트폴리오 생성 함수 개선

    이 함수는 다음을 반환합니다:
    - momentum_quantiles: 각 주식이 속한 모멘텀 분위수 (1-5)
    - momentum_avg_score: 각 주식의 평균 모멘텀 점수
    - quantile_metrics: 각 개별 지표에 대한 분위수 (1-10)
    """
    if excluded_tickers is None:
        excluded_tickers = []

    try:
        cap_date_df = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date]

        if cap_date_df.empty:
            print(f"오류: {date}에 대한 시가총액 데이터가 없습니다.")
            return pd.Series(), pd.Series(), pd.DataFrame()

        cap_date = cap_date_df.drop(columns=['date'])

        # 시가총액 가져오기 및 제외 티커 제거
        if cap_date.empty or cap_date.shape[0] == 0:
            print(f"오류: {date}에 대한 시가총액 데이터가 비어 있습니다.")
            return pd.Series(), pd.Series(), pd.DataFrame()

        market_caps = cap_date.iloc[0]
        market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

        # 시가총액 기준 상위 N개 주식 선택
        top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

        # 각 주식의 모멘텀 지표 계산
        momentum_metrics = pd.DataFrame(index=top_stocks)

        # 가격 데이터로 계산
        if 'pr_bd' in data_dict:
            price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= date]['date']

            if not price_dates.empty:
                current_date = price_dates.max()
                current_price_df = data_dict['pr_bd'][data_dict['pr_bd']['date'] == current_date]

                if not current_price_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in current_price_df.columns]
                    if available_stocks:
                        current_price = current_price_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks]

                        # 1개월 전 가격
                        one_month_ago = current_date - pd.DateOffset(months=1)
                        month_price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= one_month_ago]['date']
                        if not month_price_dates.empty:
                            month_date = month_price_dates.max()
                            month_price_df = data_dict['pr_bd'][data_dict['pr_bd']['date'] == month_date]

                            if not month_price_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in month_price_df.columns]
                                if common_stocks:
                                    month_price = month_price_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    # 0으로 나누기 오류 방지
                                    mom_1m = pd.Series(index=common_stocks)
                                    for stock in common_stocks:
                                        if month_price[stock] > 0 and not pd.isna(month_price[stock]) and not pd.isna(
                                                current_price[stock]):
                                            mom_1m[stock] = (current_price[stock] / month_price[stock]) - 1

                                    momentum_metrics['mom_1m'] = mom_1m.fillna(0)

                        # 3개월 전 가격
                        three_month_ago = current_date - pd.DateOffset(months=3)
                        three_month_price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= three_month_ago][
                            'date']
                        if not three_month_price_dates.empty:
                            three_month_date = three_month_price_dates.max()
                            three_month_price_df = data_dict['pr_bd'][data_dict['pr_bd']['date'] == three_month_date]

                            if not three_month_price_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in three_month_price_df.columns]
                                if common_stocks:
                                    three_month_price = \
                                    three_month_price_df.drop(columns=['date'], errors='ignore').iloc[0][common_stocks]
                                    # 0으로 나누기 오류 방지
                                    mom_3m = pd.Series(index=common_stocks)
                                    for stock in common_stocks:
                                        if three_month_price[stock] > 0 and not pd.isna(
                                                three_month_price[stock]) and not pd.isna(current_price[stock]):
                                            mom_3m[stock] = (current_price[stock] / three_month_price[stock]) - 1

                                    momentum_metrics['mom_3m'] = mom_3m.fillna(0)

                        # 12개월 전 가격
                        twelve_month_ago = current_date - pd.DateOffset(months=12)
                        year_price_dates = data_dict['pr_bd'][data_dict['pr_bd']['date'] <= twelve_month_ago]['date']
                        if not year_price_dates.empty:
                            year_date = year_price_dates.max()
                            year_price_df = data_dict['pr_bd'][data_dict['pr_bd']['date'] == year_date]

                            if not year_price_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in year_price_df.columns]
                                if common_stocks:
                                    year_price = year_price_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    # 0으로 나누기 오류 방지
                                    mom_12m = pd.Series(index=common_stocks)
                                    for stock in common_stocks:
                                        if year_price[stock] > 0 and not pd.isna(year_price[stock]) and not pd.isna(
                                                current_price[stock]):
                                            mom_12m[stock] = (current_price[stock] / year_price[stock]) - 1

                                    momentum_metrics['mom_12m'] = mom_12m.fillna(0)

                                    # 최근 1개월을 제외한 12개월 모멘텀
                                    if 'mom_1m' in momentum_metrics:
                                        # month_price가 존재하는 주식만 사용
                                        month_stocks = momentum_metrics['mom_1m'].index
                                        year_month_common = [s for s in common_stocks if s in month_stocks]
                                        if year_month_common:
                                            mom_12m_ex1m = pd.Series(index=year_month_common)
                                            for stock in year_month_common:
                                                if year_price[stock] > 0 and month_price[stock] > 0 and not pd.isna(
                                                        year_price[stock]) and not pd.isna(month_price[stock]):
                                                    mom_12m_ex1m[stock] = (month_price[stock] / year_price[stock]) - 1

                                            momentum_metrics['mom_12m_ex1m'] = mom_12m_ex1m.fillna(0)

        # EPS Revision 3개월 변화
        if 'revision_fact_eps_bd' in data_dict:
            eps_rev_dates = data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= date]['date']
            if not eps_rev_dates.empty:
                current_date = eps_rev_dates.max()
                current_revision_df = data_dict['revision_fact_eps_bd'][
                    data_dict['revision_fact_eps_bd']['date'] == current_date]

                if not current_revision_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in current_revision_df.columns]
                    if available_stocks:
                        current_revision = current_revision_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks]

                        three_month_ago = current_date - pd.DateOffset(months=3)
                        three_month_rev_dates = \
                        data_dict['revision_fact_eps_bd'][data_dict['revision_fact_eps_bd']['date'] <= three_month_ago][
                            'date']
                        if not three_month_rev_dates.empty:
                            three_month_date = three_month_rev_dates.max()
                            three_month_revision_df = data_dict['revision_fact_eps_bd'][
                                data_dict['revision_fact_eps_bd']['date'] == three_month_date]

                            if not three_month_revision_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in three_month_revision_df.columns]
                                if common_stocks:
                                    three_month_revision = \
                                    three_month_revision_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    eps_rev_3m_change = current_revision[common_stocks] - three_month_revision
                                    momentum_metrics['eps_rev_3m_change'] = eps_rev_3m_change.fillna(0)

        # NaN 값을 0으로 채우기
        for col in momentum_metrics.columns:
            momentum_metrics[col] = momentum_metrics[col].fillna(0)

        # 각 개별 지표에 대한 분위수 점수 생성(10 분위수)
        quantile_metrics = pd.DataFrame(index=momentum_metrics.index)
        for col in momentum_metrics.columns:
            if not momentum_metrics[col].empty and not momentum_metrics[col].isna().all():
                # 모멘텀 지표는 높은 값이 더 좋음
                quantile_metrics[col] = quantile_classify(momentum_metrics[col], n_quantiles=10, ascending=False)

        # 평균 분위수 점수 계산
        # 최소 1개 이상의 유효한 지표가 있어야 함
        if not quantile_metrics.empty and quantile_metrics.shape[1] > 0:
            valid_rows = ~quantile_metrics.isna().all(axis=1)
            momentum_avg_score = quantile_metrics.loc[valid_rows].mean(axis=1)

            # 최종 5점 분위수로 분류
            momentum_quantiles = quantile_classify(momentum_avg_score, n_quantiles=5, ascending=False)

            return momentum_quantiles, momentum_avg_score, quantile_metrics
        else:
            print(f"경고: {date}에 대한 유효한 모멘텀 지표 데이터가 없습니다")
            return pd.Series(), pd.Series(), pd.DataFrame()

    except Exception as e:
        print(f"모멘텀 포트폴리오 생성 중 오류: {e}")
        traceback.print_exc()
        return pd.Series(), pd.Series(), pd.DataFrame()


# 저변동성 포트폴리오 생성 함수
def create_low_vol_portfolio(data_dict, date, top_n=80, excluded_tickers=None):
    """저변동성 포트폴리오 생성 함수 개선

    이 함수는 다음을 반환합니다:
    - vol_quantiles: 각 주식이 속한 변동성 분위수 (1-5)
    - vol_avg_score: 각 주식의 평균 변동성 점수
    - quantile_metrics: 각 개별 지표에 대한 분위수 (1-10)
    """
    if excluded_tickers is None:
        excluded_tickers = []

    try:
        cap_date_df = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date]

        if cap_date_df.empty:
            print(f"오류: {date}에 대한 시가총액 데이터가 없습니다.")
            return pd.Series(), pd.Series(), pd.DataFrame()

        cap_date = cap_date_df.drop(columns=['date'])

        # 시가총액 가져오기 및 제외 티커 제거
        market_caps = cap_date.iloc[0]
        market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

        # 시가총액 기준 상위 N개 주식 선택
        top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

        # 각 주식의 변동성 지표 계산
        vol_metrics = pd.DataFrame(index=top_stocks)

        # 가격 데이터로 계산
        if 'pr_bd' in data_dict:
            # 지난 3년간의 데이터 가져오기
            three_years_ago = date - pd.DateOffset(years=3)
            price_data = data_dict['pr_bd'][
                (data_dict['pr_bd']['date'] >= three_years_ago) &
                (data_dict['pr_bd']['date'] <= date)
                ].copy()

            if not price_data.empty:
                # 가격 데이터를 날짜로 정렬
                price_data = price_data.sort_values('date')

                # 존재하는 열만 사용
                available_stocks = [s for s in top_stocks if s in price_data.columns]
                if available_stocks:
                    # 날짜를 인덱스로 설정
                    price_data_pivot = price_data.set_index('date')

                    # 수익률 계산
                    returns = price_data_pivot[available_stocks].pct_change().dropna()

                    if not returns.empty:
                        # 지난 3개월(약 63영업일) 변동성 계산
                        if len(returns) >= 21:  # 최소 1개월 이상의 데이터가 필요
                            last_3m = min(63, len(returns))
                            valid_stocks = []
                            vol_values = {}

                            for stock in available_stocks:
                                stock_returns = returns[stock].dropna()
                                if len(stock_returns) >= last_3m / 2:  # 최소 데이터 요구
                                    vol = stock_returns.tail(last_3m).std() * np.sqrt(252)  # 연율화
                                    if not pd.isna(vol):
                                        valid_stocks.append(stock)
                                        vol_values[stock] = vol

                            if valid_stocks:
                                vol_metrics['vol_3m'] = pd.Series(vol_values)

                        # SPX Index가 있으면 베타 계산
                        if 'SPX Index' in price_data_pivot.columns:
                            market_returns = price_data_pivot['SPX Index'].pct_change().dropna()

                            # 각 주식의 베타 계산
                            betas = {}
                            for stock in available_stocks:
                                stock_returns = returns[stock].dropna()
                                if len(stock_returns) > 30:  # 최소 데이터 요구
                                    # 공통 인덱스 찾기
                                    common_index = stock_returns.index.intersection(market_returns.index)

                                    if len(common_index) > 30:
                                        stock_returns_aligned = stock_returns[common_index]
                                        market_returns_aligned = market_returns[common_index]

                                        # 공분산 및 분산 계산
                                        cov = stock_returns_aligned.cov(market_returns_aligned)
                                        var = market_returns_aligned.var()

                                        # 베타 계산 (0으로 나누기 방지)
                                        if var > 0 and not pd.isna(cov) and not pd.isna(var):
                                            beta = cov / var
                                            betas[stock] = beta

                            if betas:
                                vol_metrics['beta_3y'] = pd.Series(betas)

        # NaN 값을 중앙값으로 채우기
        for col in vol_metrics.columns:
            if not vol_metrics[col].empty:
                median_val = vol_metrics[col].median()
                vol_metrics[col] = vol_metrics[col].fillna(median_val if not pd.isna(median_val) else 0)

        # 각 개별 지표에 대한 분위수 점수 생성(10 분위수)
        quantile_metrics = pd.DataFrame(index=vol_metrics.index)
        for col in vol_metrics.columns:
            if not vol_metrics[col].empty and not vol_metrics[col].isna().all():
                # 변동성 지표는 낮은 값이 더 좋음
                quantile_metrics[col] = quantile_classify(vol_metrics[col], n_quantiles=10, ascending=True)

        # 평균 분위수 점수 계산
        # 최소 1개 이상의 유효한 지표가 있어야 함
        if not quantile_metrics.empty and quantile_metrics.shape[1] > 0:
            valid_rows = ~quantile_metrics.isna().all(axis=1)
            vol_avg_score = quantile_metrics.loc[valid_rows].mean(axis=1)

            # 최종 5점 분위수로 분류
            vol_quantiles = quantile_classify(vol_avg_score, n_quantiles=5, ascending=False)

            return vol_quantiles, vol_avg_score, quantile_metrics
        else:
            print(f"경고: {date}에 대한 유효한 변동성 지표 데이터가 없습니다")
            return pd.Series(), pd.Series(), pd.DataFrame()

    except Exception as e:
        print(f"저변동성 포트폴리오 생성 중 오류: {e}")
        traceback.print_exc()
        return pd.Series(), pd.Series(), pd.DataFrame()


# 품질 포트폴리오 생성 함수
def create_quality_portfolio(data_dict, date, top_n=80, excluded_tickers=None):
    """품질 포트폴리오 생성 함수 개선

    이 함수는 다음을 반환합니다:
    - quality_quantiles: 각 주식이 속한 품질 분위수 (1-5)
    - quality_avg_score: 각 주식의 평균 품질 점수
    - quantile_metrics: 각 개별 지표에 대한 분위수 (1-10)
    """
    if excluded_tickers is None:
        excluded_tickers = []

    try:
        cap_date_df = data_dict['cap_us_bd'][data_dict['cap_us_bd']['date'] == date]

        if cap_date_df.empty:
            print(f"오류: {date}에 대한 시가총액 데이터가 없습니다.")
            return pd.Series(), pd.Series(), pd.DataFrame()

        cap_date = cap_date_df.drop(columns=['date'])

        # 시가총액 가져오기 및 제외 티커 제거
        market_caps = cap_date.iloc[0]
        market_caps = market_caps[~market_caps.index.isin(excluded_tickers)]

        # 시가총액 기준 상위 N개 주식 선택
        top_stocks = market_caps.sort_values(ascending=False).head(top_n).index.tolist()

        # 각 주식의 품질 지표 계산
        quality_metrics = pd.DataFrame(index=top_stocks)

        # 1. Forward ROE
        if 'roe_us_bd' in data_dict:
            roe_dates = data_dict['roe_us_bd'][data_dict['roe_us_bd']['date'] <= date]['date']
            if not roe_dates.empty:
                current_date = roe_dates.max()
                roe_df = data_dict['roe_us_bd'][data_dict['roe_us_bd']['date'] == current_date]

                if not roe_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in roe_df.columns]
                    if available_stocks:
                        quality_metrics['roe'] = roe_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks].fillna(0)

        # 2. Operating Margin
        if 'opmargin_fact_us_bd' in data_dict:
            opm_dates = data_dict['opmargin_fact_us_bd'][data_dict['opmargin_fact_us_bd']['date'] <= date]['date']
            if not opm_dates.empty:
                current_date = opm_dates.max()
                opm_df = data_dict['opmargin_fact_us_bd'][data_dict['opmargin_fact_us_bd']['date'] == current_date]

                if not opm_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in opm_df.columns]
                    if available_stocks:
                        quality_metrics['op_margin'] = opm_df.drop(columns=['date'], errors='ignore').iloc[0][
                            available_stocks].fillna(0)

        # 3. Forward FCF 12m Change
        if 'fcf_fact_us_bd' in data_dict:
            fcf_dates = data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] <= date]['date']
            if not fcf_dates.empty:
                current_date = fcf_dates.max()
                current_fcf_df = data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] == current_date]

                if not current_fcf_df.empty:
                    # 존재하는 열만 사용
                    available_stocks = [s for s in top_stocks if s in current_fcf_df.columns]
                    if available_stocks:
                        current_fcf = current_fcf_df.drop(columns=['date'], errors='ignore').iloc[0][available_stocks]

                        twelve_month_ago = current_date - pd.DateOffset(months=12)
                        fcf_12m_dates = \
                        data_dict['fcf_fact_us_bd'][data_dict['fcf_fact_us_bd']['date'] <= twelve_month_ago]['date']
                        if not fcf_12m_dates.empty:
                            fcf_12m_date = fcf_12m_dates.max()
                            year_ago_fcf_df = data_dict['fcf_fact_us_bd'][
                                data_dict['fcf_fact_us_bd']['date'] == fcf_12m_date]

                            if not year_ago_fcf_df.empty:
                                # 두 데이터셋 모두에 존재하는 주식만 사용
                                common_stocks = [s for s in available_stocks if s in year_ago_fcf_df.columns]
                                if common_stocks:
                                    year_ago_fcf = year_ago_fcf_df.drop(columns=['date'], errors='ignore').iloc[0][
                                        common_stocks]
                                    # 0으로 나누기 오류 방지
                                    fcf_growth_12m = pd.Series(index=common_stocks)
                                    for stock in common_stocks:
                                        if not pd.isna(year_ago_fcf[stock]) and not pd.isna(current_fcf[stock]) and \
                                                year_ago_fcf[stock] != 0:
                                            fcf_growth_12m[stock] = (current_fcf[stock] - year_ago_fcf[stock]) / abs(
                                                year_ago_fcf[stock])
                                    quality_metrics['fcf_growth_12m'] = fcf_growth_12m.fillna(0)

        # NaN 값을 0으로 채우기
        for col in quality_metrics.columns:
            quality_metrics[col] = quality_metrics[col].fillna(0)

        # 각 개별 지표에 대한 분위수 점수 생성(10 분위수)
        quantile_metrics = pd.DataFrame(index=quality_metrics.index)
        for col in quality_metrics.columns:
            if not quality_metrics[col].empty and not quality_metrics[col].isna().all():
                # 품질 지표는 높은 값이 더 좋음
                quantile_metrics[col] = quantile_classify(quality_metrics[col], n_quantiles=10, ascending=False)

        # 평균 분위수 점수 계산
        # 최소 1개 이상의 유효한 지표가 있어야 함
        if not quantile_metrics.empty and quantile_metrics.shape[1] > 0:
            valid_rows = ~quantile_metrics.isna().all(axis=1)
            quality_avg_score = quantile_metrics.loc[valid_rows].mean(axis=1)

            # 최종 5점 분위수로 분류
            quality_quantiles = quantile_classify(quality_avg_score, n_quantiles=5, ascending=False)

            return quality_quantiles, quality_avg_score, quantile_metrics
        else:
            print(f"경고: {date}에 대한 유효한 품질 지표 데이터가 없습니다")
            return pd.Series(), pd.Series(), pd.DataFrame()

    except Exception as e:
        print(f"품질 포트폴리오 생성 중 오류: {e}")
        traceback.print_exc()
        return pd.Series(), pd.Series(), pd.DataFrame()


# 가중치 조정 함수
def adjust_weights_by_quantile(benchmark_weights, quantiles, adjustment_factors=None):
    """
    분위수에 따라 벤치마크 가중치를 조정합니다.

    Parameters:
    -----------
    benchmark_weights : dict
        벤치마크 포트폴리오 가중치 딕셔너리
    quantiles : pd.Series
        각 주식의 분위수 (1-5)
    adjustment_factors : list, optional
        각 분위수에 적용할 조정 계수, 기본값은 [0.2, 0.1, 0, -0.1, -0.2]

    Returns:
    --------
    dict
        조정된 가중치 딕셔너리
    """
    try:
        if adjustment_factors is None:
            adjustment_factors = [0.2, 0.1, 0, -0.1, -0.2]

        if not benchmark_weights or quantiles.empty:
            print("경고: 벤치마크 가중치 또는 분위수가 비어 있습니다.")
            return benchmark_weights.copy()

        # 벤치마크의 모든 주식에 대한 가중치 초기화 (원본 유지)
        adjusted_weights = benchmark_weights.copy()

        # 분위수에 따라 조정 적용 (분위수가 있는 주식만)
        stocks_adjusted = 0
        for stock, quantile in quantiles.items():
            if stock in adjusted_weights and not pd.isna(quantile):
                # 이미 비중이 0인 주식은 조정하지 않음 (탈락한 주식)
                if adjusted_weights[stock] > 0:
                    # 분위수는 1부터 시작하므로 0부터 시작하는 리스트에 맞게 인덱스 조정
                    factor_idx = int(quantile) - 1
                    if 0 <= factor_idx < len(adjustment_factors):
                        factor = adjustment_factors[factor_idx]
                        adjusted_weights[stock] = adjusted_weights[stock] * (1 + factor)
                        stocks_adjusted += 1

        if stocks_adjusted == 0:
            print("경고: 조정된 주식이 없습니다.")
            return benchmark_weights.copy()

        # 가중치 합이 1이 되도록 정규화 (0이 아닌 가중치만)
        non_zero_weights = {k: v for k, v in adjusted_weights.items() if v > 0}
        total_weight = sum(non_zero_weights.values())

        if total_weight <= 0:
            print("경고: 조정 후 총 가중치가 0 이하입니다. 원본 가중치 반환.")
            return benchmark_weights.copy()

        # 0이 아닌 가중치만 정규화
        for stock in adjusted_weights:
            if adjusted_weights[stock] > 0:
                adjusted_weights[stock] = adjusted_weights[stock] / total_weight
                # 4자리 소수점으로 반올림
                adjusted_weights[stock] = round(adjusted_weights[stock], 4)

        return adjusted_weights
    except Exception as e:
        print(f"가중치 조정 중 오류: {e}")
        return benchmark_weights.copy()


# 포트폴리오 성과 구축 함수
def build_portfolio_performance(price_data, weights_dict, start_date, end_date):
    """포트폴리오 성과 구축 함수 개선"""
    try:
        if not weights_dict:
            print("경고: 가중치 딕셔너리가 비어 있습니다.")
            return pd.DataFrame(columns=['date'])

        # 날짜를 timestamp로 변환
        if isinstance(start_date, str):
            start_date = pd.Timestamp(start_date)
        if isinstance(end_date, str):
            end_date = pd.Timestamp(end_date)

        # 가격 데이터에서 해당 기간의 날짜 추출
        price_data_filtered = price_data[(price_data['date'] >= start_date) & (price_data['date'] <= end_date)].copy()

        if price_data_filtered.empty:
            print(f"경고: {start_date}에서 {end_date} 사이의 가격 데이터가 없습니다.")
            return pd.DataFrame(columns=['date'])

        date_range = price_data_filtered['date'].sort_values().unique()

        if len(date_range) == 0:
            print(f"경고: 날짜 범위가 비어 있습니다.")
            return pd.DataFrame(columns=['date'])

        # 모든 리밸런싱 날짜에 등장하는 모든 주식 추적
        all_stocks = set()
        for weights in weights_dict.values():
            all_stocks.update(weights.keys())

        # 모든 날짜와 주식을 위한 딕셔너리 초기화
        # 중요: 모든 주식을 포함하고 기본값을 0으로 설정
        weights_by_date = {date: {stock: 0.0 for stock in all_stocks} for date in date_range}

        # 리밸런싱 날짜 정렬
        rebalance_dates = sorted(list(weights_dict.keys()))

        if not rebalance_dates:
            print("경고: 리밸런싱 날짜가 없습니다.")
            return pd.DataFrame(columns=['date'])

        # 각 날짜에 대한 가중치 계산
        current_weights = None
        prev_date = None

        for date in date_range:
            # 가장 최근의 리밸런싱 날짜 찾기
            applicable_rebalance_dates = [d for d in rebalance_dates if d <= date]

            if applicable_rebalance_dates:
                rebalance_date = max(applicable_rebalance_dates)
                rebalance_weights = weights_dict[rebalance_date]

                # 첫 날짜이거나 리밸런싱 날짜인 경우 가중치 직접 사용
                if prev_date is None or date == rebalance_date:
                    # 중요: 모든 주식 집합에 대해 가중치 설정 (없는 주식은 0)
                    current_weights = {stock: 0.0 for stock in all_stocks}
                    for stock, weight in rebalance_weights.items():
                        current_weights[stock] = weight
                else:
                    # 아니면 가격 변화에 따라 가중치 조정
                    prev_price_data = price_data[price_data['date'] == prev_date]
                    curr_price_data = price_data[price_data['date'] == date]

                    if not prev_price_data.empty and not curr_price_data.empty:
                        # 날짜 열 제외한 가격 데이터 추출
                        prev_prices = prev_price_data.iloc[0].drop('date') if 'date' in prev_price_data.columns else \
                        prev_price_data.iloc[0]
                        curr_prices = curr_price_data.iloc[0].drop('date') if 'date' in curr_price_data.columns else \
                        curr_price_data.iloc[0]

                        # 가중치 조정 (모든 주식에 대해 가중치 유지, 변화 없는 주식은 0 유지)
                        adjusted_weights = {stock: 0.0 for stock in all_stocks}
                        for stock, weight in current_weights.items():
                            # 중요: 시가총액 기준에서 탈락한 주식의 비중은 항상 0으로 유지
                            # 현재 리밸런싱의 비중이 0이면 0 유지
                            if stock in rebalance_weights and rebalance_weights[stock] == 0:
                                adjusted_weights[stock] = 0.0
                            # 그렇지 않고 현재 비중이 있고 가격 데이터가 있는 경우만 업데이트
                            elif weight > 0 and stock in prev_prices.index and stock in curr_prices.index and \
                                    prev_prices[stock] > 0:
                                stock_return = curr_prices[stock] / prev_prices[stock]
                                adjusted_weights[stock] = weight * stock_return
                            # 그 외 경우는 모두 0으로 처리
                            else:
                                adjusted_weights[stock] = 0.0

                        if adjusted_weights:
                            current_weights = adjusted_weights

                            # 시장 중립 포트폴리오의 경우 합이 0이 되도록 재정규화
                            weight_sum = sum(current_weights.values())

                            # 이것이 시장 중립 포트폴리오인지 확인 (합이 0에 가까움)
                            if abs(weight_sum) < 0.1:  # 작은 편차 허용
                                # 시장 중립성 보장을 위한 조정
                                active_stocks = [s for s, w in current_weights.items() if w != 0]
                                if abs(weight_sum) > 1e-10 and len(active_stocks) > 0:
                                    adjustment = weight_sum / len(active_stocks)
                                    for stock in active_stocks:
                                        current_weights[stock] -= adjustment
                            # 그렇지 않으면 롱온리 포트폴리오로 취급 (합이 1)
                            elif weight_sum > 0:
                                for stock in current_weights:
                                    if weight_sum > 0:  # 0으로 나누기 방지
                                        current_weights[stock] = current_weights[stock] / weight_sum

                # 소수점 4자리로 반올림
                current_weights = {k: round(v, 4) for k, v in current_weights.items()}

                # 현재 날짜의 가중치 업데이트
                weights_by_date[date] = current_weights

            prev_date = date

        # 데이터프레임 생성
        data_rows = []
        for date, weights in weights_by_date.items():
            row = {'date': date}
            row.update(weights)
            data_rows.append(row)

        result_df = pd.DataFrame(data_rows)

        # 날짜 기준으로 정렬
        if 'date' in result_df.columns and not result_df.empty:
            result_df = result_df.sort_values('date')

        return result_df
    except Exception as e:
        print(f"포트폴리오 성과 구축 중 오류: {e}")
        traceback.print_exc()
        return pd.DataFrame(columns=['date'])


# 일별 수익률 계산 함수
def calculate_daily_returns(price_data, weights_data):
    """
    포트폴리오의 일별 수익률을 계산합니다.

    Parameters:
    -----------
    price_data : pd.DataFrame
        각 주식의 가격 데이터
    weights_data : pd.DataFrame
        각 날짜에 대한 포트폴리오 가중치

    Returns:
    --------
    pd.DataFrame
        각 날짜에 대한 포트폴리오 수익률
    """
    try:
        if weights_data.empty:
            print("경고: 가중치 데이터가 비어 있습니다.")
            return pd.DataFrame(columns=['date', 'return'])

        # 날짜 열이 있는지 확인
        if 'date' not in weights_data.columns:
            print("오류: 가중치 데이터에 'date' 열이 없습니다.")
            return pd.DataFrame(columns=['date', 'return'])

        daily_returns = pd.DataFrame({'date': weights_data['date']})
        daily_returns['return'] = 0.0

        # 최소 2일의 데이터가 필요
        if len(daily_returns) < 2:
            print("경고: 수익률을 계산하기 위한 충분한 데이터가 없습니다.")
            return daily_returns

        for i in range(1, len(daily_returns)):
            try:
                current_date = daily_returns['date'].iloc[i]
                prev_date = daily_returns['date'].iloc[i - 1]

                # 이전 날짜의 가중치 가져오기
                prev_weights = weights_data[weights_data['date'] == prev_date]

                if prev_weights.empty:
                    print(f"경고: {prev_date}에 대한 가중치 데이터가 없습니다.")
                    continue

                prev_weights = prev_weights.drop(columns=['date']).iloc[0]

                # 두 날짜의 가격 가져오기
                prev_prices = price_data[price_data['date'] == prev_date]
                current_prices = price_data[price_data['date'] == current_date]

                if prev_prices.empty or current_prices.empty:
                    print(f"경고: {prev_date} 또는 {current_date}에 대한 가격 데이터가 없습니다.")
                    continue

                prev_prices = prev_prices.drop(columns=['date']).iloc[0]
                current_prices = current_prices.drop(columns=['date']).iloc[0]

                # 가중 수익률 계산
                portfolio_return = 0.0
                valid_weights_sum = 0.0

                for stock in prev_weights.index:
                    # 비중이 0인 주식은 수익률 계산에서 제외
                    if (prev_weights[stock] > 0 and
                            stock in prev_prices.index and stock in current_prices.index and
                            prev_prices[stock] > 0 and not pd.isna(prev_prices[stock]) and
                            not pd.isna(current_prices[stock])):
                        stock_return = current_prices[stock] / prev_prices[stock] - 1
                        portfolio_return += prev_weights[stock] * stock_return
                        valid_weights_sum += prev_weights[stock]

                # 유효한 가중치가 있는 경우에만 수익률 조정
                if valid_weights_sum > 0:
                    # 수익률 정규화 (누락된 가중치 조정)
                    portfolio_return = portfolio_return * (1 / valid_weights_sum)

                daily_returns.loc[i, 'return'] = portfolio_return

            except Exception as e:
                print(f"날짜 {daily_returns['date'].iloc[i]} 처리 중 오류: {e}")
                daily_returns.loc[i, 'return'] = 0

        return daily_returns
    except Exception as e:
        print(f"일별 수익률 계산 중 오류: {e}")
        traceback.print_exc()
        return pd.DataFrame(columns=['date', 'return'])


# 성능 지표 계산 함수
def calculate_performance_metrics(returns_data, windows=None):
    """
    포트폴리오 성능 지표를 계산합니다.

    Parameters:
    -----------
    returns_data : pd.DataFrame
        'date'와 'return' 열이 있는 수익률 데이터프레임
    windows : list, optional
        성능 지표를 계산할 기간(영업일), 기본값은 [21, 63, 126, 252, 756, 1260]

    Returns:
    --------
    dict
        계산된 성능 지표
    """
    try:
        if windows is None:
            windows = [21, 63, 126, 252, 756, 1260]  # 1개월, 3개월, 6개월, 1년, 3년, 5년

        metrics = {}

        # 'date'와 'return' 열이 있는지 확인
        if returns_data.empty or 'date' not in returns_data.columns or 'return' not in returns_data.columns:
            print("경고: 수익률 데이터가 비어 있거나 필요한 열이 없습니다.")
            return metrics

        # NaN 값 처리
        returns_series = returns_data['return'].fillna(0)

        # 반환 데이터가 충분한지 확인
        max_window = max(windows)
        if len(returns_series) < max_window:
            print(f"경고: 수익률 데이터가 {len(returns_series)}일만 있어 일부 지표가 NA가 됩니다.")

        for window in windows:
            if len(returns_series) >= window:
                try:
                    # 윈도우에 해당하는 데이터 추출
                    window_returns = returns_series.iloc[-window:]

                    # 누적 수익률
                    cumulative_return = (1 + window_returns).prod() - 1
                    metrics[f'{window}d_return'] = cumulative_return

                    # 변동성
                    volatility = window_returns.std() * np.sqrt(252)  # 연율화
                    metrics[f'{window}d_volatility'] = volatility

                    # 샤프 비율
                    if volatility > 0:
                        avg_return = window_returns.mean() * 252  # 연율화
                        sharpe = avg_return / volatility
                        metrics[f'{window}d_sharpe'] = sharpe
                    else:
                        metrics[f'{window}d_sharpe'] = np.nan

                except Exception as e:
                    print(f"{window}일 성능 지표 계산 중 오류: {e}")
                    metrics[f'{window}d_return'] = np.nan
                    metrics[f'{window}d_volatility'] = np.nan
                    metrics[f'{window}d_sharpe'] = np.nan

        return metrics
    except Exception as e:
        print(f"성능 지표 계산 중 오류: {e}")
        return {}


# 모멘텀 퀀타일 베타 계산 함수
def calculate_momentum_quantile_betas(data_dict, factor_quantiles, start_date=None, end_date=None, window=63):
    """
    모멘텀 퀀타일 포트폴리오와 SPX 지수 간의 베타를 계산합니다.

    Parameters:
    -----------
    data_dict : dict
        데이터 사전
    factor_quantiles : dict
        팩터 분위수 사전
    start_date : pd.Timestamp or str, optional
        시작 날짜, None이면 데이터에서 자동 결정
    end_date : pd.Timestamp or str, optional
        종료 날짜, None이면 데이터에서 자동 결정
    window : int, default=63
        베타 계산을 위한 롤링 창 크기 (영업일)

    Returns:
    --------
    pd.DataFrame
        각 모멘텀 분위수의 베타 값을 포함하는 데이터프레임
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

        # 날짜가 제공되지 않은 경우 자동으로 결정
        if start_date is None or end_date is None:
            price_dates = data_dict['pr_bd']['date'].sort_values()
            if not price_dates.empty:
                if start_date is None:
                    start_date = price_dates.min()
                if end_date is None:
                    end_date = price_dates.max()

        # 스트링 날짜를 timestamp로 변환
        if isinstance(start_date, str):
            start_date = pd.Timestamp(start_date)
        if isinstance(end_date, str):
            end_date = pd.Timestamp(end_date)

        print(f"모멘텀 퀀타일 베타 계산: {start_date}부터 {end_date}까지")

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
        all_dates = returns_data.index

        # 모멘텀 퀀타일이 있는지 확인
        if 'momentum' not in factor_quantiles:
            print("오류: factor_quantiles에 'momentum' 키가 없습니다.")
            return None

        if not factor_quantiles['momentum']:
            print("오류: 모멘텀 퀀타일 데이터가 비어 있습니다.")
            return None

        # 디버깅 정보 출력
        print(f"사용 가능한 팩터: {list(factor_quantiles.keys())}")
        print(f"momentum 요소 키 타입: {type(factor_quantiles['momentum'])}")
        print(f"momentum 값 수: {len(factor_quantiles['momentum'])}")

        if factor_quantiles['momentum']:
            first_key = next(iter(factor_quantiles['momentum']))
            print(f"첫 번째 모멘텀 키: {first_key}, 타입: {type(first_key)}")
            print(f"첫 번째 모멘텀 값 타입: {type(factor_quantiles['momentum'][first_key])}")

        # 리밸런싱 날짜 가져오기
        rebalance_dates = sorted(factor_quantiles['momentum'].keys())
        if not rebalance_dates:
            print("오류: 리밸런싱 날짜가 없습니다.")
            return None

        # 각 퀀타일별 베타를 저장할 데이터프레임 초기화
        beta_df = pd.DataFrame(index=all_dates)

        # 빈 수익률로 퀀타일 포트폴리오 초기화
        for q in range(1, 6):
            beta_df[f'Momentum_Q{q}_Beta'] = np.nan

        # 각 퀀타일 포트폴리오의 수익률 계산
        quantile_returns = {q: pd.Series(index=all_dates, dtype='float64') for q in range(1, 6)}

        # 각 리밸런싱 날짜마다 주식을 퀀타일에 할당하고 수익률 계산
        for i in range(len(rebalance_dates)):
            current_date = rebalance_dates[i]
            print(f"리밸런싱 날짜 처리 중: {current_date}")

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
            print(
                f"모멘텀 퀀타일 유형: {type(momentum_quantiles)}, 비어 있음: {momentum_quantiles.empty if hasattr(momentum_quantiles, 'empty') else '확인할 수 없음'}")

            # Series 형식인지 확인
            if not isinstance(momentum_quantiles, pd.Series):
                print(f"경고: {current_date}의 모멘텀 퀀타일이 Series가 아닙니다: {type(momentum_quantiles)}")

                # 딕셔너리면 Series로 변환
                if isinstance(momentum_quantiles, dict):
                    print("딕셔너리를 Series로 변환합니다")
                    momentum_quantiles = pd.Series(momentum_quantiles)
                else:
                    print(f"모멘텀 퀀타일을 Series로 변환할 수 없습니다")
                    continue

            if momentum_quantiles.empty:
                print(f"경고: {current_date}에 대한 모멘텀 퀀타일이 비어 있습니다.")
                continue

            # 각 날짜에 대해 퀀타일별 동일 가중 수익률 계산
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


# 모멘텀 베타 저장 함수
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
        traceback.print_exc()


# 결과 저장 함수
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
                traceback.print_exc()

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
        if 'EXCLUDED_TICKERS' in globals():
            pd.DataFrame({'excluded_tickers': EXCLUDED_TICKERS}).to_csv(f"{output_dir}/excluded_tickers.csv",
                                                                        index=False)

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
        traceback.print_exc()


# 팩터 포트폴리오 구축 함수
def build_factor_portfolios(data_dict, start_date=None, end_date=None, excluded_tickers=None):
    """모든 팩터 포트폴리오를 구축하고 성과를 추적합니다."""
    if excluded_tickers is None:
        excluded_tickers = []

    # 데이터에서 사용 가능한 날짜 범위를 자동으로 결정
    if start_date is None or end_date is None:
        if 'pr_bd' in data_dict and not data_dict['pr_bd'].empty:
            all_available_dates = pd.to_datetime(data_dict['pr_bd']['date']).sort_values()
            if not all_available_dates.empty:
                if start_date is None:
                    start_date = all_available_dates.min()
                if end_date is None:
                    end_date = all_available_dates.max()

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
    price_data = data_dict.get('pr_bd', pd.DataFrame())
    if price_data.empty or 'date' not in price_data.columns:
        print("오류: 가격 데이터가 없거나 'date' 열이 없습니다.")
        return None

    all_dates = price_data[
        (price_data['date'] >= start_date) &
        (price_data['date'] <= end_date)
        ]['date'].sort_values()

    if all_dates.empty:
        print("오류: 지정된 날짜 범위에 대한 가격 데이터가 없습니다.")
        return None

    # 리밸런싱을 위한 분기 말 날짜 찾기
    rebalance_dates = []
    for date in all_dates:
        # 분기 말(3,6,9,12월) 확인
        if date.month in [3, 6, 9, 12] and date.day > 25:
            next_month = (date.replace(day=1) + pd.DateOffset(months=1)).replace(day=1)
            if (next_month - date).days <= 7:  # 다음 달까지 7일 이내인 경우
                rebalance_dates.append(date)

    if not rebalance_dates:
        print("경고: 리밸런싱 날짜를 찾을 수 없습니다. 대신 월말 날짜를 사용합니다.")
        # 대안: 월말 날짜 사용
        month_end_dates = []
        current_month = None
        last_date_of_month = None

        for date in sorted(all_dates):
            if current_month is None or date.month != current_month:
                if last_date_of_month is not None:
                    month_end_dates.append(last_date_of_month)
                current_month = date.month
            last_date_of_month = date

        # 마지막 달 추가
        if last_date_of_month is not None:
            month_end_dates.append(last_date_of_month)

        rebalance_dates = month_end_dates

    print(f"{len(rebalance_dates)}개의 리밸런싱 날짜 발견")

    # 리밸런싱 날짜에 따른 포트폴리오 구성 유지를 위한 변수
    previous_benchmark_stocks = {}  # 모든 이전 포트폴리오 주식 추적
    previous_metric_stocks = {}  # 지표 포트폴리오 주식 추적

    # 각 리밸런싱 날짜에 대한 포트폴리오 구축
    for rebalance_date in tqdm(rebalance_dates, desc="포트폴리오 구축 중"):
        try:
            print(f"\n{rebalance_date} 리밸런싱 처리 중...")

            # 벤치마크 포트폴리오 생성 (이전 포트폴리오 주식 모두 포함)
            benchmark_weights = create_benchmark_portfolio(
                data_dict['cap_us_bd'],
                rebalance_date,
                excluded_tickers=excluded_tickers,
                previous_portfolio=list(previous_benchmark_stocks.keys()) if previous_benchmark_stocks else None
            )

            if not benchmark_weights:
                print(f"경고: {rebalance_date}에 대한 벤치마크 포트폴리오를 생성할 수 없습니다.")
                continue

            # 현재 포트폴리오 주식 추적에 추가
            for stock in benchmark_weights.keys():
                previous_benchmark_stocks[stock] = True

            portfolio_weights['benchmark'][rebalance_date] = benchmark_weights
            print(f"벤치마크 포트폴리오 생성 완료: {len(benchmark_weights)}개 주식")

            # 팩터 포트폴리오 생성
            print("성장 포트폴리오 생성 중...")
            growth_quantiles, growth_scores, growth_metrics = create_growth_portfolio(
                data_dict, rebalance_date, excluded_tickers=excluded_tickers
            )

            print("가치 포트폴리오 생성 중...")
            value_quantiles, value_scores, value_metrics = create_value_portfolio(
                data_dict, rebalance_date, excluded_tickers=excluded_tickers
            )

            print("모멘텀 포트폴리오 생성 중...")
            momentum_quantiles, momentum_scores, momentum_metrics = create_momentum_portfolio(
                data_dict, rebalance_date, excluded_tickers=excluded_tickers
            )

            print("저변동성 포트폴리오 생성 중...")
            low_vol_quantiles, low_vol_scores, low_vol_metrics = create_low_vol_portfolio(
                data_dict, rebalance_date, excluded_tickers=excluded_tickers
            )

            print("품질 포트폴리오 생성 중...")
            quality_quantiles, quality_scores, quality_metrics = create_quality_portfolio(
                data_dict, rebalance_date, excluded_tickers=excluded_tickers
            )

            # 분위수와 지표 분위수 저장
            if not growth_quantiles.empty:
                factor_quantiles['growth'][rebalance_date] = growth_quantiles
                factor_metrics['growth'][rebalance_date] = growth_metrics
                print(f"성장 분위수 저장 완료: {len(growth_quantiles)}개 주식")

            if not value_quantiles.empty:
                factor_quantiles['value'][rebalance_date] = value_quantiles
                factor_metrics['value'][rebalance_date] = value_metrics
                print(f"가치 분위수 저장 완료: {len(value_quantiles)}개 주식")

            if not momentum_quantiles.empty:
                factor_quantiles['momentum'][rebalance_date] = momentum_quantiles
                factor_metrics['momentum'][rebalance_date] = momentum_metrics
                print(f"모멘텀 분위수 저장 완료: {len(momentum_quantiles)}개 주식")

            if not low_vol_quantiles.empty:
                factor_quantiles['low_vol'][rebalance_date] = low_vol_quantiles
                factor_metrics['low_vol'][rebalance_date] = low_vol_metrics
                print(f"저변동성 분위수 저장 완료: {len(low_vol_quantiles)}개 주식")

            if not quality_quantiles.empty:
                factor_quantiles['quality'][rebalance_date] = quality_quantiles
                factor_metrics['quality'][rebalance_date] = quality_metrics
                print(f"품질 분위수 저장 완료: {len(quality_quantiles)}개 주식")

            # 분위수에 따라 가중치 조정
            print("가중치 조정 중...")
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
            try:
                print("개별 지표 포트폴리오 생성 중...")
                metric_weights, metric_quant = create_metric_portfolios(
                    data_dict, rebalance_date, benchmark_weights,
                    excluded_tickers=excluded_tickers,
                    previous_metrics=previous_metric_stocks
                )

                # 생성된 메트릭 포트폴리오 저장
                for metric_name, weights in metric_weights.items():
                    if metric_name not in metric_portfolio_weights:
                        metric_portfolio_weights[metric_name] = {}

                    metric_portfolio_weights[metric_name][rebalance_date] = weights

                    # 이전 주식 정보 저장
                    if metric_name not in previous_metric_stocks:
                        previous_metric_stocks[metric_name] = []
                    previous_metric_stocks[metric_name].extend(list(weights.keys()))
                    # 중복 제거
                    previous_metric_stocks[metric_name] = list(set(previous_metric_stocks[metric_name]))

                # 분위수 저장
                for metric_name, quantiles in metric_quant.items():
                    if metric_name not in metric_quantiles:
                        metric_quantiles[metric_name] = {}

                    metric_quantiles[metric_name][rebalance_date] = quantiles

                print(f"{len(metric_weights)}개 개별 지표 포트폴리오 생성 완료")
            except Exception as e:
                print(f"개별 지표 포트폴리오 생성 중 오류: {e}")
                traceback.print_exc()

            # 각 팩터에 대한 정보 계수 계산
            try:
                print("정보 계수(IC) 계산 중...")
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
                            if (stock in current_prices.index and stock in future_prices.index and
                                    current_prices[stock] > 0 and not pd.isna(current_prices[stock]) and
                                    not pd.isna(future_prices[stock])):
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
                                    print(f"성장 IC 계산 완료: {len(valid_stocks)}개 주식")

                            if not value_scores.empty:
                                valid_stocks = list(set(returns_series.index) & set(value_scores.index))
                                if valid_stocks:
                                    factor_ic['value'].append({
                                        'date': rebalance_date,
                                        'ic': calculate_ic(value_scores[valid_stocks], returns_series[valid_stocks])
                                    })
                                    print(f"가치 IC 계산 완료: {len(valid_stocks)}개 주식")

                            if not momentum_scores.empty:
                                valid_stocks = list(set(returns_series.index) & set(momentum_scores.index))
                                if valid_stocks:
                                    factor_ic['momentum'].append({
                                        'date': rebalance_date,
                                        'ic': calculate_ic(momentum_scores[valid_stocks], returns_series[valid_stocks])
                                    })
                                    print(f"모멘텀 IC 계산 완료: {len(valid_stocks)}개 주식")

                            if not low_vol_scores.empty:
                                valid_stocks = list(set(returns_series.index) & set(low_vol_scores.index))
                                if valid_stocks:
                                    factor_ic['low_vol'].append({
                                        'date': rebalance_date,
                                        'ic': calculate_ic(low_vol_scores[valid_stocks], returns_series[valid_stocks])
                                    })
                                    print(f"저변동성 IC 계산 완료: {len(valid_stocks)}개 주식")

                            if not quality_scores.empty:
                                valid_stocks = list(set(returns_series.index) & set(quality_scores.index))
                                if valid_stocks:
                                    factor_ic['quality'].append({
                                        'date': rebalance_date,
                                        'ic': calculate_ic(quality_scores[valid_stocks], returns_series[valid_stocks])
                                    })
                                    print(f"품질 IC 계산 완료: {len(valid_stocks)}개 주식")
            except Exception as e:
                print(f"정보 계수 계산 중 오류: {e}")
                traceback.print_exc()

        except Exception as e:
            print(f"{rebalance_date}에 대한 포트폴리오 구축 중 오류: {e}")
            traceback.print_exc()

    # 일일 포트폴리오 가치 및 수익률 계산
    print("포트폴리오 성과 구축 중...")

    # 1. 팩터 포트폴리오
    portfolio_values = {}
    portfolio_returns = {}

    for portfolio_type in portfolio_weights:
        if portfolio_weights[portfolio_type]:
            print(f"{portfolio_type} 포트폴리오 성과 구축 중...")
            portfolio_values[portfolio_type] = build_portfolio_performance(
                data_dict['pr_bd'], portfolio_weights[portfolio_type], start_date, end_date
            )

            if not portfolio_values[portfolio_type].empty:
                print(f"{portfolio_type} 포트폴리오 일별 수익률 계산 중...")
                portfolio_returns[portfolio_type] = calculate_daily_returns(
                    data_dict['pr_bd'], portfolio_values[portfolio_type]
                )

    # 2. 개별 지표 포트폴리오
    metric_portfolio_values = {}
    metric_portfolio_returns = {}

    for metric_name in metric_portfolio_weights:
        if metric_portfolio_weights[metric_name]:
            print(f"{metric_name} 지표 포트폴리오 성과 구축 중...")
            metric_portfolio_values[metric_name] = build_portfolio_performance(
                data_dict['pr_bd'], metric_portfolio_weights[metric_name], start_date, end_date
            )

            if not metric_portfolio_values[metric_name].empty:
                print(f"{metric_name} 지표 포트폴리오 일별 수익률 계산 중...")
                metric_portfolio_returns[metric_name] = calculate_daily_returns(
                    data_dict['pr_bd'], metric_portfolio_values[metric_name]
                )

    # 성능 지표 계산
    print("성능 지표 계산 중...")

    # 1. 팩터 포트폴리오
    performance_metrics = {}
    for portfolio_type in portfolio_returns:
        if portfolio_returns[portfolio_type] is not None and not portfolio_returns[portfolio_type].empty:
            print(f"{portfolio_type} 포트폴리오 성능 지표 계산 중...")
            performance_metrics[portfolio_type] = calculate_performance_metrics(
                portfolio_returns[portfolio_type],
                windows=[21, 63, 126, 252, 756, 1260]  # 1개월, 3개월, 6개월, 1년, 3년, 5년
            )

    # 2. 개별 지표 포트폴리오
    metric_performance_metrics = {}
    for metric_name in metric_portfolio_returns:
        if metric_portfolio_returns[metric_name] is not None and not metric_portfolio_returns[metric_name].empty:
            print(f"{metric_name} 지표 포트폴리오 성능 지표 계산 중...")
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


# 메인 실행 함수
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

    # 사용 가능한 모든 날짜를 사용하도록 수정
    # 날짜 범위를 명시적으로 지정하지 않음 - build_factor_portfolios 함수가 자동으로 결정

    print("팩터 포트폴리오 구축 시도 중...")
    try:
        # EXCLUDED_TICKERS가 전역 변수로 있으면 사용
        excluded_tickers = None
        if 'EXCLUDED_TICKERS' in globals():
            excluded_tickers = EXCLUDED_TICKERS

        results = build_factor_portfolios(data_dict, excluded_tickers=excluded_tickers)

        if results is None:
            print("팩터 포트폴리오 구축에 실패했습니다.")
            return None, None

        # 날짜 범위 결정 - 결과에서 사용된 날짜 범위 가져오기
        if 'portfolio_returns' in results and 'benchmark' in results['portfolio_returns']:
            dates = results['portfolio_returns']['benchmark']['date']
            if not dates.empty:
                start_date = dates.min()
                end_date = dates.max()

                print("모멘텀 퀀타일 베타 계산 중...")
                momentum_betas = calculate_momentum_quantile_betas(
                    data_dict,
                    results.get('factor_quantiles', {}),
                    start_date,
                    end_date
                )
            else:
                print("벤치마크 포트폴리오에서 날짜를 찾을 수 없어 모멘텀 베타를 계산할 수 없습니다.")
                momentum_betas = None
        else:
            print("벤치마크 포트폴리오 결과가 없어 모멘텀 베타를 계산할 수 없습니다.")
            momentum_betas = None

        print("결과를 CSV로 저장 중...")
        output_dir = 'factor_portfolio_output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        save_results_to_csv(results, output_dir=output_dir)

        # 모멘텀 베타 별도로 저장
        if momentum_betas is not None:
            save_momentum_beta_to_csv(momentum_betas, output_dir=output_dir)
        else:
            print("모멘텀 베타 계산 중 오류가 발생했습니다.")

        print("완료!")
        return results, momentum_betas
    except Exception as e:
        print(f"팩터 포트폴리오 구축 중 오류: {e}")
        traceback.print_exc()
        return None, None


# 메인 실행 코드
if __name__ == "__main__":
    try:
        print("팩터 포트폴리오 분석 시작...")
        results, momentum_betas = main()
        if results is not None:
            print("팩터 포트폴리오 분석 완료!")
        else:
            print("오류로 인해 분석이 완료되지 않았습니다.")
    except Exception as e:
        print(f"메인 실행 중 오류 발생: {e}")
        traceback.print_exc()