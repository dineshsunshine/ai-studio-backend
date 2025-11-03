"""
Gemini API Wrapper Endpoints
All endpoints require JWT authentication and integrate with token consumption system.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import json
import logging

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.services.gemini_service import gemini_service
from app.schemas.gemini import (
    GenerateTextRequest,
    GenerateTextResponse,
    GenerateImageRequest,
    GenerateImageResponse,
    GenerateImagenRequest,
    GenerateImagenResponse,
    GenerateJsonRequest,
    GenerateJsonResponse,
    GroundedSearchRequest,
    GroundedSearchResponse,
)

router = APIRouter(prefix="/gemini", tags=["gemini"])

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# 1. POST /gemini/generate-text
# ============================================================================

@router.post(
    "/generate-text",
    response_model=GenerateTextResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Text",
    description="Generate text using Gemini API. Supports text prompts and images."
)
async def generate_text(
    request: GenerateTextRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate text using Gemini API.
    
    **Authentication:** Required (JWT)
    
    **Parameters:**
    - model: Model name (e.g., "gemini-2.5-flash")
    - systemInstruction: Optional system prompt
    - contents: Content parts (text, images, etc.)
    - config: Optional generation config (maxOutputTokens, etc.)
    
    **Use Cases:**
    - Generate look titles, descriptions, notes
    - Describe models from images
    - Decode scenes from images
    - Image captions
    
    **Returns:**
    - text: Generated text response
    """
    try:
        print(f"🔐 User {current_user.id} calling generate-text endpoint")
        
        # Consume tokens before calling Gemini
        from app.api.v1.endpoints.subscription import consume_tokens_internal
        
        token_result = consume_tokens_internal(
            user_id=str(current_user.id),
            operation="text_to_text",
            description=f"Text generation: {request.model}",
            db=db
        )
        
        if not token_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": token_result["message"],
                    "cost": token_result.get("cost"),
                    "availableTokens": token_result.get("availableTokens")
                }
            )
        
        # Call Gemini service
        result = await gemini_service.generate_text(
            model=request.model,
            system_instruction=request.systemInstruction,
            contents=request.contents,
            config=request.config
        )
        
        print(f"✅ Text generation successful for user {current_user.id}")
        return GenerateTextResponse(text=result)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in generate_text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# 2. POST /gemini/generate-image
# ============================================================================

