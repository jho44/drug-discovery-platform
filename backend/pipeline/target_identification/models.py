from pydantic import BaseModel, Field


class LitMiningRequest(BaseModel):
    query: str = Field(..., description="Free-text PubMed search query")
    max_abstracts: int = Field(default=15, ge=1, le=40)


class Evidence(BaseModel):
    pmid: str
    quote: str
    relation: str


class CandidateTarget(BaseModel):
    name: str
    type: str
    rationale: str
    confidence: str
    evidence: list[Evidence]


class Relation(BaseModel):
    subject: str
    relation: str
    object: str
    pmid: str


class Entities(BaseModel):
    genes_proteins: list[str]
    diseases: list[str]


class AbstractMeta(BaseModel):
    pmid: str
    title: str
    authors: list[str]
    journal: str
    year: str


class LitMiningResult(BaseModel):
    query: str
    abstracts_fetched: int
    abstracts_meta: list[AbstractMeta]
    entities: Entities
    relations: list[Relation]
    candidate_targets: list[CandidateTarget]
    summary: str
