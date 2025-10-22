"""
Repositorio para operaciones CRUD de Plano
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from models.plano import Plano
from schemas.plano_schemas import PlanoCreate, PlanoUpdate

class PlanoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, plano_data: PlanoCreate, usuario_id: int, url: str = None) -> Plano:
        """Crear un nuevo plano"""
        plano = Plano(
            usuario_id=usuario_id,
            nombre=plano_data.nombre,
            url=url,
            formato=plano_data.formato,
            tipo_plano=plano_data.tipo_plano,
            descripcion=plano_data.descripcion,
            medidas_extraidas=plano_data.medidas_extraidas,
            estado="subido"
        )
        self.db.add(plano)
        self.db.commit()
        self.db.refresh(plano)
        return plano

    def get_by_id(self, plano_id: int, usuario_id: int) -> Optional[Plano]:
        """Obtener un plano por ID (solo del usuario propietario)"""
        return self.db.query(Plano).filter(
            and_(Plano.id == plano_id, Plano.usuario_id == usuario_id)
        ).first()

    def get_by_id_only(self, plano_id: int) -> Optional[Plano]:
        """Obtener un plano por ID sin verificar usuario (para acceso público)"""
        return self.db.query(Plano).filter(Plano.id == plano_id).first()

    def get_all_by_usuario(self, usuario_id: int, skip: int = 0, limit: int = 100) -> List[Plano]:
        """Obtener todos los planos de un usuario con paginación"""
        return self.db.query(Plano).filter(
            Plano.usuario_id == usuario_id
        ).offset(skip).limit(limit).all()

    def count_by_usuario(self, usuario_id: int) -> int:
        """Contar total de planos de un usuario"""
        return self.db.query(Plano).filter(Plano.usuario_id == usuario_id).count()

    def update(self, plano_id: int, usuario_id: int, plano_data: PlanoUpdate) -> Optional[Plano]:
        """Actualizar un plano"""
        plano = self.get_by_id(plano_id, usuario_id)
        if not plano:
            return None
        
        update_data = plano_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plano, field, value)
        
        self.db.commit()
        self.db.refresh(plano)
        return plano

    def update_estado(self, plano_id: int, usuario_id: int, estado: str) -> Optional[Plano]:
        """Actualizar solo el estado de un plano"""
        plano = self.get_by_id(plano_id, usuario_id)
        if not plano:
            return None
        
        plano.estado = estado
        self.db.commit()
        self.db.refresh(plano)
        return plano

    def delete(self, plano_id: int, usuario_id: int) -> bool:
        """Eliminar un plano (solo del usuario propietario)"""
        plano = self.get_by_id(plano_id, usuario_id)
        if not plano:
            return False
        
        self.db.delete(plano)
        self.db.commit()
        return True

    def get_by_estado(self, usuario_id: int, estado: str) -> List[Plano]:
        """Obtener planos por estado"""
        return self.db.query(Plano).filter(
            and_(Plano.usuario_id == usuario_id, Plano.estado == estado)
        ).all()
