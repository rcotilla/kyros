import flet as ft
import typing as cast


def main(page: ft.Page):
    """
    KAIROS Frontend - Aplicación Web de Gestoría

    Ejecutar como web:
        flet run --web

    Ejecutar como desktop:
        flet run
    """

    # Configuración de página
    page.title = "KAIROS - Plataforma de Gestión de Procesos de Gestoría"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    page.padding = 0

    # Variables de estado
    counter = ft.Text("0", size=50, data=0)

    # Event handlers
    def increment_click(e: ft.Event[ft.FloatingActionButton]):
        counter.data += 1
        counter.value = str(counter.data)

    # Header

    elementos: list[ft.Control] = [
        ft.Text("Título"),
        ft.Divider(),
        ft.Container(content=ft.Text("Contenido"))
    ]

    header = ft.Container(
        content=ft.Row(
            controls=elementos,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=20,
        bgcolor=ft.colors.SURFACE,
        border_radius=0,
    )

    # Main content

    content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Contador de Procesos", size=24, weight="bold"),
                ft.Divider(),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Procesos actuales:", size=16),
                            counter,
                            ft.ElevatedButton(
                                text="+ Nuevo Proceso",
                                icon=ft.Icons.ADD,
                                on_click=increment_click,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                ),
            ],
            spacing=20,
        ),
        padding=30,
        expand=True,
    )

    # Footer
    footer = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("© 2026 KAIROS - Plataforma de Gestoría", size=12, color=ft.colors.GREY_700),
                ft.Text(f"Versión: 0.1.0 | Modo: {'Web' if page.web else 'Desktop'}", size=12, color=ft.colors.GREY_700),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=15,
        bgcolor=ft.colors.LIGHT_GREY_200,
        border_radius=0,
    )

    # Layout principal
    page.add(
        ft.Column(
            controls=[
                header,
                content,
                footer,
            ],
            expand=True,
            spacing=0,
        )
    )

    # Floating action button (solo para desktop)
    if not page.web:
        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            key="increment",
            on_click=increment_click,
        )


if __name__ == "__main__":
    # Ejecutar como web por defecto si se pasa --web
    ft.run(main)
