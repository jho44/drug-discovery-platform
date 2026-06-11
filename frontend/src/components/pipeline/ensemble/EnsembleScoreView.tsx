interface ScoredItem {
  name: string
  consensus_score: number
  appearances: number
  total_methods: number
}

interface Props {
  candidates: ScoredItem[]
  title?: string
}

export function EnsembleScoreView({ candidates, title = 'Ensemble Consensus' }: Props) {
  if (candidates.length === 0) return null

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-800 mb-3">{title}</h3>
      <div className="space-y-2">
        {candidates.map(c => (
          <div key={c.name} className="flex items-center gap-3">
            <span className="text-sm font-medium text-gray-700 w-32 shrink-0">{c.name}</span>
            <div className="flex-1 bg-gray-100 rounded-full h-2">
              <div
                className="bg-lab-500 rounded-full h-2 transition-all"
                style={{ width: `${c.consensus_score * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-500 shrink-0">
              {c.appearances}/{c.total_methods} methods
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
