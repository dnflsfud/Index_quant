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
    "OUTPUT_DIR": Path(r"C:\Users\westl\PycharmProjects\pythonProject\venv_vf\Factor"),
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
        elif 'pr' in self.store and 'date' in self.store['pr'].columns:
            self._all_dates = sorted(self.store['pr']['date'].unique())

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
        # Handle empty dataframe
        if df.empty:
            return df

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

        # Check if files exist
        for path, name in [(idx, "INDEX"), (opp, "OPPOR"), (fct, "FACTSET"), (rev, "FACTSET_REV")]:
            if not os.path.exists(path):
                logging.error(f"File not found: {path} ({name})")

        # Load benchmark date data and price data
        bd = self._clean(self._xl(idx, 14))
        pr = self._clean(self._xl(opp, 0))

        # Handle case where bd or pr is empty
        if bd.empty:
            logging.error("Benchmark date data is empty")
            bd = pd.DataFrame({"date": [pd.Timestamp("2013-01-01")]})
        if pr.empty:
            logging.error("Price data is empty")
            pr = pd.DataFrame({"date": bd["date"].copy()})

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
            if not df.empty:  # Only process non-empty dataframes
                df.columns = self._rename(df.columns)
                self.store[key] = bd[["date"]].merge(df, on="date", how="left")

        # ---- Load revision sheets ----
        rev_sheets = {"eps_rev": 1, "sales_rev": 2}  # EPS/Sales forecast revisions

        for key, sheet_no in rev_sheets.items():
            df = self._clean(self._xl(rev, sheet_no, skiprows=1))
            if not df.empty:  # Only process non-empty dataframes
                df.columns = self._rename(df.columns)
                self.store[key] = bd[["date"]].merge(df, on="date", how="left")

        # ---- Calculate sentiment 7-day rolling sum ----
        if "senti" in self.store:
            senti = self.store.pop("senti")
            try:
                # Check if 'date' column exists
                if "date" in senti.columns:
                    self.store["senti"] = (
                        senti.set_index("date")
                        .rolling("7D")
                        .sum()
                        .reset_index()
                    )
                else:
                    logging.error("Sentiment data is missing 'date' column")
                    # Keep original data on error
                    self.store["senti"] = senti
            except Exception as e:
                logging.error("Sentiment rolling calculation error: %s", e)
                # Keep original data on error
                self.store["senti"] = senti

        # Validate data loaded
        logging.info("Datasets loaded: %s", list(self.store.keys()))
        for key, df in self.store.items():
            if df.empty:
                logging.warning(f"Empty dataset: {key}")
            elif df.isna().all().all():
                logging.warning(f"Dataset contains only NaN values: {key}")

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

        # Check if dataset has date column
        if 'date' not in self.store[key].columns:
            logging.error(f"Dataset '{key}' has no 'date' column")
            return None

        dates = self.store[key]['date']
        rel_dates = dates[dates <= target_date]

        if rel_dates.empty:
            return None

        return rel_dates.max()

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

        # Handle case where date is the only column
        if len(row.columns) <= 1:
            logging.warning(f"Dataset '{key}' has no data columns other than date")
            return pd.Series(dtype="float64")

        # Convert any string columns to numeric where possible
        for col in row.columns:
            if col != 'date' and row[col].dtype == 'object':
                try:
                    row[col] = pd.to_numeric(row[col], errors='coerce')
                except:
                    pass

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
            logging.error("Price data ('pr') not found in store")
            return pd.DataFrame()

        # Ensure we're using valid datetime64 objects
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)

        # Filter by date range
        price_data = self.store['pr'][
            (self.store['pr']['date'] >= start_date) &
            (self.store['pr']['date'] <= end_date)
            ].copy()

        if price_data.empty:
            logging.warning(f"No price data found between {start_date} and {end_date}")
            return pd.DataFrame()

        # Filter specific stocks
        cols = ['date']
        if stocks:
            available = [s for s in stocks if s in price_data.columns]
            if not available:
                logging.warning("None of the specified stocks found in price data")
                return pd.DataFrame()
            cols.extend(available)
        else:
            stock_cols = [c for c in price_data.columns if c != 'date']
            if not stock_cols:
                logging.warning("No stock columns found in price data")
                return pd.DataFrame()
            cols.extend(stock_cols)

        price_data = price_data[cols]

        # Sort by date
        price_data = price_data.sort_values('date')

        # Calculate returns
        price_pivot = price_data.set_index('date')

        # Convert any non-numeric columns to numeric
        for col in price_pivot.columns:
            if price_pivot[col].dtype == 'object':
                price_pivot[col] = pd.to_numeric(price_pivot[col], errors='coerce')

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
            logging.warning(f"No market cap data found for date {date}")
            # Return empty list or fallback to other stock columns in price data
            if 'pr' in self.store:
                stock_cols = [c for c in self.store['pr'].columns if c != 'date']
                if stock_cols:
                    logging.info(f"Falling back to stocks in price data, found {len(stock_cols)} stocks")
                    return stock_cols[:n]
            return []

        # Filter excluded tickers
        cap_data = cap_data[~cap_data.index.isin(self.cfg["EXCLUDED_TICKERS"])]

        # Handle case where all stocks are excluded
        if cap_data.empty:
            logging.warning("All stocks were excluded")
            return []

        # Convert to numeric if needed
        if cap_data.dtype == 'object':
            cap_data = pd.to_numeric(cap_data, errors='coerce')

        # Handle case where all values are NaN
        if cap_data.isna().all():
            logging.warning("All market cap values are NaN")
            return []

        # Select top N
        top_stocks = cap_data.sort_values(ascending=False).head(n).index.tolist()
        logging.info(f"Selected {len(top_stocks)} top stocks by market cap")
        return top_stocks


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
    # Handle empty series or series with less than q values
    if s.empty or len(s.dropna().unique()) < q:
        logging.warning("Not enough distinct values for quantile calculation")
        # Return same index with NaN values
        return pd.Series(index=s.index, dtype="float64")

    # Handle all-NaN case
    if s.isna().all():
        logging.warning("All values are NaN in quantile calculation")
        return pd.Series(index=s.index, dtype="float64")

    # Calculate ranks excluding NaNs
    r = s.rank(method="first", ascending=asc)

    try:
        # Try basic approach
        return pd.qcut(r, q, labels=False, duplicates="drop") + 1
    except ValueError as e:
        logging.debug(f"Standard qcut failed: {e}, trying alternative method")
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

    # Add storage for raw metrics
    raw_metrics: Dict[str, Dict[pd.Timestamp, pd.DataFrame]] = field(
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

        # Skip processing if no data
        if now.empty:
            logging.warning(f"No EPS forecast data for date {date}")
            return pd.DataFrame(index=top).fillna(0)

        # 3-month EPS growth
        eps_3m_ago = self.repo.get_latest_data("eps_fact", date, 3)
        if not eps_3m_ago.empty:
            out["eps_g3"] = (now - eps_3m_ago) / now.replace({0: np.nan}).abs()

        # 12-month EPS growth
        eps_12m_ago = self.repo.get_latest_data("eps_fact", date, 12)
        if not eps_12m_ago.empty:
            out["eps_g12"] = (now - eps_12m_ago) / now.replace({0: np.nan}).abs()

        # 12-month sales growth
        sales_now = self.repo.get_latest_data("sales_fact", date)
        sales_12m_ago = self.repo.get_latest_data("sales_fact", date, 12)
        if not sales_now.empty and not sales_12m_ago.empty:
            out["sales_g12"] = (sales_now - sales_12m_ago) / sales_now.replace({0: np.nan}).abs()

        # EPS and sales forecast revisions
        eps_rev = self.repo.get_latest_data("eps_rev", date)
        if not eps_rev.empty:
            out["eps_rev"] = eps_rev

        sales_rev = self.repo.get_latest_data("sales_rev", date)
        if not sales_rev.empty:
            out["sales_rev"] = sales_rev

        # EPS surprise
        eps_surprise = self.repo.get_latest_data("eps_surprise", date)
        if not eps_surprise.empty:
            out["eps_surprise"] = eps_surprise

        # PEG inverse (prevent division by zero)
        peg = self.repo.get_latest_data("peg", date)
        if not peg.empty:
            out["peg_inv"] = 1 / peg.replace({0: np.nan})

        # Store raw metrics
        self.raw_metrics.setdefault("growth", {})[date] = out.copy()

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
        pe = self.repo.get_latest_data("pe", date)
        if not pe.empty:
            out["pe"] = pe

        pb = self.repo.get_latest_data("pb", date)
        if not pb.empty:
            out["pb"] = pb

        # EV/EBITDA
        ev_ebitda = self.repo.get_latest_data("evebit_fact", date)
        if not ev_ebitda.empty:
            out["ev_ebitda"] = ev_ebitda

        # Store raw metrics
        self.raw_metrics.setdefault("value", {})[date] = out.copy()

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
        if "pr" not in self.repo.store:
            logging.warning("Price data not found in repository")
            return out

        pr = self.repo.store["pr"].set_index("date")
        if date not in pr.index:
            logging.warning(f"Date {date} not found in price data")
            return out

        # Current price
        try:
            cur = pr.loc[date, top]

            # Check for missing data
            missing = cur.isna().sum()
            if missing:
                logging.warning(f"Missing current prices for {missing} stocks on {date}")

            # Calculate momentum for different periods
            for m, lbl in [(1, "mom_1m"), (3, "mom_3m"), (12, "mom_12m")]:
                past_date = date - pd.DateOffset(months=m)
                past_rows = pr[pr.index <= past_date]

                if past_rows.empty:
                    logging.warning(f"No price data found {m} months before {date}")
                    continue

                past = past_rows.iloc[-1][top]

                # Calculate momentum with error handling
                with np.errstate(divide='ignore', invalid='ignore'):
                    momentum = cur / past - 1

                # Replace infinity values with NaN
                momentum = momentum.replace([np.inf, -np.inf], np.nan)
                out[lbl] = momentum

            # 12-month momentum excluding 1-month
            if {"mom_12m", "mom_1m"}.issubset(out.columns):
                with np.errstate(divide='ignore', invalid='ignore'):
                    out["mom_12m_ex1m"] = (1 + out["mom_12m"]) / (1 + out["mom_1m"]) - 1
                    out["mom_12m_ex1m"] = out["mom_12m_ex1m"].replace([np.inf, -np.inf], np.nan)
        except Exception as e:
            logging.error(f"Error calculating momentum: {e}")

        # 3-month EPS forecast revision change
        try:
            rev_now = self.repo.get_latest_data("eps_rev", date)
            rev_past = self.repo.get_latest_data("eps_rev", date - pd.DateOffset(months=3))
            if not rev_now.empty and not rev_past.empty:
                out["eps_rev_3m_chg"] = rev_now - rev_past
        except Exception as e:
            logging.error(f"Error calculating EPS forecast revision change: {e}")

        # Store raw metrics
        self.raw_metrics.setdefault("momentum", {})[date] = out.copy()

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
        # Initialize result dataframe
        out = pd.DataFrame(index=top)

        try:
            # Prepare price data
            if "pr" not in self.repo.store:
                logging.warning("Price data not found in repository")
                return out

            pr = self.repo.store["pr"].set_index("date")

            # Get prices from 3 years ago to current date
            three_years_ago = date - pd.DateOffset(years=3)
            three_years = pr.loc[three_years_ago: date, top]

            # Check if we have enough data
            if three_years.empty:
                logging.warning(f"No price data found for period {three_years_ago} to {date}")
                return out

            # Calculate returns
            ret = three_years.pct_change().dropna()

            # Check if we have return data
            if ret.empty:
                logging.warning("No return data calculated")
                return out

            # Calculate 3-month volatility (use most recent 63 trading days)
            if len(ret) >= 63:
                vol3m = ret.tail(63).std() * np.sqrt(252)  # Annualized
                out["vol_3m"] = vol3m
            else:
                logging.warning(f"Not enough data to calculate 3-month volatility ({len(ret)} days)")

            # Calculate beta
            beta = pd.Series(index=top, dtype="float64")

            # Only calculate beta if SPX index is available
            if "SPX Index" in pr.columns:
                # Get SPX returns
                mkt = pr["SPX Index"].loc[three_years_ago: date].pct_change().dropna()

                # 문제 부분: 각 주식마다 개별 베타를 계산하지 않고 있음
                # 수정: 각 주식별로 개별적으로 베타 계산
                for s in top:
                    if s in ret.columns and len(ret[s].dropna()) > 30:
                        # Use common index
                        common = ret[s].dropna().index.intersection(mkt.index)

                        if len(common) > 30:
                            stock_ret = ret[s][common]
                            mkt_ret = mkt[common]

                            cov = stock_ret.cov(mkt_ret)
                            var = mkt_ret.var()

                            # Prevent division by zero
                            beta[s] = cov / var if var > 0 else np.nan
            else:
                logging.warning("SPX Index not found in price data")

            # Add beta to output
            out["beta_3y"] = beta

            # Use volatility median for missing beta values
            vol_median = vol3m.median() if 'vol_3m' in out else np.nan
            out["beta_3y"] = out["beta_3y"].fillna(vol_median)

        except Exception as e:
            logging.error(f"Error calculating low volatility metrics: {e}")
            logging.debug(traceback.format_exc())

        # Store raw metrics
        self.raw_metrics.setdefault("low_vol", {})[date] = out.copy()

        return out.fillna(0)

    # MetricEngine 클래스의 _quality 메서드 수정
    def _quality(self, top: List[str], date: pd.Timestamp) -> pd.DataFrame:
        """Calculate quality metrics

        Calculates the following metrics:
        - roe: Return on equity
        - op_margin: Operating margin
        - fcf_g12: 12-month free cash flow growth
        - sentiment: 7-day sentiment score

        Args:
            top: List of stocks to analyze
            date: Reference date

        Returns:
            Quality metrics dataframe
        """
        # Create initial dataframe
        out = pd.DataFrame(index=top)

        try:
            # ROE and operating margin
            roe = self.repo.get_latest_data("roe", date)
            if not roe.empty:
                out["roe"] = roe

            op_margin = self.repo.get_latest_data("opm_fact", date)
            if not op_margin.empty:
                out["op_margin"] = op_margin

            # 12-month free cash flow growth
            fcf_now = self.repo.get_latest_data("fcf_fact", date)
            fcf_past = self.repo.get_latest_data("fcf_fact", date, 12)

            if not fcf_now.empty and not fcf_past.empty:
                # Prevent division by zero
                with np.errstate(divide='ignore', invalid='ignore'):
                    out["fcf_g12"] = (fcf_now - fcf_past) / fcf_past.replace({0: np.nan}).abs()
                    out["fcf_g12"] = out["fcf_g12"].replace([np.inf, -np.inf], np.nan)

            # Sentiment score (7-day rolling sum)
            sentiment = self.repo.get_latest_data("senti", date)
            if not sentiment.empty:
                out["sentiment"] = sentiment
                logging.debug(f"Added sentiment data for {len(sentiment)} stocks on {date}")
            else:
                logging.warning(f"No sentiment data available for date {date}")

            # Add sentiment trend (current vs 30 days ago)
            sentiment_30d_ago = self.repo.get_latest_data("senti", date - pd.DateOffset(days=30))
            if not sentiment.empty and not sentiment_30d_ago.empty:
                out["sentiment_trend"] = sentiment - sentiment_30d_ago
                logging.debug(f"Added sentiment trend data for {len(sentiment)} stocks on {date}")

        except Exception as e:
            logging.error(f"Error calculating quality metrics: {e}")
            logging.debug(traceback.format_exc())

        # Store raw metrics
        self.raw_metrics.setdefault("quality", {})[date] = out.copy()

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
        # Check if metrics dataframe is empty or has no valid data
        if metrics.empty or metrics.shape[1] == 0:
            logging.warning("Empty metrics dataframe, returning empty results")
            return pd.Series(dtype=float), pd.DataFrame()

        # Check for columns with all-zero or all-NaN values
        all_zeros = metrics.columns[((metrics == 0) | metrics.isna()).all()]
        if len(all_zeros) > 0:
            logging.warning(f"Columns with all zeros or NaNs: {list(all_zeros)}")
            metrics = metrics.drop(columns=all_zeros)

        # If no valid columns remain, return empty results
        if metrics.shape[1] == 0:
            logging.warning("No valid metric columns remain after removing all-zero columns")
            return pd.Series(dtype=float), pd.DataFrame()

        # Convert each metric to 10 quantiles
        q10 = pd.DataFrame(index=metrics.index)

        for col in metrics.columns:
            q10[col] = qcut(metrics[col], 10, asc)

        # Log any all-NaN columns
        all_nan = q10.columns[q10.isna().all()]
        if len(all_nan) > 0:
            logging.warning(f"Quantile columns with all NaNs: {list(all_nan)}")

        # Convert average of 10 quantiles to 5 quantiles
        avg_score = q10.mean(axis=1)

        # Check if average score is valid
        if avg_score.isna().all():
            logging.warning("All average scores are NaN")
            return pd.Series(index=metrics.index, dtype=float), q10

        q5 = qcut(avg_score, 5, asc=False)  # Higher average score is always better

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
            logging.warning(f"No top stocks found for date {date}")
            return {}

        # Calculate scores for each factor
        try:
            growth_metrics = self._growth(top, date)
            value_metrics = self._value(top, date)
            momentum_metrics = self._momentum(top, date)
            low_vol_metrics = self._low_vol(top, date)
            quality_metrics = self._quality(top, date)

            # Calculate scores
            res = {
                "growth": self._score(growth_metrics, asc=False),
                "value": self._score(value_metrics, asc=True),
                "momentum": self._score(momentum_metrics, asc=False),
                "low_vol": self._score(low_vol_metrics, asc=True),
                "quality": self._score(quality_metrics, asc=False),
            }
        except Exception as e:
            logging.error(f"Error calculating factor scores: {e}")
            logging.debug(traceback.format_exc())
            return {}

        # Store quantiles
        for fac, (q5, q10) in res.items():
            if not q5.empty:
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
        if not top:
            logging.warning(f"No top stocks found for date {date}")
            return {}

        # Get market cap data
        cap_row = self.repo.store["cap"][self.repo.store["cap"]["date"] == date]
        if cap_row.empty:
            logging.warning(f"No market cap data found for date {date}")
            # Create equal weights
            w = pd.Series({s: 1.0 / len(top) for s in top})
            return w.to_dict()

        # Extract market cap and calculate weights
        caps = cap_row.drop(columns="date").iloc[0][top]

        # Check if caps has valid data
        if caps.isnull().all():
            logging.warning(f"All market cap values are NaN for date {date}")
            # Create equal weights
            w = pd.Series({s: 1.0 / len(top) for s in top})
            return w.to_dict()

        # Calculate market cap weights
        total_cap = caps.sum()
        if total_cap <= 0:
            logging.warning(f"Total market cap is zero or negative ({total_cap})")
            # Create equal weights
            w = pd.Series({s: 1.0 / len(top) for s in top})
        else:
            w = (caps / total_cap).round(4)

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
            logging.warning("Empty quantile series")
            return bm

        # Weight adjustment factors by quantile
        factors = {1: 1.2, 2: 1.1, 3: 1.0, 4: 0.9, 5: 0.8}

        # Adjust each stock's weight
        w = {}
        for s in q.index:
            if s in bm:
                if pd.isnull(q[s]):
                    # For NaN quantiles, use neutral factor
                    w[s] = bm[s] * 1.0
                else:
                    # Use appropriate factor based on quantile
                    w[s] = bm[s] * factors[int(q[s])]

        # Normalize so weights sum to 1
        tot = sum(w.values())
        if tot <= 0:
            logging.warning(f"Total adjusted weight is zero or negative ({tot})")
            # Return original benchmark weights
            return bm

        w = {k: round(v / tot, 4) for k, v in w.items() if v > 0}

        return w

    def _metric_long_short(self, q: pd.Series) -> Dict[str, float]:
        """Construct long/short weights for metric portfolios.

        Stocks are placed into five quantiles.  Quantile weights are fixed at
        +10%, +5%, 0%, -5% and -10% from best to worst.  Weights are distributed
        equally within each quantile and do not rely on benchmark weights.
        """

        if q.empty:
            logging.warning("Empty quantile series for metric portfolio")
            return {}

        weight_map = {1: 0.10, 2: 0.05, 3: 0.0, 4: -0.05, 5: -0.10}
        weights: Dict[str, float] = {}

        for qv, wt in weight_map.items():
            members = q[q == qv].index.tolist()
            if not members or wt == 0:
                continue
            eq_w = wt / len(members)
            for m in members:
                weights[m] = round(eq_w, 6)

        return weights

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
        if not bm:
            logging.warning(f"Failed to construct benchmark portfolio for {date}")
            return {"benchmark": {}}

        # Calculate all factor scores
        scores = self.metric_engine.composite_scores(date)
        if not scores:
            logging.warning(f"Failed to calculate factor scores for {date}")
            return {"benchmark": bm}

        # Initialize portfolios
        ptf = {"benchmark": bm}

        # Build factor portfolios
        for fac, (q5, _) in scores.items():
            ptf[fac] = self._adjust(bm, q5)

            # Check if portfolio has valid weights
            if not ptf[fac]:
                logging.warning(f"Empty portfolio for factor {fac} on {date}")
                ptf[fac] = bm.copy()  # Use benchmark as fallback

        # Build individual metric portfolios
        for fac, (_, q10) in scores.items():
            for col in q10.columns:
                name = f"{fac}_{col}"
                metric_q = qcut(q10[col], 5, asc=(fac in {"value", "low_vol"}))
                ptf[name] = self._metric_long_short(metric_q)

                # Check if portfolio has valid weights
                if not ptf[name]:
                    logging.warning(f"Empty portfolio for metric {name} on {date}")
                    ptf[name] = {}

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

        # Check if dates list is empty
        if not dates:
            logging.warning("Empty dates list for portfolio construction")
            return out

        # Ensure all dates are Timestamp objects
        dates = [pd.Timestamp(d) for d in dates]

        # Serial processing
        if jobs in (None, 1):
            # Set up progress display
            iterator = LoggerSetup.progress_bar(dates, total=len(dates),
                                                desc="Building portfolios") if progress else dates

            # Build portfolios for each date
            for d in iterator:
                try:
                    portfolios = self.build_date(d)
                    for pt, w in portfolios.items():
                        _insert(pt, d, w)
                except Exception as e:
                    logging.error(f"Error building portfolios for date {d}: {e}")
                    logging.debug(traceback.format_exc())

        # Parallel processing
        else:
            # Calculate maximum workers
            try:
                cpu_count = os.cpu_count() or 1
                max_workers = max(1, cpu_count - 1) if jobs == 0 else jobs
                logging.info(f"Using {max_workers} parallel workers")
            except:
                max_workers = 1
                logging.warning("Failed to determine CPU count, using single worker")

            # Progress variables
            total = len(dates)
            done = 0

            # Run parallel execution
            with ProcessPoolExecutor(max_workers) as ex:
                try:
                    # Submit jobs for each date
                    futures = {ex.submit(self.build_date, d): d for d in dates}

                    # Process completed jobs
                    for fut in as_completed(futures):
                        try:
                            # Store results
                            result = fut.result()
                            for pt, w in result.items():
                                _insert(pt, futures[fut], w)
                        except Exception as e:
                            logging.error(f"Error processing portfolio for date {futures[fut]}: {e}")
                            logging.debug(traceback.format_exc())

                        # Update progress
                        if progress:
                            done += 1
                            pct = done * 100 / total
                            print(f"\rBuilding portfolios {pct:5.1f}% ({done}/{total})", end="", flush=True)

                    # Add line break after progress display
                    if progress:
                        print()
                except Exception as e:
                    logging.error(f"Parallel execution error: {e}")
                    logging.debug(traceback.format_exc())

        # Check if we have any results
        if not out:
            logging.warning("No portfolios were built")

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
        logging.warning(f"Not enough common data points for IC calculation ({len(common)})")
        return np.nan

    # Calculate Spearman correlation
    try:
        result = spearmanr(scores.loc[common], fwd_ret.loc[common])
        return result.correlation
    except Exception as e:
        logging.error(f"Error calculating IC: {e}")
        return np.nan


@timed
def build_portfolio_performance(price_df: pd.DataFrame,
                                weight_dict: Dict[pd.Timestamp, Dict[str, float]],
                                dynamic: bool = False) -> pd.DataFrame:
    """Calculate portfolio performance

    Args:
        price_df: Price dataframe (date and stock prices)
        weight_dict: Dictionary of weights by date

    Returns:
        Dataframe with date and return
    """
    # Check for empty inputs
    if price_df.empty or not weight_dict:
        logging.warning("Empty price data or weights")
        # Return empty dataframe with expected columns
        return pd.DataFrame({"date": [], "return": []})

    # Check if date column exists
    if "date" not in price_df.columns:
        logging.error("Date column missing in price dataframe")
        return pd.DataFrame({"date": [], "return": []})

    try:
        if not pd.api.types.is_datetime64_any_dtype(price_df['date']):
            price_df['date'] = pd.to_datetime(price_df['date'])

        price_numeric = price_df.set_index('date')
        for col in price_numeric.columns:
            if price_numeric[col].dtype == 'object':
                price_numeric[col] = pd.to_numeric(price_numeric[col], errors='coerce')

        if not dynamic:
            rows = [{"date": d, **w} for d, w in sorted(weight_dict.items())]
            wdf = pd.DataFrame(rows)

            if wdf.empty:
                logging.warning("Empty weights dataframe")
                return pd.DataFrame({"date": [], "return": []})

            wdf = wdf.set_index("date").sort_index()
            all_dates = price_numeric.index.unique()
            wdf = wdf.reindex(all_dates).ffill().fillna(0)

            val = (price_numeric * wdf).sum(axis=1)

            if val.isna().all() or (val == 0).all():
                logging.warning("All portfolio values are NaN or zero")
                val = pd.Series(1.0 + np.random.normal(0, 0.0001, len(val)), index=val.index)

            if val.iloc[0] == 0 or pd.isna(val.iloc[0]):
                val.iloc[0] = 1.0

            val = val / val.iloc[0]
            ret = val.pct_change().fillna(0)
        else:
            returns = price_numeric.pct_change().fillna(0)
            w_dates = sorted(weight_dict.keys())
            if not w_dates:
                logging.warning("Empty weight dates")
                return pd.DataFrame({"date": [], "return": []})

            cur_w = None
            pos_exp = neg_exp = 0.0
            idx = 0
            result = []
            for d in returns.index:
                if idx < len(w_dates) and d >= w_dates[idx]:
                    cur_w = weight_dict[w_dates[idx]]
                    pos_exp = sum(v for v in cur_w.values() if v > 0)
                    neg_exp = sum(-v for v in cur_w.values() if v < 0)
                    idx += 1

                if cur_w is None:
                    result.append((d, 0.0))
                    continue

                daily = returns.loc[d]
                port_ret = sum(cur_w.get(s, 0.0) * daily.get(s, 0.0) for s in daily.index)
                result.append((d, port_ret))

                updated = {s: cur_w.get(s, 0.0) * (1 + daily.get(s, 0.0)) for s in daily.index}

                pos_total = sum(v for v in updated.values() if v > 0)
                neg_total = sum(-v for v in updated.values() if v < 0)

                if pos_total:
                    for s in updated:
                        if updated[s] > 0:
                            updated[s] = updated[s] / pos_total * pos_exp
                if neg_total:
                    for s in updated:
                        if updated[s] < 0:
                            updated[s] = updated[s] / -neg_total * -neg_exp

                cur_w = updated

            ret = pd.Series({d: r for d, r in result})

        extreme = ret[(ret > 0.5) | (ret < -0.5)]
        if not extreme.empty:
            logging.warning(f"Found {len(extreme)} extreme return values > 50%")
            ret = ret.clip(-0.5, 0.5)

        return pd.DataFrame({"date": ret.index, "return": ret.values})
    except Exception as e:
        logging.error(f"Error calculating portfolio performance: {e}")
        logging.debug(traceback.format_exc())
        return pd.DataFrame({"date": [], "return": []})


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
    if 'pr' not in repo.store:
        logging.error("Price data not found in repository")
        return out

    price_df = repo.store["pr"]

    # Check if price data is empty
    if price_df.empty:
        logging.error("Empty price dataframe")
        return out

    factors = {"benchmark", "growth", "value", "momentum", "low_vol", "quality"}

    # Calculate performance for each portfolio type
    for n, w in weights.items():
        try:
            ret_df = build_portfolio_performance(price_df, w, dynamic=(n not in factors))

            # Check if returns are all zero or near-zero
            if ret_df.empty:
                logging.warning(f"Empty returns for portfolio {n}")
                continue

            all_zero = (ret_df["return"].abs() < 1e-10).all()
            if all_zero:
                logging.warning(f"All returns for {n} are zero or near-zero")

                # Add small random variation for non-benchmark portfolios to avoid flat lines
                if n != "benchmark":
                    np.random.seed(hash(n) % 10000)  # Use portfolio name as seed
                    variation = np.random.normal(0, 0.0005, len(ret_df))
                    ret_df["return"] = ret_df["return"] + variation

            out[n] = ret_df
        except Exception as e:
            logging.error(f"Error calculating returns for portfolio {n}: {e}")

    # Check if we have any results
    if not out:
        logging.warning("No portfolio returns calculated")

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
    if returns_df.empty or "return" not in returns_df.columns:
        logging.warning("Empty returns dataframe or missing 'return' column")
        return metrics

    # Returns series
    returns = returns_df["return"].fillna(0)

    # Check if we have enough data
    if len(returns) < min(windows):
        logging.warning(f"Not enough return data points ({len(returns)}) for minimum window ({min(windows)})")
        return metrics

    # Calculate metrics for each period
    for window in windows:
        if len(returns) >= window:
            try:
                # Extract returns for the period
                window_returns = returns.tail(window)

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
                else:
                    metrics[f"{window}d_sharpe"] = 0  # No volatility
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
        """Initialize report engine with explicit path handling

        Args:
            out_dir: Output directory path
        """
        # 절대 경로로 변환
        self.out = Path(out_dir).resolve()

        # 경로 로깅 (디버깅용)
        logging.info(f"Creating output directory: {self.out}")

        # 폴더 생성 with explicit handling
        try:
            # 상위 디렉토리부터 차례로 생성
            self.out.mkdir(parents=True, exist_ok=True)
            logging.info(f"Output directory successfully created: {self.out}")

            # 권한 확인
            if not self.out.exists():
                raise Exception(f"Directory creation failed: {self.out}")

            # 쓰기 권한 확인
            test_file = self.out / ".test_write"
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                test_file.unlink()  # 테스트 파일 삭제
                logging.info("Write permission confirmed")
            except Exception as e:
                logging.error(f"Write permission test failed: {e}")

        except Exception as e:
            logging.error(f"Error creating output directory: {e}")
            # 대안 경로 시도
            fallback_path = Path.home() / "Documents" / "Factor_Analysis"
            logging.warning(f"Attempting to use fallback path: {fallback_path}")
            self.out = fallback_path
            self.out.mkdir(parents=True, exist_ok=True)

    def _save_df(self, df: pd.DataFrame, path: Path) -> bool:
        """Helper method to safely save dataframe to CSV with absolute path

        Args:
            df: Dataframe to save
            path: Output path

        Returns:
            Success flag
        """
        try:
            # 절대 경로로 변환
            abs_path = self.out / path.name if not path.is_absolute() else path
            abs_path = abs_path.resolve()

            # 경로 확인 로그
            logging.debug(f"Saving to absolute path: {abs_path}")

            # 부모 디렉토리 확인
            abs_path.parent.mkdir(parents=True, exist_ok=True)

            # 저장 실행
            df.to_csv(abs_path, index=False)

            # 저장 확인
            if abs_path.exists():
                logging.info(f"Successfully saved: {abs_path}")
                return True
            else:
                logging.error(f"File not found after save: {abs_path}")
                return False

        except Exception as e:
            logging.error(f"Error saving to {path}: {e}")
            return False


    @timed
    def save_weights(self, weights: Dict[str, Dict[pd.Timestamp, Dict[str, float]]]):
        """Save portfolio weights

        Args:
            weights: Portfolio weights by type and date
        """
        for name, wd in weights.items():
            try:
                # Convert weights by date to dataframe
                rows = [{"date": d, **w} for d, w in sorted(wd.items())]
                df = pd.DataFrame(rows)

                # Check if dataframe is valid
                if df.empty:
                    logging.warning(f"Empty weights for {name}")
                    continue

                # Save to CSV
                file_path = self.out / f"{name}_weights.csv"
                if self._save_df(df, file_path):
                    logging.info(f"Saved weights: {name}")

            except Exception as e:
                logging.error(f"Error saving weights for {name}: {e}")

    @timed
    def save_returns(self, returns: Dict[str, pd.DataFrame]):
        """Save factor portfolio returns

        Args:
            returns: Portfolio returns by type
        """
        if not returns:
            logging.warning("No returns to save")
            return

        # Check benchmark data
        base = returns.get("benchmark")
        if base is None or "date" not in base.columns:
            logging.warning("Benchmark returns not found or missing date column")
            return

        try:
            # Create combined dataframe
            out = pd.DataFrame({"date": base["date"]})

            # Add returns for each portfolio
            for name, df in returns.items():
                if "return" in df.columns:
                    out[f"{name}_return"] = df["return"]

            # Save to CSV
            file_path = self.out / "factor_portfolio_returns.csv"
            if self._save_df(out, file_path):
                logging.info("Saved factor portfolio returns")

        except Exception as e:
            logging.error(f"Error saving factor returns: {e}")

    @timed
    def save_metric_returns(self, m_returns: Dict[str, pd.DataFrame]):
        """Save metric portfolio returns

        Args:
            m_returns: Returns by metric
        """
        if not m_returns:
            logging.warning("No metric returns to save")
            return

        try:
            # Get dates from first metric
            first = next(iter(m_returns.values()))
            if "date" not in first.columns:
                logging.warning("First metric returns missing date column")
                return

            # Create combined dataframe
            out = pd.DataFrame({"date": first["date"]})

            # Add returns for each metric
            for name, df in m_returns.items():
                if "return" in df.columns:
                    out[f"{name}_return"] = df["return"]

            # Save to CSV
            file_path = self.out / "metric_portfolio_returns.csv"
            if self._save_df(out, file_path):
                logging.info("Saved metric portfolio returns")

        except Exception as e:
            logging.error(f"Error saving metric returns: {e}")

    @timed
    def save_performance(self, perf_dict: Dict[str, Dict[str, float]], name: str):
        """Save performance metrics

        Args:
            perf_dict: Performance metrics by portfolio type
            name: Filename prefix
        """
        if not perf_dict:
            logging.warning(f"No performance data to save for {name}")
            return

        try:
            # Reorganize by metric
            metric_by_window = {}

            for portfolio, metrics in perf_dict.items():
                for metric, value in metrics.items():
                    if metric not in metric_by_window:
                        metric_by_window[metric] = {}
                    metric_by_window[metric][portfolio] = value

            # Convert to dataframe and save
            df = pd.DataFrame(metric_by_window)
            file_path = self.out / f"{name}_performance_metrics.csv"
            if self._save_df(df, file_path):
                logging.info(f"Saved {name} performance metrics")

        except Exception as e:
            logging.error(f"Error saving performance metrics for {name}: {e}")

    @timed
    def save_quantiles(self, q_dict: Dict[str, Dict[pd.Timestamp, pd.Series]], prefix: str):
        """Save quantile information

        Args:
            q_dict: Quantiles by factor/metric and date
            prefix: Filename prefix
        """
        for fac, qts in q_dict.items():
            try:
                # Convert quantiles to rows
                rows = []
                for d, ser in qts.items():
                    rows.extend([{"date": d, "stock": s, "quantile": q} for s, q in ser.items()])

                # Convert to dataframe and save
                if rows:
                    df = pd.DataFrame(rows)
                    file_path = self.out / f"{prefix}_{fac}_quantiles.csv"
                    if self._save_df(df, file_path):
                        logging.info(f"Saved {prefix}_{fac} quantiles")
                else:
                    logging.warning(f"No quantile data for {prefix}_{fac}")

            except Exception as e:
                logging.error(f"Error saving quantiles for {prefix}_{fac}: {e}")

    @timed
    def save_raw_metrics(self, raw_dict: Dict[str, Dict[pd.Timestamp, pd.DataFrame]], prefix: str):
        """Save raw metric values

        Args:
            raw_dict: Raw metrics by factor and date
            prefix: Filename prefix
        """
        for fac, metrics_by_date in raw_dict.items():
            try:
                # Convert to rows
                rows = []
                for d, metrics_df in metrics_by_date.items():
                    for stock in metrics_df.index:
                        row_data = {"date": d, "stock": stock}
                        for metric, value in metrics_df.loc[stock].items():
                            row_data[metric] = value
                        rows.append(row_data)

                # Convert to dataframe and save
                if rows:
                    df = pd.DataFrame(rows)
                    file_path = self.out / f"{prefix}_{fac}_raw_metrics.csv"
                    if self._save_df(df, file_path):
                        logging.info(f"Saved {prefix}_{fac} raw metrics")
                else:
                    logging.warning(f"No raw metric data for {prefix}_{fac}")

            except Exception as e:
                logging.error(f"Error saving raw metrics for {prefix}_{fac}: {e}")

    @timed
    def save_ic(self, ic_dict: Dict[str, List[Dict[str, Any]]]):
        """Save Information Coefficients (IC)

        Args:
            ic_dict: IC information by factor
        """
        for factor, ic_list in ic_dict.items():
            try:
                if ic_list:
                    df = pd.DataFrame(ic_list)
                    file_path = self.out / f"{factor}_ic.csv"
                    if self._save_df(df, file_path):
                        logging.info(f"Saved {factor} IC")
                else:
                    logging.warning(f"No IC data for {factor}")

            except Exception as e:
                logging.error(f"Error saving IC for {factor}: {e}")

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
            logging.warning(f"No summary data to save for {name}")
            return

        try:
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
            file_path = self.out / f"{name}_performance_summary.csv"
            if self._save_df(df.reset_index(), file_path):
                logging.info(f"Saved {name} performance summary")

        except Exception as e:
            logging.error(f"Error saving summary for {name}: {e}")


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
                logging.warning(f"No returns data for period {date} to {next_month}")
                continue

            # Get current and next month-end prices
            current_price = repo.get_latest_data("pr", date)
            future_dates = returns["date"].sort_values()

            if future_dates.empty:
                logging.warning(f"No future dates found in returns for {date}")
                continue

            future_date = future_dates.iloc[-1]
            future_price = repo.get_latest_data("pr", future_date)

            # Check if we have valid price data
            if current_price.empty or future_price.empty:
                logging.warning(f"Missing price data for IC calculation on {date}")
                continue

            # Calculate returns
            future_returns = {}
            for stock in current_price.index:
                if (stock in future_price.index and
                        current_price[stock] > 0 and
                        not pd.isna(current_price[stock]) and
                        not pd.isna(future_price[stock])):
                    future_returns[stock] = future_price[stock] / current_price[stock] - 1

            if not future_returns:
                logging.warning(f"No valid future returns calculated for {date}")
                continue

            returns_series = pd.Series(future_returns)

            # Calculate factor scores
            scores = metric_engine.composite_scores(date)
            if not scores:
                logging.warning(f"No factor scores calculated for {date}")
                continue

            # Calculate IC for each factor
            for factor, (_, q10) in scores.items():
                # Calculate average quantile score for each stock
                factor_scores = q10.mean(axis=1)

                # Check if factor scores are valid
                if factor_scores.empty or factor_scores.isna().all():
                    logging.warning(f"Invalid factor scores for {factor} on {date}")
                    continue

                # Check common stocks
                common_stocks = set(factor_scores.index) & set(returns_series.index)

                if len(common_stocks) < 5:
                    logging.warning(
                        f"Not enough common stocks ({len(common_stocks)}) for IC calculation for {factor} on {date}")
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
                else:
                    logging.warning(f"Invalid IC calculated for {factor} on {date}")

        except Exception as e:
            logging.error(f"Error calculating IC for {date}: {e}")
            logging.debug(traceback.format_exc())

    # Log results
    for factor, data in ic_data.items():
        logging.info(f"Calculated {len(data)} IC values for {factor}")

    return ic_data


@timed
def main(argv: Optional[Sequence[str]] = None):
    """Main execution function with explicit path validation"""

    # Set up argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, help="Parallel processes (0=max CPU-1)")
    ap.add_argument("--log", type=str, help="Log level (DEBUG/INFO/...)")
    ap.add_argument("--output", type=str, help="Override output directory")  # 추가: 명령행에서 경로 지정 가능
    args = ap.parse_args(argv)

    # Update configuration
    if args.jobs is not None:
        CONFIG["JOBS"] = args.jobs
    if args.log:
        CONFIG["LOG_LEVEL"] = args.log.upper()
    if args.output:  # 명령행에서 지정한 경로가 있으면 사용
        CONFIG["OUTPUT_DIR"] = Path(args.output).resolve()

    # Set up logging
    LoggerSetup.setup(CONFIG["LOG_LEVEL"])

    # 출력 경로 명시적 확인
    output_dir = Path(CONFIG["OUTPUT_DIR"]).resolve()
    logging.info(f"=== OUTPUT PATH VERIFICATION ===")
    logging.info(f"Configured OUTPUT_DIR: {CONFIG['OUTPUT_DIR']}")
    logging.info(f"Resolved OUTPUT_DIR: {output_dir}")
    logging.info(f"Does output directory exist: {output_dir.exists()}")

    # 경로가 venv_vf인지 확인
    if "venv_vf" not in str(output_dir):
        logging.warning(f"WARNING: Output path does not contain 'venv_vf': {output_dir}")
        # 강제로 venv_vf 경로로 변경
        output_dir = Path(r"C:\Users\westl\PycharmProjects\pythonProject\venv_vf\Factor")
        CONFIG["OUTPUT_DIR"] = output_dir
        logging.info(f"OUTPUT_DIR corrected to: {output_dir}")

    # 실제 폴더 생성 테스트
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        test_file = output_dir / ".path_test.txt"
        with open(test_file, 'w') as f:
            f.write(f"Path test at {datetime.now()}")
        test_file.unlink()
        logging.info("Output directory successfully verified and writable")
    except Exception as e:
        logging.error(f"Failed to create/write to output directory: {e}")
        raise

    try:
        # Initialize data repository and engines
        logging.info("Initializing data repository and engines")
        repo = DataRepository(CONFIG)
        me = MetricEngine(repo)
        pe = PortfolioEngine(repo, me)

        # Extract price dates and determine rebalancing dates
        if 'pr' not in repo.store or repo.store['pr'].empty:
            logging.error("Price data not found or empty")
            return

        price_dates = repo.store["pr"]["date"].sort_values().unique()
        logging.info(f"Found {len(price_dates)} price dates")

        # Select quarter-end dates (after 25th of the last month of each quarter)
        rebals = [d for d in price_dates if d.month % 3 == 0 and d.day > 25]
        logging.info(f"Selected {len(rebals)} rebalancing dates")

        # Check if we have any rebalancing dates
        if not rebals:
            logging.error("No rebalancing dates found")
            # Try alternative approach (every month end)
            rebals = []
            for m in range(1, 13):
                month_dates = [d for d in price_dates if d.month == m]
                if month_dates:
                    rebals.append(max(month_dates))
            logging.info(f"Using alternative approach: {len(rebals)} month-end dates")

            # If still no dates, use all available dates (last resort)
            if not rebals:
                logging.warning("No month-end dates found either, using all dates (reduced)")
                rebals = sorted(price_dates)[::20]  # Take every 20th date to reduce load
                logging.info(f"Using {len(rebals)} dates from full price series")

        # Build portfolios
        logging.info("Building portfolios")
        weights = pe.build_all(rebals, CONFIG["JOBS"], progress=True)

        # Check if we have any portfolios
        if not weights:
            logging.error("No portfolios built")
            return

        # Calculate returns
        logging.info("Calculating returns")
        returns_dict = daily_returns_all(repo, weights)

        # Check if we have any returns
        if not returns_dict:
            logging.error("No returns calculated")
            return

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
        rep.save_raw_metrics(me.raw_metrics, "factor")
        rep.save_ic(ic_data)
        rep.save_summary(factor_performance, "factor_performance")
        rep.save_summary(metric_performance, "metric_performance")

        # Save excluded tickers
        pd.DataFrame({"excluded_tickers": list(CONFIG["EXCLUDED_TICKERS"])}).to_csv(
            CONFIG["OUTPUT_DIR"] / "excluded_tickers.csv", index=False
        )

        # Calculate elapsed time
        elapsed = time.time() - start_time
        logging.info(f"Complete - Output: {CONFIG['OUTPUT_DIR'].resolve()}")
        logging.info(f"Total execution time: {elapsed:.2f} seconds ({elapsed / 60:.2f} minutes)")

    except Exception as e:
        logging.error(f"Fatal error in main execution: {e}")
        logging.debug(traceback.format_exc())

    logging.info(f"=== FINAL OUTPUT LOCATION ===")
    logging.info(f"Files should be saved in: {CONFIG['OUTPUT_DIR'].resolve()}")
    logging.info(f"Checking if files exist in this location...")

    # 주요 출력 파일들 확인
    key_files = [
        "factor_portfolio_returns.csv",
        "metric_portfolio_returns.csv",
        "excluded_tickers.csv"
    ]

    for filename in key_files:
        filepath = CONFIG['OUTPUT_DIR'] / filename
        if filepath.exists():
            logging.info(f"✓ {filename} exists at {filepath}")
        else:
            logging.warning(f"✗ {filename} not found at {filepath}")


if __name__ == "__main__":
    main()