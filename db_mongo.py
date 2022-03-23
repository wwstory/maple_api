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
        d = self.db[table_name].find_one(query)
        return d


    def get_data_by_id(self, table_name, query):
        d = self.get_data(table_name, {'id': query['id']})
        return d


    def get_datas(self, table_name, query):
        l = self.db[table_name].find(query)
        return list(l)
    

    def create_data(self, table_name, data):
        if isinstance(data, dict):
            ret = self.db[table_name].insert_one(data)
        elif isinstance(data, BaseModel):
            ret = self.db[table_name].insert_one(data.dict())
        else:
            raise
        return ret
    

    def update_data(self, table_name, old_data, new_data):
        ...


    def delete_data(self, table_name, query):
        d = self.db[table_name].delete_one(query)
        return d


    def delete_data_by_id(self, table_name, query):
        ret = self.delete_data(table_name, {'id': query['id']})
        return ret


def get_and_inc_collection_counter_id(db: Database, collection_name='test') -> int:
    result = db['counter_id'].find_one_and_update(
        {'collection': collection_name},    # 查询
        {'$inc': {'id': 1}},                # 递增字段
        upsert=True,                        # 如果不存在，将新建
        projection={'id': True, '_id': False},  # 返回的字段
        return_document=True,               # 返回递增前(False)，还是递增后(True)的结果
    )
    return result.get('id')


class GetIncCounterId:
    '''
    使用类包装get_collection_counter_id方法
    '''
    def __init__(self, db: Database, collection_name='test'):
        self.db = db
        self.collection_name = collection_name
    
    def get_id(self):
        result = self.db['counter_id'].find_one_and_update(
            {'collection': self.collection_name},
            {'$inc': {'id': 1}},
            upsert=True,
            projection={'id': True, '_id': False},
            return_document=True,
        )
        return result.get('id')


def get_collection_counter_id(db: Database, collection_name='test') -> int:
    result = db['counter_id'].find_one(
        {'collection': collection_name},    # 查询
        projection={'id': True, '_id': False},  # 返回的字段
    )
    return result.get('id')
