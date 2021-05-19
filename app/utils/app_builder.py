#from managers import cfg_manager, usr_manager
from config.config_manager import ConfigLoader, JSONDataWrapper
from tokens.token_manager import TokenManager
from db_management.mongodb_connection import MongoDBConnection
from users.user_manager import UserManager
from service_locator import ServiceLocator
from authentication.auth_backend import AuthBackend
from clients.client_manager import ClientManager
from .ibuilder import IBuilder

from flask import Flask, redirect, json
from werkzeug.exceptions import HTTPException
import os

from api.authorization import bp_auth
from api.swagger_docs import bp_docs
from api.profiles import bp_profiles


class AppBuilder(IBuilder):
    def create_services(self, srv_locator: ServiceLocator):
        # Create interface services
        json_loader = ConfigLoader()
        cfg_manager = json_loader.loadJSON('../config/app_conf.json')
        usr_manager = UserManager()
        tm = TokenManager()
        clm = ClientManager()
        srv_locator(cfg_manager, tm, clm, usr_manager)
        setattr(srv_locator, 'mdb_connection', lambda db, collection: MongoDBConnection(cfg_manager.mongo_address, db, collection))
        setattr(srv_locator, 'auth_backend', AuthBackend())

        return srv_locator

    def create_flask(self, cfg_manager: JSONDataWrapper):
        # Create flask application
        path = os.getcwd()
        app = Flask(__name__, template_folder=path + '/templates', static_folder=path + '/static')
        app.register_blueprint(bp_auth, url_prefix='/api/v1.0/oauth')
        app.register_blueprint(bp_profiles, url_prefix='/api/v1.0')
        app.register_blueprint(bp_docs, url_prefix='/api/v1.0', template_folder='../templates', static_folder='../static')

        @app.route("/", methods=['GET', 'POST'])
        def root():
            # Make redirect to swagger-client
            return redirect(cfg_manager.flask_protocol + "://" + cfg_manager.host_address + '/api/v1.0/swagger-ui', code=308)
        
        @app.errorhandler(HTTPException)
        def handle_exception(error):
            """Return JSON instead of HTML for HTTP errors."""
            # start with the correct headers and status code from the error
            response = error.get_response()
            # replace the body with JSON
            response.data = json.dumps({
                "status": error.code,
                "error": error.name,
                "description": error.description,
            })
            response.content_type = "application/json"
            return response
        
        app.debug = cfg_manager.debug

        return app
