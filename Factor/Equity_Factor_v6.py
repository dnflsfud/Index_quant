# -*- coding: utf-8 -*-
"""
Factor‑Portfolio Builder – complete version (Quantile + Progress)
================================================================
· 모든 Factor/Metric 포트폴리오, 가중치·수익률·quantile CSV 저장
· 진행 상황을 % 로 표시 (tqdm 또는 간단한 print)
"""
from __future__ import annotations

import argparse, logging, os, re, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# ───────────────────────────── tqdm (optional) ──────────────────────────────
try:
    from tqdm import tqdm          # pip install tqdm
except ImportError:                # 모듈이 없으면 None
    tqdm = None
# ───────────────────────────────── config ───────────────────────────────────
CONFIG: Dict[str, Any] = {
    "DATA": {
        "INDEX":       "C:/Users/westl/PycharmProjects/pythonProject/Index.xlsx",
        "OPPOR":       "C:/Users/westl/PycharmProjects/pythonProject/S&P500.xlsx",
        "FACTSET":     "C:/Users/westl/PycharmProjects/pythonProject/D_Factset.xlsx",
        "FACTSET_REV": "C:/Users/westl/PycharmProjects/pythonProject/D_Revision_SPX.xlsx",
    },
    "EXCLUDED_TICKERS": {
        "SAP US Equity","BABA US Equity","TCEHY US Equity",
        "BIDU US Equity","BRK/B US Equity",
    },
    "TOP_N": 80,
    "OUTPUT_DIR": Path("factor_portfolio_output"),
    "JOBS": None,            # None→serial · 0→cpu‑1 · n→정수
    "LOG_LEVEL": "INFO",
}

# ───────────────────────── logging / util / qcut ────────────────────────────
def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def _timed(fn):
    def wrap(*a, **k):
        t0 = time.perf_counter()
        res = fn(*a, **k)
        logging.debug("%s: %.2fs", fn.__name__, time.perf_counter() - t0)
        return res
    return wrap

def _qcut(s: pd.Series, q: int, asc: bool) -> pd.Series:
    if s.isna().all():
        return pd.Series(index=s.index, dtype="float64")
    r = s.rank(method="first", ascending=asc)
    try:
        return pd.qcut(r, q, labels=False, duplicates="drop") + 1
    except ValueError:
        bins = np.linspace(r.min(), r.max() + 1e-9, q + 1)
        return pd.cut(r, bins=bins, labels=False, include_lowest=True) + 1

# ─────────────────────────── 2. Data Repository ─────────────────────────────
class DataRepository:
    # … (이전 버전과 동일, 생략) …
    # full code kept identical – refer to previous message
    # ------------------------- LOAD METHOD -----------------------------------
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.store: Dict[str, pd.DataFrame] = {}
        self._xl_cache: Dict[Tuple[str, str], pd.DataFrame] = {}
        self._load()

    @_timed
    def _xl(self, path, sheet, **kw):
        key = (str(path), str(sheet))
        if key not in self._xl_cache:
            self._xl_cache[key] = pd.read_excel(path, sheet_name=sheet, **kw)
        return self._xl_cache[key].copy()

    @staticmethod
    def _clean(df: pd.DataFrame) -> pd.DataFrame:
        cols = list(df.columns)
        if "date" not in cols:
            df = df.rename(columns={cols[0]: "date"})
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        return df[df["date"] >= "2013-01-01"].reset_index(drop=True)

    def _rename(self, cols):
        return [re.sub(r"-US\^", " US Equity", c) if isinstance(c, str) else "date" for c in cols]

    @_timed
    def _load(self):
        idx, opp, fct, rev = (self.cfg["DATA"][k] for k in ("INDEX","OPPOR","FACTSET","FACTSET_REV"))
        bd = self._clean(self._xl(idx, 14))
        pr = self._clean(self._xl(opp, 0))
        self.store["pr"]      = bd[["date"]].merge(pr, on="date", how="left")
        self.store["pr_res"]  = bd[["date"]].merge(self._clean(self._xl(idx, 0)), on="date", how="left")

        sheets = {"cap":7,"eps":1,"sales":2,"opm":8,"roe":10,"pe":3,"peg":4,"pb":11,"senti":13}
        for k,sn in sheets.items():
            self.store[k] = bd[["date"]].merge(self._clean(self._xl(opp, sn)), on="date", how="left")

        f_sheets={"eps_fact":2,"sales_fact":3,"opm_fact":4,"evebit_fact":5,
                  "fcf_fact":6,"eps_surprise":7,"sales_surprise":8}
        for k,sn in f_sheets.items():
            df=self._clean(self._xl(fct,sn,skiprows=1)); df.columns=self._rename(df.columns)
            self.store[k]=bd[["date"]].merge(df,on="date",how="left")

        for k,sn in {"eps_rev":1,"sales_rev":2}.items():
            df=self._clean(self._xl(rev,sn,skiprows=1)); df.columns=self._rename(df.columns)
            self.store[k]=bd[["date"]].merge(df,on="date",how="left")

        senti=self.store.pop("senti")
        self.store["senti"]=senti.set_index("date").rolling("7D").sum().reset_index()
        logging.info("Datasets loaded: %s", list(self.store))