@router.post(
    "/generate-image",
    response_model=GenerateImageResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Image",
    description="Generate image using Gemini API from text and/or images."
)
async def generate_image(
    http_request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate image using Gemini API.
    
    **Authentication:** Required (JWT)
    
    **Parameters:**
    - model: Model name (e.g., "gemini-2.5-flash-image")
    - systemInstruction: Optional system prompt
    - contents: Content with prompt and images
    - history: Optional multi-turn conversation history
    - config: Generation config (responseModalities, imageConfig, etc.)
    
    **Use Cases:**
    - Create new looks
    - Edit existing looks
    - Continue image editing (chat)
    - Generate board cover images
    - Extract and stage products
    
    **Returns:**
    - imageBase64: Base64-encoded generated image
    """
    try:
        print(f"🔐 User {current_user.id} calling generate-image endpoint")
        
        # ===== LOG RAW REQUEST BODY =====
        try:
            raw_body = await http_request.body()
            raw_json = json.loads(raw_body)
            print(f"\n{'='*80}")
            print(f"📋 RAW REQUEST BODY FOR /generate-image:")
            print(f"{'='*80}")
            
            # Log the structure without huge base64 data
            request_structure = {}
            for key, value in raw_json.items():
                if key == 'history' and isinstance(value, list):
                    request_structure[key] = f"<list with {len(value)} items>"
                elif isinstance(value, str) and len(str(value)) > 200:
                    request_structure[key] = f"<{len(str(value))} char string>"
                elif isinstance(value, dict):
                    request_structure[key] = f"<dict with keys: {list(value.keys())}>"
                else:
                    request_structure[key] = value
            
            print(json.dumps(request_structure, indent=2))
            print(f"{'='*80}\n")
        except Exception as log_error:
            print(f"⚠️  Could not log raw request: {log_error}")
        
        # ===== VALIDATE AGAINST SCHEMA =====
        try:
            request_data = json.loads(raw_body)
            request = GenerateImageRequest(**request_data)
            print(f"✅ Request validated successfully against GenerateImageRequest schema")
            print(f"   - model: {request.model}")
            print(f"   - systemInstruction: {'present' if request.systemInstruction else 'not set'}")
            print(f"   - contents type: {type(request.contents).__name__}")
            print(f"   - history: {'present' if request.history else 'not set'} ({len(request.history or []) if request.history else 0} items)")
            print(f"   - config: {'present' if request.config else 'not set'}")
            if request.config:
                print(f"     - config keys: {list(request.config.keys())}")
        except Exception as validation_error:
            print(f"❌ VALIDATION ERROR against schema:")
            print(f"   {validation_error}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "Request body does not match expected schema",
                    "validation_error": str(validation_error),
                    "expected_fields": ["model", "contents"],
                    "optional_fields": ["systemInstruction", "history", "config"]
                }
            )
        
        # Consume tokens before calling Gemini
        from app.api.v1.endpoints.subscription import consume_tokens_internal
        
        token_result = consume_tokens_internal(
            user_id=str(current_user.id),
            operation="multi_modal",
            description=f"Image generation: {request.model}",
            db=db
        )
        
        if not token_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": token_result["message"],
                    "cost": token_result.get("cost"),
                    "availableTokens": token_result.get("availableTokens")
                }
            )
        
        # Call Gemini service
        result = await gemini_service.generate_image(
            model=request.model,
            system_instruction=request.systemInstruction,
            contents=request.contents,
            history=request.history,
            config=request.config
        )
        
        print(f"✅ Image generation successful for user {current_user.id}")
        return GenerateImageResponse(imageBase64=result)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in generate_image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# 3. POST /gemini/generate-imagen
# ============================================================================

@router.post(
    "/generate-imagen",
    response_model=GenerateImagenResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate High-Quality Image (Imagen)",
    description="Generate high-quality images using Imagen model."
)
async def generate_imagen(
    request: GenerateImagenRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate high-quality image using Imagen model.
    
    **Authentication:** Required (JWT)
    
    **Parameters:**
    - prompt: Text prompt for image generation
    - config: Generation config (numberOfImages, aspectRatio, etc.)
    
    **Use Cases:**
    - Generate hyper-realistic fashion model images
    - Create high-quality product images
    
    **Returns:**
    - imageBase64: Base64-encoded generated image
    """
    try:
        print(f"🔐 User {current_user.id} calling generate-imagen endpoint")
        
        # Consume tokens before calling Gemini
        from app.api.v1.endpoints.subscription import consume_tokens_internal
        
        token_result = consume_tokens_internal(
            user_id=str(current_user.id),
            operation="text_to_image",
            description=f"Imagen generation: {request.prompt[:50]}...",
            db=db
        )
        
        if not token_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": token_result["message"],
                    "cost": token_result.get("cost"),
                    "availableTokens": token_result.get("availableTokens")
                }
            )
        
        # Call Gemini service
        result = await gemini_service.generate_imagen(
            prompt=request.prompt,
            config=request.config
        )
        
        print(f"✅ Imagen generation successful for user {current_user.id}")
        return GenerateImagenResponse(imageBase64=result)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in generate_imagen: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# 4. POST /gemini/generate-json
# ============================================================================

