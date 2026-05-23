"""Model Router for intelligent LLM selection in NeoGodot."""

import asyncio
import time
from typing import Dict, List, Optional, Any
import logging
from context_engine.types import (
    TaskType,
    ModelConfig,
    RoutingDecision,
    GenerationResult,
)

logger = logging.getLogger(__name__)


class ModelRouter:
    """智能模型路由器，基于能力、成本、历史和负载选择最佳模型"""
    
    ROUTING_WEIGHTS = {
        "capability": 0.4,
        "cost": 0.3,
        "history": 0.2,
        "load": 0.1,
    }
    
    ROUTING_POLICY = {
        TaskType.CODE_GENERATION: {
            "primary": "deepseek-coder",
            "secondary": "claude-3-5-sonnet",
            "fallback": "llama3.1",
        },
        TaskType.CODE_COMPLETION: {
            "primary": "deepseek-coder",
            "secondary": "claude-3-haiku",
            "fallback": "llama3.1",
        },
        TaskType.SCENE_GENERATION: {
            "primary": "deepseek-chat",
            "secondary": "claude-3-5-sonnet",
            "fallback": "llama3.1",
        },
        TaskType.DEBUGGING: {
            "primary": "deepseek-reasoner",
            "secondary": "claude-3-5-sonnet",
            "fallback": "llama3.1",
        },
        TaskType.REFACTORING: {
            "primary": "claude-3-5-sonnet",
            "secondary": "deepseek-coder",
            "fallback": "llama3.1",
        },
        TaskType.EXPLANATION: {
            "primary": "deepseek-chat",
            "secondary": "claude-3-haiku",
            "fallback": "llama3.1",
        },
        TaskType.CHAT: {
            "primary": "deepseek-chat",
            "secondary": "claude-3-haiku",
            "fallback": "llama3.1",
        },
    }
    
    MODEL_CONFIGS = {
        "deepseek-coder": ModelConfig(
            model_id="deepseek-coder",
            provider="deepseek",
            max_context_length=128000,
            cost_per_input_token=0.00014,
            cost_per_output_token=0.00028,
            avg_latency_ms=2000,
            capabilities=["code_generation", "code_completion", "debugging"],
        ),
        "deepseek-chat": ModelConfig(
            model_id="deepseek-chat",
            provider="deepseek",
            max_context_length=128000,
            cost_per_input_token=0.00014,
            cost_per_output_token=0.00028,
            avg_latency_ms=1500,
            capabilities=["chat", "explanation", "scene_generation"],
        ),
        "deepseek-reasoner": ModelConfig(
            model_id="deepseek-reasoner",
            provider="deepseek",
            max_context_length=128000,
            cost_per_input_token=0.00055,
            cost_per_output_token=0.00219,
            avg_latency_ms=5000,
            capabilities=["debugging", "reasoning", "refactoring"],
        ),
        "claude-3-5-sonnet": ModelConfig(
            model_id="claude-3-5-sonnet-20241022",
            provider="anthropic",
            max_context_length=200000,
            cost_per_input_token=0.003,
            cost_per_output_token=0.015,
            avg_latency_ms=2000,
            capabilities=["code_generation", "debugging", "refactoring", "scene_generation"],
        ),
        "claude-3-haiku": ModelConfig(
            model_id="claude-3-haiku-20240307",
            provider="anthropic",
            max_context_length=200000,
            cost_per_input_token=0.00025,
            cost_per_output_token=0.00125,
            avg_latency_ms=500,
            capabilities=["code_completion", "explanation", "chat"],
        ),
        "llama3.1": ModelConfig(
            model_id="llama3.1",
            provider="ollama",
            max_context_length=8192,
            cost_per_input_token=0.0,
            cost_per_output_token=0.0,
            avg_latency_ms=3000,
            capabilities=["code_generation", "chat", "explanation"],
        ),
    }
    
    def __init__(self, providers: Optional[Dict[str, Any]] = None):
        self.providers = providers or {}
        self._request_history: List[Dict[str, Any]] = []
        self._model_loads: Dict[str, int] = {}
    
    async def route(
        self,
        task_type: TaskType,
        prompt: str,
        context: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> GenerationResult:
        """路由请求到最佳模型
        
        Args:
            task_type: 任务类型
            prompt: 提示词
            context: 额外上下文
            temperature: 温度参数
            max_tokens: 最大生成令牌数
            
        Returns:
            生成结果
        """
        policy = self.ROUTING_POLICY.get(task_type, self.ROUTING_POLICY[TaskType.CHAT])
        model_chain = [policy["primary"], policy["secondary"], policy["fallback"]]
        
        last_error = None
        for model_id in model_chain:
            config = self.MODEL_CONFIGS.get(model_id)
            if not config or not config.enabled:
                continue
            
            try:
                result = await self._call_model(
                    config=config,
                    prompt=prompt,
                    context=context,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                
                self._record_success(model_id, result.latency_ms)
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"Model {model_id} failed: {e}")
                self._record_failure(model_id)
                continue
        
        raise RuntimeError(f"All models failed. Last error: {last_error}")
    
    async def _call_model(
        self,
        config: ModelConfig,
        prompt: str,
        context: str,
        temperature: float,
        max_tokens: int,
    ) -> GenerationResult:
        """调用指定模型"""
        provider = self.providers.get(config.provider)
        
        if not provider:
            raise ValueError(f"Provider {config.provider} not available")
        
        start_time = time.time()
        
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        content = await provider.generate(
            prompt=full_prompt,
            model=config.model_id,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        input_tokens = len(prompt.split())
        output_tokens = len(content.split())
        
        return GenerationResult(
            content=content,
            model=config.model_id,
            usage={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
            latency_ms=latency_ms,
        )
    
    def get_routing_decision(
        self,
        task_type: TaskType,
        estimated_tokens: int = 1000,
    ) -> RoutingDecision:
        """获取路由决策"""
        policy = self.ROUTING_POLICY.get(task_type, self.ROUTING_POLICY[TaskType.CHAT])
        
        primary_config = self.MODEL_CONFIGS.get(policy["primary"])
        
        estimated_cost = (
            estimated_tokens * primary_config.cost_per_input_token +
            estimated_tokens * 0.3 * primary_config.cost_per_output_token
        )
        
        return RoutingDecision(
            selected_model=policy["primary"],
            fallback_chain=[policy["secondary"], policy["fallback"]],
            estimated_cost=estimated_cost,
            estimated_latency_ms=primary_config.avg_latency_ms,
            routing_reason=f"Task type: {task_type.value}, capability optimized",
        )
    
    def _record_success(self, model_id: str, latency_ms: float) -> None:
        """记录成功请求"""
        self._request_history.append({
            "model": model_id,
            "success": True,
            "latency": latency_ms,
            "timestamp": time.time(),
        })
    
    def _record_failure(self, model_id: str) -> None:
        """记录失败请求"""
        self._request_history.append({
            "model": model_id,
            "success": False,
            "timestamp": time.time(),
        })
    
    def get_model_stats(self, model_id: str) -> Dict[str, Any]:
        """获取模型统计信息"""
        model_requests = [r for r in self._request_history if r["model"] == model_id]
        
        if not model_requests:
            return {"success_rate": 1.0, "avg_latency": 0, "total_requests": 0}
        
        success_count = sum(1 for r in model_requests if r["success"])
        avg_latency = (
            sum(r["latency"] for r in model_requests if r.get("latency")) / success_count
            if success_count > 0
            else 0
        )
        
        return {
            "success_rate": success_count / len(model_requests),
            "avg_latency": avg_latency,
            "total_requests": len(model_requests),
        }
