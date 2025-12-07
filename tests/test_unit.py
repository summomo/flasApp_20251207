# tests/test_unit.py
# Tests unitaires : on teste la logique "pure Python"
# sans (ou avec très peu) d'accès à la base ou à Flask.

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import date, timedelta

from app import _build_postgres_uri, create_app
from models import User, Task


def test_user_password_hashing():
    """
    Vérifie que set_password() crée bien un hash
    et que check_password() fonctionne correctement.
    """
    user = User(username="alice")
    user.set_password("secret")

    # Le mot de passe ne doit PAS être stocké en clair
    assert user.password_hash != "secret"
    # check_password doit renvoyer True pour le bon mot de passe
    assert user.check_password("secret") is True
    # et False pour un mauvais mot de passe
    assert user.check_password("wrong") is False


def test_task_is_overdue():
    """
    Teste la logique de Task.is_overdue().
    """
    # Tâche non complétée avec une date passée -> en retard
    past_date = date.today() - timedelta(days=1)
    task = Task(title="Old task", user_id=1, due_date=past_date, is_completed=False)
    assert task.is_overdue() is True

    # Tâche complétée -> pas en retard même si la date est passée
    done_task = Task(
        title="Done task", user_id=1, due_date=past_date, is_completed=True
    )
    assert done_task.is_overdue() is False

    # Tâche sans due_date -> jamais en retard
    no_due = Task(title="No due date", user_id=1, due_date=None, is_completed=False)
    assert no_due.is_overdue() is False


def test_build_postgres_uri_from_env(monkeypatch):
    """
    Vérifie que _build_postgres_uri() utilise bien DATABASE_URL si défini.
    """
    # On force une valeur dans l'environnement
    fake_url = "postgresql+psycopg2://user:pass@host:5432/db"
    monkeypatch.setenv("DATABASE_URL", fake_url)

    uri = _build_postgres_uri()
    assert uri == fake_url

    # On enlève DATABASE_URL pour tester la construction à partir
    # de POSTGRES_USER / PASS / HOST / PORT / DB
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_USER", "u")
    monkeypatch.setenv("POSTGRES_PASSWORD", "p")
    monkeypatch.setenv("POSTGRES_HOST", "h")
    monkeypatch.setenv("POSTGRES_PORT", "1234")
    monkeypatch.setenv("POSTGRES_DB", "mydb")

    uri = _build_postgres_uri()
    assert uri == "postgresql+psycopg2://u:p@h:1234/mydb"
