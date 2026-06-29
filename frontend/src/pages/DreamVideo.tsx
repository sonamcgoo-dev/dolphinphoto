import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Play, Download, Loader2, Wand2, Video } from 'lucide-react'
import toast from 'react-hot-toast'
import { api, imageToBase64 } from '@/api/client'
import { useAppStore } from '@/store/useAppStore'
import { motion } from 'framer-motion'
import clsx from 'clsx'

export default function DreamVideo() {
  const { currentImage, setCurrentImage, processing, setProcessing } = useAppStore()
  const [duration, setDuration] = useState(5)
  const [fps, setFps] = useState(24)
  const [motionStrength, setMotionStrength] = useState(50)
  const [prompt, setPrompt] = useState('')
  const [generatedVideo, setGeneratedVideo] = useState<string | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles[0]) {
      const base64 = await imageToBase64(acceptedFiles[0])
      setCurrentImage(base64)
      setGeneratedVideo(null)
      toast.success('Image loaded! Ready to create dream video')
    }
  }, [setCurrentImage])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] },
    maxFiles: 1,
  })

  const handleGenerate = async () => {
    if (!currentImage) return
    
    setProcessing(true)
    try {
      const response = await api.post('/dream-video/generate', {
        image: currentImage,
        prompt,
        duration,
        fps,
        motion_strength: motionStrength / 100,
      })
      
      if (response.data?.video?.path) {
        setGeneratedVideo(`http://127.0.0.1:7777/${response.data.video.path}`)
        toast.success('Dream video created!')
      }
    } catch (error) {
      toast.error('Failed to generate dream video')
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="h-full p-4 bg-space-900 overflow-auto">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-heading font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-magenta to-accent-purple flex items-center justify-center">
              <Video className="text-white" size={20} />
            </div>
            Dream Video Generator
          </h1>
          <p className="text-gray-400 mt-1">
            Transform your images into mesmerizing AI-powered videos
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Image Input */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div
              {...getRootProps()}
              className={clsx(
                'aspect-video rounded-xl border-2 border-dashed overflow-hidden transition-all cursor-pointer',
                isDragActive ? 'border-accent-magenta bg-accent-magenta/5' : 'border-space-600 hover:border-accent-magenta/50'
              )}
            >
              <input {...getInputProps()} />
              
              {currentImage ? (
                <div className="relative w-full h-full">
                  <img
                    src={currentImage}
                    alt="Source"
                    className="w-full h-full object-contain bg-space-800"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-space-900/80 to-transparent" />
                  <div className="absolute bottom-4 left-4 right-4 flex justify-between items-center">
                    <span className="text-sm text-white/80">Source Image</span>
                    <span className="px-2 py-1 rounded bg-accent-magenta/20 text-accent-magenta text-xs">
                      Click to change
                    </span>
                  </div>
                </div>
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center p-8 text-center">
                  <div className="w-16 h-16 rounded-full bg-accent-magenta/10 flex items-center justify-center mb-4">
                    <Upload className="w-8 h-8 text-accent-magenta" />
                  </div>
                  <h3 className="text-lg font-medium mb-2">
                    {isDragActive ? 'Drop your image' : 'Upload Source Image'}
                  </h3>
                  <p className="text-sm text-gray-400">
                    PNG, JPG, WebP supported
                  </p>
                </div>
              )}
            </div>

            {/* Prompt */}
            <div className="card p-4">
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Dream Description (optional)
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the dream effect you want..."
                className="input-field h-24 resize-none"
              />
            </div>
          </motion.div>

          {/* Settings & Output */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="space-y-4"
          >
            {/* Settings */}
            <div className="card p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-4 flex items-center gap-2">
                <Wand2 size={16} className="text-accent-magenta" />
                Video Settings
              </h3>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Duration</span>
                    <span className="text-accent-magenta font-mono">{duration}s</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="30"
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    className="w-full accent-accent-magenta"
                  />
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Frame Rate</span>
                    <span className="text-accent-magenta font-mono">{fps} FPS</span>
                  </div>
                  <input
                    type="range"
                    min="15"
                    max="60"
                    value={fps}
                    onChange={(e) => setFps(Number(e.target.value))}
                    className="w-full accent-accent-magenta"
                  />
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Motion Strength</span>
                    <span className="text-accent-magenta font-mono">{motionStrength}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={motionStrength}
                    onChange={(e) => setMotionStrength(Number(e.target.value))}
                    className="w-full accent-accent-magenta"
                  />
                </div>
              </div>
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={!currentImage || processing}
              className="w-full btn-primary py-4 text-lg flex items-center justify-center gap-3 disabled:opacity-50"
            >
              {processing ? (
                <>
                  <Loader2 className="animate-spin" size={24} />
                  Generating...
                </>
              ) : (
                <>
                  <Play size={24} />
                  Generate Dream Video
                </>
              )}
            </button>

            {/* Output */}
            {generatedVideo && (
              <div className="card overflow-hidden">
                <video
                  src={generatedVideo}
                  controls
                  className="w-full aspect-video bg-space-900"
                />
                <div className="p-4 flex justify-end">
                  <a
                    href={generatedVideo}
                    download={`dream-video-${Date.now()}.mp4`}
                    className="btn-secondary flex items-center gap-2"
                  >
                    <Download size={18} />
                    Download Video
                  </a>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  )
}
