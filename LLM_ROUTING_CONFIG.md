# LLM Routing Configuration Design

## Overview

The LLM routing system allows flexible assignment of cloud or local models to individual agents, with dynamic routing based on various factors including cost, privacy, performance, and task complexity.

## Configuration Structure

### 1. Model Registry (`config/models.yaml`)

```yaml
models:
  # Cloud Models
  claude-3-opus:
    provider: anthropic
    type: cloud
    model_id: claude-3-opus-20240229
    capabilities:
      - code_generation
      - architecture_design
      - complex_reasoning
    cost_per_1k_tokens:
      input: 0.015
      output: 0.075
    rate_limits:
      requests_per_minute: 50
      tokens_per_minute: 100000
    
  gpt-4-turbo:
    provider: openai
    type: cloud
    model_id: gpt-4-turbo-preview
    capabilities:
      - code_generation
      - general_reasoning
    cost_per_1k_tokens:
      input: 0.01
      output: 0.03
    rate_limits:
      requests_per_minute: 60
      tokens_per_minute: 150000

  # Local Models
  llama-3-70b:
    provider: local
    type: local
    model_path: /models/llama-3-70b
    endpoint: http://localhost:8080
    capabilities:
      - code_generation
      - general_reasoning
    resource_requirements:
      gpu_memory_gb: 48
      cpu_cores: 16
    performance:
      tokens_per_second: 30
      
  deepseek-coder-33b:
    provider: local
    type: local
    model_path: /models/deepseek-coder-33b
    endpoint: http://localhost:8081
    capabilities:
      - code_generation
      - code_completion
    resource_requirements:
      gpu_memory_gb: 24
      cpu_cores: 8
    performance:
      tokens_per_second: 45

  qwen-2-72b:
    provider: local
    type: local
    model_path: /models/qwen-2-72b
    endpoint: http://localhost:8082
    capabilities:
      - general_reasoning
      - multilingual
    resource_requirements:
      gpu_memory_gb: 48
      cpu_cores: 16
    performance:
      tokens_per_second: 25
```

### 2. Agent Configuration (`config/agents.yaml`)

```yaml
agents:
  cto_agent:
    name: "CTO Agent"
    description: "Handles architecture decisions and technical leadership"
    model_preferences:
      primary: claude-3-opus          # Best for complex architectural decisions
      fallback: gpt-4-turbo          # Fallback option
      local_alternative: llama-3-70b  # For privacy-sensitive tasks
    routing_rules:
      - condition: "task.privacy_level == 'high'"
        model: llama-3-70b
      - condition: "task.complexity > 8"
        model: claude-3-opus
      - condition: "cost_limit_reached"
        model: llama-3-70b
    capabilities_required:
      - architecture_design
      - complex_reasoning
      - code_generation

  backend_agent:
    name: "Backend Developer Agent"
    description: "Implements backend services and APIs"
    model_preferences:
      primary: deepseek-coder-33b     # Optimized for coding
      fallback: claude-3-opus         # For complex problems
      budget_mode: llama-3-70b        # Cost-effective option
    routing_rules:
      - condition: "task.type == 'code_generation'"
        model: deepseek-coder-33b
      - condition: "task.complexity > 6"
        model: claude-3-opus
      - condition: "budget_mode == true"
        model: llama-3-70b
    capabilities_required:
      - code_generation
      - code_completion

  frontend_agent:
    name: "Frontend Developer Agent"
    description: "Builds user interfaces and frontend logic"
    model_preferences:
      primary: gpt-4-turbo
      fallback: claude-3-opus
      local_alternative: llama-3-70b
    routing_rules:
      - condition: "task.involves_ui_design"
        model: gpt-4-turbo
      - condition: "task.privacy_level == 'high'"
        model: llama-3-70b
    capabilities_required:
      - code_generation
      - ui_design

  qa_agent:
    name: "QA Engineer Agent"
    description: "Tests code and ensures quality"
    model_preferences:
      primary: llama-3-70b            # Cost-effective for testing
      fallback: gpt-4-turbo
    routing_rules:
      - condition: "task.type == 'test_generation'"
        model: llama-3-70b
      - condition: "task.requires_reasoning"
        model: gpt-4-turbo
    capabilities_required:
      - code_analysis
      - test_generation
```

### 3. Routing Strategy Configuration (`config/routing.yaml`)

```yaml
routing:
  strategies:
    cost_optimized:
      description: "Minimize costs while maintaining quality"
      rules:
        - prefer_local_models: true
        - cloud_budget_per_day: 100.00
        - fallback_to_cloud_threshold: 
            complexity: 7
            confidence: 0.6
    
    performance_optimized:
      description: "Maximum speed and quality"
      rules:
        - prefer_cloud_models: true
        - parallel_requests: true
        - cache_responses: true
        
    privacy_first:
      description: "All processing on local models"
      rules:
        - allow_cloud_models: false
        - required_model_type: local
        
    balanced:
      description: "Balance between cost, performance, and privacy"
      rules:
        - cloud_for_complex_tasks: true
        - local_for_routine_tasks: true
        - dynamic_routing: true

  global_rules:
    - name: "rate_limit_protection"
      condition: "model.rate_limit_approaching"
      action: "switch_to_fallback"
      
    - name: "cost_circuit_breaker"
      condition: "daily_cost > budget * 0.8"
      action: "switch_to_local_only"
      
    - name: "privacy_enforcement"
      condition: "data.contains_pii"
      action: "force_local_model"
      
    - name: "quality_assurance"
      condition: "task.critical and model.type == 'local'"
      action: "require_cloud_verification"

  routing_factors:
    - name: "task_complexity"
      weight: 0.3
      calculation: "based_on_token_count_and_requirements"
      
    - name: "cost_efficiency"
      weight: 0.25
      calculation: "cost_per_token * estimated_tokens"
      
    - name: "privacy_requirements"
      weight: 0.2
      calculation: "data_sensitivity_score"
      
    - name: "performance_needs"
      weight: 0.15
      calculation: "required_response_time"
      
    - name: "model_availability"
      weight: 0.1
      calculation: "current_load_and_rate_limits"
```

