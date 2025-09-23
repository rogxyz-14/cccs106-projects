import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact

def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 420
    page.window_height = 700

    db_conn = init_db()

    # ---------------- Dark / Light Toggle ----------------
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_btn.icon = ft.Icons.LIGHT_MODE   # 🌞 show sun when in dark mode
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_btn.icon = ft.Icons.DARK_MODE    # 🌙 show moon when in light mode
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        tooltip="Switch Theme",
        on_click=toggle_theme,
    )

    # ---------------- Header (top bar) ----------------
    header_left = ft.Row(
        [
            ft.Icon(name=ft.Icons.CONTACT_PHONE, size=40, color=ft.Colors.BLUE_600),
            ft.Text("My Contacts", size=24, weight=ft.FontWeight.BOLD),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=10,
    )

    header = ft.Row(
        [
            header_left,
            theme_btn,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------------- Input Fields ----------------
    name_input = ft.TextField(label="Name", width=350, border_radius=12)
    phone_input = ft.TextField(label="Phone", width=350, border_radius=12)
    email_input = ft.TextField(label="Email", width=350, border_radius=12)
    inputs = (name_input, phone_input, email_input)

    add_button = ft.ElevatedButton(
        text="➕ Add Contact",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=20,
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
        ),
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn),
    )

    input_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Add New Contact", size=20, weight=ft.FontWeight.W_600),
                    name_input,
                    phone_input,
                    email_input,
                    add_button,
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
        )
    )

    # ---------------- Search Bar ----------------
    search_input = ft.TextField(
        label="🔍 Search Contact",
        width=350,
        border_radius=12,
        on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, e.control.value),
    )

    # ---------------- Contacts List ----------------
    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)

    contacts_section = ft.Column(
        [
            ft.Text("Saved Contacts", size=22, weight=ft.FontWeight.BOLD),
            contacts_list_view,
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------------- Layout ----------------
    page.add(
        ft.Column(
            [
                header,
                ft.Divider(),
                ft.Column(
                    [
                        input_card,
                        search_input,
                        ft.Divider(),
                        contacts_section,
                    ],
                    spacing=20,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],
            spacing=20,
            expand=True,
        )
    )

    # Load existing contacts
    display_contacts(page, contacts_list_view, db_conn)

if __name__ == "__main__":
    ft.app(target=main)
