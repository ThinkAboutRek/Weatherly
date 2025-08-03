import pytest
from weather.models import Search

@pytest.mark.django_db
def test_search_str_representation():
    s = Search.objects.create(city="TestCity")
    # __str__ should include the city name
    assert "TestCity" in str(s)
