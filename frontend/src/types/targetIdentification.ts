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

// --- Enrichment types ---

export interface GeneticAssociationEvidence {
  disease_name: string
  association_score: number
  source: string
}

export interface TractabilityEvidence {
  small_molecule_score: number | null
  antibody_score: number | null
  assessment: string
}

export interface OpenTargetsEvidence {
  ensembl_id: string | null
  tractability: TractabilityEvidence | null
  genetic_associations: GeneticAssociationEvidence[]
  mouse_phenotypes: string[]
  safety_liabilities: string[]
}

export interface TissueExpressionEvidence {
  tissue: string
  rna_level: string
}

export interface CancerPathologyEvidence {
  cancer_type: string
  high_expression_percent: number
  survival_correlation: string | null
}

export interface HPAEvidence {
  protein_class: string[]
  tissue_expression: TissueExpressionEvidence[]
  cancer_pathology: CancerPathologyEvidence[]
  subcellular_locations: string[]
  hpa_url: string | null
}

export interface EnrichedTarget {
  literature: CandidateTarget
  opentargets: OpenTargetsEvidence | null
  hpa: HPAEvidence | null
  integrated_confidence: 'high' | 'medium' | 'low'
  integrated_rationale: string
  validation_summary: string
  consensus_score: number | null
  methods_confirmed: number
  total_methods: number
}

export interface EnrichmentRequest {
  original_query: string
  candidate_targets: CandidateTarget[]
}

export interface EnrichmentResult {
  original_query: string
  enriched_targets: EnrichedTarget[]
  enrichment_summary: string
  methods_used: string[]
  targets_enriched: number
  targets_not_found_in_ot: string[]
  targets_not_found_in_hpa: string[]
}
