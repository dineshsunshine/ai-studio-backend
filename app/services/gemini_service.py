"""
GeminiService: Secure wrapper for Google Gemini API calls
All API calls go through this service which manages the API key and handles errors.
"""

import os
import json
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
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
            return
        
        genai.configure(api_key=api_key)
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
    
    def _convert_base64_to_inline_data(self, mime_type: str, base64_data: str) -> Dict[str, Any]:
        """Convert base64 string to Gemini inline data format."""
        return {
            "inlineData": {
                "mimeType": mime_type,
                "data": base64_data
            }
        }
    
    def _validate_image_size(self, base64_data: str, max_mb: float = 5.0) -> None:
        """Validate that base64 image doesn't exceed max size."""
        # Rough estimate: 1MB ≈ 1.33M base64 chars (4 base64 chars = 3 bytes)
        max_chars = int(max_mb * 1024 * 1024 * 4 / 3)
        if len(base64_data) > max_chars:
            raise ValueError(f"Image size exceeds {max_mb}MB limit")
    
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
            
            # Build request parameters
            kwargs = {
                "model": model,
                "contents": contents,
            }
            
            if system_instruction:
                kwargs["system_instruction"] = system_instruction
            
            if config:
                # Map config to GenerationConfig
                if "maxOutputTokens" in config:
                    kwargs["generation_config"] = {
                        "max_output_tokens": config["maxOutputTokens"]
                    }
            
            # Call Gemini API
            model_obj = genai.GenerativeModel(
                model_name=model,
                system_instruction=system_instruction
            )
            response = model_obj.generate_content(
                contents,
                generation_config=kwargs.get("generation_config")
            )
            
            # Extract text from response
            if response.text:
                print(f"✅ Gemini text generation successful")
                return response.text
            else:
                raise ValueError("Gemini API returned empty response")
        
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
        """Generate image using Gemini API."""
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
            
            # Build request parameters
            kwargs = {
                "model": actual_model,
                "contents": contents,
            }
            
            if system_instruction:
                kwargs["system_instruction"] = system_instruction
            
            # Add generation config
            gen_config = {}
            if config:
                if "responseModalities" in config:
                    gen_config["response_modalities"] = config["responseModalities"]
                if "imageConfig" in config and "aspectRatio" in config["imageConfig"]:
                    gen_config["aspect_ratio"] = config["imageConfig"]["aspectRatio"]
            
            if gen_config:
                kwargs["generation_config"] = gen_config
            
            # Call Gemini API
            model_obj = genai.GenerativeModel(
                model_name=actual_model,
                system_instruction=system_instruction
            )
            
            # Build content for multi-turn if history is provided
            if history:
                response = model_obj.generate_content(
                    history + [{"role": "user", "parts": contents.get("parts", [])}]
                )
            else:
                response = model_obj.generate_content(contents)
            
            # Extract image from response
            if response.data and hasattr(response.data, 'mime_type'):
                if "image" in response.data.mime_type:
                    # Ensure data is base64 encoded string
                    if isinstance(response.data, bytes):
                        image_base64 = base64.b64encode(response.data).decode('utf-8')
                    else:
                        image_base64 = str(response.data)
                    print(f"✅ Gemini image generation successful")
                    return image_base64
            
            # Try to get image from parts
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        if "image" in part.inline_data.mime_type:
                            # The data might already be base64 or raw bytes
                            data = part.inline_data.data
                            if isinstance(data, bytes):
                                # If it's raw bytes, encode to base64
                                image_base64 = base64.b64encode(data).decode('utf-8')
                            else:
                                # If it's already a string (base64), use as-is
                                image_base64 = str(data)
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
        """Generate high-quality image using gemini-2.5-flash-image model."""
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
            
            # Build request
            model_obj = genai.GenerativeModel(model_name=model)
            response = model_obj.generate_content(prompt)
            
            # Extract image and encode as base64
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        if "image" in part.inline_data.mime_type:
                            # The data might already be base64 or raw bytes
                            data = part.inline_data.data
                            if isinstance(data, bytes):
                                # If it's raw bytes, encode to base64
                                image_base64 = base64.b64encode(data).decode('utf-8')
                            else:
                                # If it's already a string (base64), use as-is
                                image_base64 = str(data)
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
            
            # Build request with schema
            kwargs = {
                "model": model,
                "contents": contents,
            }
            
            if system_instruction:
                kwargs["system_instruction"] = system_instruction
            
            # Add generation config with response schema
            gen_config = {}
            if config:
                if "responseMimeType" in config:
                    gen_config["response_mime_type"] = config["responseMimeType"]
                if "responseSchema" in config:
                    gen_config["response_schema"] = config["responseSchema"]
            
            # Call Gemini API
            model_obj = genai.GenerativeModel(
                model_name=model,
                system_instruction=system_instruction,
                generation_config=genai.types.GenerationConfig(**gen_config) if gen_config else None
            )
            response = model_obj.generate_content(contents)
            
            # Parse JSON response
            if response.text:
                try:
                    # Try to parse the response as JSON
                    json_response = json.loads(response.text)
                    print(f"✅ Gemini JSON generation successful")
                    return json_response
                except json.JSONDecodeError:
                    # If parsing fails, return the text wrapped
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
            
            # Build request with Google Search tool
            kwargs = {
                "model": model,
                "contents": contents,
            }
            
            if system_instruction:
                kwargs["system_instruction"] = system_instruction
            
            # Add tools
            tools = []
            if config and "tools" in config:
                tools = config["tools"]
            else:
                tools = [{"google_search": {}}]
            
            # Call Gemini API with tools
            model_obj = genai.GenerativeModel(
                model_name=model,
                system_instruction=system_instruction,
                tools=tools
            )
            response = model_obj.generate_content(contents)
            
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
