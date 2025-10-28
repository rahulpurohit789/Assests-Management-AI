#!/usr/bin/env python3
"""
AI-Powered Asset Management Chatbot
==================================

A Streamlit application that provides intelligent querying of asset data
using LangChain, HuggingFace embeddings, and ChatGroq AI.

Features:
- Natural language understanding
- Vector-based semantic search
- AI-generated responses
- Real-time asset data analysis

Usage:
    streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from src.config import Config
from src.data_loader import DataLoader
from src.ai_components import AIComponents
from src.ui_components import UIComponents

def main():
    """Main application entry point."""
    # Configure Streamlit page
    st.set_page_config(
        page_title="Asset Management Assistant",
        page_icon="💼",
        layout="centered",
        initial_sidebar_state="expanded"
    )
    
    # Initialize components
    config = Config()
    data_loader = DataLoader(config)
    ai_components = AIComponents(config)
    ui_components = UIComponents()
    
    # Display title
    ui_components.display_title()
    
    # Display sidebar
    ui_components.display_sidebar(config)
    
    # Initialize AI system (hidden from user)
    with st.spinner("Loading your asset data..."):
        # Load data
        json_data, documents = data_loader.load_and_process_data()
        if json_data is None:
            st.error("Unable to load asset data. Please check your data file.")
            st.stop()
        
        # Initialize AI components
        embeddings = ai_components.load_embeddings()
        if embeddings is None:
            st.error("Unable to initialize AI system. Please check your configuration.")
            if getattr(ai_components, "last_error", None):
                with st.expander("Show diagnostics: Embeddings", expanded=False):
                    st.code(ai_components.last_error)
            st.stop()
        
        vectorstore = ai_components.create_vector_store(documents, embeddings)
        if vectorstore is None:
            st.error("Unable to create search index. Please try again.")
            if getattr(ai_components, "last_error", None):
                with st.expander("Show diagnostics: Vector Store", expanded=False):
                    st.code(ai_components.last_error)
            st.stop()
        
        llm = ai_components.create_llm()
        if llm is None:
            st.error("Unable to connect to AI service. Please check your API key.")
            if getattr(ai_components, "last_error", None):
                with st.expander("Show diagnostics: LLM", expanded=False):
                    st.code(ai_components.last_error)
            st.stop()
        
        ai_chain, retriever = ai_components.create_ai_chain(vectorstore, llm)
        if ai_chain is None:
            st.error("Unable to initialize chat system. Please try again.")
            if getattr(ai_components, "last_error", None):
                with st.expander("Show diagnostics: AI Chain", expanded=False):
                    st.code(ai_components.last_error)
            st.stop()
    
    # Display chat interface
    ui_components.display_chat_interface(ai_chain, retriever)
    
    # Display footer
    ui_components.display_footer()

if __name__ == "__main__":
    main()
