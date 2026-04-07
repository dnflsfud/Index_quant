#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Factor Portfolio Analysis System - Final Optimized Version
==============================================
Investment factor analysis system combining clear structure and optimal performance

Sections
--------
1. Configuration and Logging System
2. DataRepository - Efficient Data Loading and Caching
3. MetricEngine - Growth/Value/Momentum/LowVol/Quality Factor Calculation
4. PortfolioEngine - Benchmark and Factor Portfolio Construction
5. Performance and Information Coefficient (IC) Utilities
6. ReportEngine - Result Output and Storage
7. CLI Entry Point and Main Execution

Run Examples:
    # Basic execution
    python factor_portfolio_optimized.py

    # Multiprocessing and detailed logging
    python factor_portfolio_optimized.py --jobs 0 --log DEBUG
"""
from __future__ import annotations

import argparse
import bisect
import logging
import os
import re
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.stats import spearmanr

# ───────────────────────────── tqdm (optional) ──────────────────────────────
try:
    from tqdm import tqdm  # pip install tqdm

    TQDM_AVAILABLE = True
except ImportError:  # False if module is not available
    TQDM_AVAILABLE = False
    tqdm = None

###############################################################################
# 1. Configuration and Logging System                                         #
###############################################################################

CONFIG: Dict[str, Any] = {
    "DATA": {
        "INDEX": "C:/Users/westl/PycharmProjects/pythonProject/Index.xlsx",
        "OPPOR": "C:/Users/westl/PycharmProjects/pythonProject/S&P500.xlsx",
        "FACTSET": "C:/Users/westl/PycharmProjects/pythonProject/D_Factset.xlsx",
        "FACTSET_REV": "C:/Users/westl/PycharmProjects/pythonProject/D_Revision_SPX.xlsx",
        "FACTSET_IDX": "C:/Users/westl/PycharmProjects/pythonProject/D_Index_Factset.xlsx",
    },
    "EXCLUDED_TICKERS": {
        "SAP US Equity",
        "BABA US Equity",
        "TCEHY US Equity",
        "BIDU US Equity",
        "BRK/B US Equity",
    },
    "TOP_N": 80,
    "OUTPUT_DIR": Path("factor_portfolio_output"),
    "JOBS": None,  # None→serial processing, 0→(CPU cores-1), n→n workers
    "LOG_LEVEL": "INFO",
    "CACHE_SIZE": 512,  # LRU cache size
}


class LoggerSetup:
    """Logging system setup and management class"""

    @staticmethod
    def setup(level: str) -> None:
        """Set logging level and format

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO),
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    @staticmethod
    def progress_bar(iterable=None, total=None, desc=None):
        """Display progress (tqdm or alternative implementation)

        Args:
            iterable: Iterable object
            total: Total number of items
            desc: Progress bar description

        Returns:
            tqdm object or alternative iterator
        """
        if TQDM_AVAILABLE:
            return tqdm(iterable, total=total, desc=desc)

        # Simple alternative implementation when tqdm is not available
        class SimpleProg:
            def __init__(self, iterable, total, desc):
                self.iterable = iterable
                self.total = total or len(iterable) if hasattr(iterable, "__len__") else None
                self.desc = desc
                self.count = 0
                self.last_print = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.iterable is None:
                    raise StopIteration

                try:
                    value = next(self._iterator)
                    self.update()
                    return value
                except StopIteration:
                    if self.desc:
                        print(f"\r{self.desc}: 100% complete", end="")
                        print()  # line break
                    raise

            def update(self, n=1):
                self.count += n
                now = time.time()
                if now - self.last_print > 0.5 and self.total:  # update every 0.5 seconds
                    pct = min(100, int(self.count * 100 / self.total))
                    if self.desc:
                        print(f"\r{self.desc}: {pct}% ({self.count}/{self.total})", end="", flush=True)
                    self.last_print = now

            def __enter__(self):
                self._iterator = iter(self.iterable)
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.desc:
                    print()  # line break

        return SimpleProg(iterable, total, desc)


