"""
Modelo de Buses para el Sistema de Gestión de Flota
Define la estructura de datos para los vehículos de transporte
Actualizado según normativas chilenas de transporte público
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
import enum
from app.core.database import Base

# Enumeraciones para estados y tipos
class EstadoBus(str, enum.Enum):
    ACTIVO = "activo"
    MANTENIMIENTO = "mantenimiento"
    FUERA_DE_SERVICIO = "fuera_de_servicio"
    RETIRADO = "retirado"

class TipoCombustible(str, enum.Enum):
    DIESEL = "diesel"
    GASOLINA = "gasolina"
    GAS = "gas"
    ELECTRICO = "electrico"
    HIBRIDO = "hibrido"

class Bus(Base):
    """
    Modelo para representar los buses de la flota
    Contiene toda la información técnica y administrativa de cada vehículo
    Actualizado según normativas chilenas de transporte
    """
    __tablename__ = "buses"

    # Identificación primaria
    id = Column(Integer, primary_key=True, index=True, comment="ID único del bus")
    patente = Column(String(8), unique=True, nullable=False, index=True, 
                    comment="Patente del vehículo formato chileno (6-8 caracteres)")
    codigo_interno = Column(String(50), unique=True, index=True,
                           comment="Código interno de la empresa")

    # Información del vehículo
    marca = Column(String(100), nullable=False, comment="Marca del vehículo")
    modelo = Column(String(100), nullable=False, comment="Modelo del vehículo")
    año = Column(Integer, nullable=False, comment="Año de fabricación")
    numero_chasis = Column(String(17), unique=True, comment="Número de chasis VIN (17 caracteres)")
    numero_motor = Column(String(100), comment="Número del motor")

    # Especificaciones técnicas
    tipo_combustible = Column(Enum(TipoCombustible), nullable=False, default=TipoCombustible.DIESEL,
                             comment="Tipo de combustible que usa")
    capacidad_sentados = Column(Integer, nullable=False, comment="Número de asientos (máximo 45 según normativa)")
    kilometraje_actual = Column(Integer, default=0, comment="Kilometraje actual del vehículo")

    # Información comercial
    fecha_compra = Column(DateTime, comment="Fecha de compra del vehículo")
    precio_compra = Column(Integer, comment="Precio de compra (en pesos chilenos)")
    
    # Estado y operación
    estado = Column(Enum(EstadoBus), default=EstadoBus.ACTIVO, nullable=False,
                   comment="Estado operacional del bus")
    
    # Observaciones y notas
    observaciones = Column(Text, comment="Observaciones adicionales sobre el vehículo")
    
    # Control de actividad
    esta_activo = Column(Boolean, default=True, nullable=False,
                        comment="Indica si el registro está activo")

    # Timestamps automáticos
    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False,
                           comment="Fecha de creación del registro")
    fecha_actualizacion = Column(DateTime, server_default=func.now(), 
                                onupdate=func.now(), nullable=False,
                                comment="Fecha de última actualización")

    # Método para representación en string
    def __repr__(self):
        return f"<Bus(patente='{self.patente}', marca='{self.marca}', modelo='{self.modelo}')>"

    # Método para verificar si necesita mantenimiento
    def necesita_mantenimiento(self, kilometraje_limite=10000):
        """
        Verifica si el bus necesita mantenimiento basado en kilometraje
        Por defecto revisa cada 10,000 km
        """
        if self.kilometraje_actual and kilometraje_limite:
            return self.kilometraje_actual % kilometraje_limite < 1000
        return False

    # Método para verificar capacidad válida según normativa
    def capacidad_valida(self):
        """Verifica que la capacidad esté dentro de los límites legales chilenos"""
        return 1 <= self.capacidad_sentados <= 45

    # Método para obtener información resumida
    def info_basica(self):
        """Retorna información básica del bus como diccionario"""
        return {
            "patente": self.patente,
            "marca": self.marca,
            "modelo": self.modelo,
            "año": self.año,
            "estado": self.estado.value,
            "capacidad_sentados": self.capacidad_sentados
        }

   # Método para validar formato de patente chilena
    def validar_patente_chilena(self):
        """Valida que la patente cumpla con formatos chilenos"""
        if not self.patente:
            return False
            
        patente_limpia = self.patente.upper().replace('-', '').replace(' ', '')
        
        # Patente nueva (6 caracteres): 4 letras + 2 números
        if len(patente_limpia) == 6:
            return patente_limpia[:4].isalpha() and patente_limpia[4:].isdigit()
        
        # Patentes antiguas (7-8 caracteres) se consideran válidas
        return 6 <= len(patente_limpia) <= 8