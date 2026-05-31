'''
Загрузка переменных окружения .env

'''


from pydantic_settings import BaseSettings
from pydantic import ConfigDict



class Settings(BaseSettings):
    
    DATABASE_URL_ASYNC: str                 # URL подключения к PostgreSQL с asyncpg драйвером

    DEBUG: bool
    POSTGRES_DB: str                        # Имя базы
    POSTGRES_USER: str                      # Пользователь базы
    POSTGRES_PASSWORD: str                  # Пароль базы
        
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )

settings = Settings()