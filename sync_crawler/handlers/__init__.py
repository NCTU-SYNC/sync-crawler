from abc import ABC, abstractmethod
from collections.abc import Iterable


class DataReader(ABC):
    @abstractmethod
    def read(self, num: int | None = None) -> Iterable:
        pass


class DataWriter(ABC):
    @abstractmethod
    def write(self, data: Iterable):
        pass
