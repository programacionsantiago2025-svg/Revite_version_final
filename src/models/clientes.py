import csv
class Cliente():
    def __init__(self, nombre, apellido, cedula, foto):
        self.__nombre = nombre
        self.__apellido = apellido
        self.__cedula = str(cedula).strip()
        self.foto = foto

    def get_nombre(self):
        return self.__nombre

    def get_apellido(self):
        return self.__apellido

    def get_cedula(self):
        return self.__cedula
