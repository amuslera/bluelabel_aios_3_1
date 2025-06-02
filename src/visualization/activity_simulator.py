"""
Agent Activity Simulator

Simulates realistic agent activities for visualization demonstration,
including code generation, testing, deployment, and team communication.
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from src.visualization.agent_visualizer import (
    AgentVisualizer, ActivityType, Message
)


class ActivitySimulator:
    """Simulates agent activities for visualization"""
    
    def __init__(self, visualizer: AgentVisualizer):
        self.visualizer = visualizer
        self.project_stage = "planning"
        self.code_snippets = self._load_code_snippets()
        self.conversation_templates = self._load_conversation_templates()
        
    def _load_code_snippets(self) -> Dict[str, List[str]]:
        """Load sample code snippets for different agents"""
        return {
            "Marcus Chen": [
                """# User model with authentication
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password_hash)""",
                
                """# FastAPI endpoint for user registration
@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # Check if user exists
    if db.query(User).filter_by(email=user_data.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hash_password(user_data.password)
    )
    db.add(user)
    db.commit()
    
    return UserResponse.from_orm(user)""",
                
                """# Database connection manager
class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()"""
            ],
            
            "Emily Rodriguez": [
                """// Modern React component with hooks
const TaskList = () => {
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    fetchTasks().then(data => {
      setTasks(data);
      setIsLoading(false);
    });
  }, []);
  
  const filteredTasks = tasks.filter(task => {
    if (filter === 'all') return true;
    return task.status === filter;
  });
  
  return (
    <div className="task-list">
      <TaskFilter onFilterChange={setFilter} />
      {isLoading ? (
        <LoadingSpinner />
      ) : (
        <TaskGrid tasks={filteredTasks} />
      )}
    </div>
  );
};""",
                
                """// Responsive task card component
const TaskCard = ({ task, onUpdate, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  
  return (
    <motion.div
      className="task-card"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="task-header">
        <h3>{task.title}</h3>
        <TaskPriority level={task.priority} />
      </div>
      
      <p className="task-description">{task.description}</p>
      
      <div className="task-actions">
        <Button
          variant="primary"
          onClick={() => setIsEditing(true)}
          aria-label="Edit task"
        >
          Edit
        </Button>
        <Button
          variant="danger"
          onClick={() => onDelete(task.id)}
          aria-label="Delete task"
        >
          Delete
        </Button>
      </div>
    </motion.div>
  );
};""",
                
                """// Custom hook for form validation
const useFormValidation = (initialValues, validationRules) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  
  const validate = (fieldName, value) => {
    const rule = validationRules[fieldName];
    if (!rule) return '';
    
    if (rule.required && !value) {
      return `${fieldName} is required`;
    }
    
    if (rule.pattern && !rule.pattern.test(value)) {
      return rule.message || `Invalid ${fieldName}`;
    }
    
    return '';
  };
  
  const handleChange = (fieldName, value) => {
    setValues(prev => ({ ...prev, [fieldName]: value }));
    setErrors(prev => ({ ...prev, [fieldName]: validate(fieldName, value) }));
  };
  
  return { values, errors, touched, handleChange };
};"""
            ],
            
            "Alex Thompson": [
                """# Comprehensive test suite for user authentication
class TestUserAuthentication:
    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash=hash_password("secure123")
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_user_registration_success(self, client, db_session):
        response = client.post("/api/register", json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "verysecure456"
        })
        
        assert response.status_code == 200
        assert response.json()["email"] == "new@example.com"
        
        # Verify user was created
        user = db_session.query(User).filter_by(email="new@example.com").first()
        assert user is not None
        assert user.verify_password("verysecure456")""",
                
                """# Performance testing with load simulation
