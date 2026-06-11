export interface LitMiningRequest {
  query: string
  max_abstracts?: number
}

export interface Evidence {
  pmid: string
  quote: string
  relation: string
}

export interface CandidateTarget {
  name: string
  type: string
  rationale: string
  confidence: 'high' | 'medium' | 'low'
  evidence: Evidence[]
}

export interface Relation {
  subject: string
  relation: string
  object: string
  pmid: string
}

export interface Entities {
  genes_proteins: string[]
  diseases: string[]
}

export interface AbstractMeta {
  pmid: string
  title: string
  authors: string[]
  journal: string
  year: string
}

export interface LitMiningResult {
  query: string
  abstracts_fetched: number
  abstracts_meta: AbstractMeta[]
  entities: Entities
  relations: Relation[]
  candidate_targets: CandidateTarget[]
  summary: string
}
