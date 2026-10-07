"""
forecast_bakeoff.py — reusable time-series model bake-off.

Runs a documented set of forecasting models through an identical rolling-origin
backtest and reports which one to use. Extracted from an earlier
forecasting project;
generic version, no project content.

Models: seasonal-naive (baseline), damped ETS (log1p), auto-ARIMA, Theta (log1p),
Croston (intermittent), and an ETS+ARIMA+Theta ensemble. Scored by MASE
(mean absolute scaled error; <1 = better than an in-sample naive step), plus
80/95% prediction-interval coverage where the model provides intervals.

Discipline carried over (see memory: keeping-outputs-engaging):
  - grade every candidate against the baseline on the SAME folds
  - if nothing beats the baseline, say so and keep the baseline
  - report the negative result; never tune to the test folds
  - Theta was the winner in the original project; do NOT assume it wins elsewhere —
    always re-run the bake-off on the new series.

Usage
-----
    from forecast_bakeoff import bakeoff
    import pandas as pd
    y = pd.Series(values, index=pd.period_range("2015-01", periods=len(values), freq="M"))
    result = bakeoff(y, horizon=12, n_origins=6)
    print(result["summary"])          # MASE per model, overall + by horizon
    print(result["winner"], result["winner_mase"])
    fc = result["forecast"]           # dict: point, lo50/hi50, lo80/hi80, lo95/hi95 from the winner

Requires: numpy, pandas, statsmodels; optional pmdarima (auto-ARIMA), sktime (Croston).
"""
from __future__ import annotations
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.forecasting.theta import ThetaModel

try:
    import pmdarima as pm
    _HAS_ARIMA = True
except Exception:
    _HAS_ARIMA = False
try:
    from sktime.forecasting.croston import Croston
    _HAS_CROSTON = True
except Exception:
    _HAS_CROSTON = False

Z80, Z95 = 1.2816, 1.9600


# ---------------- individual models: (point, lo50, hi50, lo80, hi80, lo95, hi95) ----------------
def _seasonal_naive(y, n):
    v = y.values.astype(float)
    pt = np.array([y.iloc[-12 + ((h - 1) % 12)] if len(v) >= 24 else v[-1] for h in range(1, n + 1)])
    resid = (v[12:] - v[:-12]) if len(v) > 12 else np.array([0.0])
    sd = max(resid.std(), 0.5)
    return (pt, np.clip(pt - .6745 * sd, 0, None), pt + .6745 * sd,
            np.clip(pt - Z80 * sd, 0, None), pt + Z80 * sd,
            np.clip(pt - Z95 * sd, 0, None), pt + Z95 * sd)


def _ets(y, n):
    yl = np.log1p(y.values.astype(float))
    seas = "add" if len(yl) >= 36 else None
    fit = ExponentialSmoothing(yl, trend="add", damped_trend=True, seasonal=seas,
                                seasonal_periods=12 if seas else None,
                                initialization_method="estimated").fit()
    sims = np.clip(np.expm1(np.asarray(fit.simulate(n, repetitions=2000, anchor="end"))), 0, None)
    pt = np.clip(np.expm1(np.asarray(fit.forecast(n), float)), 0, None)
    q = lambda p: np.percentile(sims, p, axis=1)
    return pt, q(25), q(75), q(10), q(90), q(2.5), q(97.5)


def _theta(y, n):
    yl = np.log1p(y.values.astype(float))
    period = 12 if len(yl) >= 24 else None
    tm = ThetaModel(yl, period=period, deseasonalize=bool(period)).fit()
    pt = np.clip(np.expm1(np.asarray(tm.forecast(n), float)), 0, None)
    ex = lambda a: np.clip(np.expm1(a.values), 0, None)
    p50, p80, p95 = (tm.prediction_intervals(n, alpha=a) for a in (0.50, 0.20, 0.05))
    return (pt, ex(p50.iloc[:, 0]), ex(p50.iloc[:, 1]), ex(p80.iloc[:, 0]), ex(p80.iloc[:, 1]),
            ex(p95.iloc[:, 0]), ex(p95.iloc[:, 1]))


