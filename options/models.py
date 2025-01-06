from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OptionType(Enum):
    PUT = "P"
    CALL = "C"


@dataclass
class Option:
    optype: OptionType
    asset_ticker: str
    expiry_date: datetime
    strike_price: float | int

    @property
    def ticker(self) -> str:
        return f"{self.asset_ticker}{self.expiry_date.strftime('%y%m%d')}{self.optype.value}{int(self.strike_price*1000):08}"

    def __str__(self) -> str:
        return self.ticker


class TradeAction(Enum):
    BUY = +1
    SELL = -1

    def __str__(self) -> str:
        return self.name
    
    @property
    def inverse(self) -> "TradeAction":
        return TradeAction(-self.value)
    

@dataclass
class OptionLeg:
    action: TradeAction
    quantity: int
    option: Option

    def __str__(self) -> str:
        return f"{self.action} {self.quantity} {self.option}"
    
    def opening_position(self, opening_price: float) -> "OptionPosition":
        return OptionPosition(self.action, self.quantity, self.option, opening_price)


@dataclass
class OptionPosition:
    action: TradeAction
    quantity: int
    option: Option
    open_price: float

    def __str__(self) -> str:
        return f"{self.action} {self.quantity} {self.option} @ ${self.open_price}"
    
    @property
    def as_leg(self) -> OptionLeg:
        return OptionLeg(self.action, self.quantity, self.option)
    
    @property
    def value(self) -> float:
        """
        Return the value of the position, i.e.
        the amount of money needed to open the position.
        Positive for long positions (giving money), 
        negative for short positions (receiving money).
        Each option contract is for 100 shares.
        """
        return self.action.value * self.quantity * self.open_price * 100

    def closing_position(self, closing_price: float) -> "OptionPosition":
        return OptionPosition(self.action.inverse, self.quantity, self.option, closing_price)
    
    def profit(self, closing_price: float) -> float:
        """Minus is because plus would mean loss (buying the value)."""
        return -self.value - self.closing_position(closing_price).value
    
    

if __name__ == "__main__":
    # smoke test

    leg = OptionLeg(TradeAction.BUY, 1, Option(OptionType.CALL, "AAPL", datetime(2026, 12, 31), 123.456))

    print("Leg:", leg)

    pos = leg.opening_position(42.69)

    print(f"Opening: {pos}")
    print(f"Debug print: {pos!r}")

    closing_price = 69.42
    closing_pos = pos.closing_position(closing_price)

    print(f"Closing it with: {closing_pos}")

    test_profit1 = pos.profit(closing_price)
    print(f"Profit: ${test_profit1}")
    assert test_profit1 == 2673  # -4269 + 6942 = 2673

    # test combo profit

    print("Combo test:")

    leg1 = OptionLeg(TradeAction.BUY, 1, Option(OptionType.CALL, "AAPL", datetime(2026, 12, 31), 111.0))  # arbitrary LONG
    leg2 = OptionLeg(TradeAction.SELL, 1, Option(OptionType.CALL, "AAPL", datetime(2026, 12, 31), 222.0))  # arbitrary SHORT

    pos1 = leg1.opening_position(0.10)  # buy for $0.10 x 100 = $10 debit
    pos2 = leg2.opening_position(1.00)  # sell for $1.00 x 100 = $100 credit

    print("Position 1:", pos1)
    print("Position 2:", pos2)

    print("Let's say pos1 changed to $0.11 and pos2 to $0.95")
    # pos1 profit: -$10 + $11 = $1
    # pos2 profit: $100 - $95 = $5
    # total profit: $1 + $5 = $6
    test_profit2 = pos1.profit(0.11) + pos2.profit(0.95)

    print(f"Total profit = ${test_profit2}")
    assert test_profit2 == 6

    print("All OK!")


