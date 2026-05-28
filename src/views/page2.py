import flet as ft
from src.models.reservas import Reserva
from src.data.base_de_datos_reservas import consultar_usuarios, eliminar_reserva


def procesar_reservas(funcion):
    def funcion_modificada(page: ft.Page):
        try:
            datos = consultar_usuarios()

            if not datos:
                return ft.Column(
                    controls=[ft.Text("No hay reservas")]
                )

            carros = []

            for fila in datos:
                nueva = Reserva(
                    fila[1],
                    fila[2],
                    fila[3],
                    fila[4],
                    fila[5],
                    fila[6],
                    fila[7],
                )

                agregado = False

                for carro in carros:
                    if (
                        carro["hora"] == fila[5]
                        and carro["sector"] == fila[6]
                        and carro["taxi"] == fila[7]
                    ):
                        if len(carro["pasajeros"]) < 4:
                            carro["pasajeros"].append({
                                "id": fila[0],
                                "data": nueva
                            })
                            agregado = True
                            break

                if not agregado:
                    carros.append({
                        "hora": fila[5],
                        "sector": fila[6],
                        "taxi": fila[7],
                        "pasajeros": [{
                            "id": fila[0],
                            "data": nueva
                        }]
                    })

            return funcion(page, carros)

        except Exception as e:
            print("Error:", e)
            return ft.Column(
                controls=[ft.Text("Error al cargar reservas")]
            )

    return funcion_modificada


def eliminar_y_recargar(e, id_reserva, page):
    try:
        eliminar_reserva(id_reserva)
        page.update()
    except Exception as error:
        page.update()


@procesar_reservas
def vista_reservas(page: ft.Page, carros):
    cards = []
    for i, carro in enumerate(carros):
        pasajeros_controls = []
        for pasajero in carro["pasajeros"]:
            p = pasajero["data"]
            id_reserva = pasajero["id"]

            pasajeros_controls.append(
                ft.Container(
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.GREY_100,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"- {p.get_nombre()} {p.get_apellido()}",
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                f"CC: {p.get_cedula()}"
                            ),

                            ft.ElevatedButton(
                                "Eliminar reserva",
                                icon=ft.Icons.DELETE,
                                bgcolor=ft.Colors.RED,
                                color=ft.Colors.WHITE,
                                on_click=lambda e,
                                id_reserva=id_reserva:
                                eliminar_y_recargar(
                                    e,
                                    id_reserva,
                                    page
                                )
                            )
                        ]
                    )
                )
            )

        card = ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=15,
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.BLACK12
            ),
            content=ft.Column(
                controls=[
                    ft.Text(
                        f"🚖 Carro {i+1}",
                        weight=ft.FontWeight.BOLD,
                        size=18
                    ),

                    ft.Text(f"Hora: {carro['hora']}"),
                    ft.Text(f"Sector: {carro['sector']}"),
                    ft.Text(f"Taxi: {carro['taxi']}"),

                    ft.Text(
                        f"Pasajeros: {len(carro['pasajeros'])}/4"
                    ),

                    ft.Divider(),

                    ft.Column(
                        controls=pasajeros_controls
                    )
                ]
            )
        )

        cards.append(card)

    return ft.Column(
        controls=[
            ft.Text(
                "📋 LISTA DE RESERVAS (BD)",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        content=card,
                        col={
                            "sm": 12,
                            "md": 6,
                            "lg": 4,
                            "xl": 3
                        }
                    )
                    for card in cards
                ],
                spacing=10,
                run_spacing=10
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )