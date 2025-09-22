import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact


def main(page: ft.Page):
    page.title = "Contact Book"
    page.theme_mode = ft.ThemeMode.LIGHT  # Default theme
    page.window_min_width = 400
    page.window_min_height = 600
    page.window_resizable = True
    page.vertical_alignment = ft.MainAxisAlignment.START

    db_conn = init_db()

    # Input fields
    name_input = ft.TextField(label="Name", width=350)
    phone_input = ft.TextField(label="Phone", width=350)
    email_input = ft.TextField(label="Email", width=350)
    inputs = (name_input, phone_input, email_input)

    # Search field
    search_field = ft.TextField(
        label="Search",
        width=350,
        on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, search_field.value)
    )

    # Contact list
    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)

    # Buttons
    add_button = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn)
    )

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()

    theme_button = ft.ElevatedButton("Toggle Theme", on_click=toggle_theme)

    # Layout
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("Enter Contact Details:", size=20, weight=ft.FontWeight.BOLD),
                    name_input,
                    phone_input,
                    email_input,
                    add_button,
                    ft.Divider(),
                    ft.Row([search_field, theme_button]),
                    ft.Text("Contacts:", size=20, weight=ft.FontWeight.BOLD),
                    contacts_list_view,
                ]
            ),
            padding=20,
        )
    )

    display_contacts(page, contacts_list_view, db_conn)


if __name__ == "__main__":
    ft.app(target=main)