# database_setup.py
import sqlite3

def crear_conexion(db_file):
    """Crea una conexión a la base de datos SQLite especificada por db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Conexión exitosa a la base de datos: {db_file}")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def crear_tabla(conn, sql_crear_tabla):
    """Crea una tabla usando la sentencia SQL proporcionada."""
    try:
        c = conn.cursor()
        c.execute(sql_crear_tabla)
    except sqlite3.Error as e:
        print(e)

def main():
    """Función principal para crear la base de datos y las tablas."""
    database = "troquelgest.db"

    # Sentencias SQL para crear cada tabla
    sql_crear_tabla_materiales = """
    CREATE TABLE IF NOT EXISTS Materiales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_material TEXT NOT NULL CHECK(tipo_material IN ('fleje', 'madera', 'goma')),
        subtipo TEXT NOT NULL,
        precio_coste REAL NOT NULL,
        unidad TEXT NOT NULL CHECK(unidad IN ('m', 'm2'))
    );
    """

    sql_crear_tabla_maquinaria = """
    CREATE TABLE IF NOT EXISTS Maquinaria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_maquina TEXT NOT NULL UNIQUE,
        coste_por_hora REAL NOT NULL
    );
    """

    sql_crear_tabla_personal = """
    CREATE TABLE IF NOT EXISTS RolesPersonal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_rol TEXT NOT NULL UNIQUE,
        coste_por_hora REAL NOT NULL
    );
    """

    sql_crear_tabla_clientes = """
    CREATE TABLE IF NOT EXISTS Clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        empresa TEXT,
        cif TEXT UNIQUE,
        direccion TEXT,
        telefono TEXT,
        email TEXT,
        porcentaje_beneficio_defecto REAL NOT NULL DEFAULT 25.0
    );
    """

    # Nuevas tablas para presupuestos
    sql_crear_tabla_presupuestos = """
    CREATE TABLE IF NOT EXISTS Presupuestos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        fecha_creacion TEXT NOT NULL,
        nombre_proyecto TEXT NOT NULL,
        ruta_dxf TEXT,
        estado TEXT,
        FOREIGN KEY (cliente_id) REFERENCES Clientes (id)
    );
    """

    sql_crear_tabla_detalle = """
    CREATE TABLE IF NOT EXISTS DetallePresupuesto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        presupuesto_id INTEGER NOT NULL,
        concepto TEXT NOT NULL,
        cantidad REAL,
        coste_unitario REAL,
        coste_total_linea REAL,
        FOREIGN KEY (presupuesto_id) REFERENCES Presupuestos (id)
    );
    """

    # Crear la conexión a la base de datos
    conn = crear_conexion(database)

    # Crear las tablas
    if conn is not None:
        crear_tabla(conn, sql_crear_tabla_materiales)
        print("Tabla 'Materiales' creada (si no existía).")

        crear_tabla(conn, sql_crear_tabla_maquinaria)
        print("Tabla 'Maquinaria' creada (si no existía).")

        crear_tabla(conn, sql_crear_tabla_personal)
        print("Tabla 'RolesPersonal' creada (si no existía).")

        crear_tabla(conn, sql_crear_tabla_clientes)
        print("Tabla 'Clientes' creada (si no existía).")

        crear_tabla(conn, sql_crear_tabla_presupuestos)
        print("Tabla 'Presupuestos' creada (si no existía).")

        crear_tabla(conn, sql_crear_tabla_detalle)
        print("Tabla 'DetallePresupuesto' creada (si no existía).")

        conn.close()
        print("Conexión a la base de datos cerrada.")
    else:
        print("Error: No se pudo crear la conexión a la base de datos.")

if __name__ == '__main__':
    main()