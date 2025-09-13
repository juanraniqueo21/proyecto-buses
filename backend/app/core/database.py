"""
Configuración de base de datos y gestión de sesiones
Sistema de Gestión de Flota de Buses
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Obtener configuración de base de datos desde variables de entorno
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "flota_buses")
DB_USER = os.getenv("DB_USER", "grupo_trabajo")
DB_PASSWORD = os.getenv("DB_PASSWORD", "grupo1234")

# Construir URL de la base de datos
URL_BASE_DATOS = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"🗄️ Conectando a: postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")

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
    """Inicializar tablas de la base de datos"""
    try:
        from models.buses import Bus  # Sin 'app.'
        from models.estados_tipos import EstadoBus, TipoCombustible  # Sin 'app.'
        Base.metadata.create_all(bind=motor_bd)
        print("✅ Tablas de base de datos inicializadas correctamente")
    except Exception as e:
        print(f"❌ Error inicializando tablas: {e}")

# Función de verificación de estado de la base de datos
def verificar_conexion_bd():
    """
    Verificar si la conexión a la base de datos funciona
    Retorna True si la conexión es exitosa, False en caso contrario
    """
    try:
        bd = SesionLocal()
        bd.execute(text("SELECT 1"))
        bd.close()
        print("✅ Conexión a base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Conexión a base de datos falló: {e}")
        return False