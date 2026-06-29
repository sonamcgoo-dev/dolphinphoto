import { create } from 'zustand'

interface DeviceInfo {
  device: string
  device_name: string
  ram_gb: number
  vram_gb?: number
  performance_tier: string
  [key: string]: unknown
}

interface AppState {
  connected: boolean
  device: DeviceInfo | null
  setupComplete: boolean
  currentImage: string | null
  currentVideo: string | null
  selectedFilter: string | null
  processing: boolean
  progress: number
  
  setConnected: (connected: boolean) => void
  setDevice: (device: DeviceInfo | null) => void
  setSetupComplete: (complete: boolean) => void
  setCurrentImage: (image: string | null) => void
  setCurrentVideo: (video: string | null) => void
  setSelectedFilter: (filter: string | null) => void
  setProcessing: (processing: boolean) => void
  setProgress: (progress: number) => void
}

export const useAppStore = create<AppState>((set) => ({
  connected: false,
  device: null,
  setupComplete: false,
  currentImage: null,
  currentVideo: null,
  selectedFilter: null,
  processing: false,
  progress: 0,
  
  setConnected: (connected) => set({ connected }),
  setDevice: (device) => set({ device }),
  setSetupComplete: (setupComplete) => set({ setupComplete }),
  setCurrentImage: (currentImage) => set({ currentImage }),
  setCurrentVideo: (currentVideo) => set({ currentVideo }),
  setSelectedFilter: (selectedFilter) => set({ selectedFilter }),
  setProcessing: (processing) => set({ processing }),
  setProgress: (progress) => set({ progress }),
}))
