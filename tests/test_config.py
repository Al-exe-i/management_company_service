import unittest

from sqlalchemy.engine import make_url

from app.core.config import Settings


class ConfigurationTests(unittest.TestCase):
    def test_database_password_with_url_characters(self):
        config = Settings(
            _env_file=None,
            POSTGRES_USER="uk_admin",
            POSTGRES_PASSWORD="test@:/?#%+ password",
            POSTGRES_SERVER="db",
            POSTGRES_PORT="5432",
            POSTGRES_DB="uk_test",
            SECRET_KEY="isolated-configuration-test-secret",
            CORS_ORIGINS=["https://uk.example.org"],
        )
        url = make_url(config.DATABASE_URL)
        self.assertEqual(url.drivername, "postgresql+asyncpg")
        self.assertEqual(url.password, config.POSTGRES_PASSWORD)
        self.assertEqual(url.host, "db")
        self.assertEqual(config.CORS_ORIGINS, ["https://uk.example.org"])
