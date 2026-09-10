'use client';
import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Nav from '../../components/Nav';
import styles from './page.module.css';

const API = process.env.NEXT_PUBLIC_API_URL ?? 'https://api.modusops.xyz';

export default function NewCase() {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [narrative, setNarrative] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files).filter(
      f => f.type === 'application/pdf' || f.name.endsWith('.csv') || f.name.endsWith('.txt')
    );
    setFiles(prev => [...prev, ...dropped]);
  }

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files) setFiles(prev => [...prev, ...Array.from(e.target.files!)]);
  }

  function removeFile(i: number) {
    setFiles(prev => prev.filter((_, idx) => idx !== i));
  }

  async function submit() {
    if (!narrative.trim() && files.length === 0) {
      setError('Provide a case narrative or upload at least one document.');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      let res: Response;
      if (files.length > 0) {
        const form = new FormData();
        form.append('description', narrative);
        files.forEach(f => form.append('files', f));
        res = await fetch(`${API}/api/cases/upload`, { method: 'POST', body: form });
      } else {
        res = await fetch(`${API}/api/cases`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ description: narrative }),
        });
      }
      if (!res.ok) throw new Error(await res.text());
      const { case_id } = await res.json();
      router.push(`/case/${case_id}`);
    } catch (e: any) {
      setError(e.message ?? 'Submission failed.');
      setSubmitting(false);
    }
  }

  return (
    <>
      <Nav />
      <main className={styles.main}>
        <div className={styles.header}>
          <div className={styles.label}>New Investigation</div>
          <h1 className={styles.title}>Submit Case File</h1>
          <p className={styles.sub}>
            Upload bank statements, transaction logs, or legal documents.
            The pipeline extracts evidence, builds adversarial briefs, and issues a
            verified verdict.
          </p>
        </div>

        <div className={styles.form}>
          <div className={styles.field}>
            <label className={styles.fieldLabel}>Case Narrative</label>
            <textarea
              className={styles.textarea}
              placeholder="Describe the suspected financial crime, entities involved, and any known facts..."
              value={narrative}
              onChange={e => setNarrative(e.target.value)}
              rows={5}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.fieldLabel}>Evidence Documents</label>
            <div
              className={styles.dropzone}
              onDragOver={e => e.preventDefault()}
              onDrop={onDrop}
              onClick={() => fileRef.current?.click()}
            >
              <input
                ref={fileRef}
                type="file"
                multiple
                accept=".pdf,.csv,.txt"
                onChange={onFileChange}
                className={styles.fileInput}
              />
              <span className={styles.dropText}>
                Drop PDF, CSV, or TXT files here — or click to browse
              </span>
            </div>

            {files.length > 0 && (
              <ul className={styles.fileList}>
                {files.map((f, i) => (
                  <li key={i} className={styles.fileItem}>
                    <span className={styles.fileName}>{f.name}</span>
                    <span className={styles.fileSize}>
                      {(f.size / 1024).toFixed(1)} KB
                    </span>
                    <button
                      className={styles.removeBtn}
                      onClick={() => removeFile(i)}
                      type="button"
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {error && <div className={styles.error}>{error}</div>}

          <button
            className={styles.submitBtn}
            onClick={submit}
            disabled={submitting}
            type="button"
          >
            {submitting ? 'Initiating pipeline...' : 'Open Investigation'}
          </button>
        </div>
      </main>
    </>
  );
}
