function HeroIllustration() {
  return (
    <svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', maxWidth: 700, height: 'auto' }}>
      {/* Sky/background */}
      <rect width="800" height="400" fill="#f0f9ff" rx="12" />

      {/* Ground / channel banks */}
      <rect x="0" y="260" width="800" height="140" fill="#d9c9a3" />
      <rect x="0" y="260" width="800" height="10" fill="#b8a37e" />

      {/* Channel water (upstream and downstream of flume) */}
      <rect x="0" y="280" width="260" height="60" fill="#7dd3fc" />
      <rect x="540" y="280" width="260" height="60" fill="#7dd3fc" />

      {/* Flume body - plan-ish stylized side view: wide entrance, narrow throat, wide exit */}
      <polygon
        points="230,270 230,350 330,320 470,320 570,350 570,270 470,300 330,300"
        fill="#dbeafe"
        stroke="#1e3a8a"
        strokeWidth="4"
      />

      {/* Water surface inside flume, dipping through the throat */}
      <path
        d="M 240,300 Q 300,300 330,308 L 470,308 Q 500,300 560,300"
        stroke="#0284c7"
        strokeWidth="4"
        fill="none"
      />

      {/* Flow arrows */}
      <g stroke="#0369a1" strokeWidth="4" fill="none" markerEnd="url(#arrowhead)">
        <line x1="80" y1="310" x2="180" y2="310" />
        <line x1="620" y1="310" x2="720" y2="310" />
      </g>
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="#0369a1" />
        </marker>
      </defs>

      {/* Simple sun/decoration */}
      <circle cx="700" cy="70" r="35" fill="#fde68a" />
    </svg>
  )
}

export default HeroIllustration