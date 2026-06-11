import { useState } from 'react'
import { TargetEvidencePanel } from './TargetEvidencePanel'
import type { CandidateTarget } from '../../../types/targetIdentification'

interface Props {
  targets: CandidateTarget[]
}

export function CandidateTargetList({ targets }: Props) {
  const [expanded, setExpanded] = useState<Set<number>>(new Set([0]))

  if (targets.length === 0) {
    return <p className="text-gray-500 text-sm">No candidate targets identified.</p>
  }

  function toggle(i: number) {
    setExpanded(prev => {
      const next = new Set(prev)
      next.has(i) ? next.delete(i) : next.add(i)
      return next
    })
  }

  return (
    <div className="space-y-2">
      {targets.map((target, i) => (
        <div key={target.name}>
          <button
            onClick={() => toggle(i)}
            className="w-full text-left flex items-center justify-between px-4 py-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className="font-medium text-gray-800">
              <span className="text-lab-600 mr-2">#{i + 1}</span>
              {target.name}
            </span>
            <span className="text-gray-400 text-xs">{expanded.has(i) ? '▲ collapse' : '▼ expand'}</span>
          </button>
          {expanded.has(i) && (
            <div className="mt-1 ml-4">
              <TargetEvidencePanel target={target} />
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
