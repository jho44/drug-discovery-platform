import type { SessionSnapshot } from '../types/pipeline'

export function exportSession(snapshot: SessionSnapshot): void {
  const json = JSON.stringify(snapshot, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `drug-discovery-${snapshot.exportedAt.slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(url)
}

export function parseSessionFile(file: File): Promise<SessionSnapshot> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const raw = JSON.parse(e.target!.result as string)
        if (raw.version !== 1 || !raw.activeStage) {
          reject(new Error('Invalid or incompatible session file'))
          return
        }
        resolve(raw as SessionSnapshot)
      } catch {
        reject(new Error('Could not parse file'))
      }
    }
    reader.onerror = () => reject(new Error('Could not read file'))
    reader.readAsText(file)
  })
}
