import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useAppStore = create(
  persist(
    (set, get) => ({
      currentAnalysis: null,
      analysesHistory: [],
      isLoading: false,
      error: null,
      
      setCurrentAnalysis: (analysis) => {
        // Save to history
        const history = get().analysesHistory
        const newHistory = [analysis, ...history].slice(0, 10)
        
        set({ 
          currentAnalysis: analysis,
          analysesHistory: newHistory
        })
        
        // Also save to localStorage for persistence
        localStorage.setItem('analysisHistory', JSON.stringify(newHistory))
      },
      
      addToHistory: (analysis) => {
        const history = get().analysesHistory
        const newHistory = [analysis, ...history].slice(0, 10)
        set({ analysesHistory: newHistory })
        localStorage.setItem('analysisHistory', JSON.stringify(newHistory))
      },
      
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      
      clearAnalysis: () => set({ currentAnalysis: null, error: null }),
    }),
    {
      name: 'ai-copilot-storage',
      partialize: (state) => ({ 
        analysesHistory: state.analysesHistory 
      }),
    }
  )
)

export default useAppStore