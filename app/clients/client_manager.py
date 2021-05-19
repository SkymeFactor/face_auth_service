from db_management.iconnection import IConnection
from .iclient import IClient


class ClientManager(IClient):

    def get_client(self, db_connection: IConnection, client_id):
        client = db_connection.find({'client_id': str(client_id)})
        
        return client[0] if len(client) > 0 else None


    def validate_client(self, db_connection: IConnection, client_id, client_secret):
        client = self.get_client(db_connection, client_id)
        if client and client['client_secret'] == client_secret:
            return True
        else:
            return False

