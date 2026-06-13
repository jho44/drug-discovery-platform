import { useState } from 'react'
import type { EnrichedTarget } from '../../../types/targetIdentification'
import { TargetEvidencePanel } from './TargetEvidencePanel'
import { OpenTargetsEvidencePanel } from './OpenTargetsEvidencePanel'
import { HPAEvidencePanel } from './HPAEvidencePanel'

interface Props {
  target: EnrichedTarget
  rank: number
}

const CONF_STYLE: Record<string, string> = {
  high: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-gray-100 text-gray-600',
}

const TABS = ['Literature', 'Genetic Evidence', 'Expression'] as const
type Tab = typeof TABS[number]

export function EnrichedTargetCard({ target, rank }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('Literature')
  const [expanded, setExpanded] = useState(rank === 0)

  return (
    <div className="border border-gray-200 rounded-lg bg-white overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full text-left flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3 min-w-0">
          <span className="text-lab-600 font-semibold shrink-0">#{rank + 1}</span>
          <span className="font-semibold text-gray-900 truncate">{target.literature.name}</span>
          <span className="text-xs text-gray-400 uppercase shrink-0">{target.literature.type}</span>
        </div>
        <div className="flex items-center gap-2 shrink-0 ml-3">
          {/* Original lit confidence */}
          <span className={`text-xs px-2 py-0.5 rounded-full ${CONF_STYLE[target.literature.confidence] ?? ''}`}>
            Lit: {target.literature.confidence}
          </span>
          {/* Integrated confidence */}
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full border ${CONF_STYLE[target.integrated_confidence] ?? ''}`}
            title="Integrated confidence combines literature, genetic, and expression evidence"
          >
            Overall: {target.integrated_confidence}
          </span>
          {/* Consensus badge */}
          {target.consensus_score !== null && (
            <span className="text-xs text-gray-400">
              {target.methods_confirmed}/{target.total_methods} sources
            </span>
          )}
          <span className="text-gray-400 text-xs ml-1">{expanded ? '▲' : '▼'}</span>
        </div>
      </button>

      {expanded && (
        <div className="border-t border-gray-100">
          {/* Validation summary */}
          {target.validation_summary && (
            <div className="px-4 py-2 bg-lab-50 border-b border-lab-100">
              <p className="text-sm text-lab-800">{target.validation_summary}</p>
            </div>
          )}

          {/* Integrated rationale */}
          {target.integrated_rationale && (
            <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">
              <p className="text-xs font-medium text-gray-500 mb-1">Integrated Assessment</p>
              <p className="text-sm text-gray-700">{target.integrated_rationale}</p>
            </div>
          )}

          {/* Tabs */}
          <div className="flex border-b border-gray-100">
            {TABS.map((tab) => {
              const disabled =
                (tab === 'Genetic Evidence' && !target.opentargets) ||
                (tab === 'Expression' && !target.hpa)
              return (
                <button
                  key={tab}
                  onClick={() => !disabled && setActiveTab(tab)}
                  disabled={disabled}
                  className={[
                    'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
                    activeTab === tab
                      ? 'border-lab-600 text-lab-700'
                      : disabled
                      ? 'border-transparent text-gray-300 cursor-default'
                      : 'border-transparent text-gray-500 hover:text-gray-700',
                  ].join(' ')}
                >
                  {tab}
                  {tab === 'Genetic Evidence' && !target.opentargets && (
                    <span className="ml-1 text-xs text-gray-300">(not found)</span>
                  )}
                  {tab === 'Expression' && !target.hpa && (
                    <span className="ml-1 text-xs text-gray-300">(not found)</span>
                  )}
                </button>
              )
            })}
          </div>

          {/* Tab content */}
          <div className="p-4">
            {activeTab === 'Literature' && (
              <TargetEvidencePanel target={target.literature} embedded />
            )}
            {activeTab === 'Genetic Evidence' && target.opentargets && (
              <OpenTargetsEvidencePanel evidence={target.opentargets} />
            )}
            {activeTab === 'Expression' && target.hpa && (
              <HPAEvidencePanel evidence={target.hpa} />
            )}
          </div>
        </div>
      )}
    </div>
  )
}
