"""
Token cost configuration for AI operations.

This is the single source of truth for all token costs.
Update costs here to change pricing across the entire application.
"""

from typing import Dict

# Token costs for different AI operations
TOKEN_COSTS: Dict[str, int] = {
    # Model Management
    "text_to_image": 10,           # Generate model with AI (e.g., Model Manager)
    
    # Look Creation
    "multi_modal": 20,             # Full look creation with multiple inputs
    
    # Finishing Studio
    "multi_modal_light": 8,        # Lighter multi-modal processing
    
    # Other Operations
    "image_to_text": 5,            # Convert image to text description
    "text_to_text": 3,             # Text processing (e.g., copywriting)
}


def get_operation_cost(operation: str) -> int:
    """
    Get the token cost for a specific operation.
    
    Args:
        operation: The operation name (e.g., 'text_to_image')
    
    Returns:
        Token cost as integer
    
    Raises:
        ValueError: If operation is not recognized
    """
    if operation not in TOKEN_COSTS:
        raise ValueError(f"Unknown operation: {operation}. Valid operations: {list(TOKEN_COSTS.keys())}")
    
    return TOKEN_COSTS[operation]


def get_all_costs() -> Dict[str, int]:
    """
    Get all operation costs.
    
    Returns:
        Dictionary of operation names to token costs
    """
    return TOKEN_COSTS.copy()


def is_valid_operation(operation: str) -> bool:
    """
    Check if an operation name is valid.
    
    Args:
        operation: The operation name to validate
    
    Returns:
        True if valid, False otherwise
    """
    return operation in TOKEN_COSTS

