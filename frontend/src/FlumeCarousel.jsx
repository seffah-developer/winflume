import { useState, useEffect } from 'react'

const SLIDES = [
  { key: 'trapezoidal', label: '60° V-Trapezoidal Flume' },
  { key: 'rbc', label: 'RBC Flume' },
  { key: 'wsc', label: 'WSC Flat-Bottom Flume' },
]

function TrapezoidalSchematic() {
  return (
    <g>
      <polygon
        points="120,140 120,260 260,220 460,220 600,260 600,140 460,180 260,180"
        fill="none" stroke="var(--accent)" strokeWidth="3"
      />
      <line x1="60" y1="200" x2="110" y2="200" stroke="var(--accent-bright)" strokeWidth="3" markerEnd="url(#carousel-arrow)" />
      <line x1="60" y1="200" x2="660" y2="200" stroke="var(--accent-dim)" strokeWidth="1" strokeDasharray="6,6" />
    </g>
  )
}

function RBCSchematic() {
  return (
    <g>
      <polygon
        points="100,150 100,250 220,180 500,180 620,250 620,150"
        fill="none" stroke="var(--accent)" strokeWidth="3"
      />
      <path d="M 110,240 Q 250,240 300,215 L 420,215 Q 470,240 610,240" fill="none" stroke="var(--accent-bright)" strokeWidth="2" />
      <line x1="60" y1="200" x2="110" y2="200" stroke="var(--accent-bright)" strokeWidth="3" markerEnd="url(#carousel-arrow)" />
    </g>
  )
}

function WSCSchematic() {
  return (
    <g>
      <polygon
        points="100,150 100,250 240,200 480,200 620,250 620,150 480,200 240,200"
        fill="none" stroke="var(--accent)" strokeWidth="3"
      />
      <rect x="240" y="195" width="240" height="10" fill="none" stroke="var(--accent-bright)" strokeWidth="2" />
      <line x1="60" y1="200" x2="110" y2="200" stroke="var(--accent-bright)" strokeWidth="3" markerEnd="url(#carousel-arrow)" />
    </g>
  )
}

const SCHEMATIC_COMPONENTS = {
  trapezoidal: TrapezoidalSchematic,
  rbc: RBCSchematic,
  wsc: WSCSchematic,
}

function FlumeCarousel() {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % SLIDES.length)
    }, 3500)
    return () => clearInterval(interval)
  }, [])

  const ActiveSchematic = SCHEMATIC_COMPONENTS[SLIDES[index].key]

  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 16,
      padding: '2rem',
      maxWidth: 700,
      margin: '0 auto',
    }}>
      <svg viewBox="0 0 680 320" style={{ width: '100%', height: 'auto' }}>
        <defs>
          <marker id="carousel-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="var(--accent-bright)" />
          </marker>
          <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
            <path d="M 30 0 L 0 0 0 30" fill="none" stroke="var(--border)" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="680" height="320" fill="url(#grid)" />
        <ActiveSchematic />
      </svg>

      <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: '1rem' }}>
        {SLIDES.map((slide, i) => (
          <button
            key={slide.key}
            onClick={() => setIndex(i)}
            style={{
              background: 'none',
              border: 'none',
              padding: '0.4rem 0.8rem',
              borderRadius: 20,
              fontSize: 13,
              color: i === index ? 'var(--accent-bright)' : 'var(--text-muted)',
              fontWeight: i === index ? 600 : 400,
              background: i === index ? 'var(--accent-dim)' : 'transparent',
            }}
          >
            {slide.label}
          </button>
        ))}
      </div>
    </div>
  )
}

export default FlumeCarousel