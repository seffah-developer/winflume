import { Link, useLocation } from 'react-router-dom'

function NavBar() {
  const location = useLocation()

  const linkStyle = (path) => ({
    textDecoration: 'none',
    color: location.pathname === path ? 'var(--accent-bright)' : 'var(--text-muted)',
    fontWeight: location.pathname === path ? 600 : 500,
    padding: '0.5rem 1rem',
    fontSize: 14,
  })

  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '1rem 2rem',
      borderBottom: '1px solid var(--border)',
      background: 'var(--surface)',
    }}>
      <Link to="/" style={{ textDecoration: 'none', color: 'var(--text)', fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.15rem' }}>
        WinFlume <span style={{ color: 'var(--accent)' }}>Pro Max</span>
      </Link>
      <div>
        <Link to="/" style={linkStyle('/')}>Home</Link>
        <Link to="/recommend" style={linkStyle('/recommend')}>Recommend</Link>
        <Link to="/design-rbc" style={linkStyle('/design-rbc')}>Design Custom RBC</Link>
      </div>
    </nav>
  )
}

export default NavBar