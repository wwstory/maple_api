# maple_api


## Quick Start

### run mongo and minio

**1. run mongo:**

```sh
#/bin/sh

USER_NAME=root
USER_PASSWORD=123456
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=admin


docker run -d --name mongo -p 27017:27017 \
    -e MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME} \
    -e MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD} \
    mongo --auth

sleep 5

docker exec -i mongo bash <<EOF
mongo
use admin
db.auth("${MONGO_INITDB_ROOT_USERNAME}", "${MONGO_INITDB_ROOT_PASSWORD}");
use test
db.createUser({user: "${USER_NAME}", pwd: "${USER_PASSWORD}", roles: [{role: "readWrite", db:"test"}]});
exit
EOF

exit 0
```

**2. run minio:**

```sh
#/bin/sh

ACCESS_KEY=minioadmin
SECRET_KEY=minioadmin
LOAL_PATH=/tmp/data
BUCKET_NAME=test
SERVER_NAME=minio

docker run -d \
    --name=minio \
    -p 9000:9000 \
    -p 9090:9090 \
    -e "MINIO_ACCESS_KEY=${ACCESS_KEY}" \
    -e "MINIO_SECRET_KEY=${SECRET_KEY}" \
    -v ${LOAL_PATH}:/data \
    minio/minio server \
    /data --console-address ":9000" --address ":9090"

sleep 5

# http://docs.minio.org.cn/docs/master/minio-client-complete-guide
# docker run --rm minio/mc ls play
# docker run --rm -it --entrypoint=/bin/sh minio/mc << EOF
docker run --rm -i --entrypoint=/bin/sh minio/mc << EOF
mc config host add ${SERVER_NAME} http://localhost:9000 ${ACCESS_KEY} ${SECRET_KEY}
mc mb ${SERVER_NAME}/${BUCKET_NAME}
mc policy set public ${SERVER_NAME}/${BUCKET_NAME}
exit
EOF
```

### fastapi example

**3. run api server:**

```python
from pydantic import BaseModel, Field
from typing import List

from maple_api.maple_fastapi import MFastAPI


mongo_conf = {
    'name': 'mongo',
    'url': 'mongodb://root:123456@127.0.0.1:27017/test',
}
storage_conf = {
    'name': 'minio',
    'url': '127.0.0.1:9090',
    'bucket': 'test',
    'access_key': 'minioadmin',
    'secret_key': 'minioadmin',
    'secure': False,
    'policy': 'public',
}

m_app = MFastAPI(database_conf=mongo_conf, storage_conf=storage_conf, prefix='/api')
app = m_app.get_backend()


class User(BaseModel):
    id: int
    username: str = Field(..., x_unique=True, x_in=True, x_out=True, x_query=True)
    email: str = Field('', x_in=True, x_out=True, x_update=True)
    password: str = Field(..., x_in=True, x_update=True)
    nickname: str = Field(None, x_exclude_out=True)
    avatar: str = Field(None, x_file=True)


class Course(BaseModel):
    id: int
    name: str


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

**run**: save as `index.py`, then execute command `uvicorn index:app --reload` in terminal.
