import Link from 'next/link';
import styles from './Nav.module.css';

export default function Nav() {
  return (
    <nav className={styles.nav}>
      <Link href="/" className={styles.wordmark}>MODUS OPS</Link>
      <div className={styles.links}>
        <Link href="/case/new" className={styles.link}>New Case</Link>
        <Link href="/cases" className={styles.link}>Case History</Link>
      </div>
    </nav>
  );
}
