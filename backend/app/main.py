import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI

app = FastAPI(
    title="Sistema de Gestión de Flota",
    description="API para gestión de buses de transporte regional",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Fleet Management System API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API funcionando correctamente"}

# Endpoint de prueba para buses (sin base de datos por ahora)
@app.get("/api/v1/buses/test")
def test_buses():
    return {
        "message": "Endpoints de buses funcionando", 
        "total_buses": 0,
        "status": "API operativa sin base de datos"
    }