import { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Search, Download, Heart, Palette, Sparkles, Zap, Ghost, Camera } from 'lucide-react'
import toast from 'react-hot-toast'
import { api, imageToBase64 } from '@/api/client'
import { useAppStore } from '@/store/useAppStore'
import { motion } from 'framer-motion'
import clsx from 'clsx'

type FilterCategory = 'social' | 'artistic' | 'color' | 'enhance' | 'glitch' | 'vintage'

interface Filter {
  id: string
  name: string
  category: string
  description: string
}

const categories: { id: FilterCategory; label: string; icon: typeof Heart }[] = [
  { id: 'social', label: 'Social Filters', icon: Heart },
  { id: 'artistic', label: 'Artistic', icon: Palette },
  { id: 'color', label: 'Color Grading', icon: Sparkles },
  { id: 'enhance', label: 'Enhance', icon: Zap },
  { id: 'glitch', label: 'Glitch Effects', icon: Ghost },
  { id: 'vintage', label: 'Vintage', icon: Camera },
]

export default function Filters() {
  const { currentImage, setCurrentImage } = useAppStore()
  const [filters, setFilters] = useState<Filter[]>([])
  const [activeCategory, setActiveCategory] = useState<FilterCategory>('social')
  const [selectedFilter, setSelectedFilter] = useState<string | null>(null)
  const [previews, setPreviews] = useState<Record<string, string>>({})
  const [processing, setProcessing] = useState(false)
  const [resultImage, setResultImage] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const response = await api.get('/filters')
        if (response.data?.categories) {
          const allFilters: Filter[] = []
          Object.entries(response.data.categories).forEach(([cat, items]: [string, any]) => {
            items.forEach((item: any) => {
              allFilters.push({ ...item, category: cat })
            })
          })
          setFilters(allFilters)
        }
      } catch {
        // Use built-in filters
        setFilters([
          { id: 'blush', name: '😊 Rosy Cheeks', category: 'social', description: 'Add rosy cheeks' },
          { id: 'smooth_skin', name: '✨ Smooth Skin', category: 'social', description: 'Perfect skin complexion' },
          { id: 'halo', name: '😇 Angel Halo', category: 'social', description: 'Add an angel halo' },
          { id: 'glasses_nerd', name: '🤓 Nerd Glasses', category: 'social', description: 'Add nerdy glasses' },
          { id: 'crown', name: '👑 Royal Crown', category: 'social', description: 'Royal crown filter' },
          { id: 'neon_glow', name: '🌈 Neon Glow', category: 'artistic', description: 'Cyberpunk neon style' },
          { id: 'vintage_film', name: '🎞️ Vintage Film', category: 'artistic', description: 'Classic film look' },
          { id: 'cinematic', name: '🎬 Cinematic', category: 'artistic', description: 'Movie color grade' },
          { id: 'teal_orange', name: '🟠💧 Teal & Orange', category: 'color', description: 'Cinematic color grade' },
          { id: 'golden_hour', name: '🌅 Golden Hour', category: 'color', description: 'Warm golden tones' },
          { id: 'hdr', name: '📸 HDR Effect', category: 'enhance', description: 'High dynamic range' },
          { id: 'vivid', name: '🌟 Vivid', category: 'enhance', description: 'Enhanced vibrancy' },
          { id: 'glitch', name: '💠 Glitch', category: 'glitch', description: 'Digital glitch effect' },
          { id: 'scanlines', name: '📺 Scanlines', category: 'glitch', description: 'Retro TV scanlines' },
          { id: 'polaroid', name: '📸 Polaroid', category: 'vintage', description: 'Instant photo style' },
          { id: 'kodachrome', name: '🎞️ Kodachrome', category: 'vintage', description: 'Classic Kodachrome colors' },
        ])
      }
    }
    fetchFilters()
  }, [])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles[0]) {
      const base64 = await imageToBase64(acceptedFiles[0])
      setCurrentImage(base64)
      setResultImage(null)
      setPreviews({})
      setSelectedFilter(null)
      toast.success('Image loaded! Select a filter')
    }
  }, [setCurrentImage])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] },
    maxFiles: 1,
  })

  const filteredFilters = filters.filter(f => {
    const matchesCategory = f.category === activeCategory
    const matchesSearch = f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         f.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && (searchQuery ? matchesSearch : true)
  })

  const handleApplyFilter = async (filterId: string) => {
    if (!currentImage) return
    
    setSelectedFilter(filterId)
    setProcessing(true)
    try {
      const response = await api.post('/filters/apply', {
        image: currentImage,
        filter_id: filterId,
        intensity: 1.0,
      })
      
      if (response.data?.result?.path) {
        const img = await fetch(`http://127.0.0.1:7777/${response.data.result.path}`)
        const blob = await img.blob()
        const reader = new FileReader()
        reader.onload = () => {
          setResultImage(reader.result as string)
        }
        reader.readAsDataURL(blob)
        toast.success(`Applied ${filterId}!`)
      }
    } catch {
      toast.error('Failed to apply filter')
    } finally {
      setProcessing(false)
    }
  }

  const categoryFilters = filteredFilters.filter(f => f.category === activeCategory)

  return (
    <div className="h-full flex flex-col lg:flex-row gap-4 p-4 bg-space-900 overflow-hidden">
      {/* Filter Grid */}
      <div className="flex-1 flex flex-col min-h-[300px] lg:min-h-0 overflow-hidden">
        {/* Categories */}
        <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={clsx(
                'px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-all flex items-center gap-2',
                activeCategory === cat.id
                  ? 'bg-accent-cyan text-space-900'
                  : 'bg-space-800 text-gray-400 hover:text-white border border-space-600'
              )}
            >
              <cat.icon size={16} />
              {cat.label}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search filters..."
            className="input-field pl-10"
          />
        </div>

        {/* Filter Grid */}
        <div className="flex-1 overflow-y-auto">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-3 xl:grid-cols-4 gap-3">
            {categoryFilters.map((filter, idx) => (
              <motion.button
                key={filter.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.03 }}
                onClick={() => handleApplyFilter(filter.id)}
                disabled={!currentImage || processing}
                className={clsx(
                  'p-3 rounded-xl border transition-all text-left',
                  selectedFilter === filter.id
                    ? 'bg-accent-cyan/20 border-accent-cyan ring-2 ring-accent-cyan'
                    : 'bg-space-800 border-space-600 hover:border-accent-cyan/50 hover:bg-space-700',
                  (!currentImage || processing) && 'opacity-50 cursor-not-allowed'
                )}
              >
                <div className="aspect-video rounded-lg bg-space-700 mb-2 flex items-center justify-center overflow-hidden">
                  {previews[filter.id] ? (
                    <img src={previews[filter.id]} alt={filter.name} className="w-full h-full object-cover" />
                  ) : (
                    <FilterIcon filterId={filter.id} />
                  )}
                </div>
                <h4 className="font-medium text-sm truncate">{filter.name}</h4>
                <p className="text-xs text-gray-500 truncate">{filter.description}</p>
              </motion.button>
            ))}
          </div>
          
          {categoryFilters.length === 0 && (
            <div className="flex flex-col items-center justify-center h-64 text-gray-400">
              <Palette size={48} className="mb-4 opacity-50" />
              <p>No filters found</p>
            </div>
          )}
        </div>
      </div>

      {/* Preview Panel */}
      <div className="w-full lg:w-96 flex flex-col gap-4">
        {/* Image Preview */}
        <div
          {...getRootProps()}
          className={clsx(
            'aspect-video rounded-xl border-2 border-dashed overflow-hidden transition-all cursor-pointer',
            isDragActive ? 'border-accent-cyan bg-accent-cyan/5' : 'border-space-600'
          )}
        >
          <input {...getInputProps()} />
          
          {currentImage ? (
            <div className="relative w-full h-full">
              <img
                src={resultImage || currentImage}
                alt="Preview"
                className="w-full h-full object-contain bg-space-800"
              />
              {resultImage && (
                <div className="absolute top-2 right-2 px-2 py-1 rounded bg-accent-cyan/80 text-xs text-space-900 font-medium">
                  ✨ Filter Applied
                </div>
              )}
            </div>
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center p-4">
              <Upload className="w-8 h-8 text-gray-400 mb-2" />
              <p className="text-sm text-gray-400 text-center">
                Upload image to apply filters
              </p>
            </div>
          )}
        </div>

        {/* Selected Filter Info */}
        {selectedFilter && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-4"
          >
            <h3 className="font-medium mb-2">Selected: {selectedFilter}</h3>
            <p className="text-sm text-gray-400">
              {filters.find(f => f.id === selectedFilter)?.description}
            </p>
          </motion.div>
        )}

        {/* Actions */}
        {resultImage && (
          <a
            href={resultImage}
            download={`filtered-${Date.now()}.png`}
            className="btn-primary flex items-center justify-center gap-2 py-3"
          >
            <Download size={18} />
            Download Image
          </a>
        )}
      </div>
    </div>
  )
}

function FilterIcon({ filterId }: { filterId: string }) {
  const icons: Record<string, JSX.Element> = {
    blush: <span className="text-2xl">😊</span>,
    smooth_skin: <span className="text-2xl">✨</span>,
    halo: <span className="text-2xl">😇</span>,
    glasses_nerd: <span className="text-2xl">🤓</span>,
    crown: <span className="text-2xl">👑</span>,
    neon_glow: <span className="text-2xl">🌈</span>,
    vintage_film: <span className="text-2xl">🎞️</span>,
    cinematic: <span className="text-2xl">🎬</span>,
    glitch: <span className="text-2xl">💠</span>,
    scanlines: <span className="text-2xl">📺</span>,
    polaroid: <span className="text-2xl">📸</span>,
  }
  
  return icons[filterId] || <Sparkles className="w-8 h-8 text-gray-500" />
}
