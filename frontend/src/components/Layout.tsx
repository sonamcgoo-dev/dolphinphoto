import { Outlet, NavLink } from 'react-router-dom'
import { useEffect, useState } from 'react'
import {
  Sparkles, Video, Wand2, Layers, Box, Plug, Folder,
  ChevronLeft, ChevronRight, Wifi, WifiOff, Menu, X
} from 'lucide-react'
import clsx from 'clsx'
import { api } from '@/api/client'
import { useAppStore } from '@/store/useAppStore'
import BrandLogo from '@/components/BrandLogo'

const navItems = [
  { path: '/studio', icon: Sparkles, label: 'Studio' },
  { path: '/dream-video', icon: Video, label: 'Dream Video' },
  { path: '/glowup', icon: Wand2, label: 'Glowup' },
  { path: '/filters', icon: Layers, label: 'Filters' },
  { path: '/models', icon: Box, label: 'Models' },
  { path: '/mcp', icon: Plug, label: 'MCP Hub' },
  { path: '/workspace', icon: Folder, label: 'Workspace' },
]

export default function Layout() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const { device, connected, setConnected, setDevice } = useAppStore()

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await api.get('/health')
        setConnected(true)
        if (res.data?.device) {
          setDevice(res.data.device)
        }
      } catch {
        setConnected(false)
      }
    }
    checkHealth()
    const interval = setInterval(checkHealth, 10000)
    return () => clearInterval(interval)
  }, [setConnected, setDevice])

  return (
    <div className="h-screen flex overflow-hidden bg-space-900">
      {/* Sidebar */}
      <aside
        className={clsx(
          'hidden lg:flex flex-col bg-space-800 border-r border-space-600 transition-all duration-300',
          collapsed ? 'w-16' : 'w-56'
        )}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-space-600">
          <div className="flex items-center gap-2 min-w-0">
            <BrandLogo className="h-8" showWordmark={!collapsed} />
          </div>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg hover:bg-space-700 text-gray-400 hover:text-white transition-colors"
          >
            {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200',
                  isActive
                    ? 'bg-accent-cyan/10 text-accent-cyan border-l-2 border-accent-cyan'
                    : 'text-gray-400 hover:text-white hover:bg-space-700'
                )
              }
            >
              <item.icon size={20} />
              {!collapsed && <span className="font-medium">{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Status */}
        <div className="p-4 border-t border-space-600">
          <div className={clsx(
            'flex items-center gap-2 text-sm',
            connected ? 'text-accent-green' : 'text-red-400'
          )}>
            {connected ? <Wifi size={16} /> : <WifiOff size={16} />}
            {!collapsed && (
              <span>{connected ? 'Connected' : 'Disconnected'}</span>
            )}
          </div>
          {device && !collapsed && (
            <div className="mt-2 text-xs text-gray-500 font-mono">
              {device.device?.toUpperCase() || 'CPU'}
            </div>
          )}
        </div>
      </aside>

      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-14 bg-space-800 border-b border-space-600 flex items-center justify-between px-4 z-50">
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-2 rounded-lg hover:bg-space-700"
        >
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <div className="flex items-center gap-2">
          <BrandLogo className="h-8" />
        </div>
        <div className={clsx(
          'flex items-center gap-1 text-xs px-2 py-1 rounded-full',
          connected ? 'bg-accent-green/20 text-accent-green' : 'bg-red-400/20 text-red-400'
        )}>
          {connected ? <Wifi size={14} /> : <WifiOff size={14} />}
        </div>
      </div>

      {/* Mobile Navigation */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 top-14 bg-space-900/95 backdrop-blur-xl z-40 p-4">
          <nav className="space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-3 px-4 py-3 rounded-lg transition-all',
                    isActive
                      ? 'bg-accent-cyan/10 text-accent-cyan'
                      : 'text-gray-400 hover:text-white hover:bg-space-800'
                  )
                }
              >
                <item.icon size={20} />
                <span className="font-medium">{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 overflow-hidden pt-14 lg:pt-0">
        <div className="h-full">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
