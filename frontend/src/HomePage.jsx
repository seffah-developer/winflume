import { Link } from 'react-router-dom'
import FlumeCarousel from './FlumeCarousel'

function HomePage() {
  return (
    <div style={{ textAlign: 'center', padding: '3rem 1rem', maxWidth: 900, margin: '0 auto' }}>
      <div style={{
        display: 'inline-block',
        fontFamily: 'var(--font-mono)',
        fontSize: 13,
        color: 'var(--accent-bright)',
        letterSpacing: '0.08em',
        border: '1px solid var(--accent-dim)',
        borderRadius: 20,
        padding: '0.3rem 0.9rem',
        marginBottom: '1.5rem',
      }}>
        OPEN CHANNEL FLOW MEASUREMENT
      </div>

      <h1 style={{ fontSize: '3rem', margin: '0 0 1rem' }}>WinFlume Pro Max</h1>
      <p style={{ fontSize: '1.15rem', color: 'var(--text-muted)', maxWidth: 560, margin: '0 auto 2.5rem', lineHeight: 1.6 }}>
        Enter your flow range, available head, and channel width.
        Get a matched flume, dimensioned diagrams, and discharge data — instantly.
      </p>

      <div style={{ marginBottom: '2.5rem' }}>
        <FlumeCarousel />
      </div>

      <Link
        to="/recommend"
        style={{
          display: 'inline-block',
          background: 'var(--accent)',
          color: '#0B1220',
          padding: '0.9rem 2.2rem',
          borderRadius: 8,
          fontSize: '1.05rem',
          fontWeight: 700,
          textDecoration: 'none',
        }}
      >
        Get a Flume Recommendation →
      </Link>
    </div>
  )
}

export default HomePage