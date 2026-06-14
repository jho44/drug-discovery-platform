import { PipelineNav } from './PipelineNav'
import { SessionControls } from './SessionControls'

interface PageShellProps {
  children: React.ReactNode
}

export function PageShell({ children }: PageShellProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-lab-900 text-white px-6 py-4 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">
            Drug Discovery Learning Platform
          </h1>
          <p className="text-lab-100 text-sm mt-0.5">
            Interactive computational pipeline
          </p>
        </div>
        <SessionControls />
      </header>
      <PipelineNav />
      <main className="flex-1 px-6 py-6 max-w-6xl mx-auto w-full">
        {children}
      </main>
    </div>
  )
}
