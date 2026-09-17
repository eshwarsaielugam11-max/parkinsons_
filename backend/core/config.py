from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError, field_validator
from typing import List, Union
import json
import os
import sys

class Settings(BaseSettings):
    MODEL_VERSION: str
    ANTHROPIC_API_KEY: str
    DATABASE_URL: str
    VECTOR_DB_PATH: str
    BACKEND_CORS_ORIGINS: List[str]
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PD Voice Classification API"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if not v.startswith("["):
                return [i.strip() for i in v.split(",")]
            return json.loads(v)
        return v

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), '../.env'),
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
if not settings.MODEL_VERSION or not settings.ANTHROPIC_API_KEY:
    raise ValueError("FATAL CONFIG ERROR: MODEL_VERSION or ANTHROPIC_API_KEY cannot be empty.")
