import os, time, requests
from flask import Blueprint, request, abort, jsonify, Response, send_file
from io import BytesIO
from db_management.mongodb_connection import MongoDBConnection
from service_locator import ServiceLocator

bp_profiles = Blueprint('profiles', __name__)


@bp_profiles.route("/user_register/<string:username>", methods=['POST'])
def register_user(username: str):
    credentials = request.headers['Authorization'].split(' ')
    if credentials[0] == 'Bearer' and len(credentials) > 1:
        token = credentials[1]
    else:
        return abort(401)
    locator = ServiceLocator()
    cfg_manager = locator.cfg_manager
    client_id = locator.token_manager.get_token_owner(MongoDBConnection(cfg_manager.mongo_address, cfg_manager.dbname, cfg_manager.at_collection), token)
    data = BytesIO(request.files.get('image').read())
    mdb = locator.mdb_connection(cfg_manager.dbname, cfg_manager.users_collection)
    locator.user_manager.create_user(mdb, username, data, client_id)
    
    return jsonify({'status': 200})#send_file(image, mimetype='image/jpeg', cache_timeout=-1)#abort(401)

@bp_profiles.route("/user_auth/<string:username>", methods=['Post'])
def authenticate(username: str):
    t1 = time.time()
    credentials = request.headers['Authorization'].split(' ')
    if credentials[0] == 'Bearer' and len(credentials) > 1:
        token = credentials[1]
    else:
        return abort(401)
    locator = ServiceLocator()
    cfg_manager = locator.cfg_manager
    mdb = MongoDBConnection(cfg_manager.mongo_address, cfg_manager.dbname, cfg_manager.at_collection)
    client_id = locator.token_manager.get_token_owner(mdb, token)
    if client_id == None:
        return abort(401)
    data = BytesIO(request.files.get('image').read())
    mdb = locator.mdb_connection(cfg_manager.dbname, cfg_manager.users_collection)
    t2 = time.time()
    is_authorized = locator.user_manager.authenticate_user(mdb, locator.auth_backend, username, data, client_id)
    t3 = time.time()

    #print("Auth time CPU: ", t2 - t1, ' Auth time GPU: ', t3 - t2)
    return jsonify({
        'status': 200,
        'authorization': 'granted' if is_authorized else 'denied'
    })

@bp_profiles.route("/user_update/<string:username>", methods=['PUT'])
def update_user(username: str):
    credentials = request.headers['Authorization'].split(' ')
    if credentials[0] == 'Bearer' and len(credentials) > 1:
        token = credentials[1]
    else:
        return abort(401)
    locator = ServiceLocator()
    cfg_manager = locator.cfg_manager
    mdb = MongoDBConnection(cfg_manager.mongo_address, cfg_manager.dbname, cfg_manager.at_collection)
    client_id = locator.token_manager.get_token_owner(mdb, token)
    if client_id == None:
        return abort(401)
    mdb = locator.mdb_connection(cfg_manager.dbname, cfg_manager.users_collection)
    count = 0
    data = request.files.get('image')
    new_username = request.args.get('new_username', None)
    if data is not None:
        count += locator.user_manager.update_user_image(mdb, username, BytesIO(data.read()), client_id).matched_count
    if new_username is not None:
        count += locator.user_manager.update_username(mdb, username, new_username, client_id).matched_count
    
    if count > 0:
        return jsonify({'status': 200})
    
    # If didn't succeed return error 404 (Not found)
    return abort(404)

@bp_profiles.route("/user_delete/<string:username>", methods=['DELETE'])
def delete_user(username: str):
    credentials = request.headers['Authorization'].split(' ')
    if credentials[0] == 'Bearer' and len(credentials) > 1:
        token = credentials[1]
    else:
        return abort(401)
    locator = ServiceLocator()
    cfg_manager = locator.cfg_manager
    mdb = MongoDBConnection(cfg_manager.mongo_address, cfg_manager.dbname, cfg_manager.at_collection)
    client_id = locator.token_manager.get_token_owner(mdb, token)
    if client_id == None:
        return abort(401)
    mdb = locator.mdb_connection(cfg_manager.dbname, cfg_manager.users_collection)
    num = locator.user_manager.delete_user(mdb, username, client_id).deleted_count
    
    if num > 0:
        return jsonify({'status': 200})

    # If didn't succeed return error 404 (Not found)
    return abort(404)
