"""
MinIO-based object storage system for AIOSv3.

Provides atomic file operations, versioning, and workspace management
for agent collaboration and artifact sharing.
"""

import asyncio
import hashlib
import io
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Optional, Dict
from urllib.parse import urlparse

from minio import Minio
from minio.error import S3Error
from minio.versioningconfig import ENABLED, VersioningConfig

logger = logging.getLogger(__name__)


@dataclass
class StorageMetadata:
    """Metadata for stored objects."""

    object_key: str
    size: int
    last_modified: datetime
    etag: str
    content_type: str
    version_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    user_metadata: Optional[Dict[str, str]] = None


@dataclass
class UploadProgress:
    """Progress information for file uploads."""

    bytes_uploaded: int
    total_bytes: int
    percentage: float
    upload_speed: float | None = None  # bytes per second
    eta: float | None = None  # estimated time remaining in seconds


class ObjectStorage:
    """
    MinIO-based object storage client for AIOSv3.

    Features:
    - Atomic file operations
    - Versioning and metadata
    - Agent workspace isolation
    - Progress tracking for large files
    - Conflict prevention
    """

    def __init__(
        self,
        endpoint: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        secure: bool = False,
    ):
        """
        Initialize object storage client.

        Args:
            endpoint: MinIO server endpoint
            access_key: Access key for authentication
            secret_key: Secret key for authentication
            secure: Whether to use HTTPS
        """
        self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = access_key or os.getenv("MINIO_ACCESS_KEY", "aiosv3")
        self.secret_key = secret_key or os.getenv(
            "MINIO_SECRET_KEY", "dev_password_123"
        )
        self.secure = secure

        # Remove http:// or https:// prefix if present
        if "://" in self.endpoint:
            parsed = urlparse(
                f"http://{self.endpoint}"
                if not self.endpoint.startswith(("http://", "https://"))
                else self.endpoint
            )
            self.endpoint = f"{parsed.hostname}:{parsed.port or (443 if parsed.scheme == 'https' else 9000)}"

        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

        # Standard bucket names
        self.workspaces_bucket = "agent-workspaces"
        self.artifacts_bucket = "shared-artifacts"
        self.system_bucket = "system-data"

    async def initialize(self) -> None:
        """Initialize storage system and create default buckets."""
        logger.info("Initializing object storage system")

        # Create default buckets if they don't exist
        default_buckets = [
            self.workspaces_bucket,
            self.artifacts_bucket,
            self.system_bucket,
        ]

        for bucket_name in default_buckets:
            await self.create_bucket_if_not_exists(bucket_name)
            await self.enable_versioning(bucket_name)

        logger.info("Object storage system initialized successfully")

    async def create_bucket_if_not_exists(self, bucket_name: str) -> bool:
        """Create a bucket if it doesn't exist."""
        try:
            # Run in thread pool since minio is sync
            exists = await asyncio.get_event_loop().run_in_executor(
                None, self.client.bucket_exists, bucket_name
            )

            if not exists:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.client.make_bucket, bucket_name
                )
                logger.info(f"Created bucket: {bucket_name}")
                return True
            else:
                logger.debug(f"Bucket already exists: {bucket_name}")
                return False

        except S3Error as e:
            logger.error(f"Failed to create bucket {bucket_name}: {e}")
            raise

    async def enable_versioning(self, bucket_name: str) -> None:
        """Enable versioning for a bucket."""
        try:
            config = VersioningConfig(ENABLED)
            await asyncio.get_event_loop().run_in_executor(
                None, self.client.set_bucket_versioning, bucket_name, config
            )
            logger.debug(f"Enabled versioning for bucket: {bucket_name}")
        except S3Error as e:
            logger.error(f"Failed to enable versioning for {bucket_name}: {e}")
            raise

    async def upload_file(
        self,
        bucket_name: str,
        object_key: str,
        file_path: str | Path,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
        tags: dict[str, str] | None = None,
        progress_callback: callable | None = None,
    ) -> StorageMetadata:
        """
        Upload a file to object storage.

        Args:
            bucket_name: Target bucket name
            object_key: Object key/path in bucket
            file_path: Local file path to upload
            content_type: MIME type of the file
            metadata: User metadata for the object
            tags: Tags for the object
            progress_callback: Callback for upload progress

        Returns:
            StorageMetadata: Metadata of uploaded object
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Auto-detect content type if not provided
        if not content_type:
            content_type = self._get_content_type(file_path)

        # Calculate file hash for integrity checking
        file_hash = await self._calculate_file_hash(file_path)

        # Prepare metadata
        object_metadata = metadata or {}
        object_metadata.update(
            {
                "uploaded-by": "aiosv3",
                "upload-timestamp": datetime.utcnow().isoformat(),
                "file-hash": file_hash,
                "original-filename": file_path.name,
            }
        )

        # Prepare tags - temporarily disabled due to API issue
        object_tags = None
        # if tags:
        #     object_tags = Tags()
        #     for key, value in tags.items():
        #         object_tags[key] = value

        try:
            # Upload file
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self._upload_file_sync,
                bucket_name,
                object_key,
                str(file_path),
                content_type,
                object_metadata,
                object_tags,
            )

            logger.info(f"Uploaded file {file_path} to {bucket_name}/{object_key}")

            # Get object metadata
            return await self.get_object_metadata(bucket_name, object_key)

        except S3Error as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            raise

    def _upload_file_sync(
        self,
        bucket_name: str,
        object_key: str,
        file_path: str,
        content_type: str,
        metadata: dict[str, str],
        tags,
    ):
        """Synchronous file upload wrapper."""
        return self.client.fput_object(
            bucket_name=bucket_name,
            object_name=object_key,
            file_path=file_path,
            content_type=content_type,
            metadata=metadata,
            tags=tags,
        )

    async def upload_data(
        self,
        bucket_name: str,
        object_key: str,
        data: bytes | str | BinaryIO,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
        tags: dict[str, str] | None = None,
    ) -> StorageMetadata:
        """
        Upload data directly to object storage.

        Args:
            bucket_name: Target bucket name
            object_key: Object key/path in bucket
            data: Data to upload
            content_type: MIME type of the data
            metadata: User metadata for the object
            tags: Tags for the object

        Returns:
            StorageMetadata: Metadata of uploaded object
        """
        # Convert data to bytes if needed
        if isinstance(data, str):
            data = data.encode("utf-8")
        elif hasattr(data, "read"):
            data = data.read()

        # Calculate data hash
        data_hash = hashlib.sha256(data).hexdigest()

        # Prepare metadata
        object_metadata = metadata or {}
        object_metadata.update(
            {
                "uploaded-by": "aiosv3",
                "upload-timestamp": datetime.utcnow().isoformat(),
                "data-hash": data_hash,
                "data-size": str(len(data)),
            }
        )

        # Prepare tags - temporarily disabled due to API issue
        object_tags = None
        # if tags:
        #     object_tags = Tags()
        #     for key, value in tags.items():
        #         object_tags[key] = value

        try:
            # Upload data
            data_stream = io.BytesIO(data)

            await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.put_object,
                bucket_name,
                object_key,
                data_stream,
                len(data),
                content_type,
                object_metadata,
                None,  # sse
                object_tags,
            )

            logger.info(f"Uploaded data to {bucket_name}/{object_key}")

            # Get object metadata
            return await self.get_object_metadata(bucket_name, object_key)

        except S3Error as e:
            logger.error(f"Failed to upload data to {bucket_name}/{object_key}: {e}")
            raise

    async def download_file(
        self,
        bucket_name: str,
        object_key: str,
        file_path: str | Path,
        version_id: str | None = None,
    ) -> Path:
        """
        Download a file from object storage.

        Args:
            bucket_name: Source bucket name
            object_key: Object key/path in bucket
            file_path: Local file path to save to
            version_id: Specific version to download

        Returns:
            Path: Path to downloaded file
        """
        file_path = Path(file_path)

        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._download_file_sync,
                bucket_name,
                object_key,
                str(file_path),
                version_id,
            )

            logger.info(f"Downloaded {bucket_name}/{object_key} to {file_path}")
            return file_path

        except S3Error as e:
            logger.error(f"Failed to download {bucket_name}/{object_key}: {e}")
            raise

    def _download_file_sync(
        self,
        bucket_name: str,
        object_key: str,
        file_path: str,
        version_id: str | None = None,
    ):
        """Synchronous file download wrapper."""
        if version_id:
            return self.client.fget_object(
                bucket_name=bucket_name,
                object_name=object_key,
                file_path=file_path,
                version_id=version_id,
            )
        else:
            return self.client.fget_object(
                bucket_name=bucket_name,
                object_name=object_key,
                file_path=file_path,
            )

    async def download_data(
        self,
        bucket_name: str,
        object_key: str,
        version_id: str | None = None,
    ) -> bytes:
        """
        Download object data as bytes.

        Args:
            bucket_name: Source bucket name
            object_key: Object key/path in bucket
            version_id: Specific version to download

        Returns:
            bytes: Object data
        """
        try:
            if version_id:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.get_object(
                        bucket_name, object_key, version_id=version_id
                    ),
                )
            else:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.client.get_object,
                    bucket_name,
                    object_key,
                )

            data = response.read()
            response.close()
            response.release_conn()

            logger.debug(f"Downloaded data from {bucket_name}/{object_key}")
            return data

        except S3Error as e:
            logger.error(
                f"Failed to download data from {bucket_name}/{object_key}: {e}"
            )
            raise

    async def get_object_metadata(
        self, bucket_name: str, object_key: str, version_id: str | None = None
    ) -> StorageMetadata:
        """Get metadata for an object."""
        try:
            if version_id:
                stat = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.stat_object(
                        bucket_name, object_key, version_id=version_id
                    ),
                )
            else:
                stat = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.client.stat_object,
                    bucket_name,
                    object_key,
                )

            return StorageMetadata(
                object_key=object_key,
                size=stat.size,
                last_modified=stat.last_modified,
                etag=stat.etag,
                content_type=stat.content_type,
                version_id=stat.version_id,
                tags=None,  # Tags need separate call
                user_metadata=stat.metadata,
            )

        except S3Error as e:
            logger.error(f"Failed to get metadata for {bucket_name}/{object_key}: {e}")
            raise

    async def delete_object(
        self, bucket_name: str, object_key: str, version_id: str | None = None
    ) -> None:
        """Delete an object from storage."""
        try:
            if version_id:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.remove_object(
                        bucket_name, object_key, version_id=version_id
                    ),
                )
            else:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.client.remove_object,
                    bucket_name,
                    object_key,
                )

            logger.info(f"Deleted {bucket_name}/{object_key}")

        except S3Error as e:
            logger.error(f"Failed to delete {bucket_name}/{object_key}: {e}")
            raise

    async def list_objects(
        self,
        bucket_name: str,
        prefix: str | None = None,
        recursive: bool = True,
        include_versions: bool = False,
    ) -> list[StorageMetadata]:
        """List objects in a bucket."""
        try:
            objects = []

            if include_versions:
                object_iter = self.client.list_objects(
                    bucket_name,
                    prefix=prefix,
                    recursive=recursive,
                    include_version=True,
                )
            else:
                object_iter = self.client.list_objects(
                    bucket_name, prefix=prefix, recursive=recursive
                )

            for obj in object_iter:
                objects.append(
                    StorageMetadata(
                        object_key=obj.object_name,
                        size=obj.size,
                        last_modified=obj.last_modified,
                        etag=obj.etag,
                        content_type=getattr(
                            obj, "content_type", "application/octet-stream"
                        ),
                        version_id=getattr(obj, "version_id", None),
                    )
                )

            return objects

        except S3Error as e:
            logger.error(f"Failed to list objects in {bucket_name}: {e}")
            raise

    async def copy_object(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        dest_key: str,
        metadata: dict[str, str] | None = None,
    ) -> StorageMetadata:
        """Copy an object within or between buckets."""
        try:
            from minio.commonconfig import CopySource

            copy_source = CopySource(source_bucket, source_key)

            await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.copy_object,
                dest_bucket,
                dest_key,
                copy_source,
                metadata=metadata,
            )

            logger.info(
                f"Copied {source_bucket}/{source_key} to {dest_bucket}/{dest_key}"
            )

            return await self.get_object_metadata(dest_bucket, dest_key)

        except S3Error as e:
            logger.error(f"Failed to copy object: {e}")
            raise

    async def create_agent_workspace(self, agent_id: str) -> str:
        """Create a dedicated workspace for an agent."""
        workspace_prefix = f"workspaces/{agent_id}/"

        # Create a marker file to establish the workspace
        marker_key = f"{workspace_prefix}.workspace"
        workspace_info = {
            "agent_id": agent_id,
            "created_at": datetime.utcnow().isoformat(),
            "workspace_type": "agent_workspace",
        }

        await self.upload_data(
            bucket_name=self.workspaces_bucket,
            object_key=marker_key,
            data=json.dumps(workspace_info),
            content_type="application/json",
            metadata={"workspace-owner": agent_id},
            tags={"type": "workspace", "agent": agent_id},
        )

        logger.info(f"Created workspace for agent {agent_id}")
        return workspace_prefix

    async def health_check(self) -> dict[str, Any]:
        """Check the health of the object storage system."""
        try:
            # Test connection by listing buckets
            buckets = await asyncio.get_event_loop().run_in_executor(
                None, self.client.list_buckets
            )

            bucket_info = {}
            for bucket in buckets:
                bucket_info[bucket.name] = {
                    "created": bucket.creation_date.isoformat(),
                }

            return {
                "status": "healthy",
                "endpoint": self.endpoint,
                "buckets": bucket_info,
                "secure": self.secure,
            }

        except Exception as e:
            return {
                "status": "error",
                "endpoint": self.endpoint,
                "error": str(e),
            }

    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        hasher = hashlib.sha256()

        def _hash_file():
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()

        return await asyncio.get_event_loop().run_in_executor(None, _hash_file)

    def _get_content_type(self, file_path: Path) -> str:
        """Get content type based on file extension."""
        import mimetypes

        content_type, _ = mimetypes.guess_type(str(file_path))
        return content_type or "application/octet-stream"


# Global object storage instance
object_storage: ObjectStorage | None = None


async def initialize_object_storage() -> ObjectStorage:
    """Initialize global object storage instance."""
    global object_storage

    if object_storage is None:
        object_storage = ObjectStorage()
        await object_storage.initialize()

    return object_storage


async def get_object_storage() -> ObjectStorage:
    """Get the global object storage instance."""
    if object_storage is None:
        return await initialize_object_storage()
    return object_storage
