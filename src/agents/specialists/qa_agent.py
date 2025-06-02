"""
Alex Thompson - QA Engineering Agent for AIOSv3.

Specializes in automated testing, bug detection, quality assurance, and team collaboration.
"""

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

from ..base.monitoring_agent import MonitoringAgent
from ..base.agent import AgentConfig
from ..base.types import Task, TaskType, TaskPriority
from ...core.messaging.queue import MessageQueue
from ...core.routing.llm_integration import llm_integration
from .qa_personality import (
    QADynamicPersonality, AlexPersonalityTraits,
    QAMoodState, QAEnergyLevel, QAFocusArea, QAPersonalityState
)
from .test_generator import (
    TestGenerator, TestSuite, TestCase, TestType,
    ProgrammingLanguage, TestingFramework, CodeAnalysis
)
from .bug_detector import (
    BugDetectionEngine, BugReport, BugSeverity, BugCategory,
    BugAnalysisResult, PythonBugDetector, JavaScriptBugDetector
)

logger = logging.getLogger(__name__)


class QATaskType(Enum):
    """Extended task types specific to QA Engineering."""
    
    # Test generation and execution
    TEST_GENERATION = "test_generation"
    TEST_EXECUTION = "test_execution"
    TEST_REVIEW = "test_review"
    TEST_OPTIMIZATION = "test_optimization"
    
    # Quality assurance
    CODE_QUALITY_REVIEW = "code_quality_review"
    BUG_DETECTION = "bug_detection"
    BUG_ANALYSIS = "bug_analysis"
    REGRESSION_TESTING = "regression_testing"
    
    # Performance and security
    PERFORMANCE_TESTING = "performance_testing"
    SECURITY_TESTING = "security_testing"
    LOAD_TESTING = "load_testing"
    STRESS_TESTING = "stress_testing"
    
    # Metrics and reporting
    QUALITY_METRICS = "quality_metrics"
    TEST_COVERAGE_ANALYSIS = "test_coverage_analysis"
    DEFECT_TRACKING = "defect_tracking"
    QUALITY_GATE_ENFORCEMENT = "quality_gate_enforcement"
    
    # Team collaboration
    QA_CONSULTATION = "qa_consultation"
    TEST_STRATEGY_PLANNING = "test_strategy_planning"
    QUALITY_STANDARDS_REVIEW = "quality_standards_review"


class TestFramework(Enum):
    """Supported testing frameworks."""
    
    # Python frameworks
    PYTEST = "pytest"
    UNITTEST = "unittest"
    HYPOTHESIS = "hypothesis"
    
    # JavaScript frameworks
    JEST = "jest"
    VITEST = "vitest"
    MOCHA = "mocha"
    JASMINE = "jasmine"
    
    # E2E frameworks
    PLAYWRIGHT = "playwright"
    CYPRESS = "cypress"
    SELENIUM = "selenium"
    
    # API testing
    POSTMAN = "postman"
    NEWMAN = "newman"
    HTTPIE = "httpie"
    
    # Performance testing
    LOCUST = "locust"
    ARTILLERY = "artillery"
    JMETER = "jmeter"


class QualityStandard(Enum):
    """Quality standards and compliance frameworks."""
    
    CODE_COVERAGE = "code_coverage"
    CYCLOMATIC_COMPLEXITY = "cyclomatic_complexity"
    MAINTAINABILITY_INDEX = "maintainability_index"
    SECURITY_COMPLIANCE = "security_compliance"
    ACCESSIBILITY_COMPLIANCE = "accessibility_compliance"
    PERFORMANCE_BENCHMARKS = "performance_benchmarks"


class AlexPersonality:
    """Alex Thompson's personality traits and communication style."""
    
    # Core personality traits
    TRAITS = {
        "methodical": "Systematic and thorough approach to testing and quality",
        "detail_oriented": "Catches subtle bugs and edge cases others miss",
        "quality_focused": "Never compromises on testing standards or quality",
        "analytical": "Data-driven decisions backed by metrics and evidence",
        "collaborative": "Works effectively with development teams",
        "patient": "Persistent in finding root causes and reproducing issues",
        "proactive": "Anticipates potential issues before they become problems",
    }
    
    # Communication style
    COMMUNICATION_STYLE = {
        "greeting": "Hello team! Alex here, ready to ensure our quality standards 🎯",
        "acknowledgment": "Understood. I'll analyze this thoroughly.",
        "thinking": "Let me examine this systematically...",
        "success": "✅ Quality check passed! Here are the results:",
        "issue_found": "🚨 Quality issue identified:",
        "suggestion": "💡 Quality improvement recommendation:",
        "collaboration": "Let's work together to improve this",
        "analysis": "📊 Based on my analysis:",
        "sign_off": "Quality assured,\n- Alex Thompson, QA Engineer",
    }
    
    # Technical preferences and standards
    TECHNICAL_PREFERENCES = {
        "testing_approach": "Test pyramid with comprehensive coverage",
        "code_quality": "Clean, maintainable, and well-documented code",
        "automation": "Automate repetitive testing tasks",
        "metrics": "Data-driven quality decisions",
        "standards": "Industry best practices and compliance",
        "collaboration": "Early involvement in development process",
    }
    
    @staticmethod
    def format_message(message_type: str, content: str) -> str:
        """Format a message with Alex's personality."""
        style = AlexPersonality.COMMUNICATION_STYLE.get(message_type, "")
        if message_type == "greeting":
            return f"{style}\n{content}"
        elif message_type == "sign_off":
            return f"{content}\n\n{style}"
        else:
            return f"{style} {content}"


