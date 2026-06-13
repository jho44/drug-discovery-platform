import type { OpenTargetsEvidence } from '../../../types/targetIdentification'

interface Props {
  evidence: OpenTargetsEvidence
}

function ScoreBar({ score, label }: { score: number | null; label: string }) {
  if (score === null) return null
  const pct = Math.round(score * 100)
  const color = score >= 0.7 ? 'bg-green-500' : score >= 0.3 ? 'bg-yellow-400' : 'bg-gray-300'
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-500 w-28 shrink-0">{label}</span>
      <div className="flex-1 bg-gray-100 rounded-full h-2">
        <div className={`${color} rounded-full h-2 transition-all`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-600 w-8 text-right">{pct}%</span>
    </div>
  )
}

export function OpenTargetsEvidencePanel({ evidence }: Props) {
  const { tractability, genetic_associations, mouse_phenotypes, safety_liabilities, ensembl_id } = evidence

  return (
    <div className="space-y-4">
      {/* Tractability */}
      {tractability && (
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Tractability</p>
          <div className="space-y-1.5">
            <ScoreBar score={tractability.small_molecule_score} label="Small molecule" />
            <ScoreBar score={tractability.antibody_score} label="Antibody" />
          </div>
          <p className="text-xs text-gray-500 mt-1.5 italic">{tractability.assessment}</p>
        </div>
      )}

      {/* Genetic associations */}
      {genetic_associations.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
            Genetic Associations
          </p>
          <div className="space-y-1.5">
            {genetic_associations.map((assoc) => (
              <div key={assoc.disease_name} className="flex items-center gap-3">
                <span className="text-xs text-gray-700 flex-1 truncate">{assoc.disease_name}</span>
                <div className="w-24 bg-gray-100 rounded-full h-1.5">
                  <div
                    className="bg-lab-500 rounded-full h-1.5"
                    style={{ width: `${Math.round(assoc.association_score * 100)}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500 w-10 text-right">
                  {assoc.association_score.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
          {ensembl_id && (
            <a
              href={`https://platform.opentargets.org/target/${ensembl_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-lab-600 hover:underline mt-2 inline-block"
            >
              View on OpenTargets →
            </a>
          )}
        </div>
      )}

      {/* Mouse phenotypes */}
      {mouse_phenotypes.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
            Mouse Knockout Phenotypes
          </p>
          <div className="flex flex-wrap gap-1.5">
            {mouse_phenotypes.map((p) => (
              <span key={p} className="bg-purple-50 text-purple-700 text-xs px-2 py-0.5 rounded-full">
                {p}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Safety */}
      {safety_liabilities.length > 0 && (
        <div>
          <p className="text-xs font-medium text-red-500 uppercase tracking-wide mb-2">
            Safety Liabilities
          </p>
          <div className="flex flex-wrap gap-1.5">
            {safety_liabilities.map((s) => (
              <span key={s} className="bg-red-50 text-red-600 text-xs px-2 py-0.5 rounded-full">
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {!tractability && genetic_associations.length === 0 && mouse_phenotypes.length === 0 && (
        <p className="text-sm text-gray-400">No detailed data available for this target.</p>
      )}
    </div>
  )
}
