import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'URBAN-COOL AI | Urban Heat Intelligence & Cooling Optimization',
  description: 'Geospatial AI platform for urban heat-stress mapping, remote sensing prediction, and cooling optimization.',
  keywords: ['Geospatial AI', 'Urban Heat Island', 'Land Surface Temperature', 'Urban Cooling', 'FastAPI', 'Next.js'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
