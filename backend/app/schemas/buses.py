"""
Schemas de Pydantic para el modelo de Buses
Define la validación de datos de entrada y salida de la API
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from ..models.buses import EstadoBus, TipoCombustible

# Schema base con campos comunes
class BusBase(BaseModel):
    """Schema base con campos comunes para buses"""
    patente: str = Field(..., min_length=6, max_length=10, description="Patente del vehículo")
    codigo_interno: Optional[str] = Field(None, max_length=50, description="Código interno de la empresa")
    marca: str = Field(..., min_length=2, max_length=100, description="Marca del vehículo")
    modelo: str = Field(..., min_length=2, max_length=100, description="Modelo del vehículo")
    año: int = Field(..., ge=1980, le=2030, description="Año de fabricación")
    numero_chasis: Optional[str] = Field(None, max_length=100, description="Número de chasis")
    numero_motor: Optional[str] = Field(None, max_length=100, description="Número del motor")
    tipo_combustible: TipoCombustible = Field(default=TipoCombustible.DIESEL, description="Tipo de combustible")
    capacidad_sentados: int = Field(..., gt=0, le=100, description="Capacidad de pasajeros sentados")
    capacidad_parados: Optional[int] = Field(default=0, ge=0, le=200, description="Capacidad de pasajeros de pie")
    kilometraje_actual: Optional[int] = Field(default=0, ge=0, description="Kilometraje actual del vehículo")
    fecha_compra: Optional[datetime] = Field(None, description="Fecha de compra del vehículo")
    precio_compra: Optional[Decimal] = Field(None, ge=0, description="Precio de compra")
    estado: EstadoBus = Field(default=EstadoBus.ACTIVO, description="Estado del bus")
    observaciones: Optional[str] = Field(None, max_length=1000, description="Observaciones adicionales")

    @validator('patente')
    def validar_patente(cls, v):
        """Validar formato de patente chilena"""
        v = v.upper().replace('-', '').replace(' ', '')
        if len(v) < 6 or len(v) > 8:
            raise ValueError('Patente debe tener entre 6 y 8 caracteres')
        return v

    @validator('año')
    def validar_año(cls, v):
        """Validar que el año sea razonable"""
        año_actual = datetime.now().year
        if v > año_actual + 1:
            raise ValueError(f'El año no puede ser mayor a {año_actual + 1}')
        return v


# Schema para crear un nuevo bus
class BusCrear(BusBase):
    """Schema para crear un nuevo bus"""
    pass

# Schema para actualizar un bus existente
class BusActualizar(BaseModel):
    """Schema para actualizar un bus existente - todos los campos opcionales"""
    patente: Optional[str] = Field(None, min_length=6, max_length=10)
    codigo_interno: Optional[str] = Field(None, max_length=50)
    marca: Optional[str] = Field(None, min_length=2, max_length=100)
    modelo: Optional[str] = Field(None, min_length=2, max_length=100)
    año: Optional[int] = Field(None, ge=1980, le=2030)
    numero_chasis: Optional[str] = Field(None, max_length=100)
    numero_motor: Optional[str] = Field(None, max_length=100)
    tipo_combustible: Optional[TipoCombustible] = None
    capacidad_sentados: Optional[int] = Field(None, gt=0, le=100)
    kilometraje_actual: Optional[int] = Field(None, ge=0)
    fecha_compra: Optional[datetime] = None
    precio_compra: Optional[Decimal] = Field(None, ge=0)
    estado: Optional[EstadoBus] = None
    observaciones: Optional[str] = Field(None, max_length=1000)

    @validator('patente')
    def validar_patente(cls, v):
        if v is not None:
            v = v.upper().replace('-', '').replace(' ', '')
            if len(v) < 6 or len(v) > 8:
                raise ValueError('Patente debe tener entre 6 y 8 caracteres')
        return v

# Schema para respuesta de la API (incluye campos calculados y de sistema)
class Bus(BusBase):
    """Schema completo del bus para respuestas de la API"""
    id: int = Field(..., description="ID único del bus")
    capacidad_total: int = Field(..., description="Capacidad total de pasajeros")
    esta_activo: bool = Field(default=True, description="Indica si el registro está activo")
    fecha_creacion: datetime = Field(..., description="Fecha de creación del registro")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        orm_mode = True  # Permite crear el schema desde objetos SQLAlchemy
        
        # Ejemplo de respuesta para documentación automática
        schema_extra = {
            "example": {
                "id": 1,
                "patente": "ABCD12",
                "codigo_interno": "BUS-001",
                "marca": "Mercedes Benz",
                "modelo": "OH-1628",
                "año": 2020,
                "numero_chasis": "9BM979018LB123456",
                "numero_motor": "OM926LA123456",
                "tipo_combustible": "diesel",
                "capacidad_sentados": 45,
                "capacidad_total": 65,
                "kilometraje_actual": 85000,
                "fecha_compra": "2020-01-15T00:00:00",
                "precio_compra": 45000000,
                "estado": "activo",
                "observaciones": "Bus en excelente estado",
                "esta_activo": True,
                "fecha_creacion": "2025-09-02T20:00:00",
                "fecha_actualizacion": "2025-09-02T20:00:00"
            }
        }

# Schema para lista de buses (versión simplificada)
class BusResumen(BaseModel):
    """Schema simplificado para listas de buses"""
    id: int
    patente: str
    marca: str
    modelo: str
    año: int
    estado: EstadoBus
    capacidad_sentados: int
    kilometraje_actual: Optional[int]

    class Config:
        orm_mode = True

# Schema para respuesta de creación exitosa
class BusRespuestaCreacion(BaseModel):
    """Schema para confirmar creación exitosa de bus"""
    mensaje: str = "Bus creado exitosamente"
    bus: Bus

# Schema para respuesta de actualización exitosa
class BusRespuestaActualizacion(BaseModel):
    """Schema para confirmar actualización exitosa de bus"""
    mensaje: str = "Bus actualizado exitosamente"
    bus: Bus

# Schema para filtros de búsqueda
class FiltrosBuses(BaseModel):
    """Schema para filtros de búsqueda de buses"""
    marca: Optional[str] = None
    estado: Optional[EstadoBus] = None
    año_desde: Optional[int] = Field(None, ge=1980)
    año_hasta: Optional[int] = Field(None, le=2030)
    capacidad_minima: Optional[int] = Field(None, gt=0)
    buscar_texto: Optional[str] = Field(None, max_length=100, description="Buscar en patente, marca o modelo")