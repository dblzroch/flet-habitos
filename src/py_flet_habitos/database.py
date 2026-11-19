"""Database layer for flet-habitos."""

import sqlite3
from datetime import date
from pathlib import Path
from typing import Self

from py_flet_habitos.models import Habit


class Database:
    """SQLite storage for habits and check-ins."""

    def __init__(self: Self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self: Self) -> None:
        """Create tables if they don't exist."""
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL DEFAULT 'blue'
            );
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                day TEXT NOT NULL,
                UNIQUE(habit_id, day),
                FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_checkins_habit_day
            ON checkins(habit_id, day);
        """
        )
        self.conn.commit()

    # --- Habits ---

    def add_habit(self: Self, habit: Habit) -> int:
        """Insert a habit and return its new id."""
        cur = self.conn.execute(
            "INSERT INTO habits (name, color) VALUES (?, ?)",
            (habit.name, habit.color),
        )
        self.conn.commit()
        last_id = cur.lastrowid
        assert last_id is not None
        return int(last_id)

    def get_habits(self: Self) -> list[Habit]:
        """Return all habits ordered by name."""
        rows = self.conn.execute(
            "SELECT id, name, color FROM habits ORDER BY name"
        ).fetchall()
        return [Habit(id=r["id"], name=r["name"], color=r["color"]) for r in rows]

    def delete_habit(self: Self, habit_id: int) -> bool:
        """Delete a habit and its check-ins. Returns True if a row was deleted."""
        cur = self.conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        self.conn.commit()
        return cur.rowcount > 0

    # --- Check-ins ---

    def add_checkin(self: Self, habit_id: int, day: str) -> int | None:
        """Add a check-in for a habit on a given day. Returns id or None if exists."""
        try:
            cur = self.conn.execute(
                "INSERT INTO checkins (habit_id, day) VALUES (?, ?)",
                (habit_id, day),
            )
            self.conn.commit()
            last_id = cur.lastrowid
            assert last_id is not None
            return int(last_id)
        except sqlite3.IntegrityError:
            return None

    def remove_checkin(self: Self, habit_id: int, day: str) -> bool:
        """Remove a check-in. Returns True if a row was deleted."""
        cur = self.conn.execute(
            "DELETE FROM checkins WHERE habit_id = ? AND day = ?", (habit_id, day)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def has_checkin(self: Self, habit_id: int, day: str) -> bool:
        """Return True if the habit has a check-in on the given day."""
        row = self.conn.execute(
            "SELECT 1 FROM checkins WHERE habit_id = ? AND day = ?",
            (habit_id, day),
        ).fetchone()
        return row is not None

    def get_checkins_for_habit(self: Self, habit_id: int) -> list[str]:
        """Return all check-in days for a habit."""
        rows = self.conn.execute(
            "SELECT day FROM checkins WHERE habit_id = ? ORDER BY day",
            (habit_id,),
        ).fetchall()
        return [r["day"] for r in rows]

    def get_all_checkins(self: Self) -> list[tuple[int, str]]:
        """Return all (habit_id, day) check-in pairs."""
        rows = self.conn.execute(
            "SELECT habit_id, day FROM checkins ORDER BY day"
        ).fetchall()
        return [(r["habit_id"], r["day"]) for r in rows]

    # --- Streaks ---

    def get_streak(self: Self, habit_id: int) -> int:
        """Return the current consecutive-day streak for a habit."""
        days = self.get_checkins_for_habit(habit_id)
        if not days:
            return 0

        day_set = set(days)
        streak = 0
        current = date.today().isoformat()
        while current in day_set:
            streak += 1
            # Move to previous day
            year, month, day = map(int, current.split("-"))
            current_date = date(year, month, day)
            current_date = current_date.fromordinal(current_date.toordinal() - 1)
            current = current_date.isoformat()
        return streak

    def get_longest_streak(self: Self, habit_id: int) -> int:
        """Return the longest consecutive-day streak for a habit."""
        days = sorted(self.get_checkins_for_habit(habit_id))
        if not days:
            return 0

        longest = 1
        current_streak = 1
        for i in range(1, len(days)):
            prev = date.fromisoformat(days[i - 1])
            curr = date.fromisoformat(days[i])
            if (curr - prev).days == 1:
                current_streak += 1
                longest = max(longest, current_streak)
            else:
                current_streak = 1
        return longest

    def export_csv(self: Self) -> str:
        """Export all habits and check-ins as CSV text."""
        lines = ["habit_id,habit_name,day"]
        for habit in self.get_habits():
            assert habit.id is not None
            for day in self.get_checkins_for_habit(habit.id):
                lines.append(f"{habit.id},{habit.name},{day}")
        return "\n".join(lines)

    def close(self: Self) -> None:
        """Close the database connection."""
        self.conn.close()
