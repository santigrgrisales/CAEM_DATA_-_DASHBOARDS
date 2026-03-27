CREATE SCHEMA IF NOT EXISTS caem_clean;

-- ---------------------------------------
CREATE TABLE caem_clean.dim_municipios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_dane VARCHAR(5) UNIQUE NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    departamento VARCHAR(150),
    nombre_normalizado VARCHAR(150) NOT NULL
);

-- 💡 Notas:
-- codigo_dane = llave real
-- nombre_normalizado = sin tildes, uppercase (para matching)

-- ---------------------------------------
CREATE TABLE caem_clean.dim_entidades ( 
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_normalizado VARCHAR(255) NOT NULL,
    nombre_oficial VARCHAR(255),
    tipo VARCHAR(50), -- judicial / publica / otra
    fuente VARCHAR(100), -- gov, rama_judicial
    UNIQUE(nombre_normalizado)
);

-- ---------------------------------------
CREATE TABLE caem_clean.mapping_municipios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    valor_original VARCHAR(255),
    valor_normalizado VARCHAR(150),
    codigo_dane VARCHAR(5),
    metodo VARCHAR(50), -- exact / fuzzy
    confianza NUMERIC(5,2),
    revisado BOOLEAN DEFAULT FALSE
);

-- ---------------------------------------
CREATE TABLE caem_clean.mapping_entidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    valor_original VARCHAR(255),
    entidad_id INT,
    metodo VARCHAR(50),
    confianza NUMERIC(5,2),
    revisado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (entidad_id) REFERENCES caem_clean.dim_entidades(id)
);

-- ---------------------------------------
CREATE TABLE caem_clean.embargos_normalizado (
    id BIGINT PRIMARY KEY,
    municipio_id INT,
    entidad_id INT AUTO_INCREMENT,
    entidad_bancaria_id INT,
    monto NUMERIC,
    fecha_oficio DATE,
    fecha_recibido DATE,

    FOREIGN KEY (municipio_id) REFERENCES caem_clean.dim_municipios(id),
    FOREIGN KEY (entidad_id) REFERENCES caem_clean.dim_entidades(id)
);
