interface EvidenceCardProps {
  pmid: string
  quote: string
  relation: string
}

export function EvidenceCard({ pmid, quote, relation }: EvidenceCardProps) {
  return (
    <div className="bg-gray-50 rounded border border-gray-200 p-3 text-sm">
      <p className="italic text-gray-700">"{quote}"</p>
      <div className="mt-2 flex items-center gap-3 text-xs text-gray-500">
        <span className="font-medium text-lab-600">{relation}</span>
        <span>·</span>
        <a
          href={`https://pubmed.ncbi.nlm.nih.gov/${pmid}/`}
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-lab-600 underline"
        >
          PMID {pmid}
        </a>
      </div>
    </div>
  )
}
