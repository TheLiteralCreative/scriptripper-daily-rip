"""
Storage service — Cloudflare R2 via boto3 (S3-compatible).
"""
import boto3
from botocore.config import Config
from app.settings import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
            region_name=settings.S3_REGION,
        )
    return _client


def upload_text(key: str, content: str, content_type: str = "text/markdown") -> str:
    """Upload text content to R2. Returns the object URL."""
    client = _get_client()
    client.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key,
        Body=content.encode("utf-8"),
        ContentType=content_type,
    )
    return f"{settings.R2_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{key}"


def download_text(key: str) -> str:
    """Download text content from R2."""
    client = _get_client()
    response = client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
    return response["Body"].read().decode("utf-8")


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    """Generate a pre-signed URL for temporary access to an archived document."""
    client = _get_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key},
        ExpiresIn=expires_in,
    )
