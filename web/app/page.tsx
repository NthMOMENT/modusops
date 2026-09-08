import Link from 'next/link';
import ReticleIcon from './components/ReticleIcon';
import Nav from './components/Nav';
import styles from './page.module.css';
import bannerStyles from './components/Banner.module.css';
import heroStyles from './components/Hero.module.css';
import statusStyles from './components/Status.module.css';
import agentsStyles from './components/Agents.module.css';
import footerStyles from './components/Footer.module.css';

const AGENTS = [
  {
    role: 'Judge',
    name: 'The Court',
    meta: 'Orchestrator · Arbiter / Final verdict authority',
    id: 'TOKEN #1416',
  },
  {
    role: 'Investigator',
    name: 'Law Enforcement',
    meta: 'Transaction tracing / Benford analysis · Timeline',
    id: 'TOKEN #1417',
  },
  {
    role: 'Prosecution',
    name: 'District Attorney',
    meta: 'Statute citation / Case construction · Argument',
    id: 'TOKEN #1418',
  },
  {
    role: 'Defense',
    name: 'Defense Counsel',
    meta: 'Red-team adversarial / Evidence challenge · Steelman',
    id: 'TOKEN #1419',
  },
];

export default function Home() {
  return (
    <>
      <div className={bannerStyles.banner}>
        <span className={bannerStyles.text}>
          RESTRICTED · UNITED STATES FEDERAL JURISDICTION ONLY · UNAUTHORIZED ACCESS PROHIBITED
        </span>
      </div>

      <Nav />

      <main className={styles.main}>
        <section className={heroStyles.hero}>
          <div className={heroStyles.meta}>
            Case No. ARB-2026-MNTN · Filed 2026-08-29 · Arbitrum Mainnet · ERC-8004
          </div>
          <div className={heroStyles.identityRow}>
            <ReticleIcon className={heroStyles.icon} />
            <h1 className={heroStyles.wordmark}>
              MODUS
              <span>OPS</span>
            </h1>
          </div>
          <p className={heroStyles.tagline}>
            Adversarial AI engine solving real-world financial crimes — four agents, one
            verdict, on-chain chain-of-custody.
          </p>
        </section>

        <section className={statusStyles.section}>
          <div className={statusStyles.sectionLabel}>System Status</div>
          <div className={statusStyles.statusRow}>
            <span className={statusStyles.dot} />
            <span className={statusStyles.statusText}>System Online</span>
          </div>
          <div className={statusStyles.ctaRow}>
            <Link href="/case/new/" className={statusStyles.ctaPrimary}>
              Submit Case File
            </Link>
            <Link href="/cases/" className={statusStyles.ctaSecondary}>
              Case History
            </Link>
          </div>
        </section>

        <section className={agentsStyles.section}>
          <div className={agentsStyles.sectionLabel}>
            Registered Agents · ERC-8004 Identity Registry · Arbitrum One
          </div>
          <div className={agentsStyles.grid}>
            {AGENTS.map((agent) => (
              <div className={agentsStyles.cell} key={agent.id}>
                <div className={agentsStyles.role}>{agent.role}</div>
                <div className={agentsStyles.name}>{agent.name}</div>
                <div className={agentsStyles.meta}>{agent.meta}</div>
                <div className={agentsStyles.id}>{agent.id}</div>
              </div>
            ))}
          </div>
        </section>

        <footer className={footerStyles.footer}>
          <div className={footerStyles.links}>
            <span>·</span>
            <span>·</span>
            <a
              className={footerStyles.link}
              href="https://github.com/NthMOMENT/modusops"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
            <span>·</span>
            <span>BUSL-1.1</span>
          </div>
          <p className={footerStyles.notice}>
            This system operates exclusively under United States federal law. Use outside the
            United States is not authorized and may violate local regulations. The operator
            assumes no liability for unauthorized use beyond US jurisdiction.
          </p>
        </footer>
      </main>
    </>
  );
}
