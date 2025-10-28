from sqlalchemy.orm import Session
from sqlalchemy import func
from models.categoria import Categoria
from models.material import Material
from schemas.categoria_schemas import CategoriaCreate, CategoriaUpdate
from typing import Optional, List

class CategoriaRepository:
    
    @staticmethod
    def create(db: Session, categoria_data: CategoriaCreate) -> Categoria:
        """Crear una nueva categoría"""
        categoria = Categoria(**categoria_data.model_dump())
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
        return categoria
    
    @staticmethod
    def get_by_id(db: Session, categoria_id: int) -> Optional[Categoria]:
        """Obtener categoría por ID"""
        return db.query(Categoria).filter(Categoria.id == categoria_id).first()
    
    @staticmethod
    def get_by_codigo(db: Session, codigo: str) -> Optional[Categoria]:
        """Obtener categoría por código"""
        return db.query(Categoria).filter(Categoria.codigo == codigo.upper()).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Categoria]:
        """Obtener todas las categorías con paginación"""
        return db.query(Categoria).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_with_count(db: Session, skip: int = 0, limit: int = None):
        """Obtener categorías con conteo de materiales"""
        query = db.query(
            Categoria,
            func.count(Material.id).label('total_materiales')
        ).outerjoin(Material).group_by(Categoria.id).offset(skip)
        
        if limit is not None:
            query = query.limit(limit)
        
        categorias = query.all()
        
        result = []
        for categoria, total_materiales in categorias:
            categoria_dict = {
                "id": categoria.id,
                "codigo": categoria.codigo,
                "nombre": categoria.nombre,
                "descripcion": categoria.descripcion,
                "imagen_url": categoria.imagen_url,
                "fecha_creacion": categoria.fecha_creacion,
                "fecha_actualizacion": categoria.fecha_actualizacion,
                "total_materiales": total_materiales
            }
            result.append(categoria_dict)
        
        return result
    
    @staticmethod
    def update(db: Session, categoria_id: int, categoria_data: CategoriaUpdate) -> Optional[Categoria]:
        """Actualizar una categoría"""
        categoria = CategoriaRepository.get_by_id(db, categoria_id)
        if not categoria:
            return None
        
        update_data = categoria_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(categoria, key, value)
        
        db.commit()
        db.refresh(categoria)
        return categoria
    
    @staticmethod
    def delete(db: Session, categoria_id: int) -> bool:
        """Eliminar una categoría"""
        categoria = CategoriaRepository.get_by_id(db, categoria_id)
        if not categoria:
            return False
        
        db.delete(categoria)
        db.commit()
        return True
    
    @staticmethod
    def count(db: Session) -> int:
        """Contar total de categorías"""
        return db.query(func.count(Categoria.id)).scalar()
