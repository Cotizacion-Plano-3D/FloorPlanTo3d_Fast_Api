"""
Script para crear datos de prueba de categorías y materiales
Ejecutar: python seed_materiales.py
"""

from database import SessionLocal, engine
from models import Base
from models.categoria import Categoria
from models.material import Material
from datetime import datetime

def create_seed_data():
    db = SessionLocal()
    
    try:
        print("🌱 Iniciando seed de categorías y materiales...")
        
        # Verificar si ya existen datos
        existing_categorias = db.query(Categoria).count()
        if existing_categorias > 0:
            print(f"ℹ️  Ya existen {existing_categorias} categorías. Se agregarán las nuevas sin duplicar.")
        
        # Crear Categorías
        categorias_data = [
            {
                "codigo": "PISOS",
                "nombre": "Pisos y Revestimientos",
                "descripcion": "Materiales para pisos interiores y exteriores",
                "imagen_url": "https://images.unsplash.com/photo-1615875474908-d77877a00e6f?w=400&h=300&fit=crop"
            },
            {
                "codigo": "PAREDES",
                "nombre": "Acabados de Paredes",
                "descripcion": "Pinturas, papeles tapiz y revestimientos de pared",
                "imagen_url": "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=400&h=300&fit=crop"
            },
            {
                "codigo": "MADERA",
                "nombre": "Maderas y Laminados",
                "descripcion": "Pisos y revestimientos de madera",
                "imagen_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop"
            },
            {
                "codigo": "PIEDRA",
                "nombre": "Piedras Naturales",
                "descripcion": "Mármol, granito y piedras decorativas",
                "imagen_url": "https://images.unsplash.com/photo-1615971677499-5467cbab01c0?w=400&h=300&fit=crop"
            },
        ]
        
        categorias = []
        for cat_data in categorias_data:
            # Verificar si ya existe
            existing = db.query(Categoria).filter(Categoria.codigo == cat_data["codigo"]).first()
            if not existing:
                categoria = Categoria(**cat_data)
                db.add(categoria)
                categorias.append(categoria)
            else:
                print(f"  ⏭️  Categoría {cat_data['codigo']} ya existe, usando la existente")
                categorias.append(existing)
        
        db.commit()
        print(f"✅ {len(categorias)} categorías creadas")
        
        # Crear Materiales
        materiales_data = [
            # Pisos y Revestimientos
            {
                "codigo": "CER-001",
                "nombre": "Cerámica Blanca Mate 30x30",
                "descripcion": "Cerámica para pisos de alto tráfico, acabado mate",
                "precio_base": 25.50,
                "unidad_medida": "m2",
                "imagen_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=400&h=400&fit=crop",
                "categoria_id": categorias[0].id
            },
            {
                "codigo": "CER-002",
                "nombre": "Cerámica Gris Oscuro 60x60",
                "descripcion": "Cerámica moderna, diseño minimalista",
                "precio_base": 42.00,
                "unidad_medida": "m2",
                "imagen_url": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=400&h=400&fit=crop",
                "categoria_id": categorias[0].id
            },
            {
                "codigo": "POR-001",
                "nombre": "Porcelanato Símil Madera Clara",
                "descripcion": "Porcelanato imitación madera, ideal para salones",
                "precio_base": 55.00,
                "unidad_medida": "m2",
                "imagen_url": "https://images.unsplash.com/photo-1615876234886-fd9a39fda97f?w=400&h=400&fit=crop",
                "categoria_id": categorias[0].id
            },
            
            # Acabados de Paredes
            {
                "codigo": "PIN-001",
                "nombre": "Pintura Latex Blanco Nieve",
                "descripcion": "Pintura lavable para interiores, acabado satinado",
                "precio_base": 35.00,
                "unidad_medida": "m2",
                "imagen_url": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=400&h=400&fit=crop",
                "categoria_id": categorias[1].id
            },
            {
                "codigo": "PIN-002",
                "nombre": "Pintura Latex Gris Perla",
                "descripcion": "Tonalidad moderna, fácil aplicación",
                "precio_base": 38.00,
                "unidad_medida": "m2",
                "imagen_url": "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=400&h=400&fit=crop",
                "categoria_id": categorias[1].id
            },
            {
                "codigo": "REV-001",
                "nombre": "Revestimiento Texturado Beige",
                "descripcion": "Acabado con relieve 3D para paredes decorativas",
                "precio_base": 65.00,
                "unidad_medida": "m2",
                "imagen_url": "https://images.unsplash.com/photo-1604580864964-0908f1b2ee8a?w=400&h=400&fit=crop",
                "categoria_id": categorias[1].id
            },
            
            # Maderas y Laminados
            {
                "codigo": "MAD-001",
                "nombre": "Piso Laminado Roble Natural",
                "descripcion": "Laminado AC4, resistente al agua",
                "precio_base": 48.00,
                "unidad_medida": "m2",
                "imagen_url": "https://images.unsplash.com/photo-1615876234886-fd9a39fda97f?w=400&h=400&fit=crop",
                "categoria_id": categorias[2].id
            },
            {
                "codigo": "MAD-002",
                "nombre": "Piso Laminado Nogal Oscuro",
                "descripcion": "Tonalidad oscura elegante, alta durabilidad",
                "precio_base": 52.00,
                "unidad_medida": "m2",
                "imagen_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=400&fit=crop",
                "categoria_id": categorias[2].id
            },
            {
                "codigo": "MAD-003",
                "nombre": "Machimbre Pino Tea",
                "descripcion": "Madera natural para revestimiento de paredes",
                "precio_base": 62.00,
                "unidad_medida": "m2",
                "imagen_url": "https://images.unsplash.com/photo-1615877411175-13f5f0f19c4d?w=400&h=400&fit=crop",
                "categoria_id": categorias[2].id
            },
            
            # Piedras Naturales
            {
                "codigo": "MAR-001",
                "nombre": "Mármol Carrara Blanco",
                "descripcion": "Mármol italiano de primera calidad",
                "precio_base": 120.00,
                "unidad_medida": "m2",
                "imagen_url": "https://images.unsplash.com/photo-1615971677499-5467cbab01c0?w=400&h=400&fit=crop",
                "categoria_id": categorias[3].id
            },
            {
                "codigo": "GRA-001",
                "nombre": "Granito Negro Absoluto",
                "descripcion": "Granito pulido de alto brillo",
                "precio_base": 95.00,
                "unidad_medida": "m2",
                "imagen_url": "https://images.unsplash.com/photo-1615971677499-5467cbab01c0?w=400&h=400&fit=crop",
                "categoria_id": categorias[3].id
            },
            {
                "codigo": "PIE-001",
                "nombre": "Piedra Laja Gris",
                "descripcion": "Piedra natural para exteriores y jardines",
                "precio_base": 45.00,
                "unidad_medida": "m2",
                "imagen_url": "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=400&h=400&fit=crop",
                "categoria_id": categorias[3].id
            },
        ]
        
        materiales = []
        for mat_data in materiales_data:
            # Verificar si ya existe
            existing = db.query(Material).filter(Material.codigo == mat_data["codigo"]).first()
            if not existing:
                material = Material(**mat_data)
                db.add(material)
                materiales.append(material)
            else:
                print(f"  ⏭️  Material {mat_data['codigo']} ya existe")
                materiales.append(existing)
        
        db.commit()
        print(f"✅ {len(materiales)} materiales creados")
        
        # Resumen
        print("\n" + "="*60)
        print("📊 RESUMEN DE DATOS CREADOS")
        print("="*60)
        for categoria in categorias:
            count = len([m for m in materiales if m.categoria_id == categoria.id])
            print(f"  📁 {categoria.nombre}: {count} materiales")
        
        print("\n✨ Seed completado exitosamente!")
        print("\n💡 Puedes usar estos materiales en el frontend")
        print("   URL del API: http://localhost:8000/materiales/")
        print("   URL Swagger: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error durante el seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()
