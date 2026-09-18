import pytest
from pydantic import ValidationError
from sqlalchemy.engine import make_url

from slotlock.settings import Settings, get_settings
from tests.conftest import TestSettings as DatabaseTestSettings
from tests.conftest import safe_test_url


def test_settings_load_environment(test_database_url, monkeypatch):
    monkeypatch.setenv('DATABASE_URL', test_database_url)
    get_settings.cache_clear()
    try:
        assert str(get_settings().database_url) == test_database_url
    finally:
        get_settings.cache_clear()


def test_sync_driver_is_rejected(test_database_url):
    url = make_url(test_database_url).set(drivername='postgresql')
    with pytest.raises(ValidationError, match='postgresql\\+asyncpg'):
        Settings(database_url=url.render_as_string(hide_password=False))
    with pytest.raises(ValueError, match='asyncpg'):
        safe_test_url(url.render_as_string(hide_password=False))


def test_missing_test_url_does_not_use_development_url(
    test_database_url, monkeypatch
):
    monkeypatch.delenv('TEST_DATABASE_URL', raising=False)
    monkeypatch.setenv('DATABASE_URL', test_database_url)
    with pytest.raises(ValidationError, match='test_database_url'):
        DatabaseTestSettings(_env_file=None)
