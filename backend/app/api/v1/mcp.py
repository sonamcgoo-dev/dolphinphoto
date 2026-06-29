"""
DolphinPhoto AI Studio - MCP API
MCP tool registry and execution endpoints
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.mcp.server import mcp_server

router = APIRouter(prefix="/mcp", tags=["mcp"])


class ToolExecuteRequest(BaseModel):
    name: str = Field(..., description="Tool name")
    arguments: dict = Field(default_factory=dict, description="Tool arguments")


class ToolListRequest(BaseModel):
    category: str | None = Field(None, description="Filter by category")
    tags: list[str] | None = Field(None, description="Filter by tags")


@router.get("/tools", response_model=dict)
async def list_tools(
    category: str | None = None,
    tags: str | None = None,
) -> dict:
    """List all available MCP tools."""
    tag_list = tags.split(",") if tags else None
    
    tools = mcp_server.list_tools(
        category=category,
        tags=tag_list,
    )
    
    return {
        "success": True,
        "tools": tools,
        "count": len(tools),
    }


@router.get("/tools/{tool_name}", response_model=dict)
async def get_tool(tool_name: str) -> dict:
    """Get details about a specific tool."""
    tool = mcp_server.get_tool(tool_name)
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return {
        "success": True,
        "tool": {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
            "category": tool.category,
            "tags": tool.tags,
            "usage_count": tool.usage_count,
        },
    }


@router.post("/tools/execute", response_model=dict)
async def execute_tool(request: ToolExecuteRequest) -> dict:
    """Execute an MCP tool."""
    try:
        result = await mcp_server.execute_tool(
            name=request.name,
            arguments=request.arguments,
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=dict)
async def get_categories() -> dict:
    """Get all tool categories."""
    tools = mcp_server.list_tools()
    
    categories = {}
    for tool in tools:
        cat = tool.get("category", "general")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(tool)
    
    return {
        "success": True,
        "categories": {
            cat: len(tools) for cat, tools in categories.items()
        },
    }


@router.get("/resources", response_model=dict)
async def get_resources() -> dict:
    """Get available MCP resources."""
    return {
        "success": True,
        "resources": [
            {
                "uri": "dolphinphoto://outputs",
                "name": "Outputs Directory",
                "description": "Generated images and videos",
            },
            {
                "uri": "dolphinphoto://models",
                "name": "Models Directory",
                "description": "AI models storage",
            },
            {
                "uri": "dolphinphoto://workspace",
                "name": "Workspace",
                "description": "Current workspace root",
            },
            {
                "uri": "dolphinphoto://temp",
                "name": "Temp Directory",
                "description": "Temporary files",
            },
        ],
    }
