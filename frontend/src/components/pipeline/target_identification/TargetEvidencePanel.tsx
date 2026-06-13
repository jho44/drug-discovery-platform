import { EvidenceCard } from '../../shared/EvidenceCard'
import type { CandidateTarget } from '../../../types/targetIdentification'

const CONFIDENCE_STYLES: Record<string, string> = {
  high: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-gray-100 text-gray-600',
}

interface Props {
  target: CandidateTarget
  /** When true, renders without the outer border card (for embedding inside EnrichedTargetCard) */
  embedded?: boolean
}

export function TargetEvidencePanel({ target, embedded = false }: Props) {
  const inner = (
    <div className="space-y-3">
      {!embedded && (
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="font-semibold text-gray-900 text-base">{target.name}</h3>
            <span className="text-xs text-gray-500 uppercase tracking-wide">{target.type}</span>
          </div>
          <span
            className={`text-xs font-medium px-2 py-1 rounded-full shrink-0 ${
              CONFIDENCE_STYLES[target.confidence] ?? CONFIDENCE_STYLES.low
            }`}
          >
            {target.confidence} confidence
          </span>
        </div>
      )}

      <p className="text-sm text-gray-600">{target.rationale}</p>

      {target.evidence.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            Supporting Evidence
          </p>
          {target.evidence.map((ev, i) => (
            <EvidenceCard key={i} pmid={ev.pmid} quote={ev.quote} relation={ev.relation} />
          ))}
        </div>
      )}
    </div>
  )

  if (embedded) return inner
  return <div className="border border-gray-200 rounded-lg p-4 bg-white">{inner}</div>
}
