"""
Router para endpoints de buses - Migrado a CRUD SQLAlchemy
Sistema de Gestión de Flota de Buses
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Imports del proyecto
from app.core.dependencies import get_db
from app.crud.buses import crud_bus
from app.models.estados_tipos import EstadoBus, TipoCombustible

# Schemas para el router (mantenemos los existentes)
class BusBase(BaseModel):
    patente: str
    marca: str
    modelo: str
    año: int
    capacidad_sentados: int
    estado_id: int
    tipo_combustible_id: int

class BusCrear(BusBase):
    codigo_interno: Optional[str] = None
    numero_chasis: Optional[str] = None
    numero_motor: Optional[str] = None
    kilometraje_actual: Optional[int] = 0
    fecha_compra: Optional[datetime] = None
    precio_compra: Optional[float] = None
    observaciones: Optional[str] = None

class BusActualizar(BaseModel):
    patente: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    año: Optional[int] = None
    capacidad_sentados: Optional[int] = None
    estado_id: Optional[int] = None
    tipo_combustible_id: Optional[int] = None
    codigo_interno: Optional[str] = None
    numero_chasis: Optional[str] = None
    numero_motor: Optional[str] = None
    kilometraje_actual: Optional[int] = None
    fecha_compra: Optional[datetime] = None
    precio_compra: Optional[float] = None
    observaciones: Optional[str] = None

# Crear router
router = APIRouter()

# Función helper para formatear fecha
def format_date(date_obj):
    """Formatear fecha para respuesta legible"""
    return date_obj.strftime("%d/%m/%Y") if date_obj else None

def bus_to_dict(bus):
    """Convertir modelo Bus a diccionario para respuesta"""
    return {
        "id": bus.id,
        "patente": bus.patente,
        "marca": bus.marca,
        "modelo": bus.modelo,
        "año": bus.año,
        "estado": bus.estado.nombre if bus.estado else None,
        "combustible": bus.tipo_combustible.nombre if bus.tipo_combustible else None,
        "capacidad": bus.capacidad_sentados,
        "kilometraje": bus.kilometraje_actual,
        "precio": float(bus.precio_compra) if bus.precio_compra else None,
        "observaciones": bus.observaciones,
        "codigo_interno": bus.codigo_interno,
        "numero_chasis": bus.numero_chasis,
        "numero_motor": bus.numero_motor,
        "fecha_compra": format_date(bus.fecha_compra)
    }

@router.get("/", summary="Listar todos los buses")
def listar_buses(db: Session = Depends(get_db)):
    """Obtener lista de todos los buses activos usando CRUD SQLAlchemy"""
    try:
        buses = crud_bus.obtener_buses(db)
        
        buses_data = [
            {
                "id": bus.id, 
                "patente": bus.patente, 
                "marca": bus.marca, 
                "modelo": bus.modelo, 
                "año": bus.año, 
                "estado": bus.estado.nombre if bus.estado else "Sin estado",
                "combustible": bus.tipo_combustible.nombre if bus.tipo_combustible else "Sin tipo",
                "capacidad": bus.capacidad_sentados
            }
            for bus in buses
        ]
        
        return {"message": "Lista de buses", "total": len(buses_data), "buses": buses_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener buses: {str(e)}")

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Crear nuevo bus")
def crear_bus(bus_data: BusCrear, db: Session = Depends(get_db)):
    """Crear un nuevo bus usando CRUD SQLAlchemy"""
    try:
        # Validaciones de entrada (mantenemos las originales)
        patente = bus_data.patente.upper().replace('-', '').replace(' ', '')
        if len(patente) < 6 or len(patente) > 8:
            raise HTTPException(status_code=400, detail="Patente debe tener entre 6 y 8 caracteres")
        
        año_actual = datetime.now().year
        if bus_data.año < 1980 or bus_data.año > año_actual + 1:
            raise HTTPException(status_code=400, detail=f"Año debe estar entre 1980 y {año_actual + 1}")
        
        if bus_data.capacidad_sentados < 1 or bus_data.capacidad_sentados > 45:
            raise HTTPException(status_code=400, detail="Capacidad debe estar entre 1 y 45 asientos")
        
        # Verificar patente única usando CRUD
        bus_existente = crud_bus.obtener_bus_por_patente(db, patente)
        if bus_existente:
            raise HTTPException(status_code=400, detail=f"Ya existe un bus con patente {patente}")
        
        # Crear bus usando CRUD
        nuevo_bus = crud_bus.crear_bus(db, bus_data)
        
        return {
            "message": "Bus creado exitosamente",
            "bus": bus_to_dict(nuevo_bus)
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/eliminados", summary="Listar buses eliminados")
def listar_buses_eliminados(db: Session = Depends(get_db)):
    """Obtener lista de buses eliminados lógicamente"""
    try:
        # Como no hay método específico en CRUD, usamos consulta directa
        from app.models.buses import Bus
        buses = db.query(Bus).filter(Bus.esta_activo == False).all()
        
        buses_eliminados = [
            {
                "id": bus.id,
                "patente": bus.patente, 
                "marca": bus.marca, 
                "modelo": bus.modelo, 
                "año": bus.año,
                "estado": bus.estado.nombre if bus.estado else None,
                "combustible": bus.tipo_combustible.nombre if bus.tipo_combustible else None,
                "fecha_eliminacion": format_date(bus.fecha_actualizacion) if bus.fecha_actualizacion else None
            } 
            for bus in buses
        ]
        
        return {
            "message": "Buses eliminados",
            "total": len(buses_eliminados),
            "buses": buses_eliminados
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/{bus_id}", summary="Obtener bus por ID")
def obtener_bus(bus_id: int, db: Session = Depends(get_db)):
    """Obtener información detallada de un bus específico usando CRUD"""
    try:
        bus = crud_bus.obtener_bus_por_id(db, bus_id)
        
        if not bus:
            raise HTTPException(status_code=404, detail="Bus no encontrado")
            
        return {"bus": bus_to_dict(bus)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.put("/{bus_id}", summary="Actualizar bus")
def actualizar_bus(bus_id: int, bus_data: BusActualizar, db: Session = Depends(get_db)):
    """Actualizar información de un bus existente usando CRUD"""
    try:
        # Verificar que el bus existe
        bus_existente = crud_bus.obtener_bus_por_id(db, bus_id)
        if not bus_existente:
            raise HTTPException(status_code=404, detail="Bus no encontrado")
        
        # Validar patente si se actualiza
        if bus_data.patente:
            patente_limpia = bus_data.patente.upper().replace('-', '').replace(' ', '')
            if len(patente_limpia) < 6 or len(patente_limpia) > 8:
                raise HTTPException(status_code=400, detail="Patente debe tener entre 6 y 8 caracteres")
            
            # Verificar patente única
            otro_bus = crud_bus.obtener_bus_por_patente(db, patente_limpia)
            if otro_bus and otro_bus.id != bus_id:
                raise HTTPException(status_code=400, detail="La patente ya está en uso por otro bus")
        
        # Actualizar usando CRUD
        bus_actualizado = crud_bus.actualizar_bus(db, bus_id, bus_data)
        if not bus_actualizado:
            raise HTTPException(status_code=404, detail="Error al actualizar el bus")
        
        return {
            "message": "Bus actualizado exitosamente",
            "bus": bus_to_dict(bus_actualizado)
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.delete("/{bus_id}", summary="Eliminar bus")
def eliminar_bus(bus_id: int, db: Session = Depends(get_db)):
    """Eliminar un bus usando CRUD SQLAlchemy (soft delete)"""
    try:
        # Obtener información del bus antes de eliminar
        bus = crud_bus.obtener_bus_por_id(db, bus_id)
        if not bus:
            raise HTTPException(status_code=404, detail="Bus no encontrado")
        
        # Eliminar usando CRUD
        resultado = crud_bus.eliminar_bus(db, bus_id)
        if not resultado:
            raise HTTPException(status_code=404, detail="Error al eliminar el bus")
        
        return {
            "message": "Bus eliminado exitosamente",
            "bus_eliminado": {
                "id": bus.id,
                "patente": bus.patente,
                "marca": bus.marca,
                "modelo": bus.modelo
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.patch("/{bus_id}/restaurar", summary="Restaurar bus eliminado")
def restaurar_bus(bus_id: int, db: Session = Depends(get_db)):
    """Restaurar un bus eliminado lógicamente"""
    try:
        # Como no hay método específico en CRUD, usamos consulta directa
        from app.models.buses import Bus
        bus = db.query(Bus).filter(Bus.id == bus_id, Bus.esta_activo == False).first()
        
        if not bus:
            raise HTTPException(status_code=404, detail="Bus no encontrado o no está eliminado")
        
        # Restaurar el bus
        bus.esta_activo = True
        db.commit()
        db.refresh(bus)
        
        return {
            "message": "Bus restaurado exitosamente",
            "bus_restaurado": {
                "id": bus.id,
                "patente": bus.patente,
                "marca": bus.marca,
                "modelo": bus.modelo
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# Endpoints auxiliares usando SQLAlchemy
@router.get("/auxiliares/estados", summary="Obtener estados disponibles")
def obtener_estados(db: Session = Depends(get_db)):
    """Obtener lista de estados de buses disponibles usando SQLAlchemy"""
    try:
        estados = db.query(EstadoBus).filter(EstadoBus.es_activo == True).all()
        
        return {
            "estados": [
                {"id": estado.id, "codigo": estado.codigo, "nombre": estado.nombre, "descripcion": estado.descripcion}
                for estado in estados
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/auxiliares/combustibles", summary="Obtener tipos de combustible")
def obtener_tipos_combustible(db: Session = Depends(get_db)):
    """Obtener lista de tipos de combustible disponibles usando SQLAlchemy"""
    try:
        tipos = db.query(TipoCombustible).filter(TipoCombustible.es_activo == True).all()
        
        return {
            "tipos_combustible": [
                {"id": tipo.id, "codigo": tipo.codigo, "nombre": tipo.nombre, 
                 "factor_emision": float(tipo.factor_emision) if tipo.factor_emision else None}
                for tipo in tipos
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/reportes/estadisticas", summary="Estadísticas de la flota")
def obtener_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas generales de la flota usando CRUD"""
    try:
        estadisticas = crud_bus.obtener_estadisticas_flota(db)
        
        # Agregar datos adicionales manualmente
        from app.models.buses import Bus
        total_eliminados = db.query(Bus).filter(Bus.esta_activo == False).count()
        
        estadisticas.update({
            "total_eliminados": total_eliminados,
            "fecha_consulta": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        
        return estadisticas
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")