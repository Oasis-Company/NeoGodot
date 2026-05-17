from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uuid
import time
import sys
import os

from dotenv import load_dotenv

from models.responses import HealthResponse, ErrorResponse, DependencyStatus
from routes import generate_router
from metrics import metrics_router
from config import ConfigManager, get_config, ConfigError
from logger import setup_logger
from websocket.manager import ConnectionManager
from websocket.protocol import MessageType, StreamMessage, parse_message
from rate_limiter import RateLimiter


logger = logging.getLogger("neogodot-runtime")
config: ConfigManager = None
start_time: float = 0


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"[INFO] Loaded environment from {env_path}")
    else:
        print(f"[INFO] No .env file found at {env_path}, using defaults")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global config, logger, start_time
    
    try:
        load_env()
        config = get_config()
        start_time = time.time()
        
        log_level = getattr(logging, config.log_level, logging.INFO)
        logger = setup_logger("neogodot-runtime", level=log_level, service="runtime")
        
        logger.info("=" * 50)
        logger.info("NeoGodot Runtime Gateway Starting", extra={
            "service": "runtime",
            "version": config.version,
            "host": config.host,
            "port": config.port,
            "debug": config.debug,
            "log_level": config.log_level
        })
        logger.info("=" * 50)
        
        if config.debug:
            logger.debug("Debug mode enabled")
            logger.debug(f"Loaded config: {vars(config)}")
        
        # 预热机制
        logger.info("Preheating services...", extra={"service": "runtime"})
        
        # 预加载缓存和配置
        from services.generation_service import GenerationService
        generation_service = GenerationService()
        app.state.generation_service = generation_service
        logger.info("Service preheating complete", extra={"service": "runtime"})
        
        yield
        
        logger.info("NeoGodot Runtime service shutting down", extra={"service": "runtime"})
        
        # 清理：关闭连接池
        try:
            if hasattr(generation_service, 'openai_provider') and hasattr(generation_service.openai_provider, 'close'):
                await generation_service.openai_provider.close()
            if hasattr(generation_service, 'anthropic_provider') and hasattr(generation_service.anthropic_provider, 'close'):
                await generation_service.anthropic_provider.close()
        except Exception as e:
            logger.error(f"Error during shutdown cleanup: {e}", extra={"error": str(e)})
            
    except ConfigError as e:
        print(f"[ERROR] Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to start service: {e}")
        sys.exit(1)


app = FastAPI(
    title="NeoGodot Runtime API",
    description="Runtime service for NeoGodot AI-powered game development",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(generate_router)
app.include_router(metrics_router)

ws_manager = ConnectionManager()
rate_limiter = RateLimiter(requests_per_second=10.0, capacity=20.0)


@app.on_event("startup")
async def startup_event():
    if config:
        logger.debug("Configuring CORS middleware", extra={
            "allowed_origins": config.allowed_origins
        })
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins if config else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加 Gzip 压缩中间件
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,  # 只压缩超过 1KB 的响应
    )


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    return await rate_limiter(request, call_next)


@app.middleware("http")
async def add_trace_id_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
    request.state.trace_id = trace_id

    start_time = time.time()
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={"trace_id": trace_id, "method": request.method, "path": request.url.path},
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Process-Time"] = str(process_time)

        logger.info(
            f"Request completed: {request.method} {request.url.path}",
            extra={
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
            },
        )
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            extra={
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "process_time": process_time,
            },
        )
        raise


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    trace_id = getattr(request.state, "trace_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code=f"HTTP_{exc.status_code}",
            trace_id=trace_id,
        ).model_dump(exclude_none=True),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", None)
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"trace_id": trace_id, "error": str(exc)},
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            code="INTERNAL_ERROR",
            trace_id=trace_id,
            details={"exception": str(exc)} if logger.level <= logging.DEBUG else None,
        ).model_dump(exclude_none=True),
    )


