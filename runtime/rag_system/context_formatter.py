"""Context Formatter for NeoGodot RAG system."""

from typing import List, Optional
from context_engine.types import RetrievedItem


class ContextFormatter:
    """上下文格式化器，用于将检索结果格式化为 LLM 可用的提示词"""
    
    def __init__(self, max_context_length: int = 8000):
        self.max_context_length = max_context_length
    
    def format(
        self,
        retrieved_items: List[RetrievedItem],
        query: Optional[str] = None,
        include_metadata: bool = True,
    ) -> str:
        """将检索结果格式化为上下文字符串
        
        Args:
            retrieved_items: 检索结果列表
            query: 原始查询（可选）
            include_metadata: 是否包含元数据
            
        Returns:
            格式化后的上下文字符串
        """
        if not retrieved_items:
            return ""
        
        context_parts = ["=== 检索到的相关上下文 ===\n"]
        
        total_length = len(context_parts[0])
        
        for idx, item in enumerate(retrieved_items, 1):
            item_content = self._format_item(item, idx, include_metadata)
            
            if total_length + len(item_content) > self.max_context_length:
                remaining = self.max_context_length - total_length
                if remaining > 100:
                    item_content = item_content[:remaining] + "\n[...截断...]"
                    context_parts.append(item_content)
                break
            
            context_parts.append(item_content)
            total_length += len(item_content)
        
        context_parts.append("\n=== 上下文结束 ===")
        
        return "\n".join(context_parts)
    
    def _format_item(
        self,
        item: RetrievedItem,
        index: int,
        include_metadata: bool,
    ) -> str:
        """格式化单个检索项"""
        parts = [f"\n--- 结果 {index} (相关度: {item.relevance_score:.2f}) ---"]
        
        if item.source_path:
            parts.append(f"来源: {item.source_path}")
        
        if item.source_type:
            parts.append(f"类型: {item.source_type}")
        
        parts.append(f"\n内容:\n{item.content}")
        
        if include_metadata and item.metadata:
            meta_str = ", ".join(f"{k}={v}" for k, v in item.metadata.items())
            if meta_str:
                parts.append(f"\n元数据: {meta_str}")
        
        return "\n".join(parts)
    
    def format_for_code_generation(
        self,
        retrieved_items: List[RetrievedItem],
        task_description: str,
    ) -> str:
        """专门为代码生成格式化上下文"""
        code_items = [item for item in retrieved_items if item.source_type == "code"]
        other_items = [item for item in retrieved_items if item.source_type != "code"]
        
        context = f"任务描述: {task_description}\n\n"
        
        if code_items:
            context += "相关代码示例:\n"
            context += self.format(code_items, include_metadata=False)
            context += "\n\n"
        
        if other_items:
            context += "相关参考资料:\n"
            context += self.format(other_items, include_metadata=False)
        
        return context
