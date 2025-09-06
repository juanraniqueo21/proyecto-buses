"""
Repository Pattern para operaciones CRUD del modelo Bus
Actualizado para trabajar con tablas normalizadas y foreign keys
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from models.buses import Bus

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from models.estados_tipos import EstadoBus, TipoCombustible
from schemas.buses import BusCrear, BusActualizar


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

    def find_by_estado_codigo(self, codigo_estado: str) -> List[Bus]:
        """Buscar buses por código de estado (ACT, MAN, FS, RET)"""
        return self.db.query(Bus)\
            .join(EstadoBus)\
            .options(joinedload(Bus.estado), joinedload(Bus.tipo_combustible))\
            .filter(and_(
                EstadoBus.codigo == codigo_estado.upper(),
                Bus.esta_activo == True
            ))\
            .all()

    def find_by_marca(self, marca: str) -> List[Bus]:
        """Buscar buses por marca"""
        return self.db.query(Bus)\
            .options(joinedload(Bus.estado), joinedload(Bus.tipo_combustible))\
            .filter(and_(
                Bus.marca.ilike(f"%{marca}%"),
                Bus.esta_activo == True
            ))\
            .all()

    def search(self, termino: str) -> List[Bus]:
        """Búsqueda general por patente, marca, modelo o código interno"""
        termino_like = f"%{termino}%"
        return self.db.query(Bus)\
            .options(joinedload(Bus.estado), joinedload(Bus.tipo_combustible))\
            .filter(and_(
                or_(
                    Bus.patente.ilike(termino_like),
                    Bus.marca.ilike(termino_like),
                    Bus.modelo.ilike(termino_like),
                    Bus.codigo_interno.ilike(termino_like)
                ),
                Bus.esta_activo == True
            ))\
            .all()

    def create(self, bus_data: BusCrear) -> Bus:
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
            codigo_interno=bus_data.codigo_interno,
            marca=bus_data.marca,
            modelo=bus_data.modelo,
            año=bus_data.año,
            numero_chasis=bus_data.numero_chasis,
            numero_motor=bus_data.numero_motor,
            tipo_combustible_id=bus_data.tipo_combustible_id,
            estado_id=bus_data.estado_id,
            capacidad_sentados=bus_data.capacidad_sentados,
            kilometraje_actual=bus_data.kilometraje_actual or 0,
            fecha_compra=bus_data.fecha_compra,
            precio_compra=bus_data.precio_compra,
            observaciones=bus_data.observaciones
        )

        self.db.add(db_bus)
        self.db.commit()
        self.db.refresh(db_bus)
        return db_bus

    def update(self, bus_id: int, bus_data: BusActualizar) -> Optional[Bus]:
        """Actualizar bus existente"""
        db_bus = self.find_by_id(bus_id)
        if not db_bus:
            return None

        # Actualizar solo campos que no son None
        update_data = bus_data.dict(exclude_unset=True)

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
        """Estadísticas de la flota"""
        total_buses = self.db.query(Bus).filter(Bus.esta_activo == True).count()

        # Estadísticas por estado
        estados_stats = self.db.query(EstadoBus.nombre, self.db.func.count(Bus.id))\
            .join(Bus)\
            .filter(Bus.esta_activo == True)\
            .group_by(EstadoBus.nombre)\
            .all()

        # Capacidad total
        capacidad_total = self.db.query(self.db.func.sum(Bus.capacidad_sentados))\
            .filter(Bus.esta_activo == True)\
            .scalar() or 0

        # Kilometraje promedio
        kilometraje_promedio = self.db.query(self.db.func.avg(Bus.kilometraje_actual))\
            .filter(and_(Bus.esta_activo == True, Bus.kilometraje_actual.isnot(None)))\
            .scalar() or 0

        return {
            "total_buses": total_buses,
            "estados": dict(estados_stats),
            "capacidad_total_flota": int(capacidad_total),
            "kilometraje_promedio": round(float(kilometraje_promedio), 2)
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

    def obtener_buses_por_estado(self, db: Session, estado: str) -> List[Bus]:
        repo = BusRepository(db)
        return repo.find_by_estado_codigo(estado)

    def obtener_buses_por_marca(self, db: Session, marca: str) -> List[Bus]:
        repo = BusRepository(db)
        return repo.find_by_marca(marca)

    def buscar_buses(self, db: Session, termino: str) -> List[Bus]:
        repo = BusRepository(db)
        return repo.search(termino)

    def crear_bus(self, db: Session, bus_data: BusCrear) -> Bus:
        repo = BusRepository(db)
        return repo.create(bus_data)

    def actualizar_bus(self, db: Session, bus_id: int, bus_data: BusActualizar) -> Optional[Bus]:
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