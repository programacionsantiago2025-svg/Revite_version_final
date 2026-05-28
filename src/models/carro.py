import csv
import json
import os
import sys


class Carro():
    def __init__(self, placa, marca, modelo, enmantenimiento, capacidad):
        self.__placa = placa
        self.__marca = marca
        self.__modelo = modelo
        self.__enmantenimiento = enmantenimiento
        self.__capacidad = capacidad

    def get_placa(self):
        return self.__placa

    def get_marca(self):
        return self.__marca

    def get_modelo(self):
        return self.__modelo

    def get_enmantenimiento(self):
        return self.__enmantenimiento

    def get_capacidad(self):
        return self.__capacidad

    def set_placa(self, placa):
        if self.__placa == placa:
            return "No se puede crear la placa"
        else:
            self.__placa = placa

    def set_marca(self, marca):
        self.__marca = marca

    def set_modelo(self, modelo):
        self.__modelo = modelo

    def set_enmantenimiento(self, enmantenimiento):
        self.__enmantenimiento = enmantenimiento


class GestorCarros:
    instancia = None

    def __new__(cls):
        if cls.instancia is None:
            cls.instancia = super().__new__(cls)
        return cls.instancia

    def guardar(self, nuevo):
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
            ruta = os.path.join(base_dir, "data", "carros.json")
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            ruta = os.path.join(base_dir, "data", "carros.json")

        os.makedirs(os.path.dirname(ruta), exist_ok=True)

        if not os.path.exists(ruta):
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump([], f)

        with open(ruta, "r", encoding="utf-8") as archivo:
            try:
                datos = json.load(archivo)
            except:
                datos = []

        datos.append({
            "placa": nuevo.get_placa(),
            "marca": nuevo.get_marca(),
            "modelo": nuevo.get_modelo(),
            "mantenimiento": nuevo.get_enmantenimiento(),
            "capacidad": nuevo.get_capacidad()
        })

        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4)


def guardar_json_carro(nuevo):
    gestor = GestorCarros()  
    gestor.guardar(nuevo)

