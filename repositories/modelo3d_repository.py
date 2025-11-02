"""
Repositorio para operaciones CRUD de Modelo3D
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from models.modelo3d import Modelo3D
from schemas.modelo3d_schemas import Modelo3DCreate

class Modelo3DRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, modelo_data: Modelo3DCreate) -> Modelo3D:
        """Crear un nuevo modelo 3D"""
        modelo = Modelo3D(
            plano_id=modelo_data.plano_id,
            datos_json=modelo_data.datos_json,
            estado_renderizado=modelo_data.estado_renderizado
        )
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        return modelo

    def get_by_plano_id(self, plano_id: int) -> Optional[Modelo3D]:
        """Obtener modelo 3D por ID del plano"""
        return self.db.query(Modelo3D).filter(Modelo3D.plano_id == plano_id).first()

    def get_by_id(self, modelo3d_id: int) -> Optional[Modelo3D]:
        """Obtener modelo 3D por su ID"""
        return self.db.query(Modelo3D).filter(Modelo3D.id == modelo3d_id).first()

    def get_by_plano_id_and_usuario(self, plano_id: int, usuario_id: int) -> Optional[Modelo3D]:
        """Obtener modelo 3D por ID del plano verificando que pertenezca al usuario"""
        return self.db.query(Modelo3D).join(Modelo3D.plano).filter(
            and_(Modelo3D.plano_id == plano_id, Modelo3D.plano.has(usuario_id=usuario_id))
        ).first()

    def update(self, plano_id: int, datos_json: dict, estado_renderizado: str = "generado") -> Optional[Modelo3D]:
        """Actualizar o crear modelo 3D"""
        modelo = self.get_by_plano_id(plano_id)
        
        if modelo:
            # Actualizar existente
            modelo.datos_json = datos_json
            modelo.estado_renderizado = estado_renderizado
        else:
            # Crear nuevo
            modelo = Modelo3D(
                plano_id=plano_id,
                datos_json=datos_json,
                estado_renderizado=estado_renderizado
            )
            self.db.add(modelo)
        
        self.db.commit()
        self.db.refresh(modelo)
        return modelo

    def delete_by_plano_id(self, plano_id: int) -> bool:
        """Eliminar modelo 3D por ID del plano"""
        modelo = self.get_by_plano_id(plano_id)
        if not modelo:
            return False
        
        self.db.delete(modelo)
        self.db.commit()
        return True

    def exists_by_plano_id(self, plano_id: int) -> bool:
        """Verificar si existe modelo 3D para un plano"""
        return self.db.query(Modelo3D).filter(Modelo3D.plano_id == plano_id).first() is not None
