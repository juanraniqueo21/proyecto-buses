import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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


class BusActualizar(BusBase):
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
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="flota_buses", 
            user="grupo_trabajo",
            password="grupo1234"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return {
            "status": "Conexión exitosa con psycopg2",
            "postgres_version": version,
            "database": "flota_buses"
        }
    except Exception as e:
        return {"status": "Error de conexión", "error": str(e)}
    
@app.post("/api/v1/buses")
def crear_bus(bus_data: BusCrear):
    """
    Crear un nuevo bus con validaciones de foreign keys
    """
    try:
        import psycopg2
        from datetime import datetime
        
        # Validar patente chilena
        patente = bus_data.patente.upper().replace('-', '').replace(' ', '')
        if len(patente) < 6 or len(patente) > 8:
            return {"error": "Patente debe tener entre 6 y 8 caracteres"}, 400
        
        # Validar año
        año_actual = datetime.now().year
        if bus_data.año < 1980 or bus_data.año > año_actual + 1:
            return {"error": f"Año debe estar entre 1980 y {año_actual + 1}"}, 400
        
        # Validar capacidad
        if bus_data.capacidad_sentados < 1 or bus_data.capacidad_sentados > 45:
            return {"error": "Capacidad debe estar entre 1 y 45 asientos"}, 400
        
        conn = psycopg2.connect(
            host="localhost", port=5433, database="flota_buses", 
            user="grupo_trabajo", password="grupo1234"
        )
        cursor = conn.cursor()
        
        # Verificar que no existe la patente
        cursor.execute("SELECT id FROM buses WHERE patente = %s", (patente,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"error": f"Ya existe un bus con patente {patente}"}, 400
        
        # Verificar que estado_id existe
        cursor.execute("SELECT id, nombre FROM estados_buses WHERE id = %s", (bus_data.estado_id,))
        estado = cursor.fetchone()
        if not estado:
            cursor.close()
            conn.close()
            return {"error": f"Estado con ID {bus_data.estado_id} no existe"}, 400
        
        # Verificar que tipo_combustible_id existe
        cursor.execute("SELECT id, nombre FROM tipos_combustible WHERE id = %s", (bus_data.tipo_combustible_id,))
        tipo_combustible = cursor.fetchone()
        if not tipo_combustible:
            cursor.close()
            conn.close()
            return {"error": f"Tipo de combustible con ID {bus_data.tipo_combustible_id} no existe"}, 400
        
        # Insertar el nuevo bus
        insert_query = """
        INSERT INTO buses (
            patente, codigo_interno, marca, modelo, año, numero_chasis, numero_motor,
            tipo_combustible_id, estado_id, capacidad_sentados, kilometraje_actual,
            fecha_compra, precio_compra, observaciones
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
        """
        
        cursor.execute(insert_query, (
            patente,
            bus_data.codigo_interno,
            bus_data.marca,
            bus_data.modelo,
            bus_data.año,
            bus_data.numero_chasis,
            bus_data.numero_motor,
            bus_data.tipo_combustible_id,
            bus_data.estado_id,
            bus_data.capacidad_sentados,
            bus_data.kilometraje_actual,
            bus_data.fecha_compra,
            bus_data.precio_compra,
            bus_data.observaciones
        ))
        
        bus_id = cursor.fetchone()[0]
        conn.commit()
        
        # Obtener el bus creado con información completa
        cursor.execute("""
            SELECT b.id, b.patente, b.marca, b.modelo, b.año, 
                   e.nombre as estado, t.nombre as combustible, b.capacidad_sentados,
                   b.kilometraje_actual, b.precio_compra, b.observaciones
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
                "id": bus_creado[0],
                "patente": bus_creado[1],
                "marca": bus_creado[2],
                "modelo": bus_creado[3],
                "año": bus_creado[4],
                "estado": bus_creado[5],
                "combustible": bus_creado[6],
                "capacidad": bus_creado[7],
                "kilometraje": bus_creado[8],
                "precio": float(bus_creado[9]) if bus_creado[9] else None,
                "observaciones": bus_creado[10],
                "fecha_compra": bus_creado[14].strftime("%d/%m/%Y") if bus_creado[14] else None

            }

        }
        
    except psycopg2.IntegrityError as e:
        return {"error": "Error de integridad en base de datos", "details": str(e)}, 400
    except Exception as e:
        return {"error": "Error interno del servidor", "details": str(e)}, 500




@app.get("/api/v1/buses")
def listar_buses():
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost", port=5433, database="flota_buses", 
            user="grupo_trabajo", password="grupo1234"
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.patente, b.marca, b.modelo, b.año, 
                   e.nombre as estado, t.nombre as combustible, b.capacidad_sentados
            FROM buses b 
            JOIN estados_buses e ON b.estado_id = e.id 
            JOIN tipos_combustible t ON b.tipo_combustible_id = t.id
            WHERE b.esta_activo = true
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
        
        return {"message": "Lista de buses", "buses": buses_data}
    except Exception as e:
        return {"message": "Error al obtener buses", "error": str(e), "buses": []}

@app.get("/api/v1/estados-buses")
def obtener_estados():
    """Obtener lista de estados disponibles para buses"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost", port=5433, database="flota_buses", 
            user="grupo_trabajo", password="grupo1234"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo, nombre, descripcion FROM estados_buses WHERE es_activo = true ORDER BY nombre")
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
        return {"error": str(e)}


@app.get("/api/v1/tipos-combustible")
def obtener_tipos_combustible():
    """Obtener lista de tipos de combustible disponibles"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost", port=5433, database="flota_buses", 
            user="grupo_trabajo", password="grupo1234"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo, nombre, factor_emision FROM tipos_combustible WHERE es_activo = true ORDER BY nombre")
        tipos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "tipos_combustible": [
                {"id": row[0], "codigo": row[1], "nombre": row[2], "factor_emision": float(row[3]) if row[3] else None}
                for row in tipos
            ]
        }
    except Exception as e:
        return {"error": str(e)}
# Endpoint para ver buses eliminados (útil para administración)
@app.get("/api/v1/buses/eliminados")
def listar_buses_eliminados():
    """
    Obtener lista de buses eliminados lógicamente
    """
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost", port=5433, database="flota_buses", 
            user="grupo_trabajo", password="grupo1234"
        )
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
                "fecha_eliminacion": row[7]
            } 
            for row in buses
        ]
        
        return {
            "message": "Buses eliminados",
            "total": len(buses_eliminados),
            "buses": buses_eliminados
        }
    except Exception as e:
        return {"error": str(e)}, 500


@app.get("/api/v1/buses/{bus_id}")
def obtener_bus(bus_id: int):
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost", port=5433, database="flota_buses", 
            user="grupo_trabajo", password="grupo1234"
        )
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
            return {"error": "Bus no encontrado"}, 404
            
        return {
            "bus": {
                "id": bus[0], "patente": bus[1], "marca": bus[2], "modelo": bus[3],
                "año": bus[4], "estado": bus[5], "combustible": bus[6], "capacidad": bus[7],
                "kilometraje": bus[8], "precio": float(bus[9]) if bus[9] else None,
                "observaciones": bus[10], "codigo_interno": bus[11],
                "numero_chasis": bus[12], "numero_motor": bus[13], "fecha_compra": bus[14].strftime("%d/%m/%Y") if bus[14] else None
            }
        }
    except Exception as e:
        return {"error": str(e)}, 500

@app.put("/api/v1/buses/{bus_id}")
def actualizar_bus(bus_id: int, bus_data: BusActualizar):
    """
    Actualizar un bus existente
    """
    try:
        import psycopg2
        from datetime import datetime
        
        conn = psycopg2.connect(
            host="localhost", port=5433, database="flota_buses", 
            user="grupo_trabajo", password="grupo1234"
        )
        cursor = conn.cursor()
        
        # Verificar que el bus existe
        cursor.execute("SELECT id FROM buses WHERE id = %s AND esta_activo = true", (bus_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return {"error": "Bus no encontrado"}, 404
        
        # Construir query dinámico solo con campos que no son None
        campos_actualizar = []
        valores = []
        
        if bus_data.patente is not None:
            patente_limpia = bus_data.patente.upper().replace('-', '').replace(' ', '')
            if len(patente_limpia) < 6 or len(patente_limpia) > 8:
                cursor.close()
                conn.close()
                return {"error": "Patente debe tener entre 6 y 8 caracteres"}, 400
            
            # Verificar que la patente no esté en uso por otro bus
            cursor.execute("SELECT id FROM buses WHERE patente = %s AND id != %s", (patente_limpia, bus_id))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return {"error": f"La patente {patente_limpia} ya está en uso por otro bus"}, 400
            
            campos_actualizar.append("patente = %s")
            valores.append(patente_limpia)
        
        if bus_data.marca is not None:
            campos_actualizar.append("marca = %s")
            valores.append(bus_data.marca)
        
        if bus_data.modelo is not None:
            campos_actualizar.append("modelo = %s")
            valores.append(bus_data.modelo)
        
        if bus_data.año is not None:
            año_actual = datetime.now().year
            if bus_data.año < 1980 or bus_data.año > año_actual + 1:
                cursor.close()
                conn.close()
                return {"error": f"Año debe estar entre 1980 y {año_actual + 1}"}, 400
            campos_actualizar.append("año = %s")
            valores.append(bus_data.año)
        
        if bus_data.capacidad_sentados is not None:
            if bus_data.capacidad_sentados < 1 or bus_data.capacidad_sentados > 45:
                cursor.close()
                conn.close()
                return {"error": "Capacidad debe estar entre 1 y 45 asientos"}, 400
            campos_actualizar.append("capacidad_sentados = %s")
            valores.append(bus_data.capacidad_sentados)
        
        if bus_data.estado_id is not None:
            cursor.execute("SELECT id FROM estados_buses WHERE id = %s", (bus_data.estado_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return {"error": f"Estado con ID {bus_data.estado_id} no existe"}, 400
            campos_actualizar.append("estado_id = %s")
            valores.append(bus_data.estado_id)
        
        if bus_data.tipo_combustible_id is not None:
            cursor.execute("SELECT id FROM tipos_combustible WHERE id = %s", (bus_data.tipo_combustible_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return {"error": f"Tipo de combustible con ID {bus_data.tipo_combustible_id} no existe"}, 400
            campos_actualizar.append("tipo_combustible_id = %s")
            valores.append(bus_data.tipo_combustible_id)
        
        if bus_data.codigo_interno is not None:
            campos_actualizar.append("codigo_interno = %s")
            valores.append(bus_data.codigo_interno)
        
        if bus_data.numero_chasis is not None:
            campos_actualizar.append("numero_chasis = %s")
            valores.append(bus_data.numero_chasis)
        
        if bus_data.numero_motor is not None:
            campos_actualizar.append("numero_motor = %s")
            valores.append(bus_data.numero_motor)
        
        if bus_data.kilometraje_actual is not None:
            campos_actualizar.append("kilometraje_actual = %s")
            valores.append(bus_data.kilometraje_actual)
        
        if bus_data.fecha_compra is not None:
            campos_actualizar.append("fecha_compra = %s")
            valores.append(bus_data.fecha_compra)
        
        if bus_data.precio_compra is not None:
            campos_actualizar.append("precio_compra = %s")
            valores.append(bus_data.precio_compra)
        
        if bus_data.observaciones is not None:
            campos_actualizar.append("observaciones = %s")
            valores.append(bus_data.observaciones)
        
        # Si no hay campos para actualizar
        if not campos_actualizar:
            cursor.close()
            conn.close()
            return {"error": "No se proporcionaron campos para actualizar"}, 400
        
        # Agregar fecha de actualización
        campos_actualizar.append("fecha_actualizacion = NOW()")
        
        # Ejecutar actualización
        update_query = f"UPDATE buses SET {', '.join(campos_actualizar)} WHERE id = %s"
        valores.append(bus_id)
        
        cursor.execute(update_query, valores)
        conn.commit()
        
        # Obtener el bus actualizado
        cursor.execute("""
            SELECT b.id, b.patente, b.marca, b.modelo, b.año, 
                   e.nombre as estado, t.nombre as combustible, b.capacidad_sentados,
                   b.kilometraje_actual, b.precio_compra, b.observaciones, b.codigo_interno,
                   b.numero_chasis, b.numero_motor, b.fecha_compra
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
                "kilometraje": bus_actualizado[8], "precio": float(bus_actualizado[9]) if bus_actualizado[9] else None,
                "observaciones": bus_actualizado[10], "codigo_interno": bus_actualizado[11],
                "numero_chasis": bus_actualizado[12], "numero_motor": bus_actualizado[13], 
                "fecha_compra": bus_actualizado[14].strftime("%d/%m/%Y") if bus_actualizado[14] else None
            }
        }
        
    except psycopg2.IntegrityError as e:
        return {"error": "Error de integridad en base de datos", "details": str(e)}, 400
    except Exception as e:
        return {"error": "Error interno del servidor", "details": str(e)}, 500

