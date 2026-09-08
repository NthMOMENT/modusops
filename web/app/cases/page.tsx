'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import Nav from '../components/Nav';
import styles from './page.module.css';

const GRAPH_URL = process.env.NEXT_PUBLIC_GRAPH_URL ??
  'https://api.studio.thegraph.com/query/1758922/modus-ops/v0.0.1';

const VERDICT_LABEL: Record<number, string> = {
  0: 'PROCEED', 1: 'DISMISS', 2: 'ESCALATE', 3: 'REVIEW',
};

const JURISDICTION_LABEL: Record<number, string> = {
  0: 'LOCAL', 1: 'STATE', 2: 'FEDERAL',
};

interface CaseEntity {
  id: string;
  caseId: string;
  verdict: number;
  confidenceScore: number;
  jurisdiction: number;
  timestamp: string;
  txHash: string;
  blockNumber: string;
}

const QUERY = `{
  cases(first: 20, orderBy: blockNumber, orderDirection: desc) {
    id
    caseId
    verdict
    confidenceScore
    jurisdiction
    timestamp
    txHash
    blockNumber
  }
}`;

export default function CasesPage() {
  const [cases, setCases] = useState<CaseEntity[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(GRAPH_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: QUERY }),
    })
      .then(r => r.json())
      .then(d => { setCases(d.data?.cases ?? []); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  return (
    <>
      <Nav />
      <main className={styles.main}>
        <div className={styles.header}>
          <div className={styles.label}>The Graph · Arbitrum One · modus-ops subgraph</div>
          <h1 className={styles.title}>Case History</h1>
        </div>

        {loading && <div className={styles.state}>Querying subgraph...</div>}
        {error && <div className={styles.error}>Subgraph error: {error}</div>}

        {!loading && cases.length === 0 && !error && (
          <div className={styles.state}>
            No verdicts on-chain yet. Submit a case to begin.
          </div>
        )}

        {cases.length > 0 && (
          <table className={styles.table}>
            <thead>
              <tr>
                <th className={styles.th}>Block</th>
                <th className={styles.th}>Case ID</th>
                <th className={styles.th}>Verdict</th>
                <th className={styles.th}>Confidence</th>
                <th className={styles.th}>Jurisdiction</th>
              </tr>
            </thead>
            <tbody>
              {cases.map(c => (
                <tr key={c.id} className={styles.tr}>
                  <td className={styles.td}><span className={styles.mono}>{c.blockNumber}</span></td>
                  <td className={styles.td}>
                    <Link href={`/case/${c.id}/verdict`} className={styles.caseLink}>
                      {c.id.slice(0, 10)}...
                    </Link>
                  </td>
                  <td className={styles.td}>
                    <span className={`${styles.verdict} ${styles['v' + c.verdict]}`}>
                      {VERDICT_LABEL[c.verdict] ?? c.verdict}
                    </span>
                  </td>
                  <td className={styles.td}><span className={styles.mono}>{c.confidenceScore}</span></td>
                  <td className={styles.td}><span className={styles.mono}>{JURISDICTION_LABEL[c.jurisdiction] ?? c.jurisdiction}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </main>
    </>
  );
}
