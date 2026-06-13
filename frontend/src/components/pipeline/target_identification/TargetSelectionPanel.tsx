import { useState, useEffect } from 'react'
import { usePipelineStore } from '../../../store/pipelineStore'
import type { CandidateTarget } from '../../../types/targetIdentification'

const CONF_STYLE: Record<string, string> = {
  high: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-gray-100 text-gray-500',
}

function TargetRow({
  target,
  checked,
  integratedConfidence,
  methodsConfirmed,
  totalMethods,
  onChange,
}: {
  target: CandidateTarget
  checked: boolean
  integratedConfidence?: string
  methodsConfirmed?: number
  totalMethods?: number
  onChange: (checked: boolean) => void
}) {
  return (
    <label className="flex items-center gap-3 px-4 py-3 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 cursor-pointer transition-colors group">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="w-4 h-4 rounded border-gray-300 text-lab-600 focus:ring-lab-500"
      />

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-medium text-gray-900">{target.name}</span>
          {target.uniprot_id ? (
            <a
              href={`https://www.uniprot.org/uniprotkb/${target.uniprot_id}`}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-xs font-mono bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded hover:underline"
            >
              {target.uniprot_id}
            </a>
          ) : (
            <span className="text-xs text-gray-300 italic">UniProt unresolved</span>
          )}
        </div>
        {target.uniprot_name && (
          <p className="text-xs text-gray-400 mt-0.5 truncate">{target.uniprot_name}</p>
        )}
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {/* Lit mining confidence */}
        <span className={`text-xs px-2 py-0.5 rounded-full ${CONF_STYLE[target.confidence] ?? ''}`}>
          Lit: {target.confidence}
        </span>

        {/* Integrated confidence if enrichment was run */}
        {integratedConfidence && (
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full border ${CONF_STYLE[integratedConfidence] ?? ''}`}
          >
            Overall: {integratedConfidence}
          </span>
        )}

        {/* Source count */}
        {methodsConfirmed !== undefined && totalMethods !== undefined && (
          <span className="text-xs text-gray-400">{methodsConfirmed}/{totalMethods} sources</span>
        )}
      </div>
    </label>
  )
}

export function TargetSelectionPanel() {
  const litResult = usePipelineStore((s) => s.litMiningResult)
  const enrichmentResult = usePipelineStore((s) => s.enrichmentResult)
  const selectedTargets = usePipelineStore((s) => s.selectedTargets)
  const setSelectedTargets = usePipelineStore((s) => s.setSelectedTargets)
  const setActiveStage = usePipelineStore((s) => s.setActiveStage)

  const [checkedNames, setCheckedNames] = useState<Set<string>>(
    new Set(selectedTargets.map((t) => t.name)),
  )

  // Sync checked state when store selection changes (e.g. page reload)
  useEffect(() => {
    setCheckedNames(new Set(selectedTargets.map((t) => t.name)))
  }, [])

  if (!litResult || litResult.candidate_targets.length === 0) return null

  // Build lookup from enrichment results for richer display
  const enrichedByName = Object.fromEntries(
    (enrichmentResult?.enriched_targets ?? []).map((e) => [e.literature.name, e]),
  )

  function toggle(name: string, on: boolean) {
    setCheckedNames((prev) => {
      const next = new Set(prev)
      on ? next.add(name) : next.delete(name)
      return next
    })
  }

  function handleConfirm() {
    const chosen = litResult!.candidate_targets.filter((t) => checkedNames.has(t.name))
    setSelectedTargets(chosen)
    setActiveStage('hit_discovery')
  }

  const checkedCount = checkedNames.size

  return (
    <div className="border-t-2 border-lab-100 pt-6 mt-6 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-base font-semibold text-gray-900">
            Carry Targets to Hit Identification
          </h3>
          <p className="text-sm text-gray-500 mt-0.5">
            Select the targets you want to investigate further. Your selection will become the
            input to Stage 2 — virtual screening and known-active lookups.
          </p>
        </div>
        {selectedTargets.length > 0 && (
          <span className="shrink-0 text-xs text-green-600 bg-green-50 px-2.5 py-1 rounded-full">
            {selectedTargets.length} previously selected
          </span>
        )}
      </div>

      <div className="space-y-2">
        {litResult.candidate_targets.map((target) => {
          const enriched = enrichedByName[target.name]
          return (
            <TargetRow
              key={target.name}
              target={target}
              checked={checkedNames.has(target.name)}
              integratedConfidence={enriched?.integrated_confidence}
              methodsConfirmed={enriched?.methods_confirmed}
              totalMethods={enriched?.total_methods}
              onChange={(on) => toggle(target.name, on)}
            />
          )
        })}
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={handleConfirm}
          disabled={checkedCount === 0}
          className="px-5 py-2.5 bg-lab-600 text-white text-sm font-medium rounded-md hover:bg-lab-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          Carry {checkedCount > 0 ? checkedCount : ''} target{checkedCount !== 1 ? 's' : ''} to Hit Identification →
        </button>
        {checkedCount === 0 && (
          <span className="text-xs text-gray-400">Select at least one target</span>
        )}
      </div>
    </div>
  )
}
