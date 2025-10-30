"""
Configuration module for the AI Asset Management Chatbot.
"""

import os
from pathlib import Path


class Config:
    """Configuration class containing all app constants and settings."""
    
    def __init__(self):
        """Initialize configuration with default values."""
        # File paths
        # Keep a primary JSON file path for backward compatibility (used in sidebar stats)
        # Point to Assets as the representative dataset
        self.JSON_FILE_PATH = "JsonData/Assests.json"
        # New: base directory containing all related JSON sources
        self.JSON_DIR = "JsonData"
        self.FAISS_INDEX_PATH = "./faiss_index"
        
        # AI Model settings
        # Use sentence-transformers directly (more compatible)
        self.EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
        self.OPENAI_MODEL = "gpt-4o-mini"
        
        # Vector store settings
        self.VECTOR_STORE_K = 50  # Increase recall for list-style queries
        
        # LLM settings
        self.LLM_TEMPERATURE = 0.7
        self.LLM_MAX_TOKENS = 2000
    
    def get_openai_api_key(self):
        """Get OpenAI API key from environment variables."""
        return os.getenv("OPENAI_API_KEY")
    
    def validate_config(self):
        """Validate that all required configuration is present."""
        errors = []
        
        if not Path(self.JSON_FILE_PATH).exists():
            errors.append(f"JSON file not found: {self.JSON_FILE_PATH}")
        if not Path(self.JSON_DIR).exists():
            errors.append(f"JSON directory not found: {self.JSON_DIR}")
        
        if not self.get_openai_api_key():
            errors.append("OPENAI_API_KEY not set in environment variables")
        
        return errors
