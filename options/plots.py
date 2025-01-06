import plotly.graph_objects as go


def plot_candles_OHLC(data, title):
    """`data` should be an ndarray of shape (days, 4);
    second axis has open, high, low and closing prices resp."""
    fig = go.Figure(data=[go.Candlestick(
        x=list(range(len(data))),
        open=data[:, 0],
        high=data[:, 1],
        low=data[:, 2],
        close=data[:, 3],
    )])

    fig.update_layout(title=title)
    fig.show()

    return fig
