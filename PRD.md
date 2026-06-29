# DolphinPhoto AI Studio - Product Requirements Document

## 1. Concept & Vision

**DolphinPhoto AI Studio** is the ultimate creative powerhouse — a Photoshop meets AI magic, wrapped in the most dynamic UI ever built. It's not just an editor; it's a complete AI creative studio that puts professional-grade photo manipulation, video generation, and AI-powered tools at your fingertips. Think Adobe Creative Suite meets Midjourney, with Snapchat-style filters, real-time previews, and seamless integrations.

The experience should feel like piloting a starship's creative console — every interaction is buttery smooth, every tool responds instantly, and the AI does the heavy lifting while you focus on creation.

## 2. Design Language

### Aesthetic Direction
**Cyberpunk Creator Console** — Deep space blacks with electric cyan and magenta accents, glass-morphic panels, subtle grid patterns, and glowing interactive elements. The UI should feel like you're inside a futuristic creative workstation.

### Color Palette
- **Primary Background**: `#0a0a0f` (Deep Space)
- **Secondary Background**: `#12121a` (Panel Dark)
- **Tertiary/Cards**: `#1a1a25` (Elevated Surface)
- **Primary Accent**: `#00d4ff` (Electric Cyan)
- **Secondary Accent**: `#ff00aa` (Hot Magenta)
- **Tertiary Accent**: `#7b2dff` (Purple Glow)
- **Success**: `#00ff88` (Neon Green)
- **Warning**: `#ffaa00` (Amber)
- **Error**: `#ff3366` (Danger Red)
- **Text Primary**: `#ffffff`
- **Text Secondary**: `#8888aa`
- **Border Glow**: `#00d4ff33` (Translucent Cyan)

### Typography
- **Headings**: `Space Grotesk` — Futuristic, geometric, readable
- **Body**: `Inter` — Clean, professional, excellent legibility
- **Monospace**: `JetBrains Mono` — For code, values, technical info
- **Scale**: 12px / 14px / 16px / 20px / 28px / 36px / 48px

### Spatial System
- **Base unit**: 4px
- **Spacing scale**: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64px
- **Border radius**: 4px (small), 8px (medium), 12px (large), 16px (cards), 24px (modals)
- **Shadows**: Layered glow effects using accent colors

### Motion Philosophy
- **Micro-interactions**: 150ms ease-out for hover states
- **Panel transitions**: 250ms cubic-bezier(0.4, 0, 0.2, 1)
- **Modal entrances**: 300ms with scale 0.95 → 1.0 and fade
- **Loading states**: Pulsing gradients with accent colors
- **Real-time previews**: Immediate response, debounced processing

### Visual Assets
- **Icons**: Lucide React icons (consistent, clean, scalable)
- **Decorative**: Animated gradient borders, subtle grid backgrounds, floating particle effects
- **Previews**: Live-updating thumbnails with processing indicators

## 3. Layout & Structure

### Main Application Layout
```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER: Logo | Navigation Tabs | MCP Status | Settings | User  │
├────────────┬────────────────────────────────────────────────────┤
│            │                                                    │
│  TOOLBOX   │              CANVAS / WORKSPACE                   │
│  SIDEBAR   │         (Main editing area with                    │
│            │          live preview)                              │
│  - Photo   │                                                    │
│  - Video   │                                                    │
│  - Filters │                                                    │
│  - AI      ├────────────────────────────────────────────────────┤
│  - Models  │              TOOL PANEL                            │
│  - MCP     │         (Context-sensitive controls)               │
│            │                                                    │
├────────────┴────────────────────────────────────────────────────┤
│  FOOTER: Status Bar | Processing Queue | Performance Metrics    │
└─────────────────────────────────────────────────────────────────┘
```

### Navigation Tabs
1. **Studio** — Main editing workspace (default)
2. **Dream Video** — AI video generation
3. **Glowup** — AI photo enhancement
4. **Filters** — Snapchat/Instagram style filters
5. **Models** — AI model management
6. **MCP Hub** — Plugin/connection management
7. **Workspace** — File browser and project management

