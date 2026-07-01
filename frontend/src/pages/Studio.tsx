import { useCallback, useEffect, useMemo, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  ArrowDown,
  ArrowUp,
  Boxes,
  Download,
  FileJson2,
  FileOutput,
  FlipHorizontal,
  FolderOpen,
  GitBranch,
  Loader2,
  RotateCw,
  ScanLine,
  Sparkles,
  Upload,
  Wand2,
} from 'lucide-react'
import clsx from 'clsx'
import toast from 'react-hot-toast'
import { api, imageToBase64 } from '@/api/client'
import { useAppStore } from '@/store/useAppStore'
import WorkflowWidget from '@/components/studio/WorkflowWidget'

interface ModelInfo {
  id: string
  name: string
  type: string
  size: number
  loaded: boolean
}

interface McpTool {
  name: string
  description: string
  category?: string
}

interface ImportedNode {
  id: string
  classType: string
  title: string
}

type WidgetKey =
  | 'workflow'
  | 'preset'
  | 'model'
  | 'lora'
  | 'rag'
  | 'mcp'
  | 'comfyNodes'
  | 'comfyExtensions'

interface WidgetConfig {
  key: WidgetKey
  title: string
  subtitle?: string
  enabled: boolean
  collapsed: boolean
}

interface PipelineMetric {
  label: string
  ms: number
}

const workflowOptions = ['Manual Retouch', 'Prompt Enhance', 'Batch Convert', 'LoRA Stylize', 'RAG Assist + MCP']
const presetOptions = ['Photo Real', 'Cinematic', 'Social Boost', 'Product Shot', 'Portrait Retouch']
const ragSources = ['Workspace Outputs', 'Projects Notes', 'Model Cards', 'Plugin Docs']
const converterFormats = ['png', 'jpeg', 'webp'] as const

const defaultWidgets: WidgetConfig[] = [
  { key: 'workflow', title: 'Workflow', enabled: true, collapsed: false },
  { key: 'preset', title: 'Presets', enabled: true, collapsed: false },
  { key: 'model', title: 'Models', enabled: true, collapsed: false },
  { key: 'lora', title: 'LoRAs', enabled: true, collapsed: false },
  { key: 'rag', title: 'RAG Sources', enabled: true, collapsed: true },
  { key: 'mcp', title: 'MCP Tool Selection', enabled: true, collapsed: true },
  {
    key: 'comfyNodes',
    title: 'ComfyUI Imported Nodes',
    subtitle: 'Loads after importing workflow JSON',
    enabled: true,
    collapsed: false,
  },
  {
    key: 'comfyExtensions',
    title: 'ComfyUI Extension Families',
    subtitle: 'Derived from imported node class names',
    enabled: true,
    collapsed: false,
  },
]

function inferExtensionFamily(classType: string): string {
  const separators = ['.', '/', ':', '_']
  for (const sep of separators) {
    if (classType.includes(sep)) {
      return classType.split(sep)[0]
    }
  }
  const camelSplit = classType.match(/^[A-Z][a-z]+/)
  if (camelSplit?.[0]) {
    return camelSplit[0]
  }
  return classType
}

function parseComfyWorkflow(raw: string): ImportedNode[] {
  const parsed = JSON.parse(raw) as unknown
  const nodes: ImportedNode[] = []

  if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
    const record = parsed as Record<string, unknown>

    if (Array.isArray(record.nodes)) {
      for (const item of record.nodes) {
        if (!item || typeof item !== 'object') continue
        const node = item as Record<string, unknown>
        const id = String(node.id ?? '')
        const classType = String(node.class_type ?? node.type ?? '')
        if (!id || !classType) continue
        const title = String((node._meta as Record<string, unknown> | undefined)?.title ?? classType)
        nodes.push({ id, classType, title })
      }
    } else {
      for (const [id, value] of Object.entries(record)) {
        if (!value || typeof value !== 'object') continue
        const node = value as Record<string, unknown>
        const classType = String(node.class_type ?? '')
        if (!classType) continue
        const title = String((node._meta as Record<string, unknown> | undefined)?.title ?? classType)
        nodes.push({ id, classType, title })
      }
    }
  }

  return nodes
}

