import { useState } from 'react'
import type { CompoundHit } from '../../../types/hitDiscovery'

const METHOD_STYLE: Record<string, string> = {
  ligand_similarity: 'bg-blue-100 text-blue-700',
  repurposing: 'bg-purple-100 text-purple-700',
  fragment: 'bg-green-100 text-green-700',
  hts: 'bg-orange-100 text-orange-700',
}

const METHOD_LABEL: Record<string, string> = {
  ligand_similarity: 'Ligand',
  repurposing: 'Repurposing',
  fragment: 'Fragment',
  hts: 'HTS',
}

const PHASE_STYLE: Record<number, string> = {
  4: 'bg-green-100 text-green-700',
  3: 'bg-yellow-100 text-yellow-700',
  2: 'bg-gray-100 text-gray-600',
  1: 'bg-gray-100 text-gray-500',
}

const PHASE_LABEL: Record<number, string> = {
  4: 'Approved',
  3: 'Phase 3',
  2: 'Phase 2',
  1: 'Phase 1',
}

function compoundUrl(hit: CompoundHit): string {
  if (hit.source === 'PubChem') {
    return `https://pubchem.ncbi.nlm.nih.gov/compound/${hit.compound_id}`
  }
  if (hit.source === 'OpenTargets') {
    return `https://platform.opentargets.org/drug/${hit.compound_id}`
  }
  return `https://www.ebi.ac.uk/chembl/compound_report_card/${hit.compound_id}`
}

export function CompoundHitCard({ hit }: { hit: CompoundHit }) {
  const [imgFailed, setImgFailed] = useState(false)

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 flex gap-3 hover:border-gray-300 transition-colors">
      {/* Structure image */}
      <div className="shrink-0 w-16 h-16 bg-gray-50 rounded border border-gray-100 flex items-center justify-center overflow-hidden">
        {hit.image_url && !imgFailed ? (
          <img
            src={hit.image_url}
            alt={hit.compound_id}
            className="w-full h-full object-contain"
            onError={() => setImgFailed(true)}
          />
        ) : (
          <span className="text-xs text-gray-400 text-center font-mono px-1 break-all leading-tight">
            {hit.compound_id}
          </span>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0 space-y-1">
        <div className="flex items-center gap-1.5 flex-wrap">
          <a
            href={compoundUrl(hit)}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-mono font-medium text-blue-600 hover:underline truncate"
          >
            {hit.compound_id}
          </a>
          <span className={`text-xs px-1.5 py-0.5 rounded-full ${METHOD_STYLE[hit.method] ?? ''}`}>
            {METHOD_LABEL[hit.method] ?? hit.method}
          </span>
          {hit.max_phase != null && PHASE_LABEL[hit.max_phase] && (
            <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${PHASE_STYLE[hit.max_phase] ?? 'bg-gray-100 text-gray-500'}`}>
              {PHASE_LABEL[hit.max_phase]}
            </span>
          )}
        </div>

        {hit.name && (
          <p className="text-xs text-gray-600 truncate">{hit.name}</p>
        )}

        <div className="flex items-center gap-3 text-xs text-gray-500 flex-wrap">
          {hit.activity_value != null && (
            <span>
              {hit.activity_unit === 'pChEMBL'
                ? `pChEMBL ${hit.activity_value.toFixed(1)}`
                : `Activity ${hit.activity_value.toFixed(1)}`}
            </span>
          )}
          {hit.molecular_weight != null && (
            <span>MW {hit.molecular_weight.toFixed(0)}</span>
          )}
          {hit.indication && (
            <span className="truncate max-w-[12rem]" title={hit.indication}>
              {hit.indication}
            </span>
          )}
          {hit.consensus_score != null && (
            <span className="text-lab-600 font-medium">
              consensus {(hit.consensus_score * 100).toFixed(0)}%
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