def timed(fn):
    """Function execution time measurement decorator

    Measures function execution time and logs at DEBUG level

    Args:
        fn: Function to measure

    Returns:
        Wrapped function
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logging.debug("%s: %.3fs", fn.__name__, elapsed)
        return result

    return wrapper


###############################################################################
# 2. Data Repository and Caching System                                       #
###############################################################################

@dataclass
class DataRepository:
    """Class for managing data loading, caching, and preprocessing

    This class efficiently loads data from Excel files, caches it,
    and transforms it into the format needed for analysis.
    """
    cfg: Dict[str, Any]

    # Fields not initialized
    store: Dict[str, pd.DataFrame] = field(default_factory=dict, init=False)
    _xl_cache: Dict[Tuple[str, int | str], pd.DataFrame] = field(
        default_factory=dict, init=False, repr=False
    )
    _all_dates: List[pd.Timestamp] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        """Load data after instance creation"""
        self._load()
        # Cache available dates
        if 'pr_bd' in self.store:
            self._all_dates = sorted(self.store['pr_bd']['date'].unique())

    @timed
    def _xl(self, path: str | Path, sheet: int | str, **kw) -> pd.DataFrame:
        """Load Excel file (with caching)

        Optimizes repeated access to the same Excel sheet by caching

        Args:
            path: Excel file path
            sheet: Sheet number or name
            **kw: Additional arguments for pandas.read_excel

        Returns:
            Loaded dataframe (copy)
        """
        key = (str(path), sheet)
        if key not in self._xl_cache:
            try:
                self._xl_cache[key] = pd.read_excel(path, sheet_name=sheet, **kw)
            except Exception as e:
                logging.error("Excel loading error (%s, %s): %s", path, sheet, e)
                return pd.DataFrame()  # Return empty dataframe on error
        return self._xl_cache[key].copy()

    @staticmethod
    def _clean(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize dataframe

        - Ensures 'date' column always exists
        - Removes data before 2013-01-01
        - Converts date data type

        Args:
            df: Original dataframe

        Returns:
            Cleaned dataframe
        """
        # Check if first column is a date and rename if needed
        cols = list(df.columns)
        if "date" not in cols:
            # Assume first column is the calendar column
            first = cols[0]
            df = df.rename(columns={first: "date"})

        # Convert and filter dates
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])  # Remove rows with failed date conversion
        df = df[df["date"] >= "2013-01-01"].reset_index(drop=True)
        return df

    def _rename(self, cols):
        """Standardize column names (convert to US Equity format)

        Args:
            cols: Original column name list

        Returns:
            Standardized column name list
        """
        return [
            re.sub(r"-US\^", " US Equity", c) if isinstance(c, str) else "date"
            for c in cols
        ]

    @timed
    def _load(self):
        """Load and preprocess all data

        Loads data from Excel files, merges appropriately, and stores in the store
        """
        # Get file paths from config
        idx, opp, fct, rev = (
            self.cfg["DATA"][k] for k in ("INDEX", "OPPOR", "FACTSET", "FACTSET_REV")
        )

        # Load benchmark date data and price data
        bd = self._clean(self._xl(idx, 14))
        pr = self._clean(self._xl(opp, 0))
        self.store["pr"] = bd[["date"]].merge(pr, on="date", how="left")

        # Load price data including SPX
        pr_res = self._clean(self._xl(idx, 0))
        self.store["pr_res"] = bd[["date"]].merge(pr_res, on="date", how="left")

        # ---- Load Bloomberg sheets ----
        sheets = {
            "cap": 7,  # Market cap
            "eps": 1,  # EPS
            "sales": 2,  # Sales
            "opm": 8,  # Operating profit margin
            "roe": 10,  # ROE
            "pe": 3,  # P/E
            "peg": 4,  # PEG
            "pb": 11,  # P/B
            "senti": 13,  # Sentiment
        }

        for key, sheet_no in sheets.items():
            df = self._clean(self._xl(opp, sheet_no))
            self.store[key] = bd[["date"]].merge(df, on="date", how="left")

        # ---- Load FactSet sheets ----
        f_sheets = {
            "eps_fact": 2,  # EPS forecast
            "sales_fact": 3,  # Sales forecast
            "opm_fact": 4,  # Operating margin forecast
            "evebit_fact": 5,  # EV/EBITDA
            "fcf_fact": 6,  # Free cash flow
            "eps_surprise": 7,  # EPS surprise
            "sales_surprise": 8,  # Sales surprise
        }

        for key, sheet_no in f_sheets.items():
            df = self._clean(self._xl(fct, sheet_no, skiprows=1))
            df.columns = self._rename(df.columns)
            self.store[key] = bd[["date"]].merge(df, on="date", how="left")

        # ---- Load revision sheets ----
        rev_sheets = {"eps_rev": 1, "sales_rev": 2}  # EPS/Sales forecast revisions

        for key, sheet_no in rev_sheets.items():
            df = self._clean(self._xl(rev, sheet_no, skiprows=1))
            df.columns = self._rename(df.columns)
            self.store[key] = bd[["date"]].merge(df, on="date", how="left")

        # ---- Calculate sentiment 7-day rolling sum ----
        if "senti" in self.store:
            senti = self.store.pop("senti")
            try:
                self.store["senti"] = (
                    senti.set_index("date")
                    .rolling("7D")
                    .sum()
                    .reset_index()
                )
            except Exception as e:
                logging.error("Sentiment rolling calculation error: %s", e)
                # Keep original data on error
                self.store["senti"] = senti

        logging.info("Datasets loaded: %s", list(self.store.keys()))

    @lru_cache(maxsize=CONFIG["CACHE_SIZE"])
    def get_nearest_date(self, target_date: pd.Timestamp, max_days: int = 5,
                         direction: str = "before") -> Optional[pd.Timestamp]:
        """Find the closest data date to a given date

        Args:
            target_date: Target date
            max_days: Maximum difference in days
            direction: 'before'(prior), 'after'(later), 'both'(bidirectional)

        Returns:
            Closest date or None
        """
        if not self._all_dates:
            return None

        idx = bisect.bisect_left(self._all_dates, target_date)

        if direction == "before":
            # Search for previous date
            if idx == 0:
                return None
            nearest = self._all_dates[idx - 1]
            days_diff = (target_date - nearest).days
            return nearest if days_diff <= max_days else None

        elif direction == "after":
            # Search for later date
            if idx >= len(self._all_dates):
                return None
            nearest = self._all_dates[idx]
            days_diff = (nearest - target_date).days
            return nearest if days_diff <= max_days else None

        else:  # "both"
            # Check for exact match
            if idx < len(self._all_dates) and self._all_dates[idx] == target_date:
                return target_date

            # Select closer of before/after dates
            before_date = self._all_dates[idx - 1] if idx > 0 else None
            after_date = self._all_dates[idx] if idx < len(self._all_dates) else None

            before_diff = (target_date - before_date).days if before_date else float('inf')
            after_diff = (after_date - target_date).days if after_date else float('inf')

            if before_diff <= after_diff and before_diff <= max_days:
                return before_date
            elif after_diff <= max_days:
                return after_date
            return None

    @lru_cache(maxsize=CONFIG["CACHE_SIZE"])
    def get_latest_date(self, key: str, date: pd.Timestamp,
                        months_ago: int = 0) -> Optional[pd.Timestamp]:
        """Get the most recent date for a dataset before the reference date

        Args:
            key: Dataset key
            date: Reference date
            months_ago: Months in the past from reference date

        Returns:
            Most recent date or None
        """
        if key not in self.store:
            return None

        # Adjust reference date if months_ago specified
        target_date = date
        if months_ago > 0:
            target_date = date - pd.DateOffset(months=months_ago)

        dates = self.store[key]['date']
        rel_dates = dates[dates <= target_date]

        if rel_dates.empty:
            return None

        return rel_dates.max()

    @lru_cache(maxsize=CONFIG["CACHE_SIZE"])
    def get_latest_data(self, key: str, date: pd.Timestamp,
                        months_ago: int = 0) -> pd.Series:
        """Get the latest data for a specific key before the reference date

        Args:
            key: Dataset key
            date: Reference date
            months_ago: Months in the past from reference date

        Returns:
            Latest data (excluding date column) or empty Series
        """
        latest_date = self.get_latest_date(key, date, months_ago)
        if latest_date is None:
            return pd.Series(dtype="float64")

        row = self.store[key][self.store[key]['date'] == latest_date]
        if row.empty:
            return pd.Series(dtype="float64")

        return row.iloc[0].drop("date")

    def get_returns(self, start_date: pd.Timestamp, end_date: pd.Timestamp,
                    stocks: Optional[List[str]] = None) -> pd.DataFrame:
        """Calculate returns for a specific period

        Args:
            start_date: Start date
            end_date: End date
            stocks: Stock list (None means all stocks)

        Returns:
            Returns dataframe
        """
        if 'pr' not in self.store:
            return pd.DataFrame()

        # Filter by date range
        price_data = self.store['pr'][
            (self.store['pr']['date'] >= start_date) &
            (self.store['pr']['date'] <= end_date)
            ].copy()

        if price_data.empty:
            return pd.DataFrame()

        # Filter specific stocks
        cols = ['date']
        if stocks:
            available = [s for s in stocks if s in price_data.columns]
            cols.extend(available)
        else:
            cols.extend([c for c in price_data.columns if c != 'date'])

        price_data = price_data[cols]

        # Sort by date
        price_data = price_data.sort_values('date')

        # Calculate returns
        price_pivot = price_data.set_index('date')
        returns = price_pivot.pct_change()

        return returns.reset_index()

    def get_top_n_stocks(self, date: pd.Timestamp, n: int = CONFIG["TOP_N"]) -> List[str]:
        """Get top N stocks by market capitalization

        Args:
            date: Reference date
            n: Number of stocks to retrieve

        Returns:
            Stock list
        """
        # Get market cap data
        cap_data = self.get_latest_data("cap", date)
        if cap_data.empty:
            return []

        # Filter excluded tickers
        cap_data = cap_data[~cap_data.index.isin(self.cfg["EXCLUDED_TICKERS"])]

        # Select top N
        return cap_data.sort_values(ascending=False).head(n).index.tolist()


