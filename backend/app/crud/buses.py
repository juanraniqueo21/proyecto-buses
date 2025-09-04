"""
Operaciones CRUD (Create, Read, Update, Delete) para el modelo Bus
Sistema de Gestión de Flota de Buses
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.buses import Bus
from app.schemas.buses import BusCrear, BusActualizar

class CRUDBus:
    """Clase para operaciones CRUD del modelo Bus"""

    def crear_bus(self, db: Session, bus_data: BusCrear) -> Bus:
        """
        Crear un nuevo bus en la base de datos
        """
        # Convertir schema a diccionario
        bus_dict = bus_data.dict()
        
        # Crear instancia del modelo
        db_bus = Bus(**bus_dict)
        
        # Guardar en base de datos
        db.add(db_bus)
        db.commit()
        db.refresh(db_bus)
        
        return db_bus

    def obtener_bus_por_id(self, db: Session, bus_id: int) -> Optional[Bus]:
        """
        Obtener un bus por su ID
        """
        return db.query(Bus).filter(Bus.id == bus_id, Bus.esta_activo == True).first()

    def obtener_bus_por_patente(self, db: Session, patente: str) -> Optional[Bus]:
        """
        Obtener un bus por su patente
        """
        return db.query(Bus).filter(Bus.patente == patente.upper(), Bus.esta_activo == True).first()

    def obtener_buses(self, db: Session, skip: int = 0, limit: int = 100) -> List[Bus]:
        """
        Obtener lista de buses con paginación
        """
        return db.query(Bus).filter(Bus.esta_activo == True).offset(skip).limit(limit).all()

    def obtener_buses_por_estado(self, db: Session, estado: str) -> List[Bus]:
        """
        Obtener buses filtrados por estado
        """
        return db.query(Bus).filter(Bus.estado == estado, Bus.esta_activo == True).all()

    def obtener_buses_por_marca(self, db: Session, marca: str) -> List[Bus]:
        """
        Obtener buses filtrados por marca
        """
        return db.query(Bus).filter(Bus.marca.ilike(f"%{marca}%"), Bus.esta_activo == True).all()

    def buscar_buses(self, db: Session, termino_busqueda: str) -> List[Bus]:
        """
        Buscar buses por patente, marca o modelo
        """
        return db.query(Bus).filter(
            or_(
                Bus.patente.ilike(f"%{termino_busqueda}%"),
                Bus.marca.ilike(f"%{termino_busqueda}%"),
                Bus.modelo.ilike(f"%{termino_busqueda}%")
            ),
            Bus.esta_activo == True
        ).all()

    def contar_buses(self, db: Session) -> int:
        """
        Contar total de buses activos
        """
        return db.query(Bus).filter(Bus.esta_activo == True).count()

    def contar_buses_por_estado(self, db: Session, estado: str) -> int:
        """
        Contar buses por estado específico
        """
        return db.query(Bus).filter(Bus.estado == estado, Bus.esta_activo == True).count()

    def actualizar_bus(self, db: Session, bus_id: int, bus_data: BusActualizar) -> Optional[Bus]:
        """
        Actualizar datos de un bus existente
        """
        # Obtener bus existente
        db_bus = self.obtener_bus_por_id(db, bus_id)
        if not db_bus:
            return None

        # Actualizar solo campos que no son None
        update_data = bus_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_bus, field, value)

        # Guardar cambios
        db.commit()
        db.refresh(db_bus)
        
        return db_bus

    def actualizar_kilometraje(self, db: Session, bus_id: int, nuevo_kilometraje: int) -> Optional[Bus]:
        """
        Actualizar específicamente el kilometraje de un bus
        """
        db_bus = self.obtener_bus_por_id(db, bus_id)
        if not db_bus:
            return None

        db_bus.kilometraje_actual = nuevo_kilometraje
        db.commit()
        db.refresh(db_bus)
        
        return db_bus

    def cambiar_estado_bus(self, db: Session, bus_id: int, nuevo_estado: str) -> Optional[Bus]:
        """
        Cambiar el estado operacional de un bus
        """
        db_bus = self.obtener_bus_por_id(db, bus_id)
        if not db_bus:
            return None

        db_bus.estado = nuevo_estado
        db.commit()
        db.refresh(db_bus)
        
        return db_bus

    def eliminar_bus(self, db: Session, bus_id: int) -> bool:
        """
        Eliminar un bus (soft delete - marcar como inactivo)
        """
        db_bus = self.obtener_bus_por_id(db, bus_id)
        if not db_bus:
            return False

        db_bus.esta_activo = False
        db.commit()
        
        return True

    def eliminar_bus_permanente(self, db: Session, bus_id: int) -> bool:
        """
        Eliminar un bus permanentemente de la base de datos
        USAR CON PRECAUCIÓN
        """
        db_bus = db.query(Bus).filter(Bus.id == bus_id).first()
        if not db_bus:
            return False

        db.delete(db_bus)
        db.commit()
        
        return True

    def obtener_buses_mantenimiento_pendiente(self, db: Session, kilometraje_limite: int = 10000) -> List[Bus]:
        """
        Obtener buses que necesitan mantenimiento según kilometraje
        """
        buses = db.query(Bus).filter(Bus.esta_activo == True).all()
        buses_mantenimiento = []
        
        for bus in buses:
            if bus.necesita_mantenimiento(kilometraje_limite):
                buses_mantenimiento.append(bus)
        
        return buses_mantenimiento

    def obtener_estadisticas_flota(self, db: Session) -> dict:
        """
        Obtener estadísticas generales de la flota
        """
        total_buses = self.contar_buses(db)
        activos = self.contar_buses_por_estado(db, "activo")
        mantenimiento = self.contar_buses_por_estado(db, "mantenimiento")
        fuera_servicio = self.contar_buses_por_estado(db, "fuera_de_servicio")
        
        return {
            "total_buses": total_buses,
            "activos": activos,
            "en_mantenimiento": mantenimiento,
            "fuera_de_servicio": fuera_servicio,
            "porcentaje_activos": round((activos / total_buses * 100) if total_buses > 0 else 0, 2)
        }

# Instancia global para usar en los endpoints
crud_bus = CRUDBus()