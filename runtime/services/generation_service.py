import logging
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
from models.requests import GenerateRequest, ImageGenerateRequest, ScriptGenerateRequest
from models.responses import GenerateResponse, ImageGenerateResponse
from providers.provider_factory import ProviderFactory
from datetime import datetime
import os
from context_engine import ContextManager, TaskType
from rag_system import QueryAnalyzer, HybridRetriever, ContextFormatter
from model_router import ModelRouter
from prompt_system import TemplateEngine, OutputParser

logger = logging.getLogger("neogodot-runtime.service")


class GenerationService:
    """Service layer for handling generation requests."""

    def __init__(self):
        self.logger = logging.getLogger("neogodot-runtime.service.generation")
        self.openai_provider = self._init_provider("openai")
        self.anthropic_provider = self._init_provider("anthropic")
        self.default_provider = self.openai_provider or self.anthropic_provider
        
        # Initialize new components
        self.context_manager = ContextManager()
        self.query_analyzer = QueryAnalyzer()
        self.context_formatter = ContextFormatter()
        self.template_engine = TemplateEngine()
        self.output_parser = OutputParser()
        
        # Initialize ModelRouter with providers
        providers = {}
        if self.openai_provider:
            providers["openai"] = self.openai_provider
        if self.anthropic_provider:
            providers["anthropic"] = self.anthropic_provider
        self.model_router = ModelRouter(providers=providers)

    def _init_provider(self, name: str) -> Optional[object]:
        """Initialize AI provider if configured."""
        api_key = os.getenv(f"{name.upper()}_API_KEY")
        if not api_key:
            self.logger.debug(f"{name} provider not configured (no API key)")
            return None
        
        try:
            config = {
                "api_key": api_key,
                "model": os.getenv(f"{name.upper()}_MODEL", "gpt-4o" if name == "openai" else "claude-3-5-sonnet-20241022"),
                "base_url": os.getenv(f"{name.upper()}_BASE_URL", ""),
                "timeout": int(os.getenv("PROVIDER_TIMEOUT", "60")),
            }
            provider = ProviderFactory.create(name, config)
            self.logger.info(f"{name} provider initialized successfully")
            return provider
        except Exception as e:
            self.logger.warning(f"Failed to initialize {name} provider: {e}")
            return None

    async def generate_text(self, request: GenerateRequest, trace_id: str) -> GenerateResponse:
        """Generate text based on the provided request."""
        self.logger.info(
            f"Processing text generation request",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_text",
                "decision_reason": "Starting text generation process",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        try:
            model = request.model or "default-text-model"
            max_tokens = request.max_tokens
            temperature = request.temperature
            stop = request.stop
            
            # Get project context if available
            project_path = getattr(request, "project_path", None)
            context_str = ""
            if project_path:
                try:
                    relevant_context = await self.context_manager.get_relevant_context(
                        project_path=Path(project_path),
                        query=request.prompt,
                        limit=5
                    )
                    context_str = self.context_formatter.format(relevant_context)
                except Exception as e:
                    self.logger.warning(f"Failed to get context: {e}")

            self.logger.info(
                f"Calling text provider",
                extra={
                    "trace_id": trace_id,
                    "policy_id": "generate_text",
                    "decision_reason": f"Invoking provider with model={model}, max_tokens={max_tokens}, temperature={temperature}",
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )

            generated_text = await self._call_text_provider(
                prompt=request.prompt,
                context=context_str,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop,
                trace_id=trace_id,
            )

            self.logger.info(
                f"Text generation successful",
                extra={
                    "trace_id": trace_id,
                    "policy_id": "generate_text",
                    "decision_reason": "Text generation completed successfully",
                    "result_length": len(generated_text),
                },
            )

            return GenerateResponse(
                success=True,
                trace_id=trace_id,
                result={
                    "text": generated_text,
                    "model": model,
                    "prompt_tokens": len(request.prompt.split()),
                    "completion_tokens": len(generated_text.split()),
                }
            )

        except Exception as e:
            self.logger.error(
                f"Text generation failed: {str(e)}",
                extra={
                    "trace_id": trace_id,
                    "policy_id": "generate_text",
                    "decision_reason": f"Text generation failed with error: {str(e)}",
                    "error_type": type(e).__name__,
                },
            )
            return GenerateResponse(
                success=False,
                trace_id=trace_id,
                error=str(e)
            )

    async def generate_image(self, request: ImageGenerateRequest, trace_id: str) -> ImageGenerateResponse:
        """Generate an image based on the provided request."""
        self.logger.info(
            f"Processing image generation request",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_image",
                "decision_reason": "Starting image generation process",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        try:
            model = request.model or "default-image-model"
            size = request.size
            quality = request.quality

            self.logger.info(
                f"Calling image provider",
                extra={
                    "trace_id": trace_id,
                    "policy_id": "generate_image",
                    "decision_reason": f"Invoking image provider with model={model}, size={size}, quality={quality}",
                    "model": model,
                    "size": size,
                    "quality": quality,
                },
            )

            image_path = await self._call_image_provider(
                prompt=request.prompt,
                model=model,
                size=size,
                quality=quality,
                trace_id=trace_id,
            )

            self.logger.info(
                f"Image generation successful",
                extra={
                    "trace_id": trace_id,
                    "policy_id": "generate_image",
                    "decision_reason": "Image generation completed successfully",
                    "image_path": image_path,
                },
            )

            return ImageGenerateResponse(
                success=True,
                trace_id=trace_id,
                image_path=image_path,
                image_url=f"file://{image_path}"
            )

        except Exception as e:
            self.logger.error(
                f"Image generation failed: {str(e)}",
                extra={
                    "trace_id": trace_id,
                    "policy_id": "generate_image",
                    "decision_reason": f"Image generation failed with error: {str(e)}",
                    "error_type": type(e).__name__,
                },
            )
            return ImageGenerateResponse(
                success=False,
                trace_id=trace_id,
                error=str(e)
            )

    async def generate_script(self, request: ScriptGenerateRequest, trace_id: str) -> GenerateResponse:
        """Generate a script (e.g., GDScript) based on the provided request."""
        self.logger.info(
            f"Processing script generation request",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_script",
                "decision_reason": "Starting script generation process",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        try:
            template_type = request.template_type
            target_class = request.target_class
            style = request.style or "gdscript"
            
            # Get project context if available
            project_path = getattr(request, "project_path", None)
            context_str = ""
            if project_path:
                try:
                    relevant_context = await self.context_manager.get_relevant_context(
                        project_path=Path(project_path),
                        query=request.prompt,
                        limit=5
                    )
                    context_str = self.context_formatter.format(relevant_context)
                except Exception as e:
                    self.logger.warning(f"Failed to get context: {e}")

            self.logger.info(
                f"Calling script provider",
                extra={
                    "trace_id": trace_id,
                    "policy_id": "generate_script",
                    "decision_reason": f"Invoking script provider with template={template_type}, target_class={target_class}, style={style}",
                    "template_type": template_type,
                    "target_class": target_class,
                    "style": style,
                },
            )

            generated_script = await self._call_script_provider(
                prompt=request.prompt,
                context=context_str,
                template_type=template_type,
                target_class=target_class,
                style=style,
                trace_id=trace_id,
            )

            self.logger.info(
                f"Script generation successful",
                extra={
                    "trace_id": trace_id,
                    "policy_id": "generate_script",
                    "decision_reason": "Script generation completed successfully",
                    "script_length": len(generated_script),
                    "style": style,
                },
            )

            return GenerateResponse(
                success=True,
                trace_id=trace_id,
                result={
                    "script": generated_script,
                    "style": style,
                    "template_type": template_type,
                    "target_class": target_class,
                    "file_path": f"ai_generated/scripts/generated_{trace_id}.gd" if style == "gdscript" else None,
                }
            )

        except Exception as e:
            self.logger.error(
                f"Script generation failed: {str(e)}",
                extra={
                    "trace_id": trace_id,
                    "policy_id": "generate_script",
                    "decision_reason": f"Script generation failed with error: {str(e)}",
                    "error_type": type(e).__name__,
                },
            )
            return GenerateResponse(
                success=False,
                trace_id=trace_id,
                error=str(e)
            )

    async def _call_text_provider(
        self,
        prompt: str,
        context: str = "",
        model: str = "default-text-model",
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stop: Optional[list] = None,
        trace_id: str = "",
    ) -> str:
        """Internal method to call the text generation provider with model router support."""
        self.logger.info(
            f"Text provider invoked",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_text",
                "decision_reason": "Calling text generation provider",
                "provider": self.default_provider.__class__.__name__ if self.default_provider else "none",
            },
        )

        if not self.default_provider:
            self.logger.warning(
                f"No AI provider configured, using fallback",
                extra={"trace_id": trace_id}
            )
            await self._simulate_processing()
            return f"Generated text based on prompt: {prompt[:50]}... (truncated)"

        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            result = await self.default_provider.generate(
                full_prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop
            )
            return result
        except Exception as e:
            self.logger.error(
                f"Provider error: {e}",
                extra={"trace_id": trace_id, "error": str(e)},
                exc_info=True
            )
            # Fallback to simulation
            await self._simulate_processing()
            return f"Generated text based on prompt: {prompt[:50]}... (truncated)"

    async def _call_image_provider(
        self,
        prompt: str,
        model: str = "default-image-model",
        size: str = "1024x1024",
        quality: str = "standard",
        trace_id: str = "",
    ) -> str:
        """Internal method to call the image generation provider."""
        self.logger.info(
            f"Image provider invoked",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_image",
                "decision_reason": "Calling image generation provider",
            },
        )

        if not self.openai_provider:
            self.logger.warning(
                f"OpenAI provider not available for image generation, using fallback",
                extra={"trace_id": trace_id}
            )
            await self._simulate_processing()
            return f"ai_generated/ui/generated_{trace_id}.png"

        try:
            result = await self.openai_provider.generate_image(
                prompt,
                model=model,
                size=size,
                quality=quality
            )
            if result and result.get("images") and len(result["images"]) > 0:
                first_image = result["images"][0]
                if first_image.get("url"):
                    return first_image["url"]
            return f"ai_generated/ui/generated_{trace_id}.png"
        except Exception as e:
            self.logger.error(
                f"Image provider error: {e}",
                extra={"trace_id": trace_id, "error": str(e)},
                exc_info=True
            )
            await self._simulate_processing()
            return f"ai_generated/ui/generated_{trace_id}.png"

    async def _call_script_provider(
        self,
        prompt: str,
        context: str = "",
        template_type: str = "",
        target_class: Optional[str] = None,
        style: str = "gdscript",
        trace_id: str = "",
    ) -> str:
        """Internal method to call the script generation provider with RAG support."""
        self.logger.info(
            f"Script provider invoked",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_script",
                "decision_reason": "Calling script generation provider",
                "style": style,
                "template_type": template_type,
            },
        )

        if not self.default_provider:
            self.logger.warning(
                f"No AI provider configured, using fallback template",
                extra={"trace_id": trace_id}
            )
            await self._simulate_processing()
            script_template = self._get_script_template(template_type, target_class, style)
            return script_template.format(prompt=prompt, target_class=target_class or "GeneratedClass")

        # Build system prompt for GDScript generation
        system_prompt = """You are a professional Godot Engine game developer. Your task is to generate clean, production-ready GDScript code.

Follow these rules strictly:
1. Use GDScript 4.x syntax
2. Always include type hints for variables and functions
3. Follow Godot's naming conventions (snake_case for variables/functions, PascalCase for classes)
4. Include useful comments explaining complex logic
5. Make code modular and reusable
6. Include proper error handling where appropriate
7. Return ONLY code, no markdown formatting, no explanations
8. Start with the extends statement followed by class_name (if applicable)
"""

        # Build user prompt with context if available
        user_prompt_parts = [f"Generate GDScript code for: {prompt}"]
        if target_class:
            user_prompt_parts.append(f"Target class: {target_class}")
        if template_type:
            user_prompt_parts.append(f"Template type: {template_type}")
        if style:
            user_prompt_parts.append(f"Code style: {style}")
        if context:
            user_prompt_parts.append(f"\nRelevant project context:\n{context}")
        
        user_prompt = "\n".join(user_prompt_parts)

        try:
            result = await self.default_provider.generate(
                user_prompt,
                model="gpt-4o" if self.openai_provider else "claude-3-5-sonnet-20241022",
                max_tokens=4096,
                temperature=0.7,
                system=system_prompt
            )

            # Clean up the result (remove any markdown formatting if present)
            result = result.strip()
            if result.startswith("```gdscript"):
                result = result[10:]
            elif result.startswith("```"):
                result = result[3:]

            if result.endswith("```"):
                result = result[:-3]

            return result.strip()

        except Exception as e:
            self.logger.error(
                f"Script provider error: {e}",
                extra={"trace_id": trace_id, "error": str(e)},
                exc_info=True
            )
            # Fallback to template
            await self._simulate_processing()
            script_template = self._get_script_template(template_type, target_class, style)
            return script_template.format(prompt=prompt, target_class=target_class or "GeneratedClass")

    async def _simulate_processing(self):
        """Simulate processing time for demonstration purposes."""
        import asyncio
        await asyncio.sleep(0.1)

    def _get_script_template(self, template_type: str, target_class: Optional[str], style: str) -> str:
        """Get the appropriate script template based on type and style."""
        if style == "gdscript":
            return f"""extends Node

class_name {target_class or "GeneratedClass"}

func _ready() -> void:
    # Script generated based on: {{prompt}}
    pass

func _process(delta: float) -> void:
    pass
"""
        elif style == "csharp":
            return f"""using Godot;

public partial class {target_class or "GeneratedClass"} : Node
{{
    // Script generated based on: {{prompt}}
    
    public override void _Ready()
    {{
    }}
    
    public override void _Process(double delta)
    {{
    }}
}}
"""
        else:
            return f"""# Script generated based on: {{prompt}}
# Style: {style}

class {target_class or "GeneratedClass"}:
    pass
"""
