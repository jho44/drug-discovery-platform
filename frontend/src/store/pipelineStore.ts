import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { PipelineStage, SessionSnapshot } from '../types/pipeline'
import type {
  LitMiningResult,
  EnrichmentResult,
  CandidateTarget,
} from '../types/targetIdentification'
import type { HitDiscoveryResult } from '../types/hitDiscovery'

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

  // Stage: Hit Discovery
  hitDiscoveryResult: HitDiscoveryResult | null
  setHitDiscoveryResult: (result: HitDiscoveryResult) => void

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
      hitDiscoveryResult: null,

      setActiveStage: (stage) => set({ activeStage: stage }),
      setLitMiningResult: (result) => set({ litMiningResult: result, enrichmentResult: null }),
      setEnrichmentResult: (result) => set({ enrichmentResult: result }),
      setSelectedTargets: (targets) => set({ selectedTargets: targets }),
      setHitDiscoveryResult: (result) => set({ hitDiscoveryResult: result }),

      isStageUnlocked: (stage) => {
        const { selectedTargets, hitDiscoveryResult } = get()
        switch (stage) {
          case 'target_identification':
            return true
          case 'hit_discovery':
            return selectedTargets.length > 0
          case 'lead_optimization':
            return hitDiscoveryResult !== null
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
          hitDiscoveryResult: snapshot.hitDiscoveryResult ?? null,
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
        hitDiscoveryResult: state.hitDiscoveryResult,
      }),
    },
  ),
)