class QAAgent(MonitoringAgent):
    """
    Alex Thompson - The QA Engineering Specialist.
    
    Expertise:
    - Automated test generation and execution
    - Bug detection and analysis
    - Quality metrics and compliance
    - Performance and security testing
    - Team collaboration and quality consulting
    """
    
    def __init__(
        self,
        agent_id: str = "alex_thompson",
        name: str = "Alex Thompson",
        config: Optional[AgentConfig] = None,
        **kwargs
    ):
        # Initialize with QA-specific configuration
        if not config:
            config = AgentConfig()
        
        config.name = name
        config.agent_type = "qa_engineer"
        config.capabilities = [
            "test_generation",
            "bug_detection",
            "quality_assurance",
            "performance_testing",
            "security_testing",
            "code_review",
            "metrics_analysis",
            "compliance_checking",
            "team_collaboration"
        ]
        
        super().__init__(agent_id=agent_id, config=config, **kwargs)
        
        # QA-specific attributes
        self.supported_frameworks = {
            framework.value for framework in TestFramework
        }
        self.quality_standards = {
            standard.value for standard in QualityStandard
        }
        
        # Quality metrics tracking
        self.quality_metrics = {
            "tests_generated": 0,
            "bugs_found": 0,
            "quality_issues_resolved": 0,
            "code_reviews_completed": 0,
            "test_coverage_improved": 0,
        }
        
        # Collaboration tracking
        self.team_interactions = {
            "marcus_chen": {"reviews_requested": 0, "issues_reported": 0},
            "emily_rodriguez": {"accessibility_reviews": 0, "ui_tests_created": 0},
        }
        
        # Initialize dynamic personality system
        self.personality = QADynamicPersonality(
            base_traits={
                "methodical": 0.95,
                "detail_oriented": 0.9,
                "quality_focused": 0.9,
                "analytical": 0.85,
                "collaborative": 0.8,
                "patient": 0.75,
            },
            name="Alex Thompson"
        )
        
        # Initialize test generation engine
        self.test_generator = TestGenerator()
        
        # Initialize bug detection engine
        self.bug_detector = BugDetectionEngine()
        
        # Initialize message queue for team collaboration
        self.message_queue = MessageQueue()
        
        # Set up collaboration topics and handlers
        self.collaboration_topics = [
            f"agent.{self.agent_id}.inbox",
            "qa.code_review",
            "qa.test_results", 
            "qa.quality_metrics",
            "qa.bug_reports",
            "team.quality_standards",
            "collaboration.frontend_backend",
            "collaboration.quality_assurance"
        ]
        
        logger.info(f"Alex Thompson (QA Agent) initialized with {len(self.supported_frameworks)} testing frameworks")

    async def _execute_task_internal(self, task: Task, model_id: str) -> Dict[str, Any]:
        """Internal task execution logic required by BaseAgent."""
        
        # Log task start for quality tracking
        self.logger.info(f"Alex starting QA task: {task.type} - {task.description[:100]}...")
        
        # Update personality based on task type
        self._update_personality_for_task(task.type)
        
        # Route to appropriate QA handler based on task type
        if task.type == TaskType.TESTING:
            result = await self.handle_testing_task(task.description)
        elif task.type == TaskType.CODE_REVIEW:
            result = await self.handle_code_review(task.description)
        elif hasattr(QATaskType, task.type.upper()):
            # Handle QA-specific task types
            qa_task_type = getattr(QATaskType, task.type.upper())
            result = await self.handle_qa_specific_task(qa_task_type, task.description)
        else:
            # Handle general tasks with QA perspective
            result = await self.handle_general_task(task.description, task.type)
        
        # Update quality metrics
        self._update_quality_metrics(task.type, result.get("success", False))
        
        # Add Alex's personality to the response
        if result.get("response"):
            # Apply personality-driven formatting based on current mood
            analysis_phrase = self.personality.get_analysis_phrase()
            result["response"] = f"{analysis_phrase} {result['response']}"
            
            # Add personality sign-off
            result["response"] += f"\n\n{self.personality.get_sign_off()}"
        
        return {
            "task_id": task.id,
            "agent_id": self.agent_id,
            "task_type": task.type,
            "result": result,
            "quality_metrics": self.quality_metrics.copy(),
            "personality_state": {
                "mood": self.personality.state.mood.value,
                "energy": self.personality.state.energy.value,
                "focus_area": self.personality.state.focus_area.value,
                "attention_to_detail": self.personality.state.attention_to_detail,
                "collaboration_enthusiasm": self.personality.state.collaboration_enthusiasm,
            },
            "timestamp": datetime.now().isoformat(),
        }

    async def handle_testing_task(self, description: str) -> Dict[str, Any]:
        """Handle general testing tasks."""
        
        self.logger.info("Alex analyzing testing requirements...")
        
        # Analyze complexity for LLM routing
        complexity = self._assess_testing_complexity(description)
        
        # Generate testing strategy using LLM
        prompt = f"""
        As Alex Thompson, a methodical QA Engineer, analyze this testing requirement:
        
        {description}
        
        Provide a comprehensive testing strategy including:
        1. Test types needed (unit, integration, E2E, performance)
        2. Testing frameworks to use
        3. Key test scenarios to cover
        4. Quality metrics to track
        5. Potential edge cases and risks
        
        Be specific and actionable in your recommendations.
        """
        
        llm_response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.agent_id,
            task_type=TaskType.TESTING,
            complexity=complexity,
            max_tokens=800,
            temperature=0.3,  # Lower temperature for consistent QA analysis
        )
        
        return {
            "strategy": llm_response.content,
            "complexity": complexity,
            "frameworks_recommended": self._recommend_frameworks(description),
            "estimated_effort": self._estimate_testing_effort(complexity),
            "success": True,
            "response": llm_response.content
        }

    async def handle_code_review(self, description: str) -> Dict[str, Any]:
        """Handle code review tasks with QA perspective."""
        
        self.logger.info("Alex conducting code quality review...")
        
        # Analyze code review complexity
        complexity = self._assess_code_review_complexity(description)
        
        prompt = f"""
        As Alex Thompson, a detail-oriented QA Engineer, review this code:
        
        {description}
        
        Provide a thorough quality assessment covering:
        1. Code quality and maintainability
        2. Potential bugs and edge cases
        3. Security vulnerabilities
        4. Performance considerations
        5. Testing gaps and recommendations
        6. Compliance with best practices
        
        Be specific about issues found and provide actionable recommendations.
        """
        
        llm_response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.agent_id,
            task_type=TaskType.CODE_REVIEW,
            complexity=complexity,
            max_tokens=1000,
            temperature=0.2,  # Very low temperature for consistent reviews
        )
        
        # Update collaboration metrics
        self.team_interactions["marcus_chen"]["reviews_requested"] += 1
        
        return {
            "review": llm_response.content,
            "complexity": complexity,
            "quality_score": self._calculate_quality_score(llm_response.content),
            "action_items": self._extract_action_items(llm_response.content),
            "success": True,
            "response": llm_response.content
        }

    async def handle_qa_specific_task(self, qa_task_type: QATaskType, description: str) -> Dict[str, Any]:
        """Handle QA-specific task types."""
        
        self.logger.info(f"Alex handling QA task: {qa_task_type.value}")
        
        # Route to specific QA handler
        if qa_task_type == QATaskType.TEST_GENERATION:
            return await self._generate_tests(description)
        elif qa_task_type == QATaskType.BUG_DETECTION:
            return await self._detect_bugs(description)
        elif qa_task_type == QATaskType.QUALITY_METRICS:
            return await self._analyze_quality_metrics(description)
        elif qa_task_type == QATaskType.PERFORMANCE_TESTING:
            return await self._plan_performance_testing(description)
        else:
            # Handle other QA tasks with general QA approach
            return await self._handle_general_qa_task(qa_task_type, description)

    async def handle_general_task(self, description: str, task_type: TaskType) -> Dict[str, Any]:
        """Handle general tasks with QA perspective."""
        
        complexity = self._assess_general_complexity(description)
        
        prompt = f"""
        As Alex Thompson, a QA Engineer, provide insights on this {task_type.value} task:
        
        {description}
        
        Focus on quality, testing, and risk assessment aspects.
        Provide specific, actionable recommendations.
        """
        
        llm_response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.agent_id,
            task_type=task_type,
            complexity=complexity,
            max_tokens=600,
            temperature=0.4,
        )
        
        return {
            "analysis": llm_response.content,
            "qa_perspective": "quality_and_risk_focused",
            "success": True,
            "response": llm_response.content
        }

    # Helper methods for complexity assessment
    def _assess_testing_complexity(self, description: str) -> int:
        """Assess complexity of testing task (1-10 scale)."""
        description_lower = description.lower()
        
        complexity = 3  # Base complexity
        
        # Increase complexity based on testing scope
        if any(term in description_lower for term in ["e2e", "end-to-end", "integration"]):
            complexity += 2
        if any(term in description_lower for term in ["performance", "load", "stress"]):
            complexity += 2
        if any(term in description_lower for term in ["security", "penetration", "vulnerability"]):
            complexity += 2
        if any(term in description_lower for term in ["automation", "framework", "ci/cd"]):
            complexity += 1
        
        return min(complexity, 10)

    def _assess_code_review_complexity(self, description: str) -> int:
        """Assess complexity of code review (1-10 scale)."""
        description_lower = description.lower()
        
        complexity = 4  # Base complexity for code review
        
        # Increase complexity based on code scope
        if any(term in description_lower for term in ["architecture", "system", "framework"]):
            complexity += 2
        if any(term in description_lower for term in ["security", "authentication", "authorization"]):
            complexity += 2
        if any(term in description_lower for term in ["performance", "optimization", "scaling"]):
            complexity += 1
        if len(description) > 1000:  # Large code review
            complexity += 1
        
        return min(complexity, 10)

    def _assess_general_complexity(self, description: str) -> int:
        """Assess complexity of general task (1-10 scale)."""
        return min(3 + len(description) // 500, 8)  # Simple scaling

    # QA-specific helper methods
    def _recommend_frameworks(self, description: str) -> List[str]:
        """Recommend appropriate testing frameworks based on description."""
        recommendations = []
        description_lower = description.lower()
        
        # Python project detection
        if any(term in description_lower for term in ["python", "fastapi", "django", "flask"]):
            recommendations.extend(["pytest", "unittest"])
        
        # JavaScript project detection
        if any(term in description_lower for term in ["javascript", "react", "vue", "node"]):
            recommendations.extend(["jest", "vitest"])
        
        # E2E testing needs
        if any(term in description_lower for term in ["e2e", "end-to-end", "user interface", "ui"]):
            recommendations.extend(["playwright", "cypress"])
        
        # API testing needs
        if any(term in description_lower for term in ["api", "rest", "endpoint"]):
            recommendations.extend(["postman", "newman"])
        
        # Performance testing needs
        if any(term in description_lower for term in ["performance", "load", "stress"]):
            recommendations.extend(["locust", "artillery"])
        
        return recommendations or ["pytest"]  # Default to pytest

    def _estimate_testing_effort(self, complexity: int) -> str:
        """Estimate testing effort based on complexity."""
        if complexity <= 3:
            return "1-2 hours"
        elif complexity <= 6:
            return "4-8 hours"
        elif complexity <= 8:
            return "1-2 days"
        else:
            return "3-5 days"

    def _calculate_quality_score(self, review_content: str) -> int:
        """Calculate a quality score (1-100) based on review content."""
        issues_found = len([line for line in review_content.split('\n') 
                           if any(term in line.lower() for term in ['issue', 'bug', 'problem', 'error'])])
        
        # Simple scoring: fewer issues = higher score
        base_score = 85
        issue_penalty = min(issues_found * 5, 40)
        return max(base_score - issue_penalty, 40)

    def _extract_action_items(self, review_content: str) -> List[str]:
        """Extract action items from review content."""
        action_items = []
        lines = review_content.split('\n')
        
        for line in lines:
            if any(term in line.lower() for term in ['should', 'recommend', 'suggest', 'fix', 'improve']):
                action_items.append(line.strip())
        
        return action_items[:5]  # Limit to top 5 action items

    def _update_quality_metrics(self, task_type: TaskType, success: bool) -> None:
        """Update quality metrics based on task completion."""
        if success:
            if task_type == TaskType.TESTING:
                self.quality_metrics["tests_generated"] += 1
            elif task_type == TaskType.CODE_REVIEW:
                self.quality_metrics["code_reviews_completed"] += 1

    # Placeholder methods for QA-specific tasks (to be implemented in subsequent tasks)
    async def _generate_tests(self, description: str) -> Dict[str, Any]:
        """Generate comprehensive test cases based on description or code."""
        
        self.logger.info("Alex generating comprehensive test suite...")
        
        # Update personality for test generation
        self.personality.update_mood("test_generation_start")
        
        # Parse the request to understand what tests are needed
        test_config = await self._parse_test_generation_request(description)
        
        try:
            if test_config["has_code"]:
                # Generate tests for provided code
                test_suite = self.test_generator.generate_test_suite(
                    code=test_config["code"],
                    language=test_config["language"],
                    framework=test_config["framework"],
                    test_types=test_config["test_types"],
                    coverage_target=test_config.get("coverage_target", 0.8)
                )
            else:
                # Generate tests based on description only
                test_suite = await self._generate_tests_from_description(test_config)
            
            # Update quality metrics
            self.quality_metrics["tests_generated"] += len(test_suite.test_cases)
            self.personality.state.tests_written_today += len(test_suite.test_cases)
            
            # Update personality based on success
            self.personality.update_mood("tests_passing")
            
            return {
                "test_suite": {
                    "name": test_suite.name,
                    "description": test_suite.description,
                    "framework": test_suite.framework.value,
                    "language": test_suite.language.value,
                    "test_count": len(test_suite.test_cases),
                    "coverage_targets": test_suite.coverage_targets,
                    "estimated_time": test_suite.total_estimated_time,
                },
                "test_cases": [
                    {
                        "name": test.name,
                        "description": test.description,
                        "type": test.test_type.value,
                        "framework": test.framework.value,
                        "code": test.code,
                        "complexity": test.complexity,
                        "tags": test.tags,
                        "estimated_time": test.estimated_execution_time,
                    }
                    for test in test_suite.test_cases
                ],
                "recommendations": await self._generate_test_recommendations(test_suite),
                "success": True,
                "response": f"Generated {len(test_suite.test_cases)} test cases for {test_suite.framework.value}"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating tests: {str(e)}")
            return {
                "error": str(e),
                "success": False,
                "response": f"Error generating tests: {str(e)}"
            }

    async def _detect_bugs(self, description: str) -> Dict[str, Any]:
        """Detect bugs and quality issues in provided code."""
        
        self.logger.info("Alex conducting comprehensive bug detection analysis...")
        
        # Update personality for bug detection
        self.personality.update_mood("bug_found", {"severity": "unknown"})
        
        try:
            # Parse the bug detection request
            bug_config = await self._parse_bug_detection_request(description)
            
            if not bug_config["has_code"]:
                # No code provided - offer general guidance
                return await self._provide_bug_detection_guidance(description)
            
            # Perform comprehensive bug analysis
            analysis_result = self.bug_detector.analyze_code(
                code=bug_config["code"],
                language=bug_config["language"],
                file_path=bug_config.get("file_path", "provided_code"),
                include_categories=bug_config.get("categories")
            )
            
            # Update personality based on findings
            if analysis_result.critical_issues:
                self.personality.update_mood("bug_found", {"severity": "critical"})
                self.personality.state.bugs_found_today += len(analysis_result.critical_issues)
            elif analysis_result.total_bugs > 0:
                self.personality.update_mood("bug_found", {"severity": "medium"})
                self.personality.state.bugs_found_today += analysis_result.total_bugs
            else:
                self.personality.update_mood("tests_passing")
            
            # Update quality metrics
            self.quality_metrics["bugs_found"] += analysis_result.total_bugs
            
            # Generate detailed response with Alex's personality
            response = await self._format_bug_analysis_response(analysis_result, bug_config)
            
            return {
                "analysis_result": {
                    "total_bugs": analysis_result.total_bugs,
                    "critical_issues_count": len(analysis_result.critical_issues),
                    "security_score": analysis_result.security_score,
                    "quality_score": analysis_result.quality_score,
                    "maintainability_score": analysis_result.maintainability_score,
                    "summary": analysis_result.analysis_summary,
                },
                "bugs_by_severity": {sev.value: count for sev, count in analysis_result.bugs_by_severity.items()},
                "bugs_by_category": {cat.value: count for cat, count in analysis_result.bugs_by_category.items()},
                "critical_issues": [
                    {
                        "title": bug.title,
                        "description": bug.description,
                        "severity": bug.severity.value,
                        "category": bug.category.value,
                        "line_number": bug.line_number,
                        "suggested_fix": bug.suggested_fix,
                        "confidence_score": bug.confidence_score,
                        "impact_analysis": bug.impact_analysis,
                    }
                    for bug in analysis_result.critical_issues
                ],
                "recommendations": analysis_result.recommendations,
                "detailed_bugs": [
                    {
                        "id": bug.id,
                        "title": bug.title,
                        "description": bug.description,
                        "severity": bug.severity.value,
                        "category": bug.category.value,
                        "bug_type": bug.bug_type.value,
                        "line_number": bug.line_number,
                        "suggested_fix": bug.suggested_fix,
                        "confidence_score": bug.confidence_score,
                        "tags": bug.tags,
                    }
                    for bug in self._get_top_bugs_for_display(analysis_result)
                ],
                "success": True,
                "response": response
            }
            
        except Exception as e:
            self.logger.error(f"Error in bug detection: {str(e)}")
            return {
                "error": str(e),
                "success": False,
                "response": f"Error during bug detection analysis: {str(e)}"
            }

    async def _analyze_quality_metrics(self, description: str) -> Dict[str, Any]:
        """Analyze and track comprehensive quality metrics."""
        
        self.logger.info("Alex analyzing quality metrics and trends...")
        
        # Update personality for metrics analysis
        self.personality.update_mood("analytical")
        
        try:
            # Parse metrics request
            metrics_config = await self._parse_metrics_request(description)
            
            if metrics_config["has_data"]:
                # Analyze provided metrics data
                analysis = await self._analyze_provided_metrics(metrics_config)
            else:
                # Generate quality metrics report for current session/project
                analysis = await self._generate_quality_report(metrics_config)
            
            # Update personality based on quality trends
            if analysis["overall_score"] > 0.8:
                self.personality.update_mood("quality_goal_achieved")
            elif analysis["overall_score"] < 0.6:
                self.personality.update_mood("concerned")
            
            return {
                "quality_analysis": analysis,
                "recommendations": analysis["recommendations"],
                "action_items": analysis["action_items"],
                "trends": analysis.get("trends", {}),
                "benchmarks": analysis.get("benchmarks", {}),
                "success": True,
                "response": analysis["summary"]
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing quality metrics: {str(e)}")
            return {
                "error": str(e),
                "success": False,
                "response": f"Error during quality metrics analysis: {str(e)}"
            }
    
    async def _parse_metrics_request(self, description: str) -> Dict[str, Any]:
        """Parse quality metrics request to understand what analysis is needed."""
        
        description_lower = description.lower()
        
        # Check if metrics data is provided
        has_data = any(keyword in description_lower for keyword in [
            "coverage", "defect", "performance", "metrics", "score", "rate", "time", "count"
        ])
        
        # Extract metrics data if present
        metrics_data = {}
        if has_data:
            # Try to extract numerical values
            coverage_match = re.search(r'coverage[:\s]*(\d+(?:\.\d+)?)', description_lower)
            if coverage_match:
                metrics_data["test_coverage"] = float(coverage_match.group(1))
            
            defect_match = re.search(r'defect[s]?[:\s]*(\d+)', description_lower)
            if defect_match:
                metrics_data["defect_count"] = int(defect_match.group(1))
                
            performance_match = re.search(r'performance[:\s]*(\d+(?:\.\d+)?)', description_lower)
            if performance_match:
                metrics_data["performance_score"] = float(performance_match.group(1))
        
        # Detect specific metric types requested
        requested_metrics = []
        if any(keyword in description_lower for keyword in ["coverage", "test coverage"]):
            requested_metrics.append("test_coverage")
        if any(keyword in description_lower for keyword in ["defect", "bug", "issue"]):
            requested_metrics.append("defect_tracking")
        if any(keyword in description_lower for keyword in ["performance", "speed", "response time"]):
            requested_metrics.append("performance")
        if any(keyword in description_lower for keyword in ["maintainability", "complexity"]):
            requested_metrics.append("maintainability")
        if any(keyword in description_lower for keyword in ["security", "vulnerability"]):
            requested_metrics.append("security")
        
        # Detect time period for analysis
        time_period = "current"
        if any(keyword in description_lower for keyword in ["trend", "over time", "historical"]):
            time_period = "historical"
        elif any(keyword in description_lower for keyword in ["weekly", "week"]):
            time_period = "weekly"
        elif any(keyword in description_lower for keyword in ["monthly", "month"]):
            time_period = "monthly"
        
        return {
            "has_data": has_data,
            "metrics_data": metrics_data,
            "requested_metrics": requested_metrics if requested_metrics else ["overall"],
            "time_period": time_period,
            "description": description
        }
    
    async def _analyze_provided_metrics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze provided metrics data."""
        
        metrics_data = config["metrics_data"]
        analysis = {
            "provided_metrics": metrics_data,
            "analysis_type": "provided_data",
            "scores": {},
            "issues": [],
            "recommendations": [],
            "action_items": [],
        }
        
        # Analyze test coverage
        if "test_coverage" in metrics_data:
            coverage = metrics_data["test_coverage"]
            if coverage > 100:  # Assume percentage
                coverage = coverage / 100
            
            analysis["scores"]["test_coverage"] = coverage
            
            if coverage < 0.6:
                analysis["issues"].append("Test coverage is below 60% - critical gap in testing")
                analysis["recommendations"].append("Increase test coverage to at least 80%")
                analysis["action_items"].append("Write additional unit and integration tests")
            elif coverage < 0.8:
                analysis["issues"].append("Test coverage could be improved")
                analysis["recommendations"].append("Aim for 80%+ test coverage")
            else:
                analysis["recommendations"].append("Excellent test coverage! Maintain current standards")
        
        # Analyze defect count
        if "defect_count" in metrics_data:
            defects = metrics_data["defect_count"]
            analysis["scores"]["defect_density"] = max(0, 1 - (defects * 0.01))  # Simple scoring
            
            if defects > 10:
                analysis["issues"].append(f"High defect count: {defects} issues found")
                analysis["recommendations"].append("Focus on defect prevention and root cause analysis")
                analysis["action_items"].append("Implement more rigorous code review process")
            elif defects > 5:
                analysis["issues"].append(f"Moderate defect count: {defects} issues")
                analysis["recommendations"].append("Continue current quality practices")
            else:
                analysis["recommendations"].append("Low defect count indicates good quality practices")
        
        # Analyze performance
        if "performance_score" in metrics_data:
            perf = metrics_data["performance_score"]
            if perf > 10:  # Assume it's response time in ms, convert to score
                perf_score = max(0, 1 - (perf / 1000))
            else:  # Assume it's already a score
                perf_score = perf
            
            analysis["scores"]["performance"] = perf_score
            
            if perf_score < 0.6:
                analysis["issues"].append("Performance issues detected")
                analysis["recommendations"].append("Investigate and optimize performance bottlenecks")
                analysis["action_items"].append("Run performance profiling and optimization")
        
        # Calculate overall score
        scores = analysis["scores"]
        if scores:
            analysis["overall_score"] = sum(scores.values()) / len(scores)
        else:
            analysis["overall_score"] = 0.7  # Default
        
        # Generate summary
        analysis["summary"] = self._generate_metrics_summary(analysis)
        
        return analysis
    
    async def _generate_quality_report(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive quality report for current project/session."""
        
        # Use current QA metrics from Alex's session
        current_metrics = {
            "tests_generated": self.quality_metrics["tests_generated"],
            "bugs_found": self.quality_metrics["bugs_found"],
            "quality_issues_resolved": self.quality_metrics["quality_issues_resolved"],
            "code_reviews_completed": self.quality_metrics["code_reviews_completed"],
        }
        
        # Calculate scores based on activity
        scores = {}
        
        # Test generation effectiveness
        if current_metrics["tests_generated"] > 0:
            scores["test_generation"] = min(1.0, current_metrics["tests_generated"] / 10)
        else:
            scores["test_generation"] = 0.0
        
        # Bug detection effectiveness
        if current_metrics["bugs_found"] > 0:
            # More bugs found = better detection, but cap at reasonable level
            scores["bug_detection"] = min(1.0, current_metrics["bugs_found"] / 5)
        else:
            scores["bug_detection"] = 0.5  # Neutral if no bugs found
        
        # Quality improvement impact
        if current_metrics["quality_issues_resolved"] > 0:
            scores["quality_improvement"] = min(1.0, current_metrics["quality_issues_resolved"] / 3)
        else:
            scores["quality_improvement"] = 0.0
        
        # Code review thoroughness
        if current_metrics["code_reviews_completed"] > 0:
            scores["code_review"] = min(1.0, current_metrics["code_reviews_completed"] / 5)
        else:
            scores["code_review"] = 0.0
        
        # Team collaboration score
        scores["collaboration"] = self.personality.state.collaboration_enthusiasm
        
        # Overall score
        overall_score = sum(scores.values()) / len(scores) if scores else 0.5
        
        # Generate recommendations based on scores
        recommendations = []
        action_items = []
        
        if scores.get("test_generation", 0) < 0.5:
            recommendations.append("Generate more comprehensive test suites")
            action_items.append("Create test cases for critical system components")
        
        if scores.get("bug_detection", 0) < 0.5:
            recommendations.append("Increase focus on bug detection and code analysis")
            action_items.append("Perform static analysis on codebase")
        
        if scores.get("collaboration", 0) < 0.7:
            recommendations.append("Enhance collaboration with development team")
            action_items.append("Schedule regular quality review sessions")
        
        if overall_score > 0.8:
            recommendations.append("Excellent quality standards - maintain current practices")
        
        # Generate trends (simulated for current session)
        trends = {
            "quality_trend": "improving" if overall_score > 0.7 else "needs_attention",
            "bugs_per_session": current_metrics["bugs_found"],
            "tests_per_session": current_metrics["tests_generated"],
            "productivity_score": overall_score
        }
        
        # Industry benchmarks (example data)
        benchmarks = {
            "test_coverage_target": 0.8,
            "defect_density_target": 0.05,
            "code_review_coverage": 1.0,
            "automated_test_ratio": 0.9
        }
        
        analysis = {
            "analysis_type": "session_report",
            "current_metrics": current_metrics,
            "scores": scores,
            "overall_score": overall_score,
            "recommendations": recommendations,
            "action_items": action_items,
            "trends": trends,
            "benchmarks": benchmarks,
            "summary": self._generate_session_summary(overall_score, current_metrics)
        }
        
        return analysis
    
    def _generate_metrics_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate human-readable summary of metrics analysis."""
        
        overall_score = analysis["overall_score"]
        issues = analysis["issues"]
        
        if overall_score > 0.9:
            quality_level = "Exceptional"
            emoji = "🏆"
        elif overall_score > 0.8:
            quality_level = "Excellent"
            emoji = "✅"
        elif overall_score > 0.7:
            quality_level = "Good"
            emoji = "👍"
        elif overall_score > 0.6:
            quality_level = "Acceptable"
            emoji = "⚠️"
        else:
            quality_level = "Needs Improvement"
            emoji = "🚨"
        
        summary_parts = [
            f"{emoji} Quality Assessment: {quality_level} (Score: {overall_score:.2f}/1.0)",
            ""
        ]
        
        if analysis.get("provided_metrics"):
            summary_parts.append("📊 Analysis of Provided Metrics:")
            for metric, value in analysis["provided_metrics"].items():
                summary_parts.append(f"• {metric.replace('_', ' ').title()}: {value}")
            summary_parts.append("")
        
        if issues:
            summary_parts.append("🔍 Key Issues Identified:")
            for issue in issues[:3]:  # Top 3 issues
                summary_parts.append(f"• {issue}")
            summary_parts.append("")
        
        if analysis.get("trends"):
            summary_parts.append("📈 Quality Trends:")
            trends = analysis["trends"]
            if trends.get("quality_trend") == "improving":
                summary_parts.append("• Quality metrics show positive improvement")
            elif trends.get("quality_trend") == "declining":
                summary_parts.append("• Quality metrics indicate areas needing attention")
            summary_parts.append("")
        
        # Add personality-driven conclusion
        if overall_score > 0.8:
            conclusion = "Quality standards are being maintained at a high level. Continue current practices!"
        elif overall_score > 0.6:
            conclusion = "Quality is generally good with room for targeted improvements."
        else:
            conclusion = "Quality metrics indicate significant opportunities for improvement."
        
        summary_parts.append(conclusion)
        
        return "\n".join(summary_parts)
    
    def _generate_session_summary(self, overall_score: float, metrics: Dict[str, int]) -> str:
        """Generate summary for current QA session."""
        
        summary_parts = [
            f"📊 Alex's QA Session Report (Score: {overall_score:.2f}/1.0)",
            "",
            f"🧪 Tests Generated: {metrics['tests_generated']}",
            f"🐛 Bugs Found: {metrics['bugs_found']}",
            f"✅ Issues Resolved: {metrics['quality_issues_resolved']}",
            f"👀 Code Reviews: {metrics['code_reviews_completed']}",
            "",
        ]
        
        # Personality-driven assessment
        if overall_score > 0.8:
            summary_parts.append("🎉 Excellent QA session! Quality standards are high.")
        elif overall_score > 0.6:
            summary_parts.append("👍 Productive QA session with good quality focus.")
        else:
            summary_parts.append("🔍 QA session shows areas where we can improve quality practices.")
        
        # Add current personality state
        mood = self.personality.state.mood.value
        energy = self.personality.state.energy.value
        summary_parts.append(f"🎭 Current State: {mood.title()}, Energy: {energy}/5")
        
        return "\n".join(summary_parts)

    async def _plan_performance_testing(self, description: str) -> Dict[str, Any]:
        """Plan performance testing strategy."""
        return {"status": "performance_testing_placeholder", "success": True, "response": "Performance testing capability will be implemented in QA-004"}

    async def _handle_general_qa_task(self, qa_task_type: QATaskType, description: str) -> Dict[str, Any]:
        """Handle other QA tasks."""
        return {"status": f"{qa_task_type.value}_placeholder", "success": True, "response": f"QA task {qa_task_type.value} will be implemented in future tasks"}

    async def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report for Alex."""
        base_status = await super().get_status_report()
        
        qa_status = {
            "qa_metrics": self.quality_metrics,
            "supported_frameworks": list(self.supported_frameworks),
            "quality_standards": list(self.quality_standards),
            "team_collaborations": self.team_interactions,
            "personality": {
                "current_mood": self.personality.state.mood.value,
                "energy_level": self.personality.state.energy.value,
                "focus_area": self.personality.state.focus_area.value,
                "attention_to_detail": self.personality.state.attention_to_detail,
                "collaboration_enthusiasm": self.personality.state.collaboration_enthusiasm,
                "quality_standards_strictness": self.personality.state.quality_standards_strictness,
                "bugs_found_today": self.personality.state.bugs_found_today,
                "tests_written_today": self.personality.state.tests_written_today,
            },
        }
        
        base_status.update(qa_status)
        return base_status

    def _update_personality_for_task(self, task_type: TaskType) -> None:
        """Update Alex's personality state based on the incoming task."""
        if task_type == TaskType.TESTING:
            self.personality.update_mood("test_generation_start")
        elif task_type == TaskType.CODE_REVIEW:
            self.personality.update_mood("code_review_start")
        elif task_type in [TaskType.BUG_FIX, TaskType.REFACTORING]:
            self.personality.update_mood("bug_found", {"severity": "medium"})
        elif task_type == TaskType.AGENT_COLLABORATION:
            self.personality.update_mood("team_collaboration")
        
        # Increment interaction count
        self.personality.state.interaction_count += 1

    async def _parse_test_generation_request(self, description: str) -> Dict[str, Any]:
        """Parse test generation request to understand requirements."""
        
        description_lower = description.lower()
        
        # Detect if code is provided
        has_code = any(keyword in description_lower for keyword in [
            "def ", "function", "class ", "import", "from ", "const ", "let ", "var "
        ])
        
        # Extract code if present (simple heuristic)
        code = ""
        if has_code:
            # Try to extract code blocks
            code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', description, re.DOTALL)
            if code_blocks:
                code = code_blocks[0]
            else:
                # Assume entire description is code if no code blocks
                code = description
        
        # Detect programming language
        language = ProgrammingLanguage.PYTHON  # Default
        if any(keyword in description_lower for keyword in ["javascript", "js", "react", "node"]):
            language = ProgrammingLanguage.JAVASCRIPT
        elif any(keyword in description_lower for keyword in ["typescript", "ts"]):
            language = ProgrammingLanguage.TYPESCRIPT
        elif any(keyword in description_lower for keyword in ["java"]):
            language = ProgrammingLanguage.JAVA
        elif any(keyword in description_lower for keyword in ["python", "py", "def ", "import"]):
            language = ProgrammingLanguage.PYTHON
        
        # Detect desired test types
        test_types = []
        if any(keyword in description_lower for keyword in ["unit", "unit test"]):
            test_types.append(TestType.UNIT)
        if any(keyword in description_lower for keyword in ["integration", "integration test"]):
            test_types.append(TestType.INTEGRATION)
        if any(keyword in description_lower for keyword in ["e2e", "end-to-end", "end to end"]):
            test_types.append(TestType.E2E)
        if any(keyword in description_lower for keyword in ["performance", "load", "stress"]):
            test_types.append(TestType.PERFORMANCE)
        if any(keyword in description_lower for keyword in ["security", "penetration", "vulnerability"]):
            test_types.append(TestType.SECURITY)
        if any(keyword in description_lower for keyword in ["api", "rest", "endpoint"]):
            test_types.append(TestType.API)
        
        # Default to unit tests if no specific type mentioned
        if not test_types:
            test_types = [TestType.UNIT]
        
        # Recommend framework based on language and context
        framework = self.test_generator.recommend_framework(
            language=language,
            test_types=test_types,
            project_context={"description": description}
        )
        
        # Detect coverage target
        coverage_target = 0.8  # Default
        coverage_match = re.search(r'(\d+)%?\s*coverage', description_lower)
        if coverage_match:
            coverage_target = float(coverage_match.group(1)) / 100
        
        return {
            "has_code": has_code,
            "code": code,
            "language": language,
            "framework": framework,
            "test_types": test_types,
            "coverage_target": coverage_target,
            "description": description
        }
    
    async def _generate_tests_from_description(self, test_config: Dict[str, Any]) -> TestSuite:
        """Generate tests based on description without specific code."""
        
        # Use LLM to understand the requirements and generate appropriate test structure
        prompt = f"""
        As Alex Thompson, a methodical QA Engineer, analyze this testing requirement:
        
        {test_config['description']}
        
        Generate a test strategy for {test_config['language'].value} using {test_config['framework'].value}.
        
        Provide:
        1. Key test scenarios to cover
        2. Test data requirements
        3. Expected assertions
        4. Setup and teardown needs
        5. Edge cases to consider
        
        Focus on {', '.join([t.value for t in test_config['test_types']])} testing.
        """
        
        llm_response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.agent_id,
            task_type=TaskType.TESTING,
            complexity=6,
            max_tokens=1000,
            temperature=0.3,
        )
        
        # Create a basic test suite based on LLM analysis
        test_suite = TestSuite(
            name=f"Test Suite - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=f"Tests generated from description using {test_config['framework'].value}",
            framework=test_config['framework'],
            language=test_config['language'],
            coverage_targets={"line": test_config['coverage_target']}
        )
        
        # Generate basic test cases for each requested type
        for test_type in test_config['test_types']:
            test_case = self.test_generator.generate_single_test(
                target_function="main_functionality",
                framework=test_config['framework'],
                test_type=test_type,
                context={
                    "language": test_config['language'],
                    "description": test_config['description'],
                    "llm_analysis": llm_response.content
                }
            )
            test_suite.test_cases.append(test_case)
        
        return test_suite
    
    async def _generate_test_recommendations(self, test_suite: TestSuite) -> List[str]:
        """Generate recommendations for improving the test suite."""
        
        recommendations = []
        
        # Coverage recommendations
        if test_suite.coverage_targets.get("line", 0) < 0.8:
            recommendations.append("Consider increasing line coverage target to at least 80%")
        
        # Framework-specific recommendations
        if test_suite.framework == TestingFramework.PYTEST:
            recommendations.append("Consider using pytest fixtures for test data setup")
            recommendations.append("Add parametrized tests for multiple input scenarios")
        elif test_suite.framework == TestingFramework.JEST:
            recommendations.append("Consider using Jest's snapshot testing for UI components")
            recommendations.append("Add mock functions for external dependencies")
        
        # Test type recommendations
        test_types = {test.test_type for test in test_suite.test_cases}
        if TestType.UNIT in test_types and TestType.INTEGRATION not in test_types:
            recommendations.append("Consider adding integration tests to verify component interactions")
        if TestType.SECURITY not in test_types:
            recommendations.append("Add security tests for input validation and injection prevention")
        
        # Complexity recommendations
        avg_complexity = sum(test.complexity for test in test_suite.test_cases) / len(test_suite.test_cases)
        if avg_complexity < 3:
            recommendations.append("Consider adding more comprehensive test scenarios")
        elif avg_complexity > 7:
            recommendations.append("Some tests may be overly complex - consider breaking them down")
        
        return recommendations
    
    async def _parse_bug_detection_request(self, description: str) -> Dict[str, Any]:
        """Parse bug detection request to understand what analysis is needed."""
        
        description_lower = description.lower()
        
        # Detect if code is provided
        has_code = any(keyword in description_lower for keyword in [
            "def ", "function", "class ", "import", "from ", "const ", "let ", "var ",
            "```", "public class", "private ", "public ", "static "
        ])
        
        # Extract code if present
        code = ""
        if has_code:
            # Try to extract code blocks first
            code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', description, re.DOTALL)
            if code_blocks:
                code = code_blocks[0]
            else:
                # Look for code patterns and extract larger chunks
                lines = description.split('\n')
                code_lines = []
                in_code = False
                
                for line in lines:
                    if any(keyword in line.lower() for keyword in ["def ", "function", "class ", "import"]):
                        in_code = True
                    
                    if in_code:
                        code_lines.append(line)
                        
                if code_lines:
                    code = '\n'.join(code_lines)
                else:
                    # Fallback: assume entire description is code if keywords found
                    code = description
        
        # Detect programming language
        language = "python"  # Default
        if any(keyword in description_lower for keyword in ["javascript", "js", "react", "node", "const ", "let "]):
            language = "javascript"
        elif any(keyword in description_lower for keyword in ["typescript", "ts"]):
            language = "typescript"
        elif any(keyword in description_lower for keyword in ["java", "public class"]):
            language = "java"
        elif any(keyword in description_lower for keyword in ["python", "py", "def ", "import"]):
            language = "python"
        elif any(keyword in description_lower for keyword in ["c#", "csharp", "using system"]):
            language = "csharp"
        
        # Detect specific bug categories to focus on
        categories = []
        if any(keyword in description_lower for keyword in ["security", "vulnerability", "injection", "xss"]):
            categories.append(BugCategory.SECURITY)
        if any(keyword in description_lower for keyword in ["performance", "slow", "optimization", "memory"]):
            categories.append(BugCategory.PERFORMANCE)
        if any(keyword in description_lower for keyword in ["logic", "bug", "error", "issue"]):
            categories.append(BugCategory.LOGIC)
        if any(keyword in description_lower for keyword in ["quality", "maintainability", "refactor"]):
            categories.append(BugCategory.CODE_QUALITY)
        
        # Extract file path if mentioned
        file_path = None
        file_match = re.search(r'file[:\s]+([^\s,]+)', description_lower)
        if file_match:
            file_path = file_match.group(1)
        
        return {
            "has_code": has_code,
            "code": code,
            "language": language,
            "categories": categories if categories else None,
            "file_path": file_path,
            "description": description
        }
    
    async def _provide_bug_detection_guidance(self, description: str) -> Dict[str, Any]:
        """Provide bug detection guidance when no code is provided."""
        
        # Use LLM to provide general guidance
        prompt = f"""
        As Alex Thompson, a methodical QA Engineer, provide guidance on this bug detection request:
        
        {description}
        
        Since no code was provided, give advice on:
        1. What types of bugs to look for in this context
        2. Testing strategies to find issues
        3. Tools and techniques for bug detection
        4. Common pitfalls to avoid
        5. Quality checkpoints to implement
        
        Be specific and actionable in your recommendations.
        """
        
        llm_response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.agent_id,
            task_type=TaskType.CODE_REVIEW,
            complexity=5,
            max_tokens=800,
            temperature=0.4,
        )
        
        return {
            "guidance": llm_response.content,
            "suggested_actions": [
                "Provide code for specific bug analysis",
                "Use static analysis tools",
                "Implement automated testing",
                "Set up continuous quality monitoring"
            ],
            "success": True,
            "response": llm_response.content
        }
    
    async def _format_bug_analysis_response(self, analysis_result: BugAnalysisResult, config: Dict[str, Any]) -> str:
        """Format bug analysis results with Alex's personality."""
        
        tone = self.personality.get_quality_assessment_tone()
        
        if analysis_result.critical_issues:
            severity = "critical"
            header = "🚨 Critical Issues Detected"
        elif analysis_result.total_bugs > 10:
            severity = "high"
            header = "⚠️ Multiple Issues Found"
        elif analysis_result.total_bugs > 0:
            severity = "medium"
            header = "📋 Quality Review Complete"
        else:
            severity = "low"
            header = "✅ Code Quality Check Passed"
        
        # Build response with personality
        response_parts = [
            f"{header}\n",
            f"Analysis Summary: {analysis_result.analysis_summary}\n",
            f"Security Score: {analysis_result.security_score:.2f}/1.0",
            f"Quality Score: {analysis_result.quality_score:.2f}/1.0",
            f"Maintainability Score: {analysis_result.maintainability_score:.2f}/1.0\n"
        ]
        
        if analysis_result.critical_issues:
            response_parts.append("🔴 Critical Issues Requiring Immediate Attention:")
            for i, issue in enumerate(analysis_result.critical_issues[:3], 1):  # Top 3
                response_parts.append(f"{i}. {issue.title} (Line {issue.line_number})")
                if issue.suggested_fix:
                    response_parts.append(f"   Fix: {issue.suggested_fix}")
            response_parts.append("")
        
        if analysis_result.recommendations:
            response_parts.append("💡 Recommendations:")
            for rec in analysis_result.recommendations:
                response_parts.append(f"• {rec}")
            response_parts.append("")
        
        # Add personality-driven conclusion
        if severity == "critical":
            conclusion = "These critical issues need immediate attention to ensure system security and stability."
        elif severity == "high":
            conclusion = "While not critical, these issues should be prioritized in the next development cycle."
        elif severity == "medium":
            conclusion = "The code is generally solid with some opportunities for improvement."
        else:
            conclusion = "Excellent code quality! Keep following these best practices."
        
        response_parts.append(conclusion)
        
        return "\n".join(response_parts)
    
    def _get_top_bugs_for_display(self, analysis_result: BugAnalysisResult) -> List[BugReport]:
        """Get the top bugs to display in response (limit for readability)."""
        
        # Get all bugs from the analysis result (need to reconstruct from critical_issues)
        # This is a simplified approach - in a real implementation, 
        # we'd store all bugs in the analysis result
        all_bugs = analysis_result.critical_issues.copy()
        
        # Sort by severity and confidence
        severity_order = {
            BugSeverity.CRITICAL: 5,
            BugSeverity.HIGH: 4,
            BugSeverity.MEDIUM: 3,
            BugSeverity.LOW: 2,
            BugSeverity.INFO: 1
        }
        
        all_bugs.sort(key=lambda bug: (
            severity_order.get(bug.severity, 0),
            bug.confidence_score
        ), reverse=True)
        
        # Return top 10 for display
        return all_bugs[:10]
    
    async def start_team_collaboration(self) -> None:
        """Initialize team collaboration by setting up message queue subscriptions."""
        
        if not self.message_queue.is_connected:
            await self.message_queue.connect()
        
        # Subscribe to collaboration topics
        for topic in self.collaboration_topics:
            try:
                await self.message_queue.register_handler(
                    agent_id=self.agent_id,
                    handler=self,
                    routing_keys=[topic],
                    queue_name=f"alex_qa_{topic.replace('.', '_')}"
                )
                self.logger.info(f"Alex subscribed to {topic}")
            except Exception as e:
                self.logger.error(f"Failed to subscribe to {topic}: {e}")
        
        # Announce availability to team
        await self.announce_qa_availability()
    
    async def announce_qa_availability(self) -> None:
        """Announce Alex's availability for QA collaboration."""
        
        announcement = {
            "agent_id": self.agent_id,
            "agent_name": "Alex Thompson",
            "role": "QA Engineer", 
            "services": [
                "Code review and quality analysis",
                "Test generation and automation",
                "Bug detection and analysis", 
                "Quality metrics tracking",
                "Performance and security testing",
                "Best practices consultation"
            ],
            "supported_frameworks": list(self.supported_frameworks),
            "quality_standards": list(self.quality_standards),
            "current_mood": self.personality.state.mood.value,
            "availability": "ready_for_collaboration"
        }
        
        await self.message_queue.broadcast(
            payload=announcement,
            sender_id=self.agent_id,
            message_type="qa_availability",
            agent_filter="development_team"
        )
        
        self.logger.info("Alex announced QA availability to team")
    
    async def collaborate_with_marcus(self, collaboration_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate specifically with Marcus (Backend Agent)."""
        
        self.logger.info(f"Alex collaborating with Marcus: {collaboration_type}")
        
        # Update personality for collaboration
        self.personality.update_mood("team_collaboration")
        
        collaboration_handlers = {
            "code_review": self._collaborate_code_review_with_marcus,
            "api_testing": self._collaborate_api_testing_with_marcus,
            "performance_review": self._collaborate_performance_review_with_marcus,
            "database_testing": self._collaborate_database_testing_with_marcus,
            "integration_testing": self._collaborate_integration_testing_with_marcus,
        }
        
        handler = collaboration_handlers.get(collaboration_type, self._generic_collaboration_with_marcus)
        
        try:
            result = await handler(content)
            
            # Remember the collaboration
            self.personality.remember_quality_interaction(
                agent_id="marcus_chen",
                interaction_type=collaboration_type,
                outcome="success",
                impact="medium"
            )
            
            # Update team interactions
            self.team_interactions["marcus_chen"][f"{collaboration_type}_sessions"] = \
                self.team_interactions["marcus_chen"].get(f"{collaboration_type}_sessions", 0) + 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error collaborating with Marcus: {e}")
            self.personality.remember_quality_interaction(
                agent_id="marcus_chen",
                interaction_type=collaboration_type,
                outcome="error",
                impact="low"
            )
            return {"error": str(e), "success": False}
    
    async def collaborate_with_emily(self, collaboration_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate specifically with Emily (Frontend Agent)."""
        
        self.logger.info(f"Alex collaborating with Emily: {collaboration_type}")
        
        # Update personality for collaboration
        self.personality.update_mood("team_collaboration")
        
        collaboration_handlers = {
            "ui_testing": self._collaborate_ui_testing_with_emily,
            "accessibility_review": self._collaborate_accessibility_review_with_emily,
            "component_testing": self._collaborate_component_testing_with_emily,
            "ux_quality_review": self._collaborate_ux_quality_with_emily,
            "frontend_performance": self._collaborate_frontend_performance_with_emily,
        }
        
        handler = collaboration_handlers.get(collaboration_type, self._generic_collaboration_with_emily)
        
        try:
            result = await handler(content)
            
            # Remember the collaboration
            self.personality.remember_quality_interaction(
                agent_id="emily_rodriguez",
                interaction_type=collaboration_type,
                outcome="success",
                impact="medium"
            )
            
            # Update team interactions
            self.team_interactions["emily_rodriguez"][f"{collaboration_type}_sessions"] = \
                self.team_interactions["emily_rodriguez"].get(f"{collaboration_type}_sessions", 0) + 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error collaborating with Emily: {e}")
            self.personality.remember_quality_interaction(
                agent_id="emily_rodriguez",
                interaction_type=collaboration_type,
                outcome="error",
                impact="low"
            )
            return {"error": str(e), "success": False}
    
    # Marcus collaboration handlers
    async def _collaborate_code_review_with_marcus(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with Marcus on backend code review."""
        
        code = content.get("code", "")
        if not code:
            return {"error": "No code provided for review", "success": False}
        
        # Perform comprehensive code review focused on backend concerns
        bug_analysis = self.bug_detector.analyze_code(
            code=code,
            language="python",
            file_path=content.get("file_path", "backend_code"),
            include_categories=[BugCategory.SECURITY, BugCategory.PERFORMANCE, BugCategory.LOGIC]
        )
        
        # Generate backend-specific recommendations
        recommendations = []
        if bug_analysis.bugs_by_category.get(BugCategory.SECURITY, 0) > 0:
            recommendations.append("🔒 Security vulnerabilities found - review input validation and SQL queries")
        if bug_analysis.bugs_by_category.get(BugCategory.PERFORMANCE, 0) > 0:
            recommendations.append("⚡ Performance issues detected - consider optimization for database queries and loops")
        if bug_analysis.security_score < 0.8:
            recommendations.append("🛡️ Enhance security measures for backend APIs")
        
        # Create collaboration response
        response = {
            "collaboration_type": "code_review",
            "partner": "marcus_chen",
            "quality_score": bug_analysis.quality_score,
            "security_score": bug_analysis.security_score,
            "critical_issues": len(bug_analysis.critical_issues),
            "recommendations": recommendations,
            "detailed_analysis": f"Backend code review complete. Found {bug_analysis.total_bugs} issues.",
            "suggested_tests": await self._suggest_backend_tests(content),
            "success": True
        }
        
        # Send results to Marcus
        await self.send_collaboration_result_to_marcus(response)
        
        return response
    
    async def _collaborate_api_testing_with_marcus(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with Marcus on API testing."""
        
        api_spec = content.get("api_spec", {})
        endpoints = content.get("endpoints", [])
        
        # Generate API tests for Marcus's endpoints
        test_plan = {
            "test_types": ["unit", "integration", "security", "performance"],
            "endpoints_to_test": endpoints,
            "security_tests": [
                "Authentication and authorization testing",
                "Input validation testing", 
                "SQL injection prevention",
                "Rate limiting verification"
            ],
            "performance_tests": [
                "Response time benchmarking",
                "Load testing with concurrent requests",
                "Database query optimization verification"
            ],
            "integration_tests": [
                "Database integration validation",
                "External service integration testing",
                "Error handling verification"
            ]
        }
        
        response = {
            "collaboration_type": "api_testing",
            "partner": "marcus_chen",
            "test_plan": test_plan,
            "estimated_effort": "2-4 hours",
            "priority": "high",
            "success": True
        }
        
        await self.send_collaboration_result_to_marcus(response)
        return response
    
    async def _collaborate_performance_review_with_marcus(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with Marcus on performance analysis."""
        
        performance_data = content.get("performance_data", {})
        code = content.get("code", "")
        
        # Analyze performance from QA perspective
        analysis = {
            "response_time_analysis": "Review database query patterns and async operations",
            "memory_usage_review": "Check for memory leaks in long-running processes",
            "scalability_assessment": "Verify horizontal scaling capabilities",
            "database_optimization": "Review indexing and query optimization",
            "caching_strategy": "Evaluate caching implementation effectiveness"
        }
        
        recommendations = [
            "Implement performance benchmarking tests",
            "Set up monitoring for response time degradation",
            "Create load testing scenarios for peak usage",
            "Review database connection pooling configuration"
        ]
        
        response = {
            "collaboration_type": "performance_review",
            "partner": "marcus_chen",
            "analysis": analysis,
            "recommendations": recommendations,
            "next_steps": [
                "Set up automated performance testing",
                "Establish performance baselines", 
                "Create alerting for performance regressions"
            ],
            "success": True
        }
        
        await self.send_collaboration_result_to_marcus(response)
        return response
    
    async def _collaborate_database_testing_with_marcus(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with Marcus on database testing strategy."""
        
        schema = content.get("database_schema", {})
        migrations = content.get("migrations", [])
        
        testing_strategy = {
            "data_integrity_tests": [
                "Foreign key constraint validation",
                "Data type validation testing",
                "Unique constraint verification"
            ],
            "migration_tests": [
                "Migration rollback testing",
                "Data preservation validation",
                "Performance impact assessment"
            ],
            "transaction_tests": [
                "ACID property verification", 
                "Deadlock prevention testing",
                "Concurrent access validation"
            ],
            "backup_recovery_tests": [
                "Backup creation validation",
                "Recovery procedure testing",
                "Data consistency verification"
            ]
        }
        
        response = {
            "collaboration_type": "database_testing",
            "partner": "marcus_chen",
            "testing_strategy": testing_strategy,
            "priority_tests": ["data_integrity_tests", "migration_tests"],
            "tools_recommended": ["pytest with database fixtures", "database seeding scripts"],
            "success": True
        }
        
        await self.send_collaboration_result_to_marcus(response)
        return response
    
    async def _collaborate_integration_testing_with_marcus(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with Marcus on integration testing."""
        
        services = content.get("services", [])
        endpoints = content.get("endpoints", [])
        
        integration_plan = {
            "service_integration_tests": [
                "Inter-service communication validation",
                "Message queue integration testing",
                "External API integration verification"
            ],
            "end_to_end_scenarios": [
                "Complete user workflow testing",
                "Multi-service transaction testing",
                "Error propagation testing"
            ],
            "contract_testing": [
                "API contract validation",
                "Schema compatibility testing",
                "Version compatibility verification"
            ]
        }
        
        response = {
            "collaboration_type": "integration_testing",
            "partner": "marcus_chen",
            "integration_plan": integration_plan,
            "test_environments": ["staging", "integration"],
            "automation_level": "high",
            "success": True
        }
        
        await self.send_collaboration_result_to_marcus(response)
        return response
    
    # Emily collaboration handlers
    async def _collaborate_ui_testing_with_emily(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with Emily on UI testing strategy."""
        
        components = content.get("components", [])
        user_flows = content.get("user_flows", [])
        
        ui_testing_plan = {
            "component_tests": [
                "Unit tests for component logic",
                "Snapshot testing for UI consistency",
                "Props and state validation testing"
            ],
            "visual_regression_tests": [
                "Cross-browser compatibility testing",
                "Responsive design validation",
                "Theme and styling consistency"
            ],
            "user_interaction_tests": [
                "Click and keyboard navigation testing",
                "Form validation and submission",
                "Error state handling verification"
            ],
            "performance_tests": [
                "Component rendering performance",
                "Bundle size optimization validation",
                "Lazy loading verification"
            ]
        }
        
        response = {
            "collaboration_type": "ui_testing",
            "partner": "emily_rodriguez",
            "testing_plan": ui_testing_plan,
            "recommended_tools": ["Jest", "React Testing Library", "Playwright", "Storybook"],
            "priority": "high",
            "success": True
        }
        
        await self.send_collaboration_result_to_emily(response)
        return response
    
    async def _collaborate_accessibility_review_with_emily(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with Emily on accessibility review."""
        
        components = content.get("components", [])
        accessibility_requirements = content.get("accessibility_requirements", "WCAG AA")
        
        accessibility_checklist = {
            "semantic_html": [
                "Proper heading hierarchy validation",
                "Semantic element usage verification",
                "Form label association testing"
            ],
            "aria_implementation": [
                "ARIA roles and properties validation",
                "Screen reader compatibility testing",
                "Focus management verification"
            ],
            "keyboard_navigation": [
                "Tab order validation",
                "Keyboard shortcut testing",
                "Focus indicator visibility"
            ],
            "color_contrast": [
                "Color contrast ratio validation",
                "Color-blind accessibility testing",
                "High contrast mode compatibility"
            ]
        }
        
        response = {
            "collaboration_type": "accessibility_review",
            "partner": "emily_rodriguez",
            "accessibility_checklist": accessibility_checklist,
            "compliance_target": accessibility_requirements,
            "testing_tools": ["axe-core", "WAVE", "Lighthouse"],
            "success": True
        }
        
        await self.send_collaboration_result_to_emily(response)
        return response
    
    async def _collaborate_component_testing_with_emily(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with Emily on component testing."""
        
        component_spec = content.get("component_spec", {})
        
        # Generate comprehensive component test strategy
        test_suite = await self._generate_component_test_suite(component_spec)
        
        response = {
            "collaboration_type": "component_testing",
            "partner": "emily_rodriguez",
            "test_suite": test_suite,
            "coverage_target": "90%",
            "test_types": ["unit", "integration", "visual"],
            "success": True
        }
        
        await self.send_collaboration_result_to_emily(response)
        return response
    
    async def _collaborate_ux_quality_with_emily(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with Emily on UX quality assessment."""
        
        user_flows = content.get("user_flows", [])
        
        ux_quality_metrics = {
            "usability_testing": [
                "Task completion rate validation",
                "Error rate measurement",
                "User satisfaction scoring"
            ],
            "performance_ux": [
                "Page load time impact on UX",
                "Interaction responsiveness testing",
                "Progressive loading validation"
            ],
            "accessibility_ux": [
                "Screen reader user experience",
                "Keyboard-only navigation flow",
                "Mobile accessibility testing"
            ]
        }
        
        response = {
            "collaboration_type": "ux_quality_review",
            "partner": "emily_rodriguez",
            "quality_metrics": ux_quality_metrics,
            "testing_approach": "user_centered",
            "success": True
        }
        
        await self.send_collaboration_result_to_emily(response)
        return response
    
    async def _collaborate_frontend_performance_with_emily(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with Emily on frontend performance testing."""
        
        performance_targets = content.get("performance_targets", {})
        
        performance_testing_plan = {
            "core_web_vitals": [
                "Largest Contentful Paint (LCP) measurement",
                "First Input Delay (FID) validation",
                "Cumulative Layout Shift (CLS) testing"
            ],
            "bundle_analysis": [
                "Bundle size optimization validation",
                "Code splitting effectiveness",
                "Unused code detection"
            ],
            "runtime_performance": [
                "Component rendering performance",
                "Memory usage monitoring",
                "Event handler efficiency testing"
            ]
        }
        
        response = {
            "collaboration_type": "frontend_performance",
            "partner": "emily_rodriguez",
            "testing_plan": performance_testing_plan,
            "tools": ["Lighthouse", "WebPageTest", "Chrome DevTools"],
            "success": True
        }
        
        await self.send_collaboration_result_to_emily(response)
        return response
    
    # Generic collaboration handlers
    async def _generic_collaboration_with_marcus(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generic collaboration handler for Marcus."""
        return {
            "collaboration_type": "general",
            "partner": "marcus_chen",
            "message": "Quality assurance consultation available",
            "available_services": ["code_review", "api_testing", "performance_review"],
            "success": True
        }
    
    async def _generic_collaboration_with_emily(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generic collaboration handler for Emily."""
        return {
            "collaboration_type": "general",
            "partner": "emily_rodriguez",
            "message": "Frontend quality assurance available",
            "available_services": ["ui_testing", "accessibility_review", "component_testing"],
            "success": True
        }
    
    # Collaboration utility methods
    async def send_collaboration_result_to_marcus(self, result: Dict[str, Any]) -> None:
        """Send collaboration results to Marcus."""
        
        await self.message_queue.send_to_agent(
            target_agent_id="marcus_chen",
            payload=result,
            sender_id=self.agent_id,
            message_type="qa_collaboration_result"
        )
        
        self.logger.info(f"Sent {result['collaboration_type']} results to Marcus")
    
    async def send_collaboration_result_to_emily(self, result: Dict[str, Any]) -> None:
        """Send collaboration results to Emily."""
        
        await self.message_queue.send_to_agent(
            target_agent_id="emily_rodriguez",
            payload=result,
            sender_id=self.agent_id,
            message_type="qa_collaboration_result"
        )
        
        self.logger.info(f"Sent {result['collaboration_type']} results to Emily")
    
    async def _suggest_backend_tests(self, content: Dict[str, Any]) -> List[str]:
        """Suggest backend-specific tests based on code analysis."""
        
        suggestions = [
            "Unit tests for business logic functions",
            "Integration tests for database operations",
            "API endpoint validation tests",
            "Authentication and authorization tests",
            "Error handling and edge case tests"
        ]
        
        # Add specific suggestions based on content
        if "database" in content.get("description", "").lower():
            suggestions.append("Database transaction and rollback tests")
        if "api" in content.get("description", "").lower():
            suggestions.append("API contract and schema validation tests")
        
        return suggestions
    
    async def _generate_component_test_suite(self, component_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test suite for a React component."""
        
        component_name = component_spec.get("name", "Component")
        props = component_spec.get("props", [])
        
        test_suite = {
            "component": component_name,
            "test_files": [
                f"{component_name}.test.jsx",
                f"{component_name}.accessibility.test.jsx",
                f"{component_name}.visual.test.jsx"
            ],
            "test_categories": {
                "unit_tests": [
                    "Component renders without crashing",
                    "Props are handled correctly",
                    "Event handlers work as expected",
                    "State changes update UI correctly"
                ],
                "accessibility_tests": [
                    "ARIA attributes are present",
                    "Keyboard navigation works",
                    "Screen reader compatibility",
                    "Color contrast validation"
                ],
                "visual_tests": [
                    "Component matches design specs",
                    "Responsive behavior validation",
                    "Theme variations testing",
                    "Snapshot regression testing"
                ]
            },
            "coverage_target": "95%",
            "framework": "Jest + React Testing Library"
        }
        
        return test_suite
    
    async def broadcast_quality_update(self, update_type: str, content: Dict[str, Any]) -> None:
        """Broadcast quality updates to the development team."""
        
        update_message = {
            "update_type": update_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "qa_agent": self.agent_id,
            "mood": self.personality.state.mood.value
        }
        
        await self.message_queue.broadcast(
            payload=update_message,
            sender_id=self.agent_id,
            message_type="quality_update",
            agent_filter="development_team"
        )
        
        self.logger.info(f"Broadcasted quality update: {update_type}")
    
    def get_personality_greeting(self) -> str:
        """Get Alex's personality-driven greeting."""
        return self.personality.get_greeting()