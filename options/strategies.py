from datetime import datetime
from typing import Callable

from combos import iron_condor_legs_same_shorts_price
from models import OptionLeg

import numpy as np
from numpy.typing import NDArray
import pandas as pd



OpeningStrategyType = Callable[
    [pd.DataFrame],  # dataframe with minute-level underlying asset price data for the day (sorted by timestamp ascendingly, no missing timestamps)
    # -> returns:
    tuple[
        int,  # index of the minute when the positions are opened (as in the dataframe)
        list[OptionLeg]  # list of legs to open
    ]
]


def opening_strategy_iron_condor_specific_minute_idx(
    minute_idx: int,
) -> OpeningStrategyType:
    """
    Return an opening strategy that opens the given legs at the specified minute index.
    """
    def strategy(df: pd.DataFrame) -> tuple[int, list[OptionLeg]]:
        asset = df.index.get_level_values("symbol").unique()[0]
        opening_minute_price = df.iloc[minute_idx]["open"]
        current_day: datetime = df.index.get_level_values("timestamp").unique()[0].to_pydatetime().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        legs = iron_condor_legs_same_shorts_price(
            n_contracts=1,
            asset=asset,
            shorts_strike_price=opening_minute_price,
            wingspan=0.015,
            dte=current_day  # 0DTE
        )
        return minute_idx, legs
    return strategy



ClosingStrategyType = Callable[
    [NDArray],  # array of profits for each minute after opening
    # -> returns:
    float  # realised profit
]


def closing_strategy_last(values: NDArray) -> float:
    return values[-1]


def closing_strategy_max(values: NDArray) -> float:
    return values.max()


def closing_strategy_middle(values: NDArray) -> float:
    return values[len(values) // 2]


def closing_strategy_limit(limit_value: float) -> ClosingStrategyType:
    def strategy(values: NDArray) -> float:
        for value in values:
            if value >= limit_value:
                return value
        return values[-1]
    return strategy


def closing_strategy_limit_stoploss(limit_value: float, stoploss_value: float) -> ClosingStrategyType:
    def strategy(values: NDArray) -> float:
        for value in values:
            if value >= limit_value:
                return value
            if value <= stoploss_value:
                return value
        return values[-1]
    return strategy


def closing_strategy_last_n(n: int) -> ClosingStrategyType:
    def strategy(values: NDArray) -> float:
        return values[-n]
    return strategy
