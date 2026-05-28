import sqlite3
import os
import sys
import shutil

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
nombre_bd = os.path.join(BASE_DIR, "revite_reserva.db")

def preparar_base_de_datos():
    if os.path.exists(nombre_bd) or not getattr(sys, "frozen", False):
        return

    plantilla = os.path.join(getattr(sys, "_MEIPASS", BASE_DIR), "revite_reserva.db")
    if os.path.exists(plantilla):
        shutil.copyfile(plantilla, nombre_bd)

def cedula_es_unica_en_reservas(cursor):
    cursor.execute("PRAGMA index_list(reservas)")
    for indice in cursor.fetchall():
        nombre_indice = indice[1]
        es_unico = indice[2]
        if not es_unico:
            continue

        cursor.execute(f"PRAGMA index_info({nombre_indice})")
        columnas = [columna[2] for columna in cursor.fetchall()]
        if columnas == ["cedula"]:
            return True
    return False

def quitar_unico_cedula_reservas(conexion, cursor):
    if not cedula_es_unica_en_reservas(cursor):
        return

    cursor.execute("ALTER TABLE reservas RENAME TO reservas_anterior")
    cursor.execute('''
        CREATE TABLE reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            cedula TEXT NOT NULL,
            foto TEXT NOT NULL,
            hora TEXT NOT NULL,
            sector TEXT NOT NULL,
            taxi TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado TEXT DEFAULT 'pendiente',
            conductor TEXT DEFAULT '',
            metodo_pago TEXT DEFAULT '',
            calificacion_cliente INTEGER DEFAULT 0,
            feedback_cliente TEXT DEFAULT '',
            calificacion_dueno INTEGER DEFAULT 0,
            feedback_dueno TEXT DEFAULT '',
            venta_valor REAL DEFAULT 0
            )
            ''')
    cursor.execute('''
        INSERT INTO reservas (
            id,nombre,apellido,cedula,foto,hora,sector,taxi,fecha_registro,
            estado,conductor,metodo_pago,calificacion_cliente,feedback_cliente,
            calificacion_dueno,feedback_dueno,venta_valor
        )
        SELECT
            id,nombre,apellido,cedula,foto,hora,sector,taxi,fecha_registro,
            estado,conductor,metodo_pago,calificacion_cliente,feedback_cliente,
            calificacion_dueno,feedback_dueno,venta_valor
        FROM reservas_anterior
            ''')
    cursor.execute("DROP TABLE reservas_anterior")
    conexion.commit()

def migrar_base_de_datos_reservas():
    preparar_base_de_datos()
    conexion = sqlite3.connect(nombre_bd)
    cursor = conexion.cursor()
    cursor.execute("PRAGMA table_info(reservas)")
    columnas = [columna[1] for columna in cursor.fetchall()]
    nuevas_columnas = {
        "estado": "TEXT DEFAULT 'pendiente'",
        "conductor": "TEXT DEFAULT ''",
        "metodo_pago": "TEXT DEFAULT ''",
        "calificacion_cliente": "INTEGER DEFAULT 0",
        "feedback_cliente": "TEXT DEFAULT ''",
        "calificacion_dueno": "INTEGER DEFAULT 0",
        "feedback_dueno": "TEXT DEFAULT ''",
        "venta_valor": "REAL DEFAULT 0"
    }
    for columna, tipo in nuevas_columnas.items():
        if columna not in columnas:
            cursor.execute(f"ALTER TABLE reservas ADD COLUMN {columna} {tipo}")
    conexion.commit()
    quitar_unico_cedula_reservas(conexion, cursor)
    conexion.close()

