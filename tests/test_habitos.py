"""Tests for flet-habitos database and models."""

import sqlite3
from datetime import date, timedelta

import pytest

from py_flet_habitos.database import Database
from py_flet_habitos.models import Checkin, Habit


# ------------------------------------------------------------------
# Models
# ------------------------------------------------------------------
def test_habit_defaults():
    h = Habit(name="Ler", color="green")
    assert h.name == "Ler"
    assert h.color == "green"
    assert h.id is None


def test_checkin_defaults():
    c = Checkin(habit_id=1, day="2024-01-05")
    assert c.habit_id == 1
    assert c.day == "2024-01-05"
    assert c.id is None


# ------------------------------------------------------------------
# Database: habits
# ------------------------------------------------------------------
def test_add_and_get_habit(tmp_path):
    db = Database(tmp_path / "test.db")
    rid = db.add_habit(Habit(name="Ler", color="green"))
    assert rid == 1

    habits = db.get_habits()
    assert len(habits) == 1
    assert habits[0].name == "Ler"
    assert habits[0].color == "green"


def test_habit_names_unique(tmp_path):
    db = Database(tmp_path / "test.db")
    db.add_habit(Habit(name="Ler", color="green"))
    with pytest.raises(sqlite3.IntegrityError):
        db.add_habit(Habit(name="Ler", color="blue"))


def test_delete_habit(tmp_path):
    db = Database(tmp_path / "test.db")
    rid = db.add_habit(Habit(name="Ler", color="green"))
    assert db.delete_habit(rid) is True
    assert db.get_habits() == []


# ------------------------------------------------------------------
# Database: check-ins
# ------------------------------------------------------------------
def test_add_and_remove_checkin(tmp_path):
    db = Database(tmp_path / "test.db")
    hid = db.add_habit(Habit(name="Ler", color="green"))

    assert db.add_checkin(hid, "2024-01-05") == 1
    assert db.has_checkin(hid, "2024-01-05") is True
    assert db.add_checkin(hid, "2024-01-05") is None  # duplicate -> None

    assert db.remove_checkin(hid, "2024-01-05") is True
    assert db.has_checkin(hid, "2024-01-05") is False


def test_get_checkins_for_habit(tmp_path):
    db = Database(tmp_path / "test.db")
    hid = db.add_habit(Habit(name="Ler", color="green"))
    db.add_checkin(hid, "2024-01-01")
    db.add_checkin(hid, "2024-01-03")

    days = db.get_checkins_for_habit(hid)
    assert days == ["2024-01-01", "2024-01-03"]


# ------------------------------------------------------------------
# Database: streaks
# ------------------------------------------------------------------
def test_streak_empty(tmp_path):
    db = Database(tmp_path / "test.db")
    hid = db.add_habit(Habit(name="Ler", color="green"))
    assert db.get_streak(hid) == 0
    assert db.get_longest_streak(hid) == 0


def test_streak_consecutive(tmp_path):
    db = Database(tmp_path / "test.db")
    hid = db.add_habit(Habit(name="Ler", color="green"))
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    day_before = (date.today() - timedelta(days=2)).isoformat()

    db.add_checkin(hid, today)
    db.add_checkin(hid, yesterday)
    db.add_checkin(hid, day_before)

    assert db.get_streak(hid) == 3
    assert db.get_longest_streak(hid) == 3


def test_streak_with_gap(tmp_path):
    db = Database(tmp_path / "test.db")
    hid = db.add_habit(Habit(name="Ler", color="green"))
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    three_days_ago = (date.today() - timedelta(days=3)).isoformat()

    db.add_checkin(hid, today)
    db.add_checkin(hid, yesterday)
    db.add_checkin(hid, three_days_ago)

    assert db.get_streak(hid) == 2
    assert db.get_longest_streak(hid) == 2


# ------------------------------------------------------------------
# Database: export
# ------------------------------------------------------------------
def test_export_csv(tmp_path):
    db = Database(tmp_path / "test.db")
    hid = db.add_habit(Habit(name="Ler", color="green"))
    db.add_checkin(hid, "2024-01-05")

    csv_text = db.export_csv()
    assert "habit_id,habit_name,day" in csv_text
    assert f"{hid},Ler,2024-01-05" in csv_text


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
def test_cli_main(monkeypatch):
    """Test that cli.main calls ft.app with the right target."""
    import py_flet_habitos.cli as cli_mod

    called = {}

    def fake_app(target):
        called["target"] = target

    monkeypatch.setattr(cli_mod, "ft_app", fake_app)
    cli_mod.main()
    assert callable(called.get("target"))
