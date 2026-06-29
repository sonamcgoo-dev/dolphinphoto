import { useState, useEffect } from 'react'
import { Box, Download, Loader2, Search, HardDrive, Cpu } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '@/api/client'
import { motion } from 'framer-motion'
import clsx from 'clsx'

interface Model {
  id: string
  name: string
  type: string
  path: string
  size: number
  loaded: boolean
}

export default function Models() {
  const [models, setModels] = useState<Model[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [loadingModel, setLoadingModel] = useState<string | null>(null)

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    setLoading(true)
    try {
      const response = await api.get('/models')
      if (response.data?.models) {
        setModels(response.data.models)
      }
    } catch {
      // Use default models
      setModels([
        { id: 'sd-21', name: 'stable-diffusion-2-1', type: 'checkpoint', path: '/models/sd-21', size: 5e9, loaded: false },
        { id: 'sdxl', name: 'stable-diffusion-xl-base-1.0', type: 'checkpoint', path: '/models/sdxl', size: 6.5e9, loaded: false },
        { id: 'sd15', name: 'runwayml-stable-diffusion-v1-5', type: 'checkpoint', path: '/models/sd15', size: 4e9, loaded: false },
        { id: 'lora-1', name: ' cinematic-lora-v1', type: 'lora', path: '/models/lora/cinematic', size: 100e6, loaded: false },
        { id: 'vae-1', name: 'stabilityai-sd-vae', type: 'vae', path: '/models/vae/ft-ema', size: 300e6, loaded: false },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleLoadModel = async (modelId: string) => {
    setLoadingModel(modelId)
    try {
      const response = await api.post('/models/load', {
        model_name: models.find(m => m.id === modelId)?.name || modelId,
        model_type: models.find(m => m.id === modelId)?.type || 'checkpoint',
      })
      if (response.data?.result?.status === 'loaded') {
        setModels(prev => prev.map(m => 
          m.id === modelId ? { ...m, loaded: true } : m
        ))
        toast.success('Model loaded!')
      }
    } catch {
      toast.error('Failed to load model')
    } finally {
      setLoadingModel(null)
    }
  }

  const handleUnloadModel = async (modelId: string) => {
    setLoadingModel(modelId)
    try {
      const response = await api.post('/models/unload', {
        model_name: models.find(m => m.id === modelId)?.name || modelId,
        model_type: models.find(m => m.id === modelId)?.type || 'checkpoint',
      })
      if (response.data?.result?.status === 'unloaded') {
        setModels(prev => prev.map(m => 
          m.id === modelId ? { ...m, loaded: false } : m
        ))
        toast.success('Model unloaded')
      }
    } catch {
      toast.error('Failed to unload model')
    } finally {
      setLoadingModel(null)
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes >= 1e9) return `${(bytes / 1e9).toFixed(1)} GB`
    if (bytes >= 1e6) return `${(bytes / 1e6).toFixed(0)} MB`
    return `${(bytes / 1e3).toFixed(0)} KB`
  }

  const filteredModels = models.filter(m => {
    const matchesSearch = m.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = typeFilter === 'all' || m.type === typeFilter
    return matchesSearch && matchesType
  })

  const typeIcons: Record<string, JSX.Element> = {
    checkpoint: <HardDrive size={16} className="text-accent-cyan" />,
    lora: <Box size={16} className="text-accent-purple" />,
    vae: <Cpu size={16} className="text-accent-magenta" />,
  }

  return (
    <div className="h-full p-4 bg-space-900 overflow-auto">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-heading font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-purple to-accent-cyan flex items-center justify-center">
              <Box className="text-white" size={20} />
            </div>
            AI Models
          </h1>
          <p className="text-gray-400 mt-1">
            Manage and load AI models for generation and processing
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search models..."
              className="input-field pl-10"
            />
          </div>
          <div className="flex gap-2">
            {['all', 'checkpoint', 'lora', 'vae'].map((type) => (
              <button
                key={type}
                onClick={() => setTypeFilter(type)}
                className={clsx(
                  'px-4 py-2 rounded-lg font-medium capitalize transition-all',
                  typeFilter === type
                    ? 'bg-accent-cyan text-space-900'
                    : 'bg-space-800 text-gray-400 hover:text-white border border-space-600'
                )}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Models Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 text-accent-cyan animate-spin" />
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredModels.map((model, idx) => (
              <motion.div
                key={model.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className={clsx(
                  'card p-4 transition-all',
                  model.loaded && 'ring-2 ring-accent-green/50'
                )}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={clsx(
                      'w-10 h-10 rounded-lg flex items-center justify-center',
                      model.type === 'checkpoint' ? 'bg-accent-cyan/20' :
                      model.type === 'lora' ? 'bg-accent-purple/20' : 'bg-accent-magenta/20'
                    )}>
                      {typeIcons[model.type] || <Box size={16} />}
                    </div>
                    <div>
                      <h3 className="font-medium truncate max-w-[180px]">{model.name}</h3>
                      <span className="text-xs text-gray-500 capitalize">{model.type}</span>
                    </div>
                  </div>
                  {model.loaded && (
                    <span className="px-2 py-0.5 rounded-full bg-accent-green/20 text-accent-green text-xs font-medium">
                      Loaded
                    </span>
                  )}
                </div>
                
                <div className="flex items-center justify-between text-sm text-gray-400 mb-4">
                  <span>{formatSize(model.size)}</span>
                  <span className="font-mono text-xs">{model.id}</span>
                </div>
                
                <div className="flex gap-2">
                  {model.loaded ? (
                    <button
                      onClick={() => handleUnloadModel(model.id)}
                      disabled={loadingModel === model.id}
                      className="flex-1 btn-secondary flex items-center justify-center gap-2 py-2"
                    >
                      {loadingModel === model.id ? (
                        <Loader2 size={16} className="animate-spin" />
                      ) : (
                        <>
                          <Box size={16} />
                          Unload
                        </>
                      )}
                    </button>
                  ) : (
                    <button
                      onClick={() => handleLoadModel(model.id)}
                      disabled={loadingModel === model.id}
                      className="flex-1 btn-primary flex items-center justify-center gap-2 py-2"
                    >
                      {loadingModel === model.id ? (
                        <Loader2 size={16} className="animate-spin" />
                      ) : (
                        <>
                          <Download size={16} />
                          Load
                        </>
                      )}
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {filteredModels.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-64 text-gray-400">
            <Box size={48} className="mb-4 opacity-50" />
            <p>No models found</p>
          </div>
        )}
      </div>
    </div>
  )
}
