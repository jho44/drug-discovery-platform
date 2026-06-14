import { useState } from 'react'
import { runHitDiscovery } from '../api/hitDiscovery'
import { usePipelineStore } from '../store/pipelineStore'
import type { CandidateTarget } from '../types/targetIdentification'

export function useHitDiscovery() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hitDiscoveryResult = usePipelineStore((s) => s.hitDiscoveryResult)
  const setHitDiscoveryResult = usePipelineStore((s) => s.setHitDiscoveryResult)

  async function run(targets: CandidateTarget[]) {
    setLoading(true)
    setError(null)
    try {
      const data = await runHitDiscovery({ selected_targets: targets })
      setHitDiscoveryResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return { result: hitDiscoveryResult, loading, error, run }
}
