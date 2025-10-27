"""
AI Image Generation service using Google's Gemini Imagen model
"""
import os
import base64
from typing import Optional
import io


class AIGenerationService:
    """
    Service for generating images using Google's Gemini Imagen model
    """
    
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.model_name = "imagen-3.0-generate-001"  # Using Imagen 3.0 as 4.0 may not be available yet
        
        self.client = None
        self.enabled = os.getenv("ENABLE_AI_GENERATION", "false").lower() == "true"
        
        if self.enabled and self.project_id:
            try:
                import vertexai
                from vertexai.preview.vision_models import ImageGenerationModel
                
                vertexai.init(project=self.project_id, location=self.location)
                self.client = ImageGenerationModel.from_pretrained(self.model_name)
                print(f"✅ AI Generation enabled with model: {self.model_name}")
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize AI generation: {e}")
                self.enabled = False
    
    def generate_image(self, prompt: str, model_name: str) -> bytes:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description for image generation
            model_name: Name of the model (for context in the prompt)
            
        Returns:
            Image data as bytes
        """
        if not self.enabled:
            raise Exception("AI generation is not enabled. Set ENABLE_AI_GENERATION=true and configure Google Cloud credentials.")
        
        # Construct full prompt for fashion model generation
        full_prompt = self._construct_fashion_prompt(prompt, model_name)
        
        try:
            # Generate image using Imagen
            response = self.client.generate_images(
                prompt=full_prompt,
                number_of_images=1,
                aspect_ratio="9:16",  # Portrait orientation for fashion models
                safety_filter_level="block_some",
                person_generation="allow_adult",
            )
            
            # Get the first generated image
            generated_image = response.images[0]
            
            # Convert to bytes
            image_bytes = generated_image._image_bytes
            
            return image_bytes
        except Exception as e:
            raise Exception(f"Failed to generate image: {str(e)}")
    
    def _construct_fashion_prompt(self, prompt_details: str, model_name: str) -> str:
        """
        Construct a detailed prompt for fashion model generation.
        
        Args:
            prompt_details: User-provided details about the model
            model_name: Name of the model
            
        Returns:
            Complete prompt for image generation
        """
        base_prompt = (
            f"A professional, high-quality fashion photograph of a model named {model_name}. "
            f"Full-body shot, studio lighting, clean white background. "
            f"The model is {prompt_details}. "
            f"Professional fashion photography, 8K resolution, detailed, realistic, "
            f"fashion editorial style, elegant pose, confident expression."
        )
        return base_prompt
    
    def generate_mock_image(self) -> bytes:
        """
        Generate a mock/placeholder image for testing when AI generation is disabled.
        
        Returns:
            Mock image data as bytes
        """
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple placeholder image
        img = Image.new('RGB', (720, 1280), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = "AI Generation\nDisabled\n\nMock Image"
        bbox = draw.textbbox((0, 0), text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((720 - text_width) // 2, (1280 - text_height) // 2)
        draw.text(position, text, fill=(100, 100, 100))
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.read()


# Global AI generation service instance
ai_generation_service = AIGenerationService()


