import { create } from 'zustand';

const useAppStore = create((set) => ({
  currentAnalysis: null,
  isLoading: false,
  error: null,
  
  setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  
  clearAnalysis: () => set({ currentAnalysis: null, error: null }),
}));

export default useAppStore;