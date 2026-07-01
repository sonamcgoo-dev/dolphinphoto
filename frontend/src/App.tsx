import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import axios from 'axios'
import Layout from './components/Layout'
import AppLoadingScreen from './components/AppLoadingScreen'
import Studio from './pages/Studio'
import DreamVideo from './pages/DreamVideo'
import Glowup from './pages/Glowup'
import Filters from './pages/Filters'
import Models from './pages/Models'
import MCPHub from './pages/MCPHub'
import Workspace from './pages/Workspace'
import Setup from './pages/Setup'
import { api } from './api/client'

function App() {
  const [bootLoading, setBootLoading] = useState(true)
  const [setupComplete, setSetupComplete] = useState(false)

  useEffect(() => {
    let mounted = true

    const loadSetupStatus = async () => {
      try {
        const response = await api.get('/setup/status')
        if (!mounted) return
        setSetupComplete(Boolean(response.data?.setup_complete))
      } catch (error) {
        if (!mounted) return
        if (!axios.isAxiosError(error)) {
          console.error(error)
        }
      } finally {
        if (mounted) {
          setBootLoading(false)
        }
      }
    }

    loadSetupStatus()
    return () => {
      mounted = false
    }
  }, [])

  if (bootLoading) {
    return <AppLoadingScreen />
  }

  return (
    <Routes>
      <Route path="/setup" element={setupComplete ? <Navigate to="/studio" replace /> : <Setup />} />
      <Route path="/" element={setupComplete ? <Layout /> : <Navigate to="/setup" replace />}>
        <Route index element={<Navigate to={setupComplete ? '/studio' : '/setup'} replace />} />
        <Route path="studio" element={<Studio />} />
        <Route path="dream-video" element={<DreamVideo />} />
        <Route path="glowup" element={<Glowup />} />
        <Route path="filters" element={<Filters />} />
        <Route path="models" element={<Models />} />
        <Route path="mcp" element={<MCPHub />} />
        <Route path="workspace" element={<Workspace />} />
      </Route>
      <Route path="*" element={<Navigate to={setupComplete ? '/studio' : '/setup'} replace />} />
    </Routes>
  )
}

export default App
