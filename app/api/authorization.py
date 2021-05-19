import os, time, requests
from flask import Blueprint, request, abort, jsonify, Response
from utils.celery_tasks import remove_code, remove_access_token, remove_refresh_token
from service_locator import ServiceLocator
from db_management.mongodb_connection import MongoDBConnection

bp_auth = Blueprint('auth', __name__)

@bp_auth.route("/authorize", methods=['GET'])
def authorize():
    # Extract query arguments
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    # Get user data for client_id
    db = ServiceLocator().mdb_connection(ServiceLocator().cfg_manager.dbname, ServiceLocator().cfg_manager.clients_collection)
    user = ServiceLocator().client_manager.get_client(db, client_id)

    # Make sure that redirect domain is trusted
    if redirect_uri.startswith(user['trusted_domain']):
        # Generate code and remember when it should be expired
        code = os.urandom(20).hex()
        expires_in = time.time() + ServiceLocator().cfg_manager.code_expire_time
        # Create a record of generated code in database
        mdb = MongoDBConnection(ServiceLocator().cfg_manager.mongo_address, ServiceLocator().cfg_manager.dbname, ServiceLocator().cfg_manager.codes_collection)
        mdb.insert({'code': str(code), 'expires_in': expires_in, 'client_id': client_id})
        # Set expiration time for this code
        remove_code.apply_async(args=(str(code), client_id), countdown=ServiceLocator().cfg_manager.code_expire_time)
        # Form post reqeust with code as query parameter
        post_url = redirect_uri + "?code=" + code
        requests.post(post_url)

        return jsonify({'satus': 200, 'description': 'success'})

    return abort(401)


@bp_auth.route("/access_token", methods=['GET'])
def get_token():
    # Extract credentials from query parameters
    client_id = request.args.get('client_id')
    client_secret = request.args.get('client_secret')
    code = request.args.get('code')
    redirect_uri = request.args.get('redirect_uri')

    # Get all users that are stored in database
    user = ServiceLocator().client_manager.get_client(ServiceLocator().mdb_connection(ServiceLocator().cfg_manager.dbname, ServiceLocator().cfg_manager.clients_collection), client_id)
    response = {}
    print(user)

    # Verify code with those are in database
    verified_codes = ServiceLocator().mdb_connection(ServiceLocator().cfg_manager.dbname, ServiceLocator().cfg_manager.codes_collection).find({'code': code})
    # In case of client_id, client_secret and code are all matching
    if int(user.get('client_id')) == int(client_id) and user.get('client_secret') == client_secret:
        if len(verified_codes) > 0:
            tm = ServiceLocator().token_manager
            access_token, refresh_token = tm.generate_tokens(
                ServiceLocator().mdb_connection(ServiceLocator().cfg_manager.dbname, ServiceLocator().cfg_manager.at_collection),
                ServiceLocator().mdb_connection(ServiceLocator().cfg_manager.dbname, ServiceLocator().cfg_manager.rt_collection),
                ServiceLocator().cfg_manager.access_token_expire_time,
                ServiceLocator().cfg_manager.refresh_token_expire_time,
                client_id
            )
            
            response = {
                "status": "success",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": ServiceLocator().cfg_manager.access_token_expire_time,
                "user_id": user.get('client_id')
            }
            requests.post(redirect_uri, json=response)

            # Delete temporary auth code
            ServiceLocator().mdb_connection(ServiceLocator().cfg_manager.dbname, ServiceLocator().cfg_manager.codes_collection).delete({'code': code})
            
            return jsonify({'satus': 200, 'description': 'success'})
        else:
            response = {"status": "error: code is not valid"}
    else:
        response = {"status": "error: invalid_credentials"}

        
    requests.post(redirect_uri, json=response)
    # If didn't succeed return error 401 (Not authorized)
    return abort(401)

# Deprecated because of potential vulnurability
@bp_auth.route("/revoke_token/<string:token>", methods=['DELETE'])
def revoke_token(token: str):
    return jsonify({'status': "failure", 'reason': "this method is deprecated"})

@bp_auth.route("/refresh_token/<string:token>", methods=['PUT'])
def refresh_token(token: str):
    # Extract credentials from query parameters
    client_id = request.args.get('client_id')
    client_secret = request.args.get('client_secret')
    redirect_uri = request.args.get('redirect_uri')
    
    locator = ServiceLocator()
    cfg_manager = locator.cfg_manager
    # Get all users that are stored in database
    user = locator.client_manager.get_client(locator.mdb_connection(cfg_manager.dbname, cfg_manager.clients_collection), client_id)
    response = {}

    # Verify refresh token with those are in database
    verified_tokens = locator.mdb_connection(cfg_manager.dbname, cfg_manager.rt_collection).find({'token': str(token)})
    # Delete session with THIS refresh token
    locator.mdb_connection(cfg_manager.dbname, cfg_manager.at_collection).delete({'refresh_token': str(token), 'client_id': client_id})
    locator.mdb_connection(cfg_manager.dbname, cfg_manager.rt_collection).delete({'token': str(token), 'client_id': client_id})

    if int(user.get('client_id')) == int(client_id) and user.get('client_secret') == client_secret:
        if len(verified_tokens) > 0:
            tm = locator.token_manager
            access_token, refresh_token = tm.generate_tokens(
                locator.mdb_connection(cfg_manager.dbname, cfg_manager.at_collection),
                locator.mdb_connection(cfg_manager.dbname, cfg_manager.rt_collection),
                locator.cfg_manager.access_token_expire_time,
                locator.cfg_manager.refresh_token_expire_time,
                client_id
            )

            response = {
                "status": "success",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": locator.cfg_manager.access_token_expire_time,
                "user_id": user.get('client_id')
            }
            requests.post(redirect_uri, json=response)

            return jsonify({'satus': 200, 'description': 'success'})
        else:
            # Delete all active sessions because of potential hack
            locator.mdb_connection(cfg_manager.dbname, cfg_manager.at_collection).delete({'client_id': client_id})
            locator.mdb_connection(cfg_manager.dbname, cfg_manager.rt_collection).delete({'client_id': client_id})

            response = {"status": "error: refresh token is invalid"}
    else:
        response = {"status": "error: invalid_credentials"}
    

    requests.post(redirect_uri, json=response)
    
    # If didn't succeed return error 401 (Not authorized)
    return abort(401)