import { usePipelineStore } from '../../../store/pipelineStore'
import { LiteratureMining } from './LiteratureMining'
import { TargetEnrichment } from './TargetEnrichment'
import { TargetSelectionPanel } from './TargetSelectionPanel'

type Tab = 'literature' | 'enrichment'
import { useState } from 'react'

export function TargetIdentificationStage() {
  const [activeTab, setActiveTab] = useState<Tab>('literature')
  const litResult = usePipelineStore((s) => s.litMiningResult)

  const enrichmentUnlocked = litResult !== null && litResult.candidate_targets.length > 0

  return (
    <div className="space-y-0">
      {/* Method tabs */}
      <div className="flex border-b border-gray-200 mb-6">
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
          title={!enrichmentUnlocked ? 'Run literature mining first' : undefined}
        >
          Target Enrichment
          <span className="ml-1.5 text-xs text-gray-300">(optional)</span>
        </button>
      </div>

      {/* Tab content */}
      {activeTab === 'literature' && <LiteratureMining />}
      {activeTab === 'enrichment' && <TargetEnrichment />}

      {/* Selection panel — always visible once lit mining has results */}
      <TargetSelectionPanel />
    </div>
  )
}
