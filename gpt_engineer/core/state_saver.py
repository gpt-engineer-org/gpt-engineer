from abc import ABC, abstractmethod

class StateSaver(ABC):

    @abstractmethod
    def snapshot(self):
        pass