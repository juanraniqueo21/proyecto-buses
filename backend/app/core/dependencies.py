
"""
Dependency injection para FastAPI
Sistema de Gestión de Flota de Buses - Refactoring Gradual Paso 1
"""

from sqlalchemy.orm import Session
from app.core.database import obtener_bd

from typing import Generator

def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos.
    Usa la función existente obtener_bd() para mantener compatibilidad.
    """
    yield from obtener_bd()