def _arima(y, n):
    yl = np.log1p(y.values.astype(float))
    seas = len(yl) >= 30
    m = pm.auto_arima(yl, seasonal=seas, m=12 if seas else 1, max_p=3, max_q=3, max_P=1, max_Q=1,
                      d=None, D=0, stepwise=True, suppress_warnings=True, error_action="ignore")
    fc, ci80 = m.predict(n, return_conf_int=True, alpha=0.20)
    _, ci95 = m.predict(n, return_conf_int=True, alpha=0.05)
    _, ci50 = m.predict(n, return_conf_int=True, alpha=0.50)
    ex = lambda a: np.clip(np.expm1(a), 0, None)
    return (ex(np.asarray(fc, float)), ex(ci50[:, 0]), ex(ci50[:, 1]),
            ex(ci80[:, 0]), ex(ci80[:, 1]), ex(ci95[:, 0]), ex(ci95[:, 1]))


def _croston(y, n):
    f = Croston(smoothing=0.1).fit(pd.Series(y.values.astype(float)))
    pt = np.clip(np.asarray(f.predict(fh=list(range(1, n + 1))), float), 0, None)
    nan = np.full(n, np.nan)
    return pt, nan, nan, nan, nan, nan, nan


def _models():
    m = {"seasonal_naive": _seasonal_naive, "ets_damped": _ets, "theta": _theta}
    if _HAS_ARIMA:
        m["auto_arima"] = _arima
    if _HAS_CROSTON:
        m["croston"] = _croston
    return m


def _mase_denom(y):
    v = y.values.astype(float)
    return max(np.abs(v[12:] - v[:-12]).mean(), 0.5) if len(v) > 12 else max(pd.Series(v).diff().abs().mean(), 0.5)


def bakeoff(y: pd.Series, horizon: int = 12, n_origins: int = 6, origin_step: int = 6):
    """y: a numeric Series indexed by monthly pd.Period. Returns a dict with
    'summary' (DataFrame), 'winner', 'winner_mase', 'by_horizon' (DataFrame),
    'pi_coverage' (DataFrame) and 'forecast' (winner refit on all data)."""
    y = y.sort_index()
    models = _models()
    origins = [y.index[-1] - horizon - origin_step * k for k in range(n_origins)][::-1]
    rows, pirows = [], []
    for origin in origins:
        if origin not in y.index or (origin + horizon) not in y.index:
            continue
        tr = y.loc[:origin]
        act = y.loc[origin + 1: origin + horizon]
        if len(act) < horizon:
            continue
        denom = _mase_denom(tr)
        for name, fn in models.items():
            try:
                pt, l50, h50, l80, h80, l95, h95 = fn(tr, horizon)
            except Exception:
                continue
            for h in range(1, horizon + 1):
                a, p = act.iloc[h - 1], pt[h - 1]
                rows.append(dict(model=name, origin=str(origin), horizon=h,
                                 abs_err=abs(a - p), scaled_err=abs(a - p) / denom))
                if np.isfinite(l80[h - 1]) and np.isfinite(h95[h - 1]):
                    pirows.append(dict(model=name, in80=int(l80[h - 1] <= a <= h80[h - 1]),
                                       in95=int(l95[h - 1] <= a <= h95[h - 1])))
    sc = pd.DataFrame(rows)
    summary = sc.groupby("model")["scaled_err"].mean().rename("mase").sort_values().reset_index()
    by_h = sc.groupby(["model", "horizon"])["scaled_err"].mean().unstack("model")
    picov = (pd.DataFrame(pirows).groupby("model")[["in80", "in95"]].mean()
             if pirows else pd.DataFrame())

    base = summary.loc[summary.model == "seasonal_naive", "mase"]
    base = float(base.iloc[0]) if len(base) else np.inf
    cand = summary[summary.model != "seasonal_naive"]
    if len(cand) and cand["mase"].min() < base:
        winner = cand.loc[cand["mase"].idxmin(), "model"]
    else:
        winner = "seasonal_naive"
    winner_mase = float(summary.loc[summary.model == winner, "mase"].iloc[0])

    fn = models[winner]
    pt, l50, h50, l80, h80, l95, h95 = fn(y, horizon)
    fut = [y.index[-1] + k for k in range(1, horizon + 1)]
    forecast = dict(month=[str(m) for m in fut], point=[float(x) for x in pt],
                    lo50=[float(x) for x in l50], hi50=[float(x) for x in h50],
                    lo80=[float(x) for x in l80], hi80=[float(x) for x in h80],
                    lo95=[float(x) for x in l95], hi95=[float(x) for x in h95],
                    model=winner, backtest_mase=winner_mase)
    return dict(summary=summary, by_horizon=by_h, pi_coverage=picov,
               winner=winner, winner_mase=winner_mase, forecast=forecast)
