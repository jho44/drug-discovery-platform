import { useState } from 'react'
import type { HPAEvidence } from '../../../types/targetIdentification'

interface Props {
  evidence: HPAEvidence
}

const LEVEL_STYLE: Record<string, string> = {
  High: 'bg-green-100 text-green-700',
  Medium: 'bg-yellow-100 text-yellow-700',
  Low: 'bg-gray-100 text-gray-500',
  'Not detected': 'bg-gray-50 text-gray-400',
}

const SURVIVAL_STYLE: Record<string, string> = {
  favorable: 'bg-green-100 text-green-700',
  unfavorable: 'bg-red-100 text-red-600',
}

export function HPAEvidencePanel({ evidence }: Props) {
  const [showAllTissues, setShowAllTissues] = useState(false)

  const expressed = evidence.tissue_expression.filter(
    (t) => t.rna_level === 'High' || t.rna_level === 'Medium',
  )
  const rest = evidence.tissue_expression.filter(
    (t) => t.rna_level !== 'High' && t.rna_level !== 'Medium',
  )
  const visibleTissues = showAllTissues ? evidence.tissue_expression : expressed.slice(0, 12)

  return (
    <div className="space-y-4">
      {/* Protein class */}
      {evidence.protein_class.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Protein Class</p>
          <div className="flex flex-wrap gap-1.5">
            {evidence.protein_class.map((c) => (
              <span key={c} className="bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-full">
                {c}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Tissue expression */}
      {evidence.tissue_expression.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
            RNA Tissue Expression
          </p>
          <div className="flex flex-wrap gap-1.5">
            {visibleTissues.map((t) => (
              <span
                key={t.tissue}
                className={`text-xs px-2 py-0.5 rounded-full ${LEVEL_STYLE[t.rna_level] ?? LEVEL_STYLE['Not detected']}`}
              >
                {t.tissue}
              </span>
            ))}
          </div>
          {(rest.length > 0 || expressed.length > 12) && (
            <button
              onClick={() => setShowAllTissues((v) => !v)}
              className="text-xs text-lab-600 hover:underline mt-1.5"
            >
              {showAllTissues ? 'Show less' : `Show all ${evidence.tissue_expression.length} tissues`}
            </button>
          )}
          <div className="flex gap-3 mt-2">
            {Object.entries(LEVEL_STYLE).map(([level, style]) => (
              <span key={level} className={`text-xs px-1.5 py-0.5 rounded ${style}`}>
                {level}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Subcellular location */}
      {evidence.subcellular_locations.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
            Subcellular Location
          </p>
          <div className="flex flex-wrap gap-1.5">
            {evidence.subcellular_locations.map((loc) => (
              <span key={loc} className="bg-indigo-50 text-indigo-600 text-xs px-2 py-0.5 rounded-full">
                {loc}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Cancer pathology */}
      {evidence.cancer_pathology.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
            Cancer Pathology
          </p>
          <table className="w-full text-xs">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-100">
                <th className="pb-1 font-medium">Cancer type</th>
                <th className="pb-1 font-medium text-right">High expr %</th>
                <th className="pb-1 font-medium text-right">Prognosis</th>
              </tr>
            </thead>
            <tbody>
              {evidence.cancer_pathology.map((c) => (
                <tr key={c.cancer_type} className="border-b border-gray-50">
                  <td className="py-1 text-gray-700">{c.cancer_type}</td>
                  <td className="py-1 text-right text-gray-600">{c.high_expression_percent.toFixed(0)}%</td>
                  <td className="py-1 text-right">
                    {c.survival_correlation ? (
                      <span
                        className={`px-1.5 py-0.5 rounded text-xs ${
                          SURVIVAL_STYLE[c.survival_correlation] ?? ''
                        }`}
                      >
                        {c.survival_correlation}
                      </span>
                    ) : (
                      <span className="text-gray-300">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {evidence.hpa_url && (
            <a
              href={evidence.hpa_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-lab-600 hover:underline mt-2 inline-block"
            >
              View on Human Protein Atlas →
            </a>
          )}
        </div>
      )}

      {evidence.tissue_expression.length === 0 && evidence.cancer_pathology.length === 0 && (
        <p className="text-sm text-gray-400">No expression data available for this target.</p>
      )}
    </div>
  )
}
