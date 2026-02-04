/**
 * Main App Component
 */
import React, { useEffect, useState } from 'react';
import { Dashboard } from './views/Dashboard';
import { Scanner } from './views/Scanner';
import { Attacks } from './views/Attacks';
import { Cracking } from './views/Cracking';
import { Wordlists } from './views/Wordlists';
import { apiClient } from './api/client';

type View = 'dashboard' | 'scanner' | 'attacks' | 'cracking' | 'wordlists';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<View>('dashboard');
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    // Check API health on mount
    const checkHealth = async () => {
      try {
        await apiClient.healthCheck();
        setApiStatus('online');
      } catch (error) {
        setApiStatus('offline');
      }
    };
    checkHealth();
  }, []);

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'scanner':
        return <Scanner />;
      case 'attacks':
        return <Attacks />;
      case 'cracking':
        return <Cracking />;
      case 'wordlists':
        return <Wordlists />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app" style={{ display: 'flex', height: '100vh', fontFamily: 'system-ui' }}>
      {/* Sidebar */}
      <nav style={{ width: '200px', backgroundColor: '#1a1a1a', color: 'white', padding: '20px' }}>
        <h2 style={{ marginBottom: '30px', fontSize: '18px' }}>WiFi Pentester</h2>
        
        {/* API Status */}
        <div style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#2a2a2a', borderRadius: '4px' }}>
          <div style={{ fontSize: '12px', marginBottom: '5px' }}>API Status</div>
          <div
            data-testid="api-status"
            style={{
              fontSize: '14px',
              fontWeight: 'bold',
              color: apiStatus === 'online' ? '#4ade80' : apiStatus === 'offline' ? '#ef4444' : '#fbbf24',
            }}
          >
            {apiStatus === 'online' ? '● Online' : apiStatus === 'offline' ? '● Offline' : '● Checking...'}
          </div>
        </div>

        {/* Navigation */}
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li style={{ marginBottom: '10px' }}>
            <button
              data-testid="nav-dashboard"
              onClick={() => setCurrentView('dashboard')}
              style={{
                width: '100%',
                padding: '10px',
                backgroundColor: currentView === 'dashboard' ? '#3b82f6' : 'transparent',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                textAlign: 'left',
              }}
            >
              Dashboard
            </button>
          </li>
          <li style={{ marginBottom: '10px' }}>
            <button
              data-testid="nav-scanner"
              onClick={() => setCurrentView('scanner')}
              style={{
                width: '100%',
                padding: '10px',
                backgroundColor: currentView === 'scanner' ? '#3b82f6' : 'transparent',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                textAlign: 'left',
              }}
            >
              Scanner
            </button>
          </li>
          <li style={{ marginBottom: '10px' }}>
            <button
              data-testid="nav-attacks"
              onClick={() => setCurrentView('attacks')}
              style={{
                width: '100%',
                padding: '10px',
                backgroundColor: currentView === 'attacks' ? '#3b82f6' : 'transparent',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                textAlign: 'left',
              }}
            >
              Attacks
            </button>
          </li>
          <li style={{ marginBottom: '10px' }}>
            <button
              data-testid="nav-cracking"
              onClick={() => setCurrentView('cracking')}
              style={{
                width: '100%',
                padding: '10px',
                backgroundColor: currentView === 'cracking' ? '#3b82f6' : 'transparent',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                textAlign: 'left',
              }}
            >
              Cracking
            </button>
          </li>
          <li style={{ marginBottom: '10px' }}>
            <button
              data-testid="nav-wordlists"
              onClick={() => setCurrentView('wordlists')}
              style={{
                width: '100%',
                padding: '10px',
                backgroundColor: currentView === 'wordlists' ? '#3b82f6' : 'transparent',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                textAlign: 'left',
              }}
            >
              Wordlists
            </button>
          </li>
        </ul>
      </nav>

      {/* Main Content */}
      <main style={{ flex: 1, padding: '20px', backgroundColor: '#f5f5f5', overflowY: 'auto' }}>
        {apiStatus === 'offline' && (
          <div
            style={{
              padding: '15px',
              backgroundColor: '#ef4444',
              color: 'white',
              borderRadius: '4px',
              marginBottom: '20px',
            }}
          >
            ⚠️ API Server Offline - Please start the backend server
          </div>
        )}
        {renderView()}
      </main>
    </div>
  );
};
