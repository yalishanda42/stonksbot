import json

from strategies import *

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
import pandas as pd
import streamlit as st


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

st.set_page_config(page_title="Interactive PnL Analysis", layout="wide")
st.title("Interactive PnL Analysis")

sidebar = st.sidebar
profit = sidebar.slider("Profit Limit ($)", min_value=10, max_value=5000, value=400, step=50)
stoploss = sidebar.slider("Stop Loss ($)", min_value=-5000, max_value=-10, value=-400, step=50)
wait_before_stoploss = sidebar.slider(
    "Wait Before Setting Stop Loss (minute idx)", min_value=0, max_value=350, value=0, step=1
)
max_closing_minute = sidebar.slider(
    "Max Closing Minute (idx)", min_value=0, max_value=350, value=300, step=1
)

df = process_fn(profit, stoploss, wait_before_stoploss, max_closing_minute)

# Plot cumulative PnL
st.subheader("Cumulative PnL ($)")
st.line_chart(df.set_index("day")["pnl"], height=400, use_container_width=True)

# Key numbers
final_pnl = float(df["pnl"].iloc[-1]) if len(df) > 0 else 0.0
avg_daily = float(df["pnl"].diff().dropna().mean()) if len(df) > 1 else 0.0
with st.columns(3)[0]:
    st.metric("Final Cumulative PnL ($)", f"{final_pnl:,.2f}")
with st.columns(3)[1]:
    st.metric("Avg PnL per Day ($)", f"{avg_daily:,.2f}")
with st.columns(3)[2]:
    st.metric("Days", len(df))

# Show recent rows if user wants
with st.expander("Show data (last 200 rows)"):
    st.dataframe(df.tail(200), use_container_width=True)
