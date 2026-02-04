/**
 * Global application state - Zustand
 */
import { create } from 'zustand';
import type {
  Adapter,
  Network,
  ScanSession,
  Attack,
  CrackingJob,
} from '../types/models';

interface AppState {
  // Adapters
  adapters: Adapter[];
  selectedAdapter: Adapter | null;
  setAdapters: (adapters: Adapter[]) => void;
  setSelectedAdapter: (adapter: Adapter | null) => void;

  // Scanning
  currentScan: ScanSession | null;
  networks: Network[];
  setCurrentScan: (scan: ScanSession | null) => void;
  setNetworks: (networks: Network[]) => void;

  // Attacks
  attacks: Attack[];
  addAttack: (attack: Attack) => void;
  updateAttack: (attackId: string, attack: Attack) => void;
  removeAttack: (attackId: string) => void;

  // Cracking
  crackingJobs: CrackingJob[];
  addCrackingJob: (job: CrackingJob) => void;
  updateCrackingJob: (jobId: string, job: CrackingJob) => void;
  removeCrackingJob: (jobId: string) => void;

  // UI State
  loading: boolean;
  error: string | null;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Adapters
  adapters: [],
  selectedAdapter: null,
  setAdapters: (adapters) => set({ adapters }),
  setSelectedAdapter: (adapter) => set({ selectedAdapter: adapter }),

  // Scanning
  currentScan: null,
  networks: [],
  setCurrentScan: (scan) => set({ currentScan: scan }),
  setNetworks: (networks) => set({ networks }),

  // Attacks
  attacks: [],
  addAttack: (attack) => set((state) => ({ attacks: [...state.attacks, attack] })),
  updateAttack: (attackId, attack) =>
    set((state) => ({
      attacks: state.attacks.map((a) => (a.id === attackId ? attack : a)),
    })),
  removeAttack: (attackId) =>
    set((state) => ({
      attacks: state.attacks.filter((a) => a.id !== attackId),
    })),

  // Cracking
  crackingJobs: [],
  addCrackingJob: (job) => set((state) => ({ crackingJobs: [...state.crackingJobs, job] })),
  updateCrackingJob: (jobId, job) =>
    set((state) => ({
      crackingJobs: state.crackingJobs.map((j) => (j.id === jobId ? job : j)),
    })),
  removeCrackingJob: (jobId) =>
    set((state) => ({
      crackingJobs: state.crackingJobs.filter((j) => j.id !== jobId),
    })),

  // UI State
  loading: false,
  error: null,
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
