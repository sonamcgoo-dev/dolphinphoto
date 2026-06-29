import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  Upload, Wand2, Crop, RotateCw, Sun, Contrast,
  Palette, Download, Undo, Redo,
  Maximize2, Trash2, Image as ImageIcon, Sparkles,
  Loader2, Check
} from 'lucide-react'
import toast from 'react-hot-toast'
import { api, imageToBase64 } from '@/api/client'
import { useAppStore } from '@/store/useAppStore'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'

export default function Studio() {
  const { currentImage, setCurrentImage, processing, setProcessing } = useAppStore()
  const [history, setHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [brightness, setBrightness] = useState(100)
  const [contrast, setContrast] = useState(100)
  const [saturation, setSaturation] = useState(100)
  const [appliedAdjustments, setAppliedAdjustments] = useState(false)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles[0]) {
      const base64 = await imageToBase64(acceptedFiles[0])
      setCurrentImage(base64)
      setHistory([base64])
      setHistoryIndex(0)
      toast.success('Image loaded successfully!')
    }
  }, [setCurrentImage])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp', '.gif'] },
    maxFiles: 1,
  })

  const handleAdjustments = async () => {
    if (!currentImage) return
    
    setProcessing(true)
    try {
      const response = await api.post('/images/color-adjust', {
        image: currentImage,
        brightness: brightness / 100,
        contrast: contrast / 100,
        saturation: saturation / 100,
      })
      
      if (response.data?.image?.path) {
        const result = await api.get(`/images/${response.data.image.id}`)
        if (result.data?.path) {
          const img = await fetch(`http://127.0.0.1:7777/${result.data.path}`)
          const blob = await img.blob()
          const reader = new FileReader()
          reader.onload = () => {
            const base64 = reader.result as string
            setCurrentImage(base64)
            setHistory(prev => [...prev.slice(0, historyIndex + 1), base64])
            setHistoryIndex(prev => prev + 1)
            setAppliedAdjustments(true)
          }
          reader.readAsDataURL(blob)
        }
      }
      toast.success('Adjustments applied!')
    } catch (error) {
      toast.error('Failed to apply adjustments')
    } finally {
      setProcessing(false)
    }
  }

  const handleGenerate = async () => {
    if (!currentImage) return
    
    setProcessing(true)
    try {
      const response = await api.post('/images/transform', {
        image: currentImage,
        prompt: 'enhance quality, professional photography, 8k',
        strength: 0.5,
      })
      
      if (response.data?.image?.path) {
        const result = await api.get(`/images/${response.data.image.id}`)
        if (result.data?.path) {
          const img = await fetch(`http://127.0.0.1:7777/${result.data.path}`)
          const blob = await img.blob()
          const reader = new FileReader()
          reader.onload = () => {
            const base64 = reader.result as string
            setCurrentImage(base64)
            setHistory(prev => [...prev.slice(0, historyIndex + 1), base64])
            setHistoryIndex(prev => prev + 1)
          }
          reader.readAsDataURL(blob)
        }
      }
      toast.success('AI enhancement applied!')
    } catch (error) {
      toast.error('Failed to generate')
    } finally {
      setProcessing(false)
    }
  }

  const handleDownload = async () => {
    if (!currentImage) return
    
    const link = document.createElement('a')
    link.href = currentImage
    link.download = `dolphinphoto-${Date.now()}.png`
    link.click()
    toast.success('Image downloaded!')
  }

  const handleClear = () => {
    setCurrentImage(null)
    setHistory([])
    setHistoryIndex(-1)
    setBrightness(100)
    setContrast(100)
    setSaturation(100)
  }

  const undo = () => {
    if (historyIndex > 0) {
      setHistoryIndex(prev => prev - 1)
      setCurrentImage(history[historyIndex - 1])
    }
  }

  const redo = () => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(prev => prev + 1)
      setCurrentImage(history[historyIndex + 1])
    }
  }

  return (
    <div className="h-full flex flex-col lg:flex-row gap-4 p-4 bg-space-900">
      {/* Canvas Area */}
      <div className="flex-1 flex flex-col min-h-[300px] lg:min-h-0">
        {/* Toolbar */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <button
              onClick={undo}
              disabled={historyIndex <= 0}
              className="p-2 rounded-lg bg-space-800 border border-space-600 hover:border-accent-cyan disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Undo size={18} />
            </button>
            <button
              onClick={redo}
              disabled={historyIndex >= history.length - 1}
              className="p-2 rounded-lg bg-space-800 border border-space-600 hover:border-accent-cyan disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Redo size={18} />
            </button>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleDownload}
              disabled={!currentImage}
              className="btn-primary flex items-center gap-2 disabled:opacity-50"
            >
              <Download size={18} />
              <span className="hidden sm:inline">Download</span>
            </button>
            <button
              onClick={handleClear}
              disabled={!currentImage}
              className="p-2 rounded-lg bg-space-800 border border-space-600 hover:border-red-500 text-red-400 disabled:opacity-50 transition-colors"
            >
              <Trash2 size={18} />
            </button>
          </div>
        </div>

        {/* Canvas */}
        <div
          {...getRootProps()}
          className={clsx(
            'flex-1 relative rounded-xl border-2 border-dashed overflow-hidden',
            isDragActive ? 'border-accent-cyan bg-accent-cyan/5' : 'border-space-600',
            currentImage ? 'border-solid' : ''
          )}
        >
          <input {...getInputProps()} />
          
          {currentImage ? (
            <div className="absolute inset-0 flex items-center justify-center p-4">
              <img
                src={currentImage}
                alt="Current"
                className="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
                style={{
                  filter: `brightness(${brightness}%) contrast(${contrast}%) saturate(${saturation}%)`,
                }}
              />
              {processing && (
                <div className="absolute inset-0 bg-space-900/80 flex items-center justify-center">
                  <Loader2 className="w-12 h-12 text-accent-cyan animate-spin" />
                </div>
              )}
            </div>
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center">
              <div className="w-20 h-20 rounded-full bg-accent-cyan/10 flex items-center justify-center mb-4">
                <Upload className="w-10 h-10 text-accent-cyan" />
              </div>
              <h3 className="text-xl font-heading font-bold mb-2">
                {isDragActive ? 'Drop your image here' : 'Upload an Image'}
              </h3>
              <p className="text-gray-400 max-w-md">
                Drag and drop an image here, or click to browse. Supports PNG, JPG, WebP, and more.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Tool Panel */}
      <AnimatePresence mode="wait">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="w-full lg:w-80 flex flex-col gap-4"
        >
          {/* Quick Actions */}
          <div className="card p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
              <Sparkles size={16} className="text-accent-cyan" />
              AI Tools
            </h3>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={handleGenerate}
                disabled={!currentImage || processing}
                className="btn-primary flex items-center justify-center gap-2 py-3"
              >
                <Wand2 size={18} />
                <span>AI Enhance</span>
              </button>
              <button
                disabled={!currentImage || processing}
                className="btn-secondary flex items-center justify-center gap-2 py-3"
              >
                <ImageIcon size={18} />
                <span>Remove BG</span>
              </button>
            </div>
          </div>

          {/* Adjustments */}
          <div className="card p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
              <Sun size={16} className="text-accent-cyan" />
              Adjustments
            </h3>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Brightness</span>
                  <span className="text-accent-cyan font-mono">{brightness}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="200"
                  value={brightness}
                  onChange={(e) => setBrightness(Number(e.target.value))}
                  className="w-full accent-accent-cyan"
                />
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Contrast</span>
                  <span className="text-accent-cyan font-mono">{contrast}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="200"
                  value={contrast}
                  onChange={(e) => setContrast(Number(e.target.value))}
                  className="w-full accent-accent-cyan"
                />
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Saturation</span>
                  <span className="text-accent-cyan font-mono">{saturation}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="200"
                  value={saturation}
                  onChange={(e) => setSaturation(Number(e.target.value))}
                  className="w-full accent-accent-cyan"
                />
              </div>
              
              <button
                onClick={handleAdjustments}
                disabled={!currentImage || processing || !appliedAdjustments}
                className={clsx(
                  'w-full py-2 rounded-lg font-medium transition-all flex items-center justify-center gap-2',
                  appliedAdjustments
                    ? 'bg-accent-green text-space-900'
                    : 'bg-accent-cyan text-space-900 hover:bg-accent-cyan/80'
                )}
              >
                {appliedAdjustments ? (
                  <>
                    <Check size={18} />
                    Applied
                  </>
                ) : (
                  'Apply Adjustments'
                )}
              </button>
            </div>
          </div>

          {/* Basic Tools */}
          <div className="card p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
              <Palette size={16} className="text-accent-cyan" />
              Basic Tools
            </h3>
            <div className="grid grid-cols-4 gap-2">
              <button className="p-3 rounded-lg bg-space-700 hover:bg-space-600 border border-space-600 hover:border-accent-cyan transition-colors flex flex-col items-center gap-1">
                <Crop size={18} />
                <span className="text-xs">Crop</span>
              </button>
              <button className="p-3 rounded-lg bg-space-700 hover:bg-space-600 border border-space-600 hover:border-accent-cyan transition-colors flex flex-col items-center gap-1">
                <RotateCw size={18} />
                <span className="text-xs">Rotate</span>
              </button>
              <button className="p-3 rounded-lg bg-space-700 hover:bg-space-600 border border-space-600 hover:border-accent-cyan transition-colors flex flex-col items-center gap-1">
                <Contrast size={18} />
                <span className="text-xs">Levels</span>
              </button>
              <button className="p-3 rounded-lg bg-space-700 hover:bg-space-600 border border-space-600 hover:border-accent-cyan transition-colors flex flex-col items-center gap-1">
                <Maximize2 size={18} />
                <span className="text-xs">Resize</span>
              </button>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
