"""
Repository Pattern para operaciones CRUD del modelo Bus
Actualizado para trabajar con tablas normalizadas y foreign keys
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

# Imports corregidos con app.
from app.models.buses import Bus
from app.models.estados_tipos import EstadoBus, TipoCombustible

# Crear schemas simples para el CRUD
class BusCrear:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class BusActualizar:
    def __init__(self, **kwargs):
        self._data = kwargs
    
    def dict(self, exclude_unset=False):
        return self._data

class BusRepository:
    """Repository para operaciones de acceso a datos de Bus"""

    def __init__(self, db: Session):
        self.db = db

    def find_all_with_details(self, skip: int = 0, limit: int = 50) -> List[Bus]:
        """Obtener todos los buses con información de estado y combustible"""
        return self.db.query(Bus)\
            .options(joinedload(Bus.estado), joinedload(Bus.tipo_combustible))\
            .filter(Bus.esta_activo == True)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def find_by_id(self, bus_id: int) -> Optional[Bus]:
        """Buscar bus por ID con información completa"""
        return self.db.query(Bus)\
            .options(joinedload(Bus.estado), joinedload(Bus.tipo_combustible))\
            .filter(and_(Bus.id == bus_id, Bus.esta_activo == True))\
            .first()

    def find_by_patente(self, patente: str) -> Optional[Bus]:
        """Buscar bus por patente"""
        patente_limpia = patente.upper().replace('-', '').replace(' ', '')
        return self.db.query(Bus)\
            .options(joinedload(Bus.estado), joinedload(Bus.tipo_combustible))\
            .filter(and_(Bus.patente == patente_limpia, Bus.esta_activo == True))\
            .first()

    def create(self, bus_data) -> Bus:
        """Crear nuevo bus con validación de foreign keys"""
        # Validar que estado_id existe
        estado = self.db.query(EstadoBus).filter(EstadoBus.id == bus_data.estado_id).first()
        if not estado:
            raise ValueError(f"Estado con ID {bus_data.estado_id} no existe")

        # Validar que tipo_combustible_id existe
        tipo_combustible = self.db.query(TipoCombustible).filter(
            TipoCombustible.id == bus_data.tipo_combustible_id
        ).first()
        if not tipo_combustible:
            raise ValueError(f"Tipo de combustible con ID {bus_data.tipo_combustible_id} no existe")

        # Limpiar patente
        patente_limpia = bus_data.patente.upper().replace('-', '').replace(' ', '')

        # Crear objeto Bus
        db_bus = Bus(
            patente=patente_limpia,
            codigo_interno=getattr(bus_data, 'codigo_interno', None),
            marca=bus_data.marca,
            modelo=bus_data.modelo,
            año=bus_data.año,
            numero_chasis=getattr(bus_data, 'numero_chasis', None),
            numero_motor=getattr(bus_data, 'numero_motor', None),
            tipo_combustible_id=bus_data.tipo_combustible_id,
            estado_id=bus_data.estado_id,
            capacidad_sentados=bus_data.capacidad_sentados,
            kilometraje_actual=getattr(bus_data, 'kilometraje_actual', 0) or 0,
            fecha_compra=getattr(bus_data, 'fecha_compra', None),
            precio_compra=getattr(bus_data, 'precio_compra', None),
            observaciones=getattr(bus_data, 'observaciones', None)
        )

        self.db.add(db_bus)
        self.db.commit()
        self.db.refresh(db_bus)
        return db_bus

    def update(self, bus_id: int, bus_data) -> Optional[Bus]:
        """Actualizar bus existente"""
        db_bus = self.find_by_id(bus_id)
        if not db_bus:
            return None

        # Obtener datos de actualización
        if hasattr(bus_data, 'dict'):
            update_data = bus_data.dict(exclude_unset=True)
        else:
            update_data = {k: v for k, v in bus_data.__dict__.items() if v is not None}

        # Validar foreign keys si se actualizan
        if 'estado_id' in update_data:
            estado = self.db.query(EstadoBus).filter(EstadoBus.id == update_data['estado_id']).first()
            if not estado:
                raise ValueError(f"Estado con ID {update_data['estado_id']} no existe")

        if 'tipo_combustible_id' in update_data:
            tipo_combustible = self.db.query(TipoCombustible).filter(
                TipoCombustible.id == update_data['tipo_combustible_id']
            ).first()
            if not tipo_combustible:
                raise ValueError(f"Tipo de combustible con ID {update_data['tipo_combustible_id']} no existe")

        # Limpiar patente si se actualiza
        if 'patente' in update_data and update_data['patente']:
            update_data['patente'] = update_data['patente'].upper().replace('-', '').replace(' ', '')

        for field, value in update_data.items():
            setattr(db_bus, field, value)

        self.db.commit()
        self.db.refresh(db_bus)
        return db_bus

    def soft_delete(self, bus_id: int) -> bool:
        """Eliminación lógica del bus"""
        db_bus = self.find_by_id(bus_id)
        if not db_bus:
            return False

        db_bus.esta_activo = False
        self.db.commit()
        return True

    def get_statistics(self) -> dict:
        """Estadísticas de la flota - CORREGIDO"""
        try:
            total_buses = self.db.query(Bus).filter(Bus.esta_activo == True).count()

            # Estadísticas por estado - CORREGIDO con left join
            from sqlalchemy import func
            estados_stats = self.db.query(EstadoBus.nombre, func.count(Bus.id))\
                .outerjoin(Bus, and_(EstadoBus.id == Bus.estado_id, Bus.esta_activo == True))\
                .group_by(EstadoBus.id, EstadoBus.nombre)\
                .all()

            # Capacidad total
            capacidad_result = self.db.query(func.sum(Bus.capacidad_sentados))\
                .filter(Bus.esta_activo == True)\
                .scalar()
            capacidad_total = int(capacidad_result) if capacidad_result else 0

            # Kilometraje promedio
            kilometraje_result = self.db.query(func.avg(Bus.kilometraje_actual))\
                .filter(and_(Bus.esta_activo == True, Bus.kilometraje_actual.isnot(None)))\
                .scalar()
            kilometraje_promedio = round(float(kilometraje_result), 2) if kilometraje_result else 0

            return {
                "total_buses": total_buses,
                "estados": dict(estados_stats) if estados_stats else {},
                "capacidad_total_flota": capacidad_total,
                "kilometraje_promedio": kilometraje_promedio
            }
        except Exception as e:
            print(f"Error en get_statistics: {e}")
            # Retornar datos por defecto en caso de error
            return {
                "total_buses": 0,
                "estados": {},
                "capacidad_total_flota": 0,
                "kilometraje_promedio": 0
            }


class CRUDBus:
    """Wrapper para mantener compatibilidad con endpoints existentes"""

    def __init__(self):
        pass

    def obtener_buses(self, db: Session, skip: int = 0, limit: int = 50) -> List[Bus]:
        repo = BusRepository(db)
        return repo.find_all_with_details(skip, limit)

    def obtener_bus_por_id(self, db: Session, bus_id: int) -> Optional[Bus]:
        repo = BusRepository(db)
        return repo.find_by_id(bus_id)

    def obtener_bus_por_patente(self, db: Session, patente: str) -> Optional[Bus]:
        repo = BusRepository(db)
        return repo.find_by_patente(patente)

    def crear_bus(self, db: Session, bus_data) -> Bus:
        repo = BusRepository(db)
        return repo.create(bus_data)

    def actualizar_bus(self, db: Session, bus_id: int, bus_data) -> Optional[Bus]:
        repo = BusRepository(db)
        return repo.update(bus_id, bus_data)

    def eliminar_bus(self, db: Session, bus_id: int) -> bool:
        repo = BusRepository(db)
        return repo.soft_delete(bus_id)

    def obtener_estadisticas_flota(self, db: Session) -> dict:
        repo = BusRepository(db)
        return repo.get_statistics()


# Instancia global para compatibilidad
crud_bus = CRUDBus()