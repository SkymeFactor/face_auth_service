from abc import ABC, abstractmethod
from io import BytesIO

class IAuth(ABC):
    @abstractmethod
    def compare(self, image_1: BytesIO, image_2: BytesIO): raise NotImplementedError