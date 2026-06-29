"""
DolphinPhoto AI Studio - MCP Server
Model Context Protocol Server Implementation
"""
from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any, Callable

from app.core.config import get_settings

settings = get_settings()


class MCPTool:
    """Represents an MCP tool."""
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict,
        handler: Callable,
        category: str = "general",
        tags: list[str] | None = None,
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler
        self.category = category
        self.tags = tags or []
        self.usage_count = 0
        self.last_used: str | None = None


class MCPServer:
    """MCP Server for tool registration and execution."""
    
    def __init__(self):
        self._tools: dict[str, MCPTool] = {}
        self._subscribers: dict[str, list[Callable]] = {}
        self._lock = asyncio.Lock()
        try:
            self._initialize_builtin_tools()
        except ImportError:
            pass  # Services require heavy dependencies like torch
    
    def _initialize_builtin_tools(self) -> None:
        """Initialize built-in MCP tools."""
        # Import services directly after they are initialized
        try:
            from app.services.ai_service import AIService
            from app.services.filter_service import FilterService
            from app.services.video_service import VideoService
        except ImportError:
            return  # Dependencies not available
        
        ai_svc = AIService()
        filter_svc = FilterService()
        video_svc = VideoService()
        
        # Image Generation Tools
        self.register_tool(
            name="image.generate",
            description="Generate images from text prompts using AI",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Text prompt for generation"},
                    "negative_prompt": {"type": "string", "description": "Negative prompt", "default": ""},
                    "width": {"type": "integer", "description": "Image width", "default": 512},
                    "height": {"type": "integer", "description": "Image height", "default": 512},
                    "steps": {"type": "integer", "description": "Inference steps", "default": 30},
                    "cfg_scale": {"type": "number", "description": "CFG scale", "default": 7.5},
                    "seed": {"type": "integer", "description": "Random seed"},
                },
                "required": ["prompt"],
            },
            handler=ai_svc.txt2img,
            category="image_generation",
            tags=["ai", "stable-diffusion", "generation"],
        )
        
        self.register_tool(
            name="image.transform",
            description="Transform an existing image using AI (img2img)",
            input_schema={
                "type": "object",
                "properties": {
                    "image": {"type": "string", "description": "Base64 encoded image"},
                    "prompt": {"type": "string", "description": "Transformation prompt"},
                    "strength": {"type": "number", "description": "Transformation strength", "default": 0.75},
                    "steps": {"type": "integer", "description": "Inference steps", "default": 30},
                },
                "required": ["image", "prompt"],
            },
            handler=ai_svc.img2img,
            category="image_generation",
            tags=["ai", "stable-diffusion", "transform"],
        )
        
        self.register_tool(
            name="image.inpaint",
            description="Edit specific regions of an image using AI",
            input_schema={
                "type": "object",
                "properties": {
                    "image": {"type": "string", "description": "Base64 encoded image"},
                    "mask": {"type": "string", "description": "Base64 encoded mask"},
                    "prompt": {"type": "string", "description": "Inpainting prompt"},
                    "steps": {"type": "integer", "description": "Inference steps", "default": 30},
                },
                "required": ["image", "mask", "prompt"],
            },
            handler=ai_svc.inpaint,
            category="image_generation",
            tags=["ai", "stable-diffusion", "inpaint"],
        )
        
        # Image Processing Tools
        self.register_tool(
            name="image.upscale",
            description="Upscale an image using AI",
            input_schema={
                "type": "object",
                "properties": {
                    "image": {"type": "string", "description": "Base64 encoded image"},
                    "scale": {"type": "integer", "description": "Upscale factor", "default": 2},
                },
                "required": ["image"],
            },
            handler=ai_svc.upscale,
            category="image_processing",
            tags=["ai", "upscale", "enhance"],
        )
        
        self.register_tool(
            name="image.remove_background",
            description="Remove background from an image",
            input_schema={
                "type": "object",
                "properties": {
                    "image": {"type": "string", "description": "Base64 encoded image"},
                },
                "required": ["image"],
            },
            handler=ai_svc.remove_background,
            category="image_processing",
            tags=["background", "remove", "ai"],
        )
        
        self.register_tool(
            name="image.restore_face",
            description="Restore and enhance faces in an image",
            input_schema={
                "type": "object",
                "properties": {
                    "image": {"type": "string", "description": "Base64 encoded image"},
                    "strength": {"type": "number", "description": "Restoration strength", "default": 1.0},
                },
                "required": ["image"],
            },
            handler=ai_svc.face_restore,
            category="image_processing",
            tags=["face", "restore", "ai", "enhance"],
        )
        
        # Filter Tools
        self.register_tool(
            name="image.filter",
            description="Apply a filter to an image",
            input_schema={
                "type": "object",
                "properties": {
                    "image": {"type": "string", "description": "Base64 encoded image"},
                    "filter_name": {"type": "string", "description": "Filter to apply"},
                    "intensity": {"type": "number", "description": "Filter intensity", "default": 1.0},
                },
                "required": ["image", "filter_name"],
            },
            handler=self._apply_filter_wrapper,
            category="filters",
            tags=["filter", "style", "effect"],
        )
        
        self.register_tool(
            name="filter.list",
            description="List all available filters",
            input_schema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter category to list"},
                },
            },
            handler=self._list_filters_wrapper,
            category="filters",
            tags=["filter", "list"],
        )
        
        # Video Tools
        self.register_tool(
            name="video.generate",
            description="Generate a slideshow video from images",
            input_schema={
                "type": "object",
                "properties": {
                    "images": {"type": "array", "items": {"type": "string"}, "description": "Base64 encoded images"},
                    "duration": {"type": "number", "description": "Duration per image", "default": 3.0},
                    "transition": {"type": "string", "description": "Transition type", "default": "fade"},
                },
                "required": ["images"],
            },
            handler=video_svc.create_slideshow,
            category="video",
            tags=["video", "slideshow", "generation"],
        )
        
        self.register_tool(
            name="video.dream",
            description="Generate AI-powered dream video from image",
            input_schema={
                "type": "object",
                "properties": {
                    "image": {"type": "string", "description": "Base64 encoded image"},
                    "prompt": {"type": "string", "description": "Dream description", "default": ""},
                    "duration": {"type": "number", "description": "Video duration", "default": 5.0},
                    "motion": {"type": "number", "description": "Motion strength", "default": 0.5},
                },
                "required": ["image"],
            },
            handler=video_svc.generate_dream_video,
            category="video",
            tags=["video", "ai", "dream", "generation"],
        )
        
        self.register_tool(
            name="video.enhance",
            description="Enhance video quality",
            input_schema={
                "type": "object",
                "properties": {
                    "video_path": {"type": "string", "description": "Path to video file"},
                    "upscale": {"type": "number", "description": "Upscale factor", "default": 1.0},
                    "denoise": {"type": "boolean", "description": "Apply denoising", "default": True},
                },
                "required": ["video_path"],
            },
            handler=video_svc.enhance_video,
            category="video",
            tags=["video", "enhance", "upscale"],
        )
        
        self.register_tool(
            name="video.trim",
            description="Trim video to specified time range",
            input_schema={
                "type": "object",
                "properties": {
                    "video_path": {"type": "string", "description": "Path to video file"},
                    "start_time": {"type": "number", "description": "Start time in seconds"},
                    "end_time": {"type": "number", "description": "End time in seconds"},
                },
                "required": ["video_path", "start_time", "end_time"],
            },
            handler=video_svc.trim_video,
            category="video",
            tags=["video", "trim", "edit"],
        )
        
        # Model Management Tools
        self.register_tool(
            name="model.load",
            description="Load an AI model into memory",
            input_schema={
                "type": "object",
                "properties": {
                    "model_name": {"type": "string", "description": "Model name or path"},
                    "model_type": {"type": "string", "description": "Model type", "default": "checkpoint"},
                },
                "required": ["model_name"],
            },
            handler=ai_svc.load_model,
            category="model_management",
            tags=["model", "load", "ai"],
        )
        
        self.register_tool(
            name="model.unload",
            description="Unload an AI model from memory",
            input_schema={
                "type": "object",
                "properties": {
                    "model_name": {"type": "string", "description": "Model name or path"},
                    "model_type": {"type": "string", "description": "Model type", "default": "checkpoint"},
                },
                "required": ["model_name"],
            },
            handler=ai_svc.unload_model,
            category="model_management",
            tags=["model", "unload", "ai"],
        )
        
        # Device/System Tools
        self.register_tool(
            name="system.info",
            description="Get device and system information",
            input_schema={
                "type": "object",
            },
            handler=self._get_system_info_wrapper,
            category="system",
            tags=["system", "info", "device"],
        )
        
        self.register_tool(
            name="system.optimal_settings",
            description="Get optimal settings for current device",
            input_schema={
                "type": "object",
            },
            handler=lambda: device_service.get_optimal_settings(),
            category="system",
            tags=["system", "settings", "optimization"],
        )
    
    def _setup_filter_tools(self) -> None:
        """Setup filter-related tools."""
        from app.services.filter_service import FilterService
        filter_svc = FilterService()
        
        self.register_tool(
            name="image.apply_filter",
            description="Apply a filter to an image",
            input_schema={
                "type": "object",
                "properties": {
                    "image": {"type": "string", "description": "Base64 encoded image"},
                    "filter_name": {"type": "string", "description": "Filter name to apply"},
                    "intensity": {"type": "number", "description": "Filter intensity (0-1)", "default": 1.0},
                },
                "required": ["image", "filter_name"],
            },
            handler=self._apply_filter_wrapper,
            category="image_filters",
            tags=["filter", "image", "process"],
        )
        
        self.register_tool(
            name="image.list_filters",
            description="List available image filters",
            input_schema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter category"},
                },
            },
            handler=self._list_filters_wrapper,
            category="image_filters",
            tags=["filter", "list", "image"],
        )
        
        # Workspace Tools
        self.register_tool(
            name="workspace.list_outputs",
            description="List output files",
            input_schema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of files", "default": 50},
                },
            },
            handler=self._list_outputs_wrapper,
            category="workspace",
            tags=["workspace", "files", "outputs"],
        )
        
        self.register_tool(
            name="workspace.get_file",
            description="Get file content or information",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "encode": {"type": "boolean", "description": "Encode as base64", "default": False},
                },
                "required": ["path"],
            },
            handler=self._get_file_wrapper,
            category="workspace",
            tags=["workspace", "file", "read"],
        )
    
    async def _apply_filter_wrapper(self, **kwargs) -> dict:
        """Wrapper for filter application."""
        from PIL import Image
        import base64
        import io
        from app.services.filter_service import filter_service
        
        image_data = kwargs.pop("image", None)
        filter_name = kwargs.pop("filter_name")
        intensity = kwargs.pop("intensity", 1.0)
        
        if image_data:
            # Decode image
            if isinstance(image_data, str) and image_data.startswith("data:"):
                image_data = image_data.split(",")[1]
            
            img_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(img_bytes))
            
            result = await filter_service.save_filtered_image(img, filter_name, intensity)
            return result
        
        return {"error": "No image provided"}
    
    async def _list_filters_wrapper(self, **kwargs) -> dict:
        """Wrapper for listing filters."""
        from app.services.filter_service import filter_service
        
        category = kwargs.get("category")
        
        if category:
            filters = filter_service.get_filters_by_category(category)
        else:
            filters = filter_service.get_all_filters()
        
        return {"filters": filters}
    
    async def _get_system_info_wrapper(self, **kwargs) -> dict:
        """Wrapper for system info."""
        from app.services.device_service import device_service
        return device_service.info.model_dump()
    
    async def _list_outputs_wrapper(self, **kwargs) -> dict:
        """Wrapper for listing outputs."""
        from pathlib import Path
        
        limit = kwargs.get("limit", 50)
        output_dir = Path(settings.OUTPUTS_DIR)
        
        files = sorted(output_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
        
        return {
            "files": [
                {
                    "name": f.name,
                    "path": str(f),
                    "size": f.stat().st_size,
                    "modified": f.stat().st_mtime,
                }
                for f in files
            ]
        }
    
    async def _get_file_wrapper(self, **kwargs) -> dict:
        """Wrapper for getting file content."""
        import base64
        from pathlib import Path
        
        path = kwargs.get("path")
        encode = kwargs.get("encode", False)
        
        file_path = Path(path)
        if not file_path.exists():
            return {"error": f"File not found: {path}"}
        
        if encode:
            with open(file_path, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf-8")
            return {"path": str(file_path), "content": content, "encoded": True}
        
        return {
            "path": str(file_path),
            "size": file_path.stat().st_size,
            "modified": file_path.stat().st_mtime,
        }
    
    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict,
        handler: Callable,
        category: str = "general",
        tags: list[str] | None = None,
    ) -> None:
        """Register a new tool."""
        tool = MCPTool(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler,
            category=category,
            tags=tags,
        )
        self._tools[name] = tool
    
    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool."""
        if name in self._tools:
            del self._tools[name]
            return True
        return False
    
    def get_tool(self, name: str) -> MCPTool | None:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(
        self,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> list[dict]:
        """List all registered tools."""
        tools = list(self._tools.values())
        
        if category:
            tools = [t for t in tools if t.category == category]
        
        if tags:
            tools = [t for t in tools if any(tag in t.tags for tag in tags)]
        
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
                "category": t.category,
                "tags": t.tags,
                "usage_count": t.usage_count,
            }
            for t in tools
        ]
    
    async def execute_tool(
        self,
        name: str,
        arguments: dict,
    ) -> dict:
        """Execute a tool with given arguments."""
        tool = self._tools.get(name)
        
        if not tool:
            return {"error": f"Tool not found: {name}"}
        
        try:
            # Validate arguments against schema
            # In production, use JSON Schema validation
            
            # Execute handler
            result = tool.handler(**arguments)
            
            # Handle coroutines
            if asyncio.iscoroutine(result):
                result = await result
            
            # Update usage stats
            tool.usage_count += 1
            
            return {
                "success": True,
                "result": result,
                "tool": name,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool": name,
            }
    
    def subscribe(self, tool_name: str, callback: Callable) -> None:
        """Subscribe to tool execution events."""
        if tool_name not in self._subscribers:
            self._subscribers[tool_name] = []
        self._subscribers[tool_name].append(callback)
    
    def unsubscribe(self, tool_name: str, callback: Callable) -> None:
        """Unsubscribe from tool execution events."""
        if tool_name in self._subscribers:
            self._subscribers[tool_name].remove(callback)


# Global instance
mcp_server = MCPServer()


# MCP Protocol Handlers
async def handle_mcp_request(request: dict) -> dict:
    """Handle incoming MCP request."""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")
    
    if method == "tools/list":
        result = mcp_server.list_tools(
            category=params.get("category"),
            tags=params.get("tags"),
        )
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    
    elif method == "tools/execute":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        result = await mcp_server.execute_tool(tool_name, arguments)
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    
    elif method == "tools/get":
        tool = mcp_server.get_tool(params.get("name"))
        if tool:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                },
            }
        return {"jsonrpc": "2.0", "id": request_id, "error": "Tool not found"}
    
    elif method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": [
                    {
                        "uri": f"dolphinphoto://outputs",
                        "name": "Outputs Directory",
                        "description": "Generated images and videos",
                    },
                    {
                        "uri": f"dolphinphoto://models",
                        "name": "Models Directory",
                        "description": "AI models",
                    },
                    {
                        "uri": f"dolphinphoto://workspace",
                        "name": "Workspace",
                        "description": "Current workspace",
                    },
                ]
            },
        }
    
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"status": "ok"}}
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
