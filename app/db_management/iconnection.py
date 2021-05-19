from abc import ABC, abstractmethod

class IConnection(ABC):
    @abstractmethod
    def insert(self, data: dict): raise NotImplementedError

    @abstractmethod
    def find(self, query: dict): raise NotImplementedError

    @abstractmethod
    def update(self, query: dict, data: dict): raise NotImplementedError

    @abstractmethod
    def delete(self, query: dict): raise NotImplementedError