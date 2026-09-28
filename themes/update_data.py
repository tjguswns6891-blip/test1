"""Rebuild themes/data.json for the theme-strength page from themes/themes.json.

Source: Yahoo Finance daily closes (one year) for every ticker, no API key needed.
Each ticker is aligned to the US trading calendar (SPY's dates) so that theme paths line up,
and a ticker that fails to download keeps its entry from the previous data.json.
Standard library only, so the GitHub Action needs no pip install.
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
CONFIG = HERE / "themes.json"
OUT = HERE / "data.json"
UA = {"User-Agent": "Mozilla/5.0 (theme-strength page updater)"}
CALENDAR = "SPY"
SPARK = 63  # daily closes kept per ticker for the sparkline (about three months)
# Period key -> trading days back from the latest close; "ytd" is resolved from the calendar.
PERIODS = {"d1": 1, "w1": 5, "m1": 21, "m3": 63, "m6": 126, "ytd": None, "y1": 252}


def get(url, tries=4):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001 - retry any network error
            if "404" in str(e):
                break
            time.sleep(2 ** k)
    raise RuntimeError(f"failed: {url}")


def daily(symbol):
    """{'name', 'currency', 'closes': [(YYYY-MM-DD, close)]} for the last year (plus a margin)."""
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}"
           f"?range=13mo&interval=1d")
    res = json.loads(get(url))["chart"]["result"][0]
    meta = res["meta"]
    tz = meta.get("gmtoffset", -14400)
    closes = {}
    for t, c in zip(res.get("timestamp") or [], res["indicators"]["quote"][0].get("close") or []):
        if c is not None and c > 0:
            d = datetime.fromtimestamp(t + tz, tz=timezone.utc).date().isoformat()  # exchange-local date
            closes[d] = c
    if not closes:
        raise RuntimeError(f"no closes: {symbol}")
    return {
        "name": meta.get("longName") or meta.get("shortName") or symbol,
        "currency": meta.get("currency") or "",
        "closes": sorted(closes.items()),
    }


def sig(x, n=5):
    return float(f"{x:.{n}g}")


def align(closes, dates):
    """Closes forward-filled onto the calendar dates; None before the ticker's first close."""
    out, i, last = [], 0, None
    for d in dates:
        while i < len(closes) and closes[i][0] <= d:
            last = closes[i][1]
            i += 1
        out.append(last)
    return out


def ret(series, back):
    if back is None or back >= len(series):
        return None
    a, b = series[-1 - back], series[-1]
    return None if a is None or b is None else round(b / a - 1, 5)


def ma_above(closes, n):
    if len(closes) < n:
        return None
    return closes[-1] >= sum(closes[-n:]) / n


def build_ticker(label, raw, dates, ytd_back):
    own = [c for _, c in raw["closes"]]
    series = align(raw["closes"], dates)
    r = {k: ret(series, b if k != "ytd" else ytd_back) for k, b in PERIODS.items()}
    r["d1"] = round(own[-1] / own[-2] - 1, 5) if len(own) > 1 else None  # its own last session
    year = own[-252:]
    return {
        "name": raw["name"],
        "cur": raw["currency"],
        "p": sig(own[-1], 6),
        "r": r,
        "hi": round(own[-1] / max(year) - 1, 4),  # distance from the 52-week high
        "a20": ma_above(own, 20),
        "a50": ma_above(own, 50),
        "sp": [sig(c, 4) if c is not None else None for c in series[-SPARK:]],
        "_series": series,
    }


def theme_paths(members, periods_back):
    """Per period, the equal-weight average of each member's price normalised to the period start.

    Its last point equals the plain average of the members' period returns, so the chart and the
    ranking agree."""
    paths = {}
    for k, back in periods_back.items():
        if not back:
            continue
        rows = [m[-1 - back:] for m in members if len(m) > back and m[-1 - back] is not None]
        if not rows:
            paths[k] = []
            continue
        pts = []
        for i in range(back + 1):
            vals = [row[i] / row[0] for row in rows if row[i] is not None]
            pts.append(round(sum(vals) / len(vals) - 1, 5))
        paths[k] = pts
    return paths


def main():
    cfg = json.loads(CONFIG.read_text())
    ymap, labels = cfg.get("yahoo", {}), cfg.get("labels", {})
    tickers = sorted({t for th in cfg["themes"] for t in th["tickers"]})
    prev = {}
    if OUT.exists():
        try:
            prev = json.loads(OUT.read_text()).get("tickers", {})
        except ValueError:
            pass

    cal = daily(CALENDAR)
    dates = [d for d, _ in cal["closes"]][-253:]
    this_year = dates[-1][:4]
    ytd_back = len(dates) - 1 - max(i for i, d in enumerate(dates) if d[:4] < this_year) \
        if any(d[:4] < this_year for d in dates) else None
    periods_back = dict(PERIODS, ytd=ytd_back)

    def fetch(t):
        try:
            return t, daily(ymap.get(t, t))
        except Exception as e:  # noqa: BLE001 - reported below, the ticker falls back
            return t, e

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(fetch, tickers))

    out, failed = {}, []
    for t, raw in results:
        if isinstance(raw, Exception):
            failed.append(t)
            if t in prev:
                out[t] = dict(prev[t], stale=True)
            continue
        rec = build_ticker(t, raw, dates, ytd_back)
        if t in labels:
            rec["name"] = labels[t]
        if ymap.get(t):
            rec["y"] = ymap[t]
        out[t] = rec
    if failed:
        print(f"  failed ({len(failed)}): {', '.join(failed)}", file=sys.stderr)

    themes = []
    for th in cfg["themes"]:
        # A stale ticker has no aligned series; it still shows in the list but stays out of the paths.
        members = [out[t]["_series"] for t in th["tickers"] if t in out and "_series" in out[t]]
        themes.append({"name": th["name"], "tickers": th["tickers"], "path": theme_paths(members, periods_back)})
    for rec in out.values():
        rec.pop("_series", None)

    data = {
        "asOf": dates[-1],
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dates": dates,
        "periods": periods_back,
        "themes": themes,
        "tickers": out,
        "missing": sorted(set(failed) - set(out)),
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"wrote {OUT} as of {dates[-1]}: {len(out)}/{len(tickers)} tickers, {len(themes)} themes")


if __name__ == "__main__":
    main()
