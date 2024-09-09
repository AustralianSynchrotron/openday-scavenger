from functools import lru_cache
from typing import Annotated, Literal
from typing import get_args as get_args_typing

from pydantic import HttpUrl, TypeAdapter, UrlConstraints, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["get_settings"]


# Type definitions for the database systems and URIs the application supports
Allowed_DB_Types = Literal["sqlite", "postgresql"]

DatabaseDsn = Annotated[
    MultiHostUrl,
    UrlConstraints(
        host_required=False,
        allowed_schemes=get_args_typing(Allowed_DB_Types),
    ),
]


class Settings(BaseSettings):
    """The settings for the application use environment variables as per the 12-factor app principle."""

    # The default values for the database are an in-memory sqlite database
    BASE_URL: HttpUrl = HttpUrl(
        "http://localhost:8000"
    )  # the base scheme, host and port of the application
    # (required to generate QR code links and restrict the cookie)

    DATABASE_SCHEME: Allowed_DB_Types = "sqlite"
    DATABASE_NAME: str = ":memory:"
    DATABASE_HOST: str = ""
    DATABASE_PORT: int | None = None
    DATABASE_USER: str | None = None
    DATABASE_PASSWORD: str | None = None

    COOKIE_KEY: str = "SYNOD_SESSION"
    COOKIE_MAX_AGE: int = 86400  # in seconds: 24 hours = 86400 seconds

    SESSIONS_ENABLED: bool = True

    model_config = SettingsConfigDict(env_file=".env")

    @computed_field()  # type: ignore[misc]
    @property
    def DATABASE_URI(self) -> DatabaseDsn:
        """Construct the database uri from the individual fields"""
        db_uri = MultiHostUrl.build(
            scheme=self.DATABASE_SCHEME,
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            path=self.DATABASE_NAME,
        )

        # Validate the constructed database URI. Not really needed, but doesn't harm either.
        TypeAdapter(DatabaseDsn).validate_python(db_uri)
        return db_uri


@lru_cache()
def get_settings() -> Settings:
    """Cache the settings, this allows the settings to be used in dependencies and for overwriting in tests"""
    return Settings()