### 4. Runtime Configuration API

```python
# Example: Dynamic model assignment via API

# Change agent's primary model
POST /api/agents/{agent_id}/model
{
  "model_id": "llama-3-70b",
  "reason": "switching to local for privacy"
}

# Override routing strategy
POST /api/routing/strategy
{
  "strategy": "privacy_first",
  "duration": "2h"
}

# Set task-specific routing
POST /api/tasks/{task_id}/routing
{
  "force_model": "claude-3-opus",
  "reason": "complex architectural decision"
}
```

## Implementation Example

```python
# core/routing/router.py

from typing import Dict, Optional
import yaml
from dataclasses import dataclass

@dataclass
class RoutingDecision:
    model_id: str
    reason: str
    confidence: float
    estimated_cost: float

class LLMRouter:
    def __init__(self, config_path: str):
        self.models = self._load_models(f"{config_path}/models.yaml")
        self.agents = self._load_agents(f"{config_path}/agents.yaml")
        self.routing = self._load_routing(f"{config_path}/routing.yaml")
        
    def route_request(
        self, 
        agent_id: str, 
        task: Dict,
        context: Dict
    ) -> RoutingDecision:
        """
        Determine which LLM to use for a given agent and task
        """
        agent_config = self.agents[agent_id]
        
        # Check routing rules in order
        for rule in agent_config.routing_rules:
            if self._evaluate_condition(rule.condition, task, context):
                return RoutingDecision(
                    model_id=rule.model,
                    reason=f"Rule: {rule.condition}",
                    confidence=0.9,
                    estimated_cost=self._estimate_cost(rule.model, task)
                )
        
        # Apply routing strategy
        strategy = context.get('routing_strategy', 'balanced')
        model_id = self._apply_strategy(
            strategy, 
            agent_config, 
            task, 
            context
        )
        
        return RoutingDecision(
            model_id=model_id,
            reason=f"Strategy: {strategy}",
            confidence=0.8,
            estimated_cost=self._estimate_cost(model_id, task)
        )
    
    def _evaluate_condition(
        self, 
        condition: str, 
        task: Dict, 
        context: Dict
    ) -> bool:
        """
        Evaluate routing condition
        """
        # Simple implementation - would be more sophisticated
        locals_dict = {'task': task, 'context': context}
        try:
            return eval(condition, {}, locals_dict)
        except:
            return False
    
    def _apply_strategy(
        self,
        strategy_name: str,
        agent_config: Dict,
        task: Dict,
        context: Dict
    ) -> str:
        """
        Apply routing strategy to select model
        """
        strategy = self.routing['strategies'][strategy_name]
        
        if strategy['rules'].get('prefer_local_models'):
            if agent_config.get('local_alternative'):
                return agent_config['local_alternative']
        
        if strategy['rules'].get('prefer_cloud_models'):
            return agent_config['primary']
        
        # Calculate scores for each model
        scores = {}
        for model_id in [
            agent_config['primary'], 
            agent_config.get('fallback'),
            agent_config.get('local_alternative')
        ]:
            if model_id:
                scores[model_id] = self._calculate_model_score(
                    model_id, 
                    task, 
                    context, 
                    strategy
                )
        
        # Return highest scoring model
        return max(scores, key=scores.get)
    
    def _calculate_model_score(
        self,
        model_id: str,
        task: Dict,
        context: Dict,
        strategy: Dict
    ) -> float:
        """
        Calculate model suitability score
        """
        model = self.models[model_id]
        score = 0.0
        
        # Factor in routing factors
        for factor in self.routing['routing_factors']:
            factor_score = self._evaluate_factor(
                factor, 
                model, 
                task, 
                context
            )
            score += factor_score * factor['weight']
        
        return score
```

## Environment-Specific Overrides

```yaml
# config/environments/production.yaml
routing:
  global_overrides:
    max_cloud_spend_per_day: 500.00
    require_local_for_pii: true
    
# config/environments/development.yaml  
routing:
  global_overrides:
    force_local_models: true  # Save costs in dev
    verbose_routing_logs: true
```

## Monitoring and Metrics

```yaml
# Routing metrics to track
metrics:
  - model_usage_by_agent
  - routing_decisions_per_strategy  
  - cost_per_agent_per_day
  - performance_by_model
  - fallback_trigger_rate
  - privacy_rule_activations
```

## Key Features

1. **Per-Agent Configuration**: Each agent can have different model preferences
2. **Rule-Based Routing**: Define conditions for model selection
3. **Strategy Support**: Pre-defined routing strategies (cost, performance, privacy)
4. **Dynamic Routing**: Runtime model switching based on conditions
5. **Cost Management**: Built-in cost tracking and limits
6. **Privacy Controls**: Automatic local routing for sensitive data
7. **Fallback Handling**: Graceful degradation when primary models unavailable
8. **A/B Testing**: Support for experimenting with different models

This configuration approach provides maximum flexibility while maintaining simplicity for common use cases.