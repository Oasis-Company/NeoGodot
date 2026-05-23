"""Template Engine for NeoGodot prompt system using Jinja2."""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    logging.warning("Jinja2 not available, using simple string formatting")

logger = logging.getLogger(__name__)


class TemplateEngine:
    """基于 Jinja2 的提示词模板引擎"""
    
    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = template_dir or self._get_default_template_dir()
        self._env = None
        
        if JINJA2_AVAILABLE:
            self._init_jinja2()
    
    def _get_default_template_dir(self) -> str:
        """获取默认模板目录"""
        current_dir = Path(__file__).parent
        template_dir = current_dir / "templates"
        return str(template_dir)
    
    def _init_jinja2(self) -> None:
        """初始化 Jinja2 环境"""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir, exist_ok=True)
        
        self._env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        self._register_filters()
    
    def _register_filters(self) -> None:
        """注册自定义过滤器"""
        if self._env:
            self._env.filters['code_block'] = self._code_block_filter
            self._env.filters['truncate'] = self._truncate_filter
    
    def _code_block_filter(self, content: str, language: str = "") -> str:
        """代码块过滤器"""
        return f"```{language}\n{content}\n```"
    
    def _truncate_filter(self, content: str, max_length: int = 1000) -> str:
        """截断过滤器"""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "[...]"
    
    def render(
        self,
        template_name: str,
        context: Dict[str, Any],
    ) -> str:
        """渲染模板
        
        Args:
            template_name: 模板名称或模板字符串
            context: 模板上下文数据
            
        Returns:
            渲染后的字符串
        """
        if JINJA2_AVAILABLE and self._env:
            try:
                return self._render_jinja2(template_name, context)
            except TemplateNotFound:
                logger.warning(f"Template {template_name} not found, using string format")
        
        return self._render_simple(template_name, context)
    
    def _render_jinja2(self, template_name: str, context: Dict[str, Any]) -> str:
        """使用 Jinja2 渲染"""
        if os.path.isfile(os.path.join(self.template_dir, template_name)):
            template = self._env.get_template(template_name)
        else:
            template = self._env.from_string(template_name)
        
        return template.render(**context)
    
    def _render_simple(self, template_str: str, context: Dict[str, Any]) -> str:
        """简单字符串格式化（备用方案）"""
        try:
            return template_str.format(**context)
        except KeyError as e:
            logger.warning(f"Missing key in context: {e}")
            return template_str
    
    def render_code_generation(
        self,
        task_description: str,
        context: str = "",
        examples: Optional[list] = None,
        language: str = "gdscript",
    ) -> str:
        """渲染代码生成提示词"""
        template = """你是一个专业的 Godot 游戏开发助手。请根据以下要求生成高质量的 {{ language }} 代码。

任务描述：
{{ task_description }}

{% if context %}
参考上下文：
{{ context }}
{% endif %}

{% if examples %}
参考示例：
{% for example in examples %}
{{ example }}
{% endfor %}
{% endif %}

请直接生成可执行的代码，不要包含额外的解释。"""
        
        return self.render(template, {
            "task_description": task_description,
            "context": context,
            "examples": examples or [],
            "language": language,
        })
    
    def render_scene_generation(
        self,
        scene_description: str,
        existing_nodes: Optional[list] = None,
    ) -> str:
        """渲染场景生成提示词"""
        template = """你是一个专业的 Godot 场景设计助手。请根据以下要求创建或修改场景。

场景描述：
{{ scene_description }}

{% if existing_nodes %}
现有节点结构：
{% for node in existing_nodes %}
- {{ node }}
{% endfor %}
{% endif %}

请输出完整的 .tscn 格式场景文件内容。"""
        
        return self.render(template, {
            "scene_description": scene_description,
            "existing_nodes": existing_nodes or [],
        })
    
    def render_chat(
        self,
        user_message: str,
        system_prompt: str = "",
        conversation_history: Optional[list] = None,
    ) -> str:
        """渲染对话提示词"""
        template = """{% if system_prompt %}{{ system_prompt }}

{% endif %}{% if conversation_history %}对话历史：
{% for message in conversation_history %}
{% if message.role == 'user' %}用户: {{ message.content }}
{% else %}助手: {{ message.content }}
{% endif %}
{% endfor %}

{% endif %}用户: {{ user_message }}
助手:"""
        
        return self.render(template, {
            "user_message": user_message,
            "system_prompt": system_prompt,
            "conversation_history": conversation_history or [],
        })
