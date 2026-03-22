import pytest
from django.contrib.auth.models import User
from weather.models import Search


@pytest.mark.django_db
def test_search_str_includes_city_and_timestamp():
    s = Search.objects.create(city="TestCity")
    result = str(s)
    assert "TestCity" in result
    assert "at" in result


@pytest.mark.django_db
def test_search_without_user_is_anonymous():
    s = Search.objects.create(city="Berlin")
    assert s.user is None


@pytest.mark.django_db
def test_search_linked_to_user():
    user = User.objects.create_user(username="tester", password="pass")
    s = Search.objects.create(city="Tokyo", user=user)
    assert s.user == user


@pytest.mark.django_db
def test_search_ordering_newest_first():
    Search.objects.create(city="Alpha")
    Search.objects.create(city="Beta")
    cities = list(Search.objects.values_list("city", flat=True))
    assert cities[0] == "Beta"


@pytest.mark.django_db
def test_search_user_set_null_on_delete():
    user = User.objects.create_user(username="gone", password="pass")
    s = Search.objects.create(city="Madrid", user=user)
    user.delete()
    s.refresh_from_db()
    assert s.user is None


@pytest.mark.django_db
def test_search_city_max_length():
    long_city = "A" * 100
    s = Search.objects.create(city=long_city)
    assert s.city == long_city
