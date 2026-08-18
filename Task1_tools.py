"""
tools.py
--------
Free, no-API-key tools shared by the agents in the Company Intelligence system.

- get_stock_performance : pulls recent price action via yfinance
- get_company_news      : pulls recent headlines via DuckDuckGo search
- calculate_volatility  : simple risk-indicator calculation (pure python, no network)

Each tool is decorated with @tool so LangGraph's `create_react_agent` can bind
it to a specific agent and call it autonomously.
"""

from __future__ import annotations

import statistics
from typing import List

import yfinance as yf
from ddgs import DDGS
from langchain_core.tools import tool


@tool
def get_stock_performance(ticker: str) -> dict:
    """
    Fetch recent stock performance for a given ticker symbol (e.g. 'NVDA', 'TSLA', 'AAPL').

    Returns a dict with the last close price, 5-day and 1-month percentage change,
    52-week high/low, and daily closing prices for the last 10 trading days.
    Use this to ground any market commentary in real numbers.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")

        if hist.empty:
            return {"error": f"No data found for ticker '{ticker}'. Check the symbol."}

        # Drop any rows with missing Close prices. yfinance sometimes includes
        # an incomplete row for the current trading day (e.g. if the market
        # is still open or data hasn't finalized), which would otherwise
        # make the "last close" look like NaN instead of the real latest price.
        hist = hist.dropna(subset=["Close"])
        if hist.empty:
            return {"error": f"No valid closing price data found for ticker '{ticker}'."}

        closes = hist["Close"].round(2)
        last_close = float(closes.iloc[-1])

        def pct_change(days: int) -> float | None:
            if len(closes) <= days:
                return None
            past = float(closes.iloc[-days - 1])
            return round((last_close - past) / past * 100, 2)

        info = stock.info or {}

        return {
            "ticker": ticker.upper(),
            "company_name": info.get("longName", ticker.upper()),
            "last_close": last_close,
            "currency": info.get("currency", "USD"),
            "change_5d_pct": pct_change(5),
            "change_1mo_pct": pct_change(21),
            "week52_high": info.get("fiftyTwoWeekHigh"),
            "week52_low": info.get("fiftyTwoWeekLow"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "last_10_closes": [round(v, 2) for v in closes.iloc[-10:].tolist()],
        }
    except Exception as e:
        return {"error": f"Failed to fetch stock data for '{ticker}': {e}"}


@tool
def get_company_news(company: str, max_results: int = 5) -> List[dict]:
    """
    Search recent news headlines about a company using DuckDuckGo.

    Args:
        company: Company or ticker name to search news for (e.g. 'Nvidia', 'Tesla').
        max_results: Number of headlines to retrieve (default 5).

    Returns a list of dicts with 'title', 'source', 'date', and 'snippet' for
    each article found. Use this to ground risk/sentiment commentary in
    actual recent events rather than guessing.
    """
    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.news(f"{company} stock news", max_results=max_results)
            )
        if not results:
            return [{"info": f"No recent news found for '{company}'."}]

        return [
            {
                "title": r.get("title"),
                "source": r.get("source"),
                "date": r.get("date"),
                "snippet": r.get("body"),
            }
            for r in results
        ]
    except Exception as e:
        return [{"error": f"Failed to fetch news for '{company}': {e}"}]


@tool
def calculate_volatility(prices: List[float]) -> dict:
    """
    Calculate a simple risk/volatility indicator from a list of recent closing prices.

    Args:
        prices: A list of recent closing prices, oldest first.

    Returns the standard deviation of daily returns (%) and a plain-language
    risk band ('Low', 'Moderate', 'High'). Use this to back up any risk-factor
    claims with an actual computed number instead of a vague guess.
    """
    try:
        if len(prices) < 3:
            return {"error": "Need at least 3 price points to calculate volatility."}

        daily_returns = [
            (prices[i] - prices[i - 1]) / prices[i - 1] * 100
            for i in range(1, len(prices))
            if prices[i - 1] != 0
        ]

        if len(daily_returns) < 2:
            return {"error": "Not enough valid returns to calculate volatility."}

        vol = round(statistics.stdev(daily_returns), 2)

        if vol < 1.5:
            band = "Low"
        elif vol < 3.5:
            band = "Moderate"
        else:
            band = "High"

        return {
            "daily_return_std_dev_pct": vol,
            "risk_band": band,
            "num_data_points": len(prices),
        }
    except Exception as e:
        return {"error": f"Failed to calculate volatility: {e}"}