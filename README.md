# maple_api


## example

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
import os
from typing import List

from maple_api.maple_fastapi import MFastAPI


app = FastAPI()
mongo_url = 'mongodb://root:123456@127.0.0.1:27017/test'

m_app = MFastAPI(app, database_url=mongo_url)


class User(BaseModel):
    # 暂不支持嵌套类
    id: int
    username: str = Field(..., x_unique=True, x_in=True, x_out=True)
    email: str = Field(..., x_in=True, x_out=True)
    password: str = Field(..., x_in=True)
    nickname: str = Field(None, x_exclude_out=True)

    class X_Config:
        query = [{'$or': ['username', 'email']}]


class Course(BaseModel):
    id: int
    name: str
    data_file: str = Field(..., x_file=True)


class SelectCourse(BaseModel):
    id: int
    course_ids: List[int] = Field(..., x_foreign_key=('course', 'id', 'list'))
    user_id: int = Field(..., x_foreign_key=('user', 'id'))


@m_app.get('/')
def root():
    return {'message': 'hello world'}

m_app.gen_api(['index'])

```
