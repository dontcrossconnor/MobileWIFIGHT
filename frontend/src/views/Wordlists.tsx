/**
 * Wordlists View - REAL implementation
 */
import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

interface Wordlist {
  key: string;
  name: string;
  filename: string;
  description: string;
  size: string;
  passwords: string;
  downloaded: boolean;
  path: string | null;
}

export const Wordlists: React.FC = () => {
  const [wordlists, setWordlists] = useState<Wordlist[]>([]);
  const [loading, setLoading] = useState(false);
  const [downloadingKey, setDownloadingKey] = useState<string | null>(null);

  useEffect(() => {
    loadWordlists();
  }, []);

  const loadWordlists = async () => {
    setLoading(true);
    try {
      const lists = await apiClient.listWordlists();
      setWordlists(lists);
    } catch (error: any) {
      alert(`Error loading wordlists: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const downloadWordlist = async (key: string) => {
    setDownloadingKey(key);
    try {
      await apiClient.downloadWordlist(key);
      await loadWordlists(); // Refresh list
      alert(`Wordlist "${key}" downloaded successfully`);
    } catch (error: any) {
      alert(`Error downloading wordlist: ${error.message}`);
    } finally {
      setDownloadingKey(null);
    }
  };

  const downloadEssentials = async () => {
    setLoading(true);
    try {
      await apiClient.downloadEssentials();
      await loadWordlists();
      alert('Essential wordlists downloaded successfully');
    } catch (error: any) {
      alert(`Error downloading essentials: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div data-testid="wordlists-view">
      <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>Wordlists</h1>

      {/* Controls */}
      <div style={{ marginBottom: '20px', backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
        <button
          data-testid="refresh-wordlists-btn"
          onClick={loadWordlists}
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            marginRight: '10px',
          }}
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>

        <button
          data-testid="download-essentials-btn"
          onClick={downloadEssentials}
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          Download Essentials
        </button>
      </div>

      {/* Wordlists List */}
      <div style={{ backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }} data-testid="wordlists-table">
          <thead>
            <tr style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
              <th style={{ padding: '12px', textAlign: 'left' }}>Name</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Description</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Size</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Passwords</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Status</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {wordlists.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ padding: '20px', textAlign: 'center', color: '#6b7280' }}>
                  {loading ? 'Loading wordlists...' : 'No wordlists found'}
                </td>
              </tr>
            ) : (
              wordlists.map((wl) => (
                <tr
                  key={wl.key}
                  data-testid={`wordlist-${wl.key}`}
                  style={{ borderBottom: '1px solid #e5e7eb' }}
                >
                  <td style={{ padding: '12px' }}>
                    <strong>{wl.name}</strong>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>{wl.filename}</div>
                  </td>
                  <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280' }}>
                    {wl.description}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center' }}>{wl.size}</td>
                  <td style={{ padding: '12px', textAlign: 'center' }}>{wl.passwords}</td>
                  <td style={{ padding: '12px', textAlign: 'center' }}>
                    {wl.downloaded ? (
                      <span
                        data-testid={`wordlist-status-${wl.key}`}
                        style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: 'bold',
                          backgroundColor: '#10b981',
                          color: 'white',
                        }}
                      >
                        Downloaded
                      </span>
                    ) : (
                      <span
                        data-testid={`wordlist-status-${wl.key}`}
                        style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: 'bold',
                          backgroundColor: '#e5e7eb',
                          color: '#6b7280',
                        }}
                      >
                        Not Downloaded
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center' }}>
                    {!wl.downloaded && (
                      <button
                        data-testid={`download-${wl.key}-btn`}
                        onClick={() => downloadWordlist(wl.key)}
                        disabled={downloadingKey === wl.key}
                        style={{
                          padding: '6px 12px',
                          backgroundColor: '#3b82f6',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: downloadingKey === wl.key ? 'not-allowed' : 'pointer',
                          fontSize: '12px',
                        }}
                      >
                        {downloadingKey === wl.key ? 'Downloading...' : 'Download'}
                      </button>
                    )}
                    {wl.downloaded && (
                      <span style={{ fontSize: '12px', color: '#6b7280' }}>
                        {wl.path}
                      </span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
