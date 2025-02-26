import pytest

from crawjud.core import AppFactory


@pytest.fixture(scope="module")
def app_factory() -> AppFactory:
    """Fixture to create an instance of AppFactory."""
    return AppFactory()
