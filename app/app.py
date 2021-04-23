import os, sys
import json
import time, base64, struct
import requests
from flask import Flask, jsonify, request, abort, render_template, redirect, Response
from mongo_helper import Mongo

# Load configuration file
conf = json.load(open("config/app_conf.json", 'r'))

# Create flask application
app = Flask(__name__)
mongo_client = Mongo(conf['mongo_dbname'], 'faces', conf['mongo_address'], 27017)
db = mongo_client[conf['mongo_dbname']]
faces_collection = db['faces']

session = {
    'access_tokens': {},
    'refresh_tokens': {},
    'codes': {}
}

@app.route("/", methods=['GET', 'POST'])
def root():
    # Redirect to swagger-client
    return redirect("http://" + conf['host_address'] + '/api/v1.0/swagger-ui', code=308)

@app.route("/api/v1.0/user_register/<string:username>", methods=['POST'])
def register_user(username: str):
    credentials = request.headers['Authorization'].split(' ')
    # In case of OAuth2.0 we satisfy the request
    if credentials[0] == 'Bearer':
        print(session[credentials[1]])
        if credentials[1] in session and session[credentials[1]] > time.time():
            # Create user profile and store it in database
            mongo_client.create_profile(username)
            return jsonify({"success": "registration request satisfied"})

        elif credentials[1] in session:
            # Remove expired token
            session.pop(credentials[1])
    
    return abort(401)

@app.route("/api/v1.0/user_auth/<string:username>", methods=['GET'])
def authenticate():

    return jsonify(
        {'hello': 'world'},
        faces_collection.find_one({"username": 'Sergei'})['faceprint']
    )

@app.route("/api/v1.0/user_update/<string:username>", methods=['PUT'])
def update_user(username: str):
    credentials = request.headers['Authorization'].split(' ')
    # In case of OAuth2.0 we satisfy the request
    if credentials[0] == 'Bearer':
        print(session[credentials[1]])
        if credentials[1] in session and session[credentials[1]] > time.time():
            # Update user profile in database
            mongo_client.update_profile(username)
            return jsonify({"success": "update request satisfied"})

        elif credentials[1] in session:
            # Remove expired token
            session.pop(credentials[1])
    
    return abort(401)

@app.route("/api/v1.0/user_delete/<string:username>", methods=['DELETE'])
def delete_user(username: str):
    credentials = request.headers['Authorization'].split(' ')
    # In case of OAuth2.0 we satisfy the request
    if credentials[0] == 'Bearer':
        if credentials[1] in session and session[credentials[1]] > time.time():
            # Delete user profile from database
            mongo_client.delete_profile(username)
            return jsonify({"success": "deletion request satisfied"})

        elif credentials[1] in session:
            # Remove expired token
            session.pop(credentials[1])
    
    # If didn't succeed return error 401 (Not authorized)
    return abort(401)

@app.route("/api/v1.0/oauth/authorize", methods=['POST'])
def authorize():
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    user = mongo_client.get_user(client_id)

    if redirect_uri.startswith(user['trusted_domain']):
        code = os.urandom(20).hex()
        expires_in = time.time() + 3600
        # Must be shceduled for removal <----------------------------
        session['codes'].update({code: expires_in})
        post_url = redirect_uri + "?code=" + code
        requests.post(post_url)
        return Response(status=200)
    else:
        return abort(401)


@app.route("/api/v1.0/oauth/access_token", methods=['GET'])
def get_token():
    # Extract credentials from query parameters
    client_id = request.args.get('client_id')
    client_secret = request.args.get('client_secret')
    code = request.args.get('code')
    redirect_uri = request.args.get('redirect_uri')

    # Check if we are deployed locally or remotely and get User IP
    if 'X-Forwarded-For' in request.headers:
        proxy_data = request.headers['X-Forwarded-For']
        ip_list = proxy_data.split(',')
        user_ip = ip_list[0]  # first address in list is User IP
    # For local development
    else:
        user_ip = request.remote_addr

    # Get all users that are stored in database
    user = mongo_client.get_user(client_id)
    response = {}

    # In case of client_id, client_secret and code are all matching
    if user.get('client_id') == int(client_id) and user.get('client_secret') == client_secret and code in session['codes']:
        if session['codes'].get(code) > time.time():
            # Set expiration time
            access_token_expires_in = time.time() + 3600
            refresh_token_expires_in = time.time() + 172800
            # Create new tokens
            access_token = os.urandom(20).hex()
            refresh_token = os.urandom(20).hex()
            # Update session storage with created tokens
            session['access_tokens'].update({
                str(access_token): {
                    'expires_in': access_token_expires_in
                }
            })
            session['refresh_tokens'].update({
                str(refresh_token): {
                    'expires_in': refresh_token_expires_in,
                    'ip': user_ip
                }
            })
            response = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": 3600,
                "user_id": user.get('_id')
            }
            requests.post(redirect_uri, json=response)
            return Response(status=200)#jsonify({'status': "OK"})
        else:
            response = {"status": "error: code is out of date"}
    else:
        response = {"status": "error: invalid_credentials"}

    # Delete temporary auth code
    session['codes'].pop(code, None)
        
    requests.post(redirect_uri, json=response)
    # If didn't succeed return error 401 (Not authorized)
    return abort(401)

@app.route("/api/v1.0/oauth/expire_token/<string:token>", methods=['DELETE'])
def expire_token(token: str):
    #print(request.headers['Authorization'].split(' ')[1])
    if token in session:
        session.pop(token)
    return jsonify({"success": "token expiration succeeded"})

@app.route("/api/v1.0/oauth/refresh_token/<string:token>", methods=['PUT'])
def refresh_token(token: str):
    pass

@app.route("/api/v1.0/swagger.json", methods=['GET'])
def get_swagger_json():
    print(os.getcwd())
    with open("app/static/swagger.json") as f:
        swagger_data = json.load(f)
    swagger_data.update(
        {"host": conf['host_address']}
    )
    return jsonify(swagger_data)


@app.route('/api/v1.0/swagger-ui', methods=['GET'])
def get_swagger():
    # Render swagger-ui page
    url_prefix = 'http://' + conf['host_address']
    return render_template(
        template_name_or_list='swaggerui.html',
        css=f'{url_prefix}/static/css/swagger-ui.css',
        fav32=f'{url_prefix}/static/img/favicon-32x32.png',
        fav16=f'{url_prefix}/static/img/favicon-16x16.png',
        bundle_js=f'{url_prefix}/static/js/swagger-ui-bundle.js',
        standalone_preset_js=f'{url_prefix}/static/js/swagger-ui-standalone-preset.js',
        swagger_json=f'{url_prefix}/api/v1.0/swagger.json'
    )


if __name__ == '__main__':
    app.run(debug=conf['debug'], host=conf['flask_address'], port=conf['flask_port'])