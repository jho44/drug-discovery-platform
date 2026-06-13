import { useTargetEnrichment } from '../../../hooks/useTargetEnrichment'
import { LoadingSpinner } from '../../shared/LoadingSpinner'
import { ErrorBanner } from '../../shared/ErrorBanner'
import { EnrichedTargetCard } from './EnrichedTargetCard'
import { usePipelineStore } from '../../../store/pipelineStore'

export function TargetEnrichment() {
  const litResult = usePipelineStore((s) => s.litMiningResult)
  const { result, loading, error, enrich } = useTargetEnrichment()

  if (!litResult) return null

  function handleEnrich() {
    enrich(litResult!.query, litResult!.candidate_targets)
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Target Enrichment</h2>
        <p className="text-sm text-gray-500 mt-1">
          Validate literature candidates with genetic association evidence from OpenTargets
          and tissue expression data from Human Protein Atlas. Claude synthesizes all three
          sources into an integrated confidence score.
        </p>
      </div>

      {!result && !loading && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <div className="text-sm text-gray-600">
            <p className="font-medium text-gray-800 mb-1">
              {litResult.candidate_targets.length} candidate target
              {litResult.candidate_targets.length !== 1 ? 's' : ''} from literature mining:
            </p>
            <div className="flex flex-wrap gap-1.5 mt-2">
              {litResult.candidate_targets.map((t) => (
                <span key={t.name} className="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full">
                  {t.name}
                </span>
              ))}
            </div>
          </div>

          <div className="text-xs text-gray-400 space-y-1">
            <p>This step will query:</p>
            <ul className="list-disc list-inside space-y-0.5 ml-2">
              <li>OpenTargets Platform — genetic associations, tractability, mouse knockout phenotypes</li>
              <li>Human Protein Atlas — tissue RNA expression, cancer pathology data</li>
              <li>Claude — integrated synthesis across all three evidence sources</li>
            </ul>
            <p className="mt-2 italic">Takes ~15–30 seconds depending on number of targets.</p>
          </div>

          <button
            onClick={handleEnrich}
            className="px-5 py-2.5 bg-lab-600 text-white text-sm font-medium rounded-md hover:bg-lab-700 transition-colors"
          >
            Enrich {Math.min(litResult.candidate_targets.length, 10)} targets with OpenTargets + HPA
          </button>
        </div>
      )}

      {loading && (
        <LoadingSpinner message="Querying OpenTargets and Human Protein Atlas, then synthesizing with Claude..." />
      )}

      {error && <ErrorBanner message={error} />}

      {result && !loading && (
        <div className="space-y-6">
          <div className="bg-lab-50 border border-lab-100 rounded-lg p-4 space-y-2">
            <p className="text-sm font-medium text-lab-900">Enrichment Summary</p>
            <p className="text-sm text-lab-800">{result.enrichment_summary}</p>
            <div className="flex flex-wrap gap-3 mt-2 text-xs text-lab-600">
              {result.methods_used.map((m) => (
                <span key={m} className="bg-lab-100 px-2 py-0.5 rounded-full">{m}</span>
              ))}
            </div>
          </div>

          {(result.targets_not_found_in_ot.length > 0 || result.targets_not_found_in_hpa.length > 0) && (
            <div className="text-xs text-gray-400 bg-gray-50 rounded p-3 space-y-1">
              {result.targets_not_found_in_ot.length > 0 && (
                <p>Not found in OpenTargets: {result.targets_not_found_in_ot.join(', ')}</p>
              )}
              {result.targets_not_found_in_hpa.length > 0 && (
                <p>Not found in Human Protein Atlas: {result.targets_not_found_in_hpa.join(', ')}</p>
              )}
            </div>
          )}

          <div>
            <h3 className="text-base font-semibold text-gray-900 mb-3">
              Validated Targets
              <span className="ml-2 text-sm font-normal text-gray-400">
                ({result.targets_enriched} enriched)
              </span>
            </h3>
            <div className="space-y-2">
              {result.enriched_targets.map((target, i) => (
                <EnrichedTargetCard key={target.literature.name} target={target} rank={i} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
