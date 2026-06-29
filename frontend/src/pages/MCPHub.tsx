import { useState, useEffect } from 'react'
import { Plug, Plus, Play, Loader2, Search, Terminal } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '@/api/client'
import { motion } from 'framer-motion'
import clsx from 'clsx'

interface MCPServer {
  id: string
  name: string
  status: 'connected' | 'disconnected'
  tools: number
  url?: string
}

interface MCPTool {
  name: string
  description: string
  category: string
  tags: string[]
}

export default function MCPHub() {
  const [servers, setServers] = useState<MCPServer[]>([])
  const [tools, setTools] = useState<MCPTool[]>([])
  const [loading, setLoading] = useState(true)
  const [executing, setExecuting] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const toolsRes = await api.get('/mcp/tools')
      
      if (toolsRes.data?.tools) {
        setTools(toolsRes.data.tools)
      }
    } catch {
      setTools([
        { name: 'image.generate', description: 'Generate images from text', category: 'image_generation', tags: ['ai', 'stable-diffusion'] },
        { name: 'image.transform', description: 'Transform images with AI', category: 'image_generation', tags: ['ai', 'transform'] },
        { name: 'image.upscale', description: 'Upscale images', category: 'image_processing', tags: ['ai', 'upscale'] },
        { name: 'image.remove_background', description: 'Remove image backgrounds', category: 'image_processing', tags: ['ai', 'background'] },
        { name: 'image.filter', description: 'Apply filters to images', category: 'filters', tags: ['filter', 'style'] },
        { name: 'video.generate', description: 'Generate slideshow videos', category: 'video', tags: ['video', 'slideshow'] },
        { name: 'video.dream', description: 'Create dream videos', category: 'video', tags: ['video', 'ai', 'dream'] },
        { name: 'model.load', description: 'Load AI models', category: 'model_management', tags: ['model', 'ai'] },
        { name: 'system.info', description: 'Get system information', category: 'system', tags: ['system', 'info'] },
      ])
    }
    
    setServers([
      { id: 'local', name: 'DolphinPhoto Local', status: 'connected', tools: tools.length },
    ])
    
    setLoading(false)
  }

  const handleExecuteTool = async (tool: MCPTool) => {
    setExecuting(true)
    try {
      const response = await api.post('/mcp/tools/execute', {
        name: tool.name,
        arguments: {},
      })
      if (response.data?.success) {
        toast.success(`Tool ${tool.name} executed!`)
      }
    } catch {
      toast.error(`Failed to execute ${tool.name}`)
    } finally {
      setExecuting(false)
    }
  }

  const filteredTools = tools.filter(t => {
    const matchesSearch = t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         t.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = categoryFilter === 'all' || t.category === categoryFilter
    return matchesSearch && matchesCategory
  })

  const categories = [...new Set(tools.map(t => t.category))]

  return (
    <div className="h-full p-4 bg-space-900 overflow-auto">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-heading font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-magenta to-accent-purple flex items-center justify-center">
              <Plug className="text-white" size={20} />
            </div>
            MCP Hub
          </h1>
          <p className="text-gray-400 mt-1">
            Model Context Protocol - Connect AI tools and services
          </p>
        </div>

        {/* Servers */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-medium flex items-center gap-2">
              <Terminal size={18} />
              Connected Servers
            </h2>
            <button className="btn-secondary flex items-center gap-2 text-sm">
              <Plus size={16} />
              Add Server
            </button>
          </div>
          <div className="flex gap-3 overflow-x-auto pb-2">
            {servers.map((server) => (
              <div
                key={server.id}
                className={clsx(
                  'card px-4 py-3 min-w-[200px] flex items-center gap-3',
                  server.status === 'connected' && 'border-accent-green/50'
                )}
              >
                <div className={clsx(
                  'w-3 h-3 rounded-full',
                  server.status === 'connected' ? 'bg-accent-green animate-pulse' : 'bg-gray-500'
                )} />
                <div className="flex-1">
                  <h3 className="font-medium text-sm">{server.name}</h3>
                  <span className="text-xs text-gray-500">{server.tools} tools</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search tools..."
              className="input-field pl-10"
            />
          </div>
          <div className="flex gap-2 overflow-x-auto pb-2">
            <button
              onClick={() => setCategoryFilter('all')}
              className={clsx(
                'px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-all',
                categoryFilter === 'all'
                  ? 'bg-accent-magenta text-white'
                  : 'bg-space-800 text-gray-400 hover:text-white border border-space-600'
              )}
            >
              All
            </button>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                className={clsx(
                  'px-4 py-2 rounded-lg font-medium capitalize whitespace-nowrap transition-all',
                  categoryFilter === cat
                    ? 'bg-accent-magenta text-white'
                    : 'bg-space-800 text-gray-400 hover:text-white border border-space-600'
                )}
              >
                {cat.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Tools Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 text-accent-magenta animate-spin" />
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredTools.map((tool, idx) => (
              <motion.div
                key={tool.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.03 }}
                className="card p-4 hover:border-accent-magenta/50 transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-mono font-medium text-sm mb-1">{tool.name}</h3>
                    <p className="text-sm text-gray-400">{tool.description}</p>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-1 mb-3">
                  {tool.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 rounded bg-space-700 text-xs text-gray-400"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                
                <button
                  onClick={() => handleExecuteTool(tool)}
                  disabled={executing}
                  className="w-full btn-secondary flex items-center justify-center gap-2 py-2"
                >
                  <Play size={16} />
                  Execute
                </button>
              </motion.div>
            ))}
          </div>
        )}

        {filteredTools.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-64 text-gray-400">
            <Plug size={48} className="mb-4 opacity-50" />
            <p>No tools found</p>
          </div>
        )}
      </div>
    </div>
  )
}
