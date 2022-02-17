from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

from . import settings

config = CosConfig(Region=settings.region, SecretId=settings.secret_id, SecretKey=settings.secret_key)
client = CosS3Client(config)


def put_obj(f, path):
    return client.put_object(
        Bucket=settings.Bucket,
        Body=f,
        Key=path,
        StorageClass="STANDARD",
        EnableMD5=False
    )


def delete_obj(path):
    return client.delete_object(
        Bucket=settings.Bucket,
        Key=path
    )


def get_cos_token(path):
    return client.get_presigned_url(
        Method='PUT',
        Bucket=settings.Bucket,
        Key=path,
    )


__all__ = [
    "put_obj",
    "delete_obj",
    "get_cos_token",
]