@router.post(
    "/generate-json",
    status_code=status.HTTP_200_OK,
    summary="Generate Structured JSON",
    description="Generate structured JSON responses using Gemini API."
)
async def generate_json(
    request: GenerateJsonRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate structured JSON responses using Gemini API.
    
    **Authentication:** Required (JWT)
    
    **Parameters:**
    - model: Model name (e.g., "gemini-2.5-flash")
    - systemInstruction: Optional system prompt
    - contents: Content to process
    - config: Generation config (responseMimeType, responseSchema, etc.)
    - taskType: Optional task identifier for response transformation
      - IMPROVE_SYSTEM_PROMPT: Return raw JSON object
      - GENERATE_VIDEO_PROMPTS: Wrap array in { "prompts": [...] }
      - ANALYZE_PRODUCT_IMAGE: Wrap array in { "attributes": [...] }
      - GENERATE_PRODUCT_COPY: Wrap object in { "copy": {...} }
    
    **Use Cases:**
    - Improve system prompts (returns JSON with improvements)
    - Analyze products from images (structured data)
    - Generate product copy (structured fields)
    - Generate video prompts from images
    
    **Returns:**
    - JSON object matching the specified responseSchema or task type format
    """
    try:
        print(f"🔐 User {current_user.id} calling generate-json endpoint")
        
        # Consume tokens before calling Gemini
        from app.api.v1.endpoints.subscription import consume_tokens_internal
        
        token_result = consume_tokens_internal(
            user_id=str(current_user.id),
            operation="text_to_text",
            description=f"JSON generation: {request.model}",
            db=db
        )
        
        if not token_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": token_result["message"],
                    "cost": token_result.get("cost"),
                    "availableTokens": token_result.get("availableTokens")
                }
            )
        
        # Call Gemini service
        result = await gemini_service.generate_json(
            model=request.model,
            system_instruction=request.systemInstruction,
            contents=request.contents,
            config=request.config
        )
        
        print(f"✅ JSON generation successful for user {current_user.id}")
        
        # Transform response based on taskType
        task_type = request.taskType or ""
        print(f"📝 Task type: {task_type}")
        
        if task_type == "GENERATE_VIDEO_PROMPTS":
            # Wrap array in { "prompts": [...] }
            if isinstance(result, list):
                print(f"🎬 Transforming response for GENERATE_VIDEO_PROMPTS")
                transformed = {
                    "prompts": result,
                    "cost": token_result.get("cost", 0)
                }
            else:
                print(f"⚠️  Expected array for GENERATE_VIDEO_PROMPTS, got object")
                transformed = {
                    "prompts": result if isinstance(result, list) else [result],
                    "cost": token_result.get("cost", 0)
                }
        
        elif task_type == "ANALYZE_PRODUCT_IMAGE":
            # Wrap array in { "attributes": [...] }
            if isinstance(result, list):
                print(f"🖼️  Transforming response for ANALYZE_PRODUCT_IMAGE")
                transformed = {
                    "attributes": result,
                    "cost": token_result.get("cost", 0)
                }
            else:
                print(f"⚠️  Expected array for ANALYZE_PRODUCT_IMAGE, got object")
                transformed = {
                    "attributes": result if isinstance(result, list) else [result],
                    "cost": token_result.get("cost", 0)
                }
        
        elif task_type == "GENERATE_PRODUCT_COPY":
            # Wrap object in { "copy": {...} }
            if isinstance(result, dict):
                print(f"📝 Transforming response for GENERATE_PRODUCT_COPY")
                transformed = {
                    "copy": result,
                    "cost": token_result.get("cost", 0)
                }
            else:
                print(f"⚠️  Expected object for GENERATE_PRODUCT_COPY, got array")
                transformed = {
                    "copy": result if isinstance(result, dict) else {"raw": result},
                    "cost": token_result.get("cost", 0)
                }
        
        else:
            # IMPROVE_SYSTEM_PROMPT or no taskType: Return raw result
            if task_type == "IMPROVE_SYSTEM_PROMPT":
                print(f"✨ Returning raw JSON for IMPROVE_SYSTEM_PROMPT")
            else:
                print(f"📊 No taskType specified, returning raw JSON")
            transformed = result
        
        # Return JSON response without Pydantic validation
        # This handles cases where the response is a list, dict, or any JSON structure
        return JSONResponse(content=transformed, status_code=status.HTTP_200_OK)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in generate_json: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# 5. POST /gemini/grounded-search
# ============================================================================

@router.post(
    "/grounded-search",
    response_model=GroundedSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate with Google Search",
    description="Generate text grounded with real-time Google Search results."
)
async def grounded_search(
    request: GroundedSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate text grounded with Google Search results.
    
    **Authentication:** Required (JWT)
    
    **Parameters:**
    - model: Model name (e.g., "gemini-2.5-flash")
    - systemInstruction: Optional system prompt
    - contents: Text content or brand/product information
    - config: Generation config (tools array with googleSearch)
    
    **Use Cases:**
    - Analyze products from text (grounded in web search)
    - Research competitors
    - Get real-time product information
    
    **Returns:**
    - text: Search-grounded text response (may be JSON or plain text)
    """
    try:
        print(f"🔐 User {current_user.id} calling grounded-search endpoint")
        
        # Consume tokens before calling Gemini
        from app.api.v1.endpoints.subscription import consume_tokens_internal
        
        token_result = consume_tokens_internal(
            user_id=str(current_user.id),
            operation="text_to_text",
            description=f"Grounded search: {request.model}",
            db=db
        )
        
        if not token_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": token_result["message"],
                    "cost": token_result.get("cost"),
                    "availableTokens": token_result.get("availableTokens")
                }
            )
        
        # Call Gemini service
        result = await gemini_service.grounded_search(
            model=request.model,
            system_instruction=request.systemInstruction,
            contents=request.contents,
            config=request.config
        )
        
        print(f"✅ Grounded search successful for user {current_user.id}")
        return GroundedSearchResponse(text=result)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in grounded_search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
