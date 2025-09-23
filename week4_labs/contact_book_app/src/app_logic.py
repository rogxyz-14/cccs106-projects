import flet as ft
import re
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db

# ---------------- Validation Helpers ----------------
def is_valid_phone(phone: str) -> bool:
    """Allow only digits, spaces, +, -, must be 7–15 chars."""
    return bool(re.fullmatch(r"[0-9+\-\s]{7,15}", phone.strip()))

def is_valid_email(email: str) -> bool:
    """Basic email validation."""
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email.strip()))


# ---------------- Contact Display ----------------
def display_contacts(page, contacts_list_view, db_conn, search_term=""):
    """Fetches and displays all contacts in styled cards."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search_term)

    for contact in contacts:
        contact_id, name, phone, email = contact
        initials = "".join([part[0].upper() for part in name.split()[:2]]) if name else "?"

        contact_card = ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        # Avatar Circle
                        ft.CircleAvatar(
                            content=ft.Text(initials, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            color=ft.Colors.BLUE,
                            radius=25,
                        ),

                        # Contact Info
                        ft.Column(
                            [
                                ft.Text(name, size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(f"📞 {phone or 'N/A'}"),
                                ft.Text(f"✉️ {email or 'N/A'}"),
                            ],
                            spacing=3,
                            expand=True,
                        ),

                        # Action Menu
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(
                                    text="Edit",
                                    icon=ft.Icons.EDIT,
                                    on_click=lambda _, c=contact: open_edit_dialog(page, c, db_conn, contacts_list_view),
                                ),
                                ft.PopupMenuItem(),
                                ft.PopupMenuItem(
                                    text="Delete",
                                    icon=ft.Icons.DELETE,
                                    on_click=lambda _, cid=contact_id: confirm_delete(page, cid, db_conn, contacts_list_view),
                                ),
                            ],
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=15,
                ),
                padding=15,
            ),
        )

        contacts_list_view.controls.append(contact_card)

    page.update()


# ---------------- Add Contact ----------------
def add_contact(page, inputs, contacts_list_view, db_conn):
    name_input, phone_input, email_input = inputs

    # --- Validation ---
    if not name_input.value.strip():
        name_input.error_text = "Name cannot be empty"
        page.update()
        return

    if phone_input.value and not is_valid_phone(phone_input.value):
        phone_input.error_text = "Invalid phone number"
        page.update()
        return

    if email_input.value and not is_valid_email(email_input.value):
        email_input.error_text = "Invalid email address"
        page.update()
        return

    try:
        add_contact_db(db_conn, name_input.value.strip(), phone_input.value.strip(), email_input.value.strip())
    except ValueError as e:
        page.snack_bar = ft.SnackBar(ft.Text(str(e)), open=True)
        page.update()
        return

    for field in inputs:
        field.value, field.error_text = "", None

    display_contacts(page, contacts_list_view, db_conn)
    page.update()


# ---------------- Delete with Confirmation ----------------
def confirm_delete(page, contact_id, db_conn, contacts_list_view):
    def delete_and_close(e):
        delete_contact_db(db_conn, contact_id)
        display_contacts(page, contacts_list_view, db_conn)
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Delete"),
        content=ft.Text("Are you sure you want to delete this contact?"),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
            ft.TextButton("Delete", on_click=delete_and_close),
        ],
    )
    page.open(dialog)


# ---------------- Edit Contact ----------------
def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    contact_id, name, phone, email = contact

    edit_name = ft.TextField(label="Name", value=name)
    edit_phone = ft.TextField(label="Phone", value=phone)
    edit_email = ft.TextField(label="Email", value=email)

    def save_and_close(e):
        if not edit_name.value.strip():
            edit_name.error_text = "Name cannot be empty"
            page.update()
            return

        if edit_phone.value and not is_valid_phone(edit_phone.value):
            edit_phone.error_text = "Invalid phone number"
            page.update()
            return

        if edit_email.value and not is_valid_email(edit_email.value):
            edit_email.error_text = "Invalid email address"
            page.update()
            return

        update_contact_db(db_conn, contact_id, edit_name.value.strip(), edit_phone.value.strip(), edit_email.value.strip())
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([edit_name, edit_phone, edit_email]),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )

    page.open(dialog)