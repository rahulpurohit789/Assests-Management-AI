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
        self.JSON_FILE_PATH = "JsonData/Data.json"
        self.FAISS_INDEX_PATH = "./faiss_index"
        
        # AI Model settings
        self.EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
        self.GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
        
        # Vector store settings
        self.VECTOR_STORE_K = 5  # Number of documents to retrieve
        
        # LLM settings
        self.LLM_TEMPERATURE = 0.1
        self.LLM_MAX_TOKENS = 2000
    
    def get_groq_api_key(self):
        """Get GROQ API key from environment variables."""
        return os.getenv("GROQ_API_KEY")
    
    def validate_config(self):
        """Validate that all required configuration is present."""
        errors = []
        
        if not Path(self.JSON_FILE_PATH).exists():
            errors.append(f"JSON file not found: {self.JSON_FILE_PATH}")
        
        if not self.get_groq_api_key():
            errors.append("GROQ_API_KEY not set in environment variables")
        
        return errors
