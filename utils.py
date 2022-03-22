import pydantic
from pydantic import BaseModel
import importlib
import inspect
import copy
from typing import List, Optional


def get_models_from_paths(model_file_paths) -> list:
    '''
    从模型路径中，动态导入BaseModel
    '''
    models = []
    for model_file_path in model_file_paths:
        module = importlib.import_module(model_file_path)
        models.extend([
            m 
            for m in [getattr(module, mod) for mod in dir(module)] 
            if inspect.isclass(m) and issubclass(m, BaseModel) and m.__name__ != 'BaseModel'
        ])
    return models


def get_fields_from_pydantic_model(m: BaseModel) -> dict:
    '''
    从Pydantic模型中获取所有字段信息
    '''
    field_dict = {}
    if inspect.isclass(m) and issubclass(m, BaseModel):
        j = getattr(m, 'schema')()
        for field, prop in j['properties'].items():
            field_dict[field] = prop
    return field_dict


def get_fields_from_pydantic_model_by_flag(m: BaseModel, flag='x_unique') -> dict:
    '''
    从Pydantic模型中获取，字段带有flag标识的字段信息
    '''
    all_field_dict = get_fields_from_pydantic_model(m)
    return {field: prop for field, prop in all_field_dict.items() if flag in prop}


def get_fields_flag_info_from_pydantic_model_by_flag(m: BaseModel, flag='x_unique') -> dict:
    '''
    从Pydantic模型中获取，字段带有flag标识信息
    '''
    all_field_dict = get_fields_from_pydantic_model(m)
    return {field: prop[flag] for field, prop in all_field_dict.items() if flag in prop}


def get_fields_name_from_pydantic_model_by_flag(m: BaseModel, flag='x_unique', *, reverse=False) -> list:
    '''
    从Pydantic模型中获取，字段带/不带有flag标识的字段名
    '''
    all_field_dict = get_fields_from_pydantic_model(m)
    if reverse:
        return [field for field, prop in all_field_dict.items() if flag not in prop]
    else:
        return [field for field, prop in all_field_dict.items() if flag in prop]


def build_new_model_from_pydantic_model_by_flag(m: BaseModel, flag='x_in', *, reverse=False, suffix='In', is_optional=False):
    '''
    从旧模型中，将带/不带有flag标志的字段构建新模型
    '''
    new_model_name = f'{m.__name__}{suffix}'
    fields = get_fields_name_from_pydantic_model_by_flag(m, flag=flag)

    if reverse:
        sub_model = pydantic_subclass(m, new_model_name, exclude_fields=fields)
    else:
        sub_model = pydantic_subclass(m, new_model_name, include_fields=fields)

    if is_optional:
        class tmp_model(sub_model, metaclass=AllOptional):
            ...
        sub_model = tmp_model
    return sub_model


def has_flag_from_pydantic_model(m: BaseModel, flag='x_exclude_out', *, reverse=False):
    '''
    模型字段是否存在flag标志
    '''
    fields = get_fields_name_from_pydantic_model_by_flag(m, flag=flag, reverse=reverse)
    return bool(fields)


def get_x_config_from_pydantic_model(m: BaseModel, attr='query'):
    '''
    从Pydantic的X_Config中获取属性
    '''
    if inspect.isclass(m) and issubclass(m, BaseModel):
        return getattr(m, attr) if hasattr(m, attr) else None
    return None


def conv_x_config_query(config):
    pass


def conv_under_line(s: str):
    ns = ''
    for i, c in enumerate(s):
        ns += f'_{c.lower()}' if c.isupper() and i != 0 else c.lower()
    return ns


# ref: https://orion-docs.prefect.io/api-ref/orion/utilities/schemas/
# def pydantic_subclass(
#     base: BaseModel,
#     name: str = None,
#     include_fields: List[str] = None,
#     exclude_fields: List[str] = None,
# ) -> BaseModel:
#     """Creates a subclass of a Pydantic model that excludes certain fields.
#     Pydantic models use the __fields__ attribute of their parent class to
#     determine inherited fields, so to create a subclass without fields, we
#     temporarily remove those fields from the parent __fields__ and use
#     `create_model` to dynamically generate a new subclass.

#     Args:
#         base (pydantic.BaseModel): a Pydantic BaseModel
#         name (str): a name for the subclass. If not provided
#             it will have the same name as the base class.
#         include_fields (List[str]): a set of field names to include.
#             If `None`, all fields are included.
#         exclude_fields (List[str]): a list of field names to exclude.
#             If `None`, no fields are excluded.

#     Returns:
#         pydantic.BaseModel: a new model subclass that contains only the specified fields.

#     Example:
#         To subclass a model with a subset of fields:
#         ```python
#         class Parent(pydantic.BaseModel):
#             x: int = 1
#             y: int = 2

#         Child = pydantic_subclass(Parent, 'Child', exclude_fields=['y'])
#         assert hasattr(Child(), 'x')
#         assert not hasattr(Child(), 'y')
#         ```

#         To subclass a model with a subset of fields but include a new field:
#         ```python
#         class Child(pydantic_subclass(Parent, exclude_fields=['y'])):
#             z: int = 3

#         assert hasattr(Child(), 'x')
#         assert not hasattr(Child(), 'y')
#         assert hasattr(Child(), 'z')
#         ```
#     """

#     # collect field names
#     field_names = set(include_fields or base.__fields__)
#     excluded_fields = set(exclude_fields or [])
#     if field_names.difference(base.__fields__):
#         raise ValueError(
#             "Included fields not found on base class: "
#             f"{field_names.difference(base.__fields__)}"
#         )
#     elif excluded_fields.difference(base.__fields__):
#         raise ValueError(
#             "Excluded fields not found on base class: "
#             f"{excluded_fields.difference(base.__fields__)}"
#         )
#     field_names.difference_update(excluded_fields)

#     # create a new class that inherits from `base` but only contains the specified
#     # pydantic __fields__
#     new_cls = type(
#         name or base.__name__,
#         (base,),
#         {
#             "__fields__": {
#                 k: copy.copy(v) for k, v in base.__fields__.items() if k in field_names
#             },
#         },
#     )

#     return new_cls


def pydantic_subclass(
    base: BaseModel,
    name: str = None,
    include_fields: List[str] = None,
    exclude_fields: List[str] = None,
) -> BaseModel:
    field_names = set([] if include_fields == [] else include_fields or base.__fields__)
    excluded_fields = set(exclude_fields or [])
    if field_names.difference(base.__fields__):
        raise ValueError(
            "Included fields not found on base class: "
            f"{field_names.difference(base.__fields__)}"
        )
    elif excluded_fields.difference(base.__fields__):
        raise ValueError(
            "Excluded fields not found on base class: "
            f"{excluded_fields.difference(base.__fields__)}"
        )
    field_names.difference_update(excluded_fields)

    # create a new class that inherits from `base` but only contains the specified
    # pydantic __fields__

    new_cls = type(
        name or base.__name__,
        (base,),
        {
            "__fields__": {
                k: copy.copy(v) for k, v in base.__fields__.items() if k in field_names
            },
        },
    )

    return new_cls


# ref: https://stackoverflow.com/questions/67699451/make-every-fields-as-optional-with-pydantic
class AllOptional(pydantic.main.ModelMetaclass):
    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
        namespaces['__annotations__'] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)