### Responsive Strategy
- **Desktop (1440px+)**: Full layout with all panels
- **Laptop (1024px-1439px)**: Collapsible sidebar, compact panels
- **Tablet (768px-1023px)**: Tab-based navigation, stacked panels

## 4. Features & Interactions

### A. Photo Tools

#### Basic Editing
- **Crop & Resize**: Free, aspect ratio presets (1:1, 4:3, 16:9, 9:16)
- **Rotate & Flip**: 90° increments, horizontal/vertical flip
- **Brightness/Contrast**: Range sliders with real-time preview
- **Hue/Saturation**: Color wheel picker with master/channel controls
- **Exposure/Gamma**: Precise adjustments with histogram overlay

#### Advanced Tools
- **Clone Stamp**: Intelligent sampling and painting
- **Healing Brush**: Remove imperfections, objects
- **Red Eye Removal**: One-click face correction
- **Perspective Correction**: Auto-detect and fix

#### AI Photo Tools
- **Txt2Img**: Generate images from text prompts
- **Img2Img**: Transform images with AI guidance
- **Inpaint**: Edit specific regions with AI
- **Outpaint**: Extend image beyond original boundaries
- **Face Swap**: Swap faces between images
- **Age/Gender Editor**: Modify subject appearance
- **Style Transfer**: Apply artistic styles

### B. Video Tools

#### Basic Video Editing
- **Import**: Support for MP4, MOV, AVI, WebM, MKV
- **Timeline**: Multi-track timeline with keyframes
- **Transitions**: Fade, dissolve, slide, zoom, glitch
- **Speed Control**: Slow-mo, fast-forward, reverse
- **Trim & Split**: Frame-accurate editing

#### AI Video Tools
- **Dream Video**: Generate videos from images with AI
- **Video Enhancement**: Upscale, denoise, stabilize
- **Style Transfer (Video)**: Apply styles to entire videos
- **Motion Interpolation**: Increase frame rate
- **Background Removal (Video)**: Process frame-by-frame

### C. Filters (Snapchat-style + Professional)

#### Social Filters
- **Face Filters**: 
  - Puppy ears, cat ears, glasses
  - Aging/youth effect
  - Gender swap preview
  - Makeup overlay (lipstick, eyeshadow)
  - Blemish smoothing

#### Artistic Filters
- **Vintage**: Film grain, light leaks, faded colors
- **Cinematic**: Color grading presets (teal-orange, golden hour)
- **Black & White**: Various conversion methods
- **HDR Effect**: High dynamic range simulation
- **Duotone**: Two-color mappings
- **Neon Glow**: Cyberpunk aesthetic
- **Glitch**: Digital corruption effects
- **Pixelate**: Retro gaming style

#### Color Filters
- **Color Splash**: Highlight specific colors
- **Color Pop**: Grayscale with color accents
- **Temperature Shift**: Cool/warm adjustments
- **Tint Control**: Green/magenta shift

### D. Image Tools

#### Format Conversion
- **Export**: PNG, JPEG, WebP, BMP, TIFF, GIF
- **Quality Control**: Compression level adjustment
- **ICC Profiles**: Color space conversion (sRGB, Adobe RGB, P3)

#### Enhancement
- **Upscale**: 2x, 4x AI upscaling
- **Denoise**: Remove noise while preserving detail
- **Sharpen**: Unsharp mask, clarity
- **Dehaze**: Remove fog/haze from photos
- **Vignette**: Darken edges

### E. MCP Client & Tool Plugins

#### MCP Server Features
- **Tool Registry**: Dynamic plugin loading
- **Connection Manager**: Connect to external MCP servers
- **Tool Invocation**: Execute remote tools
- **Resource Management**: Access remote resources
- **Prompt Templates**: Reusable prompt patterns

#### Built-in MCP Tools
```
- image.generate(prompt, model, steps, cfg)
- image.transform(image, operation, params)
- image.filter(image, filter_name, intensity)
- video.generate(frames, model, params)
- model.download(model_id, model_type)
- model.load(model_name)
- workspace.list_files(path)
- workspace.get_file(path)
```

### F. Model Management

