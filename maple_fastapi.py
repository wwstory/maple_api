from fastapi import Request, Path
from typing import List, Any, Dict, Optional
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
        model_exclude_out = [],
    ):
        super().__init__(
            backend,
            database_url,
            model_exclude_out=model_exclude_out,
        )
        print('backend: fastapi')


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
            # print(m)
            table_name = utils.conv_under_line(m.__name__.split('.')[-1])
            # print(path)
            model_in = utils.get_new_model_from_pydantic_model_by_flag(m, flag='x_in')
            if self.model_exclude_out:
                model_out = utils.get_new_model_from_pydantic_model_by_flag(m, flag='x_out')
            else:
                model_out = utils.get_new_model_from_pydantic_model_by_exclude_flag(m, exclude_flag='x_exclude_out')

            path = '/api/' + table_name + '/{id}'
            self.gen_get_one_api(
                table_name,
                router_kwargs = {
                    'path': path,
                    'response_model': model_out,
                },
            )


            path = '/api/' + table_name + 's'
            self.gen_get_many_api(
                table_name,
                router_kwargs = {
                    'path': path,
                    'response_model': List[model_out],
                },
            )


    def gen_complex_api_for_mongo(
        self,
        models,
    ):
        for m in models:
            field_dict = utils.get_fields_dict_from_pydantic_model_by_flag(m, flag='x_foreign_key')
            print(field_dict)


    def gen_get_one_api(
        self,
        table_name = None,
        *,
        router_kwargs: dict,
        request = None,
        x_extra_datas = None,
    ):
        # @self.backend.get(**router_kwargs)
        # def get_func(id: int = Path(...)):
        #     return self.db_adapter.get_data(table_name, query={'id': id})
        def get_func(id: int = Path(...)):
            return self.db_adapter.get_data(table_name, query={'id': id})
        self.backend.get(**router_kwargs)(get_func)


    def gen_get_many_api(
        self,
        table_name = None,
        *,
        router_kwargs: dict,
        request = None,
        x_extra_datas = None,
    ):
        @self.backend.get(**router_kwargs)
        @x_set_query
        def get_func(
            request: Request,
            x_extra_datas = XParam(),
        ):
            query = x_extra_datas.get('query', {})
            return self.db_adapter.get_datas(table_name, query=query)


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
    for k, v in request_dict.items():
        if isinstance(v, Request):
            return v
    print('未传入Reuqest类型的参数!')
    return None


def x_set_query(func):
    @wraps(func)
    async def wrap_func(*args, **kwargs):
        if 'x_extra_datas' in kwargs:
            kwargs['x_extra_datas'] = {}    # new 一个字典对象，避免被传参污染
            x_extra_datas = kwargs.get('x_extra_datas', None)

            request = get_request(kwargs)
            query_params = dict(request.query_params)

        # print(kwargs)

        ret_api = func(*args, **kwargs)
        return ret_api
    return wrap_func
