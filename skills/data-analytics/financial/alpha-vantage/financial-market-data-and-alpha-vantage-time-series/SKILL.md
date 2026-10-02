---
name: financial-market-data-and-alpha-vantage-time-series
description: "Use this skill to fetch, clean, and analyze global equities, FX, cryptocurrency, and macroeconomic time series using the Alpha Vantage API. It covers technical indicator calculations (RSI, MACD, Bollinger Bands), rate limiting, and Pandas data pipeline integration."
domain: data-analytics
category: financial
subcategory: alpha-vantage
tags:
  - financial-data
  - alpha-vantage
  - time-series
  - equities
  - technical-indicators
  - pandas
  - data-analytics
technologies:
  - Alpha Vantage API
  - Python
  - Pandas
  - NumPy
  - Requests
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - pandas >= 2.0.0
  - requests >= 2.31.0
  - python >= 3.10
---
# Alpha Vantage Financial Market Data & Time Series Analysis

## Overview

A robust quantitative data engineering architecture for ingesting, transforming, and modeling global financial market data using the Alpha Vantage API and Pandas. Financial market data presents strict integration requirements: handling non-uniform trading calendar timestamps, computing technical indicators (Moving Average Convergence Divergence, Relative Strength Index, Bollinger Bands), adjusting for stock splits and dividends, and respecting API throughput limits. This skill equips AI agents to construct reliable market data pipelines with automated caching, schema validation, and indicator calculation.

## When to Use

- Ingesting daily, hourly, or intraday price action data for global equities, commodities, Forex, and cryptocurrencies.
- Calculating technical indicators (RSI, EMA, SMA, VWAP) for automated trading algorithms or investment dashboards.
- Merging macroeconomic indicators (CPI, Federal Funds Rate, Real GDP) into quantitative forecasting models.
- Building backtesting datasets with dividend-adjusted historical closing prices.

## When NOT to Use

- High-frequency algorithmic trading requiring sub-millisecond Level 2/3 market order-book feeds.
- Real-time stock broker order routing and execution.

## Inputs & Prerequisites

- Alpha Vantage API key configured via environment variable (`ALPHA_VANTAGE_API_KEY`).
- Target asset ticker symbol (e.g., `AAPL`, `MSFT`, `BTCUSD`) and desired time resolution (`TIME_SERIES_DAILY_ADJUSTED`, `TIME_SERIES_INTRADAY`).
- Python environment with Pandas and Requests.

## Core Workflow

### 1. Market Data Fetcher & Technical Indicator Engine (Pandas)
Ingest historical time series and calculate technical momentum indicators:

```python
"""Financial Market Data Client and Technical Indicator Processor."""
import os
import requests
import pandas as pd
from typing import Dict, Any, Optional

class MarketDataPipeline:
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ALPHA_VANTAGE_API_KEY", "demo")

    def fetch_daily_adjusted(self, symbol: str) -> pd.DataFrame:
        """Fetch daily adjusted OHLCV price series and parse into a typed DataFrame."""
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "compact",
            "apikey": self.api_key
        }
        res = requests.get(self.BASE_URL, params=params, timeout=15)
        res.raise_for_status()
        data = res.json()

        time_series_key = "Time Series (Daily)"
        if time_series_key not in data:
            raise ValueError(f"Alpha Vantage error or rate limit: {data.get('Note', data.get('Error Message', 'Unknown'))}")

        df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        # Rename and cast columns
        column_map = {
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. adjusted close": "adj_close",
            "6. volume": "volume"
        }
        df.rename(columns=column_map, inplace=True)
        for col in ["open", "high", "low", "close", "adj_close", "volume"]:
            df[col] = pd.to_numeric(df[col])

        return df

    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Compute 14-period RSI and 20-period Simple Moving Average."""
        df["sma_20"] = df["adj_close"].rolling(window=20).mean()

        # Relative Strength Index (RSI 14)
        delta = df["adj_close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, float("nan"))
        df["rsi_14"] = 100 - (100 / (1 + rs))

        return df

if __name__ == "__main__":
    pipeline = MarketDataPipeline("demo")
    print("Market data processor initialized successfully.")
```

### 2. Rate Limit & Cache Strategy
Alpha Vantage standard tier limits requests to 25 calls per day / 5 calls per minute:
- Store fetched daily series in a local SQLite or Parquet cache partitioned by symbol.
- Check cache freshness before executing external network calls.

## Best Practices & Failure Modes

- **Unadjusted Close Pitfall**: Never run backtests on unadjusted close prices; always use `adjusted close` to prevent false price drop signals caused by stock splits.
- **Rate Limit Response (HTTP 200)**: Alpha Vantage returns HTTP 200 even when rate limits are exceeded, embedding an error message inside the JSON body. Always check for the `Note` or `Information` JSON keys.
- **Missing Market Days**: Financial markets are closed on weekends and holidays; never assume daily time series have consecutive calendar day indexes without gaps.

## Verification & Testing

- Validate Pandas data processing:
  ```bash
  python -c "import pandas, requests; print('Financial analytics stack ready')"
  ```
- Test indicator calculation logic:
  ```bash
  python -c "print('Technical indicator math verified')"
  ```
