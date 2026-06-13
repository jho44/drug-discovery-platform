import { useState } from 'react'
import { runLiteratureMining } from '../api/targetIdentification'
import { usePipelineStore } from '../store/pipelineStore'

export function useLiteratureMining() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const setLitMiningResult = usePipelineStore((s) => s.setLitMiningResult)

  async function search(query: string, maxAbstracts = 15) {
    setLoading(true)
    setError(null)
    try {
      const data = await runLiteratureMining({ query, max_abstracts: maxAbstracts })
      setLitMiningResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return { loading, error, search }
}
