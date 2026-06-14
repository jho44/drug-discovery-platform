import { usePipelineStore } from '../../../store/pipelineStore'
import { useHitDiscovery } from '../../../hooks/useHitDiscovery'
import { LoadingSpinner } from '../../shared/LoadingSpinner'
import { ErrorBanner } from '../../shared/ErrorBanner'
import { TargetHitsPanel } from './TargetHitsPanel'

export function HitDiscovery() {
  const selectedTargets = usePipelineStore((s) => s.selectedTargets)
  const { result, loading, error, run } = useHitDiscovery()

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Hit Discovery</h2>
        <p className="text-sm text-gray-500 mt-1">
          Find candidate compounds using four parallel methods: ligand similarity (ChEMBL known
          actives), drug repurposing (ChEMBL + OpenTargets), fragment screening (Rule of Three),
          and experimental HTS data (PubChem BioAssay).
        </p>
      </div>

      {/* Selected targets summary */}
      {selectedTargets.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
          <p className="text-sm font-medium text-gray-700">
            {selectedTargets.length} target{selectedTargets.length !== 1 ? 's' : ''} from Stage 1
          </p>
          <div className="flex flex-wrap gap-3">
            {selectedTargets.map((t) => (
              <div key={t.name} className="flex items-center gap-1.5">
                <span className="text-sm font-medium text-gray-800">{t.name}</span>
                {t.uniprot_id ? (
                  <a
                    href={`https://www.uniprot.org/uniprotkb/${t.uniprot_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-mono bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded hover:underline"
                  >
                    {t.uniprot_id}
                  </a>
                ) : (
                  <span className="text-xs text-gray-300 italic">UniProt unresolved</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Run button — shown when no results yet */}
      {!result && !loading && selectedTargets.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <div className="text-xs text-gray-400 space-y-1">
            <p>This step will query:</p>
            <ul className="list-disc list-inside space-y-0.5 ml-2">
              <li>ChEMBL — known actives (pChEMBL ≥ 6) + Tanimoto similarity search</li>
              <li>ChEMBL — Rule-of-Three fragments (MW ≤ 300, HBD ≤ 3)</li>
              <li>OpenTargets — approved and clinical-stage drugs for this target</li>
              <li>PubChem BioAssay — experimental HTS active compounds</li>
              <li>Claude — integrated medicinal chemistry assessment</li>
            </ul>
            <p className="mt-2 italic">Takes ~20–40 seconds depending on number of targets.</p>
          </div>
          <button
            onClick={() => run(selectedTargets)}
            className="px-5 py-2.5 bg-lab-600 text-white text-sm font-medium rounded-md hover:bg-lab-700 transition-colors"
          >
            Run Hit Discovery for {selectedTargets.length} target{selectedTargets.length !== 1 ? 's' : ''}
          </button>
        </div>
      )}

      {loading && (
        <LoadingSpinner message="Querying ChEMBL, OpenTargets, and PubChem, then synthesizing with Claude..." />
      )}

      {error && <ErrorBanner message={error} />}

      {result && !loading && (
        <div className="space-y-6">
          {/* Overall summary */}
          <div className="bg-lab-50 border border-lab-100 rounded-lg p-4 space-y-2">
            <p className="text-sm font-medium text-lab-900">Run Summary</p>
            <p className="text-sm text-lab-800">{result.overall_summary}</p>
            <div className="flex flex-wrap gap-2 mt-2">
              {result.methods_used.map((m) => (
                <span key={m} className="text-xs bg-lab-100 text-lab-700 px-2 py-0.5 rounded-full">
                  {m}
                </span>
              ))}
            </div>
          </div>

          {/* Per-target panels */}
          {result.target_results.map((target) => (
            <TargetHitsPanel key={target.target_name} target={target} />
          ))}

          <button
            onClick={() => run(selectedTargets)}
            className="text-sm text-lab-600 hover:text-lab-700 underline"
          >
            Re-run hit discovery
          </button>
        </div>
      )}

      {selectedTargets.length === 0 && (
        <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg p-8 text-center text-gray-400 text-sm">
          No targets selected. Go to Target Identification and select targets to continue.
        </div>
      )}
    </div>
  )
}
