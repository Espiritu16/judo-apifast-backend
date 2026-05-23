from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    APP_NAME: str = 'JUDO API'
    APP_VERSION: str = '0.1.0'
    API_PREFIX: str = '/api/v1'
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRE_MINUTES: int = 120
    FACTILIZA_API_TOKEN: str = ''
    FACTILIZA_API_BASE_URL: str = 'https://api.factiliza.com/v1'
    FACTILIZA_TIMEOUT_SECONDS: float = 10.0
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
settings = Settings()
