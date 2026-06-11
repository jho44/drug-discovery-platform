from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    pubmed_base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    claude_model: str = "claude-sonnet-4-20250514"
    max_abstracts_per_query: int = 20

    model_config = {"env_file": ".env"}


settings = Settings()