###############################################################################
# 3. Metric Engine                                                            #
###############################################################################

def qcut(s: pd.Series, q: int, asc: bool) -> pd.Series:
    """Optimized function to divide a series into quantiles

    Wrapper for pandas qcut with improved NaN handling and duplicate value handling

    Args:
        s: Input series
        q: Number of quantiles
        asc: True for ascending sort (lower values better), False for descending (higher values better)

    Returns:
        Series with quantile labels (1 to q)
    """
    # Handle all-NaN case
    if s.isna().all():
        return pd.Series(index=s.index, dtype="float64")

    # Calculate ranks excluding NaNs
    r = s.rank(method="first", ascending=asc)

    try:
        # Try basic approach
        return pd.qcut(r, q, labels=False, duplicates="drop") + 1
    except ValueError:
        # Alternative method for many duplicate values
        bins = np.linspace(r.min(), r.max() + 1e-9, q + 1)
        return pd.cut(r, bins=bins, labels=False, include_lowest=True) + 1


@dataclass
class MetricEngine:
    """Factor and metric calculation engine

    Handles calculation of investment factors (growth, value, momentum, low-vol, quality)
    and individual metrics.

    Attributes:
        repo: Data repository
        top_n: Number of top stocks to analyze
        excluded: Set of tickers to exclude
        factor_quantiles: Dictionary to store factor quantiles
        metric_quantiles: Dictionary to store metric quantiles
    """
    repo: DataRepository
    top_n: int = CONFIG["TOP_N"]
    excluded: Set[str] = field(default_factory=lambda: set(CONFIG["EXCLUDED_TICKERS"]))

    # Quantile storage dictionaries
    factor_quantiles: Dict[str, Dict[pd.Timestamp, pd.Series]] = field(
        default_factory=dict, init=False, repr=False
    )
    metric_quantiles: Dict[str, Dict[pd.Timestamp, pd.Series]] = field(
        default_factory=dict, init=False, repr=False
    )

    def _top(self, date: pd.Timestamp) -> List[str]:
        """Get top N stocks by market capitalization

        Args:
            date: Reference date

        Returns:
            List of top stocks
        """
        return self.repo.get_top_n_stocks(date, self.top_n)

    def _growth(self, top: List[str], date: pd.Timestamp) -> pd.DataFrame:
        """Calculate growth metrics

        Calculates the following metrics:
        - eps_g3: 3-month EPS growth
        - eps_g12: 12-month EPS growth
        - sales_g12: 12-month sales growth
        - eps_rev: EPS forecast revision
        - sales_rev: Sales forecast revision
        - eps_surprise: EPS surprise
        - peg_inv: PEG inverse

        Args:
            top: List of stocks to analyze
            date: Reference date

        Returns:
            Growth metrics dataframe
        """
        # Create initial dataframe
        out = pd.DataFrame(index=top)

        # Current EPS forecast
        now = self.repo.get_latest_data("eps_fact", date)

        # 3-month EPS growth
        eps_3m_ago = self.repo.get_latest_data("eps_fact", date, 3)
        out["eps_g3"] = (now - eps_3m_ago) / now.replace({0: np.nan}).abs()

        # 12-month EPS growth
        eps_12m_ago = self.repo.get_latest_data("eps_fact", date, 12)
        out["eps_g12"] = (now - eps_12m_ago) / now.replace({0: np.nan}).abs()

        # 12-month sales growth
        sales_now = self.repo.get_latest_data("sales_fact", date)
        sales_12m_ago = self.repo.get_latest_data("sales_fact", date, 12)
        out["sales_g12"] = (sales_now - sales_12m_ago) / sales_now.replace({0: np.nan}).abs()

        # EPS and sales forecast revisions
        out["eps_rev"] = self.repo.get_latest_data("eps_rev", date)
        out["sales_rev"] = self.repo.get_latest_data("sales_rev", date)

        # EPS surprise
        out["eps_surprise"] = self.repo.get_latest_data("eps_surprise", date)

        # PEG inverse (prevent division by zero)
        peg = self.repo.get_latest_data("peg", date)
        out["peg_inv"] = 1 / peg.replace({0: np.nan})

        return out.fillna(0)

    def _value(self, top: List[str], date: pd.Timestamp) -> pd.DataFrame:
        """Calculate value metrics

        Calculates the following metrics:
        - pe: P/E ratio
        - pb: P/B ratio
        - ev_ebitda: EV/EBITDA

        Args:
            top: List of stocks to analyze
            date: Reference date

        Returns:
            Value metrics dataframe
        """
        # Create initial dataframe
        out = pd.DataFrame(index=top)

        # P/E and P/B ratios
        out["pe"] = self.repo.get_latest_data("pe", date)
        out["pb"] = self.repo.get_latest_data("pb", date)

        # EV/EBITDA
        out["ev_ebitda"] = self.repo.get_latest_data("evebit_fact", date)

        return out.fillna(0)

    def _momentum(self, top: List[str], date: pd.Timestamp) -> pd.DataFrame:
        """Calculate momentum metrics

        Calculates the following metrics:
        - mom_1m: 1-month momentum
        - mom_3m: 3-month momentum
        - mom_12m: 12-month momentum
        - mom_12m_ex1m: 12-month momentum excluding the last month
        - eps_rev_3m_chg: 3-month EPS forecast change

        Args:
            top: List of stocks to analyze
            date: Reference date

        Returns:
            Momentum metrics dataframe
        """
        # Create initial dataframe
        out = pd.DataFrame(index=top)

        # Prepare price data
        pr = self.repo.store["pr"].set_index("date")
        if date not in pr.index:
            return out

        # Current price
        cur = pr.loc[date, top]

        # Calculate momentum for different periods
        for m, lbl in [(1, "mom_1m"), (3, "mom_3m"), (12, "mom_12m")]:
            past_date = date - pd.DateOffset(months=m)
            past_rows = pr[pr.index <= past_date]

            if past_rows.empty:
                continue

            past = past_rows.iloc[-1][top]
            out[lbl] = cur / past - 1

        # 12-month momentum excluding 1-month
        if {"mom_12m", "mom_1m"}.issubset(out.columns):
            out["mom_12m_ex1m"] = (1 + out["mom_12m"]) / (1 + out["mom_1m"]) - 1

        # 3-month EPS forecast revision change
        rev_now = self.repo.get_latest_data("eps_rev", date)
        rev_past = self.repo.get_latest_data("eps_rev", date - pd.DateOffset(months=3))
        out["eps_rev_3m_chg"] = rev_now - rev_past

        return out.fillna(0)

    def _low_vol(self, top: List[str], date: pd.Timestamp) -> pd.DataFrame:
        """Calculate low volatility metrics

        Calculates the following metrics:
        - vol_3m: 3-month volatility
        - beta_3y: 3-year beta

        Args:
            top: List of stocks to analyze
            date: Reference date

        Returns:
            Low volatility metrics dataframe
        """
        # Prepare price data
        pr = self.repo.store["pr"].set_index("date")

        # Get prices from 3 years ago to current date
        three_years = pr.loc[date - pd.DateOffset(years=3): date, top]

        # Calculate returns
        ret = three_years.pct_change().dropna()

        # Calculate 3-month volatility
        vol3m = ret.tail(63).std() * np.sqrt(252)  # Annualized

        # Calculate beta
        beta = pd.Series(index=top, dtype="float64")

        # Only calculate beta if SPX index is available
        if "SPX Index" in three_years.columns:
            mkt = three_years["SPX Index"].pct_change().dropna()

            # Calculate beta for each stock
            for s in top:
                if s in ret.columns and len(ret[s]) > 30:
                    # Use common index
                    common = ret[s].index.intersection(mkt.index)

                    if len(common) > 30:
                        stock_ret = ret[s][common]
                        mkt_ret = mkt[common]

                        cov = stock_ret.cov(mkt_ret)
                        var = mkt_ret.var()

                        # Prevent division by zero
                        beta[s] = cov / var if var > 0 else np.nan

        # Combine results (fill NaN with volatility median)
        return pd.DataFrame({"vol_3m": vol3m, "beta_3y": beta}).fillna(vol3m.median())

    def _quality(self, top: List[str], date: pd.Timestamp) -> pd.DataFrame:
        """Calculate quality metrics

        Calculates the following metrics:
        - roe: Return on equity
        - op_margin: Operating margin
        - fcf_g12: 12-month free cash flow growth

        Args:
            top: List of stocks to analyze
            date: Reference date

        Returns:
            Quality metrics dataframe
        """
        # Create initial dataframe
        out = pd.DataFrame(index=top)

        # ROE and operating margin
        out["roe"] = self.repo.get_latest_data("roe", date)
        out["op_margin"] = self.repo.get_latest_data("opm_fact", date)

        # 12-month free cash flow growth
        fcf_now = self.repo.get_latest_data("fcf_fact", date)
        fcf_past = self.repo.get_latest_data("fcf_fact", date, 12)
        out["fcf_g12"] = (fcf_now - fcf_past) / fcf_past.replace({0: np.nan}).abs()

        return out.fillna(0)

    def _score(self, metrics: pd.DataFrame, asc: bool) -> Tuple[pd.Series, pd.DataFrame]:
        """Score metrics and calculate quantiles

        Converts each metric to 10 quantiles, then averages and converts to 5 quantiles

        Args:
            metrics: Metrics dataframe
            asc: Ascending flag (True: lower is better, False: higher is better)

        Returns:
            (5-quantile series, 10-quantile dataframe)
        """
        # Convert each metric to 10 quantiles
        q10 = metrics.apply(lambda s: qcut(s, 10, asc))

        # Convert average of 10 quantiles to 5 quantiles
        q5 = qcut(q10.mean(axis=1), 5, asc=False)  # Higher average score is always better

        return q5, q10

    @timed
    def composite_scores(self, date: pd.Timestamp) -> Dict[str, Tuple[pd.Series, pd.DataFrame]]:
        """Calculate composite scores for all factors

        Calculate metrics and quantiles for each factor

        Args:
            date: Reference date

        Returns:
            Dictionary of (5-quantile, 10-quantile dataframe) tuples by factor
        """
        # Get top stocks
        top = self._top(date)
        if not top:
            return {}

        # Calculate scores for each factor
        res = {
            "growth": self._score(self._growth(top, date), asc=False),
            "value": self._score(self._value(top, date), asc=True),
            "momentum": self._score(self._momentum(top, date), asc=False),
            "low_vol": self._score(self._low_vol(top, date), asc=True),
            "quality": self._score(self._quality(top, date), asc=False),
        }

        # Store quantiles
        for fac, (q5, q10) in res.items():
            # Store factor quantiles
            self.factor_quantiles.setdefault(fac, {})[date] = q5

            # Store individual metric quantiles
            for col in q10.columns:
                mname = f"{fac}_{col}"
                q_m = qcut(q10[col], 5, asc=(fac in {"value", "low_vol"}))
                self.metric_quantiles.setdefault(mname, {})[date] = q_m

        return res


