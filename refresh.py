"""Refresh a reviewable market snapshot from Yahoo, NSE and Screener."""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent
PORTFOLIO = [
    ("TCS", "Technology"), ("INFY", "Technology"), ("RELIANCE", "Energy"),
    ("HDFCBANK", "Banking"), ("ICICIBANK", "Banking"), ("SBIN", "Banking"),
    ("BHARTIARTL", "Telecom"), ("ITC", "Consumer"), ("HINDUNILVR", "Consumer"),
    ("EICHERMOT", "Automotive"), ("MARUTI", "Automotive"), ("SUNPHARMA", "Pharma"),
    ("DRREDDY", "Pharma"), ("LT", "Industrials"), ("ASIANPAINT", "Materials"),
    ("PIDILITIND", "Materials"), ("DIXON", "Electronics"), ("POLYCAB", "Industrials"),
]
EXTRA = ["DMART", "DIVISLAB", "TRENT", "BAJFINANCE"]
HEADERS = {"User-Agent": "Mozilla/5.0 FINN-prototype/1.0", "Accept": "application/json,text/html,*/*"}


def get(session, url, **kwargs):
    response = session.get(url, timeout=18, **kwargs)
    response.raise_for_status()
    return response


def number(value):
    try:
        return float(value.replace(",", "").replace("%", "").replace("+", "").strip())
    except (AttributeError, ValueError):
        return None


def table(section):
    el = section.select_one("table") if section else None
    if not el:
        return {"periods": [], "rows": {}}
    rows = [[cell.get_text(" ", strip=True) for cell in tr.select("th,td")] for tr in el.select("tr")]
    return {"periods": rows[0][1:], "rows": {re.sub(r"\s*\+.*$", "", row[0]).strip(): [number(x) for x in row[1:]] for row in rows[1:] if row}}


def research(session, symbol):
    symbol = symbol.upper()
    if not re.fullmatch(r"[A-Z0-9&-]{1,20}", symbol):
        raise ValueError("Use an NSE ticker, such as TCS")
    url = f"https://www.screener.in/company/{symbol}/consolidated/"
    response = get(session, url)
    page = BeautifulSoup(response.text, "html.parser")
    title = page.select_one("#top h1")
    if not title:
        raise ValueError(f"No Screener page found for {symbol}")
    about = page.select_one("#top .about")
    documents = []
    for a in page.select("#documents a[href]"):
        label = a.get_text(" ", strip=True)
        href = a.get("href", "")
        if ("Annual Report" in label or label == "Transcript") and href.startswith("https://"):
            documents.append({"label": label, "url": href, "type": "annual" if "Annual Report" in label else "transcript"})
    return {
        "symbol": symbol, "name": title.get_text(" ", strip=True),
        "about": about.get_text(" ", strip=True) if about else "",
        "source": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "quarters": table(page.select_one("#quarters")),
        "annual": table(page.select_one("#profit-loss")),
        "balance": table(page.select_one("#balance-sheet")),
        "cash": table(page.select_one("#cash-flow")),
        "documents": documents[:30],
    }


def price(session, symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.NS?range=3mo&interval=1d"
    result = get(session, url).json()["chart"]["result"][0]
    q = result["indicators"]["quote"][0]
    bars = [{"date": datetime.fromtimestamp(ts, timezone.utc).date().isoformat(), "close": round(c, 2), "volume": int(v)}
            for ts, c, v in zip(result["timestamp"], q["close"], q["volume"])
            if c is not None and v is not None]
    if len(bars) < 2:
        raise ValueError(f"Not enough daily bars for {symbol}")
    last, prev = bars[-1], bars[-2]
    baseline = bars[-21:-1]
    average = sum(b["volume"] for b in baseline) / len(baseline)
    return {"symbol": symbol, "source": url, "date": last["date"], "close": last["close"],
            "change_pct": round((last["close"] / prev["close"] - 1) * 100, 2),
            "volume": last["volume"], "volume_ratio": round(last["volume"] / average, 2),
            "bars": bars[-30:]}


def classify(row):
    text = (row.get("desc", "") + " " + row.get("attchmntText", "")).lower()
    rules = [
        ("Results", ["financial results", "quarterly result", "audited result", "unaudited result"]),
        ("Management", ["resignation", "appointment", "director", "chief financial officer", "ceo", "cfo"]),
        ("Deal", ["acquisition", "merger", "amalgamation", "joint venture", "order win"]),
        ("Capital", ["capex", "capital expenditure", "fund raise", "fundraising", "rights issue"]),
        ("Risk", ["litigation", "arbitration", "penalty", "show cause"]),
        ("Dividend", ["dividend", "buyback"]),
    ]
    for category, terms in rules:
        if any(term in text for term in terms):
            return category
    return "Routine"


def announcements(session, start, end):
    url = "https://www.nseindia.com/api/corporate-announcements"
    params = {"index": "equities", "from_date": start.strftime("%d-%m-%Y"), "to_date": end.strftime("%d-%m-%Y")}
    rows = get(session, url, params=params, headers={**HEADERS, "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-announcements"}).json()
    symbols = {s for s, _ in PORTFOLIO}
    out = []
    for row in rows:
        if row.get("symbol") not in symbols:
            continue
        out.append({"id": str(row.get("seq_id") or row.get("dt")), "symbol": row["symbol"],
                    "date": row.get("sort_date", ""), "title": row.get("desc", "Announcement"),
                    "summary": row.get("attchmntText") or row.get("desc", ""),
                    "category": classify(row), "url": row.get("attchmntFile", ""),
                    "source": "NSE"})
    return sorted(out, key=lambda x: x["date"], reverse=True)


def build():
    session = requests.Session()
    session.headers.update(HEADERS)
    today = datetime.now(timezone.utc).date()
    snapshot = {"generated_at": datetime.now(timezone.utc).isoformat(),
                "portfolio": [{"symbol": s, "sector": sector} for s, sector in PORTFOLIO],
                "extra": EXTRA, "prices": {}, "filings": [], "research": {}, "errors": []}
    for symbol, _ in PORTFOLIO:
        try:
            snapshot["prices"][symbol] = price(session, symbol)
        except Exception as exc:
            snapshot["errors"].append(f"Price {symbol}: {exc}")
    try:
        snapshot["filings"] = announcements(session, today - timedelta(days=14), today)
    except Exception as exc:
        snapshot["errors"].append(f"NSE filings: {exc}")
    for symbol in ["TCS", "RELIANCE", "HDFCBANK", "DIXON", *EXTRA]:
        try:
            snapshot["research"][symbol] = research(session, symbol)
        except Exception as exc:
            snapshot["errors"].append(f"Research {symbol}: {exc}")
        time.sleep(0.15)
    target = ROOT / "dist" / "snapshot.json"
    target.write_text(json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")))
    print(f"Wrote {target}: {len(snapshot['prices'])} prices, {len(snapshot['filings'])} filings, {len(snapshot['research'])} research pages")
    for error in snapshot["errors"]:
        print("WARN", error)


if __name__ == "__main__":
    build()