#### Supported Model Types
- **Checkpoints**: Stable Diffusion checkpoints
- **LoRA**: LoRA adapters
- **Embeddings**: Textual inversions
- **Upscalers**: ESRGAN, RealESRGAN models
- **VAE**: Variational autoencoders

#### Model Operations
- **Browse**: Search CivitAI from within app
- **Download**: Background downloads with progress
- **Install**: Automatic model placement
- **Load/Unload**: Memory management
- **Preview**: Generate sample images

### G. Workflow System

#### Workflow Builder
- **Node-based Editor**: Visual workflow creation
- **Preset Workflows**: 
  - "Quick Glowup" — Enhance + sharpen + denoise
  - "Portrait Pro" — Face smoothing + makeup + lighting
  - "Cinematic Grade" — Color correction + vignette + grain
  - "Social Media" — Crop + filter + export
- **Custom Workflows**: Save and share

### H. Real-time Collaboration (Future)
- **Session Sharing**: Share workspace with others
- **Live Cursors**: See collaborator actions
- **Chat**: Built-in messaging

## 5. Component Inventory

### Navigation Components
| Component | States | Behavior |
|-----------|--------|----------|
| Tab Button | default, hover, active, disabled | Glow on hover, underline on active |
| Breadcrumb | default, clickable, current | Click navigates, current has glow |
| Sidebar Toggle | expanded, collapsed | Smooth width transition |

### Media Components
| Component | States | Behavior |
|-----------|--------|----------|
| Image Canvas | empty, loading, loaded, error | Drag-drop zone, loading shimmer |
| Video Player | stopped, playing, paused, buffering | Custom controls, progress bar |
| Thumbnail Grid | default, selected, processing | Hover preview, multi-select |
| Timeline | empty, populated, playing | Drag clips, trim handles |

### Tool Components
| Component | States | Behavior |
|-----------|--------|----------|
| Slider | default, dragging, disabled | Value tooltip on drag, haptic feel |
| Color Picker | closed, open, selecting | Wheel + input fields |
| Dropdown | closed, open, searching | Filter options, keyboard nav |
| Toggle | off, on, disabled | Animated switch |
| Button | default, hover, active, loading, disabled | Loading spinner, press effect |

### Feedback Components
| Component | States | Behavior |
|-----------|--------|----------|
| Toast | info, success, warning, error | Auto-dismiss, manual close |
| Modal | opening, open, closing | Scale animation, backdrop blur |
| Progress Bar | indeterminate, determinate | Gradient fill animation |
| Loading Skeleton | pulsing | Shimmer effect with accent colors |

### Filter Preview Components
| Component | States | Behavior |
|-----------|--------|----------|
| Filter Card | default, hover, selected, applying | Live preview on hover |
| Before/After Slider | default, dragging | Drag handle for comparison |
| Intensity Slider | 0-100% | Real-time filter adjustment |

## 6. Technical Approach

### Backend Architecture

#### Framework: FastAPI
- Async-first design for concurrent operations
- WebSocket support for real-time updates
- Auto-generated API documentation

#### Core Services
```
app/
├── api/
│   └── v1/
│       ├── images.py       # Image operations
│       ├── video.py        # Video operations
│       ├── filters.py      # Filter processing
│       ├── models.py       # Model management
│       ├── mcp.py          # MCP tool registry
│       ├── workflow.py      # Workflow execution
│       └── workspace.py    # File management
├── core/
│   ├── config.py          # Settings management
│   └── database.py        # SQLite/async SQLAlchemy
├── models/
│   └── db_models.py      # ORM models
├── services/
│   ├── ai_service.py      # Stable Diffusion
│   ├── filter_service.py  # Filter processing
│   ├── video_service.py   # Video processing
│   ├── model_service.py   # Model management
│   ├── mcp_service.py     # MCP server/client
│   └── device_service.py  # Hardware detection
├── plugins/
│   ├── manager.py         # Plugin loader
│   └── base.py            # Plugin interface
└── mcp/
    ├── server.py          # MCP server implementation
    └── tools.py           # Built-in MCP tools
```

### Frontend Architecture

