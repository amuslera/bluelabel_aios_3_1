"""
Message routing configuration for AIOSv3.

Defines routing rules, exchange topologies, and message patterns for
efficient agent-to-agent communication.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Standard message types for agent communication."""

    TASK = "task"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    NOTIFICATION = "notification"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    SYSTEM_COMMAND = "system_command"


class RoutingPattern(Enum):
    """Standard routing patterns."""

    DIRECT = "direct"  # agent.{agent_id}.{message_type}
    BROADCAST = "broadcast"  # broadcast.{message_type}
    FANOUT = "fanout"  # fanout.{group}
    TOPIC = "topic"  # topic.{category}.{subcategory}
    SYSTEM = "system"  # system.{command}


@dataclass
class ExchangeConfig:
    """Configuration for RabbitMQ exchanges."""

    name: str
    type: str  # direct, topic, fanout, headers
    durable: bool = True
    auto_delete: bool = False
    arguments: Optional[Dict[str, Any]] = None


@dataclass
class QueueConfig:
    """Configuration for RabbitMQ queues."""

    name_pattern: str  # Pattern for queue naming
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    max_length: int | None = None
    message_ttl: int | None = None
    dead_letter_exchange: str | None = None
    dead_letter_routing_key: str | None = None


@dataclass
class RoutingRule:
    """Defines how messages should be routed."""

    pattern: str
    exchange: str
    queue_config: QueueConfig
    description: str
    priority: int = 5
    enabled: bool = True


