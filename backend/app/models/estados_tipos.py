"""
Modelos de apoyo para el sistema de buses
Tablas normalizadas según el diagrama de base de datos
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text,Numeric
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import relationship

class EstadoBus(Base):
    """
    Tabla normalizada de estados de buses
    Reemplaza el enum EstadoBus por tabla de referencia
    """
    __tablename__ = "estados_buses"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True, 
                   comment="Código del estado: ACT, MAN, FS, RET")
    nombre = Column(String(50), nullable=False, 
                   comment="Nombre del estado: Activo, Mantenimiento, etc.")
    descripcion = Column(Text, comment="Descripción detallada del estado")
    permite_asignacion = Column(Boolean, default=False, 
                               comment="Si el bus puede ser asignado en este estado")
    es_activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<EstadoBus(codigo='{self.codigo}', nombre='{self.nombre}')>"
    buses = relationship("Bus", back_populates="estado")


class TipoCombustible(Base):
    """
    Tabla normalizada de tipos de combustible
    Reemplaza el enum TipoCombustible por tabla de referencia
    """
    __tablename__ = "tipos_combustible"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), unique=True, nullable=False, index=True,
                   comment="Código del combustible: DSL, GAS, ELE, HIB")
    nombre = Column(String(50), nullable=False,
                   comment="Nombre del combustible: Diesel, Gasolina, etc.")
    factor_emision = Column(Numeric(8, 4), comment="Factor de emisión para cálculos ambientales")
    es_activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<TipoCombustible(codigo='{self.codigo}', nombre='{self.nombre}')>"
    buses = relationship("Bus", back_populates="tipo_combustible")


# Datos iniciales para poblar las tablas
ESTADOS_INICIALES = [
    {"codigo": "ACT", "nombre": "Activo", "descripcion": "Bus operativo y disponible", "permite_asignacion": True},
    {"codigo": "MAN", "nombre": "Mantenimiento", "descripcion": "Bus en mantenimiento programado", "permite_asignacion": False},
    {"codigo": "FS", "nombre": "Fuera de Servicio", "descripcion": "Bus temporalmente fuera de servicio", "permite_asignacion": False},
    {"codigo": "RET", "nombre": "Retirado", "descripcion": "Bus retirado de la flota", "permite_asignacion": False},
]

TIPOS_COMBUSTIBLE_INICIALES = [
    {"codigo": "DSL", "nombre": "Diesel", "factor_emision": 2.6391},
    {"codigo": "GAS", "nombre": "Gasolina", "factor_emision": 2.3240},
    {"codigo": "ELE", "nombre": "Eléctrico", "factor_emision": 0.0000},
    {"codigo": "HIB", "nombre": "Híbrido", "factor_emision": 1.8000},
    {"codigo": "GNV", "nombre": "Gas Natural", "factor_emision": 2.0000},
]