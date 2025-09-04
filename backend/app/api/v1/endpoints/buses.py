"""
Endpoints de la API para gestión de buses
Sistema de Gestión de Flota de Buses
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import obtener_bd
from app.schemas.buses import (
    Bus, BusCrear, BusActualizar, BusResumen, 
    BusRespuestaCreacion, BusRespuestaActualizacion
)
from app.crud.buses import crud_bus

# Router para agrupar endpoints de buses
router = APIRouter()

@router.post("/", response_model=BusRespuestaCreacion, status_code=status.HTTP_201_CREATED)
def crear_bus(
    bus_data: BusCrear,
    db: Session = Depends(obtener_bd)
):
    """
    Crear un nuevo bus en la flota
    
    - **patente**: Patente del vehículo (formato chileno)
    - **marca**: Marca del vehículo
    - **modelo**: Modelo del vehículo
    - **año**: Año de fabricación
    - **capacidad_sentados**: Número de asientos (máximo 45)
    """
    # Verificar que la patente no esté en uso
    bus_existente = crud_bus.obtener_bus_por_patente(db, bus_data.patente)
    if bus_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un bus con la patente {bus_data.patente}"
        )
    
    # Crear el bus
    try:
        nuevo_bus = crud_bus.crear_bus(db, bus_data)
        return BusRespuestaCreacion(
            mensaje="Bus creado exitosamente",
            bus=nuevo_bus
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el bus: {str(e)}"
        )

@router.get("/", response_model=List[BusResumen])
def listar_buses(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de registros a retornar"),
    estado: Optional[str] = Query(None, description="Filtrar por estado del bus"),
    marca: Optional[str] = Query(None, description="Filtrar por marca"),
    buscar: Optional[str] = Query(None, description="Buscar en patente, marca o modelo"),
    db: Session = Depends(obtener_bd)
):
    """
    Obtener lista de buses con filtros opcionales
    
    - **skip**: Número de registros a omitir (para paginación)
    - **limit**: Número máximo de registros (máximo 100)
    - **estado**: Filtrar por estado (activo, mantenimiento, fuera_de_servicio, retirado)
    - **marca**: Filtrar por marca del vehículo
    - **buscar**: Término de búsqueda libre
    """
    if buscar:
        buses = crud_bus.buscar_buses(db, buscar)
    elif estado:
        buses = crud_bus.obtener_buses_por_estado(db, estado)
    elif marca:
        buses = crud_bus.obtener_buses_por_marca(db, marca)
    else:
        buses = crud_bus.obtener_buses(db, skip=skip, limit=limit)
    
    return buses

@router.get("/{bus_id}", response_model=Bus)
def obtener_bus(
    bus_id: int,
    db: Session = Depends(obtener_bd)
):
    """
    Obtener información detallada de un bus específico
    """
    bus = crud_bus.obtener_bus_por_id(db, bus_id)
    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus con ID {bus_id} no encontrado"
        )
    return bus

@router.get("/patente/{patente}", response_model=Bus)
def obtener_bus_por_patente(
    patente: str,
    db: Session = Depends(obtener_bd)
):
    """
    Obtener información de un bus por su patente
    """
    bus = crud_bus.obtener_bus_por_patente(db, patente)
    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus con patente {patente} no encontrado"
        )
    return bus

@router.put("/{bus_id}", response_model=BusRespuestaActualizacion)
def actualizar_bus(
    bus_id: int,
    bus_data: BusActualizar,
    db: Session = Depends(obtener_bd)
):
    """
    Actualizar información de un bus existente
    """
    # Verificar que el bus existe
    bus_existente = crud_bus.obtener_bus_por_id(db, bus_id)
    if not bus_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus con ID {bus_id} no encontrado"
        )
    
    # Si se actualiza la patente, verificar que no esté en uso por otro bus
    if bus_data.patente and bus_data.patente != bus_existente.patente:
        otro_bus = crud_bus.obtener_bus_por_patente(db, bus_data.patente)
        if otro_bus and otro_bus.id != bus_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La patente {bus_data.patente} ya está en uso por otro bus"
            )
    
    # Actualizar el bus
    try:
        bus_actualizado = crud_bus.actualizar_bus(db, bus_id, bus_data)
        return BusRespuestaActualizacion(
            mensaje="Bus actualizado exitosamente",
            bus=bus_actualizado
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el bus: {str(e)}"
        )

@router.patch("/{bus_id}/kilometraje")
def actualizar_kilometraje(
    bus_id: int,
    nuevo_kilometraje: int = Query(..., ge=0, description="Nuevo kilometraje del vehículo"),
    db: Session = Depends(obtener_bd)
):
    """
    Actualizar el kilometraje de un bus
    """
    bus = crud_bus.actualizar_kilometraje(db, bus_id, nuevo_kilometraje)
    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus con ID {bus_id} no encontrado"
        )
    
    return {
        "mensaje": "Kilometraje actualizado exitosamente",
        "bus_id": bus_id,
        "kilometraje_anterior": bus.kilometraje_actual - nuevo_kilometraje if bus.kilometraje_actual else 0,
        "kilometraje_nuevo": nuevo_kilometraje
    }

@router.patch("/{bus_id}/estado")
def cambiar_estado_bus(
    bus_id: int,
    nuevo_estado: str = Query(..., description="Nuevo estado del bus"),
    db: Session = Depends(obtener_bd)
):
    """
    Cambiar el estado operacional de un bus
    
    Estados válidos: activo, mantenimiento, fuera_de_servicio, retirado
    """
    estados_validos = ["activo", "mantenimiento", "fuera_de_servicio", "retirado"]
    if nuevo_estado not in estados_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Estados válidos: {', '.join(estados_validos)}"
        )
    
    bus = crud_bus.cambiar_estado_bus(db, bus_id, nuevo_estado)
    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus con ID {bus_id} no encontrado"
        )
    
    return {
        "mensaje": "Estado del bus actualizado exitosamente",
        "bus_id": bus_id,
        "estado_nuevo": nuevo_estado
    }

@router.delete("/{bus_id}")
def eliminar_bus(
    bus_id: int,
    db: Session = Depends(obtener_bd)
):
    """
    Eliminar un bus (soft delete - el bus se marca como inactivo)
    """
    resultado = crud_bus.eliminar_bus(db, bus_id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus con ID {bus_id} no encontrado"
        )
    
    return {
        "mensaje": "Bus eliminado exitosamente",
        "bus_id": bus_id
    }

@router.get("/reportes/estadisticas")
def obtener_estadisticas_flota(db: Session = Depends(obtener_bd)):
    """
    Obtener estadísticas generales de la flota
    """
    estadisticas = crud_bus.obtener_estadisticas_flota(db)
    return {
        "mensaje": "Estadísticas de la flota",
        "data": estadisticas
    }

@router.get("/reportes/mantenimiento-pendiente", response_model=List[BusResumen])
def obtener_buses_mantenimiento_pendiente(
    kilometraje_limite: int = Query(10000, ge=1000, description="Límite de kilometraje para mantenimiento"),
    db: Session = Depends(obtener_bd)
):
    """
    Obtener buses que necesitan mantenimiento según kilometraje
    """
    buses = crud_bus.obtener_buses_mantenimiento_pendiente(db, kilometraje_limite)
    return buses

@router.get("/buscar/avanzada", response_model=List[BusResumen])
def busqueda_avanzada(
    marca: Optional[str] = Query(None, description="Filtrar por marca"),
    año_desde: Optional[int] = Query(None, ge=1980, description="Año mínimo"),
    año_hasta: Optional[int] = Query(None, le=2030, description="Año máximo"),
    capacidad_minima: Optional[int] = Query(None, ge=1, le=45, description="Capacidad mínima de asientos"),
    estado: Optional[str] = Query(None, description="Estado del bus"),
    db: Session = Depends(obtener_bd)
):
    """
    Búsqueda avanzada de buses con múltiples filtros
    """
    # Esta funcionalidad requeriría una función más compleja en CRUD
    # Por ahora retornamos buses básicos según los filtros disponibles
    if marca:
        return crud_bus.obtener_buses_por_marca(db, marca)
    elif estado:
        return crud_bus.obtener_buses_por_estado(db, estado)
    else:
        return crud_bus.obtener_buses(db)