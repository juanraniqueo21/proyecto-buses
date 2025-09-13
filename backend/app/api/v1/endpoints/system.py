"""
Router para endpoints del sistema - health, info, dev tools
Sistema de Gestión de Flota de Buses
"""

import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.dependencies import get_db

# Configuración de base de datos
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")

router = APIRouter()

@router.get("/", summary="Información de la API")
def read_root():
    """Endpoint raíz con información básica de la API"""
    return {
        "message": "Sistema de Gestión de Flota - API REST",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "features": [
            "Gestión completa de buses",
            "Validaciones según normativa chilena", 
            "CRUD con soft delete",
            "Reportes y estadísticas"
        ]
    }

@router.get("/health", summary="Estado de salud del sistema")
def health_check(db: Session = Depends(get_db)):
    """Verificar estado de salud de la API y base de datos usando SQLAlchemy"""
    try:
        # Usar SQLAlchemy en lugar de psycopg2 directo
        db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "api": "operational",
            "database": "connected",
            "architecture": "Clean Architecture + SQLAlchemy",
            "message": "Todos los servicios funcionando correctamente"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "api": "operational", 
            "database": "error",
            "message": f"Problema de conexión a base de datos: {str(e)}"
        }

@router.get("/info", summary="Información del sistema")
def system_info():
    """Información detallada sobre el sistema y sus capacidades"""
    return {
        "sistema": "Sistema de Gestión de Flota de Buses",
        "version": "1.0.0",
        "arquitectura": "Clean Architecture con FastAPI + SQLAlchemy",
        "base_datos": "PostgreSQL 15",
        "contenedores": "Docker Compose",
        "modulos_disponibles": {
            "buses": {
                "descripcion": "Gestión completa de la flota",
                "endpoints": "/api/v1/buses",
                "operaciones": ["CRUD completo", "Reportes", "Validaciones"]
            }
        },
        "modulos_planificados": [
            "Autenticación JWT",
            "Gestión de conductores", 
            "Sistema de rutas",
            "Liquidaciones de sueldos",
            "Generación de PDFs"
        ],
        "documentacion": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@router.get("/dev/db-test", summary="Test de conexión DB", tags=["Desarrollo"])
def test_database(db: Session = Depends(get_db)):
    """
    Endpoint de testing para verificar conexión a PostgreSQL usando SQLAlchemy
    Solo para desarrollo - remover en producción
    """
    try:
        # Verificar versión de PostgreSQL usando SQLAlchemy
        result = db.execute(text("SELECT version()"))
        version = result.scalar()
        
        # Verificar tablas principales
        result = db.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        
        return {
            "status": "Conexión exitosa con SQLAlchemy",
            "postgres_version": version,
            "database": "flota_buses",
            "host": DB_HOST,
            "port": DB_PORT,
            "tablas_disponibles": tables,
            "connection_method": "SQLAlchemy + Dependency Injection"
        }
    except Exception as e:
        return {
            "status": "Error de conexión", 
            "error": str(e),
            "host": DB_HOST,
            "port": DB_PORT
        }