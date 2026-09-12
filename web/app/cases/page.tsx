'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import Nav from '../components/Nav';
import styles from './page.module.css';

const API = process.env.NEXT_PUBLIC_API_URL ?? 'https://api.modusops.xyz';
const ARB_EXPLORER = 'https://arbiscan.io/tx/';

interface CaseRecord {
  case_id: string;
  verdict: 'PROCEED' | 'DISMISS' | 'ESCALATE' | 'REVIEW';
  confidence_score: number;
  jurisdiction: 'LOCAL' | 'STATE' | 'FEDERAL';
  timestamp: number;
  on_chain_tx?: string | null;
}

export default function CasesPage() {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/cases`)
      .then(r => r.json())
      .then(d => { setCases(Array.isArray(d) ? d : []); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  return (
    <>
      <Nav />
      <main className={styles.main}>
        <div className={styles.header}>
          <div className={styles.label}>Modus Ops API &middot; SQLite case store</div>
          <h1 className={styles.title}>Case History</h1>
        </div>

        {loading && <div className={styles.state}>Loading cases...</div>}
        {error && <div className={styles.error}>API error: {error}</div>}

        {!loading && cases.length === 0 && !error && (
          <div className={styles.state}>
            No verdicts yet. Submit a case to begin.
          </div>
        )}

        {cases.length > 0 && (
          <table className={styles.table}>
            <thead>
              <tr>
                <th className={styles.th}>Case ID</th>
                <th className={styles.th}>Verdict</th>
                <th className={styles.th}>Confidence</th>
                <th className={styles.th}>Jurisdiction</th>
                <th className={styles.th}>Filed</th>
                <th className={styles.th}>On-chain</th>
              </tr>
            </thead>
            <tbody>
              {cases.map(c => (
                <tr key={c.case_id} className={styles.tr}>
                  <td className={styles.td}>
                    <Link href={`/case/${c.case_id}/verdict`} className={styles.caseLink}>
                      {c.case_id.slice(0, 8)}...
                    </Link>
                  </td>
                  <td className={styles.td}>
                    <span className={`${styles.verdict} ${styles['v' + c.verdict]}`}>
                      {c.verdict}
                    </span>
                  </td>
                  <td className={styles.td}><span className={styles.mono}>{c.confidence_score}</span></td>
                  <td className={styles.td}><span className={styles.mono}>{c.jurisdiction}</span></td>
                  <td className={styles.td}>
                    <span className={styles.mono}>
                      {new Date(c.timestamp * 1000).toLocaleDateString()}
                    </span>
                  </td>
                  <td className={styles.td}>
                    {c.on_chain_tx ? (
                      <a
                        href={`${ARB_EXPLORER}${c.on_chain_tx}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.caseLink}
                      >
                        {c.on_chain_tx.slice(0, 10)}...
                      </a>
                    ) : (
                      <span className={styles.mono}>pending</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <div className={styles.footnote}>
          Verdicts are also indexed on-chain via The Graph (Arbitrum One, modus-ops subgraph).
        </div>
      </main>
    </>
  );
}
