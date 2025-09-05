import sys
import os
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

@app.get("/api/v1/buses/test")
def test_buses():
    return {
        "message": "Endpoints de buses funcionando", 
        "total_buses": 0,
        "status": "API operativa con PostgreSQL"
    }
@app.get("/db-test")
def test_database():
    try:
        from sqlalchemy import create_engine, text
        # URL específica con parámetros de conexión
        database_url = "postgresql://grupo_trabajo:grupo1234@localhost:5432/flota_buses?client_encoding=utf8"
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            return {
                "status": "Conexión exitosa", 
                "postgres_version": version,
                "database": "flota_buses"
            }
    except Exception as e:
        return {"status": "Error de conexión", "error": str(e)}