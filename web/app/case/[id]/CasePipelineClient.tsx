'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import Nav from '../../components/Nav';
import styles from './page.module.css';

const API = process.env.NEXT_PUBLIC_API_URL ?? 'https://api.modusops.xyz';

type StepStatus = 'pending' | 'running' | 'done' | 'error';

interface PipelineStatus {
  case_id: string;
  status: 'running' | 'complete' | 'error';
  steps: {
    law_enforcement: StepStatus;
    prosecutor: StepStatus;
    defense: StepStatus;
    judge: StepStatus;
  };
  jurisdiction?: string;
  created_at?: string;
}

const STEP_LABELS: Record<string, string> = {
  law_enforcement: 'Law Enforcement — Evidence & Timeline',
  prosecutor: 'District Attorney — Prosecution Brief',
  defense: 'Defense Counsel — Adversarial Challenge',
  judge: 'The Court — Judicial Review & Verdict',
};

const STEP_ORDER = ['law_enforcement', 'prosecutor', 'defense', 'judge'];

export default function CasePipelineClient({ caseId }: { caseId: string }) {
  const [data, setData] = useState<PipelineStatus | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!caseId) return;
    let cancelled = false;

    async function poll() {
      try {
        const res = await fetch(`${API}/cases/${caseId}/status`);
        if (!res.ok) throw new Error(`${res.status}`);
        const json = await res.json();
        if (!cancelled) {
          setData(json);
          if (json.status === 'running') {
            setTimeout(poll, 3000);
          }
        }
      } catch (e: any) {
        if (!cancelled) setError(e.message);
      }
    }

    poll();
    return () => { cancelled = true; };
  }, [caseId]);

  return (
    <>
      <Nav />
      <main className={styles.main}>
        <div className={styles.header}>
          <div className={styles.label}>
            Case {caseId ?? '—'}
            {data?.jurisdiction && (
              <span className={styles.jurisdiction}> · {data.jurisdiction} JURISDICTION</span>
            )}
          </div>
          <h1 className={styles.title}>Investigation Pipeline</h1>
        </div>

        {error && <div className={styles.error}>Connection error: {error}</div>}

        <div className={styles.pipeline}>
          {STEP_ORDER.map((step, i) => {
            const status: StepStatus = data?.steps?.[step as keyof typeof data.steps] ?? 'pending';
            return (
              <div key={step} className={`${styles.step} ${styles[status]}`}>
                <div className={styles.stepIndex}>{String(i + 1).padStart(2, '0')}</div>
                <div className={styles.stepBody}>
                  <div className={styles.stepName}>{STEP_LABELS[step]}</div>
                  <div className={styles.stepStatus}>{status.toUpperCase()}</div>
                </div>
                <div className={styles.stepIndicator} />
              </div>
            );
          })}
        </div>

        {data?.status === 'complete' && (
          <div className={styles.verdictReady}>
            <span className={styles.verdictReadyText}>Verdict ready</span>
            <Link href={`/case/${caseId}/verdict`} className={styles.verdictLink}>
              View Judicial Ruling
            </Link>
          </div>
        )}

        {!data && !error && (
          <div className={styles.loading}>Connecting to pipeline...</div>
        )}
      </main>
    </>
  );
}
