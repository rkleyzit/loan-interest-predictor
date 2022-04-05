from abc import ABC, abstractmethod


class ForwardRateEtl(ABC):
    """Abstract class for forward rate ETLs in case we choose to have additional sources in the future"""
    def __init__(self, source: str):
        self.source = source

    @abstractmethod
    def run(self):
        ...
