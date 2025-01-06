from abc import ABC, abstractmethod
from datetime import datetime

from models import Option

import pandas as pd


class OptionsDataService(ABC):
    @abstractmethod
    def full_day_minutely_data(self, day: datetime, options: list[Option]) -> pd.DataFrame:
        ...


class AssetDataService(ABC):
    @abstractmethod
    def full_day_minutely_data(self, day: datetime, ticker: str) -> pd.DataFrame:
        ...

    @abstractmethod
    def daily_candles_data(self, start: datetime, end: datetime, ticker: str) -> pd.DataFrame:
        ...