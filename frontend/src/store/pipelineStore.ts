import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { PipelineStage, SessionSnapshot } from '../types/pipeline'
import type {
  LitMiningResult,
  EnrichmentResult,
  CandidateTarget,
} from '../types/targetIdentification'

interface PipelineStore {
  // Navigation
  activeStage: PipelineStage
  setActiveStage: (stage: PipelineStage) => void

  // Stage: Target Identification
  litMiningResult: LitMiningResult | null
  enrichmentResult: EnrichmentResult | null
  selectedTargets: CandidateTarget[]

  setLitMiningResult: (result: LitMiningResult) => void
  setEnrichmentResult: (result: EnrichmentResult) => void
  setSelectedTargets: (targets: CandidateTarget[]) => void

  // Unlock logic — a stage is accessible once its prerequisite is met
  isStageUnlocked: (stage: PipelineStage) => boolean

  clearStage1: () => void
  loadSession: (snapshot: SessionSnapshot) => void
}

export const usePipelineStore = create<PipelineStore>()(
  persist(
    (set, get) => ({
      activeStage: 'target_identification',
      litMiningResult: null,
      enrichmentResult: null,
      selectedTargets: [],

      setActiveStage: (stage) => set({ activeStage: stage }),
      setLitMiningResult: (result) => set({ litMiningResult: result, enrichmentResult: null }),
      setEnrichmentResult: (result) => set({ enrichmentResult: result }),
      setSelectedTargets: (targets) => set({ selectedTargets: targets }),

      isStageUnlocked: (stage) => {
        const { selectedTargets } = get()
        switch (stage) {
          case 'target_identification':
            return true
          case 'hit_discovery':
            return selectedTargets.length > 0
          // future stages unlock sequentially — extend here
          default:
            return false
        }
      },

      clearStage1: () =>
        set({ litMiningResult: null, enrichmentResult: null, selectedTargets: [] }),

      loadSession: (snapshot) =>
        set({
          activeStage: snapshot.activeStage,
          litMiningResult: snapshot.litMiningResult,
          enrichmentResult: snapshot.enrichmentResult,
          selectedTargets: snapshot.selectedTargets,
        }),
    }),
    {
      name: 'drug-discovery-pipeline',
      storage: createJSONStorage(() => sessionStorage),
      // Only persist data, not functions
      partialize: (state) => ({
        activeStage: state.activeStage,
        litMiningResult: state.litMiningResult,
        enrichmentResult: state.enrichmentResult,
        selectedTargets: state.selectedTargets,
      }),
    },
  ),
)
