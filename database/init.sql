-- database/init.sql
-- Script de inicialización automática para PostgreSQL
-- Solo incluye las tablas del módulo de buses que han sido probadas

-- Crear tabla de estados de buses
CREATE TABLE estados_buses (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    permite_asignacion BOOLEAN DEFAULT FALSE,
    es_activo BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT NOW() NOT NULL
);

-- Crear tabla de tipos de combustible
CREATE TABLE tipos_combustible (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    factor_emision DECIMAL(8,4),
    es_activo BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT NOW() NOT NULL
);

-- Crear tabla de buses con foreign keys funcionando
CREATE TABLE buses (
    id SERIAL PRIMARY KEY,
    patente VARCHAR(8) UNIQUE NOT NULL,
    codigo_interno VARCHAR(50) UNIQUE,
    marca VARCHAR(100) NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    año INTEGER NOT NULL,
    numero_chasis VARCHAR(17) UNIQUE,
    numero_motor VARCHAR(100),
    tipo_combustible_id INTEGER NOT NULL REFERENCES tipos_combustible(id),
    estado_id INTEGER NOT NULL REFERENCES estados_buses(id),
    capacidad_sentados INTEGER NOT NULL,
    kilometraje_actual INTEGER DEFAULT 0,
    fecha_compra TIMESTAMP,
    precio_compra DECIMAL(12,2),
    observaciones TEXT,
    esta_activo BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT NOW() NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT NOW() NOT NULL
);

-- Insertar datos iniciales de estados (probados)
INSERT INTO estados_buses (codigo, nombre, descripcion, permite_asignacion) VALUES
('ACT', 'Activo', 'Bus operativo y disponible', true),
('MAN', 'Mantenimiento', 'Bus en mantenimiento programado', false),
('FS', 'Fuera de Servicio', 'Bus temporalmente fuera de servicio', false),
('RET', 'Retirado', 'Bus retirado de la flota', false);

-- Insertar datos iniciales de tipos de combustible (probados)
INSERT INTO tipos_combustible (codigo, nombre, factor_emision) VALUES
('DSL', 'Diesel', 2.6391),
('GAS', 'Gasolina', 2.3240),
('ELE', 'Eléctrico', 0.0000),
('HIB', 'Híbrido', 1.8000),
('GNV', 'Gas Natural', 2.0000);

-- Insertar bus de ejemplo (probado con CRUD completo)
INSERT INTO buses (patente, marca, modelo, año, tipo_combustible_id, estado_id, capacidad_sentados, kilometraje_actual, observaciones) 
VALUES ('DEMO01', 'Mercedes', 'OH-1628', 2020, 1, 1, 45, 0, 'Bus de ejemplo para testing');

-- Índices para optimización (probados)
CREATE INDEX idx_buses_patente ON buses(patente);
CREATE INDEX idx_buses_estado ON buses(estado_id);
CREATE INDEX idx_buses_activo ON buses(esta_activo);