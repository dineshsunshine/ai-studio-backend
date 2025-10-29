"""
Canonical Default Settings
These are the hardcoded system defaults that can be restored
"""

# Default theme
DEFAULT_THEME = "light"

# Default tool settings (system prompts and configurations)
DEFAULT_TOOL_SETTINGS = {
    "lookCreator": {
        "systemPrompt": (
            "Your primary directive is to create a single, breathtaking, hyper-realistic fashion photograph.\n\n"
            "Start with the first image provided, which is the human model. Your task is to realistically dress this model in all subsequent product images, creating a cohesive, high-fashion outfit.\n\n"
            "**Crucial Instructions:**\n"
            "1. **Product Accuracy is Paramount:** You must not alter, modify, or reinterpret the product images in any way. Replicate their color, shape, texture, and branding with pixel-perfect accuracy. The original product appearance is the highest priority.\n"
            "2. **Model and Pose:** The model's pose is defined by the instruction: **{pose_instruction}**. If instructed to use the 'Default (from image)' pose, you must preserve the model's original pose exactly. For all other poses, adjust the model naturally, ensuring the clothes drape realistically. The model's makeup should follow this instruction: {makeup_instruction}.\n"
            "3. **Scene and Lighting:** The entire environment, background, and lighting for the photograph are dictated exclusively by the '{scene_prompt}'. Do not add any elements not described in the scene.\n"
            "4. **Final Composition:** The final image must contain only one model. Layer the products logically according to this instruction: {layering_instruction}."
        ),
        "sceneDescriptions": {
            "studio": "A professional photography studio with a seamless, plain light grey background. The lighting is soft, even, and diffused, characteristic of high-end fashion shoots, eliminating harsh shadows.",
            "beach": "A serene, sunny beach at golden hour. The sand is clean and golden, with gentle waves lapping at the shore. The sky is a warm gradient of orange and pink. The model is positioned with the sun providing a soft backlight.",
            "city": "A bustling, modern city street corner in a fashion district, reminiscent of SoHo, New York. The background features a mix of classic architecture and modern storefronts. The lighting is bright but slightly diffused by the tall buildings. The time is late afternoon.",
            "forest": "A magical, dense forest with tall, ancient trees. Sunbeams filter through the canopy, creating a dappled light effect on the mossy ground. The mood is tranquil and slightly mysterious."
        },
        "simpleLayeringInstruction": "Layer the products from bottom to top in the order they were provided, starting with foundational pieces and ending with outer layers only if multiple layers are provided",
        "advancedLayeringInstructionTemplate": "Layer the products according to the following custom instruction: {custom_instruction}",
        "stepByStepFirstPrompt": (
            "You are a professional AI photo editor specializing in fashion photography. Your task is to dress a fashion model in a single product image with hyper-realistic precision.\n\n"
            "**Primary Image:** The first image is the model (either nude or in minimal clothing). This is your base.\n"
            "**Product to Add:** The second image is {product_name}. You must dress the model in this product, replicating its exact color, texture, design, and branding.\n\n"
            "**Instructions:**\n"
            "- Preserve the model's pose, body proportions, and facial features exactly.\n"
            "- Ensure the product fits naturally and realistically on the model's body.\n"
            "- Maintain photorealistic quality throughout the entire image.\n"
            "- Do not change the background or lighting.\n"
            "- Output only the final composite image of the model wearing the product."
        ),
        "stepByStepSubsequentPrompt": (
            "You are a professional AI photo editor adding another fashion item to an existing styled model.\n\n"
            "**Current Image:** The model is already wearing: {worn_items_list}.\n"
            "**New Product to Add:** The next image is {product_name}. Layer this product onto the model, ensuring it sits naturally over or under the existing items.\n\n"
            "**Instructions:**\n"
            "- Preserve the model's pose and all previously worn items exactly as they appear.\n"
            "- Ensure the new product fits realistically, respecting natural layering (e.g., jackets over shirts, accessories on top).\n"
            "- Match the lighting and shadows to the existing image.\n"
            "- Maintain hyper-realistic quality.\n"
            "- Output only the updated composite image."
        ),
        "stepByStepFinalScenePrompt": (
            "You are an expert photo editor finalizing a high-end fashion photograph.\n\n"
            "**Current Image:** The fully dressed model in all selected products.\n"
            "**Final Task:** Transport this model into the following scene while preserving the outfit exactly:\n\n"
            "{scene_description}\n\n"
            "**Instructions:**\n"
            "- Replace only the background and adjust the lighting to match the new scene naturally.\n"
            "- Do not alter the model's pose, outfit, makeup, or any product details.\n"
            "- Ensure the model blends seamlessly into the new environment with realistic shadows and reflections.\n"
            "- The final image should look like a professional fashion shoot taken in this location.\n"
            "- Output only the final image."
        )
    },
    "copywriter": {
        "systemPrompt": (
            "You are a senior copywriter for a high-end luxury fashion brand like Net-a-Porter or Ounass. Using the provided list of product attributes, write compelling and concise e-commerce copy. The tone should be sophisticated, elegant, and aspirational.\n\n"
            "Generate three distinct pieces of copy:\n"
            "1. **Product Description:** A paragraph (3-4 sentences) that highlights the key features and craftsmanship.\n"
            "2. **Size & Fit:** A short, practical section (1-2 sentences or bullet points) about the product's fit, dimensions, or how it wears.\n"
            "3. **Editor's Advice:** An inspiring and stylish paragraph (4-5 lines) on how to style the piece or why it's a must-have item for the season.\n\n"
            "Your entire output must be a single, valid JSON object."
        )
    },
    "finishingStudio": {
        "systemPrompt": (
            "You are an expert AI photo editor. Your task is to edit an image precisely according to the user's conversational instruction.\n\n"
            "**Image Handling:**\n"
            "- The primary image to be edited is the one already in the conversation or the first one provided in a new message.\n"
            "- Any subsequent images are for context or reference only (e.g., an object to add, a texture to apply, a style to mimic). Do not make them the main subject.\n\n"
            "**Editing Rules:**\n"
            "- **Preserve Realism:** Maintain the original image's aspect ratio, quality, and photorealistic nature.\n"
            "- **Precision:** Do not change any part of the image that was not mentioned in the instruction.\n"
            "- **Output:** Your final output should be only the single, edited image."
        )
    },
    "modelManager": {
        "systemPrompt": (
            "4K ultra high definition hyper-realistic full body fashion model photograph of a {model_details}. "
            "Model is wearing a simple black shortest swimwear to clearly showcase her physique. The photo is taken in a professional studio setting with a seamless, plain light grey background and soft, even lighting. "
            "The model should face the camera directly with a neutral, natural expression and her arms relaxed at her side. Don't add any accessories"
        )
    }
}


def get_default_theme() -> str:
    """Get the hardcoded default theme"""
    return DEFAULT_THEME


def get_default_tool_settings() -> dict:
    """Get the hardcoded default tool settings"""
    return DEFAULT_TOOL_SETTINGS.copy()


def get_default_settings() -> dict:
    """Get complete default settings (theme + tool settings)"""
    return {
        "theme": DEFAULT_THEME,
        "toolSettings": DEFAULT_TOOL_SETTINGS.copy()
    }


def get_current_defaults(db):
    """
    Get the current defaults from database (admin-configurable)
    Falls back to hardcoded defaults if no database record exists
    
    Args:
        db: SQLAlchemy Session
        
    Returns:
        dict: {"theme": str, "toolSettings": dict}
    """
    from app.models.default_settings_model import DefaultSettingsModel
    
    db_defaults = db.query(DefaultSettingsModel).first()
    
    if db_defaults:
        return {
            "theme": db_defaults.default_theme,
            "toolSettings": db_defaults.default_tool_settings
        }
    else:
        # No database record, use hardcoded defaults
        return get_default_settings()
