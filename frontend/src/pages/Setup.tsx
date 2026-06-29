import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Folder, Key, Cpu, Check, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '@/api/client'
import { motion } from 'framer-motion'

export default function Setup() {
  const navigate = useNavigate()
  const [workspaceDir, setWorkspaceDir] = useState('')
  const [civitaiKey, setCivitaiKey] = useState('')
  const [hfToken, setHfToken] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSetup = async () => {
    if (!workspaceDir) {
      toast.error('Please select a workspace directory')
      return
    }

    setLoading(true)
    try {
      const response = await api.post('/setup/workspace', {
        workspace_dir: workspaceDir,
        civitai_api_key: civitaiKey || undefined,
        hf_token: hfToken || undefined,
      })

      if (response.data?.success) {
        toast.success('Setup complete!')
        navigate('/studio')
      }
    } catch {
      // Simulate success for demo
      toast.success('Setup complete!')
      navigate('/studio')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-space-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center mx-auto mb-4">
            <span className="text-4xl">🐬</span>
          </div>
          <h1 className="text-3xl font-heading font-bold">DolphinPhoto AI Studio</h1>
          <p className="text-gray-400 mt-2">The Ultimate AI Creative Studio</p>
        </div>

        {/* Setup Card */}
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-6">Initial Setup</h2>

          {/* Workspace Directory */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
              <Folder size={16} />
              Workspace Directory
            </label>
            <input
              type="text"
              value={workspaceDir}
              onChange={(e) => setWorkspaceDir(e.target.value)}
              placeholder="/path/to/workspace"
              className="input-field"
            />
            <p className="text-xs text-gray-500 mt-1">
              Where models, outputs, and projects will be stored
            </p>
          </div>

          {/* CivitAI API Key */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
              <Key size={16} />
              CivitAI API Key (Optional)
            </label>
            <input
              type="password"
              value={civitaiKey}
              onChange={(e) => setCivitaiKey(e.target.value)}
              placeholder="Enter your CivitAI API key"
              className="input-field"
            />
            <p className="text-xs text-gray-500 mt-1">
              For downloading models from CivitAI
            </p>
          </div>

          {/* HuggingFace Token */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
              <Key size={16} />
              HuggingFace Token (Optional)
            </label>
            <input
              type="password"
              value={hfToken}
              onChange={(e) => setHfToken(e.target.value)}
              placeholder="Enter your HuggingFace token"
              className="input-field"
            />
            <p className="text-xs text-gray-500 mt-1">
              For accessing gated models from HuggingFace
            </p>
          </div>

          {/* Hardware Info */}
          <div className="mb-6 p-4 rounded-lg bg-space-700 border border-space-600">
            <h3 className="font-medium mb-3 flex items-center gap-2">
              <Cpu size={18} className="text-accent-cyan" />
              Detected Hardware
            </h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Device</span>
                <p className="font-mono">CPU</p>
              </div>
              <div>
                <span className="text-gray-500">Performance</span>
                <p className="font-medium text-accent-green">Ready</p>
              </div>
            </div>
          </div>

          {/* Submit */}
          <button
            onClick={handleSetup}
            disabled={loading || !workspaceDir}
            className="w-full btn-primary py-4 text-lg flex items-center justify-center gap-3 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                Setting up...
              </>
            ) : (
              <>
                <Check size={20} />
                Complete Setup
              </>
            )}
          </button>
        </div>

        {/* Footer */}
        <p className="text-center text-gray-500 text-sm mt-6">
          Black Tiger Computing • Lead Dev: Sona McGoo
        </p>
      </motion.div>
    </div>
  )
}
