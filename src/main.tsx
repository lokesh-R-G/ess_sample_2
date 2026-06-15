import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// Suppress known ApexCharts benign runtime errors in development to avoid noisy console crashes.
if (typeof window !== 'undefined') {
  window.addEventListener('error', (e: ErrorEvent) => {
    try {
      const msg = e?.message || '';
      if (msg.includes('runMaskReveal') || msg.includes('__apexParsed')) {
        e.preventDefault();
      }
    } catch {
      // ignore
    }
  });
  window.addEventListener('unhandledrejection', (ev: PromiseRejectionEvent) => {
    try {
      const reason = (ev && (ev.reason || '') ) as any;
      const msg = typeof reason === 'string' ? reason : reason?.message || '';
      if (msg && (msg.includes('runMaskReveal') || msg.includes('__apexParsed'))) {
        ev.preventDefault();
      }
    } catch {
      // ignore
    }
  });
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
