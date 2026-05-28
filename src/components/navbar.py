import flet as ft

def navbar(on_change, rol, cerrar_sesion):
    botones = []

    if rol == "administrador":
        botones = [
            ft.TextButton(
                content="Bases de datos",
                icon=ft.Icons.STORAGE,
                style=ft.TextStyle(color="black"),
                on_click=lambda e: on_change("admin")
            ),
            ft.TextButton(
                content="Ver reservas",
                icon=ft.Icons.LIST,
                style=ft.TextStyle(color="black"),
                on_click=lambda e: on_change("reservas")
            )
        ]

    elif rol == "cliente":
        botones = [
            ft.TextButton(
                content="Hacer reserva",
                icon=ft.Icons.ADD_TASK,
                style=ft.TextStyle(color="black"),
                on_click=lambda e: on_change("cliente")
            ),
            ft.TextButton(
                content="Mis reservas",
                icon=ft.Icons.EVENT_NOTE,
                style=ft.TextStyle(color="black"),
                on_click=lambda e: on_change("mis_reservas")
            )
        ]

    elif rol == "dueno":
        botones = [
            ft.TextButton(
                content="Crear carro",
                icon=ft.Icons.DIRECTIONS_CAR,
                style=ft.TextStyle(color="black"),
                on_click=lambda e: on_change("carro")
            ),
            ft.TextButton(
                content="Solicitudes",
                icon=ft.Icons.MARK_EMAIL_UNREAD,
                style=ft.TextStyle(color="black"),
                on_click=lambda e: on_change("dueno")
            )
        ]

    botones.append(
        ft.TextButton(
            content="Salir",
            icon=ft.Icons.LOGOUT,
            style=ft.TextStyle(color="black"),
            on_click=cerrar_sesion
        )
    )

    return ft.Container(
        bgcolor=ft.Colors.BLUE_GREY_700,
        padding=10,
        border_radius=10,
        content=ft.Row(
            controls=botones,
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        )
    )
