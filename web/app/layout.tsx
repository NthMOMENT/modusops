import type { Metadata } from 'next';
import { Barlow_Condensed, IBM_Plex_Mono } from 'next/font/google';
import './globals.css';

const barlowCondensed = Barlow_Condensed({
  subsets: ['latin'],
  weight: ['300', '700', '800'],
  variable: '--font-barlow',
  display: 'swap',
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['300', '400', '500'],
  variable: '--font-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Modus Ops',
  description:
    'Adversarial AI engine solving real-world financial crimes — four agents, one verdict, on-chain chain-of-custody.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${barlowCondensed.variable} ${ibmPlexMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
