/**
 * Attacks View - REAL implementation
 */
import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { useAppStore } from '../store/useAppStore';
import type { AttackType } from '../types/models';

export const Attacks: React.FC = () => {
  const { selectedAdapter, networks, attacks, addAttack, updateAttack } = useAppStore();
  const [selectedBSSID, setSelectedBSSID] = useState('');
  const [attackType, setAttackType] = useState<AttackType>('handshake_capture');
  const [duration, setDuration] = useState(60);
  const [loading, setLoading] = useState(false);

  // Poll attack status
  useEffect(() => {
    const interval = setInterval(async () => {
      for (const attack of attacks) {
        if (attack.status === 'running' || attack.status === 'initializing') {
          try {
            const updated = await apiClient.getAttack(attack.id);
            updateAttack(attack.id, updated);
          } catch (error) {
            console.error('Error updating attack:', error);
          }
        }
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [attacks]);

  const createAttack = async () => {
    if (!selectedAdapter) {
      alert('Please select an adapter');
      return;
    }

    if (!selectedBSSID) {
      alert('Please enter a target BSSID');
      return;
    }

    setLoading(true);
    try {
      const network = networks.find((n) => n.bssid === selectedBSSID);
      
      const attack = await apiClient.createAttack({
        target_bssid: selectedBSSID,
        target_essid: network?.essid || 'Unknown',
        attack_type: attackType,
        interface: selectedAdapter.interface,
        channel: network?.channel,
        duration_seconds: duration,
        deauth_count: 0,
      });

      addAttack(attack);

      // Start immediately
      const started = await apiClient.startAttack(attack.id);
      updateAttack(attack.id, started);
    } catch (error: any) {
      alert(`Error creating attack: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const stopAttack = async (attackId: string) => {
    try {
      const stopped = await apiClient.stopAttack(attackId);
      updateAttack(attackId, stopped);
    } catch (error: any) {
      alert(`Error stopping attack: ${error.message}`);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'running': return '#10b981';
      case 'success': return '#3b82f6';
      case 'failed': return '#ef4444';
      case 'cancelled': return '#6b7280';
      default: return '#f59e0b';
    }
  };

  return (
    <div data-testid="attacks-view">
      <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>Attacks</h1>

      {/* Create Attack */}
      <div style={{ marginBottom: '20px', backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
        <h2 style={{ fontSize: '18px', marginBottom: '15px' }}>Launch Attack</h2>

        <div style={{ display: 'grid', gap: '15px', marginBottom: '15px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Target BSSID
            </label>
            <input
              data-testid="target-bssid-input"
              type="text"
              value={selectedBSSID}
              onChange={(e) => setSelectedBSSID(e.target.value)}
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
              Attack Type
            </label>
            <select
              data-testid="attack-type-select"
              value={attackType}
              onChange={(e) => setAttackType(e.target.value as AttackType)}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #e5e7eb',
                borderRadius: '4px',
              }}
            >
              <option value="handshake_capture">Handshake Capture (Deauth + Capture)</option>
              <option value="deauth">Deauthentication Only</option>
              <option value="pmkid">PMKID Attack (Clientless)</option>
              <option value="wps_pixie">WPS Pixie Dust (Fast)</option>
              <option value="wps_pin">WPS PIN Bruteforce (Slow)</option>
              <option value="wep_arp_replay">WEP ARP Replay Attack</option>
              <option value="wep_frag">WEP Fragmentation Attack</option>
              <option value="wep_chop">WEP ChopChop Attack</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Duration (seconds)
            </label>
            <input
              data-testid="duration-input"
              type="number"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value))}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #e5e7eb',
                borderRadius: '4px',
              }}
            />
          </div>
        </div>

        <button
          data-testid="launch-attack-btn"
          onClick={createAttack}
          disabled={loading || !selectedAdapter}
          style={{
            padding: '10px 20px',
            backgroundColor: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading || !selectedAdapter ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
          }}
        >
          {loading ? 'Launching...' : 'Launch Attack'}
        </button>

        {networks.length > 0 && (
          <div style={{ marginTop: '15px', fontSize: '14px' }}>
            <strong>Quick Select:</strong>
            <select
              onChange={(e) => setSelectedBSSID(e.target.value)}
              style={{
                marginLeft: '10px',
                padding: '6px',
                border: '1px solid #e5e7eb',
                borderRadius: '4px',
              }}
            >
              <option value="">Select from scanned networks...</option>
              {networks.map((net) => (
                <option key={net.bssid} value={net.bssid}>
                  {net.essid || '(Hidden)'} - {net.bssid}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Active Attacks */}
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
        <h2 style={{ fontSize: '18px', marginBottom: '15px' }}>Active Attacks</h2>

        {attacks.length === 0 ? (
          <p data-testid="no-attacks">No attacks launched</p>
        ) : (
          <div data-testid="attacks-list">
            {attacks.map((attack) => (
              <div
                key={attack.id}
                data-testid={`attack-${attack.id}`}
                style={{
                  marginBottom: '15px',
                  padding: '15px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '4px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <div>
                    <strong>{attack.config.attack_type}</strong>
                    <span style={{ marginLeft: '10px', fontSize: '14px', color: '#6b7280' }}>
                      {attack.config.target_essid} ({attack.config.target_bssid})
                    </span>
                  </div>
                  <span
                    data-testid={`attack-status-${attack.id}`}
                    style={{
                      padding: '4px 12px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      color: 'white',
                      backgroundColor: getStatusColor(attack.status),
                    }}
                  >
                    {attack.status.toUpperCase()}
                  </span>
                </div>

                <div style={{ marginBottom: '10px' }}>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>
                    Progress: {attack.progress_percent.toFixed(1)}%
                  </div>
                  <div style={{ height: '8px', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%',
                        width: `${attack.progress_percent}%`,
                        backgroundColor: '#3b82f6',
                        transition: 'width 0.3s',
                      }}
                    />
                  </div>
                </div>

                {attack.logs.length > 0 && (
                  <div style={{ fontSize: '12px', color: '#6b7280', fontFamily: 'monospace' }}>
                    Latest: {attack.logs[attack.logs.length - 1]}
                  </div>
                )}

                {(attack.status === 'running' || attack.status === 'initializing') && (
                  <button
                    data-testid={`stop-attack-${attack.id}`}
                    onClick={() => stopAttack(attack.id)}
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
                    Stop Attack
                  </button>
                )}

                {attack.result && (
                  <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#f0fdf4', borderRadius: '4px' }}>
                    <strong>Result:</strong> {attack.result.message}
                    {attack.result.handshake_file && (
                      <div style={{ fontSize: '12px', marginTop: '5px' }}>
                        Handshake: {attack.result.handshake_file}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
