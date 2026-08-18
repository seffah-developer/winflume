import { useState, useRef, useEffect } from 'react'
import { API_BASE_URL } from './config'

const FLOW_TO_GPM = {
  gpm: 1,
  cfs: 448.831,
  lps: 15.8503,
}

function CustomRbcDesigner() {
  const [targetFlow, setTargetFlow] = useState('')
  const [flowUnit, setFlowUnit] = useState('gpm')
  const [minFlow, setMinFlow] = useState('')
  const [maxWidth, setMaxWidth] = useState('')
  const [design, setDesign] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const chartRef = useRef(null)
  const chartInstance = useRef(null)

  useEffect(() => {
    if (window.Chart) return
    const script = document.createElement('script')
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js'
    document.head.appendChild(script)
  }, [])

  useEffect(() => {
    if (!design || !design.hydraulics.discharge_table) return

    function drawChart() {
      if (!window.Chart || !chartRef.current) return
      const table = design.hydraulics.discharge_table
      const nearestSizes = design.hydraulics.nearest_real_sizes_mm || []
      const labels = table.map((r) => r.head_ft.toFixed(3))
      const custom = table.map((r) => r.flow_gpm)

      const neighborColors = ['#2a78d6', '#34D399']
      const neighborDatasets = nearestSizes.map((sizeMm, i) => ({
        label: `Real ${sizeMm}mm (reference)`,
        data: table.map((r) => r[`real_${sizeMm}mm_gpm`]),
        borderColor: neighborColors[i % neighborColors.length],
        backgroundColor: 'transparent',
        borderWidth: 1.5,
        borderDash: [5, 3],
        pointRadius: 0,
        tension: 0.15,
      }))

      if (chartInstance.current) chartInstance.current.destroy()

      chartInstance.current = new window.Chart(chartRef.current, {
        type: 'line',
        data: {
          labels,
          datasets: [
            { label: `Custom ${design.throat_width_mm.toFixed(0)}mm design`, data: custom, borderColor: '#eb6834', backgroundColor: 'transparent', borderWidth: 2.5, pointRadius: 0, tension: 0.15 },
            ...neighborDatasets,
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: true, labels: { color: '#8FA8C4' } } },
          scales: {
            x: { title: { display: true, text: 'Head (ft)', color: '#8FA8C4' }, grid: { display: false }, ticks: { color: '#8FA8C4', maxTicksLimit: 8 } },
            y: { title: { display: true, text: 'Flow (GPM)', color: '#8FA8C4' }, grid: { color: '#253449' }, ticks: { color: '#8FA8C4' } },
          },
        },
      })
    }

    if (window.Chart) {
      drawChart()
    } else {
      const interval = setInterval(() => {
        if (window.Chart) {
          clearInterval(interval)
          drawChart()
        }
      }, 100)
      return () => clearInterval(interval)
    }
  }, [design])

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setDesign(null)

    if (!targetFlow) {
      setError('Enter a target maximum flow.')
      return
    }

    const targetGpm = parseFloat(targetFlow) * FLOW_TO_GPM[flowUnit]
    const minFlowGpm = minFlow ? parseFloat(minFlow) * FLOW_TO_GPM[flowUnit] : null
    const maxWidthCm = maxWidth ? parseFloat(maxWidth) : null

    setLoading(true)
    try {
      const params = new URLSearchParams({ target_max_flow_gpm: targetGpm })
      if (minFlowGpm !== null) params.set('target_min_flow_gpm', minFlowGpm)
      if (maxWidthCm !== null) params.set('max_channel_width_cm', maxWidthCm)

      const res = await fetch(`${API_BASE_URL}/design/rbc-custom?${params}`)
      if (!res.ok) throw new Error(`Server returned ${res.status}`)
      const data = await res.json()
      setDesign(data)
    } catch (err) {
      setError('Error connecting to backend: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const cardStyle = {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 12,
    padding: '1.5rem',
  }

  const diagramPanelStyle = {
    background: 'var(--bg)',
    borderRadius: 8,
    padding: '0.5rem',
    marginBottom: 12,
    border: '1px solid var(--border)',
  }

  const sectionLabelStyle = {
    fontFamily: 'var(--font-mono)', fontSize: 12, letterSpacing: '0.05em',
    color: 'var(--accent-bright)', marginBottom: 8, textTransform: 'uppercase',
  }

  const targetGpmForImg = design ? parseFloat(targetFlow) * FLOW_TO_GPM[flowUnit] : null
  const diagramParams = design
    ? new URLSearchParams({
        target_max_flow_gpm: targetGpmForImg,
        ...(minFlow ? { target_min_flow_gpm: parseFloat(minFlow) * FLOW_TO_GPM[flowUnit] } : {}),
        ...(maxWidth ? { max_channel_width_cm: parseFloat(maxWidth) } : {}),
      }).toString()
    : ''

  return (
    <div style={{ maxWidth: 720, margin: '0 auto', textAlign: 'left', padding: '1rem' }}>
      <h2>Custom RBC Flume Designer</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: 14, lineHeight: 1.6 }}>
        This design is generated by interpolating from the 5 real, physically-calibrated RBC flumes
        in the catalog (50, 75, 100, 150, 200mm) - separately validated at 1-5% accuracy against
        those real sizes. Accuracy is strongest for throat widths between 50mm and 200mm; results
        outside that range extrapolate and should be treated with more caution.
      </p>

      <form onSubmit={handleSubmit} style={{ ...cardStyle, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div>
          <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6, fontFamily: 'var(--font-mono)' }}>
            DESIRED MAXIMUM FLOW
          </label>
          <input
            type="number" step="any" placeholder="e.g. 250"
            value={targetFlow} onChange={(e) => setTargetFlow(e.target.value)}
            style={{ width: 120, marginRight: 8 }}
          />
          <select value={flowUnit} onChange={(e) => setFlowUnit(e.target.value)}>
            <option value="gpm">GPM</option>
            <option value="cfs">CFS</option>
            <option value="lps">L/S</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6, fontFamily: 'var(--font-mono)' }}>
            MINIMUM FLOW YOU NEED TO MEASURE ACCURATELY (optional)
          </label>
          <input
            type="number" step="any" placeholder="e.g. 5"
            value={minFlow} onChange={(e) => setMinFlow(e.target.value)}
            style={{ width: 120, marginRight: 8 }}
          />
          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{flowUnit.toUpperCase()} (uses the same unit as above)</span>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6, fontFamily: 'var(--font-mono)' }}>
            MAX CHANNEL WIDTH (optional, cm)
          </label>
          <input
            type="number" step="any" placeholder="e.g. 40"
            value={maxWidth} onChange={(e) => setMaxWidth(e.target.value)}
            style={{ width: 120 }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '0.7rem 1rem', background: 'var(--accent)', color: '#0B1220',
            border: 'none', borderRadius: 8, fontWeight: 700, fontSize: 15,
          }}
        >
          {loading ? 'Designing...' : 'Design Flume'}
        </button>
      </form>

      {error && <p style={{ color: '#f87171', marginTop: '1rem' }}>{error}</p>}

      {design && (
        <div style={{ ...cardStyle, marginTop: '1.5rem' }}>
          <h3 style={{ marginTop: 0 }}>
            Custom RBC Flume - {design.throat_width_mm.toFixed(1)} mm throat width
          </h3>

          <p style={{
            fontSize: 13,
            color: design.in_confirmed_range ? 'var(--success)' : 'var(--warning, #FBBF24)',
            fontFamily: 'var(--font-mono)',
          }}>
            {design.confidence_note}
          </p>

          {design.warnings && design.warnings.length > 0 && (
            <div style={{
              background: '#3A2A0F', border: '1px solid #FBBF24', borderRadius: 8,
              padding: '0.75rem 1rem', marginBottom: 16,
            }}>
              {design.warnings.map((w, i) => (
                <p key={i} style={{ fontSize: 13, color: '#FDE68A', margin: i === 0 ? 0 : '8px 0 0' }}>
                  ⚠️ {w}
                </p>
              ))}
            </div>
          )}

          <div style={sectionLabelStyle}>Plan View</div>
          <div style={diagramPanelStyle}>
            <img
              src={`${API_BASE_URL}/design/rbc-custom/diagram?${diagramParams}`}
              alt="Plan view" style={{ maxWidth: '100%', display: 'block' }}
            />
          </div>

          <div style={sectionLabelStyle}>Elevation View</div>
          <div style={diagramPanelStyle}>
            <img
              src={`${API_BASE_URL}/design/rbc-custom/diagram/elevation?${diagramParams}`}
              alt="Elevation view" style={{ maxWidth: '100%', display: 'block' }}
            />
          </div>

          <div style={sectionLabelStyle}>End View</div>
          <div style={diagramPanelStyle}>
            <img
              src={`${API_BASE_URL}/design/rbc-custom/diagram/end?${diagramParams}`}
              alt="End view" style={{ maxWidth: '100%', display: 'block' }}
            />
          </div>

          <div style={sectionLabelStyle}>Geometry (cm)</div>
          <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 13, fontFamily: 'var(--font-mono)', marginBottom: 16 }}>
            <tbody>
              {Object.entries(design.geometry).filter(([k]) => k !== 'units').map(([key, val]) => (
                <tr key={key}>
                  <td style={{ borderBottom: '1px solid var(--border)', padding: 6, color: 'var(--text-muted)' }}>{key}</td>
                  <td style={{ borderBottom: '1px solid var(--border)', padding: 6 }}>{typeof val === 'number' ? val.toFixed(2) : val}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={sectionLabelStyle}>Discharge Equation</div>
          <code style={{ fontSize: 13, display: 'block', marginBottom: 16 }}>
            {design.hydraulics.discharge_equation?.gpm?.formula || 'Not available'}
          </code>

          {design.hydraulics.discharge_table && (
            <>
              <div style={sectionLabelStyle}>Discharge curve vs. nearest real flumes</div>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>
                Shown alongside the {(design.hydraulics.nearest_real_sizes_mm || []).join('mm and ')}mm
                real calibrated flumes, so you can see the custom curve sitting between its real neighbors.
              </p>
              <div style={{ position: 'relative', width: '100%', height: 260, marginBottom: 20 }}>
                <canvas
                  ref={chartRef}
                  role="img"
                  aria-label="Line chart showing the custom interpolated discharge curve alongside its two nearest real calibrated flume curves, across the design head range"
                />
              </div>

              <div style={sectionLabelStyle}>Discharge Table</div>
              <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 13, fontFamily: 'var(--font-mono)', marginBottom: 16 }}>
                <thead>
                  <tr>
                    <th style={{ borderBottom: '1px solid var(--border)', padding: 6, textAlign: 'left', color: 'var(--text-muted)' }}>Head (ft)</th>
                    <th style={{ borderBottom: '1px solid var(--border)', padding: 6, textAlign: 'left', color: 'var(--text-muted)' }}>
                      Custom {design.throat_width_mm.toFixed(0)}mm (GPM)
                    </th>
                    {(design.hydraulics.nearest_real_sizes_mm || []).map((sizeMm) => (
                      <th key={sizeMm} style={{ borderBottom: '1px solid var(--border)', padding: 6, textAlign: 'left', color: 'var(--text-muted)' }}>
                        Real {sizeMm}mm (GPM)
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {design.hydraulics.discharge_table.map((row, i) => (
                    <tr key={i}>
                      <td style={{ borderBottom: '1px solid var(--border)', padding: 6 }}>{row.head_ft}</td>
                      <td style={{ borderBottom: '1px solid var(--border)', padding: 6 }}>{row.flow_gpm}</td>
                      {(design.hydraulics.nearest_real_sizes_mm || []).map((sizeMm) => (
                        <td key={sizeMm} style={{ borderBottom: '1px solid var(--border)', padding: 6 }}>
                          {row[`real_${sizeMm}mm_gpm`]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}

          <div style={sectionLabelStyle}>Operating Range</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13 }}>
            Max flow: {design.operating_range.max_flow_gpm.toFixed(2)} GPM
          </div>
        </div>
      )}
    </div>
  )
}

export default CustomRbcDesigner
