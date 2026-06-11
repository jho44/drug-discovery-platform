import { PipelineProvider, usePipeline } from './context/PipelineContext'
import { PageShell } from './components/layout/PageShell'
import { LiteratureMining } from './components/pipeline/target_identification/LiteratureMining'
import { HitDiscovery } from './components/pipeline/hit_discovery/HitDiscovery'

function PipelineContent() {
  const { state } = usePipeline()

  switch (state.activeStage) {
    case 'target_identification':
      return <LiteratureMining />
    case 'hit_discovery':
      return <HitDiscovery />
    default:
      return (
        <div className="text-center py-16 text-gray-400 text-sm">
          This stage is not yet implemented. Complete earlier stages to proceed.
        </div>
      )
  }
}

export default function App() {
  return (
    <PipelineProvider>
      <PageShell>
        <PipelineContent />
      </PageShell>
    </PipelineProvider>
  )
}
