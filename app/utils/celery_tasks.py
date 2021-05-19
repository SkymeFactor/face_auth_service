from celery import Celery
from config.config_manager import ConfigLoader, JSONDataWrapper
from pymongo import MongoClient

cfg_manager = ConfigLoader().loadJSON('../config/app_conf.json')
celery = Celery('tasks', backend=cfg_manager.celery_backend, broker=cfg_manager.celery_broker)

@celery.task
def remove_code(code: str, client_id: str):
    """
    It's strictly necessarry to have a new instance of DB client 
    for each function because pymongo.MongoClient() is NOT fork-safe
    """
    db = MongoClient(cfg_manager.mongo_address)[cfg_manager.dbname]
    db[cfg_manager.codes_collection].delete_one({'code': code, 'client_id': client_id})

@celery.task
def remove_access_token(access_token: str, client_id: str):
    db = MongoClient(cfg_manager.mongo_address)[cfg_manager.dbname]
    db[cfg_manager.at_collection].delete_one({"token": access_token, 'client_id': client_id})

@celery.task
def remove_refresh_token(refresh_token: str, client_id: str):
    db = MongoClient(cfg_manager.mongo_address)[cfg_manager.dbname]
    db[cfg_manager.rt_collection].delete_one({"token": refresh_token, 'client_id': client_id})

