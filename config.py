from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    В класі  будуть створюватись і валідуватись посилання з env файлу, що необхідні для роботи ботів та бази даних
    """
    # токени для ботів
    USER_BOT_TOKEN: SecretStr
    ADMIN_BOT_TOKEN: SecretStr

    # сховище зберігання у вигляді групи

    GROUP_ID:int

    # елементи для доступу до бази даних
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # елементи fsm (finite state machine)
    REDIS_PORT: int
    REDIS_HOST: str

    # номера суперадмінів
    SUPERADMIN_NUMBERS: str

    # читання env файлу, де зберігається все, щодо безпеки
    model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        """
        Буде повертати посилання для доступу до бази даних для asyncpg
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def redis_url(self) -> str:
        """
        Буде повертати посилання для підключення до Redis
        """
        return f"rediss://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    @property
    def superadmin_list(self) -> list[str]:  
        return [n.strip().replace("+", "") for n in self.SUPERADMIN_NUMBERS.split(",") if n.strip()]
    
settings = Settings()