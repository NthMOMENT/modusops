'use client';
import { useEffect, useState } from 'react';
import Nav from '../../../components/Nav';
import styles from './page.module.css';

const API = process.env.NEXT_PUBLIC_API_URL ?? 'https://api.modusops.xyz';
const ARB_EXPLORER = 'https://arbiscan.io/tx/';

interface Verdict {
  case_id: string;
  verdict: 'PROCEED' | 'DISMISS' | 'ESCALATE' | 'REVIEW';
  confidence_score: number;
  jurisdiction: string;
  judicial_summary: string;
  prosecution_brief: string;
  defense_memorandum: string;
  evidence_hashes: string[];
  on_chain_tx?: string;
  timestamp: string;
}

const VERDICT_COLOR: Record<string, string> = {
  PROCEED: '#e05a5a',
  ESCALATE: '#e08a2a',
  REVIEW: '#1b63e8',
  DISMISS: '#4a9a6a',
};

export default function VerdictClient({ caseId }: { caseId: string }) {
  const [data, setData] = useState<Verdict | null>(null);
  const [error, setError] = useState('');
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    if (!caseId) return;
    fetch(`${API}/cases/${caseId}/verdict`)
      .then(r => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setData)
      .catch(e => setError(e.message));
  }, [caseId]);

  if (error) return (
    <>
      <Nav />
      <main className={styles.main}>
        <div className={styles.error}>Error loading verdict: {error}</div>
      </main>
    </>
  );

  if (!data) return (
    <>
      <Nav />
      <main className={styles.main}>
        <div className={styles.loading}>Loading verdict...</div>
      </main>
    </>
  );

  const verdictColor = VERDICT_COLOR[data.verdict] ?? 'var(--text)';

  return (
    <>
      <Nav />
      <main className={styles.main}>
        <div className={styles.header}>
          <div className={styles.label}>Case {caseId} · {data.jurisdiction} JURISDICTION</div>
          <div className={styles.verdictRow}>
            <h1 className={styles.verdict} style={{ color: verdictColor }}>
              {data.verdict}
            </h1>
            <div className={styles.confidence}>
              <div className={styles.confidenceNum}>{data.confidence_score}</div>
              <div className={styles.confidenceLabel}>confidence</div>
            </div>
          </div>
          <div className={styles.timestamp}>
            {new Date(data.timestamp).toUTCString()}
          </div>
        </div>

        <div className={styles.section}>
          <div className={styles.sectionLabel}>Judicial Summary</div>
          <p className={styles.prose}>{data.judicial_summary}</p>
        </div>

        <div className={styles.section}>
          <button
            className={styles.toggle}
            onClick={() => setExpanded(expanded === 'da' ? null : 'da')}
            type="button"
          >
            <span>Prosecution Brief</span>
            <span className={styles.toggleIcon}>{expanded === 'da' ? '−' : '+'}</span>
          </button>
          {expanded === 'da' && (
            <div className={styles.expandedContent}>{data.prosecution_brief}</div>
          )}
        </div>

        <div className={styles.section}>
          <button
            className={styles.toggle}
            onClick={() => setExpanded(expanded === 'def' ? null : 'def')}
            type="button"
          >
            <span>Defense Memorandum</span>
            <span className={styles.toggleIcon}>{expanded === 'def' ? '−' : '+'}</span>
          </button>
          {expanded === 'def' && (
            <div className={styles.expandedContent}>{data.defense_memorandum}</div>
          )}
        </div>

        <div className={styles.section}>
          <div className={styles.sectionLabel}>Chain of Custody</div>
          <div className={styles.chainPanel}>
            {data.on_chain_tx && (
              <div className={styles.chainRow}>
                <span className={styles.chainKey}>Arbitrum One</span>
                <a
                  href={`${ARB_EXPLORER}${data.on_chain_tx}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.chainVal}
                >
                  {data.on_chain_tx.slice(0, 18)}...
                </a>
              </div>
            )}
            {data.evidence_hashes.map((h, i) => (
              <div key={i} className={styles.chainRow}>
                <span className={styles.chainKey}>Evidence {String(i + 1).padStart(2, '0')}</span>
                <span className={styles.chainVal}>{h.slice(0, 18)}...</span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </>
  );
}
