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

    # debug plot
    # plt.plot(timestamps, profits)
    # plt.show()

    return np.array(profits)


def do_simulation(
    start_date: datetime,
    end_date: datetime,
    asset: str,
    asset_data_service: AssetDataService,
    options_data_service: OptionsDataService,
    opening_strategy: OpeningStrategyType,
    closing_strategy: ClosingStrategyType,
) -> tuple[pd.DataFrame, list[NDArray]]:
    """Perform a simulation of the given strategy.
    Return the value of the portfolio at the end of each day,
    as well as the daily profit/loss position movements for analysis purposes."""

    money = 0
    results = []
    daily_pnl_movements = []
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
        daily_pnl_movements.append(potential_profits)

        closing_profit = closing_strategy(potential_profits)
        money += closing_profit
        results.append(money)

    if skipped_days > 0:
        print(f"Skipped {skipped_days} days due to incomplete data.")

    results_df = pd.DataFrame(results, index=df_asset.index.get_level_values("timestamp").unique(), columns=["total_profit"])

    return results_df, daily_pnl_movements


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    from services.alpaca import AlpacaAssetDataService, AlpacaOptionsDataService
    from strategies import *

    start_date = datetime(2024, 4, 1)  # farthest back we have data for from Alpaca is 2024-02-05
    end_date = datetime(2024, 5, 1)
    asset = "SPY"

    asset_data_service = AlpacaAssetDataService()
    options_data_service = AlpacaOptionsDataService()
    opening_strategy = opening_strategy_iron_condor_specific_minute_idx(3)
    closing_strategy = closing_strategy_limit_or_stoploss_or_last_n(500, 2000, 30)

    profit_df, _ = do_simulation(
        start_date,
        end_date,
        asset,
        asset_data_service,
        options_data_service,
        opening_strategy,
        closing_strategy,
    )

    print("Simulation complete.")
    daily_profit_df = profit_df.dropna().diff()
    print(f"Winning rate: {daily_profit_df[daily_profit_df['total_profit'] > 0].shape[0] / daily_profit_df.shape[0]:.2%}")
    
    fig, ax = plt.subplots()
    profit_df.plot(ax=ax)
    plt.show()