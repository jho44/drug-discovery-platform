import { useState } from 'react'
import { runLiteratureMining } from '../api/targetIdentification'
import type { LitMiningResult } from '../types/targetIdentification'

export function useLiteratureMining() {
  const [result, setResult] = useState<LitMiningResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function search(query: string, maxAbstracts = 15) {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await runLiteratureMining({ query, max_abstracts: maxAbstracts })
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return { result, loading, error, search }
}
