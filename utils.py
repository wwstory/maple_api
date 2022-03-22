from pydantic import BaseModel
import importlib
import inspect
import copy
from typing import List


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


def get_fields_from_pydantic_model_by_flag(m: BaseModel, flag='x_unique') -> dict:
    '''
    从Pydantic模型中获取，字段带有flag标识的字段信息
    '''
    field_dict = {}
    if inspect.isclass(m) and issubclass(m, BaseModel):
        j = getattr(m, 'schema')()
        for field, prop in j['properties'].items():
            if flag in prop:
                field_dict[field] = prop
    return field_dict


def get_fields_dict_from_pydantic_model_by_flag(m: BaseModel, flag='x_unique') -> dict:
    '''
    从Pydantic模型中获取，字段带有flag标识的字段名
    '''
    field_dict = {}
    if inspect.isclass(m) and issubclass(m, BaseModel):
        j = getattr(m, 'schema')()
        for field, prop in j['properties'].items():
            if flag in prop:
                field_dict[field] = prop[flag]
    return field_dict


def get_src_from_pydantic_model_by_flag(m: BaseModel, flag='x_in', num_skip_line=1) -> list:
    '''
    从Pydantic模型中获取，字段带有flag标识的源码
    '''
    src_lines = inspect.getsourcelines(m)[0]
    new_src_lines = [s.strip().split('=')[0] for s in src_lines[num_skip_line:] if flag in s and not s.strip().startswith('class') and ':' in s.split('=')[0]]
    return new_src_lines


def get_src_from_pydantic_model_by_exclude_flag(m: BaseModel, exclude_flag='x_exclude_out', num_skip_line=1) -> list:
    '''
    从Pydantic模型中获取，字段不带有exclude_flag标识的源码
    '''
    src_lines = inspect.getsourcelines(m)[0]
    new_src_lines = [s.strip().split('=')[0] for s in src_lines[num_skip_line:] if exclude_flag not in s and not s.strip().startswith('class') and ':' in s.split('=')[0]]
    return new_src_lines


def get_init_model_source_code():
    src_code = ''
    src_code += 'from pydantic import BaseModel\n'
    src_code += 'from typing import *\n'
    return src_code


def get_new_model_from_pydantic_model_by_flag(m: BaseModel, flag='x_in'):
    new_src_lines = get_src_from_pydantic_model_by_flag(m, flag=flag)

    if not new_src_lines:
        return None

    new_model_name = f'{m.__name__}In'

    src_code = get_init_model_source_code()
    src_code += f'class {new_model_name}(BaseModel):\n'
    for line in new_src_lines:
        src_code += f'\t{line}\n'

    scope = {}
    exec(src_code, scope)
    return scope[new_model_name]


def get_new_model_from_pydantic_model_by_exclude_flag(m: BaseModel, exclude_flag='x_exclude_out'):
    new_src_lines = get_src_from_pydantic_model_by_exclude_flag(m, exclude_flag=exclude_flag)

    if not new_src_lines:
        return None

    new_model_name = f'{m.__name__}In'

    src_code = get_init_model_source_code()
    src_code += f'class {new_model_name}(BaseModel):\n'
    for line in new_src_lines:
        src_code += f'\t{line}\n'

    print(src_code)
    scope = {}
    exec(src_code, scope)
    return scope[new_model_name]


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