###############################################################################
# 4. Portfolio Engine                                                         #
###############################################################################

@dataclass
class PortfolioEngine:
    """Portfolio construction and management engine

    Handles benchmark and various factor/metric-based portfolio construction.

    Attributes:
        repo: Data repository
        metric_engine: Metric calculation engine
    """
    repo: DataRepository
    metric_engine: MetricEngine

    def benchmark(self, date: pd.Timestamp) -> Dict[str, float]:
        """Construct benchmark portfolio (market cap weighted)

        Args:
            date: Reference date

        Returns:
            Dictionary of stock weights
        """
        # Get top stocks
        top = self.metric_engine._top(date)

        # Get market cap data
        cap_row = self.repo.store["cap"][self.repo.store["cap"]["date"] == date]
        if cap_row.empty:
            return {}

        # Extract market cap and calculate weights
        caps = cap_row.drop(columns="date").iloc[0][top]
        w = (caps / caps.sum()).round(4)

        return w.to_dict()

    def _adjust(self, bm: Dict[str, float], q: pd.Series, asc=False) -> Dict[str, float]:
        """Adjust benchmark weights based on quantiles

        Args:
            bm: Benchmark weights
            q: Quantile series
            asc: Whether quantiles are ascending

        Returns:
            Adjusted weight dictionary
        """
        if q.empty:
            return bm

        # Weight adjustment factors by quantile
        factors = {1: 1.2, 2: 1.1, 3: 1.0, 4: 0.9, 5: 0.8}

        # Adjust each stock's weight
        w = {s: bm.get(s, 0) * factors[int(q[s])] for s in q.index if s in bm}

        # Normalize so weights sum to 1
        tot = sum(w.values())
        if tot > 0:
            w = {k: round(v / tot, 4) for k, v in w.items() if v > 0}

        return w

    @timed
    def build_date(self, date: pd.Timestamp) -> Dict[str, Dict[str, float]]:
        """Build all portfolios for a specific date

        Constructs benchmark, factor-based, and individual metric portfolios

        Args:
            date: Reference date

        Returns:
            Dictionary of portfolio weights by type
        """
        # Build benchmark portfolio
        bm = self.benchmark(date)

        # Calculate all factor scores
        scores = self.metric_engine.composite_scores(date)

        # Initialize portfolios
        ptf = {"benchmark": bm}

        # Build factor portfolios
        for fac, (q5, _) in scores.items():
            ptf[fac] = self._adjust(bm, q5)

        # Build individual metric portfolios
        for fac, (_, q10) in scores.items():
            for col in q10.columns:
                name = f"{fac}_{col}"
                ptf[name] = self._adjust(bm, qcut(q10[col], 5, asc=(fac in {"value", "low_vol"})))

        return ptf

    @timed
    def build_all(self, dates: List[pd.Timestamp], jobs: Optional[int] = None,
                  progress: bool = False) -> Dict[str, Dict[pd.Timestamp, Dict[str, float]]]:
        """Build portfolios for all dates

        Args:
            dates: List of dates to build portfolios for
            jobs: Number of parallel processes (None: serial, 0: CPU-1, n: n workers)
            progress: Whether to display progress

        Returns:
            Dictionary of portfolio weights by type and date
        """
        # Results dictionary
        out: Dict[str, Dict[pd.Timestamp, Dict[str, float]]] = {}

        # Helper function to insert results
        def _insert(pt: str, d: pd.Timestamp, w):
            out.setdefault(pt, {})[d] = w

        # Serial processing
        if jobs in (None, 1):
            # Set up progress display
            iterator = LoggerSetup.progress_bar(dates, total=len(dates),
                                                desc="Building portfolios") if progress else dates

            # Build portfolios for each date
            for d in iterator:
                for pt, w in self.build_date(d).items():
                    _insert(pt, d, w)

        # Parallel processing
        else:
            # Calculate maximum workers
            max_workers = os.cpu_count() - 1 if jobs == 0 else jobs

            # Progress variables
            total = len(dates)
            done = 0

            # Run parallel execution
            with ProcessPoolExecutor(max_workers) as ex:
                # Submit jobs for each date
                futures = {ex.submit(self.build_date, d): d for d in dates}

                # Process completed jobs
                for fut in as_completed(futures):
                    # Store results
                    for pt, w in fut.result().items():
                        _insert(pt, futures[fut], w)

                    # Update progress
                    if progress:
                        done += 1
                        pct = done * 100 / total
                        print(f"\rBuilding portfolios {pct:5.1f}% ({done}/{total})", end="", flush=True)

                # Add line break after progress display
                if progress:
                    print()

        return out


