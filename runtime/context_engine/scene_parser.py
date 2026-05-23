
"""Godot scene file (.tscn) parser for NeoGodot."""

import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any

from .types import (
    SceneStructure,
    SceneNode,
    SignalConnection,
    ExternalResource,
)


class SceneParser:
    """Parser for Godot .tscn scene files."""

    def __init__(self):
        # Patterns for different section headers
        self.section_patterns = {
            "gd_scene": re.compile(r'^\[gd_scene\s*(.*)\]'),
            "ext_resource": re.compile(r'^\[ext_resource\s+(.+)\]'),
            "sub_resource": re.compile(r'^\[sub_resource\s+(.+)\]'),
            "node": re.compile(r'^\[node\s+(.+)\]'),
            "connection": re.compile(r'^\[connection\s+(.+)\]'),
        }
        # Pattern for key-value pairs in sections
        self.param_pattern = re.compile(r'(\w+)=(?:"([^"]+)"|([^\s]+))')

    def parse_scene(self, scene_path: Path) -&gt; SceneStructure:
        """Parse a .tscn scene file.
        
        Args:
            scene_path: Path to .tscn file
            
        Returns:
            SceneStructure with node tree and connections
        """
        content = scene_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        structure = SceneStructure(
            scene_path=str(scene_path),
            scene_hash=self._compute_hash(content),
        )
        
        current_node: Optional[SceneNode] = None
        node_stack: List[SceneNode] = []
        node_map: Dict[str, SceneNode] = {}
        current_properties: Dict[str, Any] = {}
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith(";"):
                continue
            
            if line.startswith("["):
                # Process previous node's properties
                if current_node:
                    current_node.properties.update(current_properties)
                    current_properties = {}
                
                # Parse section
                if match := self.section_patterns["ext_resource"].match(line):
                    resource = self._parse_ext_resource(match.group(1))
                    structure.external_resources.append(resource)
                elif match := self.section_patterns["sub_resource"].match(line):
                    pass  # Sub-resources can be handled later if needed
                elif match := self.section_patterns["node"].match(line):
                    node = self._parse_node(match.group(1), line_num)
                    structure.all_nodes.append(node)
                    node_map[node.node_path] = node
                    
                    # Build node tree
                    if node.parent_path:
                        if node.parent_path in node_map:
                            node_map[node.parent_path].children.append(node)
                    else:
                        structure.root_node = node
                    
                    current_node = node
                elif match := self.section_patterns["connection"].match(line):
                    connection = self._parse_connection(match.group(1))
                    structure.signal_connections.append(connection)
            elif current_node:
                # Collect properties for current node
                if "=" in line:
                    key, value = self._parse_property(line)
                    if key:
                        current_properties[key] = value
        
        # Process last node's properties
        if current_node:
            current_node.properties.update(current_properties)
        
        structure.node_count = len(structure.all_nodes)
        
        # Build script bindings
        for node in structure.all_nodes:
            if node.script_path:
                structure.script_bindings[node.node_path] = node.script_path
        
        return structure

    def _parse_ext_resource(self, params_str: str) -&gt; ExternalResource:
        """Parse ext_resource section parameters."""
        params = self._parse_params(params_str)
        return ExternalResource(
            resource_id=params.get("id", ""),
            resource_type=params.get("type", ""),
            resource_path=params.get("path", ""),
        )

    def _parse_node(self, params_str: str, line_num: int) -&gt; SceneNode:
        """Parse node section parameters."""
        params = self._parse_params(params_str)
        
        node_name = params.get("name", f"Node_{line_num}")
        node_type = params.get("type", "Node")
        parent_path = params.get("parent", "")
        
        if parent_path:
            node_path = f"{parent_path}/{node_name}"
        else:
            node_path = node_name
        
        script_path = params.get("script", None)
        
        return SceneNode(
            node_path=node_path,
            node_type=node_type,
            node_name=node_name,
            parent_path=parent_path if parent_path else None,
            properties={},
            script_path=script_path,
        )

    def _parse_connection(self, params_str: str) -&gt; SignalConnection:
        """Parse connection section parameters."""
        params = self._parse_params(params_str)
        flags_str = params.get("flags", "")
        flags = flags_str.split(",") if flags_str else []
        
        return SignalConnection(
            signal_name=params.get("signal", ""),
            source_node=params.get("from", ""),
            target_node=params.get("to", ""),
            target_method=params.get("method", ""),
            flags=flags,
        )

    def _parse_params(self, params_str: str) -&gt; Dict[str, str]:
        """Parse key=value parameters from section header."""
        params = {}
        for match in self.param_pattern.finditer(params_str):
            key = match.group(1)
            value = match.group(2) if match.group(2) else match.group(3)
            params[key] = value
        return params

    def _parse_property(self, line: str) -&gt; tuple[Optional[str], Any]:
        """Parse a single property line."""
        if "=" not in line:
            return None, None
        key_part, value_part = line.split("=", 1)
        key = key_part.strip()
        value = self._parse_value(value_part.strip())
        return key, value

    def _parse_value(self, value_str: str) -&gt; Any:
        """Parse a value string to appropriate type."""
        # Handle quoted strings
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        # Handle booleans
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False
        # Handle null
        if value_str.lower() == "null" or value_str.lower() == "nil":
            return None
        # Handle integers
        if value_str.isdigit() or (value_str.startswith("-") and value_str[1:].isdigit()):
            try:
                return int(value_str)
            except ValueError:
                pass
        # Handle floats
        try:
            if "." in value_str or "e" in value_str.lower():
                return float(value_str)
        except ValueError:
            pass
        # Default to string
        return value_str

    def _compute_hash(self, content: str) -&gt; str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()

