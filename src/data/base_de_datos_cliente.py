import sqlite3
import os
import sys
import shutil

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
nombre_bd = os.path.join(BASE_DIR, "revite_cliente.db")

def preparar_base_de_datos():
    if os.path.exists(nombre_bd) or not getattr(sys, "frozen", False):
        return

    plantilla = os.path.join(getattr(sys, "_MEIPASS", BASE_DIR), "revite_cliente.db")
    if os.path.exists(plantilla):
        shutil.copyfile(plantilla, nombre_bd)

def foto_es_unica_en_clientes(cursor):
    cursor.execute("PRAGMA index_list(clientes)")
    for indice in cursor.fetchall():
        nombre_indice = indice[1]
        es_unico = indice[2]
        if not es_unico:
            continue

        cursor.execute(f"PRAGMA index_info({nombre_indice})")
        columnas = [columna[2] for columna in cursor.fetchall()]
        if columnas == ["foto"]:
            return True
    return False

def quitar_unico_foto_clientes(conexion, cursor):
    if not foto_es_unica_en_clientes(cursor):
        return

    cursor.execute("ALTER TABLE clientes RENAME TO clientes_anterior")
    cursor.execute('''
        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            foto TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rating REAL DEFAULT 0,
            feedback TEXT DEFAULT ''
            )
            ''')
    cursor.execute('''
        INSERT OR IGNORE INTO clientes (
            id,nombre,apellido,cedula,foto,fecha_registro,rating,feedback
        )
        SELECT id,nombre,apellido,cedula,foto,fecha_registro,rating,feedback
        FROM clientes_anterior
            ''')
    cursor.execute("DROP TABLE clientes_anterior")
    conexion.commit()

def migrar_base_de_datos_cliente():
    preparar_base_de_datos()
    conexion = sqlite3.connect(nombre_bd)
    cursor = conexion.cursor()
    cursor.execute("PRAGMA table_info(clientes)")
    columnas = [columna[1] for columna in cursor.fetchall()]
    nuevas_columnas = {
        "rating": "REAL DEFAULT 0",
        "feedback": "TEXT DEFAULT ''"
    }
    for columna, tipo in nuevas_columnas.items():
        if columna not in columnas:
            cursor.execute(f"ALTER TABLE clientes ADD COLUMN {columna} {tipo}")
    conexion.commit()
    quitar_unico_foto_clientes(conexion, cursor)
    conexion.close()

def crear_base_de_datos_cliente():
    try:
        preparar_base_de_datos()
        conexion = sqlite3.connect(nombre_bd)
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                cedula TEXT UNIQUE NOT NULL,
                foto TEXT NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                rating REAL DEFAULT 0,
                feedback TEXT DEFAULT ''
                )
                ''')
        conexion.commit()
        migrar_base_de_datos_cliente()
        print(f"Base de datos {nombre_bd} y tabla 'clientes' creadas con exito")
    except sqlite3.Error as e:
        print(f"error al conectar error: {e}")
    finally:
        if conexion:
            conexion.close()


def insertar_cliente(nombre,apellido,cedula,foto):
    conexion = None
    try:
        cedula = str(cedula).strip()
        crear_base_de_datos_cliente()
        conexion = sqlite3.connect(nombre_bd)
        cursor = conexion.cursor()
        # Usamos '?' como placeholders para las variables
        sql = "INSERT OR IGNORE INTO clientes (nombre,apellido,cedula,foto) VALUES (?, ?, ?, ?)"
        valores = (nombre,apellido,cedula,foto)
        cursor.execute(sql,valores)
        conexion.commit()
        print(f"Usuario {nombre} guardado correctamente")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: la cedula {cedula} ya esta registrada")
        return False
    except sqlite3.Error as e:
        print(f"Error al insertar los datos:{e}")
        return False
    finally:
        if conexion:
            conexion.close()
def consultar_clientes():
    clientes = []
    conexion = None
    try:
        crear_base_de_datos_cliente()
        conexion = sqlite3.connect(nombre_bd)
        cursor = conexion.cursor()
        sql = "SELECT id,nombre,apellido,cedula,foto,fecha_registro,rating,feedback FROM clientes"
        cursor.execute(sql)
        clientes = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al consultar {e}")
    finally:
        if conexion:
            conexion.close()
    return clientes

def actualizar_rating_cliente(cedula, rating, feedback):
    cedula = str(cedula).strip()
    conexion = sqlite3.connect(nombre_bd)
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE clientes SET rating = ?, feedback = ? WHERE cedula = ?",
        (rating, feedback, cedula)
    )
    conexion.commit()
    conexion.close()


"""
    insertar_usuario("Santiago", "santiagomoralesmorales08@gmail.com", "1070600370", "3133017419")
    insertar_usuario("Nicolas", "nicolasmoralesmorales08@gmail.com", "1070600371", "3133017415")
    insertar_usuario("Pepo", "pedrosanchez@gmail.com", "1070600372", "3133017413")"""
#ACA CREAMOS LA TABLA EL ID SIEMPRE VA ES PARA QUE ME ORGANICE LA TABLA CON ELA UTOICREMENT PARA QUE SE
#ME INCREMENTE MEDIANTE LOS USUARIOS QUE LLEGUEN
# Y LA FECHA DE REGISTRO ES LA FECHA DE LO QUE SE ME CREARON