###############################################################################
# 5. Performance and Information Coefficient Utilities                        #
###############################################################################

@timed
def information_coefficient(scores: pd.Series, fwd_ret: pd.Series) -> float:
    """Calculate Information Coefficient (IC)

    Computes Spearman rank correlation between factor scores and future returns

    Args:
        scores: Factor scores
        fwd_ret: Future returns

    Returns:
        Information coefficient (Spearman correlation)
    """
    # Extract common indices
    common = scores.dropna().index.intersection(fwd_ret.dropna().index)

    # Check minimum data points
    if len(common) < 5:
        return np.nan

    # Calculate Spearman correlation
    return spearmanr(scores.loc[common], fwd_ret.loc[common]).correlation


@timed
def build_portfolio_performance(price_df: pd.DataFrame,
                                weight_dict: Dict[pd.Timestamp, Dict[str, float]]) -> pd.DataFrame:
    """Calculate portfolio performance

    Args:
        price_df: Price dataframe (date and stock prices)
        weight_dict: Dictionary of weights by date

    Returns:
        Dataframe with date and return
    """
    # Create dataframe of weights by date
    rows = [{"date": d, **w} for d, w in sorted(weight_dict.items())]
    wdf = pd.DataFrame(rows).set_index("date").sort_index()

    # Expand to all dates and fill missing values
    wdf = wdf.reindex(price_df['date']).ffill().fillna(0)

    # Calculate weighted prices
    val = (price_df.set_index('date') * wdf).sum(axis=1)

    # Normalize by first day
    val = val / val.iloc[0]

    # Calculate daily returns
    ret = val.pct_change().fillna(0)

    return pd.DataFrame({"date": ret.index, "return": ret.values})


