# maple_api


## example

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

from maple_api.maple_fastapi import MFastAPI


app = FastAPI()
mongo_url = 'mongodb://root:123456@127.0.0.1:27017/test'

m_app = MFastAPI(app, database_url=mongo_url, prefix='/api')


class User(BaseModel):
    id: int
    username: str = Field(..., x_unique=True, x_in=True, x_out=True, x_query=True)
    email: str = Field('', x_in=True, x_out=True, x_update=True)
    password: str = Field(..., x_in=True)
    nickname: str = Field(None, x_exclude_out=True)

    class X_Config:
        api = [
            {
                'path': '/abc',
                'query': [{'$and': ['username', 'email']}]
            }
        ]
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

from pprint import pprint
pprint(m_app.get_api_dict())
```
