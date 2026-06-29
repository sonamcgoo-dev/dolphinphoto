import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Sparkles, Loader2, Download, RotateCcw, Eye } from 'lucide-react'
import toast from 'react-hot-toast'
import { api, imageToBase64 } from '@/api/client'
import { useAppStore } from '@/store/useAppStore'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'

export default function Glowup() {
  const { currentImage, setCurrentImage, processing, setProcessing } = useAppStore()
  const [resultImage, setResultImage] = useState<string | null>(null)
  const [showComparison, setShowComparison] = useState(false)
  const [intensity, setIntensity] = useState(70)
  const [enhanceFace, setEnhanceFace] = useState(true)
  const [brighten, setBrighten] = useState(true)
  const [smoothSkin, setSmoothSkin] = useState(true)
  const [sharpen, setSharpen] = useState(true)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles[0]) {
      const base64 = await imageToBase64(acceptedFiles[0])
      setCurrentImage(base64)
      setResultImage(null)
      toast.success('Image loaded! Ready for glowup')
    }
  }, [setCurrentImage])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] },
    maxFiles: 1,
  })

  const handleGlowup = async () => {
    if (!currentImage) return
    
    setProcessing(true)
    try {
      const response = await api.post('/dream-video/glowup', {
        image: currentImage,
        intensity: intensity / 100,
        enhance_face: enhanceFace,
        brighten,
        smooth_skin: smoothSkin,
        sharpen,
      })
      
      if (response.data?.image?.path) {
        const img = await fetch(`http://127.0.0.1:7777/${response.data.image.path}`)
        const blob = await img.blob()
        const reader = new FileReader()
        reader.onload = () => {
          setResultImage(reader.result as string)
        }
        reader.readAsDataURL(blob)
        toast.success('Glowup complete!')
      }
    } catch (error) {
      toast.error('Failed to apply glowup')
    } finally {
      setProcessing(false)
    }
  }

  const handleReset = () => {
    setCurrentImage(null)
    setResultImage(null)
  }

  return (
    <div className="h-full p-4 bg-space-900 overflow-auto">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-heading font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-green to-accent-cyan flex items-center justify-center">
              <Sparkles className="text-space-900" size={20} />
            </div>
            AI Glowup
          </h1>
          <p className="text-gray-400 mt-1">
            Transform photos with professional AI enhancement
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Before/After Comparison */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="card overflow-hidden">
              <div className="relative aspect-[4/3] bg-space-800">
                <AnimatePresence mode="wait">
                  {!resultImage ? (
                    <div
                      key="input"
                      {...getRootProps()}
                      className={clsx(
                        'absolute inset-0 flex flex-col items-center justify-center p-8 cursor-pointer transition-all',
                        isDragActive ? 'bg-accent-green/5' : ''
                      )}
                    >
                      <input {...getInputProps()} />
                      <div className="w-16 h-16 rounded-full bg-accent-green/10 flex items-center justify-center mb-4">
                        <Upload className="w-8 h-8 text-accent-green" />
                      </div>
                      <h3 className="text-lg font-medium mb-2">
                        {isDragActive ? 'Drop your photo' : 'Upload Photo'}
                      </h3>
                      <p className="text-sm text-gray-400 text-center">
                        Upload a portrait or photo to apply AI glowup
                      </p>
                    </div>
                  ) : showComparison ? (
                    <motion.div
                      key="comparison"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="absolute inset-0 flex"
                    >
                      <div className="relative flex-1 overflow-hidden">
                        <img
                          src={currentImage!}
                          alt="Before"
                          className="w-full h-full object-contain"
                        />
                        <div className="absolute top-4 left-4 px-3 py-1 rounded-full bg-space-900/80 text-sm">
                          Before
                        </div>
                      </div>
                      <div className="relative flex-1 overflow-hidden">
                        <img
                          src={resultImage}
                          alt="After"
                          className="w-full h-full object-contain"
                        />
                        <div className="absolute top-4 right-4 px-3 py-1 rounded-full bg-accent-green/80 text-sm text-space-900">
                          After
                        </div>
                      </div>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="result"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="absolute inset-0"
                    >
                      <img
                        src={resultImage}
                        alt="After"
                        className="w-full h-full object-contain"
                      />
                      <div className="absolute bottom-4 right-4 px-3 py-1 rounded-full bg-accent-green/80 text-sm text-space-900">
                        ✨ Glowup Applied
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
                
                {processing && (
                  <div className="absolute inset-0 bg-space-900/80 flex items-center justify-center">
                    <div className="text-center">
                      <Loader2 className="w-12 h-12 text-accent-green animate-spin mx-auto mb-4" />
                      <p className="text-accent-green">Applying AI Glowup...</p>
                    </div>
                  </div>
                )}
              </div>
              
              {resultImage && (
                <div className="p-4 flex gap-2">
                  <button
                    onClick={() => setShowComparison(!showComparison)}
                    className="btn-secondary flex items-center gap-2 flex-1"
                  >
                    <Eye size={18} />
                    {showComparison ? 'View Result' : 'Compare'}
                  </button>
                  <button
                    onClick={handleReset}
                    className="btn-secondary flex items-center gap-2"
                  >
                    <RotateCcw size={18} />
                    Reset
                  </button>
                  <a
                    href={resultImage}
                    download={`glowup-${Date.now()}.png`}
                    className="btn-primary flex items-center gap-2"
                  >
                    <Download size={18} />
                    Save
                  </a>
                </div>
              )}
            </div>
          </motion.div>

          {/* Settings */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="space-y-4"
          >
            {/* Intensity */}
            <div className="card p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-4 flex items-center gap-2">
                <Sparkles size={16} className="text-accent-green" />
                Effect Intensity
              </h3>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Overall Strength</span>
                  <span className="text-accent-green font-mono">{intensity}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={intensity}
                  onChange={(e) => setIntensity(Number(e.target.value))}
                  className="w-full accent-accent-green"
                />
              </div>
            </div>

            {/* Enhancement Options */}
            <div className="card p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-4">
                Enhancement Options
              </h3>
              <div className="space-y-3">
                <label className="flex items-center justify-between cursor-pointer">
                  <span>Face Enhancement</span>
                  <input
                    type="checkbox"
                    checked={enhanceFace}
                    onChange={(e) => setEnhanceFace(e.target.checked)}
                    className="w-5 h-5 rounded bg-space-700 border-space-600 text-accent-green focus:ring-accent-green"
                  />
                </label>
                <label className="flex items-center justify-between cursor-pointer">
                  <span>Brightening</span>
                  <input
                    type="checkbox"
                    checked={brighten}
                    onChange={(e) => setBrighten(e.target.checked)}
                    className="w-5 h-5 rounded bg-space-700 border-space-600 text-accent-green focus:ring-accent-green"
                  />
                </label>
                <label className="flex items-center justify-between cursor-pointer">
                  <span>Skin Smoothing</span>
                  <input
                    type="checkbox"
                    checked={smoothSkin}
                    onChange={(e) => setSmoothSkin(e.target.checked)}
                    className="w-5 h-5 rounded bg-space-700 border-space-600 text-accent-green focus:ring-accent-green"
                  />
                </label>
                <label className="flex items-center justify-between cursor-pointer">
                  <span>Sharpening</span>
                  <input
                    type="checkbox"
                    checked={sharpen}
                    onChange={(e) => setSharpen(e.target.checked)}
                    className="w-5 h-5 rounded bg-space-700 border-space-600 text-accent-green focus:ring-accent-green"
                  />
                </label>
              </div>
            </div>

            {/* Apply Button */}
            <button
              onClick={handleGlowup}
              disabled={!currentImage || processing}
              className="w-full py-4 text-lg rounded-xl font-bold bg-gradient-to-r from-accent-green to-accent-cyan text-space-900 hover:opacity-90 transition-opacity flex items-center justify-center gap-3 disabled:opacity-50"
            >
              {processing ? (
                <>
                  <Loader2 className="animate-spin" size={24} />
                  Processing...
                </>
              ) : (
                <>
                  <Sparkles size={24} />
                  Apply Glowup ✨
                </>
              )}
            </button>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
