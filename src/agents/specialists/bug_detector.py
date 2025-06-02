"""
Bug Detection and Analysis Engine for Alex Thompson - QA Agent.

Provides comprehensive bug detection capabilities including static analysis,
pattern recognition, security vulnerability detection, and code quality assessment.
"""

import ast
import re
import json
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class BugSeverity(Enum):
    """Severity levels for detected bugs."""
    CRITICAL = "critical"      # Security vulnerabilities, crashes, data loss
    HIGH = "high"             # Major functionality broken, performance issues
    MEDIUM = "medium"         # Minor functionality issues, edge cases
    LOW = "low"               # Style issues, minor improvements
    INFO = "info"             # Suggestions and best practices


class BugCategory(Enum):
    """Categories of bugs that can be detected."""
    SECURITY = "security"
    PERFORMANCE = "performance" 
    LOGIC = "logic"
    MEMORY = "memory"
    CONCURRENCY = "concurrency"
    ERROR_HANDLING = "error_handling"
    TYPE_SAFETY = "type_safety"
    CODE_QUALITY = "code_quality"
    MAINTAINABILITY = "maintainability"
    ACCESSIBILITY = "accessibility"
    API_DESIGN = "api_design"


class BugType(Enum):
    """Specific types of bugs."""
    # Security
    SQL_INJECTION = "sql_injection"
    XSS_VULNERABILITY = "xss_vulnerability"
    HARDCODED_SECRETS = "hardcoded_secrets"
    INSECURE_RANDOMNESS = "insecure_randomness"
    
    # Performance
    INEFFICIENT_LOOP = "inefficient_loop"
    MEMORY_LEAK = "memory_leak"
    UNNECESSARY_COMPUTATION = "unnecessary_computation"
    BLOCKING_OPERATION = "blocking_operation"
    
    # Logic
    INFINITE_LOOP = "infinite_loop"
    UNREACHABLE_CODE = "unreachable_code"
    INCORRECT_CONDITION = "incorrect_condition"
    MISSING_VALIDATION = "missing_validation"
    
    # Error Handling
    UNCAUGHT_EXCEPTION = "uncaught_exception"
    EMPTY_CATCH_BLOCK = "empty_catch_block"
    IMPROPER_ERROR_HANDLING = "improper_error_handling"
    
    # Type Safety
    TYPE_MISMATCH = "type_mismatch"
    NULL_POINTER = "null_pointer"
    UNDEFINED_VARIABLE = "undefined_variable"
    
    # Code Quality
    CODE_DUPLICATION = "code_duplication"
    LONG_METHOD = "long_method"
    COMPLEX_CONDITION = "complex_condition"
    MAGIC_NUMBER = "magic_number"


@dataclass
class BugReport:
    """Represents a detected bug or issue."""
    id: str
    title: str
    description: str
    severity: BugSeverity
    category: BugCategory
    bug_type: BugType
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    code_snippet: Optional[str] = None
    suggested_fix: Optional[str] = None
    confidence_score: float = 0.8  # 0.0 to 1.0
    impact_analysis: Optional[str] = None
    references: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityVulnerability:
    """Specific security vulnerability detection."""
    cwe_id: Optional[str] = None  # Common Weakness Enumeration ID
    owasp_category: Optional[str] = None  # OWASP Top 10 category
    attack_vector: Optional[str] = None
    exploit_difficulty: str = "medium"  # easy, medium, hard
    data_exposure_risk: bool = False


@dataclass
class BugAnalysisResult:
    """Results of comprehensive bug analysis."""
    total_bugs: int
    bugs_by_severity: Dict[BugSeverity, int]
    bugs_by_category: Dict[BugCategory, int]
    critical_issues: List[BugReport]
    security_score: float  # 0.0 to 1.0
    quality_score: float   # 0.0 to 1.0
    maintainability_score: float  # 0.0 to 1.0
    recommendations: List[str]
    analysis_summary: str


