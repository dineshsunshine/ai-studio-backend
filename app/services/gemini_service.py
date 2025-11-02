"""
GeminiService: Secure wrapper for Google Gemini API calls
All API calls go through this service which manages the API key and handles errors.
Uses the new google-genai SDK for proper aspect_ratio support.
"""

import os
import json
import base64
from typing import Optional, Dict, Any, List

from google import genai
from google.genai import types
from fastapi import HTTPException, status


class GeminiService:
    """Service for making secure Gemini API calls with proper error handling."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern - create only one instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Gemini service with API key from environment."""
        # Only initialize once
        if self._initialized:
            return
        
        # Use GOOGLE_API_KEY (same as GEMINI_API_KEY)
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️  GOOGLE_API_KEY not set - Gemini endpoints will return errors until API key is configured")
            self.api_key_configured = False
            self.client = None
            return
        
        self.client = genai.Client(api_key=api_key)
        self.request_timeout = int(os.getenv("GEMINI_REQUEST_TIMEOUT", "60"))
        self.max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "2"))
        self.api_key_configured = True
        GeminiService._initialized = True
        print(f"✅ GeminiService initialized with GOOGLE_API_KEY - timeout={self.request_timeout}s, max_retries={self.max_retries}")
    
    def _handle_api_error(self, error: Exception) -> HTTPException:
        """Convert Gemini API errors to appropriate HTTP exceptions."""
        error_str = str(error).lower()
        error_message = str(error)
        
        # Check for specific error types
        if "api_key" in error_str or "authentication" in error_str or "unauthorized" in error_str:
            print(f"❌ Gemini Auth Error: {error_message}")
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Gemini API authentication failed", "code": "GEMINI_AUTH_ERROR"}
            )
        
        if "rate limit" in error_str or "quota" in error_str:
            print(f"❌ Gemini Rate Limit: {error_message}")
            return HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={"error": "Gemini API rate limit exceeded", "code": "GEMINI_RATE_LIMIT"}
            )
        
        if "invalid" in error_str or "bad request" in error_str:
            print(f"❌ Gemini Bad Request: {error_message}")
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": f"The Gemini API returned an error: {error_message}", "code": "GEMINI_BAD_REQUEST"}
            )
        
        # Default to service unavailable for other errors
        print(f"❌ Gemini API Error: {error_message}")
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": f"The Gemini API returned an error: {error_message}", "code": "GEMINI_API_ERROR"}
        )
    
    async def generate_text(
        self,
        model: str,
        system_instruction: Optional[str],
        contents: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate text using Gemini API."""
        if not self.api_key_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"error": "Gemini API is not configured", "code": "GEMINI_NOT_CONFIGURED"}
            )
        try:
            print(f"🚀 Calling Gemini generate_text with model: {model}")
            
            # Build generation config if needed
            gen_config = None
            if config and "maxOutputTokens" in config:
                gen_config = types.GenerateContentConfig(
                    max_output_tokens=config["maxOutputTokens"]
                )
            
            # Call Gemini API using new SDK
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=gen_config,
                system_instruction=system_instruction
            )
            
            # Extract text from response
            if response.text:
                print(f"✅ Gemini text generation successful")
                return response.text
            else:
                raise ValueError("Gemini API returned empty response")
        
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error in generate_text: {str(e)}")
            raise self._handle_api_error(e)
    
    async def generate_image(
        self,
        model: str,
        system_instruction: Optional[str],
        contents: Dict[str, Any],
        history: Optional[List[Dict[str, Any]]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate image using Gemini API with aspect ratio support."""
        if not self.api_key_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"error": "Gemini API is not configured", "code": "GEMINI_NOT_CONFIGURED"}
            )
        try:
            print(f"🚀 Calling Gemini generate_image with model: {model}")
            
            # Use gemini-2.5-flash-image for image generation
            actual_model = "gemini-2.5-flash-image"
            print(f"📝 Using model: {actual_model} for image generation")
            
            # Build generation config with image_config for aspect ratio
            gen_config = None
            if config:
                image_config = None
                if "imageConfig" in config:
                    aspect_ratio = config["imageConfig"].get("aspectRatio")
                    if aspect_ratio:
                        image_config = types.ImageConfig(aspect_ratio=aspect_ratio)
                        print(f"📐 Setting aspect ratio: {aspect_ratio}")
                
                response_modalities = config.get("responseModalities")
                
                gen_config = types.GenerateContentConfig(
                    image_config=image_config,
                    response_modalities=response_modalities if response_modalities else None
                )
            
            # Build content for multi-turn if history is provided
            if history:
                contents_to_send = history + [{"role": "user", "parts": contents.get("parts", [])}]
            else:
                contents_to_send = contents
            
            # Call Gemini API
            response = self.client.models.generate_content(
                model=actual_model,
                contents=contents_to_send,
                config=gen_config,
                system_instruction=system_instruction
            )
            
            # Extract image from response
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        if "image" in part.inline_data.mime_type:
                            # The data is already base64
                            image_base64 = part.inline_data.data
                            print(f"✅ Gemini image generation successful")
                            return image_base64
            
            raise ValueError("Gemini API did not return a valid image")
        
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error in generate_image: {str(e)}")
            raise self._handle_api_error(e)
    
    async def generate_imagen(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate high-quality image using gemini-2.5-flash-image with aspect ratio support."""
        if not self.api_key_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"error": "Gemini API is not configured", "code": "GEMINI_NOT_CONFIGURED"}
            )
        try:
            print(f"🚀 Calling Gemini generate_imagen with prompt: {prompt[:50]}...")
            
            # Use gemini-2.5-flash-image for high-quality image generation
            model = "gemini-2.5-flash-image"
            print(f"📝 Using model: {model} for high-quality image generation")
            
            # Build generation config with image_config for aspect ratio
            gen_config = None
            if config and "aspectRatio" in config:
                image_config = types.ImageConfig(aspect_ratio=config["aspectRatio"])
                print(f"📐 Setting aspect ratio: {config['aspectRatio']}")
                gen_config = types.GenerateContentConfig(image_config=image_config)
                if "numberOfImages" in config:
                    print(f"🖼️ Number of images requested: {config['numberOfImages']}")
            
            # Call generate_content
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=gen_config
            )
            
            # Extract image and encode as base64
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        if "image" in part.inline_data.mime_type:
                            # The data is already base64
                            image_base64 = part.inline_data.data
                            print(f"✅ Image generation successful with gemini-2.5-flash-image")
                            return image_base64
            
            raise ValueError("Image generation did not return a valid image")
        
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error in generate_imagen: {str(e)}")
            raise self._handle_api_error(e)
    
    async def generate_json(
        self,
        model: str,
        system_instruction: Optional[str],
        contents: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON response using Gemini API."""
        if not self.api_key_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"error": "Gemini API is not configured", "code": "GEMINI_NOT_CONFIGURED"}
            )
        try:
            print(f"🚀 Calling Gemini generate_json with model: {model}")
            
            # Build generation config with response schema
            gen_config = None
            if config:
                response_schema = config.get("responseSchema")
                gen_config = types.GenerateContentConfig(
                    response_mime_type=config.get("responseMimeType", "application/json"),
                    response_schema=response_schema if response_schema else None
                )
            
            # Call Gemini API
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=gen_config,
                system_instruction=system_instruction
            )
            
            # Parse JSON response
            if response.text:
                try:
                    json_response = json.loads(response.text)
                    print(f"✅ Gemini JSON generation successful")
                    return json_response
                except json.JSONDecodeError:
                    print(f"⚠️ Could not parse JSON response, returning as text")
                    return {"raw_response": response.text}
            else:
                raise ValueError("Gemini API returned empty response")
        
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error in generate_json: {str(e)}")
            raise self._handle_api_error(e)
    
    async def grounded_search(
        self,
        model: str,
        system_instruction: Optional[str],
        contents: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate text grounded with Google Search results."""
        if not self.api_key_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"error": "Gemini API is not configured", "code": "GEMINI_NOT_CONFIGURED"}
            )
        try:
            print(f"🚀 Calling Gemini grounded_search with model: {model}")
            
            # Build tools list with google_search
            tools = []
            if config and "tools" in config:
                # Parse tools from config
                if isinstance(config["tools"], list):
                    for tool in config["tools"]:
                        if isinstance(tool, dict) and "googleSearch" in tool:
                            tools.append(types.Tool.from_dict({"google_search": {}}))
            
            # Call Gemini API with tools
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                system_instruction=system_instruction,
                tools=tools if tools else [types.Tool.from_dict({"google_search": {}})]
            )
            
            # Extract text from response
            if response.text:
                print(f"✅ Gemini grounded search successful")
                return response.text
            else:
                raise ValueError("Gemini API returned empty response")
        
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error in grounded_search: {str(e)}")
            raise self._handle_api_error(e)


# Create singleton instance
gemini_service = GeminiService()
