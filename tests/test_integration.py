# tests/test_integration.py
# Tests d'intégration avec le client de test Flask.
# On teste les routes /register, /login, /tasks/new, etc.

import pytest

from app import create_app
from extensions import db
from models import User, Task


@pytest.fixture
def app():
    """
    Crée une instance d'app Flask configurée pour les tests.
    Utilise une base SQLite en mémoire.
    """
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Fournit un client de test Flask.
    """
    return app.test_client()


def register(client, username="bob", password="secret"):
    """
    Helper pour enregistrer un utilisateur.
    """
    return client.post(
        "/register",
        data={"username": username, "password": password, "confirm": password},
        follow_redirects=True,
    )


def login(client, username="bob", password="secret"):
    """
    Helper pour se connecter.
    """
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_register_and_login_flow(client, app):
    """
    Teste le flux complet :
    - inscription
    - login
    - accès à la page d'accueil
    """
    rv = register(client)
    assert b"Registration successful" in rv.data

    rv = login(client)
    assert b"Logged in successfully" in rv.data

    # Une fois connecté, on doit pouvoir accéder à "/"
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"Task" in rv.data or b"Tasks" in rv.data


def test_create_task_via_post(client, app):
    """
    Vérifie qu'on peut créer une tâche via POST /tasks/new.
    """
    register(client)
    login(client)

    rv = client.post(
        "/tasks/new",
        data={"title": "My task", "description": "Test task", "due_date": ""},
        follow_redirects=True,
    )
    assert b"Task created" in rv.data

    with app.app_context():
        tasks = Task.query.all()
        assert len(tasks) == 1
        assert tasks[0].title == "My task"


def test_toggle_task(client, app):
    """
    Vérifie qu'on peut basculer le statut d'une tâche via /tasks/<id>/toggle.
    """
    register(client)
    login(client)

    # Créer une tâche
    client.post(
        "/tasks/new",
        data={"title": "Toggle me", "description": "", "due_date": ""},
        follow_redirects=True,
    )

    with app.app_context():
        task = Task.query.first()
        task_id = task.id
        assert task.is_completed is False

    # Toggle
    rv = client.post(f"/tasks/{task_id}/toggle", follow_redirects=True)
    assert b"Task status updated" in rv.data

    with app.app_context():
        task = Task.query.get(task_id)
        assert task.is_completed is True
