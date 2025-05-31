"""
Mock LLM provider for testing and demonstration purposes.

Provides simulated responses that demonstrate the CTO Agent capabilities
without requiring real API keys.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, AsyncIterator, Optional

from .base import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ModelInfo,
    ModelCapability,
    ModelSize,
    ModelType,
    ProviderConfig,
    ProviderHealthStatus,
)

logger = logging.getLogger(__name__)


class MockConfig(ProviderConfig):
    """Configuration for mock provider."""
    
    response_delay: float = 1.0  # Simulate API delay
    failure_rate: float = 0.0    # Simulate API failures (0.0 = never fail)


class MockProvider(LLMProvider):
    """
    Mock LLM provider that generates simulated responses.
    
    Useful for testing, development, and demonstrations when
    real API keys are not available.
    """
    
    # Mock model definitions
    MOCK_MODELS = {
        "mock-cto-model": ModelInfo(
            id="mock-cto-model",
            name="Mock CTO Model",
            provider="mock",
            model_type=ModelType.CHAT,
            size=ModelSize.LARGE,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING,
                ModelCapability.ANALYSIS,
            ],
            context_length=8192,
            input_cost_per_token=0.0,  # Free for testing
            output_cost_per_token=0.0,
            max_requests_per_minute=1000,
            supports_streaming=True,
            supports_functions=False,
            privacy_level="local",
            performance_tier=3,
            availability=1.0,
        ),
    }
    
    def __init__(self, config: MockConfig):
        """Initialize mock provider."""
        super().__init__(config)
        self.config: MockConfig = config
        self._request_count = 0
    
    async def initialize(self) -> None:
        """Initialize the mock provider."""
        logger.info("Initializing mock LLM provider")
        self._models = self.MOCK_MODELS.copy()
        logger.info(f"Mock provider initialized with {len(self._models)} models")
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a mock response."""
        start_time = time.time()
        self._request_count += 1
        
        # Simulate API delay
        if self.config.response_delay > 0:
            await asyncio.sleep(self.config.response_delay)
        
        # Simulate failure rate
        if self.config.failure_rate > 0:
            import random
            if random.random() < self.config.failure_rate:
                raise Exception("Simulated API failure")
        
        # Extract user message content
        user_content = ""
        for message in request.messages:
            if message.get("role") == "user":
                user_content = message.get("content", "")
                break
        
        # Generate mock response based on content
        mock_content = self._generate_mock_content(user_content)
        
        response_time = (time.time() - start_time) * 1000
        
        # Simulate token usage
        input_tokens = len(user_content.split()) * 1.3  # Rough approximation
        output_tokens = len(mock_content.split()) * 1.3
        
        return LLMResponse(
            content=mock_content,
            model_id=request.model_id,
            provider=self.provider_name,
            input_tokens=int(input_tokens),
            output_tokens=int(output_tokens),
            total_tokens=int(input_tokens + output_tokens),
            input_cost=0.0,  # Mock provider is free
            output_cost=0.0,
            total_cost=0.0,
            response_time_ms=response_time,
            finish_reason="stop",
            request_id=f"mock_req_{self._request_count}",
        )
    
    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate a mock streaming response."""
        content = await self.generate(request)
        
        # Stream the response word by word
        words = content.content.split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.1)  # Simulate streaming delay
    
    async def get_models(self) -> list[ModelInfo]:
        """Get list of mock models."""
        return list(self._models.values())
    
    async def health_check(self) -> ProviderHealthStatus:
        """Perform mock health check."""
        return ProviderHealthStatus(
            provider_name=self.provider_name,
            is_healthy=True,
            response_time_ms=50.0,  # Fast response
            available_models=list(self._models.keys()),
            status_message="Mock provider is always healthy",
        )
    
    async def shutdown(self) -> None:
        """Shutdown mock provider."""
        logger.info("Mock provider shutdown completed")
    
    def _generate_mock_content(self, user_content: str) -> str:
        """Generate mock content based on user input."""
        user_lower = user_content.lower()
        
        # Architecture and technology decisions
        if any(word in user_lower for word in ["architecture", "messaging", "websocket", "grpc", "message queue"]):
            return self._mock_architecture_decision()
        
        # Code review responses
        elif any(word in user_lower for word in ["code review", "review code", "code quality"]):
            return self._mock_code_review()
        
        # Technical strategy
        elif any(word in user_lower for word in ["strategy", "roadmap", "planning", "technical plan"]):
            return self._mock_technical_strategy()
        
        # General CTO responses
        else:
            return self._mock_general_cto_response(user_content)
    
    def _mock_architecture_decision(self) -> str:
        """Generate mock architecture decision response."""
        return """# 🏗️ Architectural Analysis

