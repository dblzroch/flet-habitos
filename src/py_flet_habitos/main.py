"""Flet UI for flet-habitos.  # pragma: no cover"""

from datetime import date
from pathlib import Path

import flet as ft

from py_flet_habitos.database import Database
from py_flet_habitos.models import Habit


def app_main(page: ft.Page) -> None:  # pragma: no cover
    """Build the Flet UI."""
    page.title = "py-habitos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 420  # type: ignore[attr-defined]
    page.window_height = 720  # type: ignore[attr-defined]

    db = Database(Path.home() / ".local" / "share" / "flet-habitos" / "habitos.db")

    # --- UI state ---
    habit_name_field = ft.TextField(label="Nome do hábito", width=200)
    habit_color_dropdown = ft.Dropdown(
        label="Cor",
        options=[
            ft.dropdown.Option("blue", "Azul"),
            ft.dropdown.Option("green", "Verde"),
            ft.dropdown.Option("orange", "Laranja"),
            ft.dropdown.Option("purple", "Roxo"),
            ft.dropdown.Option("red", "Vermelho"),
        ],
        value="blue",
        width=140,
    )

    habits_list = ft.ListView(expand=True, spacing=8, padding=20)
    streak_text = ft.Text(size=16, weight=ft.FontWeight.BOLD)

    def refresh() -> None:
        """Refresh the UI from the database."""
        habits = db.get_habits()
        habits_list.controls.clear()

        for habit in habits:
            assert habit.id is not None
            streak = db.get_streak(habit.id)
            has_today = db.has_checkin(habit.id, date.today().isoformat())

            color = {
                "blue": ft.colors.BLUE,
                "green": ft.colors.GREEN,
                "orange": ft.colors.ORANGE,
                "purple": ft.colors.PURPLE,
                "red": ft.colors.RED,
            }.get(habit.color, ft.colors.BLUE)

            def make_toggle(hid: int, hname: str, hcolor: str):  # type: ignore[no-untyped-def]
                def toggle(e: ft.ControlEvent) -> None:
                    today = date.today().isoformat()
                    if db.has_checkin(hid, today):
                        db.remove_checkin(hid, today)
                    else:
                        db.add_checkin(hid, today)
                    refresh()

                return toggle

            habits_list.controls.append(
                ft.ListTile(
                    leading=ft.CircleAvatar(
                        content=ft.Text(habit.name[0].upper()), bgcolor=color
                    ),
                    title=ft.Text(habit.name, weight=ft.FontWeight.W_500),
                    subtitle=ft.Text(f"Streak: {streak} dias"),
                    trailing=ft.IconButton(
                        icon=ft.icons.DONE  # type: ignore[attr-defined]
                        if has_today
                        else ft.icons.RADIO_BUTTON_UNCHECKED,  # type: ignore[attr-defined]
                        icon_color=color,
                        on_click=make_toggle(habit.id, habit.name, habit.color),
                    ),
                )
            )

        page.update()

    def add_habit(e: ft.ControlEvent) -> None:
        """Add a new habit from the form."""
        if not habit_name_field.value or not habit_color_dropdown.value:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos"))  # type: ignore[attr-defined]
            page.snack_bar.open = True  # type: ignore[attr-defined]
            page.update()
            return

        habit = Habit(
            name=habit_name_field.value,
            color=str(habit_color_dropdown.value),
        )
        db.add_habit(habit)

        habit_name_field.value = ""
        habit_color_dropdown.value = "blue"

        refresh()

    def export_csv(e: ft.ControlEvent) -> None:
        """Export all data to CSV and show a download message."""
        csv_text = db.export_csv()
        preview = csv_text[:200] + ("..." if len(csv_text) > 200 else "")
        page.snack_bar = ft.SnackBar(ft.Text(preview))  # type: ignore[attr-defined]
        page.snack_bar.open = True  # type: ignore[attr-defined]
        page.update()

    # --- Layout ---
    page.add(
        ft.Text("Hábitos", size=24, weight=ft.FontWeight.BOLD),
        streak_text,
        ft.Divider(),
        ft.Row(
            [
                habit_name_field,
                habit_color_dropdown,
                ft.ElevatedButton("Adicionar", on_click=add_habit),
                ft.ElevatedButton("Exportar CSV", on_click=export_csv),
            ],
            wrap=True,
        ),
        ft.Divider(),
        ft.Text("Seus hábitos", size=18, weight=ft.FontWeight.BOLD),
        habits_list,
    )

    refresh()
