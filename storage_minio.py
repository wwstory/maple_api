from minio import Minio
from minio.error import InvalidResponseError
from starlette.datastructures import UploadFile
import os
from datetime import timedelta
from uuid import uuid4
import json

from .storage_adapter import StorageAdapter

class MinioAdapter(StorageAdapter):
    def __init__(self, url, bucket, access_key, secret_key, secure, policy, **kwargs):
        self.client = Minio(
            url,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self.url = url
        self.bucket = bucket
        self.policy = policy

        try:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
        except InvalidResponseError as e:
            print('无法创建Bucket!')
            raise e
        try:
            if policy == 'public':
                j = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": [
                                    "*"
                                ]
                            },
                            "Action": [
                                "s3:ListBucket",
                                "s3:ListBucketMultipartUploads",
                                "s3:GetBucketLocation"
                            ],
                            "Resource": [
                                f"arn:aws:s3:::{bucket}"
                            ]
                        },
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": [
                                    "*"
                                ]
                            },
                            "Action": [
                                "s3:GetObject",
                                "s3:ListMultipartUploadParts",
                                "s3:PutObject",
                                "s3:AbortMultipartUpload",
                                "s3:DeleteObject"
                            ],
                            "Resource": [
                                f"arn:aws:s3:::{bucket}/*"
                            ]
                        }
                    ]
                }
                # https://docs.min.io/docs/python-client-api-reference.html#set_bucket_policy
                self.client.set_bucket_policy(bucket, json.dumps(j))
        except InvalidResponseError as e:
            print('修改Bucket的Policy失败!')
            raise e


    def get_client(self):
        return self.client


    def upload_object(self, file: UploadFile, prefix='', bucket_name=None, use_uuid=True):
        bucket_name = bucket_name or self.bucket
        try:
            print(type(file), isinstance(file, UploadFile))
            if isinstance(file, UploadFile):   # 属于UploadFile类型的文件
                file_size = os.fstat(file.file.fileno()).st_size
                file_name = f'{uuid4()}{os.path.splitext(file.filename)[1]}' if use_uuid else file.filename
                file_name = os.path.join(prefix, file_name)
                self.client.put_object(bucket_name, file_name, file.file, file_size)
            else:
                file_size = os.fstat(file.fileno()).st_size
                file_name = f'{uuid4()}{os.path.splitext(file.name)[1]}' if use_uuid else file.name
                file_name = os.path.join(prefix, file_name)
                self.client.put_object(bucket_name, file_name, file, file_size)
            return file_name
        except InvalidResponseError as e:
            raise e


    def get_object(self, object_name, bucket_name=None):
        bucket_name = bucket_name or self.bucket
        try:
            return self.client.get_object(bucket_name, object_name)
        except InvalidResponseError as e:
            raise e


    def get_object_content(self, object_name, bucket_name=None):
        bucket_name = bucket_name or self.bucket
        return self.get_object(object_name, bucket_name).data


    def get_object_url(self, object_name, bucket_name=None, use_presigned=False, expires=timedelta(days=7)) -> str:
        bucket_name = bucket_name or self.bucket
        if not use_presigned:
            file_url = f'{self.url}/{bucket_name}/{object_name}'
        else:
            try:
                file_url = self.client.presigned_get_object(
                    bucket_name, object_name, expires=expires)
            except InvalidResponseError as e:
                raise e
        return file_url