## Executive Summary
After evaluating the messaging architecture options for AIOSv3's real-time agent collaboration, I recommend implementing **gRPC with bidirectional streaming** as our primary solution, with WebSockets as a fallback for browser-based agents.

## Technical Recommendation

### Primary Choice: gRPC with Bidirectional Streaming

**Rationale:**
- **Performance**: Sub-100ms latency for agent-to-agent communication
- **Type Safety**: Protocol Buffers provide schema evolution and strong typing
- **Scalability**: Built for high-throughput, concurrent connections
- **Ecosystem**: Excellent Python/Go support, cloud-native integration

**Architecture:**
```
[Agent A] <--gRPC--> [Message Router] <--gRPC--> [Agent B]
           ^                                    ^
           |           [WebSocket Gateway]     |
           +------------ [Browser Agents] ----+
```

### Fallback: WebSockets for Browser Integration
- Use WebSocket-to-gRPC bridge for browser-based agents
- Maintains performance for core agent communication
- Provides flexibility for future UI integrations

## Implementation Considerations

**Scalability**: 
- gRPC connection pooling supports 100+ concurrent agents
- Horizontal scaling via load balancers with session affinity
- Message queuing for offline agent handling

**Performance**: 
- Expected latency: 50-200ms for complex routing decisions
- Throughput: 10,000+ messages/second per service instance
- Connection overhead: ~2MB memory per active agent

**Operational**: 
- Docker containers with health checks
- Kubernetes service mesh for traffic management
- Prometheus metrics for monitoring

**Cost**: 
- Infrastructure: ~$200/month for 100 agents
- Development: 4-6 weeks implementation
- Operational overhead: Low (existing DevOps practices)

## Next Steps

1. **Week 1-2**: Implement gRPC service definitions and basic routing
2. **Week 3-4**: Add agent authentication and message persistence
3. **Week 5-6**: WebSocket bridge and load testing
4. **Week 6**: Production deployment and monitoring setup

## Risk Assessment

**Low Risk:**
- Team has strong gRPC experience
- Well-established technology stack
- Clear migration path from current architecture

**Mitigation:**
- Prototype implementation in first week
- Performance benchmarks before full commitment
- WebSocket fallback provides flexibility

This architecture balances performance, maintainability, and team expertise while providing a clear path to 10x scale."""

    def _mock_code_review(self) -> str:
        """Generate mock code review response."""
        return """# 🔍 CTO Code Review

## Overall Assessment
The code demonstrates solid engineering practices with good separation of concerns. There are opportunities to improve scalability and maintainability through strategic refactoring.

## Detailed Analysis

### Strengths
✅ **Architecture**: Clean separation of routing, providers, and agent logic
✅ **Error Handling**: Comprehensive exception handling with recovery strategies
✅ **Observability**: Good logging and metrics collection
✅ **Testing**: Unit tests cover core functionality

### Areas for Improvement

**1. Performance Optimization**
- Consider connection pooling for LLM providers
- Implement request batching for cost optimization
- Add response caching for repeated queries

**2. Scalability Concerns**
- Memory management for long-running agent conversations
- Database connection pooling for Redis operations
- Rate limiting implementation could be more sophisticated

**3. Code Quality**
- Some functions exceed 50 lines (consider breaking down)
- Type hints could be more specific in provider interfaces
- Configuration management needs centralization

## Architecture Impact

**Design Patterns**: 
- Excellent use of Strategy pattern for routing
- Factory pattern for agent creation is well-implemented
- Consider adding Observer pattern for event notifications

**Scalability**: 
- Current design supports horizontal scaling
- Agent state management is stateless-friendly
- Message queuing abstraction allows for future optimization

**Maintainability**: 
- Good interface abstractions
- Configuration externalization needed
- Documentation could be enhanced

**Technical Debt**: 
- Minimal debt introduction
- Some hardcoded values should be configurable
- Legacy compatibility maintained appropriately

## Recommendations

1. **Immediate (This Sprint)**:
   - Implement configuration management system
   - Add integration tests for end-to-end workflows
   - Optimize memory usage in conversation management

2. **Next Sprint**:
   - Implement connection pooling
   - Add comprehensive monitoring dashboards
   - Performance optimization based on load testing

3. **Technical Strategy**:
   - Plan for agent mesh architecture
   - Design event-driven architecture for notifications
   - Consider implementing CQRS for complex state management

**Approval**: ✅ Ready for production with noted improvements
**Priority**: Address configuration management before next release"""

    def _mock_technical_strategy(self) -> str:
        """Generate mock technical strategy response."""
        return """# 🎯 Technical Strategy & Planning

## Strategic Context
AIOSv3 represents a significant evolution in AI agent platforms. Our strategic focus should be on building a scalable, reliable foundation that enables rapid innovation while maintaining operational excellence.

## Strategic Recommendation