@timed
def daily_returns_all(repo: DataRepository,
                      weights: Dict[str, Dict[pd.Timestamp, Dict[str, float]]]) -> Dict[str, pd.DataFrame]:
    """Calculate daily returns for all portfolios

    Args:
        repo: Data repository
        weights: Portfolio weights by type and date

    Returns:
        Dictionary of daily returns by portfolio type
    """
    # Results dictionary
    out = {}

    # Get price data
    price_df = repo.store["pr"]

    # Calculate performance for each portfolio type
    for n, w in weights.items():
        out[n] = build_portfolio_performance(price_df, w)

    return out


@timed
def performance_metrics(returns_df: pd.DataFrame,
                        windows: List[int] = [21, 63, 126, 252]) -> Dict[str, float]:
    """Calculate portfolio performance metrics

    Args:
        returns_df: Returns dataframe
        windows: List of evaluation periods (days)

    Returns:
        Dictionary of performance metrics
    """
    # Results dictionary
    metrics = {}

    # Check required columns
    if "return" not in returns_df.columns:
        return metrics

    # Returns series
    returns = returns_df["return"].fillna(0)

    # Calculate metrics for each period
    for window in windows:
        if len(returns) >= window:
            # Extract returns for the period
            window_returns = returns.tail(window)

            try:
                # Cumulative return
                cumulative_return = (1 + window_returns).prod() - 1
                metrics[f"{window}d_return"] = cumulative_return

                # Volatility (annualized)
                volatility = window_returns.std() * np.sqrt(252)
                metrics[f"{window}d_volatility"] = volatility

                # Sharpe ratio
                if volatility > 0:
                    avg_return = window_returns.mean() * 252  # Annualized
                    sharpe_ratio = avg_return / volatility
                    metrics[f"{window}d_sharpe"] = sharpe_ratio
            except Exception as e:
                logging.warning(f"{window}d performance metric calculation error: {e}")

    return metrics


