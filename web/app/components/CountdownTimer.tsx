'use client';

import { useEffect, useState } from 'react';
import styles from './Countdown.module.css';

const TARGET = new Date('2026-09-04T00:00:00-04:00').getTime();

type TimeLeft = {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
};

function getTimeLeft(): TimeLeft {
  const diff = Math.max(0, TARGET - Date.now());
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
  const minutes = Math.floor((diff / (1000 * 60)) % 60);
  const seconds = Math.floor((diff / 1000) % 60);
  return { days, hours, minutes, seconds };
}

function pad(n: number): string {
  return n.toString().padStart(2, '0');
}

export default function CountdownTimer() {
  const [timeLeft, setTimeLeft] = useState<TimeLeft | null>(null);

  useEffect(() => {
    setTimeLeft(getTimeLeft());
    const interval = setInterval(() => {
      setTimeLeft(getTimeLeft());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const display = timeLeft ?? { days: 0, hours: 0, minutes: 0, seconds: 0 };

  return (
    <div className={styles.grid}>
      <div className={styles.cell}>
        <div className={styles.number}>{pad(display.days)}</div>
        <div className={styles.label}>Days</div>
      </div>
      <div className={styles.cell}>
        <div className={styles.number}>{pad(display.hours)}</div>
        <div className={styles.label}>Hours</div>
      </div>
      <div className={styles.cell}>
        <div className={styles.number}>{pad(display.minutes)}</div>
        <div className={styles.label}>Min</div>
      </div>
      <div className={styles.cell}>
        <div className={styles.number}>{pad(display.seconds)}</div>
        <div className={styles.label}>Sec</div>
      </div>
    </div>
  );
}
