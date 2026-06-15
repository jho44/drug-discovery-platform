export interface HitDiscoveryRequest {
  selected_targets: {
    name: string
    type: string
    rationale: string
    confidence: string
    evidence: { pmid: string; quote: string; relation: string }[]
    uniprot_id: string | null
    uniprot_name: string | null
  }[]
}

export interface CompoundHit {
  compound_id: string
  name: string | null
  smiles: string | null
  molecular_weight: number | null
  method: 'ligand_similarity' | 'repurposing' | 'fragment' | 'hts'
  source: 'ChEMBL' | 'OpenTargets' | 'PubChem'
  activity_value: number | null
  activity_unit: string | null
  indication: string | null
  max_phase: number | null
  assay_id: string | null
  consensus_score: number | null
  docking_score: number | null  // kcal/mol from AutoDock Vina; more negative = better binding
  image_url: string | null
}

export interface TargetHits {
  target_name: string
  uniprot_id: string | null
  chembl_target_id: string | null
  ligand_based_hits: CompoundHit[]
  repurposing_hits: CompoundHit[]
  fragment_hits: CompoundHit[]
  hts_hits: CompoundHit[]
  consensus_hits: CompoundHit[]
  docking_hits: CompoundHit[]  // consensus hits ranked by Vina docking score
  claude_summary: string
  methods_run: string[]
  total_hits: number
}

export interface HitDiscoveryResult {
  query_targets: string[]
  target_results: TargetHits[]
  overall_summary: string
  methods_used: string[]
  total_compounds_found: number
}
