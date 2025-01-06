from datetime import datetime, timezone
import os
import warnings

from models import Option
from services.base import OptionsDataService, AssetDataService

from alpaca.data.historical import OptionHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import OptionBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import dotenv
import pandas as pd


def _load_keys_from_env() -> tuple[str, str]:
    dotenv.load_dotenv()
    api_key = os.getenv("ALPACA_PAPER_API_KEY")
    secret_key = os.getenv("ALPACA_PAPER_SECRET_KEY")

    if api_key is None or secret_key is None:
        raise EnvironmentError("ALPACA_PAPER_API_KEY or ALPACA_PAPER_SECRET_KEY not set in environment vars (or .env file)")

    return api_key, secret_key


class AlpacaOptionsDataService(OptionsDataService):
    def __init__(self):     
        api_key, secret_key = _load_keys_from_env()
        self.options_client = OptionHistoricalDataClient(api_key, secret_key)

    def full_day_minutely_data(self, day: datetime, options: list[Option]) -> pd.DataFrame:
        tickers = [opt.ticker for opt in options]
        full_day_opts_df = self.options_client.get_option_bars(OptionBarsRequest(
            symbol_or_symbols=tickers,
            timeframe=TimeFrame.Minute,  # type: ignore
            start=day,
        )).df  # type: ignore

        full_day_opts_nomissing_df = full_day_opts_df\
            .reindex(pd.MultiIndex.from_product([
                tickers,
                full_day_opts_df.index.get_level_values("timestamp").unique()
            ], names=["symbol", "timestamp"]))\

        full_day_opts_nomissing_df[["volume", "vwap", "trade_count"]] = full_day_opts_nomissing_df[["volume", "vwap", "trade_count"]].fillna(0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # interpolate missing prices with latest known:
            full_day_opts_nomissing_df = full_day_opts_nomissing_df.fillna(method='ffill')  # type: ignore
            # if still no info for the whole period of some ticker, fill with $0.01:
            full_day_opts_nomissing_df = full_day_opts_nomissing_df.fillna(0.01)  
        return full_day_opts_nomissing_df


class AlpacaAssetDataService(AssetDataService):
    def __init__(self):
        api_key, secret_key = _load_keys_from_env()
        self.stocks_client = StockHistoricalDataClient(api_key, secret_key)

    def full_day_minutely_data(self, day: datetime, ticker: str) -> pd.DataFrame:
        asset_prices = self.stocks_client.get_stock_bars(StockBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=TimeFrame.Minute,  # type: ignore
            start=day,
            end=day + pd.Timedelta(days=1)
        )).df  # type: ignore

        # filter by New York working hours:
        working_day_prices = asset_prices.loc[
            (asset_prices.index.get_level_values("timestamp") >= day.replace(hour=14, minute=30, tzinfo=timezone.utc))\
            & (asset_prices.index.get_level_values("timestamp") < day.replace(hour=21, minute=0, tzinfo=timezone.utc))
        ]

        return working_day_prices

    def daily_candles_data(self, start: datetime, end: datetime, ticker: str) -> pd.DataFrame:
        asset_prices = self.stocks_client.get_stock_bars(StockBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=TimeFrame.Day,  # type: ignore
            start=start,
            end=end
        )).df  # type: ignore
        return asset_prices