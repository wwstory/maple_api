from pymongo import MongoClient, IndexModel, ASCENDING
from pymongo.database import Database
from pydantic import BaseModel
import os, importlib
from collections import defaultdict
from inspect import isclass

from .db_adapter import DataBaseAdapter


class MongoAdapter(DataBaseAdapter):
    def __init__(self, url: str):
        client = MongoClient(url)
        self.db = client[url.split('/')[-1]]


    def get_db(self):
        return self.db


    def get_data(self, table_name, query):
        d = self.db[table_name].find_one({'id': query['id']})
        return d


    def get_datas(self, table_name, query):
        print('query:', query)
        l = self.db[table_name].find(query)
        return list(l)
    

    def create_data(self, table_name, data):
        ...
    

    def update_data(self, table_name, old_data, new_data):
        ...


    def delete_data(self, table_name, query):
        ...

