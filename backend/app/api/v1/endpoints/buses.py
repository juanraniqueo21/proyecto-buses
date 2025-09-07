"""
Router para endpoints de buses - Arquitectura limpia
Sistema de Gestión de Flota de Buses
"""

import os
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import psycopg2

# Configuración de base de datos
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")

# Schemas para el router
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

# Función helper para conexión a BD
def get_db_connection():
    """Obtener conexión a PostgreSQL"""
    return psycopg2.connect(
        host=DB_HOST, 
        port=int(DB_PORT), 
        database="flota_buses", 
        user="grupo_trabajo",
        password="grupo1234"
    )

# Función helper para formatear fecha
def format_date(date_obj):
    """Formatear fecha para respuesta legible"""
    return date_obj.strftime("%d/%m/%Y") if date_obj else None

@router.get("/", summary="Listar todos los buses")
def listar_buses():
    """Obtener lista de todos los buses activos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT b.id, b.patente, b.marca, b.modelo, b.año, 
                   e.nombre as estado, t.nombre as combustible, b.capacidad_sentados
            FROM buses b 
            JOIN estados_buses e ON b.estado_id = e.id 
            JOIN tipos_combustible t ON b.tipo_combustible_id = t.id
            WHERE b.esta_activo = true
            ORDER BY b.id
        """)
        
        buses = cursor.fetchall()
        cursor.close()
        conn.close()
        
        buses_data = [
            {
                "id": row[0], "patente": row[1], "marca": row[2], "modelo": row[3], 
                "año": row[4], "estado": row[5], "combustible": row[6], "capacidad": row[7]
            } 
            for row in buses
        ]
        
        return {"message": "Lista de buses", "total": len(buses_data), "buses": buses_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener buses: {str(e)}")

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Crear nuevo bus")
def crear_bus(bus_data: BusCrear):
    """Crear un nuevo bus con validaciones completas"""
    try:
        # Validaciones de entrada
        patente = bus_data.patente.upper().replace('-', '').replace(' ', '')
        if len(patente) < 6 or len(patente) > 8:
            raise HTTPException(status_code=400, detail="Patente debe tener entre 6 y 8 caracteres")
        
        año_actual = datetime.now().year
        if bus_data.año < 1980 or bus_data.año > año_actual + 1:
            raise HTTPException(status_code=400, detail=f"Año debe estar entre 1980 y {año_actual + 1}")
        
        if bus_data.capacidad_sentados < 1 or bus_data.capacidad_sentados > 45:
            raise HTTPException(status_code=400, detail="Capacidad debe estar entre 1 y 45 asientos")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar patente única
        cursor.execute("SELECT id FROM buses WHERE patente = %s", (patente,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail=f"Ya existe un bus con patente {patente}")
        
        # Verificar foreign keys
        cursor.execute("SELECT id FROM estados_buses WHERE id = %s", (bus_data.estado_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail=f"Estado con ID {bus_data.estado_id} no existe")
        
        cursor.execute("SELECT id FROM tipos_combustible WHERE id = %s", (bus_data.tipo_combustible_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail=f"Tipo de combustible con ID {bus_data.tipo_combustible_id} no existe")
        
        # Insertar bus
        insert_query = """
        INSERT INTO buses (
            patente, codigo_interno, marca, modelo, año, numero_chasis, numero_motor,
            tipo_combustible_id, estado_id, capacidad_sentados, kilometraje_actual,
            fecha_compra, precio_compra, observaciones
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """
        
        cursor.execute(insert_query, (
            patente, bus_data.codigo_interno, bus_data.marca, bus_data.modelo,
            bus_data.año, bus_data.numero_chasis, bus_data.numero_motor,
            bus_data.tipo_combustible_id, bus_data.estado_id, bus_data.capacidad_sentados,
            bus_data.kilometraje_actual, bus_data.fecha_compra, bus_data.precio_compra,
            bus_data.observaciones
        ))
        
        bus_id = cursor.fetchone()[0]
        conn.commit()
        
        # Obtener bus creado con información completa
        cursor.execute("""
            SELECT b.id, b.patente, b.marca, b.modelo, b.año, 
                   e.nombre as estado, t.nombre as combustible, b.capacidad_sentados,
                   b.kilometraje_actual, b.precio_compra, b.observaciones, b.fecha_compra
            FROM buses b 
            JOIN estados_buses e ON b.estado_id = e.id 
            JOIN tipos_combustible t ON b.tipo_combustible_id = t.id
            WHERE b.id = %s
        """, (bus_id,))
        
        bus_creado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "message": "Bus creado exitosamente",
            "bus": {
                "id": bus_creado[0], "patente": bus_creado[1], "marca": bus_creado[2],
                "modelo": bus_creado[3], "año": bus_creado[4], "estado": bus_creado[5],
                "combustible": bus_creado[6], "capacidad": bus_creado[7],
                "kilometraje": bus_creado[8], 
                "precio": float(bus_creado[9]) if bus_creado[9] else None,
                "observaciones": bus_creado[10],
                "fecha_compra": format_date(bus_creado[11])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/eliminados", summary="Listar buses eliminados")
def listar_buses_eliminados():
    """Obtener lista de buses eliminados lógicamente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT b.id, b.patente, b.marca, b.modelo, b.año,
                   e.nombre as estado, t.nombre as combustible, 
                   b.fecha_actualizacion as fecha_eliminacion
            FROM buses b 
            LEFT JOIN estados_buses e ON b.estado_id = e.id 
            LEFT JOIN tipos_combustible t ON b.tipo_combustible_id = t.id
            WHERE b.esta_activo = false
            ORDER BY b.fecha_actualizacion DESC
        """)
        
        buses = cursor.fetchall()
        cursor.close()
        conn.close()
        
        buses_eliminados = [
            {
                "id": row[0], "patente": row[1], "marca": row[2], "modelo": row[3], 
                "año": row[4], "estado": row[5], "combustible": row[6],
                "fecha_eliminacion": format_date(row[7]) if row[7] else None
            } 
            for row in buses
        ]
        
        return {
            "message": "Buses eliminados",
            "total": len(buses_eliminados),
            "buses": buses_eliminados
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    

@router.get("/{bus_id}", summary="Obtener bus por ID")
def obtener_bus(bus_id: int):
    """Obtener información detallada de un bus específico"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT b.id, b.patente, b.marca, b.modelo, b.año, 
                   e.nombre as estado, t.nombre as combustible, b.capacidad_sentados,
                   b.kilometraje_actual, b.precio_compra, b.observaciones, b.codigo_interno,
                   b.numero_chasis, b.numero_motor, b.fecha_compra
            FROM buses b 
            JOIN estados_buses e ON b.estado_id = e.id 
            JOIN tipos_combustible t ON b.tipo_combustible_id = t.id
            WHERE b.id = %s AND b.esta_activo = true
        """, (bus_id,))
        
        bus = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not bus:
            raise HTTPException(status_code=404, detail="Bus no encontrado")
            
        return {
            "bus": {
                "id": bus[0], "patente": bus[1], "marca": bus[2], "modelo": bus[3],
                "año": bus[4], "estado": bus[5], "combustible": bus[6], "capacidad": bus[7],
                "kilometraje": bus[8], "precio": float(bus[9]) if bus[9] else None,
                "observaciones": bus[10], "codigo_interno": bus[11],
                "numero_chasis": bus[12], "numero_motor": bus[13], 
                "fecha_compra": format_date(bus[14])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.put("/{bus_id}", summary="Actualizar bus")
def actualizar_bus(bus_id: int, bus_data: BusActualizar):
    """Actualizar información de un bus existente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el bus existe
        cursor.execute("SELECT id FROM buses WHERE id = %s AND esta_activo = true", (bus_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Bus no encontrado")
        
        # Construir query dinámico
        campos_actualizar = []
        valores = []
        
        if bus_data.patente is not None:
            patente_limpia = bus_data.patente.upper().replace('-', '').replace(' ', '')
            if len(patente_limpia) < 6 or len(patente_limpia) > 8:
                cursor.close()
                conn.close()
                raise HTTPException(status_code=400, detail="Patente debe tener entre 6 y 8 caracteres")
            
            # Verificar patente única
            cursor.execute("SELECT id FROM buses WHERE patente = %s AND id != %s", (patente_limpia, bus_id))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                raise HTTPException(status_code=400, detail="La patente ya está en uso por otro bus")
            
            campos_actualizar.append("patente = %s")
            valores.append(patente_limpia)
        
        # Agregar otros campos de actualización dinámicamente
        for field, value in bus_data.dict(exclude_unset=True).items():
            if field != 'patente' and value is not None:
                campos_actualizar.append(f"{field} = %s")
                valores.append(value)
        
        if not campos_actualizar:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        
        # Ejecutar actualización
        campos_actualizar.append("fecha_actualizacion = NOW()")
        update_query = f"UPDATE buses SET {', '.join(campos_actualizar)} WHERE id = %s"
        valores.append(bus_id)
        
        cursor.execute(update_query, valores)
        conn.commit()
        
        # Obtener bus actualizado
        cursor.execute("""
            SELECT b.id, b.patente, b.marca, b.modelo, b.año, 
                   e.nombre as estado, t.nombre as combustible, b.capacidad_sentados,
                   b.kilometraje_actual, b.precio_compra, b.observaciones
            FROM buses b 
            JOIN estados_buses e ON b.estado_id = e.id 
            JOIN tipos_combustible t ON b.tipo_combustible_id = t.id
            WHERE b.id = %s
        """, (bus_id,))
        
        bus_actualizado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "message": "Bus actualizado exitosamente",
            "bus": {
                "id": bus_actualizado[0], "patente": bus_actualizado[1], "marca": bus_actualizado[2], 
                "modelo": bus_actualizado[3], "año": bus_actualizado[4], "estado": bus_actualizado[5], 
                "combustible": bus_actualizado[6], "capacidad": bus_actualizado[7],
                "kilometraje": bus_actualizado[8], 
                "precio": float(bus_actualizado[9]) if bus_actualizado[9] else None,
                "observaciones": bus_actualizado[10]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.delete("/{bus_id}", summary="Eliminar bus")
def eliminar_bus(bus_id: int):
    """Eliminar un bus (soft delete)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el bus existe
        cursor.execute("""
            SELECT b.id, b.patente, b.marca, b.modelo 
            FROM buses b WHERE b.id = %s AND b.esta_activo = true
        """, (bus_id,))
        
        bus = cursor.fetchone()
        if not bus:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Bus no encontrado")
        
        # Eliminar lógicamente
        cursor.execute("""
            UPDATE buses SET esta_activo = false, fecha_actualizacion = NOW() 
            WHERE id = %s
        """, (bus_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Bus eliminado exitosamente",
            "bus_eliminado": {
                "id": bus[0], "patente": bus[1], "marca": bus[2], "modelo": bus[3]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# Endpoints auxiliares
@router.get("/auxiliares/estados", summary="Obtener estados disponibles")
def obtener_estados():
    """Obtener lista de estados de buses disponibles"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, codigo, nombre, descripcion 
            FROM estados_buses WHERE es_activo = true 
            ORDER BY nombre
        """)
        
        estados = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "estados": [
                {"id": row[0], "codigo": row[1], "nombre": row[2], "descripcion": row[3]}
                for row in estados
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/auxiliares/combustibles", summary="Obtener tipos de combustible")
def obtener_tipos_combustible():
    """Obtener lista de tipos de combustible disponibles"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, codigo, nombre, factor_emision 
            FROM tipos_combustible WHERE es_activo = true 
            ORDER BY nombre
        """)
        
        tipos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "tipos_combustible": [
                {"id": row[0], "codigo": row[1], "nombre": row[2], 
                 "factor_emision": float(row[3]) if row[3] else None}
                for row in tipos
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.patch("/{bus_id}/restaurar", summary="Restaurar bus eliminado")
def restaurar_bus(bus_id: int):
    """Restaurar un bus eliminado lógicamente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el bus existe y está inactivo
        cursor.execute("""
            SELECT b.id, b.patente, b.marca, b.modelo 
            FROM buses b 
            WHERE b.id = %s AND b.esta_activo = false
        """, (bus_id,))
        
        bus = cursor.fetchone()
        if not bus:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Bus no encontrado o no está eliminado")
        
        # Restaurar el bus
        cursor.execute("""
            UPDATE buses 
            SET esta_activo = true, fecha_actualizacion = NOW() 
            WHERE id = %s
        """, (bus_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Bus restaurado exitosamente",
            "bus_restaurado": {
                "id": bus[0],
                "patente": bus[1],
                "marca": bus[2],
                "modelo": bus[3]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")



@router.get("/reportes/estadisticas", summary="Estadísticas de la flota")
def obtener_estadisticas():
    """Obtener estadísticas generales de la flota de buses"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total de buses
        cursor.execute("SELECT COUNT(*) FROM buses WHERE esta_activo = true")
        total_buses = cursor.fetchone()[0]
        
        # Buses por estado
        cursor.execute("""
            SELECT e.nombre, COUNT(b.id) 
            FROM estados_buses e 
            LEFT JOIN buses b ON e.id = b.estado_id AND b.esta_activo = true
            GROUP BY e.id, e.nombre
            ORDER BY e.nombre
        """)
        estados_stats = dict(cursor.fetchall())
        
        # Capacidad total
        cursor.execute("""
            SELECT COALESCE(SUM(capacidad_sentados), 0) 
            FROM buses WHERE esta_activo = true
        """)
        capacidad_total = cursor.fetchone()[0]
        
        # Total eliminados
        cursor.execute("SELECT COUNT(*) FROM buses WHERE esta_activo = false")
        total_eliminados = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "total_buses": total_buses,
            "total_eliminados": total_eliminados,
            "por_estado": estados_stats,
            "capacidad_total_flota": capacidad_total,
            "fecha_consulta": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")