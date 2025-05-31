"""
File versioning and backup system for AIOSv3 object storage.

Provides version management, backup strategies, and cleanup policies
for maintaining object history and recovery capabilities.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from core.storage.object_store import ObjectStorage, get_object_storage

logger = logging.getLogger(__name__)


class BackupStrategy(Enum):
    """Backup strategies for versioned objects."""

    NONE = "none"  # No backup
    DAILY = "daily"  # Daily backups
    WEEKLY = "weekly"  # Weekly backups
    MONTHLY = "monthly"  # Monthly backups
    ON_CHANGE = "on_change"  # Backup on every change
    SMART = "smart"  # Smart backup based on change frequency


class CleanupPolicy(Enum):
    """Cleanup policies for old versions."""

    KEEP_ALL = "keep_all"  # Never delete versions
    KEEP_RECENT = "keep_recent"  # Keep only recent versions
    KEEP_IMPORTANT = "keep_important"  # Keep tagged/important versions
    SIZE_BASED = "size_based"  # Cleanup based on storage size
    TIME_BASED = "time_based"  # Cleanup based on age


@dataclass
class VersionInfo:
    """Information about a file version."""

    version_id: str
    object_key: str
    created_at: datetime
    created_by: str
    size: int
    checksum: str
    tags: dict[str, str]
    is_latest: bool = False
    is_backup: bool = False
    change_description: str | None = None


@dataclass
class VersioningConfig:
    """Configuration for versioning behavior."""

    enabled: bool = True
    max_versions: int = 10
    backup_strategy: BackupStrategy = BackupStrategy.WEEKLY
    cleanup_policy: CleanupPolicy = CleanupPolicy.KEEP_RECENT
    retention_days: int = 30
    max_storage_mb: int = 1000
    auto_backup: bool = True
    preserve_tags: list[str] | None = None  # Tags that prevent deletion


class VersionManager:
    """
    Manages file versions and backup strategies for object storage.

    Features:
    - Automatic version creation on file changes
    - Configurable backup strategies
    - Intelligent cleanup policies
    - Version comparison and rollback
    - Storage optimization
    """

    def __init__(self, storage: ObjectStorage | None = None):
        """Initialize version manager."""
        self.storage = storage
        self.versioning_configs: dict[str, VersioningConfig] = {}

    async def initialize(self) -> None:
        """Initialize version manager."""
        if not self.storage:
            self.storage = await get_object_storage()

        # Load versioning configurations
        await self._load_versioning_configs()

        logger.info("Version manager initialized")

    async def set_versioning_config(
        self, bucket_pattern: str, config: VersioningConfig
    ) -> None:
        """Set versioning configuration for a bucket pattern."""
        self.versioning_configs[bucket_pattern] = config

        # Save configuration to storage
        await self._save_versioning_config(bucket_pattern, config)

        logger.info(f"Set versioning config for pattern {bucket_pattern}")

    async def get_versions(
        self, bucket_name: str, object_key: str, limit: int | None = None
    ) -> list[VersionInfo]:
        """Get all versions of an object."""
        try:
            # Get all versions from storage
            objects = await self.storage.list_objects(
                bucket_name=bucket_name, prefix=object_key, include_versions=True
            )

            versions = []
            latest_version = None

            for obj in objects:
                if obj.object_key == object_key:
                    # Get additional metadata
                    metadata = await self.storage.get_object_metadata(
                        bucket_name=bucket_name,
                        object_key=object_key,
                        version_id=obj.version_id,
                    )

                    version_info = VersionInfo(
                        version_id=obj.version_id or "latest",
                        object_key=object_key,
                        created_at=obj.last_modified,
                        created_by=(
                            metadata.user_metadata.get("uploaded-by", "unknown")
                            if metadata.user_metadata
                            else "unknown"
                        ),
                        size=obj.size,
                        checksum=obj.etag,
                        tags={},  # Would extract from metadata
                        is_latest=latest_version is None,
                    )

                    versions.append(version_info)

                    if latest_version is None:
                        latest_version = version_info
                        version_info.is_latest = True

            # Sort by creation time (newest first)
            versions.sort(key=lambda v: v.created_at, reverse=True)

            # Mark the newest version as latest (after sorting)
            if versions:
                # Reset all is_latest flags
                for v in versions:
                    v.is_latest = False
                # Set the first (newest) as latest
                versions[0].is_latest = True

            # Apply limit
            if limit:
                versions = versions[:limit]

            return versions

        except Exception as e:
            logger.error(f"Failed to get versions for {bucket_name}/{object_key}: {e}")
            return []

    async def create_backup(
        self,
        bucket_name: str,
        object_key: str,
        backup_type: str = "manual",
        description: str | None = None,
    ) -> str | None:
        """Create a backup of the current version."""
        try:
            # Get current object metadata
            metadata = await self.storage.get_object_metadata(bucket_name, object_key)

            # Create backup object key
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_key = f"backups/{object_key}/{backup_type}_{timestamp}"

            # Copy current version to backup location
            backup_metadata = await self.storage.copy_object(
                source_bucket=bucket_name,
                source_key=object_key,
                dest_bucket=bucket_name,
                dest_key=backup_key,
                metadata={
                    "backup_type": backup_type,
                    "backup_timestamp": datetime.utcnow().isoformat(),
                    "original_object": object_key,
                    "backup_description": description or f"{backup_type} backup",
                    "original_version": metadata.version_id or "latest",
                },
            )

            logger.info(f"Created {backup_type} backup for {bucket_name}/{object_key}")
            return backup_key

        except Exception as e:
            logger.error(f"Failed to create backup for {bucket_name}/{object_key}: {e}")
            return None

    async def restore_version(
        self,
        bucket_name: str,
        object_key: str,
        version_id: str,
        create_backup: bool = True,
    ) -> bool:
        """Restore a specific version of an object."""
        try:
            # Create backup of current version if requested
            if create_backup:
                await self.create_backup(
                    bucket_name,
                    object_key,
                    "pre_restore",
                    f"Backup before restoring to version {version_id}",
                )

            # Download the specific version
            import tempfile
            from pathlib import Path

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = Path(temp_file.name)

            try:
                # Download old version
                await self.storage.download_file(
                    bucket_name=bucket_name,
                    object_key=object_key,
                    file_path=temp_path,
                    version_id=version_id,
                )

                # Upload as new current version
                restore_metadata = {
                    "restored_from_version": version_id,
                    "restore_timestamp": datetime.utcnow().isoformat(),
                    "restore_operation": "version_rollback",
                }

                await self.storage.upload_file(
                    bucket_name=bucket_name,
                    object_key=object_key,
                    file_path=temp_path,
                    metadata=restore_metadata,
                )

                logger.info(
                    f"Restored {bucket_name}/{object_key} to version {version_id}"
                )
                return True

            finally:
                # Clean up temp file
                temp_path.unlink(missing_ok=True)

        except Exception as e:
            logger.error(
                f"Failed to restore {bucket_name}/{object_key} to version {version_id}: {e}"
            )
            return False

    async def cleanup_old_versions(
        self,
        bucket_name: str,
        object_key: str | None = None,
        config: VersioningConfig | None = None,
    ) -> dict[str, Any]:
        """Clean up old versions based on policy."""
        cleanup_config = config or self._get_versioning_config(bucket_name)

        cleanup_result = {
            "bucket_name": bucket_name,
            "cleanup_timestamp": datetime.utcnow().isoformat(),
            "versions_deleted": 0,
            "space_freed": 0,
            "errors": [],
        }

        try:
            # Determine which objects to process
            if object_key:
                objects_to_process = [object_key]
            else:
                # Get all objects in bucket
                all_objects = await self.storage.list_objects(bucket_name)
                objects_to_process = [obj.object_key for obj in all_objects]

            for obj_key in objects_to_process:
                try:
                    cleanup_stats = await self._cleanup_object_versions(
                        bucket_name, obj_key, cleanup_config
                    )

                    cleanup_result["versions_deleted"] += cleanup_stats["deleted"]
                    cleanup_result["space_freed"] += cleanup_stats["space_freed"]

                except Exception as e:
                    cleanup_result["errors"].append(
                        {"object": obj_key, "error": str(e)}
                    )

            logger.info(
                f"Cleanup completed: {cleanup_result['versions_deleted']} versions deleted, "
                f"{cleanup_result['space_freed']} bytes freed"
            )

        except Exception as e:
            cleanup_result["errors"].append({"general": str(e)})
            logger.error(f"Cleanup failed: {e}")

        return cleanup_result

    async def get_storage_stats(
        self, bucket_name: str, object_prefix: str | None = None
    ) -> dict[str, Any]:
        """Get storage statistics for versioned objects."""
        try:
            objects = await self.storage.list_objects(
                bucket_name=bucket_name, prefix=object_prefix, include_versions=True
            )

            stats = {
                "total_objects": 0,
                "total_versions": len(objects),
                "total_size": 0,
                "latest_versions_size": 0,
                "old_versions_size": 0,
                "objects_by_type": {},
                "versions_by_age": {
                    "last_day": 0,
                    "last_week": 0,
                    "last_month": 0,
                    "older": 0,
                },
            }

            unique_objects = set()
            now = datetime.utcnow()

            for obj in objects:
                unique_objects.add(obj.object_key)
                stats["total_size"] += obj.size

                # Age categorization
                age_days = (now - obj.last_modified).days
                if age_days < 1:
                    stats["versions_by_age"]["last_day"] += 1
                elif age_days < 7:
                    stats["versions_by_age"]["last_week"] += 1
                elif age_days < 30:
                    stats["versions_by_age"]["last_month"] += 1
                else:
                    stats["versions_by_age"]["older"] += 1

                # File type categorization
                file_ext = (
                    obj.object_key.split(".")[-1].lower()
                    if "." in obj.object_key
                    else "no_ext"
                )
                if file_ext not in stats["objects_by_type"]:
                    stats["objects_by_type"][file_ext] = {"count": 0, "size": 0}
                stats["objects_by_type"][file_ext]["count"] += 1
                stats["objects_by_type"][file_ext]["size"] += obj.size

            stats["total_objects"] = len(unique_objects)

            return stats

        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {}

    async def schedule_automated_backups(self) -> None:
        """Schedule automated backups based on configurations."""
        for pattern, config in self.versioning_configs.items():
            if config.auto_backup and config.backup_strategy != BackupStrategy.NONE:
                asyncio.create_task(self._backup_scheduler(pattern, config))

    # Private helper methods

    def _get_versioning_config(self, bucket_name: str) -> VersioningConfig:
        """Get versioning configuration for a bucket."""
        # Check for exact match first
        if bucket_name in self.versioning_configs:
            return self.versioning_configs[bucket_name]

        # Check for pattern matches
        for pattern, config in self.versioning_configs.items():
            if self._matches_pattern(bucket_name, pattern):
                return config

        # Return default config
        return VersioningConfig()

    def _matches_pattern(self, bucket_name: str, pattern: str) -> bool:
        """Check if bucket name matches pattern."""
        # Simple pattern matching (could be enhanced with regex)
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return bucket_name.startswith(pattern[:-1])
        if pattern.startswith("*"):
            return bucket_name.endswith(pattern[1:])
        return bucket_name == pattern

    async def _cleanup_object_versions(
        self, bucket_name: str, object_key: str, config: VersioningConfig
    ) -> dict[str, int]:
        """Clean up versions for a specific object."""
        versions = await self.get_versions(bucket_name, object_key)

        if len(versions) <= 1:
            return {"deleted": 0, "space_freed": 0}

        # Determine which versions to delete
        versions_to_delete = []

        if config.cleanup_policy == CleanupPolicy.KEEP_RECENT:
            # Keep only the most recent N versions
            if len(versions) > config.max_versions:
                versions_to_delete = versions[config.max_versions :]

        elif config.cleanup_policy == CleanupPolicy.TIME_BASED:
            # Delete versions older than retention period
            cutoff_date = datetime.utcnow() - timedelta(days=config.retention_days)
            versions_to_delete = [
                v for v in versions if v.created_at < cutoff_date and not v.is_latest
            ]

        elif config.cleanup_policy == CleanupPolicy.KEEP_IMPORTANT:
            # Keep versions with preserve tags
            preserve_tags = config.preserve_tags or []
            versions_to_delete = [
                v
                for v in versions
                if not v.is_latest and not any(tag in v.tags for tag in preserve_tags)
            ]

        # Execute deletions
        deleted_count = 0
        space_freed = 0

        for version in versions_to_delete:
            try:
                await self.storage.delete_object(
                    bucket_name=bucket_name,
                    object_key=object_key,
                    version_id=(
                        version.version_id if version.version_id != "latest" else None
                    ),
                )

                deleted_count += 1
                space_freed += version.size

            except Exception as e:
                logger.warning(f"Failed to delete version {version.version_id}: {e}")

        return {"deleted": deleted_count, "space_freed": space_freed}

    async def _save_versioning_config(
        self, pattern: str, config: VersioningConfig
    ) -> None:
        """Save versioning configuration to storage."""
        config_data = {
            "pattern": pattern,
            "enabled": config.enabled,
            "max_versions": config.max_versions,
            "backup_strategy": config.backup_strategy.value,
            "cleanup_policy": config.cleanup_policy.value,
            "retention_days": config.retention_days,
            "max_storage_mb": config.max_storage_mb,
            "auto_backup": config.auto_backup,
            "preserve_tags": config.preserve_tags,
            "updated_at": datetime.utcnow().isoformat(),
        }

        await self.storage.upload_data(
            bucket_name=self.storage.system_bucket,
            object_key=f"versioning/configs/{pattern.replace('*', 'wildcard')}.json",
            data=json.dumps(config_data),
            content_type="application/json",
        )

    async def _load_versioning_configs(self) -> None:
        """Load versioning configurations from storage."""
        try:
            objects = await self.storage.list_objects(
                bucket_name=self.storage.system_bucket, prefix="versioning/configs/"
            )

            for obj in objects:
                if obj.object_key.endswith(".json"):
                    try:
                        data = await self.storage.download_data(
                            bucket_name=self.storage.system_bucket,
                            object_key=obj.object_key,
                        )

                        config_data = json.loads(data.decode("utf-8"))
                        pattern = config_data["pattern"]

                        config = VersioningConfig(
                            enabled=config_data.get("enabled", True),
                            max_versions=config_data.get("max_versions", 10),
                            backup_strategy=BackupStrategy(
                                config_data.get("backup_strategy", "weekly")
                            ),
                            cleanup_policy=CleanupPolicy(
                                config_data.get("cleanup_policy", "keep_recent")
                            ),
                            retention_days=config_data.get("retention_days", 30),
                            max_storage_mb=config_data.get("max_storage_mb", 1000),
                            auto_backup=config_data.get("auto_backup", True),
                            preserve_tags=config_data.get("preserve_tags"),
                        )

                        self.versioning_configs[pattern] = config

                    except Exception as e:
                        logger.warning(
                            f"Failed to load versioning config {obj.object_key}: {e}"
                        )

            logger.info(
                f"Loaded {len(self.versioning_configs)} versioning configurations"
            )

        except Exception as e:
            logger.warning(f"Failed to load versioning configurations: {e}")

    async def _backup_scheduler(self, pattern: str, config: VersioningConfig) -> None:
        """Automated backup scheduler for a pattern."""
        # This would implement the actual scheduling logic
        # For now, it's a placeholder
        logger.info(f"Backup scheduler started for pattern {pattern}")


# Global version manager instance
version_manager: VersionManager | None = None


async def get_version_manager() -> VersionManager:
    """Get the global version manager instance."""
    global version_manager

    if version_manager is None:
        version_manager = VersionManager()
        await version_manager.initialize()

    return version_manager


async def initialize_version_manager() -> VersionManager:
    """Initialize global version manager instance."""
    global version_manager

    version_manager = VersionManager()
    await version_manager.initialize()

    return version_manager
