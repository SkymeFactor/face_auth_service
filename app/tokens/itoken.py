from abc import ABC, abstractmethod
from db_management.iconnection import IConnection


class IToken(ABC):
    @abstractmethod
    def get_token_owner(self, db_connection: IConnection, token: str):
        raise NotImplementedError

    @abstractmethod
    def generate_code(self, db_connection: IConnection, client_id: str, expires_in: float):
        raise NotImplementedError

    @abstractmethod
    def generate_tokens(self,
            atdb_connection: IConnection,
            rtdb_connection: IConnection,
            at_expires_in: float,
            rt_expires_in: float,
            client_id: str
    ):
        raise NotImplementedError

    @abstractmethod
    def update_tokens(self, db_connection: IConnection, refresh_token: str):
        raise NotImplementedError
