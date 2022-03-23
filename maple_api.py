from functools import wraps
from typing import List


class MapleApi:
    def __init__(
        self,
        backend,
        database_conf: dict,
        *,
        storage_conf: dict = None,
        database_id_auto_incr = True,
    ):
        '''
        database_conf: {
            'name': 'mongo',
            'url': '',
        }
        '''
        self.backend = backend
        self.api_dict = {}
        self.database_id_auto_incr = database_id_auto_incr

        if database_conf['name'] == 'mongo':
            from .db_mongo import MongoAdapter
            self.db_adapter = MongoAdapter(**database_conf)

        if storage_conf['name'] == 'minio':
            from .storage_minio import MinioAdapter
            self.sto_adapter = MinioAdapter(**storage_conf)


    def get_backend(self):
        return self.backend


    def get_db_client(self):
        return self.db_adapter.get_client()


    def get_api_dict(self):
        return self.api_dict


    def get(self, *args, **kwargs):
        def get_decorator(func):
            @self.backend.get(*args, **kwargs)
            @wraps(func)
            def func_wrap(*api_args, **api_kwargs):
                return func(*api_args, **api_kwargs)
            return func_wrap
        return get_decorator


    def post(self, *args, **kwargs):
        def post_decorator(func):
            @self.backend.post(*args, **kwargs)
            @wraps(func)
            def func_wrap(*api_args, **api_kwargs):
                return func(*api_args, **api_kwargs)
            return func_wrap
        return post_decorator


    def put(self, *args, **kwargs):
        def put_decorator(func):
            @self.backend.put(*args, **kwargs)
            @wraps(func)
            def func_wrap(*api_args, **api_kwargs):
                return func(*api_args, **api_kwargs)
            return func_wrap
        return put_decorator


    def delete(self, *args, **kwargs):
        def delete_decorator(func):
            @self.backend.delete(*args, **kwargs)
            @wraps(func)
            def func_wrap(*api_args, **api_kwargs):
                return func(*api_args, **api_kwargs)
            return func_wrap
        return delete_decorator


    def gen_api(
        self, 
        model_file_paths: List[str],
        set_unique: bool = True,
        set_foreign_key: bool = True,
    ):
        assert True, '应该被重写'



