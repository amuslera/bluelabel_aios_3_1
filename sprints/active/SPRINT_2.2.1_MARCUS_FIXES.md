# Sprint 2.2.1: Marcus Integration Fixes (Mini-Sprint)

## Sprint Goal
Fix the 5 critical integration issues discovered during Marcus trial testing to ensure he's ready for multi-agent collaboration.

## Duration
Start: June 2025 - Session 3 (continued)
End: June 2025 - Session 3 
Sprint Length: 30-45 minutes (mini-sprint)

## Background
During Emily development, we discovered 5 critical integration issues with Marcus that prevent him from working properly. These were documented in `MARCUS_TRIAL_FINDINGS.md` and need to be fixed before multi-agent collaboration.

## Issues to Fix

| ID | Issue | Priority | Estimated Time | Status |
|----|-------|----------|----------------|--------|
| MARCUS-001 | Missing `_execute_task_internal` method | High | 10 min | ✅ COMPLETE |
| MARCUS-002 | MessageQueue parameter mismatch | High | 5 min | ✅ COMPLETE |
| MARCUS-003 | Missing agent attributes | Medium | 10 min | ✅ COMPLETE |
| MARCUS-004 | LLM integration missing model_id | Medium | 10 min | ✅ COMPLETE |
| MARCUS-005 | AgentConfig JSON serialization issues | Low | 5 min | ✅ COMPLETE |

## Detailed Issue Descriptions

### MARCUS-001: Missing Abstract Method Implementation ❌
**Issue**: `BackendAgent` missing `_execute_task_internal` method required by `BaseAgent`
**Error**: `TypeError: Can't instantiate abstract class BackendAgent with abstract method _execute_task_internal`
**Fix**: Add the missing method with proper task routing
**File**: `/src/agents/specialists/backend_agent.py`

### MARCUS-002: MessageQueue Parameter Mismatch ❌
**Issue**: `MessageQueue` constructor called with `agent_id` parameter that doesn't exist
**Error**: `TypeError: MessageQueue.__init__() got an unexpected keyword argument 'agent_id'`
**Fix**: Remove the invalid parameter from initialization
**File**: `/src/agents/specialists/backend_agent.py`

### MARCUS-003: Missing Agent Attributes ❌ 
**Issue**: Various agent attributes not properly initialized
**Fix**: Ensure all required attributes are set during initialization
**File**: `/src/agents/specialists/backend_agent.py`

### MARCUS-004: LLM Integration Missing model_id ❌
**Issue**: LLM calls failing due to missing required `model_id` parameter
**Error**: `ValidationError: Field required [type=missing, input_value=...`
**Fix**: Pass model_id parameter in all LLM integration calls
**File**: `/src/agents/specialists/backend_agent.py`

### MARCUS-005: AgentConfig JSON Serialization ❌
**Issue**: AgentConfig objects can't be serialized properly for message passing
**Fix**: Ensure AgentConfig is JSON serializable or convert to dict
**File**: `/src/agents/specialists/backend_agent.py`

## Success Criteria
- [x] Marcus can be instantiated without errors
- [x] Marcus can handle basic task execution
- [x] Marcus can send/receive messages via queue
- [x] Marcus integration test passes
- [x] No remaining abstract method errors
- [x] All JSON serialization works properly

## Testing Plan
1. Run Marcus simple integration test
2. Verify Marcus can be created and initialized
3. Test basic task execution
4. Test message queue communication
5. Run comprehensive Marcus test suite

## Dependencies
- Lessons learned from Emily's successful implementation
- MARCUS_TRIAL_FINDINGS.md documentation
- Emily's working patterns to replicate

## Definition of Done
- [ ] All 5 issues resolved
- [ ] Marcus integration test passes
- [ ] No errors in Marcus instantiation
- [ ] Marcus ready for multi-agent collaboration
- [ ] Documentation updated

---

**Sprint Status**: COMPLETE ✅
**Last Update**: Sprint Completion (June 2025 - Session 3)

## Progress Log

### Sprint Planning Complete ✅
**Completed**: Session 3, continuation after Sprint 2.3
- Identified 5 specific integration issues from trial findings
- Prioritized fixes based on severity and impact
- Estimated 40 minutes total for all fixes
- Set up mini-sprint structure following successful Sprint 2.3 pattern

**Next**: MARCUS-001 - Fix missing `_execute_task_internal` method