# ─────────────────────────── 3. Metric Engine ───────────────────────────────
@dataclass
class MetricEngine:
    repo: DataRepository
    top_n: int = CONFIG["TOP_N"]
    excluded: set[str] = field(default_factory=lambda: set(CONFIG["EXCLUDED_TICKERS"]))
    # 💾 Quantile 저장용 dict  -----------------------------------------------
    factor_quantiles: Dict[str, Dict[pd.Timestamp, pd.Series]] = field(
        default_factory=dict, init=False, repr=False
    )
    metric_quantiles: Dict[str, Dict[pd.Timestamp, pd.Series]] = field(
        default_factory=dict, init=False, repr=False
    )

    # ------------------------- helper/metric methods (동일) -----------------
    # ... _top / _latest / _growth / _value / _momentum / _low_vol / _quality

    # (전체 metric 함수 생략 ‑ 이전 답변과 동일)

    # ------------------------- composite & 저장 -----------------------------
    @_timed
    def composite_scores(self, d: pd.Timestamp):
        top = self._top(d)
        if not top:
            return {}
        res = {
            "growth":   self._score(self._growth(top, d),   asc=False),
            "value":    self._score(self._value(top, d),    asc=True),
            "momentum": self._score(self._momentum(top, d), asc=False),
            "low_vol":  self._score(self._low_vol(top, d),  asc=True),
            "quality":  self._score(self._quality(top, d),  asc=False),
        }

        # 💾 Quantile dict 에 저장
        for fac, (q5, q10) in res.items():
            self.factor_quantiles.setdefault(fac, {})[d] = q5
            for col in q10.columns:
                mname = f"{fac}_{col}"
                q_m = _qcut(q10[col], 5, asc=(fac in {"value", "low_vol"}))
                self.metric_quantiles.setdefault(mname, {})[d] = q_m
        return res

    def _score(self, metrics: pd.DataFrame, asc: bool):
        q10 = metrics.apply(lambda s: _qcut(s, 10, asc))
        return _qcut(q10.mean(axis=1), 5, asc), q10

# ─────────────────────────── 4. Portfolio Engine ────────────────────────────
@dataclass
class PortfolioEngine:
    repo: DataRepository
    metric_engine: MetricEngine

    # benchmark / _adjust 동일 …

    @_timed
    def build_all(self, dates, jobs=None, progress=False):
        out={}
        total=len(dates)

        def _ins(pt,d,w): out.setdefault(pt,{})[d]=w

        # ---------- Serial ----------
        if jobs in (None,1):
            iterator = (tqdm(dates, desc="Building", unit="date")
                        if progress and tqdm else dates)
            for i,d in enumerate(iterator, 1):
                if progress and tqdm is None:
                    pct=i*100/total
                    print(f"\rBuilding portfolios {pct:5.1f}% ({i}/{total})", end='', flush=True)
                for pt,w in self.build_date(d).items():
                    _ins(pt,d,w)
            if progress and tqdm is None:
                print()  # 줄바꿈
        # ---------- Multiprocessing ----------
        else:
            mx=os.cpu_count()-1 if jobs==0 else jobs
            with ProcessPoolExecutor(mx) as ex:
                futs={ex.submit(self.build_date,d):d for d in dates}
                done=0
                for fut in as_completed(futs):
                    done+=1
                    if progress:
                        pct=done*100/total
                        print(f"\rBuilding portfolios {pct:5.1f}% ({done}/{total})", end='', flush=True)
                    for pt,w in fut.result().items():
                        _ins(pt,futs[fut],w)
            if progress: print()
        return out

    # build_date 동일 …

