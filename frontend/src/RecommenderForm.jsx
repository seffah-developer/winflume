import { useState } from 'react'

// --- Unit conversion helpers ---
const FLOW_TO_GPM = {
  gpm: 1,
  cfs: 448.831,
  lps: 15.8503, // liters per second -> gpm
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

function RecommenderForm() {
  const [minFlow, setMinFlow] = useState('')
  const [maxFlow, setMaxFlow] = useState('')
  const [flowUnit, setFlowUnit] = useState('gpm')

  const [headLoss, setHeadLoss] = useState('')
  const [headUnit, setHeadUnit] = useState('ft')

  const [channelWidth, setChannelWidth] = useState('')
  const [widthUnit, setWidthUnit] = useState('cm')

  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setResults(null)

    if (!minFlow || !maxFlow || !headLoss || !channelWidth) {
      setError('Please fill in all fields.')
      return
    }

    const minFlowGpm = parseFloat(minFlow) * FLOW_TO_GPM[flowUnit]
    const maxFlowGpm = parseFloat(maxFlow) * FLOW_TO_GPM[flowUnit]
    const availableHeadFt = parseFloat(headLoss) * LENGTH_TO_FT[headUnit]
    const channelWidthCm = parseFloat(channelWidth) * LENGTH_TO_CM[widthUnit]

    setLoading(true)
    try {
      const params = new URLSearchParams({
        min_flow_gpm: minFlowGpm,
        max_flow_gpm: maxFlowGpm,
        available_head_ft: availableHeadFt,
        channel_width_cm: channelWidthCm,
      })
      const res = await fetch(`http://127.0.0.1:8000/recommend?${params}`)
      if (!res.ok) throw new Error(`Server returned ${res.status}`)
      const data = await res.json()
      setResults(data)
    } catch (err) {
      setError('Error connecting to backend: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const fittingResults = results ? results.filter((r) => r.fits) : []
  const nonFittingResults = results ? results.filter((r) => !r.fits) : []

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', textAlign: 'left' }}>
      <h2>Flume Recommender</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

        <div>
          <label>Expected flow range: </label>
          <input
            type="number"
            step="any"
            placeholder="Min"
            value={minFlow}
            onChange={(e) => setMinFlow(e.target.value)}
            style={{ width: 80, marginRight: 8 }}
          />
          <input
            type="number"
            step="any"
            placeholder="Max"
            value={maxFlow}
            onChange={(e) => setMaxFlow(e.target.value)}
            style={{ width: 80, marginRight: 8 }}
          />
          <select value={flowUnit} onChange={(e) => setFlowUnit(e.target.value)}>
            <option value="gpm">GPM</option>
            <option value="cfs">CFS</option>
            <option value="lps">L/S</option>
          </select>
        </div>

        <div>
          <label>Available head loss: </label>
          <input
            type="number"
            step="any"
            value={headLoss}
            onChange={(e) => setHeadLoss(e.target.value)}
            style={{ width: 80, marginRight: 8 }}
          />
          <select value={headUnit} onChange={(e) => setHeadUnit(e.target.value)}>
            <option value="ft">ft</option>
            <option value="in">in</option>
            <option value="m">m</option>
            <option value="cm">cm</option>
          </select>
        </div>

        <div>
          <label>Channel width: </label>
          <input
            type="number"
            step="any"
            value={channelWidth}
            onChange={(e) => setChannelWidth(e.target.value)}
            style={{ width: 80, marginRight: 8 }}
          />
          <select value={widthUnit} onChange={(e) => setWidthUnit(e.target.value)}>
            <option value="cm">cm</option>
            <option value="in">in</option>
            <option value="ft">ft</option>
            <option value="m">m</option>
          </select>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Finding flumes...' : 'Recommend a Flume'}
        </button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {results && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Recommended ({fittingResults.length})</h3>
          {fittingResults.length === 0 && <p>No flumes in the catalog fit these requirements.</p>}
          {fittingResults.map((r) => (
            <div key={r.id} style={{ border: '2px solid green', borderRadius: 8, padding: '0.75rem', marginBottom: '0.5rem' }}>
              <strong>{r.flume_type} - {r.size_label}</strong>
              <div>Flow range: {r.min_flow_gpm?.toFixed(2)} - {r.max_flow_gpm?.toFixed(2)} GPM</div>
              <div>Required head: {r.required_head_ft?.toFixed(2)} ft</div>
              <div>Flume width: {r.flume_width_cm?.toFixed(1)} cm</div>
            </div>
          ))}

          <h3 style={{ marginTop: '1.5rem' }}>Not a fit ({nonFittingResults.length})</h3>
          {nonFittingResults.map((r) => (
            <div key={r.id} style={{ border: '1px solid #ccc', borderRadius: 8, padding: '0.75rem', marginBottom: '0.5rem', opacity: 0.7 }}>
              <strong>{r.flume_type} - {r.size_label}</strong>
              <ul>
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