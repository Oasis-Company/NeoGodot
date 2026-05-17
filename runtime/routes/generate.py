from fastapi import APIRouter, Request, HTTPException
from models.requests import GenerateRequest, ImageGenerateRequest, ScriptGenerateRequest
from models.responses import GenerateResponse, ImageGenerateResponse
from services.generation_service import GenerationService
import logging
import uuid
from typing import Optional

router = APIRouter(prefix="/v1/generate", tags=["generation"])
logger = logging.getLogger("neogodot-runtime.generate")
generation_service = GenerationService()


@router.post("", response_model=GenerateResponse)
async def generate_text(request_data: GenerateRequest, request: Request):
    """
    Text generation endpoint.
    
    Generates text based on the provided prompt using AI models.
    """
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    
    if not request_data.prompt or len(request_data.prompt.strip()) == 0:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    logger.info(
        f"Text generation request received",
        extra={
            "trace_id": trace_id,
            "prompt_length": len(request_data.prompt),
            "policy_id": "generate_text",
            "decision_reason": "User requested text generation with prompt",
        }
    )
    
    try:
        response = await generation_service.generate_text(request_data, trace_id)
        logger.info(
            f"Text generation completed",
            extra={
                "trace_id": trace_id,
                "success": response.success,
                "policy_id": "generate_text",
                "decision_reason": "Text generation completed successfully",
            }
        )
        return response
    except Exception as e:
        logger.error(
            f"Text generation failed: {str(e)}",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_text",
                "decision_reason": f"Text generation failed with error: {str(e)}",
            }
        )
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/image", response_model=ImageGenerateResponse)
async def generate_image(request_data: ImageGenerateRequest, request: Request):
    """
    Image generation endpoint.
    
    Generates images based on the provided prompt using AI image models.
    """
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    
    if not request_data.prompt or len(request_data.prompt.strip()) == 0:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    logger.info(
        f"Image generation request received",
        extra={
            "trace_id": trace_id,
            "prompt_length": len(request_data.prompt),
            "size": request_data.size,
            "quality": request_data.quality,
            "policy_id": "generate_image",
            "decision_reason": "User requested image generation with prompt",
        }
    )
    
    try:
        response = await generation_service.generate_image(request_data, trace_id)
        logger.info(
            f"Image generation completed",
            extra={
                "trace_id": trace_id,
                "success": response.success,
                "image_path": response.image_path,
                "policy_id": "generate_image",
                "decision_reason": "Image generation completed successfully",
            }
        )
        return response
    except Exception as e:
        logger.error(
            f"Image generation failed: {str(e)}",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_image",
                "decision_reason": f"Image generation failed with error: {str(e)}",
            }
        )
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.post("/script", response_model=GenerateResponse)
async def generate_script(request_data: ScriptGenerateRequest, request: Request):
    """
    Script generation endpoint.
    
    Generates GDScript or other game scripts based on the provided prompt.
    """
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    
    if not request_data.prompt or len(request_data.prompt.strip()) == 0:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    logger.info(
        f"Script generation request received",
        extra={
            "trace_id": trace_id,
            "prompt_length": len(request_data.prompt),
            "template_type": request_data.template_type,
            "target_class": request_data.target_class,
            "style": request_data.style,
            "policy_id": "generate_script",
            "decision_reason": "User requested script generation with prompt",
        }
    )
    
    try:
        response = await generation_service.generate_script(request_data, trace_id)
        logger.info(
            f"Script generation completed",
            extra={
                "trace_id": trace_id,
                "success": response.success,
                "policy_id": "generate_script",
                "decision_reason": "Script generation completed successfully",
            }
        )
        return response
    except Exception as e:
        logger.error(
            f"Script generation failed: {str(e)}",
            extra={
                "trace_id": trace_id,
                "policy_id": "generate_script",
                "decision_reason": f"Script generation failed with error: {str(e)}",
            }
        )
        raise HTTPException(status_code=500, detail=f"Script generation failed: {str(e)}")
