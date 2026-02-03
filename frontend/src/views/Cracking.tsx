/**
 * Cracking View - REAL implementation
 */
import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { useAppStore } from '../store/useAppStore';
import type { CrackMode, GPUProvider } from '../types/models';

export const Cracking: React.FC = () => {
  const { crackingJobs, addCrackingJob, updateCrackingJob } = useAppStore();
  const [handshakeFile, setHandshakeFile] = useState('');
  const [bssid, setBSSID] = useState('');
  const [essid, setESSID] = useState('');
  const [attackMode, setAttackMode] = useState<CrackMode>('wordlist');
  const [gpuProvider, setGPUProvider] = useState<GPUProvider>('local');
  const [loading, setLoading] = useState(false);

  // Poll job status
  useEffect(() => {
    const interval = setInterval(async () => {
      for (const job of crackingJobs) {
        if (job.status === 'running' || job.status === 'provisioning' || job.status === 'starting') {
          try {
            const updated = await apiClient.getCrackingJob(job.id);
            updateCrackingJob(job.id, updated);
          } catch (error) {
            console.error('Error updating job:', error);
          }
        }
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [crackingJobs]);

  const createJob = async () => {
    if (!handshakeFile || !bssid || !essid) {
      alert('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      const job = await apiClient.createCrackingJob({
        handshake_file: handshakeFile,
        bssid,
        essid,
        attack_mode: attackMode,
        wordlist_path: undefined, // Will use default
        wordlist_name: undefined,
        mask: undefined,
        rules_file: undefined,
        gpu_provider: gpuProvider,
        max_cost_usd: 10.0,
        timeout_minutes: 120,
      });

      addCrackingJob(job);

      // Start immediately
      const started = await apiClient.startCrackingJob(job.id);
      updateCrackingJob(job.id, started);
    } catch (error: any) {
      alert(`Error creating job: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const stopJob = async (jobId: string) => {
    try {
      const stopped = await apiClient.stopCrackingJob(jobId);
      updateCrackingJob(jobId, stopped);
    } catch (error: any) {
      alert(`Error stopping job: ${error.message}`);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'running': return '#10b981';
      case 'success': return '#3b82f6';
      case 'exhausted': return '#f59e0b';
      case 'failed': return '#ef4444';
      case 'cancelled': return '#6b7280';
      default: return '#6b7280';
    }
  };

  return (
    <div data-testid="cracking-view">
      <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>Password Cracking</h1>

      {/* Create Job */}
      <div style={{ marginBottom: '20px', backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
        <h2 style={{ fontSize: '18px', marginBottom: '15px' }}>Create Cracking Job</h2>

        <div style={{ display: 'grid', gap: '15px', marginBottom: '15px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Handshake File Path
            </label>
            <input
              data-testid="handshake-file-input"
              type="text"
              value={handshakeFile}
              onChange={(e) => setHandshakeFile(e.target.value)}
              placeholder="/tmp/handshake.cap"
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #e5e7eb',
                borderRadius: '4px',
              }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                BSSID
              </label>
              <input
                data-testid="crack-bssid-input"
                type="text"
                value={bssid}
                onChange={(e) => setBSSID(e.target.value)}
                placeholder="00:11:22:33:44:55"
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '4px',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                ESSID
              </label>
              <input
                data-testid="crack-essid-input"
                type="text"
                value={essid}
                onChange={(e) => setESSID(e.target.value)}
                placeholder="Network Name"
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '4px',
                }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Attack Mode
              </label>
              <select
                data-testid="attack-mode-select"
                value={attackMode}
                onChange={(e) => setAttackMode(e.target.value as CrackMode)}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '4px',
                }}
              >
                <option value="wordlist">Wordlist</option>
                <option value="mask">Mask Attack</option>
                <option value="hybrid_wm">Hybrid (Wordlist + Mask)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                GPU Provider
              </label>
              <select
                data-testid="gpu-provider-select"
                value={gpuProvider}
                onChange={(e) => setGPUProvider(e.target.value as GPUProvider)}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '4px',
                }}
              >
                <option value="local">Local GPU</option>
                <option value="vastai">Vast.ai Cloud</option>
                <option value="lambda">Lambda Labs</option>
              </select>
            </div>
          </div>
        </div>

        <button
          data-testid="create-job-btn"
          onClick={createJob}
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
          }}
        >
          {loading ? 'Creating...' : 'Create Job'}
        </button>
      </div>

      {/* Active Jobs */}
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
        <h2 style={{ fontSize: '18px', marginBottom: '15px' }}>Cracking Jobs</h2>

        {crackingJobs.length === 0 ? (
          <p data-testid="no-jobs">No cracking jobs</p>
        ) : (
          <div data-testid="jobs-list">
            {crackingJobs.map((job) => (
              <div
                key={job.id}
                data-testid={`job-${job.id}`}
                style={{
                  marginBottom: '15px',
                  padding: '15px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '4px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <div>
                    <strong>{job.config.essid}</strong>
                    <span style={{ marginLeft: '10px', fontSize: '14px', color: '#6b7280' }}>
                      ({job.config.bssid})
                    </span>
                  </div>
                  <span
                    data-testid={`job-status-${job.id}`}
                    style={{
                      padding: '4px 12px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      color: 'white',
                      backgroundColor: getStatusColor(job.status),
                    }}
                  >
                    {job.status.toUpperCase()}
                  </span>
                </div>

                <div style={{ marginBottom: '10px', fontSize: '14px', color: '#6b7280' }}>
                  Mode: {job.config.attack_mode} | Provider: {job.config.gpu_provider}
                  {job.gpu_instance && ` | GPU: ${job.gpu_instance.gpu_model}`}
                </div>

                {job.status === 'running' && (
                  <div>
                    <div style={{ marginBottom: '10px' }}>
                      <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>
                        Progress: {job.progress.progress_percent.toFixed(1)}% | 
                        Speed: {job.progress.speed_mh_per_sec.toFixed(2)} MH/s
                      </div>
                      <div style={{ height: '8px', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                        <div
                          style={{
                            height: '100%',
                            width: `${job.progress.progress_percent}%`,
                            backgroundColor: '#10b981',
                            transition: 'width 0.3s',
                          }}
                        />
                      </div>
                    </div>

                    <div style={{ fontSize: '12px', color: '#6b7280' }}>
                      Cost: ${job.cost_usd}
                    </div>
                  </div>
                )}

                {job.password && (
                  <div
                    data-testid={`job-password-${job.id}`}
                    style={{
                      marginTop: '10px',
                      padding: '10px',
                      backgroundColor: '#d1fae5',
                      borderRadius: '4px',
                      fontWeight: 'bold',
                    }}
                  >
                    Password: {job.password}
                  </div>
                )}

                {(job.status === 'running' || job.status === 'provisioning') && (
                  <button
                    data-testid={`stop-job-${job.id}`}
                    onClick={() => stopJob(job.id)}
                    style={{
                      marginTop: '10px',
                      padding: '6px 12px',
                      backgroundColor: '#6b7280',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px',
                    }}
                  >
                    Stop Job
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
