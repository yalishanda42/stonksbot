# Profit?

## Features

* Stock prices:
    * Open
    * High
    * Low
    * Close
    * Volume
* Options prices?
    * ...
* Fundamentals:
    * P/E
    * EPS
    * Dividend
    * Market Cap
    * Earnings
    * Cash Flow
    * Splits
* Tech indicators:
    * EMA
    * SMA
    * VWAP (premium on AV - need to calc myself)
    * MACD (premium on AV - need to calc myself)
    * ...?
* Economic indicators:
    * Real GDP
    * Real GDP per capita
    * Treasury Yield
    * Federal Funds Interest Rate
    * CPI
    * Inflation
    * Retail Sells
    * Unemployment Rate
* Holders?
    * Institutional
    * Insider
    * Mutual funds
* Analysis/Prediction?
    * Buy/Sell/Hold Percentages
    * 1Y Target price
* News:
    * Overall sentiment (mean, std, min, max) - precomputed from Alpha Vantage
    * Different time periods sentiment (day, week, month, year) - computed by LLM reading articles
    * Finding and parsing said company's recent news?
* Psychological
    * Fear & Greed Index
    * Put/Call Ratio
    * Is the number round, whole, etc (because of stop/limit orders)
    * Is ATH
    * Is a buy point defined by various indicators, such as 'cup without handle', etc
* Social
    * Congressmen trading?
* Misc / Derived features
    * Is stock market open / Is after hours / Is pre market / Is there a holiday


## APIs

### Alpha Vantage (Prices, News Sentiment, fundamentals, tech indicators, economic indicators)
https://www.alphavantage.co/documentation/

### Yahoo Finance (Prices, Fundamentals, Holders, Options, News(?))
https://pypi.org/project/yfinance/

### FRED (Economic Indicators)
https://fred.stlouisfed.org/docs/api/fred/
https://pypi.org/project/fredapi/

### Twitter (X)
NO HISTORIC TWEETS ANYMORE ;/
free version: max 1500 tweets read

### LLM
Anthropic's Claude 3


## Stonks to gather info on:
* AAPL
* MSFT
* AMZN
* NVDA
* TSLA
* RDDT (test only?)
* GME
* TSM
* INTC