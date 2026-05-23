
"""Test core types can be instantiated correctly."""

import sys
from pathlib import Path
from datetime import datetime

# Add runtime dir to path
runtime_dir = Path(__file__).parent
sys.path.insert(0, str(runtime_dir))

from context_engine import (
    SymbolKind,
    AccessModifier,
    TaskType,
    SourceLocation,
    SymbolInfo,
    CodeChunk,
    CodeStructure,
    SceneNode,
    SceneStructure,
    ProjectContext,
    RetrievedItem,
    QueryIntent,
)


def test_core_types():
    """Test that all core types can be instantiated without errors."""
    print("Testing core types...")
    
    # Test enums
    print("\n1. Testing enums...")
    assert SymbolKind.CLASS == "class"
    assert AccessModifier.PUBLIC == "public"
    assert TaskType.CODE_GENERATION == "code_generation"
    print("   ✓ Enums OK")
    
    # Test SourceLocation
    print("\n2. Testing SourceLocation...")
    loc = SourceLocation(
        file_path="test.gd",
        start_line=1,
        start_column=0,
        end_line=10,
        end_column=20
    )
    assert loc.file_path == "test.gd"
    print("   ✓ SourceLocation OK")
    
    # Test SymbolInfo
    print("\n3. Testing SymbolInfo...")
    symbol = SymbolInfo(
        name="test_func",
        kind=SymbolKind.FUNCTION,
        access=AccessModifier.PUBLIC,
        location=loc
    )
    assert symbol.name == "test_func"
    assert symbol.kind == SymbolKind.FUNCTION
    print("   ✓ SymbolInfo OK")
    
    # Test CodeChunk
    print("\n4. Testing CodeChunk...")
    chunk = CodeChunk(
        content="func test():\n    pass",
        chunk_type="function",
        symbol_name="test",
        file_path="test.gd",
        start_line=1,
        end_line=2
    )
    assert len(chunk.content_hash) == 16
    print("   ✓ CodeChunk OK")
    
    # Test CodeStructure
    print("\n5. Testing CodeStructure...")
    code_struct = CodeStructure(
        file_path="test.gd",
        symbols=[symbol],
        chunks=[chunk],
        total_lines=2,
        source_code=chunk.content
    )
    assert code_struct.file_path == "test.gd"
    assert len(code_struct.symbols) == 1
    print("   ✓ CodeStructure OK")
    
    # Test SceneNode
    print("\n6. Testing SceneNode...")
    node = SceneNode(
        node_path="Node2D",
        node_type="Node2D",
        node_name="Node2D"
    )
    child = SceneNode(
        node_path="Node2D/Sprite2D",
        node_type="Sprite2D",
        node_name="Sprite2D",
        parent_path="Node2D"
    )
    node.children.append(child)
    assert len(node.children) == 1
    print("   ✓ SceneNode OK")
    
    # Test SceneStructure
    print("\n7. Testing SceneStructure...")
    scene_struct = SceneStructure(
        scene_path="test.tscn",
        root_node=node,
        all_nodes=[node, child],
        node_count=2
    )
    assert scene_struct.node_count == 2
    print("   ✓ SceneStructure OK")
    
    # Test ProjectContext
    print("\n8. Testing ProjectContext...")
    project_ctx = ProjectContext(
        project_path="/test/project",
        project_name="Test Project"
    )
    project_ctx.code_structures["test.gd"] = code_struct
    project_ctx.scene_structures["test.tscn"] = scene_struct
    assert project_ctx.project_name == "Test Project"
    print("   ✓ ProjectContext OK")
    
    # Test RetrievedItem
    print("\n9. Testing RetrievedItem...")
    item = RetrievedItem(
        content="test content",
        source_type="code",
        source_path="test.gd",
        relevance_score=0.95
    )
    assert item.relevance_score == 0.95
    print("   ✓ RetrievedItem OK")
    
    # Test QueryIntent
    print("\n10. Testing QueryIntent...")
    intent = QueryIntent(
        task_type=TaskType.CODE_GENERATION,
        confidence=0.85,
        entities=[{"type": "class", "value": "Player"}]
    )
    assert intent.task_type == TaskType.CODE_GENERATION
    print("   ✓ QueryIntent OK")
    
    print("\n✅ All core types tested successfully!")
    return True


if __name__ == "__main__":
    success = test_core_types()
    sys.exit(0 if success else 1)