###############################################################################
# 6. Report Engine                                                            #
###############################################################################

class ReportEngine:
    """Result storage and reporting engine

    Provides functionality to save analysis results as CSV files

    Attributes:
        out: Output directory path
    """

    def __init__(self, out_dir: Path):
        """
        Args:
            out_dir: Output directory path
        """
        self.out = out_dir
        self.out.mkdir(exist_ok=True)

    @timed
    def save_weights(self, weights: Dict[str, Dict[pd.Timestamp, Dict[str, float]]]):
        """Save portfolio weights

        Args:
            weights: Portfolio weights by type and date
        """
        for name, wd in weights.items():
            # Convert weights by date to dataframe
            df = pd.DataFrame([{"date": d, **w} for d, w in sorted(wd.items())])

            # Save to CSV
            df.to_csv(self.out / f"{name}_weights.csv", index=False)
            logging.info("Saved: %s", name)

    @timed
    def save_returns(self, returns: Dict[str, pd.DataFrame]):
        """Save factor portfolio returns

        Args:
            returns: Portfolio returns by type
        """
        if not returns:
            return

        # Check benchmark data
        base = returns.get("benchmark")
        if base is None or "date" not in base.columns:
            return

        # Create combined dataframe
        out = pd.DataFrame({"date": base["date"]})

        # Add returns for each portfolio
        for name, df in returns.items():
            if "return" in df.columns:
                out[f"{name}_return"] = df["return"]

        # Save to CSV
        out.to_csv(self.out / "factor_portfolio_returns.csv", index=False)

    @timed
    def save_metric_returns(self, m_returns: Dict[str, pd.DataFrame]):
        """Save metric portfolio returns

        Args:
            m_returns: Returns by metric
        """
        if not m_returns:
            return

        # Get dates from first metric
        first = next(iter(m_returns.values()))
        if "date" not in first.columns:
            return

        # Create combined dataframe
        out = pd.DataFrame({"date": first["date"]})

        # Add returns for each metric
        for name, df in m_returns.items():
            if "return" in df.columns:
                out[f"{name}_return"] = df["return"]

        # Save to CSV
        out.to_csv(self.out / "metric_portfolio_returns.csv", index=False)

    @timed
    def save_performance(self, perf_dict: Dict[str, Dict[str, float]], name: str):
        """Save performance metrics

        Args:
            perf_dict: Performance metrics by portfolio type
            name: Filename prefix
        """
        if not perf_dict:
            return

        # Reorganize by metric
        metric_by_window = {}

        for portfolio, metrics in perf_dict.items():
            for metric, value in metrics.items():
                if metric not in metric_by_window:
                    metric_by_window[metric] = {}
                metric_by_window[metric][portfolio] = value

        # Convert to dataframe and save
        df = pd.DataFrame(metric_by_window)
        df.to_csv(self.out / f"{name}_performance_metrics.csv")

    @timed
    def save_quantiles(self, q_dict: Dict[str, Dict[pd.Timestamp, pd.Series]], prefix: str):
        """Save quantile information

        Args:
            q_dict: Quantiles by factor/metric and date
            prefix: Filename prefix
        """
        for fac, qts in q_dict.items():
            # Convert quantiles to rows
            rows = []
            for d, ser in qts.items():
                rows.extend([{"date": d, "stock": s, "quantile": q} for s, q in ser.items()])

            # Convert to dataframe and save
            if rows:
                pd.DataFrame(rows).to_csv(self.out / f"{prefix}_{fac}_quantiles.csv", index=False)

    @timed
    def save_ic(self, ic_dict: Dict[str, List[Dict[str, Any]]]):
        """Save Information Coefficients (IC)

        Args:
            ic_dict: IC information by factor
        """
        for factor, ic_list in ic_dict.items():
            if ic_list:
                pd.DataFrame(ic_list).to_csv(self.out / f"{factor}_ic.csv", index=False)

    @timed
    def save_summary(self, perf_metrics: Dict[str, Dict[str, float]], name: str,
                     periods: List[int] = [21, 63, 126, 252]):
        """Save performance summary table

        Args:
            perf_metrics: Performance metrics
            name: Filename
            periods: Periods (days) to include
        """
        if not perf_metrics:
            return

        # Create results dataframe
        df = pd.DataFrame(index=perf_metrics.keys())

        # Add returns and Sharpe ratios for each period
        for period in periods:
            ret_col = f"{period}d_return"
            sharpe_col = f"{period}d_sharpe"

            df[f"{period}d_Return"] = [
                perf_metrics[p].get(ret_col, np.nan) for p in df.index
            ]

            df[f"{period}d_Sharpe"] = [
                perf_metrics[p].get(sharpe_col, np.nan) for p in df.index
            ]

        # Save to CSV
        df.to_csv(self.out / f"{name}_performance_summary.csv")


