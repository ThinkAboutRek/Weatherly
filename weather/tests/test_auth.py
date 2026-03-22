import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_register_page_loads(client):
    resp = client.get(reverse("register"))
    assert resp.status_code == 200
    assert b"Register" in resp.content


@pytest.mark.django_db
def test_register_creates_user_and_redirects(client):
    resp = client.post(reverse("register"), {
        "username": "newuser",
        "password1": "strongpass123",
        "password2": "strongpass123",
    })
    assert resp.status_code == 302
    assert User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
def test_register_mismatched_passwords(client):
    resp = client.post(reverse("register"), {
        "username": "newuser",
        "password1": "pass1",
        "password2": "pass2",
    })
    assert resp.status_code == 200
    assert b"do not match" in resp.content.lower()
    assert not User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
def test_register_duplicate_username(client):
    User.objects.create_user(username="existing", password="pass")
    resp = client.post(reverse("register"), {
        "username": "existing",
        "password1": "pass",
        "password2": "pass",
    })
    assert resp.status_code == 200
    assert b"already taken" in resp.content.lower()


@pytest.mark.django_db
def test_login_page_loads(client):
    resp = client.get(reverse("login"))
    assert resp.status_code == 200
    assert b"Login" in resp.content


@pytest.mark.django_db
def test_login_valid_credentials(client):
    User.objects.create_user(username="user1", password="pass123")
    resp = client.post(reverse("login"), {
        "username": "user1",
        "password": "pass123",
    })
    assert resp.status_code == 302


@pytest.mark.django_db
def test_login_invalid_credentials(client):
    resp = client.post(reverse("login"), {
        "username": "noone",
        "password": "wrong",
    })
    assert resp.status_code == 200
    assert b"invalid" in resp.content.lower()


@pytest.mark.django_db
def test_logout_redirects_home(client):
    User.objects.create_user(username="user2", password="pass")
    client.login(username="user2", password="pass")
    resp = client.get(reverse("logout"))
    assert resp.status_code == 302


@pytest.mark.django_db
def test_authenticated_user_redirected_from_login(client):
    User.objects.create_user(username="loggedin", password="pass")
    client.login(username="loggedin", password="pass")
    resp = client.get(reverse("login"))
    assert resp.status_code == 302
