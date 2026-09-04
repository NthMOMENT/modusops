export default function ReticleIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      width="96"
      height="96"
      viewBox="0 0 96 96"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      {/* outer circle */}
      <circle cx="48" cy="48" r="44" stroke="var(--blue)" strokeWidth="1.5" />
      {/* inner circle */}
      <circle cx="48" cy="48" r="34" stroke="var(--blue)" strokeWidth="1" opacity="0.5" />
      {/* cardinal ticks — extend beyond outer ring */}
      <line x1="48" y1="0" x2="48" y2="10" stroke="var(--blue)" strokeWidth="1.5" strokeLinecap="square" />
      <line x1="48" y1="86" x2="48" y2="96" stroke="var(--blue)" strokeWidth="1.5" strokeLinecap="square" />
      <line x1="0" y1="48" x2="10" y2="48" stroke="var(--blue)" strokeWidth="1.5" strokeLinecap="square" />
      <line x1="86" y1="48" x2="96" y2="48" stroke="var(--blue)" strokeWidth="1.5" strokeLinecap="square" />
      {/* inner crosshair — shorter, faint */}
      <line x1="48" y1="14" x2="48" y2="26" stroke="var(--blue)" strokeWidth="0.75" opacity="0.35" />
      <line x1="48" y1="70" x2="48" y2="82" stroke="var(--blue)" strokeWidth="0.75" opacity="0.35" />
      <line x1="14" y1="48" x2="26" y2="48" stroke="var(--blue)" strokeWidth="0.75" opacity="0.35" />
      <line x1="70" y1="48" x2="82" y2="48" stroke="var(--blue)" strokeWidth="0.75" opacity="0.35" />
      {/* center ring */}
      <circle cx="48" cy="48" r="8" stroke="var(--blue)" strokeWidth="1" opacity="0.65" />
      {/* center fill dot */}
      <circle cx="48" cy="48" r="3.5" fill="var(--blue)" />
    </svg>
  );
}
