"""Rebuild invest/data.json for the rates-vs-stocks page.

Sources (no API keys needed):
  - Robert Shiller's monthly S&P 500 data (GitHub datasets mirror) for 1976 up to SPY's launch
  - Yahoo Finance monthly adjusted closes (dividends reinvested) for SPY, QQQ and SCHD
  - FRED: GS10 (10-year Treasury, monthly), DGS10 (latest daily), FEDFUNDS (monthly)

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


def month_end(y, m):
    nxt = date(y + (m == 12), m % 12 + 1, 1)
    return (nxt.toordinal() - 1)


def yahoo_monthly(symbol):
    """[(YYYY-MM-DD, adjclose)] month-end values; the running month is dated at its latest trade."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=max&interval=1mo&includeAdjustedClose=true"
    res = json.loads(get(url))["chart"]["result"][0]
    ts = res["timestamp"]
    adj = res["indicators"]["adjclose"][0]["adjclose"]
    last_trade = datetime.fromtimestamp(res["meta"]["regularMarketTime"], tz=timezone.utc).date()
    rows = {}
    for t, v in zip(ts, adj):
        if v is None:
            continue
        d = datetime.fromtimestamp(t, tz=timezone.utc).date()
        # Yahoo stamps monthly bars at the month start (sometimes the prior day in UTC); snap to the month it covers.
        if d.day > 20:
            d = date.fromordinal(d.toordinal() + 12)
        y, m = d.year, d.month
        if (y, m) == (last_trade.year, last_trade.month):
            label = last_trade.isoformat()
        else:
            label = date.fromordinal(month_end(y, m)).isoformat()
        rows[f"{y}-{m:02d}"] = (label, v)
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


def main():
    prev = json.loads(OUT.read_text()) if OUT.exists() else {}
    data = {"freq": dict(prev.get("freq", {}))}
    failures = []
    for key, fn in [
        ("spx", build_spx),
        ("qqq", lambda: build_etf("QQQ")),
        ("schd", lambda: build_etf("SCHD")),
        ("bond", build_rates),
        ("fed", build_fed),
    ]:
        try:
            data[key] = fn()
            data["freq"][key] = "M"
            print(f"{key}: {len(data[key])} rows, last {data[key][-1]}")
        except Exception as e:  # noqa: BLE001 - keep the old series instead of failing the page
            failures.append(key)
            print(f"{key}: FAILED ({e}); keeping previous values", file=sys.stderr)
            if key in prev:
                data[key] = prev[key]
    if len(failures) == 5:
        sys.exit("every source failed; leaving data.json untouched")
    data["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    data["stale"] = failures
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
