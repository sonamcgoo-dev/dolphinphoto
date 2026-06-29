import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Studio from './pages/Studio'
import DreamVideo from './pages/DreamVideo'
import Glowup from './pages/Glowup'
import Filters from './pages/Filters'
import Models from './pages/Models'
import MCPHub from './pages/MCPHub'
import Workspace from './pages/Workspace'
import Setup from './pages/Setup'

function App() {
  return (
    <Routes>
      <Route path="/setup" element={<Setup />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/studio" replace />} />
        <Route path="studio" element={<Studio />} />
        <Route path="dream-video" element={<DreamVideo />} />
        <Route path="glowup" element={<Glowup />} />
        <Route path="filters" element={<Filters />} />
        <Route path="models" element={<Models />} />
        <Route path="mcp" element={<MCPHub />} />
        <Route path="workspace" element={<Workspace />} />
      </Route>
    </Routes>
  )
}

export default App
