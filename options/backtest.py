from datetime import datetime

from models import OptionPosition
from services.base import OptionsDataService, AssetDataService
from strategies import OpeningStrategyType, ClosingStrategyType

import numpy as np
from numpy.typing import NDArray
import pandas as pd
from tqdm import tqdm


def closing_profit_each_timestamp(positions: list[OptionPosition], df: pd.DataFrame) -> NDArray:
    """Return the profit for each timestamp (minute) after positions open, based on the given dataframe of option prices."""
    timestamps = df.index.get_level_values("timestamp").unique()
    profits = [
        sum(
            pos.profit(float(df.loc[(pos.option.ticker, timestamp), "close"]))  # type: ignore
            for pos in positions
        )
        for timestamp in timestamps
    ]
    return np.array(profits)


def do_simulation(
    start_date: datetime,
    end_date: datetime,
    asset: str,
    asset_data_service: AssetDataService,
    options_data_service: OptionsDataService,
    opening_strategy: OpeningStrategyType,
    closing_strategy: ClosingStrategyType,
) -> pd.DataFrame:
    """Perform a simulation of the given strategy.
    Return the value of the portfolio at the end of each day."""

    money = 0
    results = []
    skipped_days = 0

    df_asset = asset_data_service.daily_candles_data(start_date, end_date, asset)

    for timestamp in tqdm(df_asset.index.get_level_values("timestamp").unique()):
        day = timestamp.to_pydatetime()
        df_day_stock = asset_data_service.full_day_minutely_data(day, asset)
        opening_timestamp, legs = opening_strategy(df_day_stock)
        df_day_options = options_data_service.full_day_minutely_data(day, [leg.option for leg in legs])

        # data is incomplete, so if opening_timestamp is before the beginning of the options data, skip this day
        if opening_timestamp < df_day_options.index.get_level_values("timestamp").min():
            skipped_days += 1
            results.append(money)  # keep the same value as the previous day, for the sake of shape-matching
            continue

        positions = [leg.opening_position(float(df_day_options.loc[(leg.option.ticker, opening_timestamp), "open"])) for leg in legs]  # type: ignore
        df_day_remaining = df_day_options[df_day_options.index.get_level_values("timestamp") >= opening_timestamp]
        potential_profits = closing_profit_each_timestamp(positions, df_day_remaining)
        closing_profit = closing_strategy(potential_profits)
        money += closing_profit
        results.append(money)

    print(f"Skipped {skipped_days} days due to incomplete data.")

    return pd.DataFrame(results, index=df_asset.index.get_level_values("timestamp").unique(), columns=["total_profit"])


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    from services.alpaca import AlpacaAssetDataService, AlpacaOptionsDataService
    from strategies import *

    start_date = datetime(2024, 2, 5)  # farthest back we have data for
    end_date = datetime(2024, 12, 31)
    asset = "SPY"

    asset_data_service = AlpacaAssetDataService()
    options_data_service = AlpacaOptionsDataService()
    opening_strategy = opening_strategy_iron_condor_specific_minute_idx(30)
    closing_strategy = closing_strategy_limit_or_last_n(150, 15)

    profit_df = do_simulation(
        start_date,
        end_date,
        asset,
        asset_data_service,
        options_data_service,
        opening_strategy,
        closing_strategy,
    )
    
    fig, ax = plt.subplots()
    profit_df.plot(ax=ax)
    plt.show()