"""
Sistema de Gestión de Flota de Buses
Aplicación principal FastAPI - Arquitectura limpia
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

# Importar routers
from app.api.v1.endpoints.buses import router as buses_router

# Configuración de base de datos
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")

# Configurar la aplicación FastAPI
app = FastAPI(
    title="Sistema de Gestión de Flota",
    description="API profesional para gestión de buses de transporte regional",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de la API
app.include_router(
    buses_router, 
    prefix="/api/v1/buses", 
    tags=["Gestión de Buses"]
)

# Endpoints básicos de la aplicación
@app.get("/", summary="Información de la API")
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

@app.get("/health", summary="Estado de salud del sistema")
def health_check():
    """Verificar estado de salud de la API y base de datos"""
    try:
        # Verificar conexión a base de datos
        conn = psycopg2.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            database="flota_buses", 
            user="grupo_trabajo",
            password="grupo1234"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "api": "operational",
            "database": "connected",
            "message": "Todos los servicios funcionando correctamente"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "api": "operational", 
            "database": "error",
            "message": f"Problema de conexión a base de datos: {str(e)}"
        }

@app.get("/info", summary="Información del sistema")
def system_info():
    """Información detallada sobre el sistema y sus capacidades"""
    return {
        "sistema": "Sistema de Gestión de Flota de Buses",
        "version": "1.0.0",
        "arquitectura": "Clean Architecture con FastAPI",
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

# Endpoint de testing de base de datos (solo para desarrollo)
@app.get("/dev/db-test", summary="Test de conexión DB", tags=["Desarrollo"])
def test_database():
    """
    Endpoint de testing para verificar conexión a PostgreSQL
    Solo para desarrollo - remover en producción
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            database="flota_buses", 
            user="grupo_trabajo",
            password="grupo1234"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        # Verificar tablas principales
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "Conexión exitosa",
            "postgres_version": version,
            "database": "flota_buses",
            "host": DB_HOST,
            "port": DB_PORT,
            "tablas_disponibles": tables
        }
    except Exception as e:
        return {
            "status": "Error de conexión", 
            "error": str(e),
            "host": DB_HOST,
            "port": DB_PORT
        }

# Manejo de eventos de la aplicación
@app.on_event("startup")
async def startup_event():
    """Eventos ejecutados al iniciar la aplicación"""
    print("🚀 Sistema de Gestión de Flota iniciado")
    print(f"📊 Documentación disponible en: /docs")
    print(f"🗄️  Base de datos: {DB_HOST}:{DB_PORT}")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos ejecutados al cerrar la aplicación"""
    print("🛑 Sistema de Gestión de Flota detenido")


