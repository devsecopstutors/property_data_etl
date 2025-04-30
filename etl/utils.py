import os
import logging
from typing import Any, Dict, List, Optional

"""
Utility functions for property data ETL operations.
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_directory_exists(directory_path: str) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        directory_path (str): Path to directory
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Created directory: {directory_path}")


def validate_data_dict(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate if all required fields exist in data dictionary.
    
    Args:
        data (Dict[str, Any]): Data dictionary to validate
        required_fields (List[str]): List of required field names
        
    Returns:
        bool: True if all required fields exist, False otherwise
    """
    return all(field in data for field in required_fields)

def flatten_json(y: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten a nested JSON object.
    
    Args:
        y (Dict[str, Any]): JSON object to flatten
        parent_key (str): Parent key for nested keys
        sep (str): Separator for nested keys
        
    Returns:
        Dict[str, Any]: Flattened JSON object
    """
    items = []
    for k, v in y.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
