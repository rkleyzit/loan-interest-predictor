from abc import ABC, abstractmethod
from datetime import datetime


class ForwardRateEtl(ABC):
    """Abstract class for forward rate ETLs in case we choose to have additional sources in the future"""
    def __init__(self, source: str, run_time: datetime):
        self.source = source
        self.run_time = run_time

    @abstractmethod
    def run(self):
        ...
