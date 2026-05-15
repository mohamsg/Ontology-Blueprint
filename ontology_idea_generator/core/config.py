import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    grouped_ontology_path: str
    merged_ideas_path: str
    source_text_path: str
    output_path: str
    model_name: str = "claude-3-5-sonnet-20240620"
    max_tokens_per_call: int = 4000
    ideas_per_group: int = 10
    output_format: str = "markdown"
    anthropic_api_key: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    def validate(self) -> bool:
        from .logger import logger
        if not os.path.exists(self.grouped_ontology_path):
            logger.error(f"Grouped ontology path does not exist: {self.grouped_ontology_path}")
            return False
        if not os.path.exists(self.merged_ideas_path):
            logger.error(f"Merged ideas path does not exist: {self.merged_ideas_path}")
            return False
        if not os.path.exists(self.source_text_path):
            logger.error(f"Source text path does not exist: {self.source_text_path}")
            return False
        if self.ideas_per_group <= 0:
            logger.error(f"Ideas per group must be positive, got: {self.ideas_per_group}")
            return False
        if self.output_format not in ["markdown", "json", "text"]:
            logger.error(f"Invalid output format: {self.output_format}")
            return False
        return True

    @classmethod
    def load_from_env(cls) -> "Config":
        return cls()
