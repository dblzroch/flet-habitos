"""Domain models for flet-habitos."""

from dataclasses import dataclass


@dataclass
class Habit:
    """A habit to track."""

    id: int | None = None
    name: str = ""
    color: str = "blue"  # Flet color name


@dataclass
class Checkin:
    """A daily check-in for a habit."""

    id: int | None = None
    habit_id: int = 0
    day: str = ""  # ISO date string
