from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    pubmed_base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    claude_model: str = "claude-sonnet-4-20250514"
    max_abstracts_per_query: int = 20
    opentargets_graphql_url: str = "https://api.platform.opentargets.org/api/v4/graphql"
    hpa_base_url: str = "https://www.proteinatlas.org"
    max_targets_to_enrich: int = 10
    chembl_api_url: str = "https://www.ebi.ac.uk/chembl/api/data"
    pubchem_api_url: str = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

    model_config = {"env_file": ".env"}


settings = Settings()
