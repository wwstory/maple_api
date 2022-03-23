from fastapi import APIRouter, Request, Path
from typing import List, Any, Dict, Optional
from pydantic import BaseModel
from pydantic.fields import Undefined
from fastapi.params import ParamTypes, Param
from functools import wraps

from .maple_api import MapleApi
from . import utils


class MFastAPI(MapleApi):
    def __init__(
        self,
        backend,
        database_url: str,
        *,
        database_id_auto_incr = True,
        prefix: str = ''
    ):
        super().__init__(
            backend,
            database_url,
            database_id_auto_incr = database_id_auto_incr,
        )
        self.prefix = prefix
        print('backend: fastapi')



    def get_api_dict(self):
        return {(router.path, list(router.methods)[0]): router.endpoint for router in self.backend.routes}


    def gen_api(
        self, 
        model_file_paths: List[str],
        set_unique: bool = True,
        set_foreign_key: bool = True,
    ):
        models = utils.get_models_from_paths(model_file_paths)
        # print(models)
        self.gen_simple_api(models)


    def gen_simple_api(
        self,
        models,
    ):
        for m in models:
            # prepare
            # print(m)
            table_name = utils.conv_under_line(m.__name__.split('.')[-1])
            router = APIRouter(tags=[table_name])

            # build model
            # print(path)
            model_in = utils.build_new_model_from_pydantic_model_by_flag(m, flag='x_in', suffix='_In')
            if utils.has_flag_from_pydantic_model(m, flag='x_exclude_out'):
                model_out = utils.build_new_model_from_pydantic_model_by_flag(m, flag='x_exclude_out', reverse=True, suffix='_Out')
            else:
                model_out = utils.build_new_model_from_pydantic_model_by_flag(m, flag='x_out', suffix='_Out')
            model_query = utils.build_new_model_from_pydantic_model_by_flag(m, flag='x_query', suffix='_Query', is_optional=True)
            model_put = utils.build_new_model_from_pydantic_model_by_flag(m, flag='x_update', suffix='_Put', is_optional=True)

            # gen api
            path = self.prefix + '/' + table_name + '/{id}'
            self.gen_get_api(
                router,
                table_name,
                router_kwargs = {
                    'path': path,
                    'response_model': model_out,
                },
            )

            path = self.prefix + '/' + table_name + 's'
            self.gen_get_many_api(
                router,
                table_name,
                model_query,
                router_kwargs = {
                    'path': path,
                    'response_model': List[model_out],
                },
            )

            path = self.prefix + '/' + table_name
            self.gen_post_api(
                router,
                table_name,
                model_in,
                m,
                router_kwargs = {
                    'path': path,
                    'response_model': model_out,
                },
            )

            path = self.prefix + '/' + table_name + '/{id}'
            self.gen_delete_api(
                router,
                table_name,
                router_kwargs = {
                    'path': path,
                },
            )

            path = self.prefix + '/' + table_name + '/{id}'
            self.gen_put_api(
                router,
                table_name,
                model_put,
                router_kwargs = {
                    'path': path,
                },
            )

            # finish
            self.backend.include_router(router)


    def gen_complex_api_for_mongo(
        self,
        models,
    ):
        for m in models:
            field_dict = utils.get_fields_dict_from_pydantic_model_by_flag(m, flag='x_foreign_key')
            print(field_dict)


    def gen_get_api(
        self,
        router,
        table_name: str = None,
        *,
        router_kwargs: dict,
        request = None,
        x_extra_datas = None,
    ):
        # @self.backend.get(**router_kwargs)
        # def get_func(id: int = Path(...)):
        #     return self.db_adapter.get_data(table_name, query={'id': id})
        def get_func(
            request: Request,
            id: int = Path(...),
            x_extra_datas = XParam(),
        ):
            query = x_extra_datas.get('query', {})
            query.update({'id': id})
            return self.db_adapter.get_data_by_id(table_name, query=query)
        router.get(**router_kwargs)(get_func)


    def gen_get_many_api(
        self,
        router,
        table_name: str = None,
        model_query: BaseModel = None,
        *,
        router_kwargs: dict,
        request = None,
        x_extra_datas = None,
    ):
        @router.get(**router_kwargs)
        @x_set_query(model_query=model_query)
        def get_many_func(
            request: Request,
            x_extra_datas = XParam(),
        ):
            query = x_extra_datas.get('query', {})
            return self.db_adapter.get_datas(table_name, query=query)


    def gen_post_api(
        self,
        router,
        table_name: str = None,
        model_in: BaseModel = None,
        model_db: BaseModel = None,
        *,
        router_kwargs: dict,
        request = None,
        x_extra_datas = None,
    ):
        try:    # mongo数据库
            from pymongo.database import Database
            if isinstance(self.get_db(), Database):
                @router.post(**router_kwargs)
                @x_set_mongo_in(database=self.get_db(), model_db=model_db, database_id_auto_incr=self.database_id_auto_incr)
                def post_func(
                    m: model_in,
                    request: Request,
                    x_extra_datas = XParam(),
                ):
                    self.db_adapter.create_data(table_name, m)
                    return model_db(**m.dict())
        except:
            ...


    def gen_delete_api(
        self,
        router,
        table_name: str = None,
        *,
        router_kwargs: dict,
        request = None,
        x_extra_datas = None,
    ):
        @router.delete(**router_kwargs)
        def delete_func(
            request: Request,
            id: int = Path(...),
            x_extra_datas = XParam(),
        ):
            query = x_extra_datas.get('query', {})
            query.update({'id': id})
            self.db_adapter.delete_data_by_id(table_name, query)
            return {'id': id}


    def gen_put_api(
        self,
        router,
        table_name: str = None,
        model_put: BaseModel = None,
        *,
        router_kwargs: dict,
        request = None,
        x_extra_datas = None,
    ):
        @router.put(**router_kwargs)
        def put_func(
            request: Request,
            m: model_put,
            id: int = Path(...),
            x_extra_datas = XParam(),
        ):
            query = x_extra_datas.get('query', {})
            query.update({'id': id})
            self.db_adapter.update_data_by_id(table_name, query, m)
            return {}


