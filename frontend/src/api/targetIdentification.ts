import { post } from './client'
import type { LitMiningRequest, LitMiningResult } from '../types/targetIdentification'

export function runLiteratureMining(request: LitMiningRequest): Promise<LitMiningResult> {
  return post<LitMiningResult>('/target-identification/literature-mining', request)
}
