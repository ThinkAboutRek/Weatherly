import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from weather.models import Search


# ---------------------------------------------------------------------------
# Recent searches
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_recent_searches_returns_five(client):
    for i in range(6):
        Search.objects.create(city=f"City{i}")
    resp = client.get(reverse("recent-searches"))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    assert data[0]["city"] == "City5"


@pytest.mark.django_db
def test_recent_searches_anonymous_shows_only_anonymous(client):
    user = User.objects.create_user(username="someone", password="pass")
    Search.objects.create(city="UserCity", user=user)
    Search.objects.create(city="AnonCity")
    resp = client.get(reverse("recent-searches"))
    cities = [r["city"] for r in resp.json()]
    assert "AnonCity" in cities
    assert "UserCity" not in cities


@pytest.mark.django_db
def test_recent_searches_authenticated_returns_own(client):
    user = User.objects.create_user(username="owner", password="pass")
    other = User.objects.create_user(username="other", password="pass")
    Search.objects.create(city="Mine", user=user)
    Search.objects.create(city="Theirs", user=other)
    client.login(username="owner", password="pass")
    resp = client.get(reverse("recent-searches"))
    cities = [r["city"] for r in resp.json()]
    assert "Mine" in cities
    assert "Theirs" not in cities


# ---------------------------------------------------------------------------
# Token auth — paginated history
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_paginated_history_requires_auth(client):
    resp = client.get(reverse("paginated-history"))
    assert resp.status_code == 401


@pytest.mark.django_db
def test_paginated_history_returns_user_searches(client):
    user = User.objects.create_user(username="pager", password="pass")
    token = Token.objects.create(user=user)
    for i in range(15):
        Search.objects.create(city=f"Place{i}", user=user)

    resp = client.get(
        reverse("paginated-history"),
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 15
    assert data["total_pages"] == 2
    assert len(data["results"]) == 10


@pytest.mark.django_db
def test_paginated_history_isolates_users(client):
    """User A's token must not expose user B's search history."""
    user_a = User.objects.create_user(username="userA", password="pass")
    user_b = User.objects.create_user(username="userB", password="pass")
    token_a = Token.objects.create(user=user_a)
    Search.objects.create(city="SecretCity", user=user_b)

    resp = client.get(
        reverse("paginated-history"),
        HTTP_AUTHORIZATION=f"Token {token_a.key}",
    )
    assert resp.status_code == 200
    cities = [r["city"] for r in resp.json()["results"]]
    assert "SecretCity" not in cities


@pytest.mark.django_db
def test_paginated_history_city_filter(client):
    user = User.objects.create_user(username="filterer", password="pass")
    token = Token.objects.create(user=user)
    Search.objects.create(city="London", user=user)
    Search.objects.create(city="Paris", user=user)
    Search.objects.create(city="Lyon", user=user)

    resp = client.get(
        reverse("paginated-history"),
        {"city": "lon"},
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    assert resp.status_code == 200
    cities = [r["city"] for r in resp.json()["results"]]
    assert "London" in cities
    assert "Paris" not in cities


@pytest.mark.django_db
def test_paginated_history_page_2(client):
    user = User.objects.create_user(username="pager2", password="pass")
    token = Token.objects.create(user=user)
    for i in range(12):
        Search.objects.create(city=f"City{i}", user=user)

    resp = client.get(
        reverse("paginated-history"),
        {"page": 2},
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 2
    assert len(data["results"]) == 2


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_csv_export_requires_login(client):
    resp = client.get(reverse("export-csv"))
    assert resp.status_code == 302
    assert "/login/" in resp["Location"]


@pytest.mark.django_db
def test_csv_export_returns_csv(client):
    user = User.objects.create_user(username="exporter", password="pass")
    Search.objects.create(city="Amsterdam", user=user)
    Search.objects.create(city="Brussels", user=user)
    client.login(username="exporter", password="pass")

    resp = client.get(reverse("export-csv"))
    assert resp.status_code == 200
    assert resp["Content-Type"] == "text/csv"
    content = resp.content.decode()
    assert "Amsterdam" in content
    assert "Brussels" in content


@pytest.mark.django_db
def test_csv_export_has_header_row(client):
    user = User.objects.create_user(username="headercheck", password="pass")
    client.login(username="headercheck", password="pass")
    resp = client.get(reverse("export-csv"))
    first_line = resp.content.decode().splitlines()[0]
    assert "City" in first_line
    assert "Searched At" in first_line


@pytest.mark.django_db
def test_csv_export_only_own_data(client):
    user = User.objects.create_user(username="mine", password="pass")
    other = User.objects.create_user(username="theirs", password="pass")
    Search.objects.create(city="MyCity", user=user)
    Search.objects.create(city="TheirCity", user=other)
    client.login(username="mine", password="pass")

    content = client.get(reverse("export-csv")).content.decode()
    assert "MyCity" in content
    assert "TheirCity" not in content


@pytest.mark.django_db
def test_csv_export_city_filter(client):
    user = User.objects.create_user(username="csvfilter", password="pass")
    Search.objects.create(city="Vienna", user=user)
    Search.objects.create(city="Venice", user=user)
    Search.objects.create(city="Oslo", user=user)
    client.login(username="csvfilter", password="pass")

    content = client.get(reverse("export-csv"), {"city": "en"}).content.decode()
    assert "Vienna" in content   # Vi-en-na
    assert "Venice" in content   # V-en-ice
    assert "Oslo" not in content


# ---------------------------------------------------------------------------
# History page
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_history_page_requires_login(client):
    resp = client.get(reverse("history"))
    assert resp.status_code == 302
    assert "/login/" in resp["Location"]


@pytest.mark.django_db
def test_history_page_shows_searches(client):
    user = User.objects.create_user(username="historian", password="pass")
    Search.objects.create(city="Lisbon", user=user)
    client.login(username="historian", password="pass")
    resp = client.get(reverse("history"))
    assert resp.status_code == 200
    assert b"Lisbon" in resp.content


@pytest.mark.django_db
def test_history_page_filters_by_city(client):
    user = User.objects.create_user(username="filterhist", password="pass")
    Search.objects.create(city="Dublin", user=user)
    Search.objects.create(city="Warsaw", user=user)
    client.login(username="filterhist", password="pass")
    resp = client.get(reverse("history"), {"city": "dublin"})
    assert b"Dublin" in resp.content
    assert b"Warsaw" not in resp.content


@pytest.mark.django_db
def test_history_page_shows_total_count(client):
    user = User.objects.create_user(username="counter", password="pass")
    for i in range(3):
        Search.objects.create(city=f"Place{i}", user=user)
    client.login(username="counter", password="pass")
    resp = client.get(reverse("history"))
    assert resp.status_code == 200
    assert b"3" in resp.content
