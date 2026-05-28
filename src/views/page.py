import flet as ft
import csv
import json
import os
import sys
from src.models.reservas import Reserva, guardar_json
from src.components.navbar import navbar
from src.views.page2 import vista_reservas
from src.models.carro import Carro, guardar_json_carro
from src.data.base_de_datos_reservas import crear_base_de_datos_reservas,insertar_reserva,consultar_usuarios,actualizar_estado_reserva,calificar_viaje_cliente,calificar_cliente_dueno
from src.data.base_de_datos_cliente import crear_base_de_datos_cliente,insertar_cliente,actualizar_rating_cliente
from src.data.base_de_datos_carros import crear_base_de_datos_carros,insertar_carro,consultar_carros
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
def main(page: ft.Page):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.join(os.path.dirname(__file__), '..', '..'))
    persona_path = os.path.join(BASE_DIR, "assets", "persona.png")

    page.title = "Mi App Principal"
    page.bgcolor = ft.Colors.BLUE_GREY_500
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    horarios = ["6:00", "6:30", "7:00", "9:30"]
    titulo = ft.Text("AGENDA TU DESTINO", size=20, weight=ft.FontWeight.BOLD)
    checks = []
    sectores = []
    contenido = ft.Column()
    menu = ft.Column()
    rol_actual = ft.Text("")
    usuario_actual = ft.Text("")
    input_login_usuario = ft.TextField(label="Usuario o cedula", width=300, bgcolor=ft.Colors.WHITE, border_radius=10, color=ft.Colors.BLACK, icon=ft.Icons.PERSON)
    input_login_password = ft.TextField(label="Contraseña", width=300, password=True, can_reveal_password=True, bgcolor=ft.Colors.WHITE, border_radius=10, color=ft.Colors.BLACK, icon=ft.Icons.LOCK)
    rol_login = ft.Dropdown(
        label="Rol",
        width=300,
        value="cliente",
        options=[
            ft.DropdownOption(key="cliente", text="Cliente"),
            ft.DropdownOption(key="dueno", text="Dueño de carro"),
            ft.DropdownOption(key="administrador", text="Administrador")
        ]
    )
    carros = ["ABC123", "DEF456", "GHI789", "JKL012"]
    input_cedula = ft.TextField(label="Cedula", hint_text="1070600370", width=300,bgcolor=ft.Colors.WHITE,border_radius=10,color=ft.Colors.BLACK,icon=ft.Icons.INFO_ROUNDED, keyboard_type=ft.KeyboardType.NUMBER)
    input_nombre = ft.TextField(label="Nombre", hint_text="Santiago", width=300,bgcolor=ft.Colors.WHITE,border_radius=10,color=ft.Colors.BLACK,icon=ft.Icons.INFO_ROUNDED)
    input_direccion = ft.TextField(label="Direccion", hint_text="Calle... Barrio...", width=300,bgcolor=ft.Colors.WHITE,border_radius=10,color=ft.Colors.BLACK,icon=ft.Icons.INFO_ROUNDED)
    input_celular = ft.TextField(label="Celular", hint_text="3133017419", width=300,bgcolor=ft.Colors.WHITE,border_radius=10,color=ft.Colors.BLACK,icon=ft.Icons.INFO_ROUNDED)
    input_placa = ft.TextField(label="Placa", width=200, bgcolor=ft.Colors.WHITE,icon=ft.Icons.ABC)
    input_marca = ft.TextField(label="Marca", width=200, bgcolor=ft.Colors.WHITE, icon= ft.Icons.SEARCH)
    input_modelo = ft.TextField(label="Modelo", width=200, bgcolor=ft.Colors.WHITE, icon= ft.Icons.ABC)
    input_capacidad = ft.TextField(label="capacidad", width=200, bgcolor=ft.Colors.WHITE, icon= ft.Icons.ABC)
    input_dueno = ft.TextField(label="Dueño", width=200, bgcolor=ft.Colors.WHITE, icon=ft.Icons.PERSON)
    input_conductor_carro = ft.TextField(label="Conductor", width=200, bgcolor=ft.Colors.WHITE, icon=ft.Icons.PERSON)
    input_metodos_pago = ft.TextField(label="Metodos de pago", value="Efectivo, Nequi", width=200, bgcolor=ft.Colors.WHITE, icon=ft.Icons.PAYMENTS)
    input_valor = ft.TextField(label="Valor viaje", value="0", width=200, bgcolor=ft.Colors.WHITE, icon=ft.Icons.ATTACH_MONEY)
    input_feedback_cliente = ft.TextField(label="Comentario del cliente", multiline=True, min_lines=2, width=300, bgcolor=ft.Colors.WHITE)
    input_feedback_dueno = ft.TextField(label="Comentario del dueño", multiline=True, min_lines=2, width=300, bgcolor=ft.Colors.WHITE)
    rating_cliente = ft.Dropdown(
        label="Calificacion al conductor",
        width=300,
        options=[ft.DropdownOption(key=str(i), text=f"{i} estrellas") for i in range(1, 6)]
    )
    rating_dueno = ft.Dropdown(
        label="Calificacion al cliente",
        width=300,
        options=[ft.DropdownOption(key=str(i), text=f"{i} estrellas") for i in range(1, 6)]
    )
    reserva_cliente = ft.Dropdown(label="Reserva para calificar", width=300, options=[])
    reserva_dueno = ft.Dropdown(label="Reserva para finalizar", width=300, options=[])
    conductor_cliente = ft.Dropdown(label="Conductor", width=300, options=[])
    metodo_pago_cliente = ft.Dropdown(label="Metodo de pago", width=300, options=[])
    check_mantenimiento = ft.Checkbox(label="En mantenimiento:")
    texto_taxi = ft.Text("NO CARRO SELECCIONADO")
    imagen = ft.Image(
        src = persona_path,
        width= 200,
        height = 200
    )
    def mostrar_mensaje(texto):
        page.snack_bar = ft.SnackBar(ft.Text(texto))
        page.snack_bar.open = True
        page.update()

    def entrar_login(e):
        usuario = str(input_login_usuario.value or "").strip()
        password = input_login_password.value or ""
        rol = rol_login.value

        if rol == "administrador":
            if usuario != "admin" or password != "admin123":
                mostrar_mensaje("Usuario o contraseña de administrador incorrectos")
                return
        else:
            if not usuario:
                mostrar_mensaje("Escriba su usuario o cedula")
                return

        rol_actual.value = rol
        usuario_actual.value = usuario
        menu.controls = [navbar(cambiar_vista, rol_actual.value, cerrar_sesion)]

        if rol == "cliente":
            input_cedula.value = usuario if usuario.isdigit() else ""
            cambiar_vista("cliente")
        elif rol == "dueno":
            input_dueno.value = usuario
            cambiar_vista("dueno")
        else:
            cambiar_vista("admin")

    def cerrar_sesion(e):
        rol_actual.value = ""
        usuario_actual.value = ""
        input_login_password.value = ""
        menu.controls = []
        contenido.controls = [vista_login()]
        page.update()

    def seleccionar_taxi(e):
        texto_taxi.value = f"Carro seleccionado: {e.control.data}"
        page.update()
    def reserva_es_del_dueno(reserva):
        if rol_actual.value != "dueno":
            return True
        usuario_dueno = str(usuario_actual.value or "").strip().lower()
        taxi_reserva = str(reserva[7] or "").strip().lower()
        carros_dueno = []

        for carro in consultar_carros():
            dueno_carro = str(carro[7] or "").strip().lower()
            placa_carro = str(carro[1] or "").strip().lower()

            if dueno_carro == usuario_dueno:
                carros_dueno.append(carro)
                if placa_carro and placa_carro in taxi_reserva:
                    return True

        if not carros_dueno:
            return True

        for carro in consultar_carros():
            placa_carro = str(carro[1] or "").strip().lower()
            if placa_carro and placa_carro in taxi_reserva:
                return False

        if reserva[9] == "pendiente":
            return True

        return False

    def crear_reserva_args(*args):
        nueva = Reserva(
            args[0],
            args[1],
            args[2],
            args[3],
            args[4],
            args[5],
            args[6]
    )
        guardar_json(
            nombre=nueva.get_nombre(),
            apellido=nueva.get_apellido(),
            cedula=nueva.get_cedula(),
            foto=nueva.foto,
            hora=nueva.get_hora(),
            sector=nueva.get_sector(),
            taxi=nueva.get_taxi()
    )
    def crear_reserva():
        nombre = input_nombre.value
        cedula = str(input_cedula.value or "").strip()
        foto = imagen.src
        sector = radios.value
        hora = None
        taxi_seleccionado = texto_taxi.value
        conductor = conductor_cliente.value or ""
        metodo_pago = metodo_pago_cliente.value or ""
        valor = input_valor.value or "0"

        for check in checks:
            if check.value:  
                hora = check.label
                break

        if not nombre or not cedula or not sector or not hora or "NO CARRO" in taxi_seleccionado:
            mostrar_mensaje("Complete nombre, cedula, sector, horario y carro")
            return

        if not cedula.isdigit():
            mostrar_mensaje("La cedula debe contener solo numeros")
            return

        insertar_cliente(nombre, "", cedula, foto)
        reserva_guardada = insertar_reserva(nombre, "", cedula, foto, hora, sector, taxi_seleccionado, conductor, metodo_pago, valor)
        if not reserva_guardada:
            mostrar_mensaje("No se pudo guardar la reserva. Revise los datos")
            return
        usuario_actual.value = cedula
        input_cedula.value = cedula
        crear_reserva_args(
            nombre,
            "",  
            cedula,
            foto,
            hora,
            sector,
            taxi_seleccionado
        )
        cargar_reservas_para_calificar()
        mostrar_mensaje(f"Reserva enviada para {nombre}")
    def cargar_reservas_para_calificar():
        reservas = consultar_usuarios()
        opciones_cliente = []
        opciones_dueno = []
        for reserva in reservas:
            texto = f"{reserva[0]} - {reserva[1]} - {reserva[5]} - {reserva[7]} - {reserva[9]}"
            if reserva[9] in ["aceptada", "finalizado"] and (rol_actual.value != "cliente" or str(reserva[3]) == str(usuario_actual.value)):
                opciones_cliente.append(ft.DropdownOption(key=str(reserva[0]), text=texto))
            if reserva[9] == "aceptada" and reserva_es_del_dueno(reserva):
                opciones_dueno.append(ft.DropdownOption(key=str(reserva[0]), text=texto))
        reserva_cliente.options = opciones_cliente
        reserva_dueno.options = opciones_dueno
        page.update()
    def aceptar_reserva(id_reserva):
        actualizar_estado_reserva(id_reserva, "aceptada")
        cargar_reservas_para_calificar()
        cambiar_vista("dueno")
        mostrar_mensaje("Solicitud aceptada")
    def rechazar_reserva(id_reserva):
        actualizar_estado_reserva(id_reserva, "rechazada")
        cargar_reservas_para_calificar()
        cambiar_vista("dueno")
        mostrar_mensaje("Solicitud rechazada")
    def guardar_calificacion_cliente():
        if not reserva_cliente.value or not rating_cliente.value:
            mostrar_mensaje("Seleccione una reserva y una calificacion")
            return
        calificar_viaje_cliente(reserva_cliente.value, rating_cliente.value, input_feedback_cliente.value or "")
        cargar_reservas_para_calificar()
        mostrar_mensaje("Gracias por calificar el viaje")
    def guardar_calificacion_dueno():
        if not reserva_dueno.value or not rating_dueno.value:
            mostrar_mensaje("Seleccione una reserva y una calificacion")
            return
        reserva = None
        for fila in consultar_usuarios():
            if str(fila[0]) == str(reserva_dueno.value):
                reserva = fila
                break
        calificar_cliente_dueno(reserva_dueno.value, rating_dueno.value, input_feedback_dueno.value or "")
        if reserva:
            actualizar_rating_cliente(reserva[3], rating_dueno.value, input_feedback_dueno.value or "")
        cargar_reservas_para_calificar()
        mostrar_mensaje("Cliente calificado y viaje finalizado")
    async def handle_pick_files(e):
        picker = ft.FilePicker()
        files = await picker.pick_files(allow_multiple=False)
        if files:
            imagen.src = files[0].path
    def crear_carro():
        placa = input_placa.value
        marca = input_marca.value
        modelo = input_modelo.value
        mantenimiento = check_mantenimiento.value
        capacidad = input_capacidad.value
        dueno = input_dueno.value
        conductor = input_conductor_carro.value
        metodos_pago = input_metodos_pago.value
        if not placa or not marca or not modelo or not capacidad or not dueno or not conductor:
            mostrar_mensaje("Complete los datos del carro, dueño y conductor")
            return
        nuevo_carro = Carro(placa, marca, modelo, mantenimiento, capacidad)
        guardar_json_carro(nuevo_carro)
        insertar_carro(placa, marca, modelo, mantenimiento, capacidad, dueno, conductor, metodos_pago)
        nuevo_cuadro = ft.Container( 
            width=150,
            height=180,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(color=ft.Colors.BLACK, blur_radius=20),
            border_radius=10,
            padding=10,
            data=placa,
            on_click=seleccionar_taxi,
            content=ft.Column(
                controls=[
                    ft.Text(f"{marca} - {placa} - Capacidad: {capacidad}", weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        contenedor_principal.controls.insert(-1, nuevo_cuadro)
        cargar_opciones_carros()
        mostrar_mensaje("Carro guardado")

    
    with open(os.path.join(BASE_DIR, "src", "data", "destinos.json"), "r", encoding="utf-8") as archivo:
        sectores = json.load(archivo)
    """
    with open("src/data/carros.json", "r", encoding="utf-8") as archivo:
        carros = json.load(archivo)
    """
    carros = []
    datos_bd = consultar_carros()

    for carro in datos_bd:
        carros.append({
            "placa": carro[1],
            "marca": carro[2],
            "modelo": carro[3],
            "capacidad": carro[5],
            "dueno": carro[7],
            "conductor": carro[8],
            "metodos_pago": carro[9]
        })
    def cargar_opciones_carros():
        datos = consultar_carros()
        opciones_conductor = []
        metodos = []
        for carro in datos:
            texto_carro = f"{carro[2]} {carro[1]} - {carro[8]}"
            if carro[8]:
                opciones_conductor.append(ft.DropdownOption(key=carro[8], text=texto_carro))
            for metodo in str(carro[9]).split(","):
                metodo_limpio = metodo.strip()
                if metodo_limpio and metodo_limpio not in metodos:
                    metodos.append(metodo_limpio)
        conductor_cliente.options = opciones_conductor
        metodo_pago_cliente.options = [ft.DropdownOption(key=metodo, text=metodo) for metodo in metodos]
    
    for hora in horarios:
        check = ft.Checkbox(label=hora)
        checks.append(check)
    col1 = ft.Column(
        controls=[
            input_cedula,
            input_nombre,
            input_direccion,
            input_celular,
        ],
    )
    col2 = ft.Container(
        width=200,
        height=250,
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        shadow = ft.BoxShadow(color= ft.Colors.BLACK,blur_radius=20),
        content=ft.Column(
            controls=[
                imagen,
                ft.ElevatedButton("Cargar foto",on_click=handle_pick_files,),
            ],
            alignment=ft.MainAxisAlignment.END,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    lista_horarios = ft.Column(
        controls=[
            ft.Text("Horarios", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                bgcolor = ft.Colors.WHITE,
                padding=10,
                border_radius=10,
                content=ft.Column(controls=checks)
            )
        ],
        spacing=10
    )
    seccion_carros = ft.Container(
        margin= 50,
        content=ft.Column(
        controls=[
            ft.Text("REGISTRAR CARRO", size=18, weight=ft.FontWeight.BOLD),
            input_placa,
            input_marca,
            input_modelo,
            input_capacidad,
            input_dueno,
            input_conductor_carro,
            input_metodos_pago,
            check_mantenimiento,
            ft.ElevatedButton("Guardar carro", on_click=lambda e: crear_carro())
        ],
    alignment=ft.MainAxisAlignment.CENTER,
    horizontal_alignment= ft.CrossAxisAlignment.CENTER
    ),
    bgcolor=ft.Colors.GREY_400,
    border_radius= 20,
    width= 250,
    padding= 10
    )

    radios = ft.RadioGroup(
        content=ft.ListView(
            controls=[ft.Radio(label=s, value=s) for s in sectores],
            spacing=5
        ),
        value=None  
    )

    cuadro_sectores = ft.Container(
        width=300,
        height=200,
        padding=10,
        border_radius=8,
        shadow = ft.BoxShadow(color= ft.Colors.BLACK,blur_radius=20),
        content=radios,
        bgcolor= ft.Colors.WHITE
        
    )
    cuadros = []

    for carro in carros:
        cuadro = ft.Container(
            width=150,
            height=180,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(color=ft.Colors.BLACK, blur_radius=20),
            border_radius=10,
            padding=10,
            data=f"{carro['marca']} - {carro['placa']}",
            on_click=seleccionar_taxi,
            content=ft.Column(
                controls=[
                    ft.Text(
                        f"{carro['marca']} - {carro['placa']}",
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(f"Capacidad: {carro['capacidad']}"),
                    ft.Text(f"Dueño: {carro['dueno']}"),
                    ft.Text(f"Conductor: {carro['conductor']}"),
                    ft.Text(f"Pago: {carro['metodos_pago']}")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        cuadros.append(cuadro)
    filas_carros = []

    for i in range(0, len(cuadros), 2):
        fila = ft.Row(
            controls=cuadros[i:i+2],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            spacing=10
        )
        filas_carros.append(fila)
    contenedor_principal = ft.Column(
        controls=filas_carros + [texto_taxi],
        spacing=10
    )
    
    def vista_login():
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[ft.Text("INICIAR SESION", size=24, weight=ft.FontWeight.BOLD)],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    controls=[
                        ft.Container(
                            bgcolor=ft.Colors.GREY_300,
                            border_radius=20,
                            padding=20,
                            width=360,
                            content=ft.Column(
                                controls=[
                                    rol_login,
                                    input_login_usuario,
                                    input_login_password,
                                    ft.ElevatedButton("Entrar", icon=ft.Icons.LOGIN, on_click=entrar_login)
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=12
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            spacing=20
        )

    def vista_admin():
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[ft.Text("ADMINISTRADOR", size=20, weight=ft.FontWeight.BOLD)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Base de datos clientes", icon=ft.Icons.STORAGE, on_click=lambda e: crear_base_de_datos_cliente()),
                        ft.ElevatedButton("Base de datos reservas", icon=ft.Icons.STORAGE, on_click=lambda e: crear_base_de_datos_reservas()),
                        ft.ElevatedButton("Base de datos carros", icon=ft.Icons.STORAGE, on_click=lambda e: crear_base_de_datos_carros())
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                )
            ],
            spacing=15
        )

    def tarjeta_mi_reserva(reserva):
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=12,
            shadow=ft.BoxShadow(color=ft.Colors.BLACK12, blur_radius=10),
            content=ft.Column(
                controls=[
                    ft.Text(f"Reserva #{reserva[0]}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Cliente: {reserva[1]}"),
                    ft.Text(f"Hora: {reserva[5]}"),
                    ft.Text(f"Sector: {reserva[6]}"),
                    ft.Text(f"Carro: {reserva[7]}"),
                    ft.Text(f"Conductor: {reserva[10]}"),
                    ft.Text(f"Pago: {reserva[11]}"),
                    ft.Text(f"Estado: {reserva[9]}"),
                    ft.Text(f"Mi calificacion al conductor: {reserva[12]}"),
                    ft.Text(f"Comentario del dueno: {reserva[15]}")
                ]
            )
        )

    def vista_mis_reservas():
        cargar_reservas_para_calificar()
        reservas = []
        cedula_actual = str(input_cedula.value or usuario_actual.value).strip()
        for reserva in consultar_usuarios():
            if str(reserva[3]).strip() == cedula_actual:
                reservas.append(tarjeta_mi_reserva(reserva))
        if not reservas:
            reservas = [ft.Text("No tienes reservas registradas")]
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[ft.Text("MIS RESERVAS", size=20, weight=ft.FontWeight.BOLD)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.ResponsiveRow(
                    controls=[ft.Container(content=reserva, col={"sm": 12, "md": 6, "lg": 4}) for reserva in reservas],
                    spacing=10,
                    run_spacing=10
                ),
                ft.Divider(),
                ft.Text("Calificar despues del viaje", size=18, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[reserva_cliente, rating_cliente, input_feedback_cliente],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Enviar calificacion", icon=ft.Icons.STAR, on_click=lambda e: guardar_calificacion_cliente())
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            spacing=12
        )

    def vista_inicio():
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[titulo],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[col1, col2],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                ft.Row(
                    controls=[lista_horarios, cuadro_sectores, contenedor_principal],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[conductor_cliente, metodo_pago_cliente, input_valor],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Base de datos clientes", on_click= lambda e: crear_base_de_datos_cliente()),
                        ft.ElevatedButton("Base de datos reservas", on_click= lambda e: crear_base_de_datos_reservas()),
                        ft.ElevatedButton("Base de datos carros", on_click= lambda e: crear_base_de_datos_carros()),
                        ft.ElevatedButton(
                            "Crear reserva",
                            on_click=lambda e: crear_reserva()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
            ]
        )
    def vista_cliente():
        cargar_opciones_carros()
        cargar_reservas_para_calificar()
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[ft.Text("CLIENTE", size=20, weight=ft.FontWeight.BOLD)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[col1, col2],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                ft.Row(
                    controls=[lista_horarios, cuadro_sectores, contenedor_principal],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[conductor_cliente, metodo_pago_cliente, input_valor],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Enviar reserva", icon=ft.Icons.SEND, on_click=lambda e: crear_reserva())
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            spacing=15
        )
    def vista_carro():
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[seccion_carros],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ]
        )
    def tarjeta_solicitud(reserva):
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=12,
            shadow=ft.BoxShadow(color=ft.Colors.BLACK12, blur_radius=10),
            content=ft.Column(
                controls=[
                    ft.Text(f"{reserva[1]} - CC {reserva[3]}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Hora: {reserva[5]}"),
                    ft.Text(f"Sector: {reserva[6]}"),
                    ft.Text(f"Carro: {reserva[7]}"),
                    ft.Text(f"Conductor: {reserva[10]}"),
                    ft.Text(f"Pago: {reserva[11]}"),
                    ft.Text(f"Estado: {reserva[9]}"),
                    ft.Row(
                        controls=[
                            ft.IconButton(icon=ft.Icons.CHECK, tooltip="Aceptar", on_click=lambda e, id_reserva=reserva[0]: aceptar_reserva(id_reserva)),
                            ft.IconButton(icon=ft.Icons.CLOSE, tooltip="Rechazar", on_click=lambda e, id_reserva=reserva[0]: rechazar_reserva(id_reserva))
                        ]
                    )
                ]
            )
        )
    def tarjeta_venta(reserva):
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=12,
            shadow=ft.BoxShadow(color=ft.Colors.BLACK12, blur_radius=10),
            content=ft.Column(
                controls=[
                    ft.Text(f"{reserva[1]} - {reserva[7]}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Valor: ${reserva[16]}"),
                    ft.Text(f"Calificacion cliente al conductor: {reserva[12]}"),
                    ft.Text(f"Feedback cliente: {reserva[13]}"),
                    ft.Text(f"Calificacion dueño al cliente: {reserva[14]}"),
                    ft.Text(f"Feedback dueño: {reserva[15]}"),
                ]
            )
        )
    def vista_dueno():
        cargar_reservas_para_calificar()
        reservas = consultar_usuarios()
        solicitudes = []
        ventas = []
        for reserva in reservas:
            if not reserva_es_del_dueno(reserva):
                continue
            if reserva[9] == "pendiente":
                solicitudes.append(tarjeta_solicitud(reserva))
            if reserva[9] in ["aceptada", "finalizado"]:
                ventas.append(tarjeta_venta(reserva))
        if not solicitudes:
            solicitudes = [ft.Text("No hay solicitudes pendientes")]
        if not ventas:
            ventas = [ft.Text("No hay historial de ventas")]
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[ft.Text("DUEÑO DE CARRO", size=20, weight=ft.FontWeight.BOLD)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Text("Solicitudes", size=18, weight=ft.FontWeight.BOLD),
                ft.ResponsiveRow(
                    controls=[ft.Container(content=solicitud, col={"sm": 12, "md": 6, "lg": 4}) for solicitud in solicitudes],
                    spacing=10,
                    run_spacing=10
                ),
                ft.Divider(),
                ft.Text("Calificar cliente", size=18, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[reserva_dueno, rating_dueno, input_feedback_dueno],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Finalizar y calificar", icon=ft.Icons.STAR, on_click=lambda e: guardar_calificacion_dueno())
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Divider(),
                ft.Text("Historial de ventas", size=18, weight=ft.FontWeight.BOLD),
                ft.ResponsiveRow(
                    controls=[ft.Container(content=venta, col={"sm": 12, "md": 6, "lg": 4}) for venta in ventas],
                    spacing=10,
                    run_spacing=10
                )
            ],
            spacing=12
        )
    def cambiar_vista(vista):
        if vista == "admin":
            contenido.controls = [vista_admin()]
        elif vista == "inicio":
            contenido.controls = [vista_inicio()]
        elif vista == "cliente":
            contenido.controls = [vista_cliente()]
        elif vista == "mis_reservas":
            contenido.controls = [vista_mis_reservas()]
        elif vista == "dueno":
            contenido.controls = [vista_dueno()]
        elif vista == "reservas":
            contenido.controls = [vista_reservas(page)]
        elif vista == "carro":
            contenido.controls = [vista_carro()]
        
        page.update()
    page.add(
        ft.Column(
            controls=[
                menu,
                contenido
            ]
        )
    )
    cargar_opciones_carros()
    cargar_reservas_para_calificar()
    contenido.controls = [vista_login()]
    page.update()
ft.app(target=main)
#iniciar : python -m src.views.page
#GENERAR EJECUtABLE: pyinstaller --onefile --windowed --add-data "assets;assets" src/views/page.py
#ejecutable:pyinstaller --onefile --windowed --add-data "assets;assets" --add-data "src/data/destinos.json;src/data" --paths "." --collect-data flet --hidden-import "src" --hidden-import "src.models" --hidden-import "src.models.carro" --hidden-import "src.models.clientes" --hidden-import "src.models.reservas" --hidden-import "src.components" --hidden-import "src.components.navbar" --hidden-import "src.data" --hidden-import "src.data.base_de_datos_carros" --hidden-import "src.data.base_de_datos_cliente" --hidden-import "src.data.base_de_datos_reservas" --hidden-import "src.views" --hidden-import "src.views.page2" --name "ReviteCarros" src/views/page.py
