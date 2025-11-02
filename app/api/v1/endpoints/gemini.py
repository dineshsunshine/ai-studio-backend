"""
Gemini API Wrapper Endpoints
All endpoints require JWT authentication and integrate with token consumption system.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
    request: GenerateImageRequest,
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
    response_model=GenerateJsonResponse,
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
    
    **Use Cases:**
    - Improve system prompts (returns JSON with improvements)
    - Analyze products from images (structured data)
    - Generate product copy (structured fields)
    - Generate video prompts from images
    
    **Returns:**
    - JSON object matching the specified responseSchema
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
        return result
    
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