**Phase 1 (Q1 2024): Foundation Consolidation**
- Complete Enhanced BaseAgent framework rollout
- Implement production-grade monitoring and observability
- Establish CI/CD pipeline with automated testing

**Phase 2 (Q2 2024): Scale & Performance**
- Multi-region deployment architecture
- Advanced routing algorithms with ML optimization
- Agent collaboration patterns and best practices

**Phase 3 (Q3 2024): Innovation Platform**
- Agent marketplace and plugin ecosystem
- Advanced reasoning capabilities
- Real-time collaborative decision making

## Detailed Strategy

### Technical Architecture Evolution

**Current State**: Solid foundation with modular components
**Target State**: Cloud-native, event-driven, globally distributed

**Key Initiatives**:
1. **Event-Driven Architecture**: Transition from synchronous to event-based communication
2. **Service Mesh**: Implement Istio for advanced traffic management
3. **Data Strategy**: Real-time analytics for agent performance optimization

### Team & Capability Development

**Current Skills**: Strong Python, growing Kubernetes expertise
**Needed Skills**: Distributed systems, ML optimization, security

**Investment Plan**:
- 2 senior engineers: Distributed systems expertise
- 1 ML engineer: Agent optimization and routing intelligence  
- DevOps engineer: Production operations and reliability

### Technology Roadmap

**Near-term (6 months)**:
- gRPC-based communication
- Redis cluster for distributed state
- Prometheus/Grafana monitoring stack

**Medium-term (12 months)**:
- Multi-cloud deployment
- ML-driven routing optimization
- Advanced security and compliance

## Success Metrics

**Technical**:
- 99.9% uptime SLA
- <100ms agent-to-agent communication latency
- 10x scaling capability (1000+ concurrent agents)

**Business**:
- 50% reduction in operational costs through optimization
- 2x faster feature delivery through improved platform
- 90% developer satisfaction with platform tools

**Team**:
- 100% team members trained on new architecture
- <2 week onboarding time for new engineers
- 80% internal tool adoption rate

**Operational**:
- Zero-downtime deployments
- <5 minute incident response time
- 99% automated test coverage

## Roadmap

### Q1 2024: Foundation (Months 1-3)
- ✅ Enhanced BaseAgent framework
- 🔄 Production monitoring implementation
- 📋 Automated testing pipeline
- 📋 Documentation and runbooks

### Q2 2024: Scale (Months 4-6)
- Event-driven architecture implementation
- Multi-region deployment
- Performance optimization initiative
- Security hardening

### Q3 2024: Innovation (Months 7-9)
- Agent collaboration patterns
- ML-driven routing optimization
- Developer experience improvements
- Beta customer onboarding

**Investment Required**: $2M annually (team + infrastructure)
**Expected ROI**: 300% through operational efficiency and market opportunity
**Risk Level**: Medium (well-understood technologies, experienced team)"""

    def _mock_general_cto_response(self, user_content: str) -> str:
        """Generate general CTO response."""
        return f"""# 🎯 CTO Analysis

Thank you for bringing this technical question to my attention. Based on my analysis of the situation and our current AIOSv3 platform context, here's my assessment:

## Technical Perspective

The question you've raised touches on important aspects of our platform architecture and engineering strategy. From a CTO standpoint, I consider several factors:

1. **Technical Excellence**: How does this align with our engineering best practices?
2. **Business Impact**: What's the potential value and risk to our product?
3. **Team Capability**: Do we have the skills and resources to execute effectively?
4. **Strategic Alignment**: How does this fit our long-term technical roadmap?

## Analysis

**Context**: {user_content[:200]}{"..." if len(user_content) > 200 else ""}

**Assessment**: This requires careful consideration of our current architecture, team capabilities, and strategic priorities. I recommend we approach this systematically with proper evaluation criteria.

**Technical Considerations**:
- Scalability implications for our agent platform
- Integration with existing Enhanced BaseAgent framework
- Performance impact on current operations
- Maintenance and operational overhead

**Business Considerations**:
- Implementation timeline and resource requirements
- Risk assessment and mitigation strategies
- Alignment with product roadmap and customer needs

## Key Takeaways

1. **Thorough Analysis Required**: Complex technical decisions need comprehensive evaluation
2. **Team Collaboration**: Engineering team input essential for implementation planning
3. **Incremental Approach**: Consider phased implementation to minimize risk
4. **Success Metrics**: Define clear criteria for measuring outcomes

## Recommended Actions

1. **Technical Deep Dive**: Schedule architecture review session with senior engineers
2. **Prototype Development**: Build proof of concept to validate approach
3. **Risk Assessment**: Identify potential challenges and mitigation strategies
4. **Implementation Planning**: Create detailed timeline with milestones and dependencies

I'm confident our team can address this effectively with proper planning and execution. Let's schedule a technical review session to dive deeper into the specifics.

---
*CTO Agent | {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""