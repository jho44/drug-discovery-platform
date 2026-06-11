import { createContext, useContext, useReducer } from 'react'
import type { PipelineStage } from '../types/pipeline'
import type { LitMiningResult } from '../types/targetIdentification'

interface PipelineState {
  activeStage: PipelineStage
  targetIdentificationResult: LitMiningResult | null
}

type PipelineAction =
  | { type: 'SET_ACTIVE_STAGE'; stage: PipelineStage }
  | { type: 'SET_TARGET_ID_RESULT'; result: LitMiningResult }

function pipelineReducer(state: PipelineState, action: PipelineAction): PipelineState {
  switch (action.type) {
    case 'SET_ACTIVE_STAGE':
      return { ...state, activeStage: action.stage }
    case 'SET_TARGET_ID_RESULT':
      return { ...state, targetIdentificationResult: action.result }
  }
}

const initialState: PipelineState = {
  activeStage: 'target_identification',
  targetIdentificationResult: null,
}

const PipelineContext = createContext<{
  state: PipelineState
  dispatch: React.Dispatch<PipelineAction>
} | null>(null)

export function PipelineProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(pipelineReducer, initialState)
  return (
    <PipelineContext.Provider value={{ state, dispatch }}>
      {children}
    </PipelineContext.Provider>
  )
}

export function usePipeline() {
  const ctx = useContext(PipelineContext)
  if (!ctx) throw new Error('usePipeline must be used inside PipelineProvider')
  return ctx
}
