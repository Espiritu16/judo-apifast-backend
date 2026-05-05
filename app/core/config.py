from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = 'JUDO API'
    APP_VERSION: str = '0.1.0'
    API_PREFIX: str = '/api/v1'

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
