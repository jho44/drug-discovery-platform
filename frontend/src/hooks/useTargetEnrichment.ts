import { useState } from 'react'
import { runEnrichment } from '../api/targetIdentification'
import type { CandidateTarget, EnrichmentResult } from '../types/targetIdentification'

export function useTargetEnrichment() {
  const [result, setResult] = useState<EnrichmentResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function enrich(query: string, candidates: CandidateTarget[]) {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await runEnrichment({ original_query: query, candidate_targets: candidates })
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return { result, loading, error, enrich }
}
