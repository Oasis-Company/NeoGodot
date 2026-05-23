
"""Regex-based GDScript parser for NeoGodot."""

import re
import hashlib
from pathlib import Path
from typing import List, Optional, Tuple

from .types import (
    CodeStructure,
    CodeChunk,
    SymbolInfo,
    SymbolKind,
    AccessModifier,
    SourceLocation,
    DependencyInfo,
)


class GDScriptParser:
    """Regex-based GDScript parser to extract symbols, chunks, and structure."""

    def __init__(self):
        self.patterns = {
            "class_name": re.compile(r'^class_name\s+(\w+)(?:\s+extends\s+(\w+))?', re.MULTILINE),
            "extends": re.compile(r'^extends\s+([\w\.]+(?:\s*\.\s*[\w\.]+)*)', re.MULTILINE),
            "func": re.compile(
                r'^(?:static\s+)?func\s+(\w+)\s*\(([\s\S]*?)\)\s*(?:-&gt;\s*([\w\[\]]+))?',
                re.MULTILINE
            ),
            "var": re.compile(r'^var\s+(\w+)(?::\s*([\w\[\]]+))?(?:\s*=\s*([^\n]+))?', re.MULTILINE),
            "signal": re.compile(r'^signal\s+(\w+)\s*\(([\s\S]*?)\)', re.MULTILINE),
            "enum": re.compile(r'^enum\s+(\w+)?\s*\{([\s\S]*?)\}', re.MULTILINE),
            "const": re.compile(r'^const\s+(\w+)(?::\s*([\w\[\]]+))?(?:\s*=\s*([^\n]+))?', re.MULTILINE),
            "preload": re.compile(r'(?:var|const)\s+\w+\s*=\s*preload\s*\(\s*"([^"]+)"\s*\)', re.MULTILINE),
        }

    def parse_file(self, file_path: Path) -&gt; CodeStructure:
        """Parse a GDScript file and return its structure.
        
        Args:
            file_path: Path to .gd file
            
        Returns:
            CodeStructure with symbols, chunks, and dependencies
        """
        source_code = file_path.read_text(encoding="utf-8")
        lines = source_code.splitlines()
        
        structure = CodeStructure(
            file_path=str(file_path),
            source_code=source_code,
            total_lines=len(lines),
            file_hash=self._compute_hash(source_code),
        )
        
        # Extract basic class info
        structure.class_name = self._extract_class_name(source_code)
        structure.extends = self._extract_extends(source_code)
        structure.imports = self._extract_imports(source_code)
        
        # Extract symbols
        structure.symbols = self._extract_symbols(source_code, str(file_path), lines)
        
        # Extract dependencies
        structure.dependencies = self._extract_dependencies(source_code, structure)
        
        # Generate semantic chunks
        structure.chunks = self._generate_chunks(source_code, str(file_path), lines)
        
        return structure

    def _compute_hash(self, content: str) -&gt; str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def _extract_class_name(self, source: str) -&gt; Optional[str]:
        """Extract class_name declaration."""
        match = self.patterns["class_name"].search(source)
        if match:
            return match.group(1)
        return None

    def _extract_extends(self, source: str) -&gt; Optional[str]:
        """Extract extends declaration."""
        # First check class_name line for extends
        class_match = self.patterns["class_name"].search(source)
        if class_match and class_match.group(2):
            return class_match.group(2)
        
        # Then check standalone extends
        match = self.patterns["extends"].search(source)
        if match:
            return match.group(1)
        return None

    def _extract_imports(self, source: str) -&gt; List[str]:
        """Extract all preload paths as imports."""
        imports = []
        for match in self.patterns["preload"].finditer(source):
            imports.append(match.group(1))
        return imports

    def _extract_symbols(self, source: str, file_path: str, lines: List[str]) -&gt; List[SymbolInfo]:
        """Extract all symbols from source code."""
        symbols = []
        
        # Find line numbers for symbols
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            # Check for function
            func_match = self.patterns["func"].search(line)
            if func_match:
                symbol = self._create_func_symbol(func_match, file_path, line_num, source)
                symbols.append(symbol)
                continue
            
            # Check for variable
            var_match = self.patterns["var"].search(line)
            if var_match:
                symbol = self._create_var_symbol(var_match, file_path, line_num)
                symbols.append(symbol)
                continue
            
            # Check for signal
            signal_match = self.patterns["signal"].search(line)
            if signal_match:
                symbol = self._create_signal_symbol(signal_match, file_path, line_num)
                symbols.append(symbol)
                continue
            
            # Check for const
            const_match = self.patterns["const"].search(line)
            if const_match:
                symbol = self._create_const_symbol(const_match, file_path, line_num)
                symbols.append(symbol)
                continue
        
        # Handle enums (multi-line)
        enum_matches = list(self.patterns["enum"].finditer(source))
        for enum_match in enum_matches:
            start_line = source.count("\n", 0, enum_match.start()) + 1
            symbol = self._create_enum_symbol(enum_match, file_path, start_line)
            symbols.append(symbol)
        
        return symbols

    def _create_func_symbol(
        self,
        match: re.Match,
        file_path: str,
        line_num: int,
        source: str,
    ) -&gt; SymbolInfo:
        """Create SymbolInfo for a function."""
        name = match.group(1)
        params = match.group(2) or ""
        return_type = match.group(3)
        
        access = AccessModifier.PRIVATE if name.startswith("_") else AccessModifier.PUBLIC
        signature = f"func {name}({params})"
        if return_type:
            signature += f" -&gt; {return_type}"
        
        return SymbolInfo(
            name=name,
            kind=SymbolKind.FUNCTION,
            access=access,
            location=SourceLocation(
                file_path=file_path,
                start_line=line_num,
                start_column=match.start(1) - len("func ") if "func " in source[match.start():match.end()] else 0,
                end_line=line_num,
                end_column=match.end(),
            ),
            signature=signature,
        )

    def _create_var_symbol(
        self,
        match: re.Match,
        file_path: str,
        line_num: int,
    ) -&gt; SymbolInfo:
        """Create SymbolInfo for a variable."""
        name = match.group(1)
        type_hint = match.group(2)
        default_value = match.group(3)
        
        access = AccessModifier.PRIVATE if name.startswith("_") else AccessModifier.PUBLIC
        
        return SymbolInfo(
            name=name,
            kind=SymbolKind.VARIABLE,
            access=access,
            location=SourceLocation(
                file_path=file_path,
                start_line=line_num,
                start_column=match.start(1) - len("var ") if "var " in match.string else 0,
                end_line=line_num,
                end_column=match.end(),
            ),
            type_hint=type_hint,
            default_value=default_value.strip() if default_value else None,
        )

    def _create_signal_symbol(
        self,
        match: re.Match,
        file_path: str,
        line_num: int,
    ) -&gt; SymbolInfo:
        """Create SymbolInfo for a signal."""
        name = match.group(1)
        params = match.group(2) or ""
        
        return SymbolInfo(
            name=name,
            kind=SymbolKind.SIGNAL,
            access=AccessModifier.PUBLIC,
            location=SourceLocation(
                file_path=file_path,
                start_line=line_num,
                start_column=match.start(1) - len("signal ") if "signal " in match.string else 0,
                end_line=line_num,
                end_column=match.end(),
            ),
            signature=f"signal {name}({params})",
        )

    def _create_enum_symbol(
        self,
        match: re.Match,
        file_path: str,
        line_num: int,
    ) -&gt; SymbolInfo:
        """Create SymbolInfo for an enum."""
        name = match.group(1) or "anonymous_enum"
        enum_body = match.group(2)
        
        end_line = line_num + enum_body.count("\n")
        
        return SymbolInfo(
            name=name,
            kind=SymbolKind.ENUM,
            access=AccessModifier.PUBLIC,
            location=SourceLocation(
                file_path=file_path,
                start_line=line_num,
                start_column=match.start(),
                end_line=end_line,
                end_column=match.end(),
            ),
        )

    def _create_const_symbol(
        self,
        match: re.Match,
        file_path: str,
        line_num: int,
    ) -&gt; SymbolInfo:
        """Create SymbolInfo for a constant."""
        name = match.group(1)
        type_hint = match.group(2)
        default_value = match.group(3)
        
        access = AccessModifier.PRIVATE if name.startswith("_") else AccessModifier.PUBLIC
        
        return SymbolInfo(
            name=name,
            kind=SymbolKind.CONSTANT,
            access=access,
            location=SourceLocation(
                file_path=file_path,
                start_line=line_num,
                start_column=match.start(1) - len("const ") if "const " in match.string else 0,
                end_line=line_num,
                end_column=match.end(),
            ),
            type_hint=type_hint,
            default_value=default_value.strip() if default_value else None,
        )

    def _extract_dependencies(
        self,
        source: str,
        structure: CodeStructure,
    ) -&gt; List[DependencyInfo]:
        """Extract code dependencies."""
        dependencies = []
        
        # Extends dependency
        if structure.extends:
            dependencies.append(DependencyInfo(
                source="self",
                target=structure.extends,
                dep_type="extends",
            ))
        
        # Preload dependencies
        for path in structure.imports:
            dependencies.append(DependencyInfo(
                source="self",
                target=path,
                dep_type="preload",
                target_file=path,
            ))
        
        return dependencies

    def _generate_chunks(
        self,
        source: str,
        file_path: str,
        lines: List[str],
    ) -&gt; List[CodeChunk]:
        """Generate semantic chunks from source code."""
        chunks = []
        
        # Add file-level chunk
        chunks.append(CodeChunk(
            content=source,
            chunk_type="file",
            symbol_name=Path(file_path).stem,
            file_path=file_path,
            start_line=1,
            end_line=len(lines),
        ))
        
        # Find function chunks
        in_func = False
        func_start = 0
        func_name = ""
        func_indent = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip comments and empty lines
            if not stripped or stripped.startswith("#"):
                continue
            
            # Check for function start
            func_match = self.patterns["func"].search(line)
            if func_match:
                if in_func:
                    # Add previous function
                    func_content = "\n".join(lines[func_start-1:line_num-1])
                    chunks.append(CodeChunk(
                        content=func_content,
                        chunk_type="function",
                        symbol_name=func_name,
                        file_path=file_path,
                        start_line=func_start,
                        end_line=line_num-1,
                    ))
                
                in_func = True
                func_start = line_num
                func_name = func_match.group(1)
                func_indent = len(line) - len(line.lstrip())
                continue
            
            # Check for function end (dedent)
            if in_func:
                current_indent = len(line) - len(line.lstrip())
                if stripped and current_indent &lt;= func_indent and line_num &gt; func_start:
                    # Function ends at previous line
                    func_content = "\n".join(lines[func_start-1:line_num-1])
                    chunks.append(CodeChunk(
                        content=func_content,
                        chunk_type="function",
                        symbol_name=func_name,
                        file_path=file_path,
                        start_line=func_start,
                        end_line=line_num-1,
                    ))
                    in_func = False
        
        # Add last function if still in one
        if in_func:
            func_content = "\n".join(lines[func_start-1:])
            chunks.append(CodeChunk(
                content=func_content,
                chunk_type="function",
                symbol_name=func_name,
                file_path=file_path,
                start_line=func_start,
                end_line=len(lines),
            ))
        
        return chunks

