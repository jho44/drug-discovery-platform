import { useState } from 'react'
import type { CompoundHit, TargetHits } from '../../../types/hitDiscovery'
import { CompoundHitCard } from './CompoundHitCard'

type Tab = 'docking' | 'consensus' | 'ligand' | 'repurposing' | 'fragment' | 'hts'

const TABS: { id: Tab; label: string; key: keyof TargetHits }[] = [
  { id: 'docking', label: 'Docking', key: 'docking_hits' },
  { id: 'consensus', label: 'Consensus', key: 'consensus_hits' },
  { id: 'ligand', label: 'Ligand-Based', key: 'ligand_based_hits' },
  { id: 'repurposing', label: 'Repurposing', key: 'repurposing_hits' },
  { id: 'fragment', label: 'Fragments', key: 'fragment_hits' },
  { id: 'hts', label: 'HTS', key: 'hts_hits' },
]

function HitCount({ n }: { n: number }) {
  if (n === 0) return null
  return (
    <span className="ml-1.5 bg-gray-100 text-gray-500 text-xs px-1.5 py-0.5 rounded-full">
      {n}
    </span>
  )
}

export function TargetHitsPanel({ target }: { target: TargetHits }) {
  const [activeTab, setActiveTab] = useState<Tab>(
    target.docking_hits?.length ? 'docking' : 'consensus'
  )

  const currentHits = (target[TABS.find((t) => t.id === activeTab)!.key] as CompoundHit[]) ?? []

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Target header */}
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-gray-900">{target.target_name}</span>
          {target.uniprot_id && (
            <a
              href={`https://www.uniprot.org/uniprotkb/${target.uniprot_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-mono bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded hover:underline"
            >
              {target.uniprot_id}
            </a>
          )}
          {target.chembl_target_id && (
            <a
              href={`https://www.ebi.ac.uk/chembl/target_report_card/${target.chembl_target_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-mono bg-amber-50 text-amber-700 px-1.5 py-0.5 rounded hover:underline"
            >
              {target.chembl_target_id}
            </a>
          )}
        </div>
        <span className="text-xs text-gray-400">{target.total_hits} unique compounds</span>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 overflow-x-auto">
        {TABS.map((tab) => {
          const hits = target[tab.key] as CompoundHit[]
          const count = hits?.length ?? 0
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={[
                'px-4 py-2 text-sm font-medium border-b-2 whitespace-nowrap transition-colors',
                activeTab === tab.id
                  ? 'border-lab-600 text-lab-700'
                  : 'border-transparent text-gray-500 hover:text-gray-700',
              ].join(' ')}
            >
              {tab.label}
              <HitCount n={count} />
            </button>
          )
        })}
      </div>

      {/* Tab content */}
      <div className="p-4">
        {currentHits.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-6">No hits found for this method.</p>
        ) : (
          <div className="space-y-2">
            {currentHits.map((hit) => (
              <CompoundHitCard key={`${hit.compound_id}-${hit.method}`} hit={hit} />
            ))}
          </div>
        )}
      </div>

      {/* Claude summary */}
      {target.claude_summary && (
        <div className="px-4 py-3 border-t border-gray-100 bg-lab-50">
          <p className="text-xs font-medium text-lab-700 mb-1">Claude assessment</p>
          <p className="text-sm text-lab-800">{target.claude_summary}</p>
        </div>
      )}
    </div>
  )
}
