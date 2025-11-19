-- Crear tabla de cotizaciones (PostgreSQL)
CREATE TABLE IF NOT EXISTS cotizaciones (
    id SERIAL PRIMARY KEY,
    plano_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    cliente_nombre VARCHAR(255) NOT NULL,
    cliente_email VARCHAR(255) NOT NULL,
    cliente_telefono VARCHAR(50),
    descripcion TEXT,
    materiales JSONB NOT NULL,
    subtotal REAL NOT NULL DEFAULT 0.0,
    iva REAL NOT NULL DEFAULT 0.0,
    total REAL NOT NULL DEFAULT 0.0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (plano_id) REFERENCES plano(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Crear índices para mejorar el rendimiento de las consultas
CREATE INDEX IF NOT EXISTS idx_cotizaciones_plano_id ON cotizaciones(plano_id);
CREATE INDEX IF NOT EXISTS idx_cotizaciones_usuario_id ON cotizaciones(usuario_id);
CREATE INDEX IF NOT EXISTS idx_cotizaciones_fecha_creacion ON cotizaciones(fecha_creacion);

-- Función para actualizar automáticamente fecha_actualizacion
CREATE OR REPLACE FUNCTION update_cotizaciones_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar automáticamente fecha_actualizacion
DROP TRIGGER IF EXISTS update_cotizaciones_fecha_actualizacion ON cotizaciones;
CREATE TRIGGER update_cotizaciones_fecha_actualizacion
BEFORE UPDATE ON cotizaciones
FOR EACH ROW
EXECUTE FUNCTION update_cotizaciones_fecha_actualizacion();