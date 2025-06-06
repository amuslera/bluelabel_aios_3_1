"""
Database models
Generated by Apollo (Simple Agent Experiment)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # TODO: Add entity-specific fields
    
    def __repr__(self):
        return f"<User(id={self.id})>"

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # TODO: Add entity-specific fields
    
    def __repr__(self):
        return f"<Product(id={self.id})>"

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # TODO: Add entity-specific fields
    
    def __repr__(self):
        return f"<Order(id={self.id})>"

class OrderItem(Base):
    __tablename__ = 'orderitems'
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # TODO: Add entity-specific fields
    
    def __repr__(self):
        return f"<OrderItem(id={self.id})>"
