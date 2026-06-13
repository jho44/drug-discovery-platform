import { useState } from 'react'
import { runEnrichment } from '../api/targetIdentification'
import { usePipelineStore } from '../store/pipelineStore'
import type { CandidateTarget } from '../types/targetIdentification'

export function useTargetEnrichment() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const enrichmentResult = usePipelineStore((s) => s.enrichmentResult)
  const setEnrichmentResult = usePipelineStore((s) => s.setEnrichmentResult)

  async function enrich(query: string, candidates: CandidateTarget[]) {
    setLoading(true)
    setError(null)
    try {
      const data = await runEnrichment({ original_query: query, candidate_targets: candidates })
      setEnrichmentResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return { result: enrichmentResult, loading, error, enrich }
}
