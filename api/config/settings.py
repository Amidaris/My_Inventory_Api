from pydantic_settings import BaseSettings
from pydantic import computed_field
from pydantic import SecretStr
from pydantic import ConfigDict


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: SecretStr
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Logs
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str
    LOG_BACKUP_COUNT: int = 14
    # directory where uploaded documents are stored
    DOCUMENTS_DIR: str = "./documents"

    # Documents storage
    DOCUMENTS_DIR: str = "documents"

    # Pydantic v2 config
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @computed_field
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

   
settings = Settings()
