"""Rebuild invest/data.json for the rates-vs-stocks page.

Sources (no API keys needed):
  - Robert Shiller's monthly S&P 500 data (GitHub datasets mirror) for 1976 up to SPY's launch
  - Yahoo Finance monthly adjusted closes (dividends reinvested) for SPY, QQQ and SCHD
  - FRED: GS10 (10-year Treasury, monthly), DGS10 (latest daily), FEDFUNDS (monthly),
    CPIAUCSL (CPI, turned into year-over-year inflation), WTISPLC + DCOILWTICO (WTI crude),
    VIXCLS (daily VIX, averaged per month)

If one source fails, that series keeps its values from the previous data.json so the page never breaks.
Standard library only, so the GitHub Action needs no pip install.
"""
import csv
import io
import json
import sys
import time
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

OUT = Path(__file__).with_name("data.json")
START = "1975-12"
UA = {"User-Agent": "Mozilla/5.0 (rates-vs-stocks page updater)"}


def get(url, tries=4):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001 - retry any network error
            print(f"  retry {k + 1}/{tries} {url}: {e}", file=sys.stderr)
            time.sleep(2 ** (k + 1))
    raise RuntimeError(f"failed: {url}")


def yahoo_monthly(symbol):
    """[(YYYY-MM-DD, adjclose)] on the last trading day of each month; the running month ends at the latest close."""
    now = int(time.time())
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?period1=0&period2={now}&interval=1d&includeAdjustedClose=true")
    res = json.loads(get(url))["chart"]["result"][0]
    tz = res["meta"].get("gmtoffset", -14400)
    ts = res["timestamp"]
    adj = res["indicators"]["adjclose"][0]["adjclose"]
    days = [datetime.fromtimestamp(t + tz, tz=timezone.utc).date() for t in ts]  # exchange-local dates
    gaps = sorted(b.toordinal() - a.toordinal() for a, b in zip(days, days[1:]))
    monthly_bars = bool(gaps) and gaps[len(gaps) // 2] > 20
    last_trade = datetime.fromtimestamp(res["meta"]["regularMarketTime"] + tz, tz=timezone.utc).date()
    rows = {}
    for d, v in zip(days, adj):
        if v is None:
            continue
        key = d.strftime("%Y-%m")
        if monthly_bars:
            # Yahoo sometimes answers long daily requests with monthly bars stamped at the month start;
            # each bar's close is the month-end close.
            if key == last_trade.strftime("%Y-%m"):
                d = last_trade
            else:
                nxt = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
                d = date.fromordinal(nxt.toordinal() - 1)
        rows[key] = (d.isoformat(), v)  # later rows in the month overwrite earlier ones
    print(f"  {symbol}: {'monthly' if monthly_bars else 'daily'} bars, {len(ts)} rows")
    return [rows[k] for k in sorted(rows)]


def fred(series, since="1953-01-01"):
    text = get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={since}")
    out = []
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 2 or not row[0][:1].isdigit() or row[1] in (".", ""):
            continue
        out.append((row[0], float(row[1])))
    return out


def shiller():
    text = get("https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv")
    return [
        (r["Date"][:7], float(r["SP500"]), float(r["Dividend"]))
        for r in csv.DictReader(io.StringIO(text))
    ]


def build_spx():
    """Total-return index: Shiller monthly averages + dividends until SPY exists, then SPY adjusted closes."""
    sh = [r for r in shiller() if r[0] >= START]
    spy = yahoo_monthly("SPY")
    spy_start = spy[0][0][:7]
    out, tr, last = [], 1.0, None
    for ym, p, d in sh:
        if last:
            lp, ld = last
            tr *= p / lp + (ld / lp if ld > 0 else 0.0) / 12
        if ym == spy_start:
            # SPY's first month-end takes over from here.
            out.append([spy[0][0], round(tr, 6)])
            break
        out.append([f"{ym}-15", round(tr, 6)])
        last = (p, d)
    for (_, v0), (d1, v1) in zip(spy, spy[1:]):
        tr *= v1 / v0
        out.append([d1, round(tr, 6)])
    return out


def build_etf(symbol):
    rows = yahoo_monthly(symbol)
    base = rows[0][1]
    return [[d, round(v / base, 6)] for d, v in rows]


def bond_price(coupon, yld, years):
    if yld <= 0:
        yld = 1e-6
    i, n = yld / 2, 2 * years
    return coupon / yld * (1 - (1 + i) ** -n) + (1 + i) ** -n


def build_rates():
    """10-year yield (monthly GS10 + latest daily DGS10) and the synthetic constant-maturity bond it implies."""
    gs10 = [(d[:7] + "-15", v) for d, v in fred("GS10") if d[:7] >= START]
    daily = fred("DGS10", since=f"{date.today().year - 1}-01-01")
    pts = list(gs10)
    if daily and daily[-1][0] > pts[-1][0]:
        pts.append(daily[-1])
    out, tr, px, prev = [], 1.0, 1.0, None
    for d, y in pts:
        if prev:
            pd, py = prev
            dt = (date.fromisoformat(d).toordinal() - date.fromisoformat(pd).toordinal()) / 365.25
            p = bond_price(py / 100, y / 100, 10 - dt)
            tr *= p + py / 100 * dt
            px *= p
        out.append([d, y, round(tr, 6), round(px, 6)])
        prev = (d, y)
    return out


def build_fed():
    return [[d[:7] + "-15", v] for d, v in fred("FEDFUNDS") if d[:7] >= START]


def build_cpi():
    """Year-over-year CPI inflation in %."""
    cpi = fred("CPIAUCSL", since="1974-01-01")
    by_month = {d[:7]: v for d, v in cpi}
    out = []
    for d, v in cpi:
        prev = by_month.get(f"{int(d[:4]) - 1}{d[4:7]}")
        if prev and d[:7] >= START:
            out.append([d[:7] + "-15", round((v / prev - 1) * 100, 2)])
    return out


def build_oil():
    """WTI crude, $/barrel: monthly averages plus the latest daily price."""
    out = [[d[:7] + "-15", v] for d, v in fred("WTISPLC") if d[:7] >= START]
    daily = fred("DCOILWTICO", since=f"{date.today().year - 1}-01-01")
    if daily and daily[-1][0] > out[-1][0]:
        out.append([daily[-1][0], daily[-1][1]])
    return out


def build_vix():
    """VIX monthly average (daily closes); the running month is dated at its latest close."""
    daily = fred("VIXCLS", since="1990-01-01")
    months = {}
    for d, v in daily:
        months.setdefault(d[:7], []).append((d, v))
    last = daily[-1][0][:7]
    out = []
    for ym in sorted(months):
        vals = months[ym]
        label = vals[-1][0] if ym == last else ym + "-15"
        out.append([label, round(sum(v for _, v in vals) / len(vals), 2)])
    return out


def main():
    prev = json.loads(OUT.read_text()) if OUT.exists() else {}
    data = {"freq": dict(prev.get("freq", {}))}
    failures = []
    sources = [
        ("spx", build_spx),
        ("qqq", lambda: build_etf("QQQ")),
        ("schd", lambda: build_etf("SCHD")),
        ("bond", build_rates),
        ("fed", build_fed),
        ("cpi", build_cpi),
        ("oil", build_oil),
        ("vix", build_vix),
    ]
    for key, fn in sources:
        try:
            data[key] = fn()
            data["freq"][key] = "M"
            print(f"{key}: {len(data[key])} rows, last {data[key][-1]}")
        except Exception as e:  # noqa: BLE001 - keep the old series instead of failing the page
            failures.append(key)
            print(f"{key}: FAILED ({e}); keeping previous values", file=sys.stderr)
            if key in prev:
                data[key] = prev[key]
    if len(failures) == len(sources):
        sys.exit("every source failed; leaving data.json untouched")
    data["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    data["stale"] = failures
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
