from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GovBidGenie"
    API_V1_STR: str = "/api/v1"

    # Database settings
    DATABASE_URL: str

    # Azure DevOps settings
    ADO_ORG_URL: str
    ADO_PAT: str

    # External API Keys
    OPENAI_API_KEY: str | None = None
    SAM_API_KEY: str | None = None

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = 'ignore'

settings = Settings()
