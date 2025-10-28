from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from models.material_modelo3d import MaterialModelo3D
from models.material import Material
from schemas.material_modelo3d_schemas import MaterialModelo3DCreate, MaterialModelo3DUpdate
from typing import Optional, List

class MaterialModelo3DRepository:
    
    @staticmethod
    def create(db: Session, material_modelo3d_data: MaterialModelo3DCreate) -> MaterialModelo3D:
        """Crear una nueva relación material-modelo3d"""
        # Calcular subtotal
        subtotal = material_modelo3d_data.cantidad * material_modelo3d_data.precio_unitario
        
        material_modelo3d = MaterialModelo3D(
            **material_modelo3d_data.model_dump(),
            subtotal=subtotal
        )
        db.add(material_modelo3d)
        db.commit()
        db.refresh(material_modelo3d)
        return material_modelo3d
    
    @staticmethod
    def create_bulk(db: Session, materiales_data: List[MaterialModelo3DCreate]) -> List[MaterialModelo3D]:
        """Crear múltiples relaciones material-modelo3d"""
        materiales = []
        for material_data in materiales_data:
            subtotal = material_data.cantidad * material_data.precio_unitario
            material = MaterialModelo3D(
                **material_data.model_dump(),
                subtotal=subtotal
            )
            materiales.append(material)
        
        db.add_all(materiales)
        db.commit()
        for material in materiales:
            db.refresh(material)
        return materiales
    
    @staticmethod
    def get_by_id(db: Session, material_modelo3d_id: int) -> Optional[MaterialModelo3D]:
        """Obtener relación por ID"""
        return db.query(MaterialModelo3D).filter(MaterialModelo3D.id == material_modelo3d_id).first()
    
    @staticmethod
    def get_by_id_with_details(db: Session, material_modelo3d_id: int) -> Optional[MaterialModelo3D]:
        """Obtener relación por ID con detalles del material"""
        return db.query(MaterialModelo3D).options(
            joinedload(MaterialModelo3D.material).joinedload(Material.categoria)
        ).filter(MaterialModelo3D.id == material_modelo3d_id).first()
    
    @staticmethod
    def get_by_modelo3d(db: Session, modelo3d_id: int) -> List[MaterialModelo3D]:
        """Obtener todos los materiales de un modelo 3D"""
        return db.query(MaterialModelo3D).filter(MaterialModelo3D.modelo3d_id == modelo3d_id).all()
    
    @staticmethod
    def get_by_modelo3d_with_details(db: Session, modelo3d_id: int) -> List[MaterialModelo3D]:
        """Obtener todos los materiales de un modelo 3D con detalles"""
        return db.query(MaterialModelo3D).options(
            joinedload(MaterialModelo3D.material).joinedload(Material.categoria)
        ).filter(MaterialModelo3D.modelo3d_id == modelo3d_id).all()
    
    @staticmethod
    def get_by_material(db: Session, material_id: int) -> List[MaterialModelo3D]:
        """Obtener todos los modelos 3D que usan un material"""
        return db.query(MaterialModelo3D).filter(MaterialModelo3D.material_id == material_id).all()
    
    @staticmethod
    def update(db: Session, material_modelo3d_id: int, material_data: MaterialModelo3DUpdate) -> Optional[MaterialModelo3D]:
        """Actualizar una relación material-modelo3d"""
        material_modelo3d = MaterialModelo3DRepository.get_by_id(db, material_modelo3d_id)
        if not material_modelo3d:
            return None
        
        update_data = material_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(material_modelo3d, key, value)
        
        # Recalcular subtotal
        material_modelo3d.subtotal = material_modelo3d.cantidad * material_modelo3d.precio_unitario
        
        db.commit()
        db.refresh(material_modelo3d)
        return material_modelo3d
    
    @staticmethod
    def delete(db: Session, material_modelo3d_id: int) -> bool:
        """Eliminar una relación material-modelo3d"""
        material_modelo3d = MaterialModelo3DRepository.get_by_id(db, material_modelo3d_id)
        if not material_modelo3d:
            return False
        
        db.delete(material_modelo3d)
        db.commit()
        return True
    
    @staticmethod
    def delete_by_modelo3d(db: Session, modelo3d_id: int) -> bool:
        """Eliminar todos los materiales de un modelo 3D"""
        db.query(MaterialModelo3D).filter(MaterialModelo3D.modelo3d_id == modelo3d_id).delete()
        db.commit()
        return True
    
    @staticmethod
    def get_total_cost(db: Session, modelo3d_id: int) -> float:
        """Obtener el costo total de materiales de un modelo 3D"""
        total = db.query(func.sum(MaterialModelo3D.subtotal)).filter(
            MaterialModelo3D.modelo3d_id == modelo3d_id
        ).scalar()
        return total if total else 0.0
    
    @staticmethod
    def count_by_modelo3d(db: Session, modelo3d_id: int) -> int:
        """Contar materiales de un modelo 3D"""
        return db.query(func.count(MaterialModelo3D.id)).filter(
            MaterialModelo3D.modelo3d_id == modelo3d_id
        ).scalar()
