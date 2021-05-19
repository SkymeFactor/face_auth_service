from abc import ABC, abstractmethod
from db_management.iconnection import IConnection
from authentication.iauth import IAuth
from io import BytesIO


class IUser(ABC):
    @abstractmethod
    def authenticate_user(self, db_connection: IConnection, auth_backend: IAuth, username: str, data: BytesIO, client_id: str):
        raise NotImplementedError

    @abstractmethod
    def find_user(self, db_connection: IConnection, username: str, client_id: str):
        raise NotImplementedError

    @abstractmethod
    def create_user(self, db_connection: IConnection, username: str, data: BytesIO, client_id: str):
        raise NotImplementedError

    @abstractmethod
    def update_username(self, db_connection: IConnection, username: str, new_username: str, client_id: str):
        raise NotImplementedError

    @abstractmethod
    def update_user_image(self, db_connection: IConnection, username: str, data: BytesIO, client_id: str):
        raise NotImplementedError

    @abstractmethod
    def delete_user(self, db_connection: IConnection, username: str, client_id: str):
        raise NotImplementedError