class TestAPIPerformance:
    @pytest.mark.performance
    def test_concurrent_user_requests(self):
        async def make_request(session, user_id):
            url = f"http://localhost:8000/api/users/{user_id}"
            async with session.get(url) as response:
                return response.status, await response.json()
        
        async def run_load_test():
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i in range(100):  # 100 concurrent requests
                    tasks.append(make_request(session, i))
                
                start_time = time.time()
                results = await asyncio.gather(*tasks)
                end_time = time.time()
                
                # Analyze results
                successful = sum(1 for status, _ in results if status == 200)
                avg_time = (end_time - start_time) / len(results)
                
                assert successful >= 95  # 95% success rate
                assert avg_time < 0.1    # Less than 100ms average""",
                
                """# Security vulnerability testing
class TestSecurityVulnerabilities:
    def test_sql_injection_prevention(self, client):
        # Attempt SQL injection
        malicious_input = "'; DROP TABLE users; --"
        response = client.post("/api/login", json={
            "email": malicious_input,
            "password": "test"
        })
        
        # Should handle gracefully, not execute SQL
        assert response.status_code in [400, 401]
        assert "error" in response.json()
    
    def test_xss_prevention(self, client):
        # Attempt XSS
        xss_payload = "<script>alert('XSS')</script>"
        response = client.post("/api/tasks", json={
            "title": xss_payload,
            "description": "Test task"
        })
        
        # Check response sanitizes input
        if response.status_code == 200:
            task = response.json()
            assert "<script>" not in task["title"]
            assert "&lt;script&gt;" in task["title"]"""
            ],
            
            "Jordan Kim": [
                """# Kubernetes deployment configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taskmaster-api
  namespace: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: taskmaster-api
  template:
    metadata:
      labels:
        app: taskmaster-api
    spec:
      containers:
      - name: api
        image: taskmaster/api:v1.2.3
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10""",
                
                """# GitHub Actions CI/CD pipeline
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run tests
      run: |
        docker-compose run --rm test
        
    - name: Security scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: taskmaster/api:${{ github.sha }}
        
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
        
    - name: Deploy to EKS
      run: |
        kubectl set image deployment/taskmaster-api \\
          api=taskmaster/api:${{ github.sha }} \\
          --record -n production
          
    - name: Wait for rollout
      run: |
        kubectl rollout status deployment/taskmaster-api -n production""",
                
                """# Prometheus alerting rules
groups:
  - name: taskmaster_alerts
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: |
        sum(rate(http_requests_total{status=~"5.."}[5m])) /
        sum(rate(http_requests_total[5m])) > 0.05
      for: 5m
      labels:
        severity: critical
        service: taskmaster-api
      annotations:
        summary: "High error rate detected"
        description: "Error rate is {{ $value | humanizePercentage }} for the last 5 minutes"
        
    - alert: HighMemoryUsage
      expr: |
        container_memory_usage_bytes{pod=~"taskmaster-api-.*"} /
        container_spec_memory_limit_bytes > 0.9
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Pod memory usage is high"
        description: "Pod {{ $labels.pod }} memory usage is above 90%"
"""
            ]
        }
        
    def _load_conversation_templates(self) -> Dict[str, List[Dict[str, str]]]:
        """Load conversation templates between agents"""
        return {
            "planning": [
                {"from": "Marcus Chen", "to": "Emily Rodriguez", "message": "I've set up the API endpoints. Ready for frontend integration?"},
                {"from": "Emily Rodriguez", "to": "Marcus Chen", "message": "Perfect! I'll start working on the API client. Can you share the OpenAPI spec?"},
                {"from": "Marcus Chen", "to": "Emily Rodriguez", "message": "Sure! Just generated it. Check /docs for the interactive documentation."},
                {"from": "Alex Thompson", "to": "Marcus Chen", "message": "I'm seeing the API docs. I'll start writing integration tests."},
                {"from": "Jordan Kim", "to": "Team", "message": "I'm setting up the CI/CD pipeline. All code will auto-deploy on merge to main."}
            ],
            "development": [
                {"from": "Emily Rodriguez", "to": "Marcus Chen", "message": "The login endpoint returns 404. Is it deployed?"},
                {"from": "Marcus Chen", "to": "Emily Rodriguez", "message": "My bad! Forgot to add it to the router. Fixed now."},
                {"from": "Alex Thompson", "to": "Marcus Chen", "message": "Found a bug: user registration allows duplicate emails."},
                {"from": "Marcus Chen", "to": "Alex Thompson", "message": "Good catch! Adding unique constraint now."},
                {"from": "Jordan Kim", "to": "Team", "message": "Deployed hotfix to staging. Please verify before I push to prod."}
            ],
            "testing": [
                {"from": "Alex Thompson", "to": "Team", "message": "Running full test suite now. 127 tests collected..."},
                {"from": "Alex Thompson", "to": "Emily Rodriguez", "message": "UI tests failing on mobile viewport. Missing responsive styles?"},
                {"from": "Emily Rodriguez", "to": "Alex Thompson", "message": "On it! I'll add media queries for mobile breakpoints."},
                {"from": "Alex Thompson", "to": "Marcus Chen", "message": "Performance test shows API response time > 500ms under load."},
                {"from": "Marcus Chen", "to": "Alex Thompson", "message": "I'll add caching and optimize the database queries."}
            ],
            "deployment": [
                {"from": "Jordan Kim", "to": "Team", "message": "Starting production deployment. ETA: 5 minutes."},
                {"from": "Jordan Kim", "to": "Team", "message": "Blue environment is up. Running smoke tests..."},
                {"from": "Alex Thompson", "to": "Jordan Kim", "message": "All smoke tests passing! Good to switch traffic."},
                {"from": "Jordan Kim", "to": "Team", "message": "Switching traffic to blue environment... Done! Zero downtime! 🚀"},
                {"from": "Emily Rodriguez", "to": "Jordan Kim", "message": "Confirmed! Frontend is loading fast. Great job!"}
            ],
            "incident": [
                {"from": "Jordan Kim", "to": "Team", "message": "🚨 ALERT: High error rate detected in production!"},
                {"from": "Marcus Chen", "to": "Jordan Kim", "message": "Checking logs now... Seeing database connection timeouts."},
                {"from": "Jordan Kim", "to": "Marcus Chen", "message": "Database CPU at 98%. Scaling up RDS instance."},
                {"from": "Alex Thompson", "to": "Team", "message": "I can reproduce the issue. Happens with bulk operations."},
                {"from": "Marcus Chen", "to": "Team", "message": "Found it! Missing connection pooling. Deploying fix."}
            ]
        }
        
    async def simulate_planning_phase(self):
        """Simulate initial planning phase"""
        self.project_stage = "planning"
        
        # Marcus starts thinking about architecture
        await self.visualizer.update_agent_activity(
            "Marcus Chen",
            ActivityType.THINKING,
            "Designing API architecture",
            progress=0,
            metadata={"mood": "thoughtful"}
        )
        
        await asyncio.sleep(self.visualizer.pacing.get_delay(2))
        
        # Emily starts UI design
        await self.visualizer.update_agent_activity(
            "Emily Rodriguez",
            ActivityType.DESIGNING,
            "Creating wireframes for task management UI",
            progress=30,
            metadata={"mood": "creative"}
        )
        
        # Send planning messages
        for conv in self.conversation_templates["planning"][:3]:
            await self.visualizer.send_message(
                conv["from"], 
                conv.get("to", "Team"),
                conv["message"]
            )
            await asyncio.sleep(self.visualizer.pacing.get_delay(1.5))
            
    async def simulate_development_phase(self):
        """Simulate active development phase"""
        self.project_stage = "development"
        
        # Update workflow
        self.visualizer.update_workflow("Development Sprint", [
            {"name": "Backend API", "completed": False},
            {"name": "Frontend UI", "completed": False},
            {"name": "Database Schema", "completed": False},
            {"name": "Authentication", "completed": False}
        ])
        
        # Marcus coding backend
        code_snippet = random.choice(self.code_snippets["Marcus Chen"])
        await self.visualizer.update_agent_activity(
            "Marcus Chen",
            ActivityType.CODING,
            "Implementing user authentication endpoints",
            progress=45,
            code_snippet=code_snippet,
            metadata={"mood": "focused"}
        )
        
        await asyncio.sleep(self.visualizer.pacing.get_delay(2))
        
        # Emily coding frontend
        code_snippet = random.choice(self.code_snippets["Emily Rodriguez"])
        await self.visualizer.update_agent_activity(
            "Emily Rodriguez",
            ActivityType.CODING,
            "Building responsive task list component",
            progress=60,
            code_snippet=code_snippet,
            metadata={"mood": "energetic"}
        )
        
        # Alex preparing tests
        await self.visualizer.update_agent_activity(
            "Alex Thompson",
            ActivityType.THINKING,
            "Planning test scenarios for authentication",
            progress=20,
            metadata={"mood": "methodical"}
        )
        
        # Jordan setting up infrastructure
        await self.visualizer.update_agent_activity(
            "Jordan Kim",
            ActivityType.CODING,
            "Writing Terraform configs for AWS infrastructure",
            progress=35,
            metadata={"mood": "focused"}
        )
        
        # Simulate some development conversations
        for conv in self.conversation_templates["development"][:2]:
            await asyncio.sleep(self.visualizer.pacing.get_delay(2))
            await self.visualizer.send_message(
                conv["from"],
                conv.get("to", "Team"),
                conv["message"]
            )
            
    async def simulate_testing_phase(self):
        """Simulate testing phase"""
        self.project_stage = "testing"
        
        # Alex starts testing
        code_snippet = random.choice(self.code_snippets["Alex Thompson"])
        await self.visualizer.update_agent_activity(
            "Alex Thompson",
            ActivityType.TESTING,
            "Running authentication test suite",
            progress=0,
            code_snippet=code_snippet,
            metadata={"mood": "focused"}
        )
        
        # Animate test progress
        for progress in range(0, 101, 10):
            await self.visualizer.update_agent_activity(
                "Alex Thompson",
                ActivityType.TESTING,
                f"Running tests... {progress}% complete",
                progress=progress,
                metadata={"mood": "focused"}
            )
            await asyncio.sleep(self.visualizer.pacing.get_delay(0.5))
            
        # Test results
        await self.visualizer.send_message(
            "Alex Thompson",
            "Team",
            "✅ 127 tests passed, 3 failed. Working on fixes..."
        )
        
        # Other agents respond to test results
        await self.visualizer.update_agent_activity(
            "Marcus Chen",
            ActivityType.DEBUGGING,
            "Fixing authentication edge cases",
            progress=70,
            metadata={"mood": "focused"}
        )
        
        await self.visualizer.update_agent_activity(
            "Emily Rodriguez",
            ActivityType.REVIEWING,
            "Reviewing accessibility test results",
            progress=80,
            metadata={"mood": "thoughtful"}
        )
        
    async def simulate_deployment_phase(self):
        """Simulate deployment phase"""
        self.project_stage = "deployment"
        
        # Jordan prepares deployment
        code_snippet = random.choice(self.code_snippets["Jordan Kim"])
        await self.visualizer.update_agent_activity(
            "Jordan Kim",
            ActivityType.DEPLOYING,
            "Preparing production deployment",
            progress=0,
            code_snippet=code_snippet,
            metadata={"mood": "focused"}
        )
        
        # Update workflow
        self.visualizer.update_workflow("Production Deployment", [
            {"name": "Build Docker images", "completed": True},
            {"name": "Run security scans", "completed": True},
            {"name": "Deploy to staging", "completed": True},
            {"name": "Deploy to production", "completed": False},
            {"name": "Switch traffic", "completed": False}
        ])
        
        # Deployment messages
        for conv in self.conversation_templates["deployment"]:
            await self.visualizer.send_message(
                conv["from"],
                conv.get("to", "Team"),
                conv["message"]
            )
            await asyncio.sleep(self.visualizer.pacing.get_delay(2))
            
            # Update Jordan's progress
            if "Starting" in conv["message"]:
                progress = 20
            elif "Blue environment" in conv["message"]:
                progress = 60
            elif "Switching traffic" in conv["message"]:
                progress = 90
            else:
                progress = 100
                
            await self.visualizer.update_agent_activity(
                "Jordan Kim",
                ActivityType.DEPLOYING,
                "Deploying to production",
                progress=progress,
                metadata={"mood": "efficient" if progress < 100 else "accomplished"}
            )
            
    async def simulate_incident(self):
        """Simulate an incident response"""
        self.project_stage = "incident"
        
        # Alert!
        await self.visualizer.send_message(
            "Jordan Kim",
            "Team",
            "🚨 ALERT: High error rate detected in production!"
        )
        
        # Everyone springs into action
        await self.visualizer.update_agent_activity(
            "Jordan Kim",
            ActivityType.MONITORING,
            "Analyzing system metrics and logs",
            progress=50,
            metadata={"mood": "incident"}
        )
        
        await self.visualizer.update_agent_activity(
            "Marcus Chen",
            ActivityType.DEBUGGING,
            "Investigating API errors",
            progress=30,
            metadata={"mood": "stressed"}
        )
        
        await self.visualizer.update_agent_activity(
            "Alex Thompson",
            ActivityType.TESTING,
            "Running diagnostic tests",
            progress=40,
            metadata={"mood": "alert"}
        )
        
        await self.visualizer.update_agent_activity(
            "Emily Rodriguez",
            ActivityType.MONITORING,
            "Checking frontend error reports",
            progress=60,
            metadata={"mood": "concerned"}
        )
        
        # Incident resolution conversation
        for conv in self.conversation_templates["incident"]:
            await self.visualizer.send_message(
                conv["from"],
                conv.get("to", "Team"),
                conv["message"]
            )
            await asyncio.sleep(self.visualizer.pacing.get_delay(1.5))
            
    async def run_simulation(self, duration: int = 60):
        """Run the full simulation"""
        phases = [
            self.simulate_planning_phase,
            self.simulate_development_phase,
            self.simulate_testing_phase,
            self.simulate_deployment_phase,
            self.simulate_incident
        ]
        
        for phase in phases:
            if not self.visualizer.running:
                break
                
            await phase()
            await asyncio.sleep(self.visualizer.pacing.get_delay(3))
            
        # Final celebration
        if self.visualizer.running:
            await self.visualizer.update_agent_activity(
                "Jordan Kim",
                ActivityType.IDLE,
                "All systems operational! ☕",
                progress=100,
                metadata={"mood": "accomplished"}
            )
            
            for agent in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson"]:
                await self.visualizer.update_agent_activity(
                    agent,
                    ActivityType.IDLE,
                    "Great work team! 🎉",
                    progress=100,
                    metadata={"mood": "accomplished"}
                )