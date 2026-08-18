import { useState } from 'react'
import FlumeDetail from './FlumeDetail'
import { API_BASE_URL } from './config'

const FLOW_TO_GPM = {
  gpm: 1,
  cfs: 448.831,
  lps: 15.8503,
}

const LENGTH_TO_FT = {
  ft: 1,
  in: 1 / 12,
  m: 3.28084,
  cm: 0.0328084,
}

const LENGTH_TO_CM = {
  cm: 1,
  in: 2.54,
  ft: 30.48,
  m: 100,
}

const MAX_HEAD_LOSS_FT = 7

const CHANNEL_TYPE_LABELS = {
  concrete: 'Concrete-lined channel',
  earthen: 'Earthen / dirt channel',
  grass: 'Grass-lined channel',
}

const cardStyle = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 12,
  padding: '1.5rem',
}

const fieldLabelStyle = {
  display: 'block',
  fontSize: 13,
  color: 'var(--text-muted)',
  marginBottom: 6,
  fontFamily: 'var(--font-mono)',
  letterSpacing: '0.03em',
}

function RecommenderForm() {
  const [minFlow, setMinFlow] = useState('')
  const [maxFlow, setMaxFlow] = useState('')
  const [flowUnit, setFlowUnit] = useState('gpm')
  const [openDiagramId, setOpenDiagramId] = useState(null)

  const [channelType, setChannelType] = useState('concrete')
  const [knowsHeadLoss, setKnowsHeadLoss] = useState(false)
  const [headLossFt, setHeadLossFt] = useState(MAX_HEAD_LOSS_FT)

  const [channelWidth, setChannelWidth] = useState('')
  const [widthUnit, setWidthUnit] = useState('cm')

  const [results, setResults] = useState(null)
  const [usedHeadFt, setUsedHeadFt] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setResults(null)

    if (!minFlow || !maxFlow || !channelWidth) {
      setError('Please fill in all fields.')
      return
    }

    const minFlowGpm = parseFloat(minFlow) * FLOW_TO_GPM[flowUnit]
    const maxFlowGpm = parseFloat(maxFlow) * FLOW_TO_GPM[flowUnit]
    const availableHeadFt = knowsHeadLoss ? headLossFt : MAX_HEAD_LOSS_FT
    const channelWidthCm = parseFloat(channelWidth) * LENGTH_TO_CM[widthUnit]

    setLoading(true)
    const startTime = Date.now()
    const MIN_LOADING_MS = 1000

    try {
      const params = new URLSearchParams({
        min_flow_gpm: minFlowGpm,
        max_flow_gpm: maxFlowGpm,
        available_head_ft: availableHeadFt,
        channel_width_cm: channelWidthCm,
      })
      const res = await fetch(`${API_BASE_URL}/recommend?${params}`)
      if (!res.ok) throw new Error(`Server returned ${res.status}`)
      const data = await res.json()

      const elapsed = Date.now() - startTime
      if (elapsed < MIN_LOADING_MS) {
        await new Promise((resolve) => setTimeout(resolve, MIN_LOADING_MS - elapsed))
      }

      setResults(data)
      setUsedHeadFt(availableHeadFt)
    } catch (err) {
      setError('Error connecting to backend: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const fittingResults = results ? results.filter((r) => r.fits) : []
  const nonFittingResults = results ? results.filter((r) => !r.fits) : []

  return (
    <div style={{ maxWidth: 720, margin: '0 auto', textAlign: 'left', padding: '1rem' }}>
      <h2 style={{ marginBottom: '1.5rem' }}>Flume Recommender</h2>

      <form onSubmit={handleSubmit} style={{ ...cardStyle, display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

        <div>
          <label style={fieldLabelStyle}>EXPECTED FLOW RANGE</label>
          <input
            type="number" step="any" placeholder="Min"
            value={minFlow} onChange={(e) => setMinFlow(e.target.value)}
            style={{ width: 90, marginRight: 8 }}
          />
          <input
            type="number" step="any" placeholder="Max"
            value={maxFlow} onChange={(e) => setMaxFlow(e.target.value)}
            style={{ width: 90, marginRight: 8 }}
          />
          <select value={flowUnit} onChange={(e) => setFlowUnit(e.target.value)}>
            <option value="gpm">GPM</option>
            <option value="cfs">CFS</option>
            <option value="lps">L/S</option>
          </select>
        </div>

        <div>
          <label style={fieldLabelStyle}>CHANNEL TYPE</label>
          <select
            value={channelType}
            onChange={(e) => setChannelType(e.target.value)}
            style={{ width: '100%' }}
          >
            <option value="concrete">{CHANNEL_TYPE_LABELS.concrete}</option>
            <option value="earthen">{CHANNEL_TYPE_LABELS.earthen}</option>
            <option value="grass">{CHANNEL_TYPE_LABELS.grass}</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={knowsHeadLoss}
              onChange={(e) => setKnowsHeadLoss(e.target.checked)}
            />
            <span style={fieldLabelStyle}>I KNOW MY AVAILABLE HEAD LOSS / DROP</span>
          </label>

          {knowsHeadLoss ? (
            <div style={{ marginTop: 10 }}>
              <label style={fieldLabelStyle}>
                AVAILABLE DROP: <span style={{ color: 'var(--accent-bright)' }}>{headLossFt.toFixed(1)} ft</span>
              </label>
              <input
                type="range"
                min="0"
                max={MAX_HEAD_LOSS_FT}
                step="0.1"
                value={headLossFt}
                onChange={(e) => setHeadLossFt(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent)' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                <span>0 ft</span>
                <span>{MAX_HEAD_LOSS_FT} ft</span>
              </div>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6, marginBottom: 0 }}>
                This is how much the water level can drop across the flume - usually the difference
                in elevation between the channel just before and just after where you'd install it.
              </p>
            </div>
          ) : (
            <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6, marginBottom: 0 }}>
              Not sure? Leave this unchecked and we'll consider all flumes regardless of head loss.
            </p>
          )}
        </div>

        <div>
          <label style={fieldLabelStyle}>CHANNEL WIDTH</label>
          <input
            type="number" step="any"
            value={channelWidth} onChange={(e) => setChannelWidth(e.target.value)}
            style={{ width: 90, marginRight: 8 }}
          />
          <select value={widthUnit} onChange={(e) => setWidthUnit(e.target.value)}>
            <option value="cm">cm</option>
            <option value="in">in</option>
            <option value="ft">ft</option>
            <option value="m">m</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            padding: '0.7rem 1rem', background: 'var(--accent)', color: '#0B1220',
            border: 'none', borderRadius: 8, fontWeight: 700, fontSize: 15,
          }}
        >
          {loading && (
            <span style={{
              display: 'inline-block', width: 16, height: 16,
              border: '2px solid #0B122055', borderTopColor: '#0B1220',
              borderRadius: '50%', animation: 'winflume-spin 0.7s linear infinite',
            }} />
          )}
          {loading ? 'Finding flumes...' : 'Recommend a Flume'}
        </button>
        <style>{`
          @keyframes winflume-spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}</style>
      </form>

      {loading && (
        <div style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--text-muted)' }}>
          <div style={{
            width: 40, height: 40, border: '4px solid var(--surface-raised)',
            borderTopColor: 'var(--accent)', borderRadius: '50%',
            margin: '0 auto 1rem', animation: 'winflume-spin 0.8s linear infinite',
          }} />
          Searching the catalog for the best fit...
        </div>
      )}

      {error && <p style={{ color: '#f87171', marginTop: '1rem' }}>{error}</p>}

      {results && !loading && (
        <div style={{ marginTop: '2rem' }}>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)' }}>
            {knowsHeadLoss
              ? `Calculated using ${usedHeadFt?.toFixed(1)} ft of available head loss.`
              : 'Head loss was not restricted - showing flumes based on flow range and channel width only.'}
          </p>
          <h3 style={{ color: 'var(--success)' }}>Recommended ({fittingResults.length})</h3>
          {fittingResults.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No flumes in the catalog fit these requirements.</p>}
          {fittingResults.map((r) => (
            <div key={r.id} style={{ ...cardStyle, border: '1px solid var(--success)', marginBottom: '0.75rem' }}>
              <strong style={{ fontFamily: 'var(--font-display)' }}>{r.flume_type} — {r.size_label}</strong>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--text-muted)', marginTop: 8 }}>
                <div>Flow range: {r.min_flow_gpm?.toFixed(2)} – {r.max_flow_gpm?.toFixed(2)} GPM</div>
                <div>Required head: {r.required_head_ft?.toFixed(2)} ft</div>
                <div>Flume width: {r.flume_width_cm?.toFixed(1)} cm</div>
              </div>
              {r.characteristics && (
                <div style={{ marginTop: 10, fontSize: 13, color: 'var(--text)', lineHeight: 1.5 }}>
                  <div><strong style={{ color: 'var(--accent-bright)' }}>Best for:</strong> {r.characteristics.best_for}</div>
                  <div style={{ marginTop: 4 }}><strong style={{ color: 'var(--accent-bright)' }}>Sediment:</strong> {r.characteristics.sediment_handling}</div>
                </div>
              )}
              <button
                type="button"
                onClick={() => setOpenDiagramId(openDiagramId === r.id ? null : r.id)}
                style={{
                  marginTop: 12, background: 'var(--surface-raised)', color: 'var(--accent-bright)',
                  border: '1px solid var(--border)', borderRadius: 6, padding: '0.4rem 0.9rem', fontSize: 13,
                }}
              >
                {openDiagramId === r.id ? 'Hide Details' : 'View Details'}
              </button>
              {openDiagramId === r.id && <FlumeDetail flumeId={r.id} />}
            </div>
          ))}

          <h3 style={{ marginTop: '2rem', color: 'var(--text-muted)' }}>Not a fit ({nonFittingResults.length})</h3>
          {nonFittingResults.map((r) => (
            <div key={r.id} style={{ ...cardStyle, opacity: 0.6, marginBottom: '0.5rem' }}>
              <strong>{r.flume_type} — {r.size_label}</strong>
              <ul style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)', margin: '0.5rem 0 0' }}>
                {r.reasons_excluded.map((reason, i) => (
                  <li key={i}>{reason}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default RecommenderForm
