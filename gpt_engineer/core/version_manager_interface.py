from abc import ABC, abstractmethod

class VersionManagerInterface(ABC):

    @abstractmethod
    def snapshot(self):
        pass