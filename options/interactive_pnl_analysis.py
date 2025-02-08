import json

from strategies import *

from gradio.layouts import Column
from gradio.blocks import Blocks
from gradio.components import LinePlot, Slider
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
import pandas as pd


with open("daily_movements_open2.json", "r") as f:
    daily_movements = json.load(f)
    daily_movements = [np.array(l) for l in daily_movements]
    assert len(daily_movements) > 0, "No data loaded"


def calculate_pnl(profit, stoploss, wait_before_stoploss, max_closing_minute) -> NDArray:
    pnl = np.array([
        closing_strategy_limit_or_stoploss_after_n_ormth_minute(
            profit,
            stoploss,
            wait_before_stoploss,
            max_closing_minute,
        )(daily_movement)
        for daily_movement in daily_movements
    ])
    cumulative_pnl = pnl.cumsum()
    
    return cumulative_pnl

def pnl_to_df(pnl: NDArray) -> pd.DataFrame:
    return pd.DataFrame({
        "day": list(range(len(pnl))),
        "pnl": pnl,
    })

def process_fn(profit, stoploss, wait_before_stoploss, max_closing_minute) -> pd.DataFrame:
    pnl = calculate_pnl(profit, stoploss, wait_before_stoploss, max_closing_minute)
    return pnl_to_df(pnl)

with Blocks() as blocks:
    with Column():
        profit = Slider(
            minimum=10, maximum=5000, value=400, step=50, 
            label="Profit Limit ($)"
        )
        stoploss = Slider(
            minimum=-5000, maximum=-10, value=-400, step=50, 
            label="Stop Loss ($)"
        )
        wait_before_stoploss = Slider(
            minimum=0, maximum=350, value=0, step=1, 
            label="Wait Before Setting Stop Loss (minute idx)"
        )
        max_closing_minute = Slider(
            minimum=0, maximum=350, value=300, step=1, 
            label="Max Closing Minute (idx)"
        )
    
    plot = LinePlot(
        process_fn,
        x="day",
        y="pnl",
        inputs=[profit, stoploss, wait_before_stoploss, max_closing_minute],
        title="Cumulative PnL ($)",
        x_title="Day (idx)",
        y_title="$",
        height=400,
    )



blocks.launch()
