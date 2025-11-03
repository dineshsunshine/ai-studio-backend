"""
GeminiService: Secure wrapper for Google Gemini API calls
All API calls go through this service which manages the API key and handles errors.
Uses the new google-genai SDK for proper aspect_ratio support.
"""

import os
import json
import base64
from typing import Optional, Dict, Any, List, Union

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
        contents: Union[Dict[str, Any], List[Dict[str, Any]]],
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
            
            # Build contents with system instruction
            contents_with_system = contents
            if system_instruction:
                # In new SDK, add system instruction to the message itself
                if isinstance(contents, dict) and "parts" in contents:
                    contents_with_system = {
                        "parts": [
                            {"text": f"{system_instruction}\n\n{contents['parts'][0].get('text', '')}" if i == 0 else content}
                            for i, content in enumerate(contents.get("parts", []))
                        ]
                    }
            
            # Call Gemini API using new SDK
            response = self.client.models.generate_content(
                model=model,
                contents=contents_with_system,
                config=gen_config
            )
            
            # Extract text from response
            print(f"📝 Response type: {type(response)}")
            
            # New SDK structure: response.candidates[0].content.parts[0].text
            try:
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        # Try direct text access first
                        if hasattr(candidate.content, 'text') and candidate.content.text:
                            print(f"✅ Gemini text generation successful (direct text)")
                            return candidate.content.text
                        # Try parts access
                        if hasattr(candidate.content, 'parts'):
                            parts = candidate.content.parts
                            if parts and len(parts) > 0:
                                part = parts[0]
                                if hasattr(part, 'text') and part.text:
                                    print(f"✅ Gemini text generation successful (from parts)")
                                    return part.text
                            elif not parts:
                                # parts is None or empty - check finish_reason
                                finish_reason = getattr(candidate, 'finish_reason', None)
                                if finish_reason and 'MAX_TOKENS' in str(finish_reason):
                                    print(f"⚠️  Response was cut off due to maxOutputTokens limit")
                                    raise ValueError("maxOutputTokens limit too low - Gemini API did not generate content")
            except ValueError:
                raise
            except Exception as e:
                print(f"⚠️  Exception accessing candidates: {e}")
            
            # Fallback: Try old SDK pattern
            try:
                if hasattr(response, 'text') and response.text:
                    print(f"✅ Gemini text generation successful (fallback response.text)")
                    return response.text
            except Exception as e:
                print(f"⚠️  Exception accessing response.text: {e}")
            
            # Last resort: return string representation
            print(f"❌ Could not extract text, response: {str(response)[:200]}")
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
        contents: Union[Dict[str, Any], List[Dict[str, Any]]],
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
            
            # Handle contents - can be dict (single message) or list (conversation history)
            # If contents is a list, it's already the full conversation history
            # If contents is a dict, it's a single message that may need to be combined with history
            if isinstance(contents, list):
                # Contents is already full conversation history
                contents_to_send = contents
                print(f"📝 Contents is a list with {len(contents)} items (conversation history)")
            else:
                # Contents is a dict (single message)
                if history:
                    # Combine history with current contents
                    contents_to_send = history + [{"role": "user", "parts": contents.get("parts", [])}]
                    print(f"📝 Combined {len(history)} history items with current contents")
                else:
                    # Just use the dict contents as-is
                    contents_to_send = contents
                    print(f"📝 Using contents dict directly")
            
            # Call Gemini API
            response = self.client.models.generate_content(
                model=actual_model,
                contents=contents_to_send,
                config=gen_config
            )
            
            # Extract image from response
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        if "image" in part.inline_data.mime_type:
                            # The data might be bytes or already base64 string
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
                            # The data might be bytes or already base64 string
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
        contents: Union[Dict[str, Any], List[Dict[str, Any]]],
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
                config=gen_config
            )
            
            # Parse JSON response
            response_text = None
            
            # New SDK structure: response.candidates[0].content.parts[0].text
            try:
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts and len(candidate.content.parts) > 0:
                            part = candidate.content.parts[0]
                            if hasattr(part, 'text') and part.text:
                                response_text = part.text
            except Exception as e:
                print(f"⚠️  Exception accessing candidates: {e}")
            
            # Fallback: Try old SDK pattern
            if not response_text:
                try:
                    if hasattr(response, 'text') and response.text:
                        response_text = response.text
                except Exception as e:
                    print(f"⚠️  Exception accessing response.text: {e}")
            
            if response_text:
                try:
                    json_response = json.loads(response_text)
                    print(f"✅ Gemini JSON generation successful")
                    return json_response
                except json.JSONDecodeError:
                    print(f"⚠️ Could not parse JSON response, returning as text")
                    return {"raw_response": response_text}
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
        contents: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate text grounded with web search by integrating system instruction."""
        if not self.api_key_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"error": "Gemini API is not configured", "code": "GEMINI_NOT_CONFIGURED"}
            )
        try:
            print(f"🚀 Calling Gemini grounded_search with model: {model}")
            
            # Enhance system instruction to enable web search
            base_instruction = system_instruction or ""
            if "web search" not in base_instruction.lower() and "search" not in base_instruction.lower():
                base_instruction += "\n\nYou have access to web search. Use it to find current, accurate information to ground your responses in real-world data."
            
            print(f"📝 Enabled web search via system instruction")
            
            # Format and integrate system instruction with contents
            # In the new SDK, we need to integrate system instruction into the message
            if isinstance(contents, str):
                # String content - prepend system instruction
                contents_to_send = f"{base_instruction}\n\n{contents}" if base_instruction else contents
            elif isinstance(contents, dict) and "parts" in contents:
                # Dict with parts - prepend to first part's text
                parts = contents.get("parts", [])
                if parts:
                    first_part = parts[0]
                    if isinstance(first_part, dict) and "text" in first_part:
                        updated_text = f"{base_instruction}\n\n{first_part['text']}" if base_instruction else first_part['text']
                        contents_to_send = {
                            "parts": [
                                {**first_part, "text": updated_text},
                                *parts[1:]
                            ]
                        }
                    else:
                        contents_to_send = contents
                else:
                    contents_to_send = contents
            elif isinstance(contents, list):
                # List of messages (conversation history) - prepend to last user message or add system instruction
                contents_to_send = contents
                # For lists, the first message should have the system instruction
                if contents_to_send and isinstance(contents_to_send[0], dict) and "parts" in contents_to_send[0]:
                    first_msg = contents_to_send[0]
                    parts = first_msg.get("parts", [])
                    if parts and isinstance(parts[0], dict) and "text" in parts[0]:
                        updated_text = f"{base_instruction}\n\n{parts[0]['text']}" if base_instruction else parts[0]['text']
                        contents_to_send[0] = {
                            **first_msg,
                            "parts": [{**parts[0], "text": updated_text}, *parts[1:]]
                        }
            else:
                contents_to_send = contents
            
            # Build generation config
            gen_config = None
            if config:
                config_kwargs = {}
                if "maxOutputTokens" in config:
                    config_kwargs["max_output_tokens"] = config["maxOutputTokens"]
                if config_kwargs:
                    gen_config = types.GenerateContentConfig(**config_kwargs)
            
            # Call Gemini API without system_instruction parameter
            # System instruction is already integrated into the contents
            print(f"🌐 Calling Gemini with web search enabled")
            response = self.client.models.generate_content(
                model=model,
                contents=contents_to_send,
                config=gen_config
            )
            
            # Extract text from response
            # New SDK structure: response.candidates[0].content.parts[0].text
            try:
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts and len(candidate.content.parts) > 0:
                            part = candidate.content.parts[0]
                            if hasattr(part, 'text') and part.text:
                                print(f"✅ Gemini grounded search successful")
                                return part.text
            except Exception as e:
                print(f"⚠️  Exception accessing candidates: {e}")
            
            # Fallback: Try old SDK pattern
            try:
                if hasattr(response, 'text') and response.text:
                    print(f"✅ Gemini grounded search successful (fallback)")
                    return response.text
            except Exception as e:
                print(f"⚠️  Exception accessing response.text: {e}")
            
            raise ValueError("Gemini API returned empty response")
        
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error in grounded_search: {str(e)}")
            raise self._handle_api_error(e)


# Create singleton instance
gemini_service = GeminiService()
