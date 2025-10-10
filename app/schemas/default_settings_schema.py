"""
Pydantic Schemas for Admin Default Settings Management
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field
from app.schemas.settings import ToolSettingsComplete


class DefaultSettingsData(BaseModel):
    """Schema for default settings that new users receive"""
    defaultTheme: Literal['light', 'dark'] = Field(..., description="Default UI theme for new users")
    defaultToolSettings: ToolSettingsComplete = Field(..., description="Default tool settings for new users")
    
    class Config:
        json_schema_extra = {
            "example": {
                "defaultTheme": "light",
                "defaultToolSettings": {
                    "lookCreator": {
                        "systemPrompt": "...",
                        "sceneDescriptions": {...},
                        "simpleLayeringInstruction": "...",
                        "advancedLayeringInstructionTemplate": "..."
                    },
                    "copywriter": {"systemPrompt": "..."},
                    "finishingStudio": {"systemPrompt": "..."},
                    "modelManager": {"systemPrompt": "..."}
                }
            }
        }


class DefaultSettingsResponse(BaseModel):
    """Response schema with metadata"""
    defaultTheme: Literal['light', 'dark']
    defaultToolSettings: ToolSettingsComplete
    updatedAt: str = Field(..., description="ISO timestamp of last update")
    updatedBy: Optional[str] = Field(None, description="Admin user ID who last updated (None if never updated)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "defaultTheme": "light",
                "defaultToolSettings": {...},
                "updatedAt": "2025-10-10T12:00:00Z",
                "updatedBy": "admin-user-id-123"
            }
        }