###############################################################################
# 7. Main Execution                                                           #
###############################################################################

@timed
def calculate_ic_data(repo: DataRepository, metric_engine: MetricEngine,
                      dates: List[pd.Timestamp]) -> Dict[str, List[Dict[str, Any]]]:
    """Calculate factor Information Coefficients (IC)

    Calculate and store IC for each factor

    Args:
        repo: Data repository
        metric_engine: Metric engine
        dates: Evaluation date list

    Returns:
        Dictionary of IC information by factor
    """
    # Results dictionary
    ic_data = {
        "growth": [],
        "value": [],
        "momentum": [],
        "low_vol": [],
        "quality": []
    }

    # Calculate IC for each date
    for date in dates:
        try:
            # Calculate next month date
            next_month = date + pd.DateOffset(months=1)

            # Calculate returns for next month
            returns = repo.get_returns(date, next_month)

            if returns.empty:
                continue

            # Get current and next month-end prices
            current_price = repo.get_latest_data("pr", date)
            future_dates = returns["date"].sort_values()

            if future_dates.empty:
                continue

            future_date = future_dates.iloc[-1]
            future_price = repo.get_latest_data("pr", future_date)

            # Calculate returns
            future_returns = {}
            for stock in current_price.index:
                if (stock in future_price.index and
                        current_price[stock] > 0 and
                        not pd.isna(current_price[stock]) and
                        not pd.isna(future_price[stock])):
                    future_returns[stock] = future_price[stock] / current_price[stock] - 1

            if not future_returns:
                continue

            returns_series = pd.Series(future_returns)

            # Calculate factor scores
            scores = metric_engine.composite_scores(date)

            # Calculate IC for each factor
            for factor, (_, q10) in scores.items():
                # Calculate average quantile score for each stock
                factor_scores = q10.mean(axis=1)

                # Check common stocks
                common_stocks = set(factor_scores.index) & set(returns_series.index)

                if len(common_stocks) < 5:
                    continue

                # Calculate and store IC
                ic = information_coefficient(
                    factor_scores[list(common_stocks)],
                    returns_series[list(common_stocks)]
                )

                if not pd.isna(ic):
                    ic_data[factor].append({
                        "date": date,
                        "ic": ic
                    })
        except Exception as e:
            logging.warning(f"Error calculating IC for {date}: {e}")

    return ic_data


@timed
def main(argv: Optional[Sequence[str]] = None):
    """Main execution function

    Args:
        argv: Command line arguments
    """
    # Set up argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, help="Parallel processes (0=max CPU-1)")
    ap.add_argument("--log", type=str, help="Log level (DEBUG/INFO/...)")
    args = ap.parse_args(argv)

    # Update configuration
    if args.jobs is not None:
        CONFIG["JOBS"] = args.jobs
    if args.log:
        CONFIG["LOG_LEVEL"] = args.log.upper()

    # Set up logging
    LoggerSetup.setup(CONFIG["LOG_LEVEL"])

    # Initialize data repository and engines
    logging.info("Initializing data and engines")
    repo = DataRepository(CONFIG)
    me = MetricEngine(repo)
    pe = PortfolioEngine(repo, me)

    # Extract price dates and determine rebalancing dates
    price_dates = repo.store["pr"]["date"].sort_values().unique()

    # Select quarter-end dates (after 25th of the last month of each quarter)
    rebals = [d for d in price_dates if d.month % 3 == 0 and d.day > 25]
    logging.info("%d rebalancing dates", len(rebals))

    # Build portfolios
    weights = pe.build_all(rebals, CONFIG["JOBS"], progress=True)

    # Calculate returns
    logging.info("Calculating returns")
    returns_dict = daily_returns_all(repo, weights)

    # Separate factor and metric portfolios
    factors = {"benchmark", "growth", "value", "momentum", "low_vol", "quality"}
    factor_returns = {k: v for k, v in returns_dict.items() if k in factors}
    metric_returns = {k: v for k, v in returns_dict.items() if k not in factors}

    # Calculate performance metrics
    logging.info("Calculating performance metrics")
    factor_performance = {k: performance_metrics(v) for k, v in factor_returns.items()}
    metric_performance = {k: performance_metrics(v) for k, v in metric_returns.items()}

    # Calculate IC
    logging.info("Calculating Information Coefficients (IC)")
    ic_data = calculate_ic_data(repo, me, rebals)

    # Save results
    logging.info("Saving results")
    rep = ReportEngine(CONFIG["OUTPUT_DIR"])
    rep.save_weights(weights)
    rep.save_returns(factor_returns)
    rep.save_metric_returns(metric_returns)
    rep.save_performance(factor_performance, "factor")
    rep.save_performance(metric_performance, "metric")
    rep.save_quantiles(me.factor_quantiles, "factor")
    rep.save_quantiles(me.metric_quantiles, "metric")
    rep.save_ic(ic_data)
    rep.save_summary(factor_performance, "factor_performance")
    rep.save_summary(metric_performance, "metric_performance")

    # Save excluded tickers
    pd.DataFrame({"excluded_tickers": list(CONFIG["EXCLUDED_TICKERS"])}).to_csv(
        CONFIG["OUTPUT_DIR"] / "excluded_tickers.csv", index=False
    )

    logging.info("Complete - Output: %s", CONFIG["OUTPUT_DIR"].resolve())


if __name__ == "__main__":
    main()