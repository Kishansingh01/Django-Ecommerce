"""
Custom storage backends for AWS S3.
"""
from storages.backends.s3boto3 import S3Boto3Storage


class MediaRootS3Boto3Storage(S3Boto3Storage):
    """Storage for media files on S3."""
    location = 'media'
    file_overwrite = False
