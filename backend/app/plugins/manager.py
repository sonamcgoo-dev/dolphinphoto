"""
DolphinPhoto AI Studio - Plugin Manager
Plugin discovery, loading, and lifecycle management
"""
from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


class Plugin:
    """Base plugin class."""
    
    name: str = "base_plugin"
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    
    def on_load(self) -> None:
        """Called when plugin is loaded."""
        pass
    
    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        pass
    
    def on_startup(self) -> None:
        """Called on application startup."""
        pass
    
    def on_shutdown(self) -> None:
        """Called on application shutdown."""
        pass
    
    def get_tools(self) -> list[dict]:
        """Get MCP tools provided by this plugin."""
        return []
    
    def get_routes(self) -> list[Any]:
        """Get FastAPI routes provided by this plugin."""
        return []


class PluginManager:
    """Manages plugin discovery, loading, and lifecycle."""
    
    def __init__(self):
        self._plugins: dict[str, Plugin] = {}
        self._hooks: dict[str, list[Callable]] = {
            "startup": [],
            "shutdown": [],
            "tool_call": [],
        }
    
    def discover_and_load(self, plugins_dir: Path) -> list[str]:
        """Discover and load plugins from directory."""
        loaded = []
        
        if not plugins_dir.exists():
            plugins_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created plugins directory: {plugins_dir}")
            return loaded
        
        # Import built-in plugins
        self._load_builtin_plugins()
        
        # Discover external plugins
        for plugin_file in plugins_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
            
            try:
                # Import plugin module
                module_name = f"plugins.{plugin_file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, plugin_file)
                
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find plugin class
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, Plugin)
                            and attr is not Plugin
                        ):
                            self.load_plugin(attr())
                            loaded.append(attr_name)
                            break
            
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_file}: {e}")
        
        # Register hooks from all plugins
        for plugin in self._plugins.values():
            try:
                plugin.on_load()
            except Exception as e:
                logger.error(f"Plugin {plugin.name} on_load failed: {e}")
        
        logger.info(f"Loaded {len(loaded)} external plugins")
        return loaded
    
    def _load_builtin_plugins(self) -> None:
        """Load built-in plugins."""
        # Built-in plugins can be added here
        pass
    
    def load_plugin(self, plugin: Plugin) -> bool:
        """Load a plugin instance."""
        if plugin.name in self._plugins:
            logger.warning(f"Plugin already loaded: {plugin.name}")
            return False
        
        self._plugins[plugin.name] = plugin
        logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
        
        # Register plugin tools
        for tool in plugin.get_tools():
            from app.mcp.server import mcp_server
            mcp_server.register_tool(**tool)
        
        return True
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin."""
        if name not in self._plugins:
            return False
        
        plugin = self._plugins[name]
        
        try:
            plugin.on_unload()
        except Exception as e:
            logger.error(f"Plugin {name} on_unload failed: {e}")
        
        del self._plugins[name]
        logger.info(f"Unloaded plugin: {name}")
        return True
    
    def all(self) -> list[Plugin]:
        """Get all loaded plugins."""
        return list(self._plugins.values())
    
    def get(self, name: str) -> Plugin | None:
        """Get a plugin by name."""
        return self._plugins.get(name)
    
    def register_hook(self, event: str, callback: Callable) -> None:
        """Register a lifecycle hook."""
        if event in self._hooks:
            self._hooks[event].append(callback)
    
    def trigger_hook(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Trigger a lifecycle hook."""
        if event in self._hooks:
            for callback in self._hooks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Hook {event} failed: {e}")


# Global instance
plugin_manager = PluginManager()
