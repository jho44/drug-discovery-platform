import { useLiteratureMining } from '../../../hooks/useLiteratureMining'
import { LitMiningSearchForm } from './LitMiningSearchForm'
import { CandidateTargetList } from './CandidateTargetList'
import { LoadingSpinner } from '../../shared/LoadingSpinner'
import { ErrorBanner } from '../../shared/ErrorBanner'
import { usePipelineStore } from '../../../store/pipelineStore'

export function LiteratureMining() {
  const { loading, error, search } = useLiteratureMining()
  const litMiningResult = usePipelineStore((s) => s.litMiningResult)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Literature Mining</h2>
        <p className="text-sm text-gray-500 mt-1">
          Search PubMed abstracts and extract candidate drug targets using AI-powered named
          entity recognition and relation extraction.
        </p>
      </div>

      <LitMiningSearchForm onSearch={search} loading={loading} />

      {loading && (
        <LoadingSpinner message="Fetching abstracts from PubMed and analyzing with Claude..." />
      )}

      {error && <ErrorBanner message={error} />}

      {litMiningResult && !loading && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="bg-lab-50 border border-lab-100 rounded-lg p-4">
            <p className="text-sm font-medium text-lab-900 mb-1">Summary</p>
            <p className="text-sm text-lab-800">{litMiningResult.summary}</p>
            <p className="text-xs text-lab-600 mt-2">
              Analyzed {litMiningResult.abstracts_fetched} abstracts for "{litMiningResult.query}"
            </p>
          </div>

          {/* Entities */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                Genes / Proteins
              </p>
              <div className="flex flex-wrap gap-1.5">
                {litMiningResult.entities.genes_proteins.map((name) => (
                  <span key={name} className="bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-full">
                    {name}
                  </span>
                ))}
              </div>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                Diseases
              </p>
              <div className="flex flex-wrap gap-1.5">
                {litMiningResult.entities.diseases.map((name) => (
                  <span key={name} className="bg-orange-50 text-orange-700 text-xs px-2 py-0.5 rounded-full">
                    {name}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Candidate Targets */}
          <div>
            <h3 className="text-base font-semibold text-gray-900 mb-3">
              Candidate Targets
              <span className="ml-2 text-sm font-normal text-gray-400">
                ({litMiningResult.candidate_targets.length} identified)
              </span>
            </h3>
            <CandidateTargetList targets={litMiningResult.candidate_targets} />
          </div>

          {/* Abstracts used */}
          <details>
            <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
              View {litMiningResult.abstracts_meta.length} abstracts used
            </summary>
            <ul className="mt-2 space-y-1 ml-4">
              {litMiningResult.abstracts_meta.map((a) => (
                <li key={a.pmid} className="text-xs text-gray-500">
                  <a
                    href={`https://pubmed.ncbi.nlm.nih.gov/${a.pmid}/`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-lab-600 underline"
                  >
                    [{a.year}] {a.title}
                  </a>
                  {a.journal && <span className="ml-1 text-gray-400">— {a.journal}</span>}
                </li>
              ))}
            </ul>
          </details>
        </div>
      )}
    </div>
  )
}
