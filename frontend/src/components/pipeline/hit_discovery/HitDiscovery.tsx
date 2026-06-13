import { usePipelineStore } from '../../../store/pipelineStore'

export function HitDiscovery() {
  const selectedTargets = usePipelineStore((s) => s.selectedTargets)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Hit Discovery</h2>
        <p className="text-sm text-gray-500 mt-1">
          Find compounds with known activity against your selected targets using ChEMBL,
          OpenTargets repurposing candidates, and PubChem BioAssay HTS results.
        </p>
      </div>

      {/* Show selected targets */}
      {selectedTargets.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
          <p className="text-sm font-medium text-gray-700">
            Selected targets from Stage 1
          </p>
          <div className="space-y-2">
            {selectedTargets.map((t) => (
              <div key={t.name} className="flex items-center gap-3">
                <span className="font-medium text-gray-800 text-sm">{t.name}</span>
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
                <span className="text-xs text-gray-400">{t.uniprot_name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg p-8 text-center text-gray-400 text-sm">
        Virtual screening and known-active lookups coming soon.
        <br />
        <span className="text-xs mt-1 block">
          Will query ChEMBL, OpenTargets repurposing candidates, and PubChem BioAssay
          using the UniProt IDs above.
        </span>
      </div>
    </div>
  )
}