class MessageRoutingConfig:
    """
    Central configuration for message routing in AIOSv3.

    Manages:
    - Exchange topology
    - Queue configurations
    - Routing rules
    - Message patterns
    """

    def __init__(self, config_path: str | None = None):
        """Initialize routing configuration."""
        self.exchanges: dict[str, ExchangeConfig] = {}
        self.routing_rules: dict[str, RoutingRule] = {}
        self.queue_configs: dict[str, QueueConfig] = {}

        if config_path:
            self.load_from_file(config_path)
        else:
            self._setup_default_configuration()

    def _setup_default_configuration(self) -> None:
        """Set up default routing configuration."""
        logger.info("Setting up default message routing configuration")

        # Define exchanges
        self.exchanges = {
            "agents": ExchangeConfig(
                name="aiosv3.agents",
                type="topic",
                durable=True,
                arguments={"description": "Main exchange for agent communication"},
            ),
            "broadcast": ExchangeConfig(
                name="aiosv3.broadcast",
                type="fanout",
                durable=True,
                arguments={"description": "Broadcast exchange for system messages"},
            ),
            "system": ExchangeConfig(
                name="aiosv3.system",
                type="direct",
                durable=True,
                arguments={"description": "System commands and control messages"},
            ),
            "dlx": ExchangeConfig(
                name="aiosv3.agents.dlx",
                type="topic",
                durable=True,
                arguments={"description": "Dead letter exchange for failed messages"},
            ),
        }

        # Define standard queue configurations
        self.queue_configs = {
            "agent_direct": QueueConfig(
                name_pattern="agent.{agent_id}",
                durable=True,
                message_ttl=3600000,  # 1 hour
                dead_letter_exchange="aiosv3.agents.dlx",
                dead_letter_routing_key="failed.{agent_id}",
            ),
            "agent_tasks": QueueConfig(
                name_pattern="agent.{agent_id}.tasks",
                durable=True,
                max_length=1000,
                message_ttl=7200000,  # 2 hours
                dead_letter_exchange="aiosv3.agents.dlx",
                dead_letter_routing_key="failed.{agent_id}.tasks",
            ),
            "broadcast": QueueConfig(
                name_pattern="broadcast.{agent_id}",
                durable=False,
                auto_delete=True,
                message_ttl=300000,  # 5 minutes
            ),
            "system": QueueConfig(
                name_pattern="system.{component}",
                durable=True,
                message_ttl=1800000,  # 30 minutes
                dead_letter_exchange="aiosv3.agents.dlx",
                dead_letter_routing_key="failed.system.{component}",
            ),
            "responses": QueueConfig(
                name_pattern="response.{agent_id}.{correlation_id}",
                durable=False,
                exclusive=True,
                auto_delete=True,
                message_ttl=30000,  # 30 seconds
            ),
            "dlx": QueueConfig(
                name_pattern="dlx.{original_routing_key}",
                durable=True,
                message_ttl=86400000,  # 24 hours
            ),
        }

        # Define routing rules
        self.routing_rules = {
            # Direct agent communication
            "agent_direct": RoutingRule(
                pattern="agent.{agent_id}.{message_type}",
                exchange="agents",
                queue_config=self.queue_configs["agent_direct"],
                description="Direct communication to specific agents",
                priority=10,
            ),
            # Task distribution
            "agent_tasks": RoutingRule(
                pattern="task.{agent_type}.{task_type}",
                exchange="agents",
                queue_config=self.queue_configs["agent_tasks"],
                description="Task distribution by agent and task type",
                priority=9,
            ),
            # Broadcast messages
            "broadcast_all": RoutingRule(
                pattern="broadcast.{message_type}",
                exchange="broadcast",
                queue_config=self.queue_configs["broadcast"],
                description="Broadcast messages to all agents",
                priority=7,
            ),
            # System commands
            "system_commands": RoutingRule(
                pattern="system.{command}",
                exchange="system",
                queue_config=self.queue_configs["system"],
                description="System-level commands and control",
                priority=8,
            ),
            # Response routing
            "responses": RoutingRule(
                pattern="response.{agent_id}.{correlation_id}",
                exchange="agents",
                queue_config=self.queue_configs["responses"],
                description="Response messages for request-reply pattern",
                priority=10,
            ),
            # Error and failed message handling
            "error_handling": RoutingRule(
                pattern="error.{agent_id}.{error_type}",
                exchange="agents",
                queue_config=self.queue_configs["agent_direct"],
                description="Error notification and handling",
                priority=6,
            ),
            # Status updates
            "status_updates": RoutingRule(
                pattern="status.{agent_id}.{status_type}",
                exchange="agents",
                queue_config=self.queue_configs["agent_direct"],
                description="Agent status updates and heartbeats",
                priority=5,
            ),
            # Dead letter handling
            "dlx_routing": RoutingRule(
                pattern="failed.{original_routing_key}",
                exchange="dlx",
                queue_config=self.queue_configs["dlx"],
                description="Dead letter queue for failed messages",
                priority=1,
            ),
        }

    def get_routing_key(self, pattern: str, **kwargs) -> str:
        """Generate a routing key from a pattern and parameters."""
        try:
            return pattern.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing parameter {e} for routing pattern {pattern}")
            raise ValueError(f"Missing parameter {e} for routing pattern {pattern}")

    def get_queue_name(self, config: QueueConfig, **kwargs) -> str:
        """Generate a queue name from configuration and parameters."""
        try:
            return config.name_pattern.format(**kwargs)
        except KeyError as e:
            logger.error(
                f"Missing parameter {e} for queue pattern {config.name_pattern}"
            )
            raise ValueError(
                f"Missing parameter {e} for queue pattern {config.name_pattern}"
            )

    def find_routing_rule(self, routing_key: str) -> RoutingRule | None:
        """Find the best matching routing rule for a routing key."""
        # For now, simple exact match - could be enhanced with pattern matching
        for rule_name, rule in self.routing_rules.items():
            if self._matches_pattern(routing_key, rule.pattern):
                return rule
        return None

    def _matches_pattern(self, routing_key: str, pattern: str) -> bool:
        """Check if a routing key matches a pattern."""
        # Simple implementation - could be enhanced with regex or glob patterns
        # For now, just check if the general structure matches
        key_parts = routing_key.split(".")
        pattern_parts = pattern.split(".")

        if len(key_parts) != len(pattern_parts):
            return False

        for key_part, pattern_part in zip(key_parts, pattern_parts, strict=False):
            if pattern_part.startswith("{") and pattern_part.endswith("}"):
                continue  # Wildcard match
            if key_part != pattern_part:
                return False

        return True

    def get_agent_routing_keys(
        self, agent_id: str, agent_type: str = None
    ) -> list[str]:
        """Get all routing keys that an agent should listen to."""
        routing_keys = []

        # Direct messages to agent
        routing_keys.append(f"agent.{agent_id}.*")

        # Task messages by type
        if agent_type:
            routing_keys.append(f"task.{agent_type}.*")

        # Broadcast messages
        routing_keys.append("broadcast.*")

        # Status requests
        routing_keys.append(f"status.{agent_id}.*")

        # Error notifications for this agent
        routing_keys.append(f"error.{agent_id}.*")

        return routing_keys

    def get_exchange_config(self, exchange_name: str) -> ExchangeConfig | None:
        """Get configuration for an exchange."""
        return self.exchanges.get(exchange_name)

    def get_routing_rule(self, rule_name: str) -> RoutingRule | None:
        """Get a specific routing rule."""
        return self.routing_rules.get(rule_name)

    def load_from_file(self, config_path: str) -> None:
        """Load routing configuration from YAML file."""
        try:
            with open(config_path) as f:
                config_data = yaml.safe_load(f)

            # Load exchanges
            if "exchanges" in config_data:
                self.exchanges = {}
                for name, config in config_data["exchanges"].items():
                    self.exchanges[name] = ExchangeConfig(**config)

            # Load queue configs
            if "queue_configs" in config_data:
                self.queue_configs = {}
                for name, config in config_data["queue_configs"].items():
                    self.queue_configs[name] = QueueConfig(**config)

            # Load routing rules
            if "routing_rules" in config_data:
                self.routing_rules = {}
                for name, rule_data in config_data["routing_rules"].items():
                    queue_config_name = rule_data.pop("queue_config")
                    queue_config = self.queue_configs[queue_config_name]
                    rule_data["queue_config"] = queue_config
                    self.routing_rules[name] = RoutingRule(**rule_data)

            logger.info(f"Loaded routing configuration from {config_path}")

        except Exception as e:
            logger.error(f"Failed to load routing configuration: {e}")
            logger.info("Using default configuration")
            self._setup_default_configuration()

    def save_to_file(self, config_path: str) -> None:
        """Save current routing configuration to YAML file."""
        config_data = {
            "exchanges": {
                name: {
                    "name": config.name,
                    "type": config.type,
                    "durable": config.durable,
                    "auto_delete": config.auto_delete,
                    "arguments": config.arguments,
                }
                for name, config in self.exchanges.items()
            },
            "queue_configs": {
                name: {
                    "name_pattern": config.name_pattern,
                    "durable": config.durable,
                    "exclusive": config.exclusive,
                    "auto_delete": config.auto_delete,
                    "max_length": config.max_length,
                    "message_ttl": config.message_ttl,
                    "dead_letter_exchange": config.dead_letter_exchange,
                    "dead_letter_routing_key": config.dead_letter_routing_key,
                }
                for name, config in self.queue_configs.items()
            },
            "routing_rules": {
                name: {
                    "pattern": rule.pattern,
                    "exchange": rule.exchange,
                    "queue_config": self._find_queue_config_name(rule.queue_config),
                    "description": rule.description,
                    "priority": rule.priority,
                    "enabled": rule.enabled,
                }
                for name, rule in self.routing_rules.items()
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)

        logger.info(f"Saved routing configuration to {config_path}")

    def _find_queue_config_name(self, queue_config: QueueConfig) -> str:
        """Find the name of a queue configuration."""
        for name, config in self.queue_configs.items():
            if config == queue_config:
                return name
        return "unknown"

    def validate_configuration(self) -> list[str]:
        """Validate the current configuration and return any issues."""
        issues = []

        # Check that all routing rules reference valid exchanges
        for rule_name, rule in self.routing_rules.items():
            if rule.exchange not in self.exchanges:
                issues.append(
                    f"Routing rule '{rule_name}' references unknown exchange '{rule.exchange}'"
                )

        # Check for duplicate queue patterns that might conflict
        patterns = {}
        for config_name, config in self.queue_configs.items():
            pattern = config.name_pattern
            if pattern in patterns:
                issues.append(
                    f"Duplicate queue pattern '{pattern}' in configs '{patterns[pattern]}' and '{config_name}'"
                )
            patterns[pattern] = config_name

        return issues


# Global routing configuration instance
routing_config = MessageRoutingConfig()
