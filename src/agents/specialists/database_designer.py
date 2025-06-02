"""
Database design module for Marcus Chen.

Provides database schema generation, optimization suggestions, and migration support.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class DatabaseType(Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"


class RelationType(Enum):
    """Database relationship types."""
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_MANY = "many_to_many"


@dataclass
class ColumnSpec:
    """Specification for a database column."""
    name: str
    type: str  # SQLAlchemy type string
    nullable: bool = True
    unique: bool = False
    primary_key: bool = False
    foreign_key: Optional[str] = None  # table.column format
    default: Optional[Any] = None
    index: bool = False
    constraints: Optional[List[str]] = None


@dataclass
class TableSpec:
    """Specification for a database table."""
    name: str
    columns: List[ColumnSpec]
    indexes: Optional[List[List[str]]] = None  # Multi-column indexes
    constraints: Optional[List[str]] = None
    comment: Optional[str] = None


@dataclass
class RelationshipSpec:
    """Specification for table relationships."""
    from_table: str
    to_table: str
    relation_type: RelationType
    from_column: str
    to_column: str
    cascade_delete: bool = False
    back_populates: Optional[str] = None


class DatabaseDesigner:
    """Marcus's database design engine."""
    
    def __init__(self, db_type: DatabaseType = DatabaseType.POSTGRESQL):
        self.db_type = db_type
        
    def generate_sqlalchemy_models(self, tables: List[TableSpec], relationships: List[RelationshipSpec]) -> str:
        """Generate SQLAlchemy model classes."""
        imports = self._generate_imports()
        base_class = self._generate_base_class()
        models = []
        
        # Generate table models
        for table in tables:
            model = self._generate_model(table, relationships)
            models.append(model)
        
        # Generate association tables for many-to-many
        association_tables = self._generate_association_tables(relationships)
        
        return f"{imports}\n\n{base_class}\n\n{association_tables}\n\n{''.join(models)}"
    
    def _generate_imports(self) -> str:
        """Generate necessary imports."""
        return '''"""
Database models designed by Marcus Chen.

Using SQLAlchemy with async support and best practices.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, 
    DateTime, Date, JSON, ForeignKey, Table,
    UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, List

Base = declarative_base()'''
    
    def _generate_base_class(self) -> str:
        """Generate base model class with common fields."""
        return '''
class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BaseModel(Base, TimestampMixin):
    """Base model with common fields."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"'''
    
    def _generate_model(self, table: TableSpec, relationships: List[RelationshipSpec]) -> str:
        """Generate a single model class."""
        class_name = self._table_name_to_class_name(table.name)
        
        # Start class definition
        model = f"\n\nclass {class_name}(BaseModel):\n"
        
        # Add docstring
        if table.comment:
            model += f'    """{table.comment}"""\n'
        else:
            model += f'    """{class_name} model."""\n'
        
        # Table name
        model += f"    __tablename__ = '{table.name}'\n\n"
        
        # Add columns
        for col in table.columns:
            if col.name not in ['id', 'created_at', 'updated_at']:  # Skip base fields
                model += self._generate_column(col)
        
        # Add relationships
        table_relationships = [r for r in relationships if r.from_table == table.name]
        if table_relationships:
            model += "\n    # Relationships\n"
            for rel in table_relationships:
                model += self._generate_relationship(rel)
        
        # Add indexes
        if table.indexes:
            model += "\n    # Indexes\n"
            for idx_columns in table.indexes:
                idx_name = f"idx_{table.name}_{'_'.join(idx_columns)}"
                model += f"    __table_args__ = (Index('{idx_name}', {', '.join(repr(c) for c in idx_columns)}),)\n"
        
        # Add constraints
        if table.constraints:
            model += "\n    # Constraints\n"
            for constraint in table.constraints:
                model += f"    # {constraint}\n"
        
        # Add string representation
        model += f"\n    def __repr__(self):\n"
        model += f"        return f\"<{class_name}(id={{self.id}})>\"\n"
        
        return model
    
    def _generate_column(self, col: ColumnSpec) -> str:
        """Generate a column definition."""
        parts = [f"    {col.name} = Column("]
        
        # Column type
        parts.append(col.type)
        
        # Foreign key
        if col.foreign_key:
            parts.append(f", ForeignKey('{col.foreign_key}')")
        
        # Other attributes
        if col.primary_key:
            parts.append(", primary_key=True")
        if col.unique:
            parts.append(", unique=True")
        if not col.nullable:
            parts.append(", nullable=False")
        if col.index:
            parts.append(", index=True")
        if col.default is not None:
            if isinstance(col.default, str):
                parts.append(f", default='{col.default}'")
            else:
                parts.append(f", default={col.default}")
        
        parts.append(")\n")
        return "".join(parts)
    
    def _generate_relationship(self, rel: RelationshipSpec) -> str:
        """Generate a relationship definition."""
        target_class = self._table_name_to_class_name(rel.to_table)
        
        if rel.relation_type == RelationType.ONE_TO_MANY:
            return f"    {rel.to_table} = relationship('{target_class}', back_populates='{rel.back_populates or rel.from_table}', cascade='all, delete-orphan' if {rel.cascade_delete} else None)\n"
        elif rel.relation_type == RelationType.MANY_TO_MANY:
            assoc_table = f"{rel.from_table}_{rel.to_table}_association"
            return f"    {rel.to_table} = relationship('{target_class}', secondary='{assoc_table}', back_populates='{rel.back_populates or rel.from_table}')\n"
        else:  # ONE_TO_ONE
            return f"    {rel.to_table} = relationship('{target_class}', uselist=False, back_populates='{rel.back_populates or rel.from_table}')\n"
    
    def _generate_association_tables(self, relationships: List[RelationshipSpec]) -> str:
        """Generate association tables for many-to-many relationships."""
        tables = []
        
        for rel in relationships:
            if rel.relation_type == RelationType.MANY_TO_MANY:
                table_name = f"{rel.from_table}_{rel.to_table}_association"
                table = f"""
{table_name} = Table(
    '{table_name}',
    Base.metadata,
    Column('{rel.from_table}_id', Integer, ForeignKey('{rel.from_table}.id'), primary_key=True),
    Column('{rel.to_table}_id', Integer, ForeignKey('{rel.to_table}.id'), primary_key=True)
)"""
                tables.append(table)
        
        return "\n".join(tables)
    
    def _table_name_to_class_name(self, table_name: str) -> str:
        """Convert table_name to ClassName."""
        parts = table_name.split('_')
        return ''.join(part.capitalize() for part in parts)
    
    def generate_migration_script(self, tables: List[TableSpec]) -> str:
        """Generate Alembic migration script."""
        return f'''"""Create {', '.join(t.name for t in tables)} tables

Revision ID: generated_by_marcus
Create Date: {datetime.utcnow().isoformat()}

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'generated_by_marcus'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create tables."""
{self._generate_create_tables(tables)}


def downgrade():
    """Drop tables."""
{self._generate_drop_tables(tables)}
'''
    
    def _generate_create_tables(self, tables: List[TableSpec]) -> str:
        """Generate CREATE TABLE statements."""
        statements = []
        
        for table in tables:
            stmt = f"    op.create_table('{table.name}',\n"
            for col in table.columns:
                stmt += f"        sa.Column('{col.name}', sa.{col.type}"
                if not col.nullable:
                    stmt += ", nullable=False"
                if col.primary_key:
                    stmt += ", primary_key=True"
                stmt += "),\n"
            stmt += "    )\n"
            statements.append(stmt)
        
        return "\n".join(statements)
    
    def _generate_drop_tables(self, tables: List[TableSpec]) -> str:
        """Generate DROP TABLE statements."""
        statements = []
        for table in reversed(tables):  # Reverse order for foreign keys
            statements.append(f"    op.drop_table('{table.name}')")
        return "\n".join(statements)
    
    def suggest_indexes(self, table: TableSpec, query_patterns: List[str]) -> List[str]:
        """Suggest indexes based on query patterns."""
        suggestions = []
        
        # Analyze query patterns
        for pattern in query_patterns:
            pattern_lower = pattern.lower()
            
            # Look for WHERE clauses
            if "where" in pattern_lower:
                # Extract column names (simplified)
                for col in table.columns:
                    if col.name in pattern_lower and not col.index and not col.primary_key:
                        suggestions.append(f"CREATE INDEX idx_{table.name}_{col.name} ON {table.name}({col.name});")
            
            # Look for JOIN conditions
            if "join" in pattern_lower:
                for col in table.columns:
                    if col.foreign_key and col.name in pattern_lower:
                        suggestions.append(f"CREATE INDEX idx_{table.name}_{col.name} ON {table.name}({col.name});")
        
        # Remove duplicates
        return list(set(suggestions))
    
    def optimize_schema(self, tables: List[TableSpec]) -> Dict[str, List[str]]:
        """Provide schema optimization suggestions."""
        optimizations = {}
        
        for table in tables:
            suggestions = []
            
            # Check for missing indexes on foreign keys
            for col in table.columns:
                if col.foreign_key and not col.index:
                    suggestions.append(f"Add index to foreign key column '{col.name}'")
            
            # Check for large text columns without separate storage
            for col in table.columns:
                if col.type == "Text" and not any(c.name == f"{col.name}_summary" for c in table.columns):
                    suggestions.append(f"Consider adding a summary column for '{col.name}' for faster queries")
            
            # Check for missing timestamps
            has_created = any(col.name == "created_at" for col in table.columns)
            has_updated = any(col.name == "updated_at" for col in table.columns)
            if not has_created:
                suggestions.append("Add 'created_at' timestamp column")
            if not has_updated:
                suggestions.append("Add 'updated_at' timestamp column")
            
            if suggestions:
                optimizations[table.name] = suggestions
        
        return optimizations