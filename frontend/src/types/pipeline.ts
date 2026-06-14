import type { LitMiningResult, EnrichmentResult, CandidateTarget } from './targetIdentification'
import type { HitDiscoveryResult } from './hitDiscovery'

export type PipelineStage =
  | 'target_identification'
  | 'hit_discovery'
  | 'lead_optimization'
  | 'preclinical'
  | 'clinical_trials'
  | 'regulatory_approval'

export const PIPELINE_STAGES: { id: PipelineStage; label: string }[] = [
  { id: 'target_identification', label: 'Target Identification' },
  { id: 'hit_discovery', label: 'Hit Discovery' },
  { id: 'lead_optimization', label: 'Lead Optimization' },
  { id: 'preclinical', label: 'Preclinical' },
  { id: 'clinical_trials', label: 'Clinical Trials' },
  { id: 'regulatory_approval', label: 'Regulatory Approval' },
]

export interface SessionSnapshot {
  version: 1
  exportedAt: string
  activeStage: PipelineStage
  litMiningResult: LitMiningResult | null
  enrichmentResult: EnrichmentResult | null
  selectedTargets: CandidateTarget[]
  hitDiscoveryResult?: HitDiscoveryResult | null
}
