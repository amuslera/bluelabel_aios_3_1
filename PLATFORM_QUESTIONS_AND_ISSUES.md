# Platform Questions and Issues Log

## Meta Strategy
Using our own AI agents to build the platform (eating our own dogfood) to identify what works and what doesn't. All agents work on development branches with PR reviews.

## Fundamental Questions

### 1. Project Scope & Types
- [ ] What types of projects should Hermes handle?
  - Traditional software development (web apps, APIs)?
  - Data enrichment/scraping projects?
  - Research and analysis tasks?
  - Automation workflows?
  - Other services?
- [ ] How do we categorize projects beyond BUILD/AUTOMATE/ANALYZE?
- [ ] Should different project types route to different conversation flows?

### 2. Hermes Conversation Design
- [ ] What's the optimal conversation flow?
  - How many turns before handoff?
  - When is "enough" information gathered?
  - How to handle ambiguous requests?
- [ ] How should Hermes adapt his responses based on:
  - User technical level?
  - Project complexity?
  - Conversation stage?
- [ ] When should Hermes recognize he doesn't understand vs. asking for clarification?

### 3. Agent Capabilities & Limitations
- [ ] What can our agents realistically do TODAY?
- [ ] What tasks are suitable for autonomous execution?
- [ ] What requires human oversight/review?
- [ ] How do we handle agent mistakes/hallucinations?

### 4. Multi-Agent Orchestration
- [ ] Is the orchestration system ready for real use?
- [ ] How do agents communicate task status?
- [ ] How do we handle dependencies between agents?
- [ ] What's the PR/review workflow for agent code?

### 5. Quality & Safety
- [ ] How do we ensure agents don't break existing code?
- [ ] What's the testing strategy for agent-generated code?
- [ ] How do we validate agent outputs before merging?
- [ ] What are the rollback procedures?

## Observed Issues

### Hermes Issues (from LinkedIn lookup conversation)
1. **Intent Detection Failure**: Classified data enrichment as "explore_platform" with decreasing confidence
2. **Generic Responses**: Kept listing all agents instead of understanding specific need
3. **Loop Behavior**: Asked for more info repeatedly despite clear requirements
4. **No Requirement Extraction**: Missed "127 names", "LinkedIn", "position column"
5. **Confidence Decay**: 50% → 40% → 32% → 26% → 20% instead of increasing

### System Issues
1. **Limited Intent Categories**: BUILD/AUTOMATE/ANALYZE too restrictive
2. **Static System Prompts**: Not adapting to conversation context
3. **No Learning**: Each turn seems disconnected from previous

## Action Items

### Immediate Tests
- [ ] Test basic orchestration with a simple, well-defined task
- [ ] Set up development branch workflow for agents
- [ ] Create PR review process for agent submissions

### Platform Improvements Needed
- [ ] Expand Hermes intent detection vocabulary
- [ ] Implement dynamic system prompts
- [ ] Add requirement extraction patterns
- [ ] Create project type taxonomy

### Process Setup
- [ ] Define which tasks are "agent-safe"
- [ ] Create agent coding standards
- [ ] Set up automated testing for agent PRs
- [ ] Build review checklist

## Test Project Ideas

### Good First Tests (Low Risk)
1. **Documentation Updates**: Have agents update their own docs
2. **Test Writing**: Add unit tests for existing code
3. **Code Comments**: Add docstrings to functions
4. **Simple Refactoring**: Extract constants, rename variables

### Medium Risk Tests
1. **Bug Fixes**: Well-defined, isolated bugs
2. **New Utilities**: Standalone helper functions
3. **Config Updates**: Non-breaking configuration changes

### High Risk (Not Ready Yet)
1. **Core System Changes**: Architecture modifications
2. **API Changes**: Breaking changes to interfaces
3. **Database Migrations**: Schema changes
4. **Security Features**: Authentication/authorization

## Success Metrics
- [ ] Agent task completion rate
- [ ] PR rejection rate
- [ ] Time to merge
- [ ] Bugs introduced per PR
- [ ] Human intervention required

## Questions for Next Session
1. Should we test orchestration with a simple task first?
2. What's our git branch naming convention for agents?
3. How do we handle agent API rate limits?
4. What's the escalation path when agents get stuck?

---
*Last Updated: June 3, 2025*
*Status: Active Planning*