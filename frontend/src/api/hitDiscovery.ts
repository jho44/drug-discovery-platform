import { post } from './client'
import type { HitDiscoveryRequest, HitDiscoveryResult } from '../types/hitDiscovery'

export function runHitDiscovery(request: HitDiscoveryRequest): Promise<HitDiscoveryResult> {
  return post<HitDiscoveryResult>('/hit-discovery/run', request)
}
