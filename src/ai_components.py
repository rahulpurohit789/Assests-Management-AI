"""
AI components module for the AI Asset Management Chatbot.
Handles embeddings, vector store, LLM, and AI chain creation.
"""

import streamlit as st
from pathlib import Path
from typing import Optional, Tuple, Any
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


class AIComponents:
    """Handles all AI-related components and operations."""
    
    def __init__(self, config):
        """Initialize AI components with configuration."""
        self.config = config
    
    @st.cache_resource
    def load_embeddings(_self) -> Optional[FastEmbedEmbeddings]:
        """Load HuggingFace embeddings model."""
        try:
            # FastEmbed uses CPU-only and avoids heavy torch deps
            embeddings = FastEmbedEmbeddings(
                model_name=_self.config.EMBEDDING_MODEL
            )
            return embeddings
        except Exception as e:
            return None
    
    @st.cache_resource
    def create_vector_store(_self, documents: list, _embeddings: FastEmbedEmbeddings) -> Optional[FAISS]:
        """Create FAISS vector store from documents."""
        try:
            # Check if FAISS index exists
            if Path(_self.config.FAISS_INDEX_PATH).exists():
                try:
                    vectorstore = FAISS.load_local(
                        _self.config.FAISS_INDEX_PATH,
                        _embeddings,
                        allow_dangerous_deserialization=True
                    )
                except Exception:
                    # Rebuild if load fails (e.g., dimension mismatch after model change)
                    vectorstore = FAISS.from_documents(
                        documents=documents,
                        embedding=_embeddings
                    )
                    vectorstore.save_local(_self.config.FAISS_INDEX_PATH)
            else:
                vectorstore = FAISS.from_documents(
                    documents=documents,
                    embedding=_embeddings
                )
                vectorstore.save_local(_self.config.FAISS_INDEX_PATH)
            
            return vectorstore
            
        except Exception as e:
            return None
    
    @st.cache_resource
    def create_llm(_self) -> Optional[ChatGroq]:
        """Create ChatGroq LLM instance."""
        try:
            api_key = _self.config.get_groq_api_key()
            if not api_key:
                return None
            
            llm = ChatGroq(
                model=_self.config.GROQ_MODEL,
                temperature=0.7,
                max_tokens=_self.config.LLM_MAX_TOKENS,
                groq_api_key=api_key
            )
            
            return llm
            
        except Exception as e:
            return None
    
    def create_ai_chain(self, vectorstore: FAISS, llm: ChatGroq) -> Tuple[Optional[Any], Optional[Any]]:
        """Create AI-powered chain using available components."""
        try:
            print("Creating AI chain...")
            
            # Load ALL data for analysis
            import json
            with open('JsonData/Data.json', 'r', encoding='utf-8') as f:
                all_data = json.load(f)
            
            print(f"Loaded {len(all_data)} assets")
            
            # Create a comprehensive data summary for the AI
            entities = {}
            groups = {}
            categories = {}
            floors = set()
            plants = set()
            
            for asset in all_data:
                # Count entities
                entity = asset.get('entityName', 'Unknown')
                entities[entity] = entities.get(entity, 0) + 1
                
                # Count groups
                group = asset.get('groupId', 'Unknown')
                groups[group] = groups.get(group, 0) + 1
                
                # Count categories
                category = asset.get('categoryId', 'Unknown')
                categories[category] = categories.get(category, 0) + 1
                
                # Extract floors
                if 'floor' in group.lower() or '_1F' in group or '_2F' in group or '_3F' in group:
                    floors.add(group)
                
                # Extract plants
                if 'plant' in group.lower():
                    plants.add(group)
                
                # Check custom fields for floors
                custom_fields = asset.get('customFields', [])
                for field in custom_fields:
                    if field.get('fieldName') == 'Floor' and field.get('value'):
                        floors.add(f"Floor {field.get('value')}")
            
            print(f"Data analysis complete: {len(entities)} entities, {len(groups)} groups, {len(categories)} categories")
            
            # Create the data summary
            data_summary = f"ASSET DATABASE SUMMARY ({len(all_data)} total assets):\n\n"
            data_summary += f"ENTITIES ({len(entities)} unique):\n"
            for entity, count in sorted(entities.items()):
                data_summary += f"- {entity}: {count} assets\n"
            
            data_summary += f"\nGROUPS ({len(groups)} unique):\n"
            for group, count in sorted(groups.items()):
                data_summary += f"- {group}: {count} assets\n"
            
            data_summary += f"\nCATEGORIES ({len(categories)} unique):\n"
            for category, count in sorted(categories.items()):
                data_summary += f"- {category}: {count} assets\n"
            
            data_summary += f"\nFLOORS FOUND ({len(floors)} unique):\n"
            for floor in sorted(floors):
                data_summary += f"- {floor}\n"
            
            data_summary += f"\nPLANTS FOUND ({len(plants)} unique):\n"
            for plant in sorted(plants):
                data_summary += f"- {plant}\n"
            
            print(f"Data summary created: {len(data_summary)} characters")
            
            # Create prompt template
            total_assets = len(all_data)
            prompt_template = PromptTemplate(
                input_variables=["data_summary", "conversation_history", "question"],
                template=f"""You are an asset management assistant with access to ALL {total_assets} assets. Use the complete data summary to give direct, confident answers.

PREVIOUS CONVERSATION HISTORY:
{{conversation_history}}

CURRENT QUESTION: {{question}}

Data Summary:
{{data_summary}}

Instructions:
- You have access to ALL {total_assets} assets in the database
- Remember and refer back to the previous conversation history when answering
- If the user is asking for more details about something mentioned earlier, use that context
- Use the data summary above to answer questions accurately
- For counting questions, use the exact numbers from the summary
- Be direct and confident in your answers
- Don't show uncertainty - you have access to all the data
- RESPOND IN THE SAME LANGUAGE AS THE QUESTION. If the user asks in Japanese, respond in Japanese. If they ask in English, respond in English. Match the language of their query.

Answer:"""
            )
            
            print("Prompt template created")
            
            # Create a simple chain class with conversation history
            class SimpleChain:
                def __init__(self, llm, prompt_template, data_summary):
                    self.llm = llm
                    self.prompt_template = prompt_template
                    self.data_summary = data_summary
                
                def invoke(self, question, conversation_history=""):
                    try:
                        # Format the prompt with the data summary and conversation history
                        formatted_prompt = self.prompt_template.format(
                            data_summary=self.data_summary,
                            conversation_history=conversation_history,
                            question=question
                        )
                        
                        # Get response from LLM
                        response = self.llm.invoke(formatted_prompt)
                        
                        # Extract content if it's a message object
                        if hasattr(response, 'content'):
                            return response.content
                        else:
                            return str(response)
                    except Exception as e:
                        print(f"Error in chain invoke: {e}")
                        return f"Error processing request: {str(e)}"
            
            print("Simple chain created successfully")
            simple_chain = SimpleChain(llm, prompt_template, data_summary)
            
            return simple_chain, None
            
        except Exception as e:
            print(f"Error creating AI chain: {e}")
            import traceback
            traceback.print_exc()
            return None, None
