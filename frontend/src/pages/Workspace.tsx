import { useState, useEffect } from 'react'
import { Folder, FileImage, FileVideo, File, Trash2, Download, RefreshCw, Grid, List, Search } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '@/api/client'
import { motion } from 'framer-motion'
import clsx from 'clsx'

interface FileItem {
  name: string
  path: string
  type: 'image' | 'video' | 'file'
  size: number
  modified: number
}

export default function Workspace() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchFiles()
  }, [])

  const fetchFiles = async () => {
    setLoading(true)
    try {
      const response = await api.get('/workspace/outputs')
      if (response.data?.files) {
        setFiles(response.data.files)
      }
    } catch {
      setFiles([
        { name: 'demo-output-1.png', path: '/outputs/demo-1.png', type: 'image', size: 1024 * 500, modified: Date.now() / 1000 },
        { name: 'demo-output-2.jpg', path: '/outputs/demo-2.jpg', type: 'image', size: 1024 * 800, modified: Date.now() / 1000 - 3600 },
        { name: 'demo-video.mp4', path: '/outputs/demo-video.mp4', type: 'video', size: 1024 * 1024 * 5, modified: Date.now() / 1000 - 7200 },
      ])
    }
    setLoading(false)
  }

  const handleDelete = async (file: FileItem) => {
    try {
      await api.delete('/workspace/file', { params: { path: file.path } })
      setFiles(prev => prev.filter(f => f.path !== file.path))
      toast.success('File deleted')
    } catch {
      toast.error('Failed to delete file')
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
    if (bytes >= 1024) return `${(bytes / 1024).toFixed(0)} KB`
    return `${bytes} B`
  }

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp * 1000)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const filteredFiles = files.filter(f => 
    f.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'image': return <FileImage size={24} className="text-accent-cyan" />
      case 'video': return <FileVideo size={24} className="text-accent-magenta" />
      default: return <File size={24} className="text-gray-400" />
    }
  }

  return (
    <div className="h-full p-4 bg-space-900 overflow-auto">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-heading font-bold flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-green flex items-center justify-center">
                <Folder className="text-space-900" size={20} />
              </div>
              Workspace
            </h1>
            <p className="text-gray-400 mt-1">
              Browse and manage your generated content
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={fetchFiles}
              className="p-2 rounded-lg bg-space-800 border border-space-600 hover:border-accent-cyan transition-colors"
            >
              <RefreshCw size={18} />
            </button>
            <div className="flex rounded-lg overflow-hidden border border-space-600">
              <button
                onClick={() => setViewMode('grid')}
                className={clsx(
                  'p-2 transition-colors',
                  viewMode === 'grid' ? 'bg-accent-cyan text-space-900' : 'bg-space-800'
                )}
              >
                <Grid size={18} />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={clsx(
                  'p-2 transition-colors',
                  viewMode === 'list' ? 'bg-accent-cyan text-space-900' : 'bg-space-800'
                )}
              >
                <List size={18} />
              </button>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search files..."
            className="input-field pl-10"
          />
        </div>

        {/* Files */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin" />
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {filteredFiles.map((file, idx) => (
              <motion.div
                key={file.path}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.03 }}
                className="card overflow-hidden group"
              >
                <div className="aspect-square bg-space-700 relative">
                  {file.type === 'image' ? (
                    <img
                      src={`http://127.0.0.1:7777/${file.path}`}
                      alt={file.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none'
                      }}
                    />
                  ) : file.type === 'video' ? (
                    <div className="w-full h-full flex items-center justify-center bg-space-800">
                      <FileVideo size={48} className="text-accent-magenta" />
                    </div>
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <File size={48} className="text-gray-400" />
                    </div>
                  )}
                  
                  {/* Overlay */}
                  <div className="absolute inset-0 bg-space-900/80 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <a
                      href={`http://127.0.0.1:7777/${file.path}`}
                      download={file.name}
                      className="p-2 rounded-lg bg-accent-cyan text-space-900 hover:bg-accent-cyan/80 transition-colors"
                    >
                      <Download size={18} />
                    </a>
                    <button
                      onClick={() => handleDelete(file)}
                      className="p-2 rounded-lg bg-red-500/80 text-white hover:bg-red-500 transition-colors"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
                <div className="p-3">
                  <h3 className="font-medium text-sm truncate">{file.name}</h3>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>{formatSize(file.size)}</span>
                    <span>{formatDate(file.modified)}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredFiles.map((file, idx) => (
              <motion.div
                key={file.path}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.02 }}
                className="card p-4 flex items-center gap-4 group"
              >
                <div className="w-12 h-12 rounded-lg bg-space-700 flex items-center justify-center">
                  {getFileIcon(file.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium truncate">{file.name}</h3>
                  <p className="text-sm text-gray-500 truncate">{file.path}</p>
                </div>
                <div className="text-right hidden sm:block">
                  <p className="text-sm">{formatSize(file.size)}</p>
                  <p className="text-xs text-gray-500">{formatDate(file.modified)}</p>
                </div>
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <a
                    href={`http://127.0.0.1:7777/${file.path}`}
                    download={file.name}
                    className="p-2 rounded-lg bg-accent-cyan text-space-900 hover:bg-accent-cyan/80 transition-colors"
                  >
                    <Download size={18} />
                  </a>
                  <button
                    onClick={() => handleDelete(file)}
                    className="p-2 rounded-lg bg-red-500/80 text-white hover:bg-red-500 transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {filteredFiles.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-64 text-gray-400">
            <Folder size={48} className="mb-4 opacity-50" />
            <p>No files found</p>
          </div>
        )}
      </div>
    </div>
  )
}