def crear_base_de_datos_reservas():
    try:
        preparar_base_de_datos()
        conexion = sqlite3.connect(nombre_bd)
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                cedula TEXT NOT NULL,
                foto TEXT NOT NULL,
                hora TEXT NOT NULL,
                sector TEXT NOT NULL,
                taxi TEXT NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estado TEXT DEFAULT 'pendiente',
                conductor TEXT DEFAULT '',
                metodo_pago TEXT DEFAULT '',
                calificacion_cliente INTEGER DEFAULT 0,
                feedback_cliente TEXT DEFAULT '',
                calificacion_dueno INTEGER DEFAULT 0,
                feedback_dueno TEXT DEFAULT '',
                venta_valor REAL DEFAULT 0
                )
                ''')
        conexion.commit()
        migrar_base_de_datos_reservas()
        print(f"Base de datos {nombre_bd} y tabla 'usuarios' creadas con exito")
    except sqlite3.Error as e:
        print(f"error al conectar error: {e}")
    finally:
        if conexion:
            conexion.close()


def insertar_reserva(nombre,apellido,cedula,foto,hora,sector,taxi,conductor="",metodo_pago="",venta_valor=0):
    conexion = None
    try:
        cedula = str(cedula).strip()
        venta_valor = float(venta_valor or 0)
        crear_base_de_datos_reservas()
        conexion = sqlite3.connect(nombre_bd)
        cursor = conexion.cursor()
        sql = "INSERT INTO reservas (nombre,apellido,cedula,foto,hora,sector,taxi,estado,conductor,metodo_pago,venta_valor) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        valores = (nombre,apellido,cedula,foto,hora,sector,taxi,"pendiente",conductor,metodo_pago,venta_valor)
        cursor.execute(sql,valores)
        conexion.commit()
        print(f"Reserva para {nombre} guardada correctamente")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: la cedula {cedula} ya esta registrada")
        return False
    except ValueError:
        print("Error: el valor del viaje debe ser numerico")
        return False
    except sqlite3.Error as e:
        print(f"Error al insertar los datos:{e}")
        return False
    finally:
        if conexion:
            conexion.close()
def consultar_usuarios():
    usuarios = []
    conexion = None
    try:
        crear_base_de_datos_reservas()
        conexion = sqlite3.connect(nombre_bd)
        cursor = conexion.cursor()
        sql = "SELECT id,nombre,apellido,cedula,foto,hora,sector,taxi,fecha_registro,estado,conductor,metodo_pago,calificacion_cliente,feedback_cliente,calificacion_dueno,feedback_dueno,venta_valor FROM reservas"
        cursor.execute(sql)
        usuarios = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al consultar {e}")
    finally:
        if conexion:
            conexion.close()
    return usuarios
def actualizar_estado_reserva(id_reserva, estado):
    conexion = sqlite3.connect(nombre_bd)
    cursor = conexion.cursor()
    cursor.execute("UPDATE reservas SET estado = ? WHERE id = ?", (estado, id_reserva))
    conexion.commit()
    conexion.close()

def calificar_viaje_cliente(id_reserva, calificacion, feedback):
    conexion = sqlite3.connect(nombre_bd)
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE reservas SET calificacion_cliente = ?, feedback_cliente = ? WHERE id = ?",
        (calificacion, feedback, id_reserva)
    )
    conexion.commit()
    conexion.close()

def calificar_cliente_dueno(id_reserva, calificacion, feedback):
    conexion = sqlite3.connect(nombre_bd)
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE reservas SET calificacion_dueno = ?, feedback_dueno = ?, estado = ? WHERE id = ?",
        (calificacion, feedback, "finalizado", id_reserva)
    )
    conexion.commit()
    conexion.close()

def eliminar_reserva(id_reserva):
    conexion = sqlite3.connect(nombre_bd)
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM reservas WHERE id = ?",
        (id_reserva,)
    )

    conexion.commit()
    conexion.close()
#ACA CREAMOS LA TABLA EL ID SIEMPRE VA ES PARA QUE ME ORGANICE LA TABLA CON ELA UTOICREMENT PARA QUE SE
#ME INCREMENTE MEDIANTE LOS USUARIOS QUE LLEGUEN
# Y LA FECHA DE REGISTRO ES LA FECHA DE LO QUE SE ME CREARON
