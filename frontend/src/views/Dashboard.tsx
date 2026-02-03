/**
 * Dashboard View - REAL implementation
 */
import React, { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import { useAppStore } from '../store/useAppStore';

export const Dashboard: React.FC = () => {
  const { adapters, setAdapters, selectedAdapter, setSelectedAdapter } = useAppStore();
  const [loading, setLoading] = useState(false);

  const detectAdapters = async () => {
    setLoading(true);
    try {
      const detected = await apiClient.detectAdapters();
      setAdapters(detected);
      if (detected.length > 0 && !selectedAdapter) {
        setSelectedAdapter(detected[0]);
      }
    } catch (error: any) {
      alert(`Error detecting adapters: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    detectAdapters();
  }, []);

  const toggleMonitorMode = async () => {
    if (!selectedAdapter) return;
    
    setLoading(true);
    try {
      const isMonitor = selectedAdapter.mode === 'monitor';
      const updated = await apiClient.setMonitorMode(selectedAdapter.interface, !isMonitor);
      setSelectedAdapter(updated);
      
      // Refresh adapters
      const detected = await apiClient.detectAdapters();
      setAdapters(detected);
    } catch (error: any) {
      alert(`Error toggling monitor mode: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div data-testid="dashboard-view">
      <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>Dashboard</h1>

      {/* Adapter Section */}
      <div style={{ marginBottom: '30px', backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
        <h2 style={{ fontSize: '18px', marginBottom: '15px' }}>WiFi Adapters</h2>
        
        <button
          data-testid="detect-adapters-btn"
          onClick={detectAdapters}
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            marginBottom: '15px',
          }}
        >
          {loading ? 'Detecting...' : 'Detect Adapters'}
        </button>

        {adapters.length === 0 ? (
          <p data-testid="no-adapters">No adapters detected. Click "Detect Adapters" to scan.</p>
        ) : (
          <div data-testid="adapter-list">
            {adapters.map((adapter) => (
              <div
                key={adapter.interface}
                data-testid={`adapter-${adapter.interface}`}
                onClick={() => setSelectedAdapter(adapter)}
                style={{
                  padding: '15px',
                  marginBottom: '10px',
                  backgroundColor: selectedAdapter?.interface === adapter.interface ? '#eff6ff' : '#f9fafb',
                  border: selectedAdapter?.interface === adapter.interface ? '2px solid #3b82f6' : '1px solid #e5e7eb',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{adapter.interface}</div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>
                  Chipset: {adapter.chipset} | Driver: {adapter.driver}
                </div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>
                  Mode: <span data-testid={`adapter-mode-${adapter.interface}`}>{adapter.mode}</span> | 
                  Status: {adapter.status} | 
                  TX Power: {adapter.tx_power_dbm} dBm
                </div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>
                  Monitor Capable: {adapter.monitor_mode_capable ? '✓' : '✗'} | 
                  Injection Capable: {adapter.injection_capable ? '✓' : '✗'}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Selected Adapter Controls */}
      {selectedAdapter && (
        <div style={{ marginBottom: '30px', backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
          <h2 style={{ fontSize: '18px', marginBottom: '15px' }}>
            Adapter Controls: {selectedAdapter.interface}
          </h2>
          
          <button
            data-testid="toggle-monitor-mode-btn"
            onClick={toggleMonitorMode}
            disabled={loading}
            style={{
              padding: '10px 20px',
              backgroundColor: selectedAdapter.mode === 'monitor' ? '#ef4444' : '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {selectedAdapter.mode === 'monitor' ? 'Disable Monitor Mode' : 'Enable Monitor Mode'}
          </button>
        </div>
      )}

      {/* Quick Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
          <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>Adapters</div>
          <div style={{ fontSize: '32px', fontWeight: 'bold' }} data-testid="adapter-count">
            {adapters.length}
          </div>
        </div>
        
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
          <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>Active Scans</div>
          <div style={{ fontSize: '32px', fontWeight: 'bold' }}>0</div>
        </div>
        
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
          <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>Active Attacks</div>
          <div style={{ fontSize: '32px', fontWeight: 'bold' }}>0</div>
        </div>
        
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
          <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>Cracking Jobs</div>
          <div style={{ fontSize: '32px', fontWeight: 'bold' }}>0</div>
        </div>
      </div>
    </div>
  );
};
