from abc import ABC, abstractmethod
from db_management.iconnection import IConnection


class IClient(ABC):
    @abstractmethod
    def get_client(self, db_connection: IConnection, client_id: str):
        raise NotImplementedError

    @abstractmethod
    def validate_client(self, db_connection: IConnection, client_id: str, client_secret: str):
    	raise NotImplementedError