@app.get("/api/v1/buses-sql-test")
def test_buses_sql():
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost", port=5433, database="flota_buses", 
            user="grupo_trabajo", password="grupo1234"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, patente, marca, modelo FROM buses;")
        buses = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"buses_from_sql": buses}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/api/v1/buses/{bus_id}")
def eliminar_bus(bus_id: int):
    """
    Eliminar un bus (eliminación lógica - soft delete)
    El bus se marca como inactivo pero permanece en la base de datos
    """
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost", port=5433, database="flota_buses", 
            user="grupo_trabajo", password="grupo1234"
        )
        cursor = conn.cursor()
        
        # Verificar que el bus existe y está activo
        cursor.execute("""
            SELECT b.id, b.patente, b.marca, b.modelo, e.nombre as estado 
            FROM buses b 
            LEFT JOIN estados_buses e ON b.estado_id = e.id
            WHERE b.id = %s AND b.esta_activo = true
        """, (bus_id,))
        
        bus = cursor.fetchone()
        if not bus:
            cursor.close()
            conn.close()
            return {"error": "Bus no encontrado o ya está eliminado"}, 404
        
        # Verificar si el bus puede ser eliminado (reglas de negocio)
        # Por ejemplo, no eliminar buses que están en rutas activas
        # Esta validación se expandirá cuando implementes el módulo de asignaciones
        
        # Realizar eliminación lógica
        cursor.execute("""
            UPDATE buses 
            SET esta_activo = false, fecha_actualizacion = NOW() 
            WHERE id = %s
        """, (bus_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Bus eliminado exitosamente",
            "bus_eliminado": {
                "id": bus[0],
                "patente": bus[1],
                "marca": bus[2],
                "modelo": bus[3],
                "estado_anterior": bus[4]
            },
            "nota": "El bus ha sido marcado como inactivo pero permanece en la base de datos"
        }
        
    except Exception as e:
        return {"error": "Error interno del servidor", "details": str(e)}, 500


# Endpoint adicional para restaurar buses eliminados
@app.patch("/api/v1/buses/{bus_id}/restaurar")
def restaurar_bus(bus_id: int):
    """
    Restaurar un bus eliminado lógicamente
    """
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost", port=5433, database="flota_buses", 
            user="grupo_trabajo", password="grupo1234"
        )
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
            return {"error": "Bus no encontrado o no está eliminado"}, 404
        
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
        
    except Exception as e:
        return {"error": "Error interno del servidor", "details": str(e)}, 500


