
"""Resource file indexer for NeoGodot."""

import os
from pathlib import Path
from typing import Dict, List, Any

from .types import ResourceInfo


class ResourceIndexer:
    """Indexes resource files and generates ResourceInfo objects."""

    # File extension to resource type mapping
    RESOURCE_TYPES = {
        # Images
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
        ".bmp": "image",
        ".tga": "image",
        ".webp": "image",
        ".svg": "image",
        ".psd": "image",
        # Audio
        ".wav": "audio",
        ".mp3": "audio",
        ".ogg": "audio",
        ".flac": "audio",
        ".m4a": "audio",
        # 3D Models
        ".obj": "model",
        ".fbx": "model",
        ".gltf": "model",
        ".glb": "model",
        ".dae": "model",
        ".blend": "model",
        # Video
        ".mp4": "video",
        ".webm": "video",
        ".mkv": "video",
        ".avi": "video",
        # Fonts
        ".ttf": "font",
        ".otf": "font",
        ".woff": "font",
        ".woff2": "font",
        # Godot-specific resources
        ".tres": "godot_resource",
        ".tscn": "scene",
        ".gd": "script",
        ".shader": "shader",
        ".material": "material",
        ".tex": "texture",
        # Data
        ".json": "data",
        ".csv": "data",
        ".xml": "data",
        ".toml": "data",
        ".yaml": "data",
        ".yml": "data",
    }

    def __init__(self):
        pass

    def index_file(self, file_path: Path) -&gt; ResourceInfo:
        """Index a single resource file.
        
        Args:
            file_path: Path to resource file
            
        Returns:
            ResourceInfo object
        """
        ext = file_path.suffix.lower()
        resource_type = self.RESOURCE_TYPES.get(ext, "unknown")
        
        file_size = 0
        try:
            file_size = file_path.stat().st_size
        except (OSError, FileNotFoundError):
            pass
        
        return ResourceInfo(
            resource_path=str(file_path),
            resource_type=resource_type,
            file_size=file_size,
            format=ext.lstrip("."),
            metadata=self._extract_metadata(file_path, resource_type),
        )

    def index_directory(
        self,
        dir_path: Path,
        recursive: bool = True,
    ) -&gt; Dict[str, ResourceInfo]:
        """Index all resource files in a directory.
        
        Args:
            dir_path: Directory to index
            recursive: Whether to recurse into subdirectories
            
        Returns:
            Dictionary mapping file paths to ResourceInfo objects
        """
        resources: Dict[str, ResourceInfo] = {}
        
        if not dir_path.exists() or not dir_path.is_dir():
            return resources
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                info = self.index_file(file_path)
                resources[str(file_path)] = info
        
        return resources

    def _extract_metadata(self, file_path: Path, resource_type: str) -&gt; Dict[str, Any]:
        """Extract metadata from resource file.
        
        This is a basic implementation. In a real-world scenario, you might want
        to use specialized libraries for different file types.
        """
        metadata: Dict[str, Any] = {}
        
        # Add basic file info
        metadata["file_name"] = file_path.name
        metadata["file_stem"] = file_path.stem
        metadata["parent_dir"] = str(file_path.parent)
        
        # Try to get file timestamps
        try:
            stat = file_path.stat()
            metadata["created"] = stat.st_ctime
            metadata["modified"] = stat.st_mtime
        except (OSError, FileNotFoundError):
            pass
        
        # Type-specific metadata (placeholder for now)
        if resource_type == "image":
            metadata["supports_alpha"] = file_path.suffix.lower() in [".png", ".tga", ".webp"]
        elif resource_type == "audio":
            pass
        elif resource_type == "model":
            pass
        
        return metadata

    def get_resources_by_type(
        self,
        resources: Dict[str, ResourceInfo],
        resource_type: str,
    ) -&gt; List[ResourceInfo]:
        """Filter resources by type.
        
        Args:
            resources: Dictionary of resources
            resource_type: Type to filter by
            
        Returns:
            List of ResourceInfo objects of the specified type
        """
        return [
            info for info in resources.values()
            if info.resource_type == resource_type
        ]

    def get_supported_extensions(self) -&gt; List[str]:
        """Get list of supported file extensions.
        
        Returns:
            List of supported extensions (including leading dot)
        """
        return list(self.RESOURCE_TYPES.keys())

