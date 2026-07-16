import { useState, useEffect } from 'react'

function FlumeDetail({ flumeId }) {
  const [discharge, setDischarge] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    setDischarge(null)
    setError(null)
    fetch(`http://127.0.0.1:8000/flumes/${flumeId}/discharge`)
      .then((res) => res.json())
      .then((data) => setDischarge(data))
      .catch((err) => setError('Error loading discharge data: ' + err.message))
  }, [flumeId])

  const imgStyle = { maxWidth: '100%', border: '1px solid #ddd', borderRadius: 4, marginBottom: 8 }

  return (
    <div style={{ border: '1px solid #ccc', borderRadius: 8, padding: '1rem', marginTop: 8 }}>

      <h4>Plan View</h4>
      <img src={`http://127.0.0.1:8000/flumes/${flumeId}/diagram`} alt="Plan view" style={imgStyle} />

      <h4>Elevation View</h4>
      <img src={`http://127.0.0.1:8000/flumes/${flumeId}/diagram/elevation`} alt="Elevation view" style={imgStyle} />

      <h4>End View</h4>
      <img src={`http://127.0.0.1:8000/flumes/${flumeId}/diagram/end`} alt="End view" style={imgStyle} />

      <h4>Discharge Equations</h4>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {discharge && discharge.error && <p style={{ color: 'red' }}>{discharge.error}</p>}
      {discharge && !discharge.error && (
        <>
          <ul>
            {Object.entries(discharge.equations).map(([unit, formula]) => (
              <li key={unit}><code>{formula}</code></li>
            ))}
          </ul>

          <h4>Discharge Table</h4>
          <p style={{ fontSize: 12, color: '#555' }}>
            Valid head range: {discharge.valid_head_range_ft.min} - {discharge.valid_head_range_ft.max} ft
          </p>
          <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 13 }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid #ddd', padding: 4, textAlign: 'left' }}>Head (ft)</th>
                <th style={{ border: '1px solid #ddd', padding: 4, textAlign: 'left' }}>Flow (GPM)</th>
              </tr>
            </thead>
            <tbody>
              {discharge.table.map((row, i) => (
                <tr key={i}>
                  <td style={{ border: '1px solid #ddd', padding: 4 }}>{row.head_ft}</td>
                  <td style={{ border: '1px solid #ddd', padding: 4 }}>
                    {row.flow_gpm !== null ? row.flow_gpm : '-'}
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