class PythonBugDetector:
    """Python-specific bug detection using AST analysis."""
    
    def __init__(self):
        self.security_patterns = self._initialize_security_patterns()
        self.performance_patterns = self._initialize_performance_patterns()
        self.logic_patterns = self._initialize_logic_patterns()
    
    def analyze_code(self, code: str, file_path: str = "unknown") -> List[BugReport]:
        """Analyze Python code for bugs and issues."""
        bugs = []
        
        try:
            tree = ast.parse(code)
            
            # Run different analysis passes
            bugs.extend(self._analyze_security_issues(tree, code, file_path))
            bugs.extend(self._analyze_performance_issues(tree, code, file_path))
            bugs.extend(self._analyze_logic_issues(tree, code, file_path))
            bugs.extend(self._analyze_error_handling(tree, code, file_path))
            bugs.extend(self._analyze_code_quality(tree, code, file_path))
            
        except SyntaxError as e:
            bugs.append(BugReport(
                id=f"syntax_error_{hash(code)}",
                title="Syntax Error",
                description=f"Syntax error in code: {str(e)}",
                severity=BugSeverity.HIGH,
                category=BugCategory.LOGIC,
                bug_type=BugType.INCORRECT_CONDITION,
                file_path=file_path,
                line_number=getattr(e, 'lineno', None),
                confidence_score=1.0
            ))
        
        return bugs
    
    def _analyze_security_issues(self, tree: ast.AST, code: str, file_path: str) -> List[BugReport]:
        """Detect security vulnerabilities in Python code."""
        bugs = []
        
        for node in ast.walk(tree):
            # SQL Injection detection
            if isinstance(node, ast.Call):
                if self._is_sql_vulnerable(node, code):
                    bugs.append(self._create_sql_injection_bug(node, file_path))
            
            # Hardcoded secrets detection
            if isinstance(node, ast.Assign):
                if self._has_hardcoded_secrets(node, code):
                    bugs.append(self._create_hardcoded_secret_bug(node, file_path))
            
            # Insecure randomness
            if isinstance(node, ast.Call):
                if self._uses_insecure_random(node):
                    bugs.append(self._create_insecure_random_bug(node, file_path))
        
        return bugs
    
    def _analyze_performance_issues(self, tree: ast.AST, code: str, file_path: str) -> List[BugReport]:
        """Detect performance issues in Python code."""
        bugs = []
        
        for node in ast.walk(tree):
            # Inefficient loops
            if isinstance(node, ast.For):
                if self._is_inefficient_loop(node):
                    bugs.append(self._create_inefficient_loop_bug(node, file_path))
            
            # Unnecessary computations in loops
            if isinstance(node, (ast.For, ast.While)):
                if self._has_unnecessary_computation(node):
                    bugs.append(self._create_unnecessary_computation_bug(node, file_path))
        
        return bugs
    
    def _analyze_logic_issues(self, tree: ast.AST, code: str, file_path: str) -> List[BugReport]:
        """Detect logic errors in Python code."""
        bugs = []
        
        for node in ast.walk(tree):
            # Infinite loop detection
            if isinstance(node, ast.While):
                if self._is_potential_infinite_loop(node):
                    bugs.append(self._create_infinite_loop_bug(node, file_path))
            
            # Unreachable code
            if self._is_unreachable_code(node):
                bugs.append(self._create_unreachable_code_bug(node, file_path))
            
            # Missing validation
            if isinstance(node, ast.FunctionDef):
                if self._missing_input_validation(node):
                    bugs.append(self._create_missing_validation_bug(node, file_path))
        
        return bugs
    
    def _analyze_error_handling(self, tree: ast.AST, code: str, file_path: str) -> List[BugReport]:
        """Analyze error handling patterns."""
        bugs = []
        
        for node in ast.walk(tree):
            # Empty except blocks
            if isinstance(node, ast.ExceptHandler):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    bugs.append(self._create_empty_except_bug(node, file_path))
            
            # Broad exception catching
            if isinstance(node, ast.ExceptHandler):
                if self._is_too_broad_exception(node):
                    bugs.append(self._create_broad_exception_bug(node, file_path))
        
        return bugs
    
    def _analyze_code_quality(self, tree: ast.AST, code: str, file_path: str) -> List[BugReport]:
        """Analyze code quality issues."""
        bugs = []
        
        for node in ast.walk(tree):
            # Long methods
            if isinstance(node, ast.FunctionDef):
                if self._is_long_method(node):
                    bugs.append(self._create_long_method_bug(node, file_path))
            
            # Complex conditions
            if isinstance(node, ast.If):
                if self._is_complex_condition(node):
                    bugs.append(self._create_complex_condition_bug(node, file_path))
            
            # Magic numbers
            if isinstance(node, ast.Num):
                if self._is_magic_number(node):
                    bugs.append(self._create_magic_number_bug(node, file_path))
        
        return bugs
    
    # Security detection helpers
    def _is_sql_vulnerable(self, node: ast.Call, code: str) -> bool:
        """Check if SQL call is vulnerable to injection."""
        if hasattr(node.func, 'attr'):
            if node.func.attr in ['execute', 'executemany', 'query']:
                # Check if using string formatting in SQL
                for arg in node.args:
                    if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
                        return True
                    if isinstance(arg, ast.JoinedStr):  # f-strings
                        return True
        return False
    
    def _has_hardcoded_secrets(self, node: ast.Assign, code: str) -> bool:
        """Detect hardcoded secrets in assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                if any(secret in var_name for secret in ['password', 'secret', 'key', 'token', 'api_key']):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        if len(node.value.value) > 8:  # Non-trivial string
                            return True
        return False
    
    def _uses_insecure_random(self, node: ast.Call) -> bool:
        """Check for insecure random number generation."""
        if hasattr(node.func, 'attr'):
            if node.func.attr in ['random', 'randint', 'choice']:
                if hasattr(node.func, 'value') and hasattr(node.func.value, 'id'):
                    if node.func.value.id == 'random':
                        return True
        return False
    
    # Performance detection helpers
    def _is_inefficient_loop(self, node: ast.For) -> bool:
        """Check for inefficient loop patterns."""
        # Check for list concatenation in loop
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.AugAssign) and isinstance(stmt.op, ast.Add):
                if isinstance(stmt.target, ast.Name):
                    return True
        return False
    
    def _has_unnecessary_computation(self, node: Union[ast.For, ast.While]) -> bool:
        """Check for computations that could be moved outside the loop."""
        # Simplified check for function calls in loops that don't depend on loop variable
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call):
                # This is a simplified heuristic
                return True
        return False
    
    # Logic detection helpers
    def _is_potential_infinite_loop(self, node: ast.While) -> bool:
        """Check for potential infinite loops."""
        # Check if loop condition is modified in body
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            # while True: - check for break statements
            has_break = False
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Break):
                    has_break = True
                    break
            return not has_break
        return False
    
    def _is_unreachable_code(self, node: ast.AST) -> bool:
        """Check for unreachable code."""
        # Simplified check - code after return statements
        if hasattr(node, 'body') and isinstance(node.body, list):
            for i, stmt in enumerate(node.body[:-1]):
                if isinstance(stmt, ast.Return):
                    if i + 1 < len(node.body):
                        return True
        return False
    
    def _missing_input_validation(self, node: ast.FunctionDef) -> bool:
        """Check if function is missing input validation."""
        # Simple heuristic: public functions without any if statements
        if not node.name.startswith('_'):  # Public function
            has_validation = False
            for stmt in node.body[:3]:  # Check first few statements
                if isinstance(stmt, ast.If):
                    has_validation = True
                    break
            return not has_validation and len(node.args.args) > 0
        return False
    
    # Error handling helpers
    def _is_too_broad_exception(self, node: ast.ExceptHandler) -> bool:
        """Check for overly broad exception handling."""
        if node.type is None:  # bare except:
            return True
        if isinstance(node.type, ast.Name) and node.type.id == 'Exception':
            return True
        return False
    
    # Code quality helpers
    def _is_long_method(self, node: ast.FunctionDef) -> bool:
        """Check if method is too long."""
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            return (node.end_lineno - node.lineno) > 50
        return len(node.body) > 20
    
    def _is_complex_condition(self, node: ast.If) -> bool:
        """Check for overly complex conditions."""
        complexity = self._calculate_condition_complexity(node.test)
        return complexity > 4
    
    def _calculate_condition_complexity(self, node: ast.AST) -> int:
        """Calculate complexity of a condition."""
        if isinstance(node, ast.BoolOp):
            return 1 + sum(self._calculate_condition_complexity(value) for value in node.values)
        elif isinstance(node, ast.Compare):
            return len(node.ops)
        else:
            return 1
    
    def _is_magic_number(self, node: ast.Num) -> bool:
        """Check for magic numbers."""
        if isinstance(node.n, (int, float)):
            # Common non-magic numbers
            if node.n in [0, 1, -1, 2, 10, 100, 1000]:
                return False
            return True
        return False
    
    # Bug creation helpers
    def _create_sql_injection_bug(self, node: ast.Call, file_path: str) -> BugReport:
        """Create SQL injection bug report."""
        return BugReport(
            id=f"sql_injection_{hash(str(node.lineno))}",
            title="SQL Injection Vulnerability",
            description="SQL query uses string formatting which is vulnerable to injection attacks",
            severity=BugSeverity.CRITICAL,
            category=BugCategory.SECURITY,
            bug_type=BugType.SQL_INJECTION,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Use parameterized queries or prepared statements",
            confidence_score=0.9,
            impact_analysis="Could allow unauthorized database access and data manipulation",
            references=["https://owasp.org/www-community/attacks/SQL_Injection"]
        )
    
    def _create_hardcoded_secret_bug(self, node: ast.Assign, file_path: str) -> BugReport:
        """Create hardcoded secret bug report."""
        return BugReport(
            id=f"hardcoded_secret_{hash(str(node.lineno))}",
            title="Hardcoded Secret",
            description="Sensitive information appears to be hardcoded in the source code",
            severity=BugSeverity.HIGH,
            category=BugCategory.SECURITY,
            bug_type=BugType.HARDCODED_SECRETS,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Move sensitive values to environment variables or secure configuration",
            confidence_score=0.8,
            impact_analysis="Sensitive information could be exposed if source code is compromised"
        )
    
    def _create_insecure_random_bug(self, node: ast.Call, file_path: str) -> BugReport:
        """Create insecure randomness bug report."""
        return BugReport(
            id=f"insecure_random_{hash(str(node.lineno))}",
            title="Insecure Random Number Generation",
            description="Using predictable random number generation for security-sensitive operations",
            severity=BugSeverity.MEDIUM,
            category=BugCategory.SECURITY,
            bug_type=BugType.INSECURE_RANDOMNESS,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Use cryptographically secure random number generation (secrets module)",
            confidence_score=0.7
        )
    
    def _create_inefficient_loop_bug(self, node: ast.For, file_path: str) -> BugReport:
        """Create inefficient loop bug report."""
        return BugReport(
            id=f"inefficient_loop_{hash(str(node.lineno))}",
            title="Inefficient Loop Pattern",
            description="Loop contains operations that could be optimized",
            severity=BugSeverity.MEDIUM,
            category=BugCategory.PERFORMANCE,
            bug_type=BugType.INEFFICIENT_LOOP,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Consider using list comprehensions or built-in functions",
            confidence_score=0.6
        )
    
    def _create_unnecessary_computation_bug(self, node: Union[ast.For, ast.While], file_path: str) -> BugReport:
        """Create unnecessary computation bug report."""
        return BugReport(
            id=f"unnecessary_computation_{hash(str(node.lineno))}",
            title="Unnecessary Computation in Loop",
            description="Computation inside loop could be moved outside for better performance",
            severity=BugSeverity.LOW,
            category=BugCategory.PERFORMANCE,
            bug_type=BugType.UNNECESSARY_COMPUTATION,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Move loop-invariant computations outside the loop",
            confidence_score=0.5
        )
    
    def _create_infinite_loop_bug(self, node: ast.While, file_path: str) -> BugReport:
        """Create infinite loop bug report."""
        return BugReport(
            id=f"infinite_loop_{hash(str(node.lineno))}",
            title="Potential Infinite Loop",
            description="While loop may not have a proper exit condition",
            severity=BugSeverity.HIGH,
            category=BugCategory.LOGIC,
            bug_type=BugType.INFINITE_LOOP,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Ensure loop has proper break conditions or modify loop variable",
            confidence_score=0.7
        )
    
    def _create_unreachable_code_bug(self, node: ast.AST, file_path: str) -> BugReport:
        """Create unreachable code bug report."""
        return BugReport(
            id=f"unreachable_code_{hash(str(node.lineno))}",
            title="Unreachable Code",
            description="Code appears to be unreachable due to earlier return statement",
            severity=BugSeverity.LOW,
            category=BugCategory.CODE_QUALITY,
            bug_type=BugType.UNREACHABLE_CODE,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Remove unreachable code or restructure logic",
            confidence_score=0.8
        )
    
    def _create_missing_validation_bug(self, node: ast.FunctionDef, file_path: str) -> BugReport:
        """Create missing validation bug report."""
        return BugReport(
            id=f"missing_validation_{hash(str(node.lineno))}",
            title="Missing Input Validation",
            description=f"Function '{node.name}' may be missing input validation",
            severity=BugSeverity.MEDIUM,
            category=BugCategory.LOGIC,
            bug_type=BugType.MISSING_VALIDATION,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Add input validation at the beginning of the function",
            confidence_score=0.6
        )
    
    def _create_empty_except_bug(self, node: ast.ExceptHandler, file_path: str) -> BugReport:
        """Create empty except block bug report."""
        return BugReport(
            id=f"empty_except_{hash(str(node.lineno))}",
            title="Empty Exception Handler",
            description="Exception handler is empty, suppressing potentially important errors",
            severity=BugSeverity.MEDIUM,
            category=BugCategory.ERROR_HANDLING,
            bug_type=BugType.EMPTY_CATCH_BLOCK,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Add proper error handling or logging in exception handler",
            confidence_score=0.9
        )
    
    def _create_broad_exception_bug(self, node: ast.ExceptHandler, file_path: str) -> BugReport:
        """Create broad exception handling bug report."""
        return BugReport(
            id=f"broad_exception_{hash(str(node.lineno))}",
            title="Overly Broad Exception Handling",
            description="Exception handler catches too broad a range of exceptions",
            severity=BugSeverity.LOW,
            category=BugCategory.ERROR_HANDLING,
            bug_type=BugType.IMPROPER_ERROR_HANDLING,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Catch specific exception types instead of broad Exception",
            confidence_score=0.7
        )
    
    def _create_long_method_bug(self, node: ast.FunctionDef, file_path: str) -> BugReport:
        """Create long method bug report."""
        return BugReport(
            id=f"long_method_{hash(str(node.lineno))}",
            title="Long Method",
            description=f"Method '{node.name}' is too long and should be refactored",
            severity=BugSeverity.LOW,
            category=BugCategory.MAINTAINABILITY,
            bug_type=BugType.LONG_METHOD,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Break method into smaller, more focused methods",
            confidence_score=0.8
        )
    
    def _create_complex_condition_bug(self, node: ast.If, file_path: str) -> BugReport:
        """Create complex condition bug report."""
        return BugReport(
            id=f"complex_condition_{hash(str(node.lineno))}",
            title="Complex Conditional",
            description="Conditional statement is too complex and hard to understand",
            severity=BugSeverity.LOW,
            category=BugCategory.MAINTAINABILITY,
            bug_type=BugType.COMPLEX_CONDITION,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Break complex condition into multiple simpler conditions or extract to variables",
            confidence_score=0.7
        )
    
    def _create_magic_number_bug(self, node: ast.Num, file_path: str) -> BugReport:
        """Create magic number bug report."""
        return BugReport(
            id=f"magic_number_{hash(str(node.lineno))}",
            title="Magic Number",
            description=f"Magic number {node.n} should be replaced with a named constant",
            severity=BugSeverity.LOW,
            category=BugCategory.MAINTAINABILITY,
            bug_type=BugType.MAGIC_NUMBER,
            file_path=file_path,
            line_number=getattr(node, 'lineno', None),
            suggested_fix="Replace magic number with a named constant",
            confidence_score=0.6
        )
    
    def _initialize_security_patterns(self) -> Dict[str, List[str]]:
        """Initialize security vulnerability patterns."""
        return {
            "sql_injection": ["execute", "executemany", "query"],
            "secrets": ["password", "secret", "key", "token", "api_key"],
            "crypto": ["random", "randint", "choice"]
        }
    
    def _initialize_performance_patterns(self) -> Dict[str, List[str]]:
        """Initialize performance issue patterns."""
        return {
            "inefficient_loops": ["+=", "append", "extend"],
            "blocking_ops": ["sleep", "request", "open"]
        }
    
    def _initialize_logic_patterns(self) -> Dict[str, List[str]]:
        """Initialize logic error patterns."""
        return {
            "infinite_loops": ["while True", "while 1"],
            "unreachable": ["return", "break", "continue"]
        }


class JavaScriptBugDetector:
    """JavaScript/TypeScript specific bug detection using regex patterns."""
    
    def analyze_code(self, code: str, file_path: str = "unknown") -> List[BugReport]:
        """Analyze JavaScript/TypeScript code for bugs."""
        bugs = []
        
        # Security issues
        bugs.extend(self._detect_xss_vulnerabilities(code, file_path))
        bugs.extend(self._detect_eval_usage(code, file_path))
        
        # Performance issues
        bugs.extend(self._detect_inefficient_dom_access(code, file_path))
        bugs.extend(self._detect_memory_leaks(code, file_path))
        
        # Logic issues
        bugs.extend(self._detect_type_coercion_issues(code, file_path))
        bugs.extend(self._detect_undefined_variables(code, file_path))
        
        return bugs
    
    def _detect_xss_vulnerabilities(self, code: str, file_path: str) -> List[BugReport]:
        """Detect XSS vulnerabilities in JavaScript."""
        bugs = []
        
        # innerHTML with user input
        innerHTML_pattern = r'\.innerHTML\s*=\s*[^;]+(?:input|param|query|data)'
        for match in re.finditer(innerHTML_pattern, code, re.IGNORECASE):
            line_num = code[:match.start()].count('\n') + 1
            bugs.append(BugReport(
                id=f"xss_innerHTML_{hash(match.group())}",
                title="XSS Vulnerability - innerHTML",
                description="Using innerHTML with potentially untrusted data",
                severity=BugSeverity.HIGH,
                category=BugCategory.SECURITY,
                bug_type=BugType.XSS_VULNERABILITY,
                file_path=file_path,
                line_number=line_num,
                suggested_fix="Use textContent or properly sanitize input",
                confidence_score=0.8
            ))
        
        return bugs
    
    def _detect_eval_usage(self, code: str, file_path: str) -> List[BugReport]:
        """Detect dangerous eval usage."""
        bugs = []
        
        eval_pattern = r'\beval\s*\('
        for match in re.finditer(eval_pattern, code):
            line_num = code[:match.start()].count('\n') + 1
            bugs.append(BugReport(
                id=f"eval_usage_{hash(match.group())}",
                title="Dangerous eval() Usage",
                description="Using eval() can lead to code injection vulnerabilities",
                severity=BugSeverity.HIGH,
                category=BugCategory.SECURITY,
                bug_type=BugType.XSS_VULNERABILITY,
                file_path=file_path,
                line_number=line_num,
                suggested_fix="Avoid eval() and use safer alternatives like JSON.parse()",
                confidence_score=0.9
            ))
        
        return bugs
    
    def _detect_inefficient_dom_access(self, code: str, file_path: str) -> List[BugReport]:
        """Detect inefficient DOM access patterns."""
        bugs = []
        
        # Multiple getElementById calls
        dom_pattern = r'document\.getElementById\([^)]+\)'
        matches = list(re.finditer(dom_pattern, code))
        if len(matches) > 5:  # Threshold for inefficient access
            bugs.append(BugReport(
                id=f"inefficient_dom_{hash(code)}",
                title="Inefficient DOM Access",
                description="Multiple DOM queries could be cached for better performance",
                severity=BugSeverity.LOW,
                category=BugCategory.PERFORMANCE,
                bug_type=BugType.INEFFICIENT_LOOP,
                file_path=file_path,
                suggested_fix="Cache DOM elements in variables",
                confidence_score=0.7
            ))
        
        return bugs
    
    def _detect_memory_leaks(self, code: str, file_path: str) -> List[BugReport]:
        """Detect potential memory leaks."""
        bugs = []
        
        # Event listeners without removal
        listener_pattern = r'addEventListener\s*\('
        remove_pattern = r'removeEventListener\s*\('
        
        add_count = len(re.findall(listener_pattern, code))
        remove_count = len(re.findall(remove_pattern, code))
        
        if add_count > remove_count + 2:  # Allow some variance
            bugs.append(BugReport(
                id=f"memory_leak_{hash(code)}",
                title="Potential Memory Leak",
                description="Event listeners added but not properly removed",
                severity=BugSeverity.MEDIUM,
                category=BugCategory.MEMORY,
                bug_type=BugType.MEMORY_LEAK,
                file_path=file_path,
                suggested_fix="Ensure event listeners are removed when no longer needed",
                confidence_score=0.6
            ))
        
        return bugs
    
    def _detect_type_coercion_issues(self, code: str, file_path: str) -> List[BugReport]:
        """Detect problematic type coercion."""
        bugs = []
        
        # == instead of ===
        loose_equality_pattern = r'[^!=]==[^=]'
        for match in re.finditer(loose_equality_pattern, code):
            line_num = code[:match.start()].count('\n') + 1
            bugs.append(BugReport(
                id=f"type_coercion_{hash(match.group())}",
                title="Loose Equality Comparison",
                description="Using == instead of === can lead to unexpected type coercion",
                severity=BugSeverity.LOW,
                category=BugCategory.TYPE_SAFETY,
                bug_type=BugType.TYPE_MISMATCH,
                file_path=file_path,
                line_number=line_num,
                suggested_fix="Use strict equality (===) instead of loose equality (==)",
                confidence_score=0.8
            ))
        
        return bugs
    
    def _detect_undefined_variables(self, code: str, file_path: str) -> List[BugReport]:
        """Detect potential undefined variable usage."""
        bugs = []
        
        # Basic undefined check (simplified)
        undefined_pattern = r'\bundefined\b'
        if re.search(undefined_pattern, code):
            bugs.append(BugReport(
                id=f"undefined_check_{hash(code)}",
                title="Undefined Variable Check",
                description="Code contains undefined checks which may indicate potential issues",
                severity=BugSeverity.INFO,
                category=BugCategory.TYPE_SAFETY,
                bug_type=BugType.UNDEFINED_VARIABLE,
                file_path=file_path,
                suggested_fix="Ensure variables are properly initialized",
                confidence_score=0.4
            ))
        
        return bugs


class BugDetectionEngine:
    """Main bug detection engine that coordinates different detectors."""
    
    def __init__(self):
        self.python_detector = PythonBugDetector()
        self.javascript_detector = JavaScriptBugDetector()
    
    def analyze_code(
        self,
        code: str,
        language: str,
        file_path: str = "unknown",
        include_categories: Optional[List[BugCategory]] = None
    ) -> BugAnalysisResult:
        """Perform comprehensive bug analysis on code."""
        
        # Get detector based on language
        if language.lower() in ['python', 'py']:
            bugs = self.python_detector.analyze_code(code, file_path)
        elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
            bugs = self.javascript_detector.analyze_code(code, file_path)
        else:
            # Generic analysis for unsupported languages
            bugs = self._generic_analysis(code, file_path)
        
        # Filter by categories if specified
        if include_categories:
            bugs = [bug for bug in bugs if bug.category in include_categories]
        
        # Calculate metrics
        analysis_result = self._calculate_analysis_metrics(bugs)
        
        return analysis_result
    
    def _generic_analysis(self, code: str, file_path: str) -> List[BugReport]:
        """Generic analysis for unsupported languages."""
        bugs = []
        
        # Basic pattern matching for common issues
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Potential SQL injection
            if 'query' in line_lower and ('%' in line or '+' in line):
                bugs.append(BugReport(
                    id=f"generic_sql_{hash(line)}",
                    title="Potential SQL Injection",
                    description="Possible SQL injection vulnerability detected",
                    severity=BugSeverity.MEDIUM,
                    category=BugCategory.SECURITY,
                    bug_type=BugType.SQL_INJECTION,
                    file_path=file_path,
                    line_number=i + 1,
                    confidence_score=0.5
                ))
            
            # TODO comments (code quality)
            if 'todo' in line_lower or 'fixme' in line_lower:
                bugs.append(BugReport(
                    id=f"todo_{hash(line)}",
                    title="TODO Comment",
                    description="Code contains TODO or FIXME comment",
                    severity=BugSeverity.INFO,
                    category=BugCategory.CODE_QUALITY,
                    bug_type=BugType.CODE_DUPLICATION,
                    file_path=file_path,
                    line_number=i + 1,
                    confidence_score=1.0
                ))
        
        return bugs
    
    def _calculate_analysis_metrics(self, bugs: List[BugReport]) -> BugAnalysisResult:
        """Calculate comprehensive analysis metrics."""
        
        total_bugs = len(bugs)
        
        # Count by severity
        bugs_by_severity = {}
        for severity in BugSeverity:
            bugs_by_severity[severity] = len([b for b in bugs if b.severity == severity])
        
        # Count by category
        bugs_by_category = {}
        for category in BugCategory:
            bugs_by_category[category] = len([b for b in bugs if b.category == category])
        
        # Get critical issues
        critical_issues = [b for b in bugs if b.severity in [BugSeverity.CRITICAL, BugSeverity.HIGH]]
        
        # Calculate scores (0.0 to 1.0, higher is better)
        security_score = max(0.0, 1.0 - (bugs_by_severity.get(BugSeverity.CRITICAL, 0) * 0.3 + 
                                        bugs_by_severity.get(BugSeverity.HIGH, 0) * 0.1))
        
        quality_score = max(0.0, 1.0 - (total_bugs * 0.02))  # Penalize for total bug count
        
        maintainability_score = max(0.0, 1.0 - (bugs_by_category.get(BugCategory.MAINTAINABILITY, 0) * 0.1))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(bugs_by_severity, bugs_by_category)
        
        # Create summary
        summary = self._create_analysis_summary(total_bugs, bugs_by_severity, security_score)
        
        return BugAnalysisResult(
            total_bugs=total_bugs,
            bugs_by_severity=bugs_by_severity,
            bugs_by_category=bugs_by_category,
            critical_issues=critical_issues,
            security_score=security_score,
            quality_score=quality_score,
            maintainability_score=maintainability_score,
            recommendations=recommendations,
            analysis_summary=summary
        )
    
    def _generate_recommendations(
        self,
        bugs_by_severity: Dict[BugSeverity, int],
        bugs_by_category: Dict[BugCategory, int]
    ) -> List[str]:
        """Generate actionable recommendations based on bug analysis."""
        
        recommendations = []
        
        # Security recommendations
        if bugs_by_severity.get(BugSeverity.CRITICAL, 0) > 0:
            recommendations.append("🚨 Critical security issues found - address immediately")
        
        if bugs_by_category.get(BugCategory.SECURITY, 0) > 3:
            recommendations.append("Consider security code review and penetration testing")
        
        # Performance recommendations
        if bugs_by_category.get(BugCategory.PERFORMANCE, 0) > 5:
            recommendations.append("Multiple performance issues detected - consider optimization")
        
        # Code quality recommendations
        if bugs_by_category.get(BugCategory.MAINTAINABILITY, 0) > 10:
            recommendations.append("Code maintainability could be improved through refactoring")
        
        # Error handling recommendations
        if bugs_by_category.get(BugCategory.ERROR_HANDLING, 0) > 3:
            recommendations.append("Improve error handling and exception management")
        
        # General recommendations
        total_bugs = sum(bugs_by_severity.values())
        if total_bugs > 20:
            recommendations.append("Consider code review process improvements")
        
        if not recommendations:
            recommendations.append("Code quality is good - continue following best practices")
        
        return recommendations
    
    def _create_analysis_summary(
        self,
        total_bugs: int,
        bugs_by_severity: Dict[BugSeverity, int],
        security_score: float
    ) -> str:
        """Create a human-readable analysis summary."""
        
        critical_count = bugs_by_severity.get(BugSeverity.CRITICAL, 0)
        high_count = bugs_by_severity.get(BugSeverity.HIGH, 0)
        
        if critical_count > 0:
            priority = "CRITICAL"
            summary = f"Found {critical_count} critical security issues that require immediate attention."
        elif high_count > 0:
            priority = "HIGH"
            summary = f"Found {high_count} high-priority issues that should be addressed soon."
        elif total_bugs > 10:
            priority = "MEDIUM"
            summary = f"Found {total_bugs} total issues, mostly minor quality improvements."
        else:
            priority = "LOW"
            summary = f"Code quality is good with only {total_bugs} minor issues detected."
        
        summary += f" Security score: {security_score:.2f}/1.0"
        
        return summary