"""A module to handle plugins for this package."""

# In general, plugins can be implemented by a package introducing
# an `entry-points` in the `pyproject.toml` file. This package
# expects the namespace to be `pydicomsorter.plugins`.

from importlib.metadata import EntryPoints, entry_points
from typing import Any, Dict, List

discovered_plugins: EntryPoints = entry_points(group="pydicomsorter.plugins")

def get_plugins() -> Dict[str, Any]:
    """Get all available plugins."""
    return {plugin.name: plugin for plugin in discovered_plugins}

def list_plugins() -> List[str]:
    """List all available plugins."""
    return [plugin.name for plugin in discovered_plugins]
