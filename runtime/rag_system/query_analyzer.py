"""Query Analyzer for NeoGodot RAG system."""

import re
from typing import Dict, Any, List, Optional
import logging
from context_engine.types import TaskType, QueryIntent

logger = logging.getLogger(__name__)


class QueryAnalyzer:
    """简单查询意图分析器"""
    
    def __init__(self):
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """初始化关键词模式"""
        self.patterns = {
            TaskType.CODE_GENERATION: [
                r"创建|create|generate|生成|写.*代码|write.*code|实现|implement",
                r"函数|function|类|class|脚本|script",
            ],
            TaskType.CODE_COMPLETION: [
                r"补全|complete|继续|continue|填充|fill",
                r"缺失|missing|TODO|todo",
            ],
            TaskType.SCENE_GENERATION: [
                r"场景|scene|节点|node|创建场景|create.*scene",
                r"2D|3D|游戏对象|game.*object|sprite|camera",
            ],
            TaskType.DEBUGGING: [
                r"调试|debug|错误|error|bug|问题|problem",
                r"不工作|not.*work|崩溃|crash|异常|exception",
            ],
            TaskType.REFACTORING: [
                r"重构|refactor|优化|optimize|改进|improve",
                r"清理|clean|简化|simplify",
            ],
            TaskType.EXPLANATION: [
                r"解释|explain|说明|how|如何|什么是|what is",
                r"理解|understand|学习|learn",
            ],
            TaskType.CHAT: [
                r"聊天|chat|你好|hello|hi|嗨",
                r"？|\?|帮助|help",
            ],
        }
    
    def analyze(self, query: str) -> QueryIntent:
        """分析查询意图
        
        Args:
            query: 用户查询字符串
            
        Returns:
            QueryIntent 对象，包含任务类型、置信度和实体
        """
        task_type_scores = self._calculate_task_scores(query.lower())
        
        if not task_type_scores:
            return QueryIntent(
                task_type=TaskType.CHAT,
                confidence=0.5,
                entities=[],
                expanded_queries=[query]
            )
        
        best_task = max(task_type_scores.keys(), key=lambda k: task_type_scores[k])
        confidence = task_type_scores[best_task]
        
        entities = self._extract_entities(query)
        expanded_queries = self._expand_query(query, best_task)
        
        return QueryIntent(
            task_type=best_task,
            confidence=confidence,
            entities=entities,
            expanded_queries=expanded_queries
        )
    
    def _calculate_task_scores(self, query: str) -> Dict[TaskType, float]:
        """计算每个任务类型的得分"""
        scores = {}
        
        for task_type, patterns in self.patterns.items():
            match_count = 0
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    match_count += 1
            
            if match_count > 0:
                scores[task_type] = min(1.0, 0.3 + match_count * 0.25)
        
        return scores
    
    def _extract_entities(self, query: str) -> List[Dict[str, Any]]:
        """从查询中提取实体"""
        entities = []
        
        class_match = re.search(r'class\s+(\w+)|(\w+)\s+类', query, re.IGNORECASE)
        if class_match:
            class_name = class_match.group(1) or class_match.group(2)
            entities.append({
                "type": "class_name",
                "value": class_name,
            })
        
        func_match = re.search(r'func(?:tion)?\s+(\w+)|(\w+)\s+函数', query, re.IGNORECASE)
        if func_match:
            func_name = func_match.group(1) or func_match.group(2)
            entities.append({
                "type": "function_name",
                "value": func_name,
            })
        
        file_match = re.search(r'(\w+\.(?:gd|tscn|tres))', query, re.IGNORECASE)
        if file_match:
            entities.append({
                "type": "file_path",
                "value": file_match.group(1),
            })
        
        return entities
    
    def _expand_query(self, query: str, task_type: TaskType) -> List[str]:
        """扩展查询以提高检索召回率"""
        expanded = [query]
        
        if task_type in [TaskType.CODE_GENERATION, TaskType.CODE_COMPLETION]:
            expanded.append(f"godot {query}")
            expanded.append(f"gdscript {query}")
        
        return expanded
