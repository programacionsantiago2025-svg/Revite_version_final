import csv
import json
import os
import sys
from src.models.clientes import Cliente
from datetime import datetime
import flet as ft

fecha_actual = datetime.now()
horas = ["5:00", "5:30", "6:00"]
sectores = []


class Reserva(Cliente):
    def __init__(self, nombre, apellido, cedula, foto, hora, sector, taxi_seleccionado):
        super().__init__(nombre, apellido, cedula, foto)
        self.__hora = hora
        self.__sector = sector
        self.__taxi_seleccionado = taxi_seleccionado
        self.carros = []

    def get_hora(self):
        return self.__hora

    def get_sector(self):
        return self.__sector

    def get_taxi(self):
        return self.__taxi_seleccionado

    def ver_carros(self):
        if not self.carros:
            print("No hay reservas")
            return


def guardar_json(**kwargs):
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
        ruta = os.path.join(base_dir, "data", "reservas.json")
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        ruta = os.path.join(base_dir, "data", "reservas.json")

    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump([], f)

    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    datos.append(kwargs)

    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4)
