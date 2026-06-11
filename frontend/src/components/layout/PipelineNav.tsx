import { PIPELINE_STAGES } from '../../types/pipeline'
import { usePipeline } from '../../context/PipelineContext'

export function PipelineNav() {
  const { state, dispatch } = usePipeline()

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3">
      <ol className="flex items-center gap-1 flex-wrap">
        {PIPELINE_STAGES.map((stage, index) => {
          const isActive = state.activeStage === stage.id
          const isCompleted =
            PIPELINE_STAGES.findIndex(s => s.id === state.activeStage) > index

          return (
            <li key={stage.id} className="flex items-center">
              {index > 0 && (
                <span className="mx-2 text-gray-300 text-sm">›</span>
              )}
              <button
                onClick={() => dispatch({ type: 'SET_ACTIVE_STAGE', stage: stage.id })}
                className={[
                  'px-3 py-1.5 rounded text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-lab-600 text-white'
                    : isCompleted
                    ? 'text-lab-600 hover:bg-lab-50'
                    : 'text-gray-400 cursor-default',
                ].join(' ')}
                disabled={!isActive && !isCompleted}
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
