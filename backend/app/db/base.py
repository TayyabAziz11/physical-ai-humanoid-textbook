"""
SQLAlchemy declarative base

This module provides the base class for all ORM models.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all database models

    All ORM models should inherit from this class.
    """
    pass
