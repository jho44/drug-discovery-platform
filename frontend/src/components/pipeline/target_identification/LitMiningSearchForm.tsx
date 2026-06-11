import { useState } from 'react'

const EXAMPLES = [
  'BRAF-V600E NSCLC',
  'osimertinib resistance in EGFR-mutant lung cancer',
  'apoptosis in triple-negative breast cancer',
  'CDK4/6 inhibitor resistance in ER+ breast cancer',
]

interface Props {
  onSearch: (query: string) => void
  loading: boolean
}

export function LitMiningSearchForm({ onSearch, loading }: Props) {
  const [query, setQuery] = useState('')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (query.trim()) onSearch(query.trim())
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Search query
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder={EXAMPLES[0]}
            className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-lab-500 focus:outline-none focus:ring-1 focus:ring-lab-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-4 py-2 bg-lab-600 text-white text-sm font-medium rounded-md hover:bg-lab-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Mining...' : 'Mine Literature'}
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="text-xs text-gray-500">Examples:</span>
        {EXAMPLES.map(ex => (
          <button
            key={ex}
            type="button"
            onClick={() => setQuery(ex)}
            className="text-xs text-lab-600 hover:text-lab-800 underline"
          >
            {ex}
          </button>
        ))}
      </div>

      <p className="text-xs text-gray-400">
        Tip: specific queries (gene + mutation + disease) produce more useful results than broad terms.
      </p>
    </form>
  )
}
