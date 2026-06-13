import { useState } from 'react'
import { LiteratureMining } from './LiteratureMining'
import { TargetEnrichment } from './TargetEnrichment'
import type { LitMiningResult } from '../../../types/targetIdentification'

type Tab = 'literature' | 'enrichment'

export function TargetIdentificationStage() {
  const [activeTab, setActiveTab] = useState<Tab>('literature')
  const [litResult, setLitResult] = useState<LitMiningResult | null>(null)

  const enrichmentUnlocked = litResult !== null && litResult.candidate_targets.length > 0

  return (
    <div className="space-y-4">
      {/* Method tabs */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('literature')}
          className={[
            'px-5 py-2.5 text-sm font-medium border-b-2 transition-colors',
            activeTab === 'literature'
              ? 'border-lab-600 text-lab-700'
              : 'border-transparent text-gray-500 hover:text-gray-700',
          ].join(' ')}
        >
          Literature Mining
          {litResult && (
            <span className="ml-2 bg-green-100 text-green-600 text-xs px-1.5 py-0.5 rounded-full">
              {litResult.candidate_targets.length} targets
            </span>
          )}
        </button>
        <button
          onClick={() => enrichmentUnlocked && setActiveTab('enrichment')}
          disabled={!enrichmentUnlocked}
          className={[
            'px-5 py-2.5 text-sm font-medium border-b-2 transition-colors',
            activeTab === 'enrichment'
              ? 'border-lab-600 text-lab-700'
              : enrichmentUnlocked
              ? 'border-transparent text-gray-500 hover:text-gray-700'
              : 'border-transparent text-gray-300 cursor-default',
          ].join(' ')}
          title={!enrichmentUnlocked ? 'Run literature mining first to unlock enrichment' : undefined}
        >
          Target Enrichment
          <span className="ml-1.5 text-xs text-gray-300">(optional)</span>
          {!enrichmentUnlocked && (
            <span className="ml-2 text-xs text-gray-300">— run lit mining first</span>
          )}
        </button>
      </div>

      {/* Tab content */}
      {activeTab === 'literature' && (
        <LiteratureMining onComplete={setLitResult} />
      )}
      {activeTab === 'enrichment' && litResult && (
        <TargetEnrichment litResult={litResult} />
      )}
    </div>
  )
}
