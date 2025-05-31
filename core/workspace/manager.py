"""
Agent Workspace Management for AIOSv3.

Provides workspace isolation, conflict resolution, and synchronization
for multi-agent collaboration on shared artifacts.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from core.storage.object_store import ObjectStorage, get_object_storage

logger = logging.getLogger(__name__)


class WorkspaceType(Enum):
    """Types of workspaces available."""

    AGENT_PRIVATE = "agent_private"  # Private agent workspace
    AGENT_SHARED = "agent_shared"  # Shared between specific agents
    PROJECT_SHARED = "project_shared"  # Shared across project
    SYSTEM_SHARED = "system_shared"  # System-wide shared workspace


class ConflictResolution(Enum):
    """Conflict resolution strategies."""

    LAST_WRITER_WINS = "last_writer_wins"  # Most recent write wins
    MERGE_CHANGES = "merge_changes"  # Attempt to merge changes
    MANUAL_REVIEW = "manual_review"  # Require manual intervention
    VERSION_BRANCH = "version_branch"  # Create version branches
    AGENT_PRIORITY = "agent_priority"  # Use agent priority ranking


@dataclass
class WorkspaceConfig:
    """Configuration for workspace behavior."""

    workspace_id: str
    workspace_type: WorkspaceType
    owner_agent_id: str
    authorized_agents: list[str]
    conflict_resolution: ConflictResolution = ConflictResolution.LAST_WRITER_WINS
    auto_sync: bool = True
    sync_interval: float = 30.0  # seconds
    max_versions: int = 10
    retention_days: int = 30


@dataclass
class WorkspaceMetadata:
    """Metadata about a workspace."""

    workspace_id: str
    workspace_type: WorkspaceType
    owner_agent_id: str
    created_at: datetime
    last_accessed: datetime
    last_modified: datetime
    file_count: int
    total_size: int
    version_count: int


@dataclass
class FileConflict:
    """Information about a file conflict."""

    file_path: str
    workspace_id: str
    conflicting_versions: list[dict[str, Any]]
    conflict_type: str
    detected_at: datetime
    resolution_strategy: ConflictResolution
    resolved: bool = False
    resolution_result: str | None = None


class WorkspaceManager:
    """
    Manages agent workspaces for isolated and collaborative work.

    Features:
    - Workspace isolation per agent or project
    - File conflict detection and resolution
    - Automatic synchronization between agents
    - Version management and rollback
    - Access control and permissions
    """

    def __init__(self, storage: ObjectStorage | None = None):
        """Initialize workspace manager."""
        self.storage = storage
        self.active_workspaces: dict[str, WorkspaceConfig] = {}
        self.sync_tasks: dict[str, asyncio.Task] = {}
        self.conflict_queue: list[FileConflict] = []

    async def initialize(self) -> None:
        """Initialize workspace manager."""
        if not self.storage:
            self.storage = await get_object_storage()

        # Load existing workspace configurations
        await self._load_workspace_configs()

        logger.info("Workspace manager initialized")

    async def create_workspace(
        self,
        workspace_id: str,
        workspace_type: WorkspaceType,
        owner_agent_id: str,
        authorized_agents: list[str] | None = None,
        config: dict[str, Any] | None = None,
    ) -> WorkspaceConfig:
        """Create a new workspace for an agent or project."""
        authorized_agents = authorized_agents or [owner_agent_id]

        workspace_config = WorkspaceConfig(
            workspace_id=workspace_id,
            workspace_type=workspace_type,
            owner_agent_id=owner_agent_id,
            authorized_agents=authorized_agents,
            **(config or {}),
        )

        # Create workspace directory structure
        await self._create_workspace_structure(workspace_config)

        # Save workspace configuration
        await self._save_workspace_config(workspace_config)

        # Add to active workspaces
        self.active_workspaces[workspace_id] = workspace_config

        # Start sync task if auto-sync is enabled
        if workspace_config.auto_sync:
            await self._start_sync_task(workspace_config)

        logger.info(f"Created workspace {workspace_id} for agent {owner_agent_id}")
        return workspace_config

    async def get_workspace(self, workspace_id: str) -> WorkspaceConfig | None:
        """Get workspace configuration."""
        if workspace_id in self.active_workspaces:
            return self.active_workspaces[workspace_id]

        # Try to load from storage
        return await self._load_workspace_config(workspace_id)

    async def list_workspaces(
        self,
        agent_id: str | None = None,
        workspace_type: WorkspaceType | None = None,
    ) -> list[WorkspaceMetadata]:
        """List available workspaces."""
        workspaces = []

        # List workspace marker files
        objects = await self.storage.list_objects(
            bucket_name=self.storage.workspaces_bucket,
            prefix="workspaces/",
            recursive=True,
        )

        workspace_configs = [
            obj for obj in objects if obj.object_key.endswith(".workspace")
        ]

        for config_obj in workspace_configs:
            try:
                # Load workspace config
                data = await self.storage.download_data(
                    bucket_name=self.storage.workspaces_bucket,
                    object_key=config_obj.object_key,
                )

                config_data = json.loads(data.decode("utf-8"))
                workspace_id = config_data.get("workspace_id")

                # Apply filters
                if agent_id and config_data.get("owner_agent_id") != agent_id:
                    if agent_id not in config_data.get("authorized_agents", []):
                        continue

                if (
                    workspace_type
                    and config_data.get("workspace_type") != workspace_type.value
                ):
                    continue

                # Get workspace statistics
                metadata = await self._get_workspace_metadata(workspace_id, config_data)
                workspaces.append(metadata)

            except Exception as e:
                logger.warning(
                    f"Failed to load workspace config {config_obj.object_key}: {e}"
                )
                continue

        return workspaces

    async def upload_file(
        self,
        workspace_id: str,
        file_path: str,
        local_path: Path,
        agent_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Upload a file to a workspace with conflict detection."""
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")

        # Check permissions
        if not self._check_write_permission(workspace, agent_id):
            raise PermissionError(
                f"Agent {agent_id} not authorized to write to workspace {workspace_id}"
            )

        # Check for existing file
        object_key = f"workspaces/{workspace_id}/files/{file_path}"

        try:
            existing_metadata = await self.storage.get_object_metadata(
                bucket_name=self.storage.workspaces_bucket, object_key=object_key
            )

            # Conflict detected - handle based on strategy
            conflict = await self._handle_file_conflict(
                workspace, file_path, agent_id, existing_metadata
            )

            if conflict and not conflict.resolved:
                # Store in conflict queue for manual resolution
                self.conflict_queue.append(conflict)
                raise RuntimeError(
                    f"File conflict detected for {file_path} - requires resolution"
                )

        except Exception:
            # File doesn't exist - no conflict
            pass

        # Prepare metadata
        upload_metadata = {
            "workspace_id": workspace_id,
            "uploaded_by": agent_id,
            "upload_timestamp": datetime.utcnow().isoformat(),
            "file_path": file_path,
            **(metadata or {}),
        }

        # Upload file
        result = await self.storage.upload_file(
            bucket_name=self.storage.workspaces_bucket,
            object_key=object_key,
            file_path=local_path,
            metadata=upload_metadata,
        )

        # Update workspace last modified
        await self._update_workspace_timestamp(workspace_id)

        logger.info(
            f"Uploaded {file_path} to workspace {workspace_id} by agent {agent_id}"
        )
        return object_key

    async def download_file(
        self,
        workspace_id: str,
        file_path: str,
        local_path: Path,
        agent_id: str,
        version_id: str | None = None,
    ) -> Path:
        """Download a file from a workspace."""
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")

        # Check permissions
        if not self._check_read_permission(workspace, agent_id):
            raise PermissionError(
                f"Agent {agent_id} not authorized to read from workspace {workspace_id}"
            )

        object_key = f"workspaces/{workspace_id}/files/{file_path}"

        result = await self.storage.download_file(
            bucket_name=self.storage.workspaces_bucket,
            object_key=object_key,
            file_path=local_path,
            version_id=version_id,
        )

        # Update workspace last accessed
        await self._update_workspace_timestamp(workspace_id, access_only=True)

        logger.info(
            f"Downloaded {file_path} from workspace {workspace_id} by agent {agent_id}"
        )
        return result

    async def list_workspace_files(
        self, workspace_id: str, agent_id: str, prefix: str | None = None
    ) -> list[dict[str, Any]]:
        """List files in a workspace."""
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")

        # Check permissions
        if not self._check_read_permission(workspace, agent_id):
            raise PermissionError(
                f"Agent {agent_id} not authorized to read from workspace {workspace_id}"
            )

        search_prefix = f"workspaces/{workspace_id}/files/"
        if prefix:
            search_prefix += prefix

        objects = await self.storage.list_objects(
            bucket_name=self.storage.workspaces_bucket, prefix=search_prefix
        )

        files = []
        for obj in objects:
            # Extract relative file path
            relative_path = obj.object_key.replace(
                f"workspaces/{workspace_id}/files/", ""
            )

            files.append(
                {
                    "file_path": relative_path,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "content_type": obj.content_type,
                    "version_id": obj.version_id,
                    "object_key": obj.object_key,
                }
            )

        return files

    async def sync_workspace(self, workspace_id: str) -> dict[str, Any]:
        """Manually sync a workspace."""
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")

        sync_result = {
            "workspace_id": workspace_id,
            "sync_timestamp": datetime.utcnow().isoformat(),
            "conflicts_detected": 0,
            "files_synced": 0,
            "errors": [],
        }

        try:
            # Get all files in workspace
            files = await self.list_workspace_files(
                workspace_id, workspace.owner_agent_id
            )

            for file_info in files:
                try:
                    # Check for conflicts with other agents
                    await self._check_file_sync_conflicts(workspace, file_info)
                    sync_result["files_synced"] += 1

                except Exception as e:
                    sync_result["conflicts_detected"] += 1
                    sync_result["errors"].append(
                        {"file": file_info["file_path"], "error": str(e)}
                    )

            logger.info(
                f"Synced workspace {workspace_id}: {sync_result['files_synced']} files, {sync_result['conflicts_detected']} conflicts"
            )

        except Exception as e:
            sync_result["errors"].append({"general": str(e)})
            logger.error(f"Failed to sync workspace {workspace_id}: {e}")

        return sync_result

    async def resolve_conflict(
        self, conflict_id: int, resolution: str, agent_id: str
    ) -> bool:
        """Resolve a file conflict."""
        if conflict_id >= len(self.conflict_queue):
            raise ValueError("Invalid conflict ID")

        conflict = self.conflict_queue[conflict_id]
        workspace = await self.get_workspace(conflict.workspace_id)

        if not workspace:
            raise ValueError(f"Workspace {conflict.workspace_id} not found")

        # Check if agent has permission to resolve conflicts
        if (
            agent_id != workspace.owner_agent_id
            and agent_id not in workspace.authorized_agents
        ):
            raise PermissionError("Agent not authorized to resolve conflicts")

        try:
            # Apply resolution based on strategy
            if resolution == "use_latest":
                # Keep the most recent version
                pass  # Already the default behavior
            elif resolution == "use_version":
                # User specified which version to keep
                # Implementation would depend on the specific version
                pass
            elif resolution == "merge":
                # Attempt automatic merge
                await self._attempt_merge_resolution(conflict)

            conflict.resolved = True
            conflict.resolution_result = resolution

            logger.info(
                f"Resolved conflict for {conflict.file_path} in workspace {conflict.workspace_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to resolve conflict {conflict_id}: {e}")
            return False

    async def cleanup_workspace(
        self, workspace_id: str, agent_id: str, cleanup_type: str = "old_versions"
    ) -> dict[str, Any]:
        """Clean up old versions and temporary files."""
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")

        # Check permissions
        if agent_id != workspace.owner_agent_id:
            raise PermissionError("Only workspace owner can perform cleanup")

        cleanup_result = {
            "workspace_id": workspace_id,
            "cleanup_type": cleanup_type,
            "cleaned_files": 0,
            "space_freed": 0,
            "errors": [],
        }

        if cleanup_type == "old_versions":
            # Clean up old file versions based on retention policy
            files = await self.list_workspace_files(workspace_id, agent_id)

            for file_info in files:
                try:
                    # Get all versions of this file
                    versions = await self.storage.list_objects(
                        bucket_name=self.storage.workspaces_bucket,
                        prefix=file_info["object_key"],
                        include_versions=True,
                    )

                    # Keep only the latest N versions
                    if len(versions) > workspace.max_versions:
                        old_versions = versions[workspace.max_versions :]

                        for old_version in old_versions:
                            await self.storage.delete_object(
                                bucket_name=self.storage.workspaces_bucket,
                                object_key=old_version.object_key,
                                version_id=old_version.version_id,
                            )

                            cleanup_result["cleaned_files"] += 1
                            cleanup_result["space_freed"] += old_version.size

                except Exception as e:
                    cleanup_result["errors"].append(
                        {"file": file_info["file_path"], "error": str(e)}
                    )

        logger.info(
            f"Cleaned workspace {workspace_id}: {cleanup_result['cleaned_files']} files, {cleanup_result['space_freed']} bytes freed"
        )
        return cleanup_result

    # Private helper methods

    async def _create_workspace_structure(self, config: WorkspaceConfig) -> None:
        """Create the directory structure for a workspace."""
        workspace_prefix = f"workspaces/{config.workspace_id}/"

        # Create workspace marker
        workspace_info = {
            "workspace_id": config.workspace_id,
            "workspace_type": config.workspace_type.value,
            "owner_agent_id": config.owner_agent_id,
            "created_at": datetime.utcnow().isoformat(),
        }

        await self.storage.upload_data(
            bucket_name=self.storage.workspaces_bucket,
            object_key=f"{workspace_prefix}.workspace",
            data=json.dumps(workspace_info),
            content_type="application/json",
        )

        # Create subdirectories
        for subdir in ["files/", "temp/", "shared/", "backups/"]:
            await self.storage.upload_data(
                bucket_name=self.storage.workspaces_bucket,
                object_key=f"{workspace_prefix}{subdir}.gitkeep",
                data="",
                content_type="text/plain",
            )

    async def _save_workspace_config(self, config: WorkspaceConfig) -> None:
        """Save workspace configuration to storage."""
        config_data = {
            "workspace_id": config.workspace_id,
            "workspace_type": config.workspace_type.value,
            "owner_agent_id": config.owner_agent_id,
            "authorized_agents": config.authorized_agents,
            "conflict_resolution": config.conflict_resolution.value,
            "auto_sync": config.auto_sync,
            "sync_interval": config.sync_interval,
            "max_versions": config.max_versions,
            "retention_days": config.retention_days,
            "updated_at": datetime.utcnow().isoformat(),
        }

        await self.storage.upload_data(
            bucket_name=self.storage.workspaces_bucket,
            object_key=f"configs/{config.workspace_id}.json",
            data=json.dumps(config_data),
            content_type="application/json",
        )

    async def _load_workspace_configs(self) -> None:
        """Load all workspace configurations from storage."""
        try:
            objects = await self.storage.list_objects(
                bucket_name=self.storage.workspaces_bucket, prefix="configs/"
            )

            for obj in objects:
                if obj.object_key.endswith(".json"):
                    try:
                        config = await self._load_workspace_config_from_object(
                            obj.object_key
                        )
                        if config:
                            self.active_workspaces[config.workspace_id] = config
                    except Exception as e:
                        logger.warning(
                            f"Failed to load workspace config {obj.object_key}: {e}"
                        )

            logger.info(
                f"Loaded {len(self.active_workspaces)} workspace configurations"
            )

        except Exception as e:
            logger.warning(f"Failed to load workspace configurations: {e}")

    async def _load_workspace_config(
        self, workspace_id: str
    ) -> WorkspaceConfig | None:
        """Load a specific workspace configuration."""
        try:
            return await self._load_workspace_config_from_object(
                f"configs/{workspace_id}.json"
            )
        except Exception:
            return None

    async def _load_workspace_config_from_object(
        self, object_key: str
    ) -> WorkspaceConfig | None:
        """Load workspace config from storage object."""
        try:
            data = await self.storage.download_data(
                bucket_name=self.storage.workspaces_bucket, object_key=object_key
            )

            config_data = json.loads(data.decode("utf-8"))

            return WorkspaceConfig(
                workspace_id=config_data["workspace_id"],
                workspace_type=WorkspaceType(config_data["workspace_type"]),
                owner_agent_id=config_data["owner_agent_id"],
                authorized_agents=config_data["authorized_agents"],
                conflict_resolution=ConflictResolution(
                    config_data.get("conflict_resolution", "last_writer_wins")
                ),
                auto_sync=config_data.get("auto_sync", True),
                sync_interval=config_data.get("sync_interval", 30.0),
                max_versions=config_data.get("max_versions", 10),
                retention_days=config_data.get("retention_days", 30),
            )

        except Exception as e:
            logger.error(f"Failed to load workspace config from {object_key}: {e}")
            return None

    def _check_read_permission(self, workspace: WorkspaceConfig, agent_id: str) -> bool:
        """Check if agent has read permission for workspace."""
        return (
            agent_id == workspace.owner_agent_id
            or agent_id in workspace.authorized_agents
            or workspace.workspace_type
            in [WorkspaceType.PROJECT_SHARED, WorkspaceType.SYSTEM_SHARED]
        )

    def _check_write_permission(
        self, workspace: WorkspaceConfig, agent_id: str
    ) -> bool:
        """Check if agent has write permission for workspace."""
        return (
            agent_id == workspace.owner_agent_id
            or agent_id in workspace.authorized_agents
        )

    async def _handle_file_conflict(
        self,
        workspace: WorkspaceConfig,
        file_path: str,
        agent_id: str,
        existing_metadata: Any,
    ) -> FileConflict | None:
        """Handle file conflicts based on workspace strategy."""
        if workspace.conflict_resolution == ConflictResolution.LAST_WRITER_WINS:
            # Allow overwrite - no conflict
            return None

        # Create conflict record
        conflict = FileConflict(
            file_path=file_path,
            workspace_id=workspace.workspace_id,
            conflicting_versions=[
                {
                    "agent_id": agent_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "write",
                }
            ],
            conflict_type="concurrent_modification",
            detected_at=datetime.utcnow(),
            resolution_strategy=workspace.conflict_resolution,
        )

        if workspace.conflict_resolution == ConflictResolution.AGENT_PRIORITY:
            # Auto-resolve based on agent priority (simplified)
            if agent_id == workspace.owner_agent_id:
                conflict.resolved = True
                conflict.resolution_result = "owner_priority"
                return None

        return conflict

    async def _get_workspace_metadata(
        self, workspace_id: str, config_data: dict
    ) -> WorkspaceMetadata:
        """Get metadata for a workspace."""
        # Count files and calculate size
        files = await self.storage.list_objects(
            bucket_name=self.storage.workspaces_bucket,
            prefix=f"workspaces/{workspace_id}/files/",
        )

        total_size = sum(obj.size for obj in files)

        return WorkspaceMetadata(
            workspace_id=workspace_id,
            workspace_type=WorkspaceType(config_data["workspace_type"]),
            owner_agent_id=config_data["owner_agent_id"],
            created_at=datetime.fromisoformat(
                config_data.get("created_at", "2024-01-01T00:00:00")
            ),
            last_accessed=datetime.utcnow(),  # Would be tracked separately
            last_modified=datetime.fromisoformat(
                config_data.get("updated_at", "2024-01-01T00:00:00")
            ),
            file_count=len(files),
            total_size=total_size,
            version_count=0,  # Would require separate tracking
        )

    async def _update_workspace_timestamp(
        self, workspace_id: str, access_only: bool = False
    ) -> None:
        """Update workspace timestamp."""
        # This would update workspace metadata
        # For now, we'll skip the implementation as it requires additional tracking
        pass

    async def _start_sync_task(self, config: WorkspaceConfig) -> None:
        """Start automatic sync task for workspace."""
        if config.workspace_id in self.sync_tasks:
            return

        async def sync_loop():
            while True:
                try:
                    await asyncio.sleep(config.sync_interval)
                    await self.sync_workspace(config.workspace_id)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(
                        f"Sync task error for workspace {config.workspace_id}: {e}"
                    )

        task = asyncio.create_task(sync_loop())
        self.sync_tasks[config.workspace_id] = task

    async def _check_file_sync_conflicts(
        self, workspace: WorkspaceConfig, file_info: dict
    ) -> None:
        """Check for sync conflicts in a file."""
        # This would implement conflict detection logic
        # For now, we'll assume no conflicts
        pass

    async def _attempt_merge_resolution(self, conflict: FileConflict) -> None:
        """Attempt to automatically merge conflicting versions."""
        # This would implement automatic merge logic
        # For now, we'll mark as requiring manual intervention
        conflict.resolution_result = "merge_failed_manual_required"


# Global workspace manager instance
workspace_manager: WorkspaceManager | None = None


async def get_workspace_manager() -> WorkspaceManager:
    """Get the global workspace manager instance."""
    global workspace_manager

    if workspace_manager is None:
        workspace_manager = WorkspaceManager()
        await workspace_manager.initialize()

    return workspace_manager


async def initialize_workspace_manager() -> WorkspaceManager:
    """Initialize global workspace manager instance."""
    global workspace_manager

    workspace_manager = WorkspaceManager()
    await workspace_manager.initialize()

    return workspace_manager