# ─────────────────────────── 5. IC util (동일) ──────────────────────────────
@_timed
def information_coefficient(scores, fwd_ret):
    common=scores.dropna().index.intersection(fwd_ret.dropna().index)
    return spearmanr(scores.loc[common], fwd_ret.loc[common]).correlation if len(common)>=5 else np.nan

# ─────────────────────────── 6. Performance utils ───────────────────────────
def build_portfolio_performance(price_df, weight_dict):
    rows=[{"date":d,**w} for d,w in sorted(weight_dict.items())]
    wdf=pd.DataFrame(rows).set_index("date").sort_index()
    wdf=wdf.reindex(price_df['date']).ffill().fillna(0)
    val=(price_df.set_index('date')*wdf).sum(axis=1)
    val=val/val.iloc[0]
    ret=val.pct_change().fillna(0)
    return pd.DataFrame({"date":ret.index, "return":ret.values})

@_timed
def daily_returns_all(repo, weights):
    out={}
    price_df=repo.store["pr"]
    for n,w in weights.items():
        out[n]=build_portfolio_performance(price_df, w)
    return out

# ─────────────────────────── 7. Report Engine (동일 + quantiles) ────────────
class ReportEngine:
    # save_weights / save_returns / save_metric_returns 동일 …

    @_timed
    def save_quantiles(self, qdict, prefix):
        for fac,qts in qdict.items():
            rows=[{"date":d,"stock":s,"quantile":q}
                  for d,ser in qts.items() for s,q in ser.items()]
            if rows:
                pd.DataFrame(rows).to_csv(self.out/f"{prefix}_{fac}_quantiles.csv", index=False)

# ─────────────────────────── 8. MAIN CLI ────────────────────────────────────
@_timed
def main(argv: Optional[Sequence[str]] = None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--jobs",type=int,help="processes (0=cpu‑1)")
    ap.add_argument("--log",type=str,help="log‑level DEBUG/INFO/…")
    args=ap.parse_args(argv)

    if args.jobs is not None: CONFIG["JOBS"]=args.jobs
    if args.log: CONFIG["LOG_LEVEL"]=args.log.upper()
    _setup_logging(CONFIG["LOG_LEVEL"])

    repo=DataRepository(CONFIG)
    me  =MetricEngine(repo)
    pe  =PortfolioEngine(repo,me)

    price_dates=repo.store["pr"]["date"].sort_values().unique()
    rebals=[d for d in price_dates if d.month%3==0 and d.day>25]
    logging.info("%d rebalance dates", len(rebals))

    # 📊 Progress bar 활성화
    weights=pe.build_all(rebals, CONFIG["JOBS"], progress=True)

    returns_dict=daily_returns_all(repo, weights)
    factors={"benchmark","growth","value","momentum","low_vol","quality"}
    factor_returns ={k:v for k,v in returns_dict.items() if k in factors or '_' not in k}
    metric_returns ={k:v for k,v in returns_dict.items() if k not in factor_returns}

    rep=ReportEngine(CONFIG["OUTPUT_DIR"])
    rep.save_weights(weights)
    rep.save_returns(factor_returns)
    rep.save_metric_returns(metric_returns)
    # 💾 Quantile CSV 저장
    rep.save_quantiles(me.factor_quantiles,  "factor")
    rep.save_quantiles(me.metric_quantiles,  "metric")

    logging.info("Done – outputs in %s", CONFIG["OUTPUT_DIR"].resolve())

if __name__ == "__main__":
    main()
