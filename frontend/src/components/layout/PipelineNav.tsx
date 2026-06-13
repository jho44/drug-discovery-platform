import { PIPELINE_STAGES } from '../../types/pipeline'
import { usePipelineStore } from '../../store/pipelineStore'

export function PipelineNav() {
  const activeStage = usePipelineStore((s) => s.activeStage)
  const setActiveStage = usePipelineStore((s) => s.setActiveStage)
  const isStageUnlocked = usePipelineStore((s) => s.isStageUnlocked)

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3">
      <ol className="flex items-center gap-1 flex-wrap">
        {PIPELINE_STAGES.map((stage, index) => {
          const isActive = activeStage === stage.id
          const unlocked = isStageUnlocked(stage.id)

          return (
            <li key={stage.id} className="flex items-center">
              {index > 0 && <span className="mx-2 text-gray-300 text-sm">›</span>}
              <button
                onClick={() => unlocked && setActiveStage(stage.id)}
                disabled={!unlocked}
                className={[
                  'px-3 py-1.5 rounded text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-lab-600 text-white'
                    : unlocked
                    ? 'text-lab-600 hover:bg-lab-50'
                    : 'text-gray-300 cursor-default',
                ].join(' ')}
              >
                <span className="mr-1.5 text-xs opacity-60">{index + 1}.</span>
                {stage.label}
              </button>
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
