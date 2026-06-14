import { useRef, useState } from 'react'
import { usePipelineStore } from '../../store/pipelineStore'
import { exportSession, parseSessionFile } from '../../utils/sessionIO'
import type { SessionSnapshot } from '../../types/pipeline'

export function SessionControls() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [feedback, setFeedback] = useState<string | null>(null)

  const activeStage = usePipelineStore((s) => s.activeStage)
  const litMiningResult = usePipelineStore((s) => s.litMiningResult)
  const enrichmentResult = usePipelineStore((s) => s.enrichmentResult)
  const selectedTargets = usePipelineStore((s) => s.selectedTargets)
  const hitDiscoveryResult = usePipelineStore((s) => s.hitDiscoveryResult)
  const loadSession = usePipelineStore((s) => s.loadSession)

  function showFeedback(msg: string) {
    setFeedback(msg)
    setTimeout(() => setFeedback(null), 2000)
  }

  function handleExport() {
    const snapshot: SessionSnapshot = {
      version: 1,
      exportedAt: new Date().toISOString(),
      activeStage,
      litMiningResult,
      enrichmentResult,
      selectedTargets,
      hitDiscoveryResult,
    }
    exportSession(snapshot)
    showFeedback('Exported!')
  }

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const snapshot = await parseSessionFile(file)
      loadSession(snapshot)
      showFeedback('Session loaded!')
    } catch (err) {
      showFeedback(err instanceof Error ? err.message : 'Import failed')
    }
    e.target.value = ''
  }

  const btnClass =
    'px-3 py-1.5 text-sm font-medium rounded border border-lab-400 text-lab-100 hover:bg-lab-700 transition-colors'

  return (
    <div className="flex flex-col items-end gap-1">
      <div className="flex gap-2">
        <button onClick={handleExport} className={btnClass} title="Save session to file">
          ↓ Export
        </button>
        <button
          onClick={() => fileInputRef.current?.click()}
          className={btnClass}
          title="Load session from file"
        >
          ↑ Import
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>
      {feedback && (
        <span className="text-xs text-lab-200">{feedback}</span>
      )}
    </div>
  )
}
