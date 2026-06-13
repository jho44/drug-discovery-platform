import { post } from './client'
import type { LitMiningRequest, LitMiningResult, EnrichmentRequest, EnrichmentResult } from '../types/targetIdentification'

export function runLiteratureMining(request: LitMiningRequest): Promise<LitMiningResult> {
  return post<LitMiningResult>('/target-identification/literature-mining', request)
}

export function runEnrichment(request: EnrichmentRequest): Promise<EnrichmentResult> {
  return post<EnrichmentResult>('/target-identification/enrich', request)
}
