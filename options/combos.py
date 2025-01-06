from datetime import datetime

from models import OptionLeg, Option, OptionType, TradeAction


def iron_condor_legs_same_shorts_price(
    n_contracts: int,
    asset: str,
    shorts_strike_price: float,
    wingspan: float,
    dte: datetime,
) -> list[OptionLeg]:
    """
    Return the legs of an iron condor with the same strike price for the shorts.
    The longs are offset at the same percentage of the price (`wingspan` is the ratio) from the shorts.
    `dte` is the days to expiration.
    """

    lower_strike, higher_strike = shorts_strike_price * (1 - wingspan), shorts_strike_price * (1 + wingspan)
    high, low, middle = round(higher_strike), round(lower_strike), round(shorts_strike_price)  # TODO: add rounding customization

    legs = [
        OptionLeg(TradeAction.SELL, n_contracts, Option(OptionType.CALL, asset, dte, middle)),
        OptionLeg(TradeAction.SELL, n_contracts, Option(OptionType.PUT, asset, dte, middle)),
        OptionLeg(TradeAction.BUY, n_contracts, Option(OptionType.CALL, asset, dte, high)),
        OptionLeg(TradeAction.BUY, n_contracts, Option(OptionType.PUT, asset, dte, low)),
    ]
    return legs
