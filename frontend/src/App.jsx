import { Routes, Route } from 'react-router-dom'
import './App.css'
import NavBar from './NavBar'
import HomePage from './HomePage'
import RecommenderPage from './RecommenderPage'
import CustomRbcDesigner from './CustomRbcDesigner'



function App() {
  return (
    <div>
      <NavBar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/recommend" element={<RecommenderPage />} />
        <Route path="/design-rbc" element={<CustomRbcDesigner />} />
      </Routes>
    </div>
  )
}

export default App