@app.get("/v1/health", response_model=HealthResponse)
async def health_check():
    from datetime import datetime
    from providers.provider_factory import ProviderFactory
    
    providers_status = []
    
    # Check OpenAI provider status
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        providers_status.append(DependencyStatus(
            name="openai",
            status="connected" if len(openai_key) > 20 else "not_configured",
            model="gpt-4o"
        ))
    else:
        providers_status.append(DependencyStatus(
            name="openai",
            status="not_configured"
        ))
    
    # Check Anthropic provider status
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        providers_status.append(DependencyStatus(
            name="anthropic",
            status="connected" if len(anthropic_key) > 20 else "not_configured",
            model="claude-3-5-sonnet-20241022"
        ))
    else:
        providers_status.append(DependencyStatus(
            name="anthropic",
            status="not_configured"
        ))
    
    uptime_seconds = time.time() - start_time if start_time > 0 else 0
    
    response = HealthResponse(
        status="healthy",
        version=config.version if config else "1.0.0",
        uptime=uptime_seconds,
        providers=providers_status
    )
    
    logger.debug("Health check requested", extra={
        "status": response.status,
        "version": response.version,
        "timestamp": response.timestamp.isoformat(),
        "uptime": uptime_seconds,
        "providers": [{"name": p.name, "status": p.status} for p in providers_status]
    })
    
    return response


@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    connection_id = await ws_manager.connect(websocket)
    trace_id = str(uuid.uuid4())
    logger.info(f"WebSocket connected", extra={"connection_id": connection_id, "trace_id": trace_id})

    try:
        await ws_manager.send_message(
            connection_id,
            StreamMessage(
                type=MessageType.PONG,
                connection_id=connection_id,
                trace_id=trace_id,
            ).model_dump(),
        )

        while True:
            data = await websocket.receive_text()
            message = parse_message(data)

            if "error" in message:
                await ws_manager.send_message(
                    connection_id,
                    StreamMessage(
                        type=MessageType.ERROR,
                        connection_id=connection_id,
                        error=message["error"],
                        trace_id=trace_id,
                    ).model_dump(),
                )
                continue

            msg_type = message.get("type")

            if msg_type == MessageType.PING:
                await ws_manager.send_message(
                    connection_id,
                    StreamMessage(
                        type=MessageType.PONG,
                        connection_id=connection_id,
                        trace_id=trace_id,
                    ).model_dump(),
                )
            elif msg_type == MessageType.GENERATE:
                task_id = str(uuid.uuid4())
                await ws_manager.send_message(
                    connection_id,
                    StreamMessage(
                        type=MessageType.GENERATION_COMPLETE,
                        connection_id=connection_id,
                        task_id=task_id,
                        payload={"message": "Generation completed", "task_id": task_id},
                        trace_id=trace_id,
                    ).model_dump(),
                )
            else:
                await ws_manager.send_message(
                    connection_id,
                    StreamMessage(
                        type=MessageType.ERROR,
                        connection_id=connection_id,
                        error=f"Unknown message type: {msg_type}",
                        trace_id=trace_id,
                    ).model_dump(),
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected", extra={"connection_id": connection_id})
    except Exception as e:
        logger.error(f"WebSocket error", extra={"connection_id": connection_id, "error": str(e)}, exc_info=True)
    finally:
        await ws_manager.disconnect(connection_id)


if __name__ == "__main__":
    import uvicorn
    
    try:
        load_env()
        config = get_config()
        
        print("=" * 50)
        print("NeoGodot Runtime Gateway")
        print("=" * 50)
        print(f"Host: {config.host}")
        print(f"Port: {config.port}")
        print(f"Debug: {config.debug}")
        print(f"Log Level: {config.log_level}")
        print(f"Version: {config.version}")
        print("=" * 50)
        print(f"Starting server on http://{config.host}:{config.port}")
        print(f"API Documentation: http://{config.host}:{config.port}/docs")
        print(f"Health Check: http://{config.host}:{config.port}/v1/health")
        print("=" * 50)
        
        uvicorn.run(
            "main:app",
            host=config.host,
            port=config.port,
            reload=config.debug,
            log_level=config.log_level.lower(),
        )
    except ConfigError as e:
        print(f"\n[ERROR] Configuration Error: {e}\n")
        print("Please check your .env file and try again.")
        print("See runtime/README.md for more information about environment variables.\n")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INFO] Service stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Failed to start service: {e}\n")
        sys.exit(1)
