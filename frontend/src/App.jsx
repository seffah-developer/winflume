import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState('Loading...')

  useEffect(() => {
    fetch('http://127.0.0.1:8000/')
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((err) => setMessage('Error connecting to backend: ' + err.message))
  }, [])

  return (
    <div>
      <h1>WinFlume Pro Max</h1>
      <p>Backend says: {message}</p>
    </div>
  )
}

export default App