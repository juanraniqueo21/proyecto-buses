"""
Configuración de base de datos y gestión de sesiones
Sistema de Gestión de Flota de Buses
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# URL de la base de datos desde variable de entorno o por defecto para desarrollo
URL_BASE_DATOS = os.getenv(
    "DATABASE_URL", 
    "postgresql://grupo_trabajo:grupo1234@localhost:5433/flota_buses"
)


motor_bd = create_engine(
    URL_BASE_DATOS,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300
)

# Crear motor de SQLAlchemy
motor_bd = create_engine(
    URL_BASE_DATOS,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"options": "-c timezone=utc -c client_encoding=utf8"}
)

# Crear clase SessionLocal
SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor_bd)

# Crear clase Base para los modelos
Base = declarative_base()

# Dependencia para obtener sesión de base de datos
def obtener_bd():
    """
    Dependencia de sesión de base de datos para FastAPI
    Asegura el manejo adecuado del ciclo de vida de la sesión
    """
    bd = SesionLocal()
    try:
        yield bd
    finally:
        bd.close()

# Función de inicialización de base de datos
def inicializar_bd():
    """
    Inicializar tablas de la base de datos
    Se llama al inicio de la aplicación
    """
    # Importar todos los modelos aquí para asegurar que están registrados con SQLAlchemy
    # Esto será necesario cuando creemos los modelos
    Base.metadata.create_all(bind=motor_bd)

# Función de verificación de estado de la base de datos
def verificar_conexion_bd():
    """
    Verificar si la conexión a la base de datos funciona
    Retorna True si la conexión es exitosa, False en caso contrario
    """
    try:
        bd = SesionLocal()
        from sqlalchemy import text
        bd.execute(text("SELECT 1"))
        bd.close()
        return True
    except Exception as e:
        print(f"Conexión a base de datos falló: {e}")
        return False
    
def inicializar_bd():
    """Inicializar tablas de la base de datos"""
    from models.buses import Bus  # Sin 'app.'
    from models.estados_tipos import EstadoBus, TipoCombustible  # Sin 'app.'
    Base.metadata.create_all(bind=motor_bd)