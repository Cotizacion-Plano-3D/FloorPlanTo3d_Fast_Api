# Implementación de Sistema de Cotizaciones y Presupuestos

## 📋 Resumen

Se ha implementado un sistema completo de cotizaciones y presupuestos que incluye:

1. **Extracción automática de medidas** de los planos (área, perímetro, conteos de elementos)
2. **Endpoints de API** para crear y gestionar cotizaciones
3. **Interfaz de usuario** para generar presupuestos con materiales
4. **Botones de acceso rápido** en múltiples lugares del sistema

## 🗄️ Cambios en Base de Datos

### Nueva Tabla: `cotizaciones`

```sql
CREATE TABLE cotizaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plano_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    cliente_nombre VARCHAR(255) NOT NULL,
    cliente_email VARCHAR(255) NOT NULL,
    cliente_telefono VARCHAR(50),
    descripcion TEXT,
    materiales JSON NOT NULL,
    subtotal REAL NOT NULL DEFAULT 0.0,
    iva REAL NOT NULL DEFAULT 0.0,
    total REAL NOT NULL DEFAULT 0.0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (plano_id) REFERENCES plano(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

### Ejecutar Migración

```bash
# Opción 1: Desde Python
cd FloorPlanTo3d_Fast_Api
python -c "from database import engine; from models import Base, Cotizacion; Base.metadata.create_all(bind=engine)"

# Opción 2: Usando SQLite directamente (si usas SQLite)
sqlite3 database.db < migrations/create_cotizaciones_table.sql
```

### Campo Actualizado: `medidas_extraidas`

El campo `medidas_extraidas` en la tabla `planos` ahora se llena automáticamente con:

```json
{
  "area_total": 150.5,
  "area_paredes": 120.0,
  "area_ventanas": 15.5,
  "area_puertas": 10.0,
  "perimetro_total": 45.0,
  "num_paredes": 8,
  "num_ventanas": 4,
  "num_puertas": 2,
  "bounds": {
    "ancho": 12.5,
    "alto": 10.0
  },
  "objetos": [
    {
      "id": "wall_1",
      "tipo": "wall",
      "ancho": 5.0,
      "alto": 3.0,
      "profundidad": 0.2,
      "area": 15.0,
      "posicion": { "x": 2.5, "y": 1.5, "z": 0 }
    }
  ],
  "total_objetos": 14
}
```

## 🔧 Archivos Nuevos Backend

### Modelos
- `models/cotizacion.py` - Modelo SQLAlchemy para cotizaciones

### Schemas
- `schemas/cotizacion_schemas.py` - Schemas Pydantic para validación

### Repositorios
- `repositories/cotizacion_repository.py` - Operaciones de base de datos

### Routers
- `routers/cotizacion.py` - Endpoints REST API

### Servicios
- `services/plano_service.py` - Método `_extract_measurements()` agregado

### Migraciones
- `migrations/create_cotizaciones_table.sql` - Script SQL

## 🎨 Archivos Nuevos Frontend

### Componentes
- `components/quotation-form.tsx` - Formulario de información del cliente
- `components/quotation-panel.tsx` - Panel de selección de materiales
- `components/quotation-summary.tsx` - Resumen de costos

### Páginas
- `app/quotation/[planoId]/page.tsx` - Página principal de cotización

### Tipos
- `types/api.ts` - Tipos TypeScript agregados para `Cotizacion` y `MaterialCotizacion`

### API Cliente
- `lib/api.ts` - Métodos agregados:
  - `createCotizacion()`
  - `getCotizacion()`
  - `getCotizacionesByPlano()`
  - `getCotizacionesUsuario()`
  - `deleteCotizacion()`

## 📍 Botones de Acceso Agregados

1. **`floor-plan-3d-viewer.tsx`**
   - Botón verde "Crear Cotización" en la parte superior izquierda del visor 3D

2. **`floor-plan-gallery.tsx`**
   - Botón "Cotización" debajo de cada tarjeta de plano en la galería

3. **`floor-plan-preview.tsx`**
   - Botón "Cotizar" en la esquina superior derecha del preview 3D

## 🚀 Endpoints API

### Cotizaciones

```
POST   /cotizaciones/              - Crear nueva cotización
GET    /cotizaciones/              - Obtener todas las cotizaciones del usuario
GET    /cotizaciones/{id}          - Obtener cotización específica
GET    /cotizaciones/plano/{id}    - Obtener cotizaciones de un plano
DELETE /cotizaciones/{id}          - Eliminar cotización
```

### Ejemplo de Uso

```typescript
// Crear cotización
const cotizacion = await apiClient.createCotizacion({
  plano_id: 1,
  cliente_nombre: "Juan Pérez",
  cliente_email: "juan@example.com",
  descripcion: "Renovación de departamento",
  materiales: [
    {
      material_id: 1,
      nombre: "Porcelanato Premium",
      categoria: "Pisos",
      cantidad: 50,
      precio_unitario: 45.0,
      subtotal: 2250.0
    }
  ],
  subtotal: 2250.0,
  iva: 427.5,
  total: 2677.5
})
```

## 🔄 Flujo de Usuario

1. Usuario sube un plano (se extraen medidas automáticamente)
2. Usuario visualiza el plano en 3D
3. Usuario hace clic en "Crear Cotización"
4. Sistema carga materiales disponibles de la base de datos
5. Usuario selecciona materiales y cantidades
6. Usuario ingresa información del cliente
7. Sistema calcula subtotal, IVA (19%) y total
8. Usuario genera la cotización
9. Sistema guarda la cotización en la base de datos

## ✅ Funcionalidades Implementadas

- ✅ Extracción automática de medidas de planos
- ✅ Gestión completa de cotizaciones (CRUD)
- ✅ Selección de materiales con descuentos
- ✅ Cálculo automático de totales (subtotal + IVA)
- ✅ Validación de campos requeridos
- ✅ Interfaz responsiva (móvil y desktop)
- ✅ Integración con visor 3D de planos
- ✅ Botones de acceso rápido en múltiples vistas

## 🔜 Mejoras Futuras Sugeridas

1. **Exportación a PDF** de cotizaciones
2. **Envío por email** de cotizaciones al cliente
3. **Plantillas** de cotización personalizables
4. **Historial** de cotizaciones por plano
5. **Comparación** de múltiples cotizaciones
6. **Seguimiento** de estado (pendiente, aprobada, rechazada)
7. **Firma digital** del cliente
8. **Conversión** a orden de compra

## 📝 Notas Importantes

- El sistema usa **IVA del 19%** por defecto (configurable en el código)
- Las medidas se extraen en **metros** y **metros cuadrados**
- Los materiales se cargan desde la tabla `material` existente
- Las cotizaciones se asocian al usuario y al plano
- El sistema soporta **múltiples cotizaciones por plano**

## 🐛 Debugging

Si hay problemas:

1. Verificar que la tabla `cotizaciones` existe
2. Verificar que los modelos están importados en `models/__init__.py`
3. Verificar que el router está registrado en `main.py`
4. Verificar que hay materiales en la base de datos
5. Revisar logs del backend para errores de extracción de medidas

