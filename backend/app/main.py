"""
Sistema de Gestión de Flota de Buses
Aplicación principal FastAPI - Arquitectura limpia
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar routers
from app.api.v1.endpoints.buses import router as buses_router
from app.api.v1.endpoints.system import router as system_router

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

# Incluir router del sistema (endpoints básicos)
app.include_router(
    system_router,
    tags=["Sistema"]
)

# Manejo de eventos de la aplicación
@app.on_event("startup")
async def startup_event():
    """Eventos ejecutados al iniciar la aplicación"""
    print("🚀 Sistema de Gestión de Flota iniciado")
    print(f"📊 Documentación disponible en: /docs")
    print(f"🗄️  Base de datos: {DB_HOST}:{DB_PORT}")
    print("🏗️  Arquitectura: Clean Architecture + SQLAlchemy")
    print("📂 Routers: Buses, Sistema")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos ejecutados al cerrar la aplicación"""
    print("🛑 Sistema de Gestión de Flota detenido")


