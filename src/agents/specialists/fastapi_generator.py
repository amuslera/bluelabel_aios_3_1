"""
FastAPI code generation module for Marcus Chen.

Provides templates and generation logic for FastAPI applications.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class APIStyle(Enum):
    """API design styles Marcus can use."""
    REST = "rest"
    GRAPHQL = "graphql"
    ASYNC = "async"
    SYNC = "sync"


@dataclass
class EndpointSpec:
    """Specification for an API endpoint."""
    method: str  # GET, POST, PUT, DELETE, PATCH
    path: str
    description: str
    request_body: Optional[Dict[str, Any]] = None
    response_model: Optional[str] = None
    query_params: Optional[List[str]] = None
    path_params: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    auth_required: bool = True


@dataclass
class ModelSpec:
    """Specification for a data model."""
    name: str
    fields: Dict[str, str]  # field_name -> field_type
    description: str
    validators: Optional[Dict[str, str]] = None
    examples: Optional[Dict[str, Any]] = None


class FastAPITemplates:
    """Marcus's collection of FastAPI templates and patterns."""
    
    @staticmethod
    def get_base_app_template() -> str:
        """Get base FastAPI application template."""
        return '''"""
{description}

Built with ❤️ by Marcus Chen
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import List, Optional

from .models import *
from .database import get_db, init_db
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    logger.info("🚀 Starting up...")
    await init_db()
    yield
    logger.info("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="{title}",
    description="{description}",
    version="{version}",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint."""
    return {{
        "status": "healthy",
        "message": "Welcome to {title}",
        "version": "{version}"
    }}


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check."""
    return {{
        "status": "healthy",
        "database": "connected",
        "version": "{version}"
    }}
'''

    @staticmethod
    def get_model_template(spec: ModelSpec) -> str:
        """Generate Pydantic model from specification."""
        fields = []
        for field_name, field_type in spec.fields.items():
            if field_name in (spec.validators or {}):
                validator = spec.validators[field_name]
                fields.append(f"    {field_name}: {field_type}  # {validator}")
            else:
                fields.append(f"    {field_name}: {field_type}")
        
        fields_str = "\n".join(fields)
        
        example_str = ""
        if spec.examples:
            example_items = [f'            "{k}": {repr(v)}' for k, v in spec.examples.items()]
            example_str = f'''
    
    class Config:
        schema_extra = {{
            "example": {{
{",".join(example_items)}
            }}
        }}'''
        
        return f'''class {spec.name}(BaseModel):
    """{spec.description}"""
{fields_str}{example_str}
'''

    @staticmethod
    def get_crud_endpoints_template(resource_name: str, model_name: str) -> str:
        """Generate CRUD endpoints for a resource."""
        resource_lower = resource_name.lower()
        resource_plural = f"{resource_lower}s"
        
        return f'''# {resource_name} endpoints

@app.get("/{resource_plural}", response_model=List[{model_name}], tags=["{resource_lower}"])
async def get_{resource_plural}(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all {resource_plural} with pagination."""
    try:
        query = select({model_name}).offset(skip).limit(limit)
        result = await db.execute(query)
        {resource_plural} = result.scalars().all()
        return {resource_plural}
    except Exception as e:
        logger.error(f"Error fetching {resource_plural}: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch {resource_plural}"
        )


@app.get("/{resource_plural}/{{id}}", response_model={model_name}, tags=["{resource_lower}"])
async def get_{resource_lower}(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific {resource_lower} by ID."""
    query = select({model_name}).where({model_name}.id == id)
    result = await db.execute(query)
    {resource_lower} = result.scalar_one_or_none()
    
    if not {resource_lower}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name} not found"
        )
    
    return {resource_lower}


@app.post("/{resource_plural}", response_model={model_name}, status_code=status.HTTP_201_CREATED, tags=["{resource_lower}"])
async def create_{resource_lower}(
    {resource_lower}: {model_name}Create,
    db: AsyncSession = Depends(get_db)
):
    """Create a new {resource_lower}."""
    try:
        db_{resource_lower} = {model_name}(**{resource_lower}.dict())
        db.add(db_{resource_lower})
        await db.commit()
        await db.refresh(db_{resource_lower})
        return db_{resource_lower}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating {resource_lower}: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create {resource_lower}"
        )


@app.put("/{resource_plural}/{{id}}", response_model={model_name}, tags=["{resource_lower}"])
async def update_{resource_lower}(
    id: int,
    {resource_lower}_update: {model_name}Update,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing {resource_lower}."""
    query = select({model_name}).where({model_name}.id == id)
    result = await db.execute(query)
    {resource_lower} = result.scalar_one_or_none()
    
    if not {resource_lower}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name} not found"
        )
    
    # Update fields
    update_data = {resource_lower}_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr({resource_lower}, field, value)
    
    try:
        await db.commit()
        await db.refresh({resource_lower})
        return {resource_lower}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating {resource_lower}: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update {resource_lower}"
        )


@app.delete("/{resource_plural}/{{id}}", status_code=status.HTTP_204_NO_CONTENT, tags=["{resource_lower}"])
async def delete_{resource_lower}(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a {resource_lower}."""
    query = select({model_name}).where({model_name}.id == id)
    result = await db.execute(query)
    {resource_lower} = result.scalar_one_or_none()
    
    if not {resource_lower}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name} not found"
        )
    
    try:
        await db.delete({resource_lower})
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting {resource_lower}: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete {resource_lower}"
        )
'''

    @staticmethod
    def get_auth_middleware_template() -> str:
        """Generate authentication middleware."""
        return '''from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from .config import settings
from .models import User

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and return current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Here you would typically fetch the user from database
    # For now, returning a mock user
    return {"username": username, "id": payload.get("user_id")}
'''

    @staticmethod
    def get_database_config_template() -> str:
        """Generate database configuration."""
        return '''"""
Database configuration and session management.

Following Marcus's best practices for async database handling.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create declarative base with naming convention
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

Base = declarative_base(metadata=metadata)


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        # In production, use Alembic migrations instead
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created")
'''

    @staticmethod
    def get_error_handler_template() -> str:
        """Generate error handling utilities."""
        return '''"""
Custom error handlers and exceptions.

Marcus's approach to clean error handling.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base API exception."""
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions."""
    logger.error(f"API Exception: {exc.message} - Details: {exc.details}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "path": str(request.url)
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with better formatting."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"][1:]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation failed",
            "details": errors,
            "path": str(request.url)
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": str(request.url)
        }
    )


def setup_exception_handlers(app):
    """Register all exception handlers."""
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
'''


