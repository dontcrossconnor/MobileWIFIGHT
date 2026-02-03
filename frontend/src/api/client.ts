/**
 * API Client - REAL implementation
 */
import axios, { AxiosInstance } from 'axios';
import type {
  Adapter,
  Network,
  Client,
  ScanSession,
  ScanConfig,
  Attack,
  AttackConfig,
  CrackingJob,
  CrackingJobConfig,
  CrackingProgress,
  Report,
  ReportFormat,
} from '../types/models';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Adapter endpoints
  async detectAdapters(): Promise<Adapter[]> {
    const response = await this.client.post('/adapter/detect');
    return response.data;
  }

  async getAdapter(iface: string): Promise<Adapter> {
    const response = await this.client.get(`/adapter/${iface}`);
    return response.data;
  }

  async setMonitorMode(iface: string, enable: boolean): Promise<Adapter> {
    const response = await this.client.post(`/adapter/${iface}/monitor-mode`, null, {
      params: { enable },
    });
    return response.data;
  }

  async setChannel(iface: string, channel: number): Promise<void> {
    await this.client.post(`/adapter/${iface}/channel`, null, {
      params: { channel },
    });
  }

  async setTxPower(iface: string, power_dbm: number): Promise<void> {
    await this.client.post(`/adapter/${iface}/tx-power`, null, {
      params: { power_dbm },
    });
  }

  // Scanner endpoints
  async startScan(config: ScanConfig): Promise<ScanSession> {
    const response = await this.client.post('/scan', config);
    return response.data;
  }

  async stopScan(sessionId: string): Promise<void> {
    await this.client.delete(`/scan/${sessionId}`);
  }

  async getScanSession(sessionId: string): Promise<ScanSession> {
    const response = await this.client.get(`/scan/${sessionId}`);
    return response.data;
  }

  async getNetworks(sessionId: string): Promise<Network[]> {
    const response = await this.client.get(`/scan/${sessionId}/networks`);
    return response.data;
  }

  async getClients(sessionId: string, bssid?: string): Promise<Client[]> {
    const response = await this.client.get(`/scan/${sessionId}/clients`, {
      params: bssid ? { bssid } : undefined,
    });
    return response.data;
  }

  // Attack endpoints
  async createAttack(config: AttackConfig): Promise<Attack> {
    const response = await this.client.post('/attacks', config);
    return response.data;
  }

  async startAttack(attackId: string): Promise<Attack> {
    const response = await this.client.post(`/attacks/${attackId}/start`);
    return response.data;
  }

  async stopAttack(attackId: string): Promise<Attack> {
    const response = await this.client.delete(`/attacks/${attackId}`);
    return response.data;
  }

  async getAttack(attackId: string): Promise<Attack> {
    const response = await this.client.get(`/attacks/${attackId}`);
    return response.data;
  }

  async getActiveAttacks(): Promise<Attack[]> {
    const response = await this.client.get('/attacks');
    return response.data;
  }

  // Cracking endpoints
  async createCrackingJob(config: CrackingJobConfig): Promise<CrackingJob> {
    const response = await this.client.post('/cracking/jobs', config);
    return response.data;
  }

  async startCrackingJob(jobId: string): Promise<CrackingJob> {
    const response = await this.client.post(`/cracking/jobs/${jobId}/start`);
    return response.data;
  }

  async stopCrackingJob(jobId: string): Promise<CrackingJob> {
    const response = await this.client.delete(`/cracking/jobs/${jobId}`);
    return response.data;
  }

  async getCrackingJob(jobId: string): Promise<CrackingJob> {
    const response = await this.client.get(`/cracking/jobs/${jobId}`);
    return response.data;
  }

  async getCrackingProgress(jobId: string): Promise<CrackingProgress> {
    const response = await this.client.get(`/cracking/jobs/${jobId}/progress`);
    return response.data;
  }

  // Capture endpoints
  async verifyHandshake(file: string, bssid: string): Promise<{ valid: boolean }> {
    const response = await this.client.post('/captures/verify', { file, bssid });
    return response.data;
  }

  // Wordlist endpoints
  async listWordlists(): Promise<any[]> {
    const response = await this.client.get('/wordlists');
    return response.data;
  }

  async downloadWordlist(key: string): Promise<void> {
    await this.client.post(`/wordlists/download/${key}`);
  }

  async downloadEssentials(): Promise<void> {
    await this.client.post('/wordlists/download-essentials');
  }

  // Report endpoints
  async generateReport(
    networks: Network[],
    attacks: Attack[],
    jobs: CrackingJob[],
    format: ReportFormat
  ): Promise<Report> {
    const response = await this.client.post('/reports', {
      networks,
      attacks,
      jobs,
      format,
    });
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health', {
      baseURL: API_BASE_URL,
    });
    return response.data;
  }
}

export const apiClient = new APIClient();
