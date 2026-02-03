/**
 * Scanner View - REAL implementation
 */
import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { useAppStore } from '../store/useAppStore';
import type { Network } from '../types/models';

export const Scanner: React.FC = () => {
  const { selectedAdapter, currentScan, setCurrentScan, networks, setNetworks } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [selectedNetwork, setSelectedNetwork] = useState<Network | null>(null);

  // Poll for networks while scanning
  useEffect(() => {
    if (!currentScan) return;

    const interval = setInterval(async () => {
      try {
        const fetchedNetworks = await apiClient.getNetworks(currentScan.id);
        setNetworks(fetchedNetworks);
        
        // Update scan session
        const session = await apiClient.getScanSession(currentScan.id);
        setCurrentScan(session);
      } catch (error) {
        console.error('Error fetching networks:', error);
      }
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [currentScan]);

  const startScan = async () => {
    if (!selectedAdapter) {
      alert('Please select an adapter first');
      return;
    }

    if (selectedAdapter.mode !== 'monitor') {
      alert('Adapter must be in monitor mode');
      return;
    }

    setLoading(true);
    try {
      const session = await apiClient.startScan({
        interface: selectedAdapter.interface,
        mode: 'passive',
        hop_interval_ms: 500,
        channels: undefined,
        capture_file: undefined,
      });
      setCurrentScan(session);
      setNetworks([]);
    } catch (error: any) {
      alert(`Error starting scan: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const stopScan = async () => {
    if (!currentScan) return;

    setLoading(true);
    try {
      await apiClient.stopScan(currentScan.id);
      setCurrentScan(null);
    } catch (error: any) {
      alert(`Error stopping scan: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getSignalColor = (signal: number): string => {
    if (signal >= -50) return '#10b981';
    if (signal >= -70) return '#f59e0b';
    return '#ef4444';
  };

  const getEncryptionColor = (encryption: string): string => {
    if (encryption === 'OPEN') return '#ef4444';
    if (encryption.includes('WEP')) return '#ef4444';
    if (encryption.includes('WPA3')) return '#10b981';
    return '#f59e0b';
  };

  return (
    <div data-testid="scanner-view">
      <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>Network Scanner</h1>

      {/* Controls */}
      <div style={{ marginBottom: '20px', backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
        <div style={{ marginBottom: '15px' }}>
          <strong>Selected Adapter:</strong> {selectedAdapter?.interface || 'None'}
          {selectedAdapter && ` (${selectedAdapter.mode})`}
        </div>

        {currentScan ? (
          <div>
            <button
              data-testid="stop-scan-btn"
              onClick={stopScan}
              disabled={loading}
              style={{
                padding: '10px 20px',
                backgroundColor: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer',
              }}
            >
              Stop Scan
            </button>
            <div style={{ marginTop: '10px', color: '#10b981' }} data-testid="scan-status">
              ● Scanning... ({networks.length} networks found)
            </div>
          </div>
        ) : (
          <button
            data-testid="start-scan-btn"
            onClick={startScan}
            disabled={loading || !selectedAdapter || selectedAdapter.mode !== 'monitor'}
            style={{
              padding: '10px 20px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading || !selectedAdapter ? 'not-allowed' : 'pointer',
            }}
          >
            Start Scan
          </button>
        )}
      </div>

      {/* Networks Table */}
      <div style={{ backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }} data-testid="networks-table">
          <thead>
            <tr style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
              <th style={{ padding: '12px', textAlign: 'left' }}>SSID</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>BSSID</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Channel</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Signal</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Encryption</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Clients</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Handshake</th>
            </tr>
          </thead>
          <tbody>
            {networks.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: '20px', textAlign: 'center', color: '#6b7280' }}>
                  {currentScan ? 'Scanning for networks...' : 'No networks found. Start a scan.'}
                </td>
              </tr>
            ) : (
              networks.map((network) => (
                <tr
                  key={network.bssid}
                  data-testid={`network-${network.bssid}`}
                  onClick={() => setSelectedNetwork(network)}
                  style={{
                    borderBottom: '1px solid #e5e7eb',
                    cursor: 'pointer',
                    backgroundColor: selectedNetwork?.bssid === network.bssid ? '#eff6ff' : 'white',
                  }}
                >
                  <td style={{ padding: '12px' }}>
                    <strong>{network.essid || '(Hidden)'}</strong>
                  </td>
                  <td style={{ padding: '12px', fontFamily: 'monospace', fontSize: '13px' }}>
                    {network.bssid}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center' }}>{network.channel}</td>
                  <td style={{ padding: '12px', textAlign: 'center' }}>
                    <span style={{ color: getSignalColor(network.signal), fontWeight: 'bold' }}>
                      {network.signal} dBm
                    </span>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center' }}>
                    <span
                      style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        backgroundColor: getEncryptionColor(network.encryption),
                        color: 'white',
                      }}
                    >
                      {network.encryption}
                    </span>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center' }}>{network.clients.length}</td>
                  <td style={{ padding: '12px', textAlign: 'center' }}>
                    {network.handshake_captured ? '✓' : ''}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Selected Network Details */}
      {selectedNetwork && (
        <div
          style={{ marginTop: '20px', backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}
          data-testid="network-details"
        >
          <h3 style={{ fontSize: '18px', marginBottom: '15px' }}>Selected Network Details</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <div><strong>SSID:</strong> {selectedNetwork.essid || '(Hidden)'}</div>
            <div><strong>BSSID:</strong> {selectedNetwork.bssid}</div>
            <div><strong>Channel:</strong> {selectedNetwork.channel}</div>
            <div><strong>Frequency:</strong> {selectedNetwork.frequency} MHz</div>
            <div><strong>Encryption:</strong> {selectedNetwork.encryption}</div>
            <div><strong>Cipher:</strong> {selectedNetwork.cipher}</div>
            <div><strong>Auth:</strong> {selectedNetwork.authentication}</div>
            <div><strong>WPS:</strong> {selectedNetwork.wps ? 'Enabled' : 'Disabled'}</div>
            <div><strong>Signal:</strong> {selectedNetwork.signal} dBm</div>
            <div><strong>Clients:</strong> {selectedNetwork.clients.length}</div>
          </div>
        </div>
      )}
    </div>
  );
};
