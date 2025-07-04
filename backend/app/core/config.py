from pydantic_settings import BaseSettings
from typing import List, Any, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "GovBidGenie"
    API_V1_STR: str = "/api/v1"

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[Any] = ["*"]

    # Database settings
    DATABASE_URL: Optional[str] = None

    # Azure DevOps settings
    ADO_ORG_URL: Optional[str] = None
    ADO_PAT: Optional[str] = None

    # External API Keys
    OPENAI_API_KEY: Optional[str] = None
    SAM_API_KEY: Optional[str] = None
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_PAGE_ID: Optional[str] = None
    FACEBOOK_PAGE_ACCESS_TOKEN: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = 'ignore'

settings = Settings()
