# 🐬 DolphinPhoto

Local AI photo & video editing application by Black Tiger Computing.

## Features

- **AI-Powered Editing**: Stable Diffusion (txt2img, img2img, inpainting), background removal, upscaling, denoising, sharpening
- **Video Generation**: Create videos from images with transitions and effects
- **Dream Video**: AI-powered video generation from image sequences with face detection
- **Glowup**: AI creative enhancement with face restoration
- **Model Management**: Browse and download models from CivitAI with hardware-specific recommendations
- **LoRA Support**: Load, manage, and apply LoRA adapters to customize AI outputs
- **Workflow System**: Create, save, and execute custom image processing pipelines
- **File Conversion**: Convert between PNG, JPEG, WebP, BMP, and TIFF formats
- **MCP Server**: Model Context Protocol for agent/IDE integration
- **Hardware-Aware**: Automatic GPU detection and optimization (CUDA, MPS, CPU)
- **Local-First**: All processing happens on your machine - no cloud required
- **Cross-Platform**: Windows, macOS, and Linux support via Electron

## Tech Stack

### Backend
- **FastAPI**: Modern async web framework
- **PyTorch**: AI/ML framework with CPU/GPU support
- **Diffusers**: Stable Diffusion models
- **OpenCV**: Image processing
- **SQLite**: Local database for settings and jobs

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Fast build tool
- **TailwindCSS**: Styling
- **Radix UI**: Component library
- **Electron**: Desktop application wrapper

## Prerequisites

- **Python 3.12+**: For the backend
- **Node.js 22+**: For the frontend
- **5+ GB free disk space**: For Python dependencies and AI models

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd dolphinphoto
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
```

### 4. Run the Application

#### Development Mode (PowerShell on Windows)
```powershell
.\dev.ps1
```

This will start:
- Backend API server on `http://127.0.0.1:7777`
- Frontend dev server on `http://localhost:5173`

#### Manual Startup

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

#### Electron Desktop App
```bash
cd frontend
npm run electron:dev
```

## First-Time Setup

1. Launch the application
2. Complete the setup wizard:
   - Choose a workspace directory (where models and outputs will be stored)
   - Optionally add your CivitAI API key for model downloads
3. Start editing!

## Usage

### Basic Workflow
1. **Upload Images**: Drag and drop images into the editor
2. **Select Tool**: Choose from the sidebar (Filters, Resize, AI tools, etc.)
3. **Adjust Settings**: Use the tool panel to configure parameters
4. **Process**: Click to apply the transformation
5. **Download**: Save your results

### Advanced Features

#### Workflows
Create reusable processing pipelines:
- Combine multiple operations (filters, AI tools, transforms)
- Save and load custom workflows
- Use preset workflows for common tasks (Quick Enhance, Portrait Glowup, Vintage Photo, Social Media Ready)

#### LoRA Management
- Browse and download LoRA adapters from CivitAI
- Load LoRAs into memory for use in txt2img/img2img
- Apply multiple LoRAs with custom weights
- Manage loaded LoRAs via the Models panel

#### MCP Integration
The DolphinPhoto MCP server allows AI agents and IDEs to integrate with the application:
- Run the MCP server: `python -m app.mcp.server`
- Provides tools for image generation, transformation, and processing
- Exposes device information and model resources
- Enables automation and batch processing workflows

#### Hardware-Specific Recommendations
During setup, DolphinPhoto analyzes your hardware and recommends:
- Optimal models for your GPU/CPU configuration
- Starter pack of essential models (checkpoint, upscaler, LoRA)
- Performance expectations based on your hardware tier

### AI Tools
- **Txt2Img**: Generate images from text prompts
- **Img2Img**: Transform images with AI
- **Inpaint**: Edit specific regions of images
- **Remove Background**: Automatic background removal
- **Upscale**: Enhance image resolution with AI
- **Glowup**: Creative AI enhancement

### Video Tools
- **Video Generator**: Create slideshows with transitions
- **Dream Video**: AI-powered video generation

## Project Structure

```
dolphinphoto/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration, database
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic (AI tools, etc.)
│   │   └── plugins/      # Plugin system
│   ├── main.py           # Application entry point
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── store/        # State management (Zustand)
│   │   └── utils/        # Utilities, API client
│   ├── electron/         # Electron main process
│   └── package.json      # Node dependencies
└── dev.ps1              # Development launcher
```

## Configuration

### Backend
Configuration is managed via environment variables and database settings. See `backend/app/core/config.py` for options.

### Frontend
Environment variables are set in `frontend/.env`:
```
VITE_API_URL=http://127.0.0.1:7777
```

## GPU Acceleration

The application automatically detects and uses available GPU acceleration:
- **CUDA**: NVIDIA GPUs (install PyTorch with CUDA support)
- **MPS**: Apple Silicon (M1/M2/M3) GPUs
- **CPU**: Fallback for systems without GPU

For optimal performance with NVIDIA GPUs:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (requires 3.12+)
- Verify dependencies: `pip install -r requirements.txt`
- Check port 7777 is not in use

### Frontend won't start
- Check Node.js version: `node --version` (requires 22+)
- Verify dependencies: `npm install`
- Check backend is running on port 7777

### Out of disk space
The application requires ~5 GB for Python dependencies and additional space for AI models. Free up disk space before installation.

### AI models not downloading
- Verify CivitAI API key is set in setup
- Check internet connection
- Ensure workspace directory has write permissions

## License

MIT License - see LICENSE file for details

## Credits

**Black Tiger Computing**
Lead Developer: Sona McGoo

Built with:
- FastAPI, React, TypeScript, TailwindCSS
- PyTorch, Diffusers, Transformers
- Electron, Radix UI, Lucide Icons