class FastAPICodeGenerator:
    """Marcus's FastAPI code generation engine."""
    
    def __init__(self):
        self.templates = FastAPITemplates()
        
    def generate_api_structure(self, project_name: str, description: str) -> Dict[str, str]:
        """Generate complete API project structure."""
        return {
            "main.py": self.templates.get_base_app_template().format(
                title=project_name,
                description=description,
                version="1.0.0"
            ),
            "models.py": self._generate_base_models(),
            "database.py": self.templates.get_database_config_template(),
            "config.py": self._generate_config(),
            "errors.py": self.templates.get_error_handler_template(),
            "auth.py": self.templates.get_auth_middleware_template(),
            "requirements.txt": self._generate_requirements(),
            ".env.example": self._generate_env_example(),
            "README.md": self._generate_readme(project_name, description),
        }
    
    def generate_crud_api(self, resource_name: str, fields: Dict[str, str]) -> Dict[str, str]:
        """Generate a complete CRUD API for a resource."""
        model_spec = ModelSpec(
            name=f"{resource_name}",
            fields=fields,
            description=f"{resource_name} model for API"
        )
        
        # Generate model variations
        base_model = self.templates.get_model_template(model_spec)
        create_model = base_model.replace(f"class {resource_name}", f"class {resource_name}Create")
        update_model = base_model.replace(f"class {resource_name}", f"class {resource_name}Update")
        
        # Generate endpoints
        endpoints = self.templates.get_crud_endpoints_template(resource_name, resource_name)
        
        return {
            "models.py": f"{base_model}\n\n{create_model}\n\n{update_model}",
            "endpoints.py": endpoints,
        }
    
    def _generate_base_models(self) -> str:
        """Generate base model imports and common models."""
        return '''"""
Data models for the API.

Using Pydantic for validation and SQLAlchemy for ORM.
"""

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List

from .database import Base


# SQLAlchemy Models

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Pydantic Models

class BaseResponse(BaseModel):
    """Base response model with common fields."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True
'''

    def _generate_config(self) -> str:
        """Generate configuration module."""
        return '''"""
Application configuration.

Using Pydantic settings for environment variable management.
"""

from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    APP_NAME: str = "FastAPI App"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
'''

    def _generate_requirements(self) -> str:
        """Generate requirements.txt."""
        return '''# FastAPI and dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
black==23.11.0
ruff==0.1.6

# Monitoring
prometheus-client==0.19.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
'''

    def _generate_env_example(self) -> str:
        """Generate .env.example file."""
        return '''# Application
APP_NAME="My FastAPI App"
DEBUG=False

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]
'''

    def _generate_readme(self, project_name: str, description: str) -> str:
        """Generate README.md."""
        return f'''# {project_name}

{description}

Built with FastAPI by Marcus Chen 🚀

## Features

- ⚡ Fast async API with FastAPI
- 🔐 JWT authentication
- 📊 PostgreSQL with async SQLAlchemy
- 🧪 Comprehensive test suite
- 📝 Auto-generated API documentation
- 🔍 Request validation with Pydantic
- 🚨 Structured error handling
- 📈 Production-ready with monitoring

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and update values
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `alembic upgrade head`
5. Start the server: `uvicorn main:app --reload`

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with: `pytest`

## Contributing

PRs welcome! Please follow the existing code style.

---

Made with ❤️ and ☕ by Marcus Chen
'''