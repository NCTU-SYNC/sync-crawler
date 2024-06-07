from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Optional


class DataReader(ABC):
    @abstractmethod
    def read(self, num: Optional[int] = None) -> Iterable:
        pass


class DataWriter(ABC):
    @abstractmethod
    def write(self, data: Iterable):
        pass
