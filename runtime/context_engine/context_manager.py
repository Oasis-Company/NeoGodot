
"""Context manager for NeoGodot project indexing and querying."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from .types import (
    ProjectContext,
    ProjectStats,
    CodeStructure,
    SceneStructure,
    ResourceInfo,
    FileChangeEvent,
    ChangeType,
    RetrievedItem,
)
from .gdscript_parser import GDScriptParser
from .scene_parser import SceneParser
from .resource_indexer import ResourceIndexer
from .vector_store import VectorStore


class ContextManager:
    """Manages project context building and incremental updates."""

    SUPPORTED_CODE_EXTENSIONS = {".gd"}
    SUPPORTED_SCENE_EXTENSIONS = {".tscn", ".scn"}

    def __init__(self, vector_store_path: Optional[str] = None):
        """Initialize ContextManager.
        
        Args:
            vector_store_path: Path to persist vector store data
        """
        self.code_parser = GDScriptParser()
        self.scene_parser = SceneParser()
        self.resource_indexer = ResourceIndexer()
        self.vector_store = VectorStore(persist_directory=vector_store_path)
        
        self._project_contexts: Dict[str, ProjectContext] = {}

    async def build_project_context(self, project_path: Path) -&gt; ProjectContext:
        """Build complete project context.
        
        Args:
            project_path: Path to Godot project root
            
        Returns:
            Complete ProjectContext object
        """
        context = ProjectContext(
            project_path=str(project_path),
            project_name=project_path.name,
        )
        
        # Scan project
        files = self._scan_project(project_path)
        
        # Parse code files
        for file_path in files["code"]:
            try:
                structure = self.code_parser.parse_file(file_path)
                context.code_structures[str(file_path)] = structure
                
                # Add to symbol index
                for symbol in structure.symbols:
                    if symbol.name not in context.symbol_index:
                        context.symbol_index[symbol.name] = []
                    context.symbol_index[symbol.name].append(symbol)
            except Exception as e:
                print(f"Error parsing code file {file_path}: {e}")
        
        # Parse scene files
        for file_path in files["scene"]:
            try:
                structure = self.scene_parser.parse_scene(file_path)
                context.scene_structures[str(file_path)] = structure
            except Exception as e:
                print(f"Error parsing scene file {file_path}: {e}")
        
        # Index resources
        context.resource_index = self.resource_indexer.index_directory(project_path)
        
        # Build vector index
        await self._build_vector_index(context)
        
        # Update stats
        context.stats = self._compute_stats(context)
        context.is_fully_indexed = True
        context.last_updated = datetime.now()
        
        # Cache context
        self._project_contexts[str(project_path)] = context
        
        return context

    def _scan_project(self, project_path: Path) -&gt; Dict[str, List[Path]]:
        """Scan project directory and categorize files.
        
        Args:
            project_path: Project root directory
            
        Returns:
            Dictionary with categorized file paths
        """
        files: Dict[str, List[Path]] = {
            "code": [],
            "scene": [],
            "resource": [],
        }
        
        for file_path in project_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            # Skip hidden files and directories
            if any(part.startswith(".") for part in file_path.parts):
                continue
            
            ext = file_path.suffix.lower()
            
            if ext in self.SUPPORTED_CODE_EXTENSIONS:
                files["code"].append(file_path)
            elif ext in self.SUPPORTED_SCENE_EXTENSIONS:
                files["scene"].append(file_path)
            else:
                files["resource"].append(file_path)
        
        return files

    async def _build_vector_index(self, context: ProjectContext):
        """Build vector index from code chunks.
        
        Args:
            context: Project context to build index for
        """
        all_chunks = []
        for code_structure in context.code_structures.values():
            all_chunks.extend(code_structure.chunks)
        
        if all_chunks:
            self.vector_store.add_documents(all_chunks)

    async def update_context(
        self,
        project_path: Path,
        change: FileChangeEvent,
    ):
        """Incrementally update context for file changes.
        
        Args:
            project_path: Project root path
            change: File change event to process
        """
        context = self._project_contexts.get(str(project_path))
        if not context:
            return
        
        file_path = Path(change.file_path)
        ext = file_path.suffix.lower()
        
        if change.change_type == ChangeType.DELETED:
            await self._handle_file_deleted(file_path, ext, context)
        elif change.change_type in (ChangeType.CREATED, ChangeType.MODIFIED):
            await self._handle_file_changed(file_path, ext, context)
        
        context.last_updated = change.timestamp

    async def _handle_file_deleted(
        self,
        file_path: Path,
        ext: str,
        context: ProjectContext,
    ):
        """Handle file deletion.
        
        Args:
            file_path: Path of deleted file
            ext: File extension
            context: Project context to update
        """
        str_path = str(file_path)
        
        if ext in self.SUPPORTED_CODE_EXTENSIONS:
            if str_path in context.code_structures:
                # Remove from symbol index
                structure = context.code_structures[str_path]
                for symbol in structure.symbols:
                    if symbol.name in context.symbol_index:
                        filtered = [
                            s for s in context.symbol_index[symbol.name]
                            if s.location.file_path != str_path
                        ]
                        if filtered:
                            context.symbol_index[symbol.name] = filtered
                        else:
                            del context.symbol_index[symbol.name]
                
                # Remove from vector store
                self.vector_store.delete_by_file_path(str_path)
                
                # Remove from code structures
                del context.code_structures[str_path]
        
        elif ext in self.SUPPORTED_SCENE_EXTENSIONS:
            if str_path in context.scene_structures:
                del context.scene_structures[str_path]
        
        elif str_path in context.resource_index:
            del context.resource_index[str_path]

    async def _handle_file_changed(
        self,
        file_path: Path,
        ext: str,
        context: ProjectContext,
    ):
        """Handle file creation or modification.
        
        Args:
            file_path: Path of changed file
            ext: File extension
            context: Project context to update
        """
        if not file_path.exists():
            return
        
        str_path = str(file_path)
        
        if ext in self.SUPPORTED_CODE_EXTENSIONS:
            try:
                # Remove old from vector store if exists
                if str_path in context.code_structures:
                    self.vector_store.delete_by_file_path(str_path)
                
                # Parse new
                structure = self.code_parser.parse_file(file_path)
                context.code_structures[str_path] = structure
                
                # Update symbol index
                for symbol in structure.symbols:
                    if symbol.name not in context.symbol_index:
                        context.symbol_index[symbol.name] = []
                    # Remove old entries for this file
                    filtered = [
                        s for s in context.symbol_index[symbol.name]
                        if s.location.file_path != str_path
                    ]
                    filtered.append(symbol)
                    context.symbol_index[symbol.name] = filtered
                
                # Add new chunks to vector store
                self.vector_store.add_documents(structure.chunks)
            except Exception as e:
                print(f"Error updating code file {file_path}: {e}")
        
        elif ext in self.SUPPORTED_SCENE_EXTENSIONS:
            try:
                structure = self.scene_parser.parse_scene(file_path)
                context.scene_structures[str_path] = structure
            except Exception as e:
                print(f"Error updating scene file {file_path}: {e}")
        
        else:
            try:
                info = self.resource_indexer.index_file(file_path)
                context.resource_index[str_path] = info
            except Exception as e:
                print(f"Error indexing resource file {file_path}: {e}")

    def _compute_stats(self, context: ProjectContext) -&gt; ProjectStats:
        """Compute project statistics.
        
        Args:
            context: Project context to compute stats for
            
        Returns:
            ProjectStats object
        """
        total_lines = sum(
            cs.total_lines
            for cs in context.code_structures.values()
        )
        
        total_symbols = sum(
            len(cs.symbols)
            for cs in context.code_structures.values()
        )
        
        return ProjectStats(
            total_files=(
                len(context.code_structures) +
                len(context.scene_structures) +
                len(context.resource_index)
            ),
            total_code_files=len(context.code_structures),
            total_scene_files=len(context.scene_structures),
            total_resources=len(context.resource_index),
            total_symbols=total_symbols,
            total_lines_of_code=total_lines,
            indexed_at=datetime.now(),
        )

    async def get_relevant_context(
        self,
        project_path: Path,
        query: str,
        context_type: Optional[str] = None,
        limit: int = 10,
    ) -&gt; List[RetrievedItem]:
        """Get context relevant to query.
        
        Args:
            project_path: Project root path
            query: Search query
            context_type: Type of context to search (code/scene/resource)
            limit: Maximum number of results to return
            
        Returns:
            List of relevant RetrievedItem objects
        """
        collection = "code_chunks"
        if context_type == "scene":
            collection = "scene_chunks"  # Not implemented yet
        elif context_type == "resource":
            collection = "resource_chunks"  # Not implemented yet
        
        results = self.vector_store.search(
            query=query,
            collection_name=collection,
            n_results=limit,
        )
        
        return results

    def get_cached_context(self, project_path: Path) -&gt; Optional[ProjectContext]:
        """Get cached project context if available.
        
        Args:
            project_path: Project root path
            
        Returns:
            Cached ProjectContext or None
        """
        return self._project_contexts.get(str(project_path))

    def clear_cache(self, project_path: Optional[Path] = None):
        """Clear cached contexts.
        
        Args:
            project_path: Specific project to clear, or None for all
        """
        if project_path:
            str_path = str(project_path)
            if str_path in self._project_contexts:
                del self._project_contexts[str_path]
        else:
            self._project_contexts.clear()

