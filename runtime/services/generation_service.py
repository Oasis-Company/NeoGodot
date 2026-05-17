import logging
import uuid
from typing import Optional, Dict, Any
from models.requests import GenerateRequest, ImageGenerateRequest, ScriptGenerateRequest
from models.responses import GenerateResponse, ImageGenerateResponse
from datetime import datetime

logger = logging.getLogger("neogodot-runtime.service")


class GenerationService:
    """
    Service layer for handling generation requests.
    
    This service is responsible for:
    - Processing generation requests
    - Calling appropriate providers
    - Logging decisions and policy compliance
    - Error handling
    """
    
    def __init__(self):
        self.logger = logging.getLogger("neogodot-runtime.service.generation")
    
    async def generate_text(self, request: GenerateRequest, trace_id: str) -> GenerateResponse:
        """
        Generate text based on the provided request.
        
        Args:
            request: The text generation request containing prompt and parameters
            trace_id: The trace ID for tracking this operation
            
        Returns:
            GenerateResponse with the generation result or error
        """
        self.logger.info(
            f"Processing text generation request",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_text",
                "decision_reason": "Starting text generation process",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        
        try:
            model = request.model or "default-text-model"
            max_tokens = request.max_tokens
            temperature = request.temperature
            stop = request.stop
            
            self.logger.info(
                f"Calling text provider",
                extra={
                    "trace_id": trace_id,
                    "policy_id": "generate_text",
                    "decision_reason": f"Invoking provider with model={model}, max_tokens={max_tokens}, temperature={temperature}",
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }
            )
            
            generated_text = await self._call_text_provider(
                prompt=request.prompt,
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
                }
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
                }
            )
            return GenerateResponse(
                success=False,
                trace_id=trace_id,
                error=str(e)
            )
    
    async def generate_image(self, request: ImageGenerateRequest, trace_id: str) -> ImageGenerateResponse:
        """
        Generate an image based on the provided request.
        
        Args:
            request: The image generation request containing prompt and parameters
            trace_id: The trace ID for tracking this operation
            
        Returns:
            ImageGenerateResponse with the generation result or error
        """
        self.logger.info(
            f"Processing image generation request",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_image",
                "decision_reason": "Starting image generation process",
                "timestamp": datetime.utcnow().isoformat(),
            }
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
                }
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
                }
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
                }
            )
            return ImageGenerateResponse(
                success=False,
                trace_id=trace_id,
                error=str(e)
            )
    
    async def generate_script(self, request: ScriptGenerateRequest, trace_id: str) -> GenerateResponse:
        """
        Generate a script (e.g., GDScript) based on the provided request.
        
        Args:
            request: The script generation request containing prompt and parameters
            trace_id: The trace ID for tracking this operation
            
        Returns:
            GenerateResponse with the generation result or error
        """
        self.logger.info(
            f"Processing script generation request",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_script",
                "decision_reason": "Starting script generation process",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        
        try:
            template_type = request.template_type
            target_class = request.target_class
            style = request.style or "gdscript"
            
            self.logger.info(
                f"Calling script provider",
                extra={
                    "trace_id": trace_id,
                    "policy_id": "generate_script",
                    "decision_reason": f"Invoking script provider with template={template_type}, target_class={target_class}, style={style}",
                    "template_type": template_type,
                    "target_class": target_class,
                    "style": style,
                }
            )
            
            generated_script = await self._call_script_provider(
                prompt=request.prompt,
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
                }
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
                }
            )
            return GenerateResponse(
                success=False,
                trace_id=trace_id,
                error=str(e)
            )
    
    async def _call_text_provider(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        stop: Optional[list],
        trace_id: str,
    ) -> str:
        """
        Internal method to call the text generation provider.
        
        This is a placeholder for actual provider integration.
        """
        self.logger.info(
            f"Text provider invoked",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_text",
                "decision_reason": "Calling text generation provider",
            }
        )
        
        await self._simulate_processing()
        
        return f"Generated text based on prompt: {prompt[:50]}... (truncated)"
    
    async def _call_image_provider(
        self,
        prompt: str,
        model: str,
        size: str,
        quality: str,
        trace_id: str,
    ) -> str:
        """
        Internal method to call the image generation provider.
        
        This is a placeholder for actual provider integration.
        """
        self.logger.info(
            f"Image provider invoked",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_image",
                "decision_reason": "Calling image generation provider",
            }
        )
        
        await self._simulate_processing()
        
        return f"ai_generated/ui/generated_{trace_id}.png"
    
    async def _call_script_provider(
        self,
        prompt: str,
        template_type: str,
        target_class: Optional[str],
        style: str,
        trace_id: str,
    ) -> str:
        """
        Internal method to call the script generation provider.
        
        This is a placeholder for actual provider integration.
        """
        self.logger.info(
            f"Script provider invoked",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_script",
                "decision_reason": "Calling script generation provider",
            }
        )
        
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
            return f'''extends Node

class_name {target_class or "GeneratedClass"}

func _ready() -> void:
    # Script generated based on: {{prompt}}
    pass

func _process(delta: float) -> void:
    pass
'''
        elif style == "csharp":
            return f'''using Godot;

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
'''
        else:
            return f'''# Script generated based on: {{prompt}}
# Style: {style}

class {target_class or "GeneratedClass"}:
    pass
'''