#### Framework: React 18 + TypeScript
- Vite for fast development
- Zustand for state management
- React Query for server state
- TailwindCSS for styling
- Radix UI for accessible primitives

#### Key Components
```
frontend/
├── src/
│   ├── components/
│   │   ├── canvas/        # Main editing canvas
│   │   ├── filters/       # Filter system
│   │   ├── tools/         # Tool panels
│   │   ├── timeline/       # Video timeline
│   │   ├── models/         # Model browser
│   │   └── mcp/           # MCP hub
│   ├── pages/
│   │   ├── Studio.tsx
│   │   ├── DreamVideo.tsx
│   │   ├── Glowup.tsx
│   │   ├── Filters.tsx
│   │   ├── Models.tsx
│   │   └── MCPHub.tsx
│   ├── store/
│   │   ├── editorStore.ts
│   │   ├── filterStore.ts
│   │   └── modelStore.ts
│   └── api/
│       └── client.ts
├── electron/
│   ├── main.ts
│   └── preload.ts
└── package.json
```

### MCP Integration

#### MCP Server (Backend)
- Implements MCP specification
- Exposes tools via JSON-RPC over stdio
- WebSocket bridge for web clients
- Tool registration system for plugins

#### MCP Client (Frontend)
- Connect to local/remote MCP servers
- Display available tools
- Execute tools with progress tracking
-结果缓存

### Data Models

#### Database Schema
```sql
-- Settings
settings (key TEXT PRIMARY KEY, value TEXT)

-- Jobs
jobs (id, type, status, params JSON, result, created_at, updated_at)

-- Models
models (id, name, type, path, size, downloaded, metadata JSON)
```

#### File Storage
```
workspace/
├── models/           # AI models
├── outputs/          # Generated images/videos
├── workflows/        # Saved workflows
├── temp/             # Temporary files
└── projects/          # Project files
```

### Performance Considerations

#### Image Processing
- Lazy loading for thumbnails
- Web Workers for heavy operations
- Tile-based rendering for large images
- GPU acceleration via WebGL

#### Video Processing
- Frame-by-frame processing with batching
- Hardware acceleration (NVENC, QSV, VCE)
- Streaming output for long videos
- Memory-mapped file handling

#### Model Loading
- Lazy model loading
- Memory management with model eviction
- Model caching
- Quantized model support

## 7. Integrations

### External Services
- **CivitAI**: Model browsing and downloads
- **Hugging Face**: Additional model access
- **Local MCP Servers**: Custom tool integration

### File Systems
- **Local Filesystem**: Direct file access (Electron)
- **Cloud Storage**: S3, Google Drive, Dropbox (future)

### AI Providers
- **Local (Primary)**: Stable Diffusion, custom models
- **API (Optional)**: OpenAI, Anthropic for chat features

## 8. Packaging & Distribution

### Desktop Application (Electron)
- **Windows**: .exe installer (NSIS)
- **macOS**: .dmg package
- **Linux**: AppImage, .deb

### Standalone Executable
- PyInstaller for Python backend
- Electron bundling for frontend
- Combined into single installer

### Workspace Distribution
- Pre-configured model packs
- Docker containerization
- Portable mode (no installation)

## 9. MVP Scope

For initial release, implement:

### Core Features
1. ✅ Image upload and display
2. ✅ Basic photo tools (crop, rotate, brightness, contrast)
3. ✅ AI filters (Snapchat-style)
4. ✅ Color filters and adjustments
5. ✅ Export in multiple formats
6. ✅ Model management UI
7. ✅ MCP tool registry
8. ✅ Basic video support (import, timeline, transitions)
9. ✅ Dream Video generation
10. ✅ Glowup enhancement

### Technical Requirements
1. ✅ FastAPI backend with all endpoints
2. ✅ React frontend with dynamic UI
3. ✅ Electron desktop wrapper
4. ✅ SQLite database
5. ✅ Model download and management
6. ✅ MCP server integration
7. ✅ Complete workspace structure

## 10. Success Metrics

- Application launches without errors
- Images can be loaded, edited, and exported
- Filters apply in real-time with preview
- Video timeline functions correctly
- Models download and load successfully
- MCP tools execute and return results
- No console errors in production build
