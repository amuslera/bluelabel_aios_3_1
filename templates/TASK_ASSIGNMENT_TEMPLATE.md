# Task Assignment Template

## Task Identification
**Task ID**: [SPRINT-XXX]  
**Title**: [Clear, actionable task title]  
**Priority**: [High/Medium/Low]  
**Assigned to**: [Agent Name]  
**Estimated Effort**: [Hours/Days]  

## Task Description
[Detailed description of what needs to be done. Be specific about the expected outcome.]

## Context
[Why this task is important and how it fits into the bigger picture]

## Acceptance Criteria
- [ ] [Specific, measurable criterion 1]
- [ ] [Specific, measurable criterion 2]
- [ ] [Specific, measurable criterion 3]
- [ ] Tests written and passing (>80% coverage)
- [ ] Documentation updated
- [ ] PR created and reviewed

## Technical Requirements
- **Framework/Library**: [Specific tech to use]
- **Integration Points**: [APIs, services to connect with]
- **Performance**: [Any performance requirements]
- **Security**: [Security considerations]

## Dependencies
- **Blocked by**: [List any blocking tasks]
- **Blocks**: [List tasks that depend on this]
- **Needs from other agents**: [Specific requirements]

## Resources
- **Design mockups**: [Link if applicable]
- **API documentation**: [Link if applicable]
- **Related code**: [File paths]
- **Reference examples**: [Similar implementations]

## Definition of Done
- [ ] Code complete and committed
- [ ] All acceptance criteria met
- [ ] Tests passing in CI/CD
- [ ] Code reviewed by CTO agent
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] Stakeholder approval received

## Notes
[Any additional context, warnings, or helpful information]

---

**Example Usage**:

## Task Identification
**Task ID**: SPRINT6-001  
**Title**: Build Control Center Dashboard UI  
**Priority**: High  
**Assigned to**: Alex Rivera (Frontend Agent)  
**Estimated Effort**: 2 days  

## Task Description
Create the main dashboard interface for the Control Center using Textual framework. The dashboard should display real-time agent status, current tasks, and system metrics in a grid layout.

## Context
This is the primary interface users will use to monitor and manage their AI development team. It needs to be intuitive, responsive, and update in real-time.

## Acceptance Criteria
- [ ] Grid layout with 4 main panels implemented
- [ ] Real-time WebSocket updates working
- [ ] Keyboard navigation fully functional
- [ ] Color coding for agent status
- [ ] Responsive to terminal size changes
- [ ] Tests written and passing (>80% coverage)
- [ ] Documentation updated
- [ ] PR created and reviewed

## Technical Requirements
- **Framework/Library**: Textual 0.41.0+
- **Integration Points**: WebSocket server at ws://localhost:8765
- **Performance**: Updates should render <100ms
- **Security**: Validate all incoming WebSocket data

## Dependencies
- **Blocked by**: None
- **Blocks**: SPRINT6-003 (Integration task)
- **Needs from other agents**: WebSocket message format from Backend

## Resources
- **Design mockups**: /designs/control_center_ui.png
- **API documentation**: /docs/websocket_api.md
- **Related code**: /demos/control_center_prototypes/
- **Reference examples**: Textual calculator example

## Definition of Done
- [ ] Code complete and committed
- [ ] All acceptance criteria met
- [ ] Tests passing in CI/CD
- [ ] Code reviewed by CTO agent
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] Stakeholder approval received

## Notes
- Use Rich for styling console output
- Consider accessibility for screen readers
- Add help text for keyboard shortcuts