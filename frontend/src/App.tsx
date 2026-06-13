import { PageShell } from './components/layout/PageShell'
import { TargetIdentificationStage } from './components/pipeline/target_identification/TargetIdentificationStage'
import { HitDiscovery } from './components/pipeline/hit_discovery/HitDiscovery'
import { usePipelineStore } from './store/pipelineStore'

function PipelineContent() {
  const activeStage = usePipelineStore((s) => s.activeStage)

  switch (activeStage) {
    case 'target_identification':
      return <TargetIdentificationStage />
    case 'hit_discovery':
      return <HitDiscovery />
    default:
      return (
        <div className="text-center py-16 text-gray-400 text-sm">
          This stage is not yet implemented.
        </div>
      )
  }
}

export default function App() {
  return (
    <PageShell>
      <PipelineContent />
    </PageShell>
  )
}
