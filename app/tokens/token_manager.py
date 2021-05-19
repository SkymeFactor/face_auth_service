import os, time

from db_management.iconnection import IConnection
from .itoken import IToken
from utils.celery_tasks import remove_code, remove_access_token, remove_refresh_token


class TokenManager(IToken):
    def get_token_owner(self, db_connection: IConnection, token: str):
        client_id = None
        token = db_connection.find({'token': token})
        if len(token) > 0:
            client_id = token[0].get('client_id', None)
        
        return client_id

    def generate_code(self, db_connection: IConnection, client_id: str, expires_in: float):
        # Generate code and remember when it should be expired
        code = os.urandom(20).hex()
        expires_in = time.time() + expires_in
        # Create a record of generated code in database
        db_connection.insert({
            'code': str(code),
            'expires_in': expires_in,
            'client_id': client_id
        })
        # Set expiration time for this code
        remove_code.apply_async(args=(str(code), client_id), countdown=expires_in)

        return code

    def generate_tokens(self,
                atdb_connection: IConnection,
                rtdb_connection: IConnection,
                at_expires_in: float,
                rt_expires_in: float,
                client_id: str
        ):
        # Create new tokens
        access_token = os.urandom(20).hex()
        refresh_token = os.urandom(20).hex()
        # Set expiration time
        access_token_expires_in = time.time() + at_expires_in
        refresh_token_expires_in = time.time() + rt_expires_in
        # Update session storage with created tokens
        atdb_connection.insert({
            'token': str(access_token),
            'refresh_token': refresh_token,
            'expires_in': access_token_expires_in,
            'client_id': client_id
        })
        rtdb_connection.insert({
            'token': str(refresh_token),
            'expires_in': refresh_token_expires_in,
            'client_id': client_id
        })
        # Remove tokens from session storage after expiration
        remove_access_token.apply_async(args=(str(access_token), client_id), countdown=at_expires_in)
        remove_refresh_token.apply_async(args=(str(refresh_token), client_id), countdown=rt_expires_in)

        return access_token, refresh_token

    def update_tokens(self, db_connection: IConnection, refresh_token: str):
        pass
