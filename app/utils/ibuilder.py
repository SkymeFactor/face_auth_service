from abc import ABC, abstractmethod
from service_locator import ServiceLocator
from config.config_manager import JSONDataWrapper

class IBuilder(ABC):
    @abstractmethod
    def create_services(self, srv_locator: ServiceLocator): raise NotImplementedError

    @abstractmethod
    def create_flask(self, cfg_manager: JSONDataWrapper): raise NotImplementedError
