"""
CI/CD Pipeline Management for Jordan Kim

Handles pipeline generation, configuration, and automation for various
platforms including GitHub Actions, GitLab CI, Jenkins, and more.
"""

import textwrap
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    """Configuration for a CI/CD pipeline"""
    platform: str  # 'github', 'gitlab', 'jenkins', 'azure', 'bitbucket'
    project_name: str
    language: str  # 'python', 'javascript', 'java', 'go', etc.
    framework: Optional[str] = None  # 'django', 'fastapi', 'react', 'vue', etc.
    test_framework: Optional[str] = None  # 'pytest', 'jest', 'junit', etc.
    deployment_target: str = 'kubernetes'  # 'kubernetes', 'ecs', 'lambda', 'vm'
    environments: List[str] = field(default_factory=lambda: ['dev', 'staging', 'prod'])
    docker_registry: str = 'docker.io'
    enable_security_scan: bool = True
    enable_code_quality: bool = True
    enable_performance_tests: bool = False
    notification_channels: List[str] = field(default_factory=list)


class CICDManager:
    """Manages CI/CD pipeline generation and configuration"""
    
    def __init__(self):
        self.supported_platforms = ['github', 'gitlab', 'jenkins', 'azure', 'bitbucket']
        self.templates = {}
        
    def generate_pipeline(self, config: PipelineConfig) -> Dict[str, str]:
        """Generate complete CI/CD pipeline configuration"""
        if config.platform == 'github':
            return self._generate_github_actions(config)
        elif config.platform == 'gitlab':
            return self._generate_gitlab_ci(config)
        elif config.platform == 'jenkins':
            return self._generate_jenkinsfile(config)
        else:
            return self._generate_generic_pipeline(config)
            
    def _generate_github_actions(self, config: PipelineConfig) -> Dict[str, str]:
        """Generate GitHub Actions workflow"""
        workflows = {}
        
        # Main CI/CD workflow
        workflows['.github/workflows/ci-cd.yml'] = self._github_main_workflow(config)
        
        # PR workflow
        workflows['.github/workflows/pr-check.yml'] = self._github_pr_workflow(config)
        
        # Security scanning workflow
        if config.enable_security_scan:
            workflows['.github/workflows/security.yml'] = self._github_security_workflow(config)
            
        # Scheduled dependency updates
        workflows['.github/workflows/dependency-update.yml'] = self._github_dependency_workflow(config)
        
        return workflows
        
    def _github_main_workflow(self, config: PipelineConfig) -> str:
        """Generate main GitHub Actions workflow"""
        return f"""name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  workflow_dispatch:

env:
  REGISTRY: {config.docker_registry}
  IMAGE_NAME: ${{{{ github.repository }}}}

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up {config.language.title()}
      uses: {self._get_language_setup_action(config.language)}
      
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: {self._get_cache_path(config.language)}
        key: ${{{{ runner.os }}}}-deps-${{{{ hashFiles('**/package-lock.json', '**/requirements.txt', '**/go.sum') }}}}
        
    - name: Install dependencies
      run: {self._get_install_command(config)}
      
    - name: Run tests
      run: {self._get_test_command(config)}
      
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        
  {self._generate_security_job(config) if config.enable_security_scan else ''}
  
  {self._generate_code_quality_job(config) if config.enable_code_quality else ''}
  
  build:
    name: Build and Push
    needs: [test{', security' if config.enable_security_scan else ''}{', quality' if config.enable_code_quality else ''}]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
      
    - name: Log in to Registry
      uses: docker/login-action@v2
      with:
        registry: ${{{{ env.REGISTRY }}}}
        username: ${{{{ github.actor }}}}
        password: ${{{{ secrets.GITHUB_TOKEN }}}}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{{{ env.REGISTRY }}}}/${{{{ env.IMAGE_NAME }}}}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{{{version}}}}
          type=semver,pattern={{{{major}}}}.{{{{minor}}}}
          type=sha
          
    - name: Build and push image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{{{ steps.meta.outputs.tags }}}}
        labels: ${{{{ steps.meta.outputs.labels }}}}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
  {self._generate_deployment_jobs(config)}
"""

    def _github_pr_workflow(self, config: PipelineConfig) -> str:
        """Generate PR check workflow"""
        return f"""name: PR Checks

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  lint:
    name: Lint Code
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up {config.language.title()}
      uses: {self._get_language_setup_action(config.language)}
      
    - name: Run linter
      run: {self._get_lint_command(config)}
      
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        {self._get_test_matrix(config)}
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up environment
      uses: {self._get_language_setup_action(config.language)}
      {self._get_matrix_setup(config)}
      
    - name: Install dependencies
      run: {self._get_install_command(config)}
      
    - name: Run tests
      run: {self._get_test_command(config)}
      
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
"""

    def _github_security_workflow(self, config: PipelineConfig) -> str:
        """Generate security scanning workflow"""
        return f"""name: Security Scanning

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2 AM

jobs:
  dependency-check:
    name: Dependency Security Check
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/{config.language}@master
      env:
        SNYK_TOKEN: ${{{{ secrets.SNYK_TOKEN }}}}
        
  container-scan:
    name: Container Security Scan
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build image for scanning
      run: docker build -t localscan:${{{{ github.sha }}}} .
      
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'localscan:${{{{ github.sha }}}}'
        format: 'table'
        exit-code: '1'
        ignore-unfixed: true
        vuln-type: 'os,library'
        severity: 'CRITICAL,HIGH'
        
  code-scan:
    name: Code Security Analysis
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: {config.language}
        
    - name: Autobuild
      uses: github/codeql-action/autobuild@v2
      
    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
"""

    def _github_dependency_workflow(self, config: PipelineConfig) -> str:
        """Generate dependency update workflow"""
        return f"""name: Dependency Updates

on:
  schedule:
    - cron: '0 3 * * 1'  # Weekly on Monday at 3 AM
  workflow_dispatch:

jobs:
  update-dependencies:
    name: Update Dependencies
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up {config.language.title()}
      uses: {self._get_language_setup_action(config.language)}
      
    - name: Update dependencies
      run: |
        {self._get_dependency_update_command(config)}
        
    - name: Run tests
      run: {self._get_test_command(config)}
      
    - name: Create Pull Request
      uses: peter-evans/create-pull-request@v5
      with:
        commit-message: 'chore: update dependencies'
        title: 'Automated dependency updates'
        body: |
          Automated dependency updates for the week.
          
          Please review the changes and ensure all tests pass.
        branch: automated-dependency-updates
        delete-branch: true
"""

    def _generate_gitlab_ci(self, config: PipelineConfig) -> Dict[str, str]:
        """Generate GitLab CI configuration"""
        return {
            '.gitlab-ci.yml': f"""# GitLab CI/CD Configuration
# Generated by Jordan Kim - DevOps Engineer

stages:
  - test
  - build
  - security
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

.test-template:
  stage: test
  image: {self._get_ci_image(config.language)}
  before_script:
    - {self._get_install_command(config)}
  cache:
    paths:
      - {self._get_cache_path(config.language)}

test:unit:
  extends: .test-template
  script:
    - {self._get_test_command(config)}
  coverage: '/{self._get_coverage_regex(config.language)}/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

test:lint:
  extends: .test-template
  script:
    - {self._get_lint_command(config)}

build:docker:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $IMAGE_TAG .
    - docker push $IMAGE_TAG
    - docker tag $IMAGE_TAG $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main
    - develop

security:scan:
  stage: security
  image: 
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy image --exit-code 0 --no-progress $IMAGE_TAG
    - trivy image --exit-code 1 --severity HIGH,CRITICAL --no-progress $IMAGE_TAG
  allow_failure: true

{self._generate_gitlab_deployment_jobs(config)}

# Notification job
notify:slack:
  stage: .post
  image: appropriate/curl:latest
  script:
    - |
      if [ "$CI_JOB_STATUS" == "success" ]; then
        curl -X POST $SLACK_WEBHOOK -H 'Content-type: application/json' \
          --data '{{"text":"✅ Pipeline succeeded for $CI_PROJECT_NAME!"}}'
      else
        curl -X POST $SLACK_WEBHOOK -H 'Content-type: application/json' \
          --data '{{"text":"❌ Pipeline failed for $CI_PROJECT_NAME!"}}'
      fi
  when: always
  only:
    variables:
      - $SLACK_WEBHOOK
"""
        }

    def _generate_jenkinsfile(self, config: PipelineConfig) -> Dict[str, str]:
        """Generate Jenkinsfile"""
        return {
            'Jenkinsfile': f"""// Jenkinsfile - Declarative Pipeline
// Generated by Jordan Kim - DevOps Engineer

pipeline {{
    agent any
    
    environment {{
        DOCKER_REGISTRY = '{config.docker_registry}'
        IMAGE_NAME = "{config.project_name}"
        IMAGE_TAG = "${{env.BUILD_NUMBER}}"
    }}
    
    options {{
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
                script {{
                    env.GIT_COMMIT = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                    env.GIT_BRANCH = sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
                }}
            }}
        }}
        
        stage('Test') {{
            parallel {{
                stage('Unit Tests') {{
                    steps {{
                        sh '{self._get_test_command(config)}'
                        {self._get_test_report_step(config)}
                    }}
                }}
                
                stage('Lint') {{
                    steps {{
                        sh '{self._get_lint_command(config)}'
                    }}
                }}
                
                stage('Security Scan') {{
                    steps {{
                        sh '''
                            docker run --rm -v "$PWD":/src \
                              aquasec/trivy fs --exit-code 0 /src
                        '''
                    }}
                }}
            }}
        }}
        
        stage('Build') {{
            steps {{
                script {{
                    docker.build("${{env.IMAGE_NAME}}:${{env.IMAGE_TAG}}")
                    docker.build("${{env.IMAGE_NAME}}:latest")
                }}
            }}
        }}
        
        stage('Push') {{
            when {{
                branch pattern: "main|develop", comparator: "REGEXP"
            }}
            steps {{
                script {{
                    docker.withRegistry("https://${{env.DOCKER_REGISTRY}}", 'docker-credentials') {{
                        docker.image("${{env.IMAGE_NAME}}:${{env.IMAGE_TAG}}").push()
                        docker.image("${{env.IMAGE_NAME}}:latest").push()
                    }}
                }}
            }}
        }}
        
        {self._generate_jenkins_deployment_stages(config)}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
        success {{
            echo 'Pipeline succeeded!'
            {self._generate_notification_step(config, 'success')}
        }}
        failure {{
            echo 'Pipeline failed!'
            {self._generate_notification_step(config, 'failure')}
        }}
    }}
}}
"""
        }

    def _get_language_setup_action(self, language: str) -> str:
        """Get the appropriate GitHub Action for language setup"""
        actions = {
            'python': 'actions/setup-python@v4\n      with:\n        python-version: "3.11"',
            'javascript': 'actions/setup-node@v3\n      with:\n        node-version: "18"',
            'java': 'actions/setup-java@v3\n      with:\n        java-version: "17"\n        distribution: "temurin"',
            'go': 'actions/setup-go@v4\n      with:\n        go-version: "1.21"',
            'ruby': 'ruby/setup-ruby@v1\n      with:\n        ruby-version: "3.1"',
            'rust': 'actions-rs/toolchain@v1\n      with:\n        toolchain: stable',
        }
        return actions.get(language, 'actions/setup-node@v3')

    def _get_cache_path(self, language: str) -> str:
        """Get cache paths for different languages"""
        paths = {
            'python': '~/.cache/pip',
            'javascript': 'node_modules',
            'java': '~/.m2',
            'go': '~/go/pkg/mod',
            'ruby': 'vendor/bundle',
            'rust': '~/.cargo',
        }
        return paths.get(language, 'cache')

    def _get_install_command(self, config: PipelineConfig) -> str:
        """Get dependency installation command"""
        commands = {
            'python': 'pip install -r requirements.txt',
            'javascript': 'npm ci',
            'java': 'mvn clean install -DskipTests',
            'go': 'go mod download',
            'ruby': 'bundle install',
            'rust': 'cargo build --release',
        }
        
        # Framework-specific adjustments
        if config.framework == 'django':
            return 'pip install -r requirements.txt && python manage.py collectstatic --noinput'
        elif config.framework == 'react':
            return 'npm ci && npm run build'
            
        return commands.get(config.language, 'echo "No install command"')

    def _get_test_command(self, config: PipelineConfig) -> str:
        """Get test execution command"""
        if config.test_framework:
            frameworks = {
                'pytest': 'pytest --cov=. --cov-report=xml',
                'jest': 'npm test -- --coverage',
                'junit': 'mvn test',
                'go test': 'go test -v -coverprofile=coverage.out ./...',
                'rspec': 'bundle exec rspec',
                'cargo': 'cargo test',
            }
            return frameworks.get(config.test_framework, 'echo "No test command"')
            
        # Default by language
        commands = {
            'python': 'pytest',
            'javascript': 'npm test',
            'java': 'mvn test',
            'go': 'go test ./...',
            'ruby': 'bundle exec rake test',
            'rust': 'cargo test',
        }
        return commands.get(config.language, 'echo "No test command"')

    def _get_lint_command(self, config: PipelineConfig) -> str:
        """Get linting command"""
        commands = {
            'python': 'ruff check . && mypy .',
            'javascript': 'npm run lint',
            'java': 'mvn checkstyle:check',
            'go': 'golangci-lint run',
            'ruby': 'rubocop',
            'rust': 'cargo clippy -- -D warnings',
        }
        return commands.get(config.language, 'echo "No lint command"')

    def _get_ci_image(self, language: str) -> str:
        """Get Docker image for CI"""
        images = {
            'python': 'python:3.11-slim',
            'javascript': 'node:18-alpine',
            'java': 'maven:3.8-openjdk-17',
            'go': 'golang:1.21-alpine',
            'ruby': 'ruby:3.1-slim',
            'rust': 'rust:latest',
        }
        return images.get(language, 'ubuntu:latest')

    def _get_coverage_regex(self, language: str) -> str:
        """Get coverage regex pattern"""
        patterns = {
            'python': r'TOTAL.*\s+(\d+)%',
            'javascript': r'All files.*?\s+(\d+\.?\d*)',
            'java': r'Total.*?(\d+)%',
            'go': r'coverage: (\d+\.?\d*)%',
        }
        return patterns.get(language, r'(\d+)%')

    def _generate_deployment_jobs(self, config: PipelineConfig) -> str:
        """Generate deployment jobs for GitHub Actions"""
        jobs = []
        
        for env in config.environments:
            if env == 'prod':
                needs = "['build', 'deploy-staging']"
                condition = "github.ref == 'refs/heads/main'"
            elif env == 'staging':
                needs = "['build']"
                condition = "github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'"
            else:
                needs = "['build']"
                condition = "github.ref == 'refs/heads/develop'"
                
            jobs.append(f"""
  deploy-{env}:
    name: Deploy to {env.title()}
    needs: {needs}
    runs-on: ubuntu-latest
    if: {condition}
    environment:
      name: {env}
      url: https://{env}.{config.project_name}.com
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to {env.title()}
      run: |
        echo "Deploying to {env} environment"
        # Add your deployment script here
        kubectl set image deployment/{config.project_name} \\
          app=${{{{ env.REGISTRY }}}}/${{{{ env.IMAGE_NAME }}}}:${{{{ github.sha }}}} \\
          -n {env}
""")
        
        return '\n'.join(jobs)

    def _generate_gitlab_deployment_jobs(self, config: PipelineConfig) -> str:
        """Generate deployment jobs for GitLab CI"""
        jobs = []
        
        for env in config.environments:
            jobs.append(f"""
deploy:{env}:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/{config.project_name} app=$IMAGE_TAG -n {env}
    - kubectl rollout status deployment/{config.project_name} -n {env}
  environment:
    name: {env}
    url: https://{env}.{config.project_name}.com
  only:
    - {'main' if env == 'prod' else 'main\n    - develop'}
""")
        
        return '\n'.join(jobs)

    def _generate_jenkins_deployment_stages(self, config: PipelineConfig) -> str:
        """Generate deployment stages for Jenkins"""
        stages = []
        
        for env in config.environments:
            stages.append(f"""
        stage('Deploy to {env.title()}') {{
            when {{
                branch pattern: "{'main' if env == 'prod' else 'main|develop'}", comparator: "REGEXP"
            }}
            steps {{
                script {{
                    sh '''
                        kubectl set image deployment/{config.project_name} \\
                          app=${{env.IMAGE_NAME}}:${{env.IMAGE_TAG}} \\
                          -n {env}
                        kubectl rollout status deployment/{config.project_name} -n {env}
                    '''
                }}
            }}
        }}""")
        
        return '\n'.join(stages)

    def _generate_security_job(self, config: PipelineConfig) -> str:
        """Generate security scanning job"""
        return """
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Upload scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
"""

    def _generate_code_quality_job(self, config: PipelineConfig) -> str:
        """Generate code quality job"""
        return f"""
  quality:
    name: Code Quality
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: SonarQube Scan
      uses: sonarsource/sonarqube-scan-action@master
      env:
        GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        SONAR_TOKEN: ${{{{ secrets.SONAR_TOKEN }}}}
"""

    def _get_test_matrix(self, config: PipelineConfig) -> str:
        """Get test matrix configuration"""
        if config.language == 'python':
            return 'python-version: ["3.9", "3.10", "3.11"]'
        elif config.language == 'javascript':
            return 'node-version: ["16", "18", "20"]'
        elif config.language == 'java':
            return 'java-version: ["11", "17", "21"]'
        else:
            return 'os: [ubuntu-latest]'

    def _get_matrix_setup(self, config: PipelineConfig) -> str:
        """Get matrix-specific setup"""
        if config.language in ['python', 'javascript', 'java']:
            return f"""with:
        {config.language}-version: ${{{{ matrix.{config.language}-version }}}}"""
        return ""

    def _get_dependency_update_command(self, config: PipelineConfig) -> str:
        """Get dependency update command"""
        commands = {
            'python': 'pip-upgrade requirements.txt',
            'javascript': 'npm update && npm audit fix',
            'java': 'mvn versions:use-latest-releases',
            'go': 'go get -u ./... && go mod tidy',
            'ruby': 'bundle update',
            'rust': 'cargo update',
        }
        return commands.get(config.language, 'echo "No update command"')

    def _get_test_report_step(self, config: PipelineConfig) -> str:
        """Get test report publishing step for Jenkins"""
        if config.language == 'python':
            return "junit 'test-results/*.xml'"
        elif config.language == 'javascript':
            return "junit 'test-results/jest-*.xml'"
        elif config.language == 'java':
            return "junit '**/target/surefire-reports/*.xml'"
        else:
            return "echo 'No test reports to publish'"

    def _generate_notification_step(self, config: PipelineConfig, status: str) -> str:
        """Generate notification step"""
        if 'slack' in config.notification_channels:
            emoji = '✅' if status == 'success' else '❌'
            return f"""
            slackSend(
                color: '{status}',
                message: "{emoji} Build #{env.BUILD_NUMBER} {status}: ${env.JOB_NAME}"
            )"""
        return "echo 'No notifications configured'"

    def _generate_generic_pipeline(self, config: PipelineConfig) -> Dict[str, str]:
        """Generate a generic pipeline template"""
        return {
            'ci-cd-pipeline.yml': f"""# Generic CI/CD Pipeline
# Platform: {config.platform}
# Generated by Jordan Kim - DevOps Engineer

# This is a template pipeline. Please customize for your specific platform.

pipeline:
  name: {config.project_name}-pipeline
  
  stages:
    - test
    - build
    - security
    - deploy
    
  test:
    steps:
      - name: Install dependencies
        command: {self._get_install_command(config)}
      - name: Run tests
        command: {self._get_test_command(config)}
      - name: Run linter
        command: {self._get_lint_command(config)}
        
  build:
    steps:
      - name: Build application
        command: docker build -t {config.project_name}:latest .
      - name: Push to registry
        command: docker push {config.docker_registry}/{config.project_name}:latest
        
  security:
    steps:
      - name: Scan for vulnerabilities
        command: trivy image {config.project_name}:latest
        
  deploy:
    environments: {config.environments}
    steps:
      - name: Deploy to environment
        command: |
          kubectl set image deployment/{config.project_name} \\
            app={config.docker_registry}/{config.project_name}:latest
"""
        }