export default function Studio() {
  const { currentImage, setCurrentImage, processing, setProcessing } = useAppStore()
  const [history, setHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [models, setModels] = useState<ModelInfo[]>([])
  const [mcpTools, setMcpTools] = useState<McpTool[]>([])
  const [widgets, setWidgets] = useState<WidgetConfig[]>(defaultWidgets)
  const [selectedWorkflow, setSelectedWorkflow] = useState(workflowOptions[0])
  const [selectedPreset, setSelectedPreset] = useState(presetOptions[0])
  const [selectedModel, setSelectedModel] = useState('')
  const [selectedLoras, setSelectedLoras] = useState<string[]>([])
  const [selectedMcpTools, setSelectedMcpTools] = useState<string[]>([])
  const [selectedRagSources, setSelectedRagSources] = useState<string[]>([])
  const [converterFormat, setConverterFormat] = useState<(typeof converterFormats)[number]>('png')
  const [prompt, setPrompt] = useState('clean retouch, natural lighting, high detail')
  const [strength, setStrength] = useState(0.45)
  const [steps, setSteps] = useState(30)
  const [cfgScale, setCfgScale] = useState(7.5)
  const [importedNodes, setImportedNodes] = useState<ImportedNode[]>([])
  const [selectedImportedNodes, setSelectedImportedNodes] = useState<string[]>([])
  const [selectedExtensions, setSelectedExtensions] = useState<string[]>([])
  const [downloadBusy, setDownloadBusy] = useState(false)
  const [metrics, setMetrics] = useState<PipelineMetric[]>([
    { label: 'Load', ms: 180 },
    { label: 'Prep', ms: 210 },
    { label: 'Manual', ms: 95 },
    { label: 'AI', ms: 320 },
    { label: 'Output', ms: 140 },
  ])

  const checkpointModels = useMemo(() => models.filter((m) => m.type === 'checkpoint'), [models])
  const loraModels = useMemo(() => models.filter((m) => m.type === 'lora'), [models])
  const extensionFamilies = useMemo(
    () => Array.from(new Set(importedNodes.map((n) => inferExtensionFamily(n.classType)))).sort(),
    [importedNodes],
  )
  const maxMetric = Math.max(...metrics.map((m) => m.ms), 1)

  useEffect(() => {
    const fetchRightRailData = async () => {
      try {
        const [modelsRes, mcpRes] = await Promise.all([api.get('/models'), api.get('/mcp/tools')])
        const fetchedModels: ModelInfo[] = modelsRes.data?.models ?? []
        const fetchedTools: McpTool[] = mcpRes.data?.tools ?? []
        setModels(fetchedModels)
        setMcpTools(fetchedTools)
        if (!selectedModel && fetchedModels.length > 0) {
          const firstCkpt = fetchedModels.find((m) => m.type === 'checkpoint')
          setSelectedModel(firstCkpt?.name ?? fetchedModels[0].name)
        }
      } catch {
        setModels([
          { id: 'sd21', name: 'stabilityai/stable-diffusion-2-1', type: 'checkpoint', size: 5e9, loaded: false },
          { id: 'sdxl', name: 'stabilityai/stable-diffusion-xl-base-1.0', type: 'checkpoint', size: 6.5e9, loaded: false },
          { id: 'cine', name: 'cinematic-lora-v2', type: 'lora', size: 110e6, loaded: false },
          { id: 'fashion', name: 'fashion-portrait-lora', type: 'lora', size: 98e6, loaded: false },
        ])
        setMcpTools([
          { name: 'workspace.search', description: 'Search workspace files', category: 'workspace' },
          { name: 'image.metadata', description: 'Inspect image metadata', category: 'image' },
          { name: 'prompt.expand', description: 'Expand prompt intent', category: 'prompt' },
        ])
      }
    }
    fetchRightRailData()
  }, [selectedModel])

  const pushMetric = (label: string, ms: number) => {
    setMetrics((prev) => prev.map((m) => (m.label === label ? { ...m, ms: Math.round(ms) } : m)))
  }

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (!acceptedFiles[0]) return
      const base64 = await imageToBase64(acceptedFiles[0])
      setCurrentImage(base64)
      setHistory([base64])
      setHistoryIndex(0)
      pushMetric('Load', 150 + Math.random() * 120)
      toast.success('Image loaded')
    },
    [setCurrentImage],
  )

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] },
    maxFiles: 1,
    noClick: true,
  })

  const loadImageElement = (src: string) =>
    new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = () => reject(new Error('Failed to load image'))
      img.src = src
    })

  const pushHistory = (nextImage: string) => {
    setHistory((prev) => [...prev.slice(0, historyIndex + 1), nextImage])
    setHistoryIndex((prev) => prev + 1)
    setCurrentImage(nextImage)
  }

  const transformCurrentImage = async (
    label: string,
    transformer: (ctx: CanvasRenderingContext2D, img: HTMLImageElement) => void,
  ) => {
    if (!currentImage) return
    const started = performance.now()
    setProcessing(true)
    try {
      const img = await loadImageElement(currentImage)
      const canvas = document.createElement('canvas')
      canvas.width = img.width
      canvas.height = img.height
      const ctx = canvas.getContext('2d')
      if (!ctx) throw new Error('Canvas not available')
      transformer(ctx, img)
      pushHistory(canvas.toDataURL('image/png'))
      pushMetric(label, performance.now() - started)
      toast.success(`${label} applied`)
    } catch {
      toast.error(`${label} failed`)
    } finally {
      setProcessing(false)
    }
  }

  const rotateRight = () =>
    transformCurrentImage('Manual', (ctx, img) => {
      const canvas = ctx.canvas
      canvas.width = img.height
      canvas.height = img.width
      ctx.translate(canvas.width / 2, canvas.height / 2)
      ctx.rotate(Math.PI / 2)
      ctx.drawImage(img, -img.width / 2, -img.height / 2)
    })

  const flipHorizontal = () =>
    transformCurrentImage('Manual', (ctx, img) => {
      ctx.translate(img.width, 0)
      ctx.scale(-1, 1)
      ctx.drawImage(img, 0, 0)
    })

  const autoEnhance = () =>
    transformCurrentImage('Prep', (ctx, img) => {
      ctx.filter = 'contrast(1.08) saturate(1.1) brightness(1.03)'
      ctx.drawImage(img, 0, 0)
    })

  const runAiEnhance = async () => {
    if (!currentImage) return
    const started = performance.now()
    setProcessing(true)
    try {
      await api.post('/images/transform', {
        image: currentImage,
        prompt,
        strength,
        steps,
        cfg_scale: cfgScale,
        model_name: selectedModel || undefined,
      })
      pushMetric('AI', performance.now() - started)
      toast.success('AI transform submitted')
    } catch {
      toast.error('AI transform unavailable. Check backend status.')
    } finally {
      setProcessing(false)
    }
  }

  const convertAndDownload = async () => {
    if (!currentImage) return
    const started = performance.now()
    setDownloadBusy(true)
    try {
      const img = await loadImageElement(currentImage)
      const canvas = document.createElement('canvas')
      canvas.width = img.width
      canvas.height = img.height
      const ctx = canvas.getContext('2d')
      if (!ctx) throw new Error('Canvas not available')
      ctx.drawImage(img, 0, 0)
      const mime = converterFormat === 'jpeg' ? 'image/jpeg' : converterFormat === 'webp' ? 'image/webp' : 'image/png'
      const quality = converterFormat === 'png' ? undefined : 0.92
      const dataUrl = canvas.toDataURL(mime, quality)
      const link = document.createElement('a')
      link.href = dataUrl
      link.download = `dolphinphoto-convert-${Date.now()}.${converterFormat}`
      link.click()
      pushMetric('Output', performance.now() - started)
      toast.success(`Converted to ${converterFormat.toUpperCase()}`)
    } catch {
      toast.error('File conversion failed')
    } finally {
      setDownloadBusy(false)
    }
  }

  const downloadCurrent = () => {
    if (!currentImage) return
    setDownloadBusy(true)
    const link = document.createElement('a')
    link.href = currentImage
    link.download = `dolphinphoto-${Date.now()}.png`
    link.click()
    pushMetric('Output', 80 + Math.random() * 80)
    setTimeout(() => setDownloadBusy(false), 550)
  }

  const undo = () => {
    if (historyIndex <= 0) return
    const nextIndex = historyIndex - 1
    setHistoryIndex(nextIndex)
    setCurrentImage(history[nextIndex] ?? null)
  }

  const redo = () => {
    if (historyIndex >= history.length - 1) return
    const nextIndex = historyIndex + 1
    setHistoryIndex(nextIndex)
    setCurrentImage(history[nextIndex] ?? null)
  }

  const clearCanvas = () => {
    setCurrentImage(null)
    setHistory([])
    setHistoryIndex(-1)
  }

  const toggleFromArray = (value: string, array: string[], setter: (next: string[]) => void) => {
    if (array.includes(value)) {
      setter(array.filter((x) => x !== value))
      return
    }
    setter([...array, value])
  }

  const setWidget = (key: WidgetKey, updater: (w: WidgetConfig) => WidgetConfig) => {
    setWidgets((prev) => prev.map((w) => (w.key === key ? updater(w) : w)))
  }

  const moveWidget = (index: number, direction: -1 | 1) => {
    const nextIndex = index + direction
    if (nextIndex < 0 || nextIndex >= widgets.length) return
    setWidgets((prev) => {
      const copy = [...prev]
      const [item] = copy.splice(index, 1)
      copy.splice(nextIndex, 0, item)
      return copy
    })
  }

  const importComfyWorkflow = async (file: File) => {
    try {
      const text = await file.text()
      const nodes = parseComfyWorkflow(text)
      if (nodes.length === 0) {
        toast.error('No compatible ComfyUI nodes found in JSON')
        return
      }
      setImportedNodes(nodes)
      setSelectedImportedNodes(nodes.map((n) => n.id))
      setSelectedExtensions(Array.from(new Set(nodes.map((n) => inferExtensionFamily(n.classType)))))
      setSelectedWorkflow('Imported ComfyUI')
      pushMetric('Prep', 80 + Math.random() * 140)
      toast.success(`Imported ComfyUI workflow (${nodes.length} nodes)`)
    } catch {
      toast.error('Invalid ComfyUI workflow JSON')
    }
  }

  const renderWidgetContent = (key: WidgetKey) => {
    switch (key) {
      case 'workflow':
        return (
          <select className="input-field" value={selectedWorkflow} onChange={(e) => setSelectedWorkflow(e.target.value)}>
            {workflowOptions.concat(importedNodes.length > 0 ? ['Imported ComfyUI'] : []).map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        )
      case 'preset':
        return (
          <select className="input-field" value={selectedPreset} onChange={(e) => setSelectedPreset(e.target.value)}>
            {presetOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        )
      case 'model':
        return (
          <select className="input-field" value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
            {checkpointModels.length === 0 ? (
              <option value="">No checkpoints found</option>
            ) : (
              checkpointModels.map((model) => (
                <option key={model.id} value={model.name}>
                  {model.name}
                </option>
              ))
            )}
          </select>
        )
      case 'lora':
        return (
          <div className="space-y-1 max-h-28 overflow-auto border border-space-600 rounded-lg p-2 bg-space-700/50">
            {loraModels.length === 0 ? (
              <div className="text-xs text-gray-500">No LoRAs detected</div>
            ) : (
              loraModels.map((lora) => (
                <label key={lora.id} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={selectedLoras.includes(lora.name)}
                    onChange={() => toggleFromArray(lora.name, selectedLoras, setSelectedLoras)}
                  />
                  <span>{lora.name}</span>
                </label>
              ))
            )}
          </div>
        )
      case 'rag':
        return (
          <div className="space-y-1 border border-space-600 rounded-lg p-2 bg-space-700/50">
            {ragSources.map((source) => (
              <label key={source} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={selectedRagSources.includes(source)}
                  onChange={() => toggleFromArray(source, selectedRagSources, setSelectedRagSources)}
                />
                <span>{source}</span>
              </label>
            ))}
          </div>
        )
      case 'mcp':
        return (
          <div className="space-y-1 max-h-36 overflow-auto border border-space-600 rounded-lg p-2 bg-space-700/50">
            {mcpTools.length === 0 ? (
              <div className="text-xs text-gray-500">No MCP tools available</div>
            ) : (
              mcpTools.map((tool) => (
                <label key={tool.name} className="flex items-start gap-2 text-sm">
                  <input
                    type="checkbox"
                    className="mt-1"
                    checked={selectedMcpTools.includes(tool.name)}
                    onChange={() => toggleFromArray(tool.name, selectedMcpTools, setSelectedMcpTools)}
                  />
                  <span>
                    <span className="block">{tool.name}</span>
                    <span className="text-xs text-gray-500">{tool.description}</span>
                  </span>
                </label>
              ))
            )}
          </div>
        )
      case 'comfyNodes':
        return (
          <div className="space-y-1 max-h-32 overflow-auto border border-space-600 rounded-lg p-2 bg-space-700/50">
            {importedNodes.length === 0 ? (
              <div className="text-xs text-gray-500">Import a ComfyUI JSON to populate nodes</div>
            ) : (
              importedNodes.map((node) => (
                <label key={node.id} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={selectedImportedNodes.includes(node.id)}
                    onChange={() => toggleFromArray(node.id, selectedImportedNodes, setSelectedImportedNodes)}
                  />
                  <span className="truncate">
                    {node.title} <span className="text-xs text-gray-500">({node.classType})</span>
                  </span>
                </label>
              ))
            )}
          </div>
        )
      case 'comfyExtensions':
        return (
          <div className="space-y-1 border border-space-600 rounded-lg p-2 bg-space-700/50">
            {extensionFamilies.length === 0 ? (
              <div className="text-xs text-gray-500">No extension families discovered yet</div>
            ) : (
              extensionFamilies.map((family) => (
                <label key={family} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={selectedExtensions.includes(family)}
                    onChange={() => toggleFromArray(family, selectedExtensions, setSelectedExtensions)}
                  />
                  <span>{family}</span>
                </label>
              ))
            )}
          </div>
        )
    }
  }

  return (
    <div className="h-full p-4 bg-space-900 overflow-y-auto xl:overflow-hidden">
      <div className="h-auto xl:h-full grid grid-cols-1 xl:grid-cols-[1.2fr_1.2fr_0.95fr] gap-4">
        <section className="card p-4 flex flex-col min-h-[520px] xl:min-h-0 overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <Wand2 size={18} className="text-accent-cyan" />
              Manual + AI Tools
            </h2>
            <div className="flex items-center gap-2">
              <button className="btn-secondary py-1.5 px-3 flex items-center gap-2" onClick={open}>
                <FolderOpen size={14} />
                Open
              </button>
              <button className="btn-secondary py-1.5 px-3" onClick={undo} disabled={historyIndex <= 0}>
                Undo
              </button>
              <button className="btn-secondary py-1.5 px-3" onClick={redo} disabled={historyIndex >= history.length - 1}>
                Redo
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 mb-3">
            <button className="btn-secondary flex items-center justify-center gap-2 py-2" onClick={autoEnhance} disabled={!currentImage || processing}>
              <Sparkles size={16} /> Auto
            </button>
            <button className="btn-secondary flex items-center justify-center gap-2 py-2" onClick={rotateRight} disabled={!currentImage || processing}>
              <RotateCw size={16} /> Rotate
            </button>
            <button className="btn-secondary flex items-center justify-center gap-2 py-2" onClick={flipHorizontal} disabled={!currentImage || processing}>
              <FlipHorizontal size={16} /> Flip
            </button>
            <button className="btn-primary flex items-center justify-center gap-2 py-2" onClick={runAiEnhance} disabled={!currentImage || processing}>
              {processing ? <Loader2 size={16} className="animate-spin" /> : <Wand2 size={16} />} Enhance
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_auto] gap-2 mb-3">
            <input value={prompt} onChange={(e) => setPrompt(e.target.value)} className="input-field" placeholder="Prompt" />
            <select value={converterFormat} onChange={(e) => setConverterFormat(e.target.value as (typeof converterFormats)[number])} className="input-field">
              {converterFormats.map((fmt) => (
                <option key={fmt} value={fmt}>
                  {fmt.toUpperCase()}
                </option>
              ))}
            </select>
            <button className="btn-primary flex items-center justify-center gap-2" onClick={convertAndDownload} disabled={!currentImage}>
              <FileOutput size={16} />
              Convert
            </button>
          </div>

          <div className="grid grid-cols-3 gap-2 mb-3">
            <label className="text-xs text-gray-400">
              Strength {strength.toFixed(2)}
              <input type="range" min="0.1" max="1" step="0.05" value={strength} onChange={(e) => setStrength(Number(e.target.value))} className="w-full accent-accent-cyan" />
            </label>
            <label className="text-xs text-gray-400">
              Steps {steps}
              <input type="range" min="10" max="80" step="1" value={steps} onChange={(e) => setSteps(Number(e.target.value))} className="w-full accent-accent-cyan" />
            </label>
            <label className="text-xs text-gray-400">
              CFG {cfgScale.toFixed(1)}
              <input type="range" min="1" max="15" step="0.5" value={cfgScale} onChange={(e) => setCfgScale(Number(e.target.value))} className="w-full accent-accent-cyan" />
            </label>
          </div>

          <div
            {...getRootProps()}
            className={clsx(
              'flex-1 rounded-xl border-2 border-dashed relative overflow-hidden',
              isDragActive ? 'border-accent-cyan bg-accent-cyan/10' : 'border-space-600',
            )}
          >
            <input {...getInputProps()} />
            {currentImage ? (
              <>
                <img src={currentImage} alt="Studio preview" className="w-full h-full object-contain bg-space-800" />
                {processing && (
                  <div className="absolute inset-0 bg-space-900/65 flex items-center justify-center">
                    <Loader2 className="animate-spin text-accent-cyan" size={36} />
                  </div>
                )}
              </>
            ) : (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
                <Upload className="text-accent-cyan mb-2" size={30} />
                <p className="font-medium">Drop image here</p>
                <p className="text-sm text-gray-500">Manual tools + converter + modular workflow widgets</p>
              </div>
            )}
          </div>

          <div className="mt-3 flex items-center gap-2">
            <button className="btn-primary flex items-center gap-2" onClick={downloadCurrent} disabled={!currentImage || downloadBusy}>
              {downloadBusy ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
              Download
            </button>
            <button className="btn-secondary" onClick={clearCanvas} disabled={!currentImage}>
              Clear
            </button>
          </div>
          {(processing || downloadBusy) && (
            <div className="mt-2">
              <div className="h-2 rounded bg-space-700 overflow-hidden">
                <div
                  className="h-2 bg-gradient-to-r from-accent-cyan to-accent-purple animate-pulse"
                  style={{ width: processing ? '70%' : '100%' }}
                />
              </div>
              <p className="text-xs text-gray-400 mt-1">{processing ? 'Processing…' : 'Preparing download…'}</p>
            </div>
          )}
        </section>

        <section className="card p-4 flex flex-col min-h-[520px] xl:min-h-0 overflow-hidden">
          <h2 className="text-lg font-bold flex items-center gap-2 mb-3">
            <GitBranch size={18} className="text-accent-purple" />
            Pipeline Graph
          </h2>

          <div className="rounded-xl border border-space-600 bg-space-800/70 p-3 mb-3">
            <svg viewBox="0 0 640 220" className="w-full h-52">
              <defs>
                <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#00d4ff" />
                  <stop offset="100%" stopColor="#7b2dff" />
                </linearGradient>
              </defs>
              <line x1="90" y1="110" x2="550" y2="110" stroke="url(#lineGrad)" strokeWidth="3" />
              {(importedNodes.length > 0
                ? importedNodes.slice(0, 5).map((node, index) => ({
                    x: 90 + index * 115,
                    y: index % 2 === 0 ? 90 : 140,
                    label: node.title.slice(0, 8),
                  }))
                : [
                    { x: 90, y: 110, label: 'Input' },
                    { x: 200, y: 70, label: 'Prep' },
                    { x: 320, y: 110, label: 'Manual' },
                    { x: 430, y: 150, label: 'AI' },
                    { x: 550, y: 110, label: 'Output' },
                  ]
              ).map((node) => (
                <g key={`${node.x}-${node.y}-${node.label}`}>
                  <circle cx={node.x} cy={node.y} r="24" fill="#12121a" stroke="#00d4ff" strokeWidth="2" />
                  <text x={node.x} y={node.y + 4} fill="#e6f9ff" fontSize="11" textAnchor="middle">
                    {node.label}
                  </text>
                </g>
              ))}
            </svg>
            <p className="text-xs text-gray-400 mt-1">
              Workflow: <span className="text-accent-cyan">{selectedWorkflow}</span> • Preset: <span className="text-accent-cyan">{selectedPreset}</span>
            </p>
          </div>

          <div className="rounded-xl border border-space-600 bg-space-800/70 p-3 mb-3">
            <div className="flex items-center gap-2 mb-2 text-sm font-medium text-gray-300">
              <ScanLine size={15} className="text-accent-cyan" />
              Execution Graph (ms)
            </div>
            <div className="space-y-2">
              {metrics.map((m) => (
                <div key={m.label}>
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>{m.label}</span>
                    <span>{m.ms} ms</span>
                  </div>
                  <div className="h-2 rounded bg-space-700">
                    <div
                      className="h-2 rounded bg-gradient-to-r from-accent-cyan to-accent-purple"
                      style={{ width: `${Math.max(6, Math.round((m.ms / maxMetric) * 100))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-space-600 bg-space-800/70 p-3">
            <label className="text-sm font-medium mb-2 flex items-center gap-2">
              <FileJson2 size={15} className="text-accent-green" />
              Import ComfyUI Workflow JSON
            </label>
            <input
              type="file"
              accept=".json,application/json"
              className="input-field"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) {
                  importComfyWorkflow(file)
                  e.currentTarget.value = ''
                }
              }}
            />
            <p className="text-xs text-gray-500 mt-2">
              Imported nodes can be enabled as modular widgets and shown in graph execution.
            </p>
          </div>
        </section>

        <section className="card p-4 min-h-[520px] xl:min-h-0 overflow-y-auto">
          <h2 className="text-lg font-bold flex items-center gap-2 mb-3">
            <Boxes size={18} className="text-accent-magenta" />
            Modular Workflow Widgets
          </h2>

          <div className="rounded-xl border border-space-600 bg-space-800/70 p-2 mb-3">
            <div className="text-xs text-gray-400 mb-2">Widget Manager</div>
            <div className="space-y-1">
              {widgets.map((widget, index) => (
                <div key={widget.key} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={widget.enabled}
                    onChange={() => setWidget(widget.key, (w) => ({ ...w, enabled: !w.enabled }))}
                  />
                  <span className="flex-1">{widget.title}</span>
                  <button className="btn-ghost p-1" onClick={() => moveWidget(index, -1)} disabled={index === 0}>
                    <ArrowUp size={14} />
                  </button>
                  <button className="btn-ghost p-1" onClick={() => moveWidget(index, 1)} disabled={index === widgets.length - 1}>
                    <ArrowDown size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            {widgets
              .filter((w) => w.enabled)
              .map((widget) => (
                <WorkflowWidget
                  key={widget.key}
                  title={widget.title}
                  subtitle={widget.subtitle}
                  collapsed={widget.collapsed}
                  onToggle={() => setWidget(widget.key, (w) => ({ ...w, collapsed: !w.collapsed }))}
                >
                  {renderWidgetContent(widget.key)}
                </WorkflowWidget>
              ))}
          </div>
        </section>
      </div>
    </div>
  )
}
