"""
Pydantic Schemas for User Settings
"""
from typing import Dict, Optional, Literal
from pydantic import BaseModel, Field, field_validator


# Scene descriptions for Look Creator
class SceneDescriptions(BaseModel):
    studio: str = Field(..., min_length=1, description="Studio scene description")
    beach: str = Field(..., min_length=1, description="Beach scene description")
    city: str = Field(..., min_length=1, description="City scene description")
    forest: str = Field(..., min_length=1, description="Forest scene description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "studio": "A clean, minimalist photography studio with soft lighting...",
                "beach": "A serene beach setting during golden hour...",
                "city": "An urban cityscape with modern architecture...",
                "forest": "A lush forest clearing with natural light..."
            }
        }


# Look Creator settings
class LookCreatorSettings(BaseModel):
    systemPrompt: str = Field(..., min_length=1, description="System prompt for Look Creator AI")
    sceneDescriptions: SceneDescriptions
    simpleLayeringInstruction: str = Field(..., min_length=1, description="Layering instruction for Simple Mode")
    advancedLayeringInstructionTemplate: str = Field(..., min_length=1, description="Layering instruction template for Advanced Mode")
    
    class Config:
        json_schema_extra = {
            "example": {
                "systemPrompt": "You are an expert fashion AI assistant...",
                "sceneDescriptions": {
                    "studio": "A clean studio...",
                    "beach": "A beach...",
                    "city": "A city...",
                    "forest": "A forest..."
                },
                "simpleLayeringInstruction": "Layer the products from bottom to top...",
                "advancedLayeringInstructionTemplate": "Layer products according to: {custom_instruction}"
            }
        }


# Tool settings (for copywriter, finishingStudio, modelManager)
class ToolSettings(BaseModel):
    systemPrompt: str = Field(..., min_length=1, description="System prompt for the AI tool")
    
    class Config:
        json_schema_extra = {
            "example": {
                "systemPrompt": "You are a professional fashion copywriter..."
            }
        }


# Tool Settings (just the tools, no theme)
class ToolSettingsComplete(BaseModel):
    lookCreator: LookCreatorSettings
    copywriter: ToolSettings
    finishingStudio: ToolSettings
    modelManager: ToolSettings
    
    @field_validator('lookCreator', 'copywriter', 'finishingStudio', 'modelManager')
    @classmethod
    def validate_not_none(cls, v):
        if v is None:
            raise ValueError("Setting cannot be None")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "lookCreator": {
                    "systemPrompt": "You are an expert fashion AI...",
                    "sceneDescriptions": {
                        "studio": "A clean studio...",
                        "beach": "A beach...",
                        "city": "A city...",
                        "forest": "A forest..."
                    },
                    "simpleLayeringInstruction": "...",
                    "advancedLayeringInstructionTemplate": "..."
                },
                "copywriter": {
                    "systemPrompt": "You are a professional fashion copywriter..."
                },
                "finishingStudio": {
                    "systemPrompt": "You are an expert image editing AI..."
                },
                "modelManager": {
                    "systemPrompt": "You are an AI assistant for fashion model management..."
                }
            }
        }


# Complete User Settings (theme + tool settings)
class UserSettingsData(BaseModel):
    theme: Literal['light', 'dark'] = Field(..., description="UI theme preference")
    toolSettings: ToolSettingsComplete = Field(..., description="Tool-specific settings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "theme": "dark",
                "toolSettings": {
                    "lookCreator": {
                        "systemPrompt": "You are an expert fashion AI...",
                        "sceneDescriptions": {
                            "studio": "...",
                            "beach": "...",
                            "city": "...",
                            "forest": "..."
                        },
                        "simpleLayeringInstruction": "...",
                        "advancedLayeringInstructionTemplate": "..."
                    },
                    "copywriter": {"systemPrompt": "..."},
                    "finishingStudio": {"systemPrompt": "..."},
                    "modelManager": {"systemPrompt": "..."}
                },
                "updatedAt": "2025-10-10T12:00:00Z"
            }
        }


class UserSettingsResponse(UserSettingsData):
    """Schema for user settings with metadata"""
    updatedAt: str = Field(..., alias="updatedAt", description="ISO timestamp of last update")

    class Config:
        json_schema_extra = {
            "example": {
                "theme": "dark",
                "toolSettings": {
                    "lookCreator": {"systemPrompt": "...", "sceneDescriptions": {"studio": "...", "beach": "...", "city": "...", "forest": "..."}},
                    "copywriter": {"systemPrompt": "..."},
                    "finishingStudio": {"systemPrompt": "..."},
                    "modelManager": {"systemPrompt": "..."}
                },
                "updatedAt": "2025-10-10T12:00:00Z"
                            "forest": "..."
                        }
                    },
                    "copywriter": {"systemPrompt": "..."},
                    "finishingStudio": {"systemPrompt": "..."},
                    "modelManager": {"systemPrompt": "..."}
                }
            }
        }


# Response schema with metadata
class UserSettingsResponse(BaseModel):
    """Response schema for user settings with metadata"""
    theme: Literal['light', 'dark']
    toolSettings: ToolSettingsComplete
    updatedAt: str = Field(..., description="ISO timestamp of last update")
    
    class Config:
        json_schema_extra = {
            "example": {
                "theme": "dark",
                "toolSettings": {
                    "lookCreator": {"systemPrompt": "...", "sceneDescriptions": {}},
                    "copywriter": {"systemPrompt": "..."},
                    "finishingStudio": {"systemPrompt": "..."},
                    "modelManager": {"systemPrompt": "..."}
                },
                "updatedAt": "2025-10-10T12:00:00Z"
            }
        }

