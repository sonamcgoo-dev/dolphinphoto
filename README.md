# 🐬 DolphinPhoto AI Studio

## The Ultimate AI Creative Studio

> **Photoshop meets AI Magic** — A comprehensive creative suite for photo/video editing with AI-powered tools, filters, and real-time processing.

![Version](https://img.shields.io/badge/version-1.0.0-00d4ff?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-7b2dff?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-00ff88?style=for-the-badge)

---

## ✨ Features

### 🎨 Photo Tools
- **AI Generation**: Text-to-image, image-to-image, inpainting with Stable Diffusion
- **Smart Editing**: Crop, resize, rotate, brightness, contrast, saturation controls
- **Background Removal**: One-click AI-powered background removal
- **Upscaling**: 2x, 4x AI upscaling with Real-ESRGAN
- **Face Restoration**: GFPGAN-powered face enhancement

### 🎬 Video Tools
- **Dream Video**: Transform images into mesmerizing AI-powered videos
- **Video Slideshows**: Create videos from image collections with transitions
- **Video Enhancement**: Upscale, denoise, and stabilize videos
- **Trim & Edit**: Frame-accurate video cutting and speed control

### 🌈 Filters (60+)

**Social Filters (Snapchat-style)**
- 🐶🐱🐰 Face filters (puppy ears, cat ears, bunny ears)
- 🤓🕶️ Glasses (nerd, sunglasses)
- 😇👑👼 Accessories (halo, crown, flower crown)
- 😊💄✨ Beauty (blush, lipstick, eyeshadow, smooth skin)

**Artistic Filters**
- 🎞️ Vintage Film, 🎬 Cinematic, ✏️ Sketch, 🖼️ Oil Painting
- 🌈 Neon Glow, 💖 Pink, 💙 Blue, 💜 Purple
- 🎨 Watercolor, 📚 Comic Book, ✨ Holographic

**Color Grading**
- 🟠💧 Teal & Orange, 🌅 Golden Hour, ❄️ Cool Blue
- Duotones, Color Splash, Color Pop

**Glitch Effects**
- 💠 Glitch, 📺 Scanlines, 📡 Static, 🌈 RGB Shift

### 🤖 AI Tools (MCP Integration)
- **Model Context Protocol**: Connect AI agents and tools
- **Tool Registry**: 20+ built-in AI tools
- **Plugin System**: Extend functionality with custom plugins

### 📦 Model Management
- **CivitAI Integration**: Browse and download models
- **HuggingFace Support**: Access gated models
- **Local Models**: Checkpoint, LoRA, VAE, embeddings

---

## 🏗️ Tech Stack

### Backend
```
FastAPI          — Async web framework
PyTorch          — AI/ML with CUDA/MPS/CPU support
Diffusers        — Stable Diffusion pipelines
OpenCV           — Computer vision & video processing
SQLAlchemy       — Async database ORM
RemBG            — Background removal
Real-ESRGAN      — Image upscaling
```

### Frontend
```
React 18         — UI framework
TypeScript       — Type safety
Vite             — Build tool
TailwindCSS      — Styling
Radix UI         — Accessible components
Framer Motion    — Animations
Zustand          — State management
```

### Desktop
```
Electron         — Cross-platform desktop app
```

---

## 📥 Installation

### Prerequisites
- **Python 3.12+** — Backend runtime
- **Node.js 22+** — Frontend development
- **5+ GB free disk** — Dependencies and models

### Quick Start

#### Windows
```powershell
.\start.bat
```

#### Windows Installer (downloadable EXE)
```powershell
cd frontend
npm install
npm run electron:build:win
```
Installer output: `frontend\release\DolphinPhoto AI Studio Setup 1.0.0.exe`

On first launch from the installer build, the app bootstraps backend dependencies, then starts the studio and pre-pulls the default model in the background. To skip model pre-pull for testing, set `DOLPHINPHOTO_SKIP_MODEL_PULL=1`.

#### macOS/Linux
```bash
chmod +x start.sh
./start.sh
```

#### Manual Start
```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## 🚀 Usage

1. **Studio** - Main editing workspace
2. **Dream Video** - AI video generation
3. **Glowup** - AI photo enhancement
4. **Filters** - Browse and apply 60+ filters
5. **Models** - Manage AI models
6. **MCP Hub** - Connect AI tools
7. **Workspace** - Browse generated content

---

## 🗂️ Project Structure

```
dolphinphoto/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/           # Configuration
│   │   ├── services/       # Business logic
│   │   │   ├── ai_service.py      # Stable Diffusion
│   │   │   ├── filter_service.py   # 60+ filters
│   │   │   ├── video_service.py    # Video processing
│   │   │   └── device_service.py   # Hardware detection
│   │   ├── mcp/            # MCP server
│   │   └── plugins/        # Plugin system
│   └── main.py             # Entry point
│
├── frontend/
│   ├── src/
│   │   ├── pages/          # Application pages
│   │   ├── store/          # Zustand stores
│   │   └── api/            # API client
│   └── electron/           # Desktop app
│
├── start.bat               # Windows launcher
├── start.sh               # Unix launcher
└── README.md              # This file
```

---

## 💻 Hardware Support

| Hardware | Performance |
|----------|-------------|
| NVIDIA GPU (24GB+) | 🔥 Elite |
| NVIDIA GPU (16GB) | ⚡ Premium |
| NVIDIA GPU (8GB) | 💪 High |
| Apple Silicon | 🍎 M1-M3 |
| CPU Only | 💻 Fallback |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License

---

## 🐬 Credits

**Black Tiger Computing**
Lead Developer: Sona McGoo

Built with FastAPI, React, PyTorch, Diffusers, and ❤️
