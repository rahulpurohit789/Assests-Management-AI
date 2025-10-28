"""
Data loading and processing module for the AI Asset Management Chatbot.
"""

import json
import streamlit as st
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from langchain_core.documents import Document


class DataLoader:
    """Handles loading and processing of JSON asset data."""
    
    def __init__(self, config):
        """Initialize data loader with configuration."""
        self.config = config
    
    def load_and_process_data(self) -> Tuple[Optional[List[Dict]], Optional[List[Document]]]:
        """
        Load and process JSON data into searchable documents.
        
        Returns:
            Tuple of (json_data, documents) or (None, None) if error
        """
        try:
            # Check if JSON file exists
            if not Path(self.config.JSON_FILE_PATH).exists():
                return None, None
            
            # Load JSON data with multiple encoding attempts
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            json_data = None
            
            for encoding in encodings:
                try:
                    with open(self.config.JSON_FILE_PATH, 'r', encoding=encoding) as f:
                        json_data = json.load(f)
                    break
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
            
            if json_data is None:
                return None, None
            
            # Process documents
            documents = []
            for asset_data in json_data:
                text_content = self._create_asset_text(asset_data)
                doc = Document(
                    page_content=text_content,
                    metadata=self._extract_metadata(asset_data)
                )
                documents.append(doc)
            
            return json_data, documents
            
        except Exception as e:
            return None, None
    
    def _create_asset_text(self, asset_data: Dict[str, Any]) -> str:
        """Create comprehensive text representation of an asset."""
        text_parts = []
        
        # Basic information
        basic_fields = [
            ('assetId', 'Asset ID'),
            ('entityName', 'Entity'),
            ('description', 'Description'),
            ('manufacturer', 'Manufacturer'),
            ('model', 'Model'),
            ('categoryId', 'Category'),
            ('typeId', 'Type'),
            ('statusId', 'Status'),
            ('customer', 'Customer'),
            ('groupId', 'Group'),
            ('serialNumber', 'Serial Number'),
            ('barcode', 'Barcode'),
            ('purchaseDate', 'Purchase Date'),
            ('purchaseCost', 'Purchase Cost')
        ]
        
        for field_key, field_label in basic_fields:
            value = asset_data.get(field_key, 'N/A')
            text_parts.append(f"{field_label}: {value}")
        
        # Custom fields
        custom_fields = asset_data.get('customFields', [])
        if custom_fields:
            text_parts.append("Custom Fields:")
            for field in custom_fields:
                field_name = field.get('fieldName', 'Unknown')
                field_value = field.get('value', 'N/A')
                if field_value and field_value != 'N/A':
                    text_parts.append(f"  {field_name}: {field_value}")
        
        return "\n".join(text_parts)
    
    def _extract_metadata(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant metadata from asset data."""
        return {
            'assetId': asset_data.get('assetId', ''),
            'entityName': asset_data.get('entityName', ''),
            'manufacturer': asset_data.get('manufacturer', ''),
            'customer': asset_data.get('customer', ''),
            'categoryId': asset_data.get('categoryId', ''),
            'typeId': asset_data.get('typeId', ''),
            'statusId': asset_data.get('statusId', ''),
            'description': asset_data.get('description', ''),
            'purchaseDate': asset_data.get('purchaseDate', ''),
            'purchaseCost': asset_data.get('purchaseCost', ''),
            'serialNumber': asset_data.get('serialNumber', ''),
            'barcode': asset_data.get('barcode', ''),
            'model': asset_data.get('model', ''),
            'groupId': asset_data.get('groupId', ''),
            'customFields': asset_data.get('customFields', [])
        }
