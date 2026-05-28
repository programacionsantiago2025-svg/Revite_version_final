import sqlite3
import os
import sys
import shutil

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
nombre_bd = os.path.join(BASE_DIR, "revite_carros.db")

def preparar_base_de_datos():
    if os.path.exists(nombre_bd) or not getattr(sys, "frozen", False):
        return

    plantilla = os.path.join(getattr(sys, "_MEIPASS", BASE_DIR), "revite_carros.db")
    if os.path.exists(plantilla):
        shutil.copyfile(plantilla, nombre_bd)

def migrar_base_de_datos_carros():
    preparar_base_de_datos()
    conexion = sqlite3.connect(nombre_bd)
    cursor = conexion.cursor()
    cursor.execute("PRAGMA table_info(carros)")
    columnas = [columna[1] for columna in cursor.fetchall()]
    nuevas_columnas = {
        "dueno": "TEXT DEFAULT ''",
        "conductor": "TEXT DEFAULT ''",
        "metodos_pago": "TEXT DEFAULT 'Efectivo'"
    }
    for columna, tipo in nuevas_columnas.items():
        if columna not in columnas:
            cursor.execute(f"ALTER TABLE carros ADD COLUMN {columna} {tipo}")
    conexion.commit()
    conexion.close()

def crear_base_de_datos_carros():
    try:
        preparar_base_de_datos()
        conexion = sqlite3.connect(nombre_bd)
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placa TEXT UNIQUE NOT NULL,
                marca TEXT NOT NULL,
                modelo TEXT NOT NULL,
                mantenimiento TEXT NOT NULL,
                capacidad TEXT NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dueno TEXT DEFAULT '',
                conductor TEXT DEFAULT '',
                metodos_pago TEXT DEFAULT 'Efectivo'
                )
                ''')
        conexion.commit()
        migrar_base_de_datos_carros()
        print(f"Base de datos {nombre_bd} y tabla 'carros' creadas con exito")
    except sqlite3.Error as e:
        print(f"error al conectar error: {e}")
    finally:
        if conexion:
            conexion.close()


def insertar_carro(placa,marca,modelo,mantenimiento,capacidad,dueno="",conductor="",metodos_pago="Efectivo"):
    try:
        crear_base_de_datos_carros()
        conexion = sqlite3.connect(nombre_bd)
        cursor = conexion.cursor()
        sql = "INSERT INTO carros (placa,marca,modelo,mantenimiento,capacidad,dueno,conductor,metodos_pago) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        valores = (placa,marca,modelo,mantenimiento,capacidad,dueno,conductor,metodos_pago)
        cursor.execute(sql,valores)
        conexion.commit()
        print(f"Carro {placa} guardado correctamente")
    except sqlite3.IntegrityError:
        print(f"Error: la placa {placa} ya esta registrada")
    except sqlite3.Error as e:
        print(f"Error al insertar los datos:{e}")
    finally:
        if conexion:
            conexion.close()
def consultar_carros():
    carros = []
    try:
        crear_base_de_datos_carros()
        conexion = sqlite3.connect(nombre_bd)
        cursor = conexion.cursor()
        sql = "SELECT id,placa,marca,modelo,mantenimiento,capacidad,fecha_registro,dueno,conductor,metodos_pago FROM carros"
        cursor.execute(sql)
        carros = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al consultar {e}")
    finally:
        if conexion:
            conexion.close()
    return carros
   

"""
    insertar_usuario("Santiago", "santiagomoralesmorales08@gmail.com", "1070600370", "3133017419")
    insertar_usuario("Nicolas", "nicolasmoralesmorales08@gmail.com", "1070600371", "3133017415")
    insertar_usuario("Pepo", "pedrosanchez@gmail.com", "1070600372", "3133017413")"""
#ACA CREAMOS LA TABLA EL ID SIEMPRE VA ES PARA QUE ME ORGANICE LA TABLA CON ELA UTOICREMENT PARA QUE SE
#ME INCREMENTE MEDIANTE LOS USUARIOS QUE LLEGUEN
# Y LA FECHA DE REGISTRO ES LA FECHA DE LO QUE SE ME CREARON
