-- =============================================
-- LIMPIEZA DE BASE DE DATOS
-- =============================================

-- 1. ELIMINAR VISTAS (si existen)
DROP VIEW IF EXISTS feed_noticias CASCADE;

-- 2. ELIMINAR FUNCIONES / PROCEDIMIENTOS
DROP FUNCTION IF EXISTS crear_amistad(INT, INT) CASCADE;

-- 3. ELIMINAR TABLAS (orden correcto por FKs)
DROP TABLE IF EXISTS comentarios CASCADE;
DROP TABLE IF EXISTS publicaciones CASCADE;
DROP TABLE IF EXISTS amistades CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

-- =============================================
-- TABLAS PRINCIPALES
-- =============================================

-- 1. Tabla de Usuarios
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    fecha_registro DATE DEFAULT CURRENT_DATE,
    pais VARCHAR(50)
);

-- 2. Tabla de Publicaciones
CREATE TABLE publicaciones (
    id_publicacion SERIAL PRIMARY KEY,
    texto_contenido TEXT,
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes_contador INT DEFAULT 0,
    autor_id INT NOT NULL  -- FK luego
);

-- 3. Tabla de Comentarios
CREATE TABLE comentarios (
    id_comentario SERIAL PRIMARY KEY,
    contenido VARCHAR(255),
    fecha_comentario TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT NOT NULL,         -- FK luego
    publicacion_id INT NOT NULL      -- FK luego
);

-- 4. Tabla de Amistades
CREATE TABLE amistades (
    id_amistad SERIAL PRIMARY KEY,
    fecha_amistad DATE DEFAULT CURRENT_DATE,
    estado VARCHAR(20),
    usuario_solicitante_id INT NOT NULL, -- FK luego
    usuario_receptor_id INT NOT NULL     -- FK luego
);

-- =============================================
-- DATOS SEMILLA
-- =============================================

INSERT INTO usuarios (nombre, email, pais) VALUES 
('Ana Garcia', 'ana@mail.com', 'Colombia'),
('Carlos Perez', 'carlos@mail.com', 'Mexico'),
('Beatriz Lopez', 'bea@mail.com', 'Argentina'),
('David Ruiz', 'david@mail.com', 'Colombia');

INSERT INTO publicaciones (texto_contenido, autor_id) VALUES 
('Hola mundo, este es mi primer post', 1),
('Me encanta el café de Colombia', 2),
('Buscando recomendaciones de libros', 1);

INSERT INTO amistades (usuario_solicitante_id, usuario_receptor_id, estado) VALUES 
(1, 2, 'ACEPTADA'),
(2, 3, 'ACEPTADA'),
(3, 4, 'ACEPTADA');

-- =============================================
-- FOREIGN KEYS QUE FALTABAN
-- =============================================

ALTER TABLE publicaciones
ADD CONSTRAINT fk_publicaciones_autor
FOREIGN KEY (autor_id)
REFERENCES usuarios(id_usuario)
ON DELETE CASCADE;

ALTER TABLE comentarios
ADD CONSTRAINT fk_comentarios_usuario
FOREIGN KEY (usuario_id)
REFERENCES usuarios(id_usuario)
ON DELETE CASCADE;

ALTER TABLE comentarios
ADD CONSTRAINT fk_comentarios_publicacion
FOREIGN KEY (publicacion_id)
REFERENCES publicaciones(id_publicacion)
ON DELETE CASCADE;

ALTER TABLE amistades
ADD CONSTRAINT fk_amistades_solicitante
FOREIGN KEY (usuario_solicitante_id)
REFERENCES usuarios(id_usuario)
ON DELETE CASCADE;

ALTER TABLE amistades
ADD CONSTRAINT fk_amistades_receptor
FOREIGN KEY (usuario_receptor_id)
REFERENCES usuarios(id_usuario)
ON DELETE CASCADE;

-- =============================================
-- RESTRICCIÓN CHECK (no amigo de sí mismo)
-- =============================================

ALTER TABLE amistades
ADD CONSTRAINT chk_amistad_no_mismo_usuario
CHECK (usuario_solicitante_id <> usuario_receptor_id);

-- =============================================
-- 20 REGISTROS EXTRA DE AMISTADES
-- =============================================

INSERT INTO amistades (usuario_solicitante_id, usuario_receptor_id, estado) VALUES
(1, 3, 'ACEPTADA'),
(1, 4, 'PENDIENTE'),
(2, 1, 'PENDIENTE'),
(2, 4, 'ACEPTADA'),
(3, 1, 'ACEPTADA'),
(4, 1, 'PENDIENTE'),
(3, 2, 'ACEPTADA'),
(4, 2, 'ACEPTADA'),
(4, 3, 'ACEPTADA'),
(1, 2, 'PENDIENTE'),
(2, 3, 'PENDIENTE'),
(3, 4, 'PENDIENTE'),
(4, 1, 'ACEPTADA'),
(1, 4, 'ACEPTADA'),
(2, 4, 'PENDIENTE'),
(3, 1, 'PENDIENTE'),
(4, 3, 'PENDIENTE'),
(2, 1, 'ACEPTADA'),
(3, 2, 'PENDIENTE'),
(4, 2, 'PENDIENTE');

-- ============================================================
-- 1. PROCEDIMIENTO ALMACENADO: crear_amistad(id1, id2)
-- ============================================================

CREATE OR REPLACE FUNCTION crear_amistad(id1 INT, id2 INT)
RETURNS TEXT AS $$
DECLARE
    existe_amistad INT;
BEGIN
    -- Verificar si ya existe amistad entre id1 y id2 (en cualquier dirección)
    SELECT COUNT(*) INTO existe_amistad
    FROM amistades
    WHERE (usuario_solicitante_id = id1 AND usuario_receptor_id = id2)
       OR (usuario_solicitante_id = id2 AND usuario_receptor_id = id1);

    -- Si ya existe, devolver mensaje sin insertar
    IF existe_amistad > 0 THEN
        RETURN 'Ya existe una relación de amistad entre esos usuarios.';
    END IF;

    -- Insertar la nueva amistad
    INSERT INTO amistades (usuario_solicitante_id, usuario_receptor_id, estado)
    VALUES (id1, id2, 'PENDIENTE');

    RETURN 'Amistad creada correctamente.';
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 2. VISTA: feed_noticias
-- ============================================================

CREATE OR REPLACE VIEW feed_noticias AS
SELECT 
    u.nombre AS usuario,
    p.texto_contenido AS contenido,
    p.fecha_publicacion AS fecha,
    COUNT(c.id_comentario) AS total_comentarios
FROM publicaciones p
JOIN usuarios u ON u.id_usuario = p.autor_id
LEFT JOIN comentarios c ON c.publicacion_id = p.id_publicacion
GROUP BY u.nombre, p.texto_contenido, p.fecha_publicacion
ORDER BY p.fecha_publicacion DESC;
