import { useState, useEffect } from 'react'
import { API_BASE_URL } from './config'

function FlumeDetail({ flumeId }) {
  const [discharge, setDischarge] = useState(null)
  const [flume, setFlume] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    setDischarge(null)
    setFlume(null)
    setError(null)
    fetch(`${API_BASE_URL}/flumes/${flumeId}`)
      .then((res) => res.json())
      .then((data) => setFlume(data))
      .catch(() => {})
    fetch(`${API_BASE_URL}/flumes/${flumeId}/discharge`)
      .then((res) => res.json())
      .then((data) => setDischarge(data))
      .catch((err) => setError('Error loading discharge data: ' + err.message))
  }, [flumeId])

  const hasGeometry = flume && flume.geometry !== null
  const originalDrawings = flume && flume.original_drawings

  const diagramPanelStyle = {
    background: 'var(--bg)',
    borderRadius: 8,
    padding: '0.5rem',
    marginBottom: 12,
    border: '1px solid var(--border)',
  }
  const imgStyle = { maxWidth: '100%', display: 'block' }
  const sectionLabelStyle = {
    fontFamily: 'var(--font-mono)', fontSize: 12, letterSpacing: '0.05em',
    color: 'var(--accent-bright)', marginBottom: 8, textTransform: 'uppercase',
  }
  const linkButtonStyle = {
    display: 'inline-block', background: 'var(--surface-raised)', color: 'var(--accent-bright)',
    border: '1px solid var(--border)', borderRadius: 6, padding: '0.5rem 0.9rem',
    fontSize: 13, textDecoration: 'none', marginRight: 8, marginBottom: 8,
  }

  return (
    <div style={{
      background: 'var(--surface-raised)',
      border: '1px solid var(--border)',
      borderRadius: 10,
      padding: '1.25rem',
      marginTop: 12,
    }}>

      {hasGeometry ? (
        <>
          <div style={sectionLabelStyle}>Plan View</div>
          <div style={diagramPanelStyle}>
            <img src={`${API_BASE_URL}/flumes/${flumeId}/diagram`} alt="Plan view" style={imgStyle} />
          </div>

          <div style={sectionLabelStyle}>Elevation View</div>
          <div style={diagramPanelStyle}>
            <img src={`${API_BASE_URL}/flumes/${flumeId}/diagram/elevation`} alt="Elevation view" style={imgStyle} />
          </div>

          <div style={sectionLabelStyle}>End View</div>
          <div style={diagramPanelStyle}>
            <img src={`${API_BASE_URL}/flumes/${flumeId}/diagram/end`} alt="End view" style={imgStyle} />
          </div>
        </>
      ) : (
        <div style={{ ...diagramPanelStyle, color: 'var(--text-muted)' }}>
          <p style={{ margin: '0 0 8px', fontSize: 13 }}>
            Generated diagrams aren't available yet for this flume - view the original manufacturer drawing instead:
          </p>
        </div>
      )}

      {originalDrawings && (
        <div style={{ marginBottom: 16 }}>
          {originalDrawings.dimension_drawing_pdf && (
            <a
              href={`${API_BASE_URL}/drawings/${originalDrawings.dimension_drawing_pdf}`}
              target="_blank" rel="noreferrer"
              style={linkButtonStyle}
            >
              📐 Original Dimension Drawing (PDF)
            </a>
          )}
          {originalDrawings.discharge_table_pdf && (
            <a
              href={`${API_BASE_URL}/drawings/${originalDrawings.discharge_table_pdf}`}
              target="_blank" rel="noreferrer"
              style={linkButtonStyle}
            >
              📄 Original Discharge Table (PDF)
            </a>
          )}
        </div>
      )}

      {flume && flume.characteristics && (
        <>
          <div style={sectionLabelStyle}>Characteristics</div>
          <div style={{ fontSize: 13, color: 'var(--text)', lineHeight: 1.6, marginBottom: 16 }}>
            <div><strong style={{ color: 'var(--accent-bright)' }}>Best for:</strong> {flume.characteristics.best_for}</div>
            <div style={{ marginTop: 6 }}><strong style={{ color: 'var(--accent-bright)' }}>Sediment handling:</strong> {flume.characteristics.sediment_handling}</div>
            <div style={{ marginTop: 6 }}><strong style={{ color: 'var(--accent-bright)' }}>Recommended channel material:</strong> {flume.characteristics.recommended_channel_material}</div>
            <div style={{ marginTop: 6 }}><strong style={{ color: 'var(--accent-bright)' }}>Installation notes:</strong> {flume.characteristics.installation_notes}</div>
          </div>
        </>
      )}

      <div style={sectionLabelStyle}>Discharge Equations</div>
      {error && <p style={{ color: '#f87171' }}>{error}</p>}
      {discharge && discharge.error && <p style={{ color: '#f87171' }}>{discharge.error}</p>}
      {discharge && !discharge.error && (
        <>
          <ul style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--text)', paddingLeft: 20 }}>
            {Object.entries(discharge.equations).map(([unit, formula]) => (
              <li key={unit} style={{ marginBottom: 4 }}>{formula}</li>
            ))}
          </ul>

          <div style={{ ...sectionLabelStyle, marginTop: 16 }}>Discharge Table</div>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            Valid head range: {discharge.valid_head_range_ft.min} – {discharge.valid_head_range_ft.max} ft
          </p>
          <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 13 }}>
            <thead>
              <tr>
                <th style={{ borderBottom: '1px solid var(--border)', padding: 6, textAlign: 'left', color: 'var(--text-muted)' }}>Head (ft)</th>
                <th style={{ borderBottom: '1px solid var(--border)', padding: 6, textAlign: 'left', color: 'var(--text-muted)' }}>Flow (GPM)</th>
              </tr>
            </thead>
            <tbody>
              {discharge.table.map((row, i) => (
                <tr key={i}>
                  <td style={{ borderBottom: '1px solid var(--border)', padding: 6 }}>{row.head_ft}</td>
                  <td style={{ borderBottom: '1px solid var(--border)', padding: 6 }}>
                    {row.flow_gpm !== null ? row.flow_gpm : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  )
}

export default FlumeDetail
