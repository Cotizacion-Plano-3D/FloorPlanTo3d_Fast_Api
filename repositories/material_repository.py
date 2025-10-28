from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from models.material import Material
from models.categoria import Categoria
from schemas.material_schemas import MaterialCreate, MaterialUpdate
from typing import Optional, List

class MaterialRepository:
    
    @staticmethod
    def create(db: Session, material_data: MaterialCreate) -> Material:
        """Crear un nuevo material"""
        material = Material(**material_data.model_dump())
        db.add(material)
        db.commit()
        db.refresh(material)
        return material
    
    @staticmethod
    def get_by_id(db: Session, material_id: int) -> Optional[Material]:
        """Obtener material por ID"""
        return db.query(Material).filter(Material.id == material_id).first()
    
    @staticmethod
    def get_by_id_with_categoria(db: Session, material_id: int) -> Optional[Material]:
        """Obtener material por ID con su categoría"""
        return db.query(Material).options(joinedload(Material.categoria)).filter(Material.id == material_id).first()
    
    @staticmethod
    def get_by_codigo(db: Session, codigo: str) -> Optional[Material]:
        """Obtener material por código"""
        return db.query(Material).filter(Material.codigo == codigo.upper()).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Material]:
        """Obtener todos los materiales con paginación"""
        return db.query(Material).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_with_categoria(db: Session, skip: int = 0, limit: int = 100) -> List[Material]:
        """Obtener todos los materiales con su categoría"""
        return db.query(Material).options(joinedload(Material.categoria)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_categoria(db: Session, categoria_id: int, skip: int = 0, limit: int = 100) -> List[Material]:
        """Obtener materiales por categoría"""
        return db.query(Material).filter(Material.categoria_id == categoria_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def search_by_name(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[Material]:
        """Buscar materiales por nombre o descripción"""
        search = f"%{search_term}%"
        return db.query(Material).filter(
            (Material.nombre.ilike(search)) | 
            (Material.descripcion.ilike(search)) |
            (Material.codigo.ilike(search))
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, material_id: int, material_data: MaterialUpdate) -> Optional[Material]:
        """Actualizar un material"""
        material = MaterialRepository.get_by_id(db, material_id)
        if not material:
            return None
        
        update_data = material_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(material, key, value)
        
        db.commit()
        db.refresh(material)
        return material
    
    @staticmethod
    def delete(db: Session, material_id: int) -> bool:
        """Eliminar un material"""
        material = MaterialRepository.get_by_id(db, material_id)
        if not material:
            return False
        
        db.delete(material)
        db.commit()
        return True
    
    @staticmethod
    def count(db: Session) -> int:
        """Contar total de materiales"""
        return db.query(func.count(Material.id)).scalar()
    
    @staticmethod
    def count_by_categoria(db: Session, categoria_id: int) -> int:
        """Contar materiales por categoría"""
        return db.query(func.count(Material.id)).filter(Material.categoria_id == categoria_id).scalar()
