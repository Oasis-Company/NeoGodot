"""Output Parser for NeoGodot prompt system."""

import re
import json
from typing import Dict, Any, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class OutputParser:
    """LLM 输出解析器，支持 JSON 和 Markdown 代码块"""
    
    def __init__(self):
        self._json_patterns = [
            r'```(?:json)?\s*([\s\S]*?)\s*```',
            r'\{[\s\S]*\}',
            r'\[[\s\S]*\]',
        ]
        self._code_block_pattern = r'```(\w*)\s*([\s\S]*?)\s*```'
    
    def parse(self, text: str) -> Dict[str, Any]:
        """解析 LLM 输出
        
        Args:
            text: LLM 输出文本
            
        Returns:
            解析结果字典
        """
        result = {
            "raw_text": text,
            "json": None,
            "code_blocks": [],
            "plain_text": text,
        }
        
        json_data = self._extract_json(text)
        if json_data:
            result["json"] = json_data
        
        code_blocks = self._extract_code_blocks(text)
        if code_blocks:
            result["code_blocks"] = code_blocks
        
        result["plain_text"] = self._clean_text(text)
        
        return result
    
    def _extract_json(self, text: str) -> Optional[Union[Dict, List]]:
        """提取 JSON 数据"""
        for pattern in self._json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            
            for match in matches:
                json_str = match.strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """提取 Markdown 代码块"""
        code_blocks = []
        
        matches = re.findall(self._code_block_pattern, text, re.DOTALL)
        
        for language, code in matches:
            code_blocks.append({
                "language": language or "text",
                "code": code.strip(),
            })
        
        if not code_blocks:
            gdscript_code = self._extract_gdscript_without_markdown(text)
            if gdscript_code:
                code_blocks.append({
                    "language": "gdscript",
                    "code": gdscript_code.strip(),
                })
        
        return code_blocks
    
    def _extract_gdscript_without_markdown(self, text: str) -> Optional[str]:
        """尝试提取没有 Markdown 标记的 GDScript 代码"""
        lines = text.split('\n')
        code_lines = []
        in_code = False
        
        gdscript_keywords = [
            'extends', 'class_name', 'func', 'var', 'const', 'signal',
            'if', 'else', 'for', 'while', 'match', 'return',
            'Node', 'Control', 'CharacterBody2D', 'CharacterBody3D',
        ]
        
        for line in lines:
            stripped = line.strip()
            
            if any(keyword in stripped for keyword in gdscript_keywords):
                in_code = True
            
            if in_code:
                code_lines.append(line)
        
        if code_lines:
            return '\n'.join(code_lines)
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """清理文本，移除代码块和 JSON"""
        cleaned = re.sub(self._code_block_pattern, '', text)
        cleaned = re.sub(r'\{[\s\S]*\}', '', cleaned)
        cleaned = re.sub(r'\[[\s\S]*\]', '', cleaned)
        return cleaned.strip()
    
    def parse_code(self, text: str, language: Optional[str] = None) -> Optional[str]:
        """专门解析代码
        
        Args:
            text: LLM 输出文本
            language: 指定语言（可选）
            
        Returns:
            代码字符串
        """
        result = self.parse(text)
        
        if not result["code_blocks"]:
            return None
        
        if language:
            for block in result["code_blocks"]:
                if block["language"].lower() == language.lower():
                    return block["code"]
        
        return result["code_blocks"][0]["code"]
    
    def parse_json_safe(self, text: str, default: Any = None) -> Any:
        """安全解析 JSON
        
        Args:
            text: LLM 输出文本
            default: 默认值
            
        Returns:
            解析的 JSON 数据或默认值
        """
        try:
            result = self.parse(text)
            return result["json"] if result["json"] is not None else default
        except Exception as e:
            logger.warning(f"JSON parsing failed: {e}")
            return default
