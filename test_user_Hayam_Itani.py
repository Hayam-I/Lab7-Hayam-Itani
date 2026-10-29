import pytest
from flask import json
from app import (app, starting_users, create_db_table, insert_user, get_users,
                 get_user_by_id, update_user, delete_user)


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    '''Runs each test in an empty temp folder, so app.py builds a new database.db there'''
    monkeypatch.chdir(tmp_path)
    create_db_table()


@pytest.fixture
def client():
    '''Returns a Flask test client for calling the API'''
    return app.test_client()


@pytest.fixture
def new_user():
    '''Returns a fake user that is not in the database yet'''
    return {"name": "New Test User", "email": "new@example.com", "phone": "70000099",
            "address": "Street 9, Byblos", "country": "Lebanon"}


def test_database_created_with_starting_users():
    users = get_users()
    assert [user["user_id"] for user in users] == [1, 2, 3]
    for user in users:
        del user["user_id"]
    assert users == starting_users
def test_insert_user(new_user):
    inserted = insert_user(new_user)
    assert inserted["user_id"] == 4
    assert inserted["name"] == "New Test User"
    assert get_user_by_id(4) == inserted


def test_get_users():
    users = get_users()
    assert len(users) == 3
    assert users[0]["email"] == "user1@example.com"


def test_get_user_by_id():
    assert get_user_by_id(2)["name"] == "Test User Two"
    assert get_user_by_id(99) == {}


def test_update_user():
    user = get_user_by_id(1)
    user["country"] = "France"
    updated = update_user(user)
    assert updated["country"] == "France"
    assert get_user_by_id(1)["country"] == "France"


def test_delete_user():
    result = delete_user(1)
    assert result["status"] == "User deleted successfully"
    assert get_user_by_id(1) == {}
    assert len(get_users()) == 2
def test_api_get_users(client):
    response = client.get('/api/users')
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert len(data) == 3
    assert "Test User One" in str(response.data)


def test_api_get_user(client):
    response = client.get('/api/users/2')
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data["name"] == "Test User Two"


def test_api_add_user(client, new_user):
    response = client.post('/api/users/add', data=json.dumps(new_user),
                           content_type='application/json')
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data["user_id"] == 4
    assert data["email"] == "new@example.com"
    assert get_user_by_id(4)["name"] == "New Test User"


def test_api_update_user(client):
    user = get_user_by_id(3)
    user["phone"] = "71111111"
    response = client.put('/api/users/update', data=json.dumps(user),
                          content_type='application/json')
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data["phone"] == "71111111"
    assert get_user_by_id(3)["phone"] == "71111111"


def test_api_delete_user(client):
    response = client.delete('/api/users/delete/3')
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data["status"] == "User deleted successfully"
    assert get_user_by_id(3) == {}
