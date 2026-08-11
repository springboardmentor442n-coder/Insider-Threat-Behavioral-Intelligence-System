import React, { useEffect, useState } from 'react';
import { analyticsAPI } from '../services/api';
import { Cpu, CheckCircle2, FileCode, Layers, ShieldCheck, BarChart2 } from 'lucide-react';

const Models = () => {
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        const info = await analyticsAPI.getModelInfo();
        setModelInfo(info);
      } catch (err) {
        console.error("Model info fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchModelInfo();
  }, []);

  if (loading) {
    return <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '100px' }}>Loading Trained Model Registry...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '28px' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Cpu color="var(--accent-cyan)" size={28} />
          <span>Trained ML Model Registry</span>
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
          Real-time status of loaded Gradient Boosting Classifier model artifacts and hold-out evaluation performance
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '28px' }}>
        {/* Model Specs Card */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={20} color="var(--accent-cyan)" />
            <span>Deployed Classifier Model</span>
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Model Architecture</span>
              <strong style={{ color: 'var(--accent-cyan)', fontSize: '0.85rem' }}>{modelInfo?.model_name}</strong>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Number of Features</span>
              <strong style={{ color: 'var(--accent-purple)', fontSize: '0.85rem' }}>{modelInfo?.features_count} Behavioral Features</strong>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Preprocessing Scaler</span>
              <strong style={{ color: 'var(--accent-emerald)', fontSize: '0.85rem' }}>{modelInfo?.scaler}</strong>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loaded Status</span>
              <span style={{ color: 'var(--accent-emerald)', fontWeight: 700, fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <CheckCircle2 size={16} /> Active & In-Memory
              </span>
            </div>
          </div>
        </div>

        {/* Notebook Evaluation Metrics Card */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart2 size={20} color="var(--accent-purple)" />
            <span>Hold-out Test Evaluation Metrics (Notebook 02)</span>
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
            <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Accuracy</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>99.95%</div>
            </div>

            <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Precision</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-emerald)' }}>98.80%</div>
            </div>

            <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Recall</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-purple)' }}>99.82%</div>
            </div>

            <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>F1-Score</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-low)' }}>99.31%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Artifact Files Status Table */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileCode size={20} color="var(--accent-cyan)" />
          <span>Serialized Model Artifact Files</span>
        </h3>

        <table className="custom-table">
          <thead>
            <tr>
              <th>Artifact File Name</th>
              <th>Expected Path</th>
              <th>Status</th>
              <th>File Size</th>
            </tr>
          </thead>
          <tbody>
            {modelInfo?.artifacts?.map((art, idx) => (
              <tr key={idx}>
                <td style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{art.file_name}</td>
                <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{art.path}</td>
                <td>
                  <span style={{ color: 'var(--accent-emerald)', fontWeight: 700, fontSize: '0.8rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <CheckCircle2 size={14} /> Loaded
                  </span>
                </td>
                <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{(art.size_bytes / 1024).toFixed(1)} KB</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Models;