class XParamClass(Param):
    in_: ParamTypes = ParamTypes.query

    def __init__(
        self,
        default: Any,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = Undefined,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        **extra: Any,
    ):
        super().__init__(
            default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            deprecated=deprecated,
            example=example,
            examples=examples,
            include_in_schema=include_in_schema,
            **extra,
        )


def XParam(
    default: dict = {},
    *,
    alias: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
    example: Any = Undefined,
    examples: Optional[Dict[str, Any]] = None,
    deprecated: Optional[bool] = None,
    include_in_schema: bool = False,
    **extra: Any,
) -> Any:
    return XParamClass(
        default,
        alias=alias,
        title=title,
        description=description,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        regex=regex,
        example=example,
        examples=examples,
        deprecated=deprecated,
        include_in_schema=include_in_schema,
        **extra,
    )


def get_request(request_dict):
    for _, v in request_dict.items():
        if isinstance(v, Request):
            return v
    print('未传入Reuqest类型的参数!')
    return None


def x_set_query(
    model_query: BaseModel = None,
):
    def func_decorator(func):
        @wraps(func)
        async def func_wrap(*args, **kwargs):
            if 'x_extra_datas' in kwargs:
                kwargs['x_extra_datas'] = {}    # new 一个字典对象，避免被传参污染
                x_extra_datas = kwargs.get('x_extra_datas', None)

                request = get_request(kwargs)
                query_params = dict(request.query_params)

                x_extra_datas['query'] = model_query(**query_params).dict(exclude_none=True)

            # print(kwargs)

            ret_api = func(*args, **kwargs)
            return ret_api
        return func_wrap
    return func_decorator


def x_set_mongo_in(
    database,
    model_db,
    database_id_auto_incr = True,
):
    def func_decorator(func):
        @wraps(func)
        async def func_wrap(*args, **kwargs):
            if 'm' in kwargs:
                try:    # 如果是mongo数据库，且带id字段，使用自增
                    from pymongo.database import Database
                    if isinstance(database, Database):
                        if database_id_auto_incr:
                            def get_and_inc_collection_counter_id(db: Database, collection_name='test') -> int:
                                result = db['counter_id'].find_one_and_update(
                                    {'collection': collection_name},    # 查询
                                    {'$inc': {'id': 1}},                # 递增字段
                                    upsert=True,                        # 如果不存在，将新建
                                    projection={'id': True, '_id': False},  # 返回的字段
                                    return_document=True,               # 返回递增前(False)，还是递增后(True)的结果
                                )
                                return result.get('id')
                        
                            m = kwargs.get('m', None)
                            if 'id' not in m.dict() and 'id' in model_db.schema()['properties']:
                                new_m = model_db(**m.dict(), id=get_and_inc_collection_counter_id(database, model_db.__name__))
                            elif 'id' in new_m.dict():
                                new_m = model_db(**m.dict())
                                new_m.id = get_and_inc_collection_counter_id(database, model_db.__name__)
                            kwargs['m'] = new_m

                except:
                    ...

                # print(kwargs)

            ret_api = func(*args, **kwargs)
            return ret_api
        return func_wrap
    return func_decorator
