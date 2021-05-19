from db_management.iconnection import IConnection
from authentication.iauth import IAuth
from .iuser import IUser
from io import BytesIO
from bson import Binary


class UserManager(IUser):
    def authenticate_user(self, db_connection: IConnection, auth_backend: IAuth, username: str, data: BytesIO, client_id: str):
        img1 = data
        user = self.find_user(db_connection, username, client_id)
        if user is not None:
            img2 = BytesIO(user['image'])
            result = auth_backend.compare(img1, img2)
            return result
        
        return False
    

    def find_user(self, db_connection: IConnection, username: str, client_id: str):
        user = db_connection.find({'username': username, 'client_id': client_id})

        return user[0] if len(user) > 0 else None
    
    def create_user(self, db_connection: IConnection, username: str, data: BytesIO, client_id: str):
        img = Binary(data.read())
        _id = db_connection.insert({'username': username, 'image': img, 'client_id': client_id})

        return _id
    
    def update_username(self, db_connection: IConnection, username: str, new_username: str, client_id: str):
        _id = db_connection.update({'username': username, 'client_id': client_id}, {'$set': {'username': new_username}})

        return _id

    def update_user_image(self, db_connection: IConnection, username: str, data: BytesIO, client_id: str):
        img = Binary(data.read())
        _id = db_connection.update({'username': username, 'client_id': client_id}, {'$set': {'image': img}})
        
        return _id

    def delete_user(self, db_connection: IConnection, username: str, client_id: str):
        _num = db_connection.delete({'username': username, 'client_id': client_id})

        return _num
    