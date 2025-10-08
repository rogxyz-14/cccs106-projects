import flet as ft

def main(page: ft.Page):
    page.title = "Regalado Task Tracker"
    page.window_width = 700
    page.window_height = 600
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    tasks = []
    task_list = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO)

    # 🧮 Update progress bar and text
    def update_progress():
        total = len(tasks)
        completed = sum(1 for t in tasks if t["checkbox"].value)
        if total == 0:
            progress_text.value = "No tasks yet"
            progress_bar.value = 0
        else:
            progress_text.value = f"{completed} of {total} tasks completed"
            progress_bar.value = completed / total
        page.update()

    # ✅ Toggle task completion
    def toggle_task(e):
        checkbox = e.control
        task_container = checkbox.data
        if checkbox.value:
            task_container.bgcolor = ft.Colors.LIGHT_GREEN_100
            task_container.content.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
        else:
            task_container.bgcolor = ft.Colors.YELLOW_100
            task_container.content.style = ft.TextStyle(decoration=None)
        update_progress()
        page.update()

    # 🧹 Delete Task with Confirmation
    def confirm_delete(e):
        task_row = e.control.data
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Deletion"),
            content=ft.Text(f"Are you sure you want to delete this task?\n\"{task_row.controls[0].controls[1].content.value}\""),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.dialog.close()),
                ft.TextButton("Delete", on_click=lambda e: delete_task(task_row))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def delete_task(task_row):
        task_list.controls.remove(task_row)
        tasks[:] = [t for t in tasks if t["row"] != task_row]
        page.dialog.open = False
        update_progress()
        page.update()

    # ➕ Add task
    def add_task(e):
        if task_input.value.strip() == "":
            return

        # Container for task text
        task_text = ft.Text(task_input.value)
        task_container = ft.Container(
            content=task_text,
            bgcolor=ft.Colors.YELLOW_100,
            padding=ft.padding.symmetric(horizontal=6, vertical=4),
            border_radius=4
        )

        # Checkbox
        task_checkbox = ft.Checkbox(
            value=False,
            label="",
            on_change=toggle_task,
        )
        task_checkbox.data = task_container  # link checkbox to container

        # Delete button
        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED,
            bgcolor=ft.Colors.RED_100,
            tooltip="Delete Task",
            data=None,  # will be updated after row creation
            on_click=confirm_delete

        )

        # Left side group
        left_group = ft.Row(
            controls=[task_checkbox, task_container],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Task row layout
        task_row = ft.Row(
            controls=[left_group, delete_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # link delete button to the row itself
        delete_btn.data = task_row

        # Add to list and UI
        tasks.append({"row": task_row, "checkbox": task_checkbox})
        task_list.controls.append(task_row)

        task_input.value = ""
        update_progress()
        page.update()

    # 📝 Input Section
    task_input = ft.TextField(
        hint_text="What needs to be done?",
        bgcolor=ft.Colors.WHITE,
        expand=True
    )

    add_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD_TASK,
        bgcolor=ft.Colors.GREEN,
        on_click=add_task
    )

    input_row = ft.Row(
        controls=[task_input, add_button],
        alignment=ft.MainAxisAlignment.START
    )

    # 📊 Progress Tracking
    progress_text = ft.Text(
        value="No tasks yet",
        color=ft.Colors.GREY
    )

    progress_bar = ft.ProgressBar(
        width=600,
        value=0
    )

    progress_section = ft.Column(
        controls=[progress_text, progress_bar],
        spacing=6
    )

    # 🧩 Add everything to page
    page.add(
        input_row,
        progress_section,
        task_list
    )

ft.app(target=main)
