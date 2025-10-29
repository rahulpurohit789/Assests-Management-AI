"""
AI components module for the AI Asset Management Chatbot.
Handles embeddings, vector store, LLM, and AI chain creation.
"""

import streamlit as st
from pathlib import Path
from typing import Optional, Tuple, Any
from langchain_community.embeddings import HuggingFaceEmbeddings
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
        self.last_error: Optional[str] = None
    
    @st.cache_resource
    def load_embeddings(_self) -> Optional[HuggingFaceEmbeddings]:
        """Load HuggingFace embeddings model."""
        try:
            # Use HuggingFace embeddings directly
            embeddings = HuggingFaceEmbeddings(
                model_name=_self.config.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'}
            )
            return embeddings
        except Exception as e:
            import traceback
            _self.last_error = (
                "Embeddings initialization failed\n"
                f"Model: {_self.config.EMBEDDING_MODEL}\n"
                f"Error: {e}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            print(_self.last_error)
            return None
    
    @st.cache_resource
    def create_vector_store(_self, documents: list, _embeddings: HuggingFaceEmbeddings) -> Optional[FAISS]:
        """Create FAISS vector store from documents."""
        try:
            # Always build fresh on startup to ensure index directory is created
            vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=_embeddings
            )
            vectorstore.save_local(_self.config.FAISS_INDEX_PATH)
            
            return vectorstore
            
        except Exception as e:
            import traceback
            _self.last_error = (
                "FAISS vector store creation failed\n"
                f"Index path: {_self.config.FAISS_INDEX_PATH}\n"
                f"Docs: {len(documents) if documents else 0}\n"
                f"Error: {e}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            print(_self.last_error)
            return None
    
    @st.cache_resource
    def create_llm(_self) -> Optional[ChatGroq]:
        """Create ChatGroq LLM instance."""
        try:
            api_key = _self.config.get_groq_api_key()
            if not api_key:
                _self.last_error = "Missing GROQ_API_KEY in environment variables"
                print(_self.last_error)
                return None
            
            llm = ChatGroq(
                model=_self.config.GROQ_MODEL,
                temperature=_self.config.LLM_TEMPERATURE,
                max_tokens=_self.config.LLM_MAX_TOKENS,
                groq_api_key=api_key
            )
            
            return llm
            
        except Exception as e:
            import traceback
            _self.last_error = (
                "LLM initialization failed\n"
                f"Model: {_self.config.GROQ_MODEL}\n"
                f"Error: {e}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            print(_self.last_error)
            return None
    
    def create_ai_chain(self, vectorstore: FAISS, llm: ChatGroq) -> Tuple[Optional[Any], Optional[Any]]:
        """Create a retrieval-augmented generation chain using the vector store."""
        try:
            retriever = vectorstore.as_retriever(search_kwargs={"k": self.config.VECTOR_STORE_K})

            prompt_template = PromptTemplate(
                input_variables=["context", "conversation_history", "question"],
                template=(
                    "You are a senior data analyst specializing in asset management and maintenance operations. "
                    "You analyze complex business data to provide actionable insights.\n\n"
                    
                    "## Data Structure:\n"
                    "All documents are prefixed with 'DOC: [TYPE]' where TYPE indicates the record type.\n"
                    "Available types: ASSET, WORK ORDER, CUSTOMER, VENDOR, INVOICE, PURCHASE ORDER, "
                    "EMPLOYEE, PART, SERVICE ITEM, WORK TYPE, WORK PRIORITY, etc.\n"
                    "GLOBAL SUMMARY documents contain aggregate counts, totals, and statistical breakdowns.\n\n"
                    
                    "## Entity Relationships:\n"
                    "- Assets are linked to Customers and have Work Orders\n"
                    "- Work Orders generate Invoices and link to Employees\n"
                    "- Vendors supply Purchase Orders and Parts\n"
                    "- Invoices can originate from Work Orders and link to Customers\n"
                    "- All entities can have Custom Fields with additional metadata\n\n"
                    
                    "CONVERSATION HISTORY:\n{conversation_history}\n\n"
                    
                    "CURRENT QUESTION: {question}\n\n"
                    
                    "AVAILABLE DATA (showing top {k} relevant documents):\n{context}\n\n"
                    
                    "## Analytical Response Guidelines:\n"
                    "1. **Count Queries** (how many, count, total):\n"
                    "   - ALWAYS use GLOBAL SUMMARY documents when present\n"
                    "   - Extract exact numbers, never estimate\n"
                    "   - Reference the specific count: 'According to GLOBAL SUMMARY: Total assets: 424'\n\n"
                    
                    "2. **List Queries** (list all, show all):\n"
                    "   - Provide all relevant DOC entries with their IDs\n"
                    "   - Include key identifying fields (IDs, names, status)\n"
                    "   - Group by categories when relevant\n\n"
                    
                    "3. **Analysis Queries** (trends, patterns, insights):\n"
                    "   - Identify patterns across documents\n"
                    "   - Highlight anomalies or notable findings\n"
                    "   - Provide business-relevant context for numbers\n"
                    "   - Suggest actionable recommendations when appropriate\n\n"
                    
                    "4. **Detail Queries** (tell me about, details of):\n"
                    "   - Extract comprehensive information from DOC entries\n"
                    "   - Include related entities (e.g., work orders for an asset)\n"
                    "   - Show custom fields, nested data, and relationships\n\n"
                    
                    "5. **Aggregation Queries** (total cost, average, sum):\n"
                    "   - Calculate from multiple documents\n"
                    "   - Show your calculation method briefly\n"
                    "   - Include entity IDs for traceability\n\n"
                    
                    "## General Rules:\n"
                    "- Be precise with numbers - extract exact values from context\n"
                    "- Never say 'None' if data exists - search all DOC types\n"
                    "- Always include relevant IDs (assetId, workOrderNumber, invoiceNumber, etc.)\n"
                    "- If information is incomplete, acknowledge it but provide what you can\n"
                    "- Provide business context - explain what the numbers mean\n"
                    "- For translation requests, maintain data accuracy across all languages\n\n"
                    
                    "Remember: You're helping business users understand their operations. "
                    "Be clear, precise, and helpful."
                ).replace("{k}", str(self.config.VECTOR_STORE_K))
            )

            class RAGChain:
                def __init__(self, llm, retriever, prompt_template, vectorstore):
                    self.llm = llm
                    self.retriever = retriever
                    self.prompt_template = prompt_template
                    self.vectorstore = vectorstore

                def invoke(self, question: str, conversation_history: str = ""):
                    try:
                        # Comprehensive normalization for common misspellings
                        qnorm = (question or "").lower()
                        normalization_map = {
                            "assests": "assets",
                            "assest": "asset", 
                            "workorder": "work order",
                            "workorders": "work orders",
                            "purchaseorder": "purchase order",
                            "purchaseorders": "purchase orders",
                            "customers": "customer",
                            "vendors": "vendor",
                            "invoices": "invoice",
                            "employees": "employee",
                            "parts": "part",
                            "serviceitems": "service item"
                        }
                        
                        for wrong, correct in normalization_map.items():
                            qnorm = qnorm.replace(wrong, correct)

                        # Detect query intent for intelligent retrieval
                        count_keywords = ["how many", "count", "total", "number of", "amount of"]
                        is_count_query = any(keyword in qnorm for keyword in count_keywords)
                        
                        # Detect list queries for special handling
                        list_keywords = ["list all", "show all", "all customers", "all vendors", "all employees", "all assets"]
                        is_list_query = any(keyword in qnorm for keyword in list_keywords)
                        
                        # More robust entity detection
                        entity_keywords = {
                            "asset": ["asset", "assest", "assests"],
                            "customer": ["customer", "clients", "client"],
                            "vendor": ["vendor", "supplier", "suppliers"],
                            "work_order": ["work order", "workorder", "work orders"],
                            "invoice": ["invoice", "invoices"],
                            "employee": ["employee", "staff", "worker"],
                            "part": ["part", "parts"],
                            "purchase_order": ["purchase order", "purchaseorder", "po"]
                        }

                        # Use normalized query for retrieval (LangChain >= 0.1.46)
                        docs = self.retriever.invoke(qnorm)
                        parts = [d.page_content for d in docs]
                        
                        # Always include summary documents if present for intelligent retrieval
                        global_summary_content = None
                        customers_summary_content = None
                        try:
                            store = getattr(self.vectorstore, "docstore", None)
                            mapping = getattr(store, "_dict", {}) if store else {}
                            for _id, doc in mapping.items():
                                if isinstance(doc, Document):
                                    if doc.metadata.get("doc_type") == "global_summary":
                                        global_summary_content = doc.page_content
                                    elif doc.metadata.get("doc_type") == "customers_summary":
                                        customers_summary_content = doc.page_content
                        except Exception:
                            pass
                        
                        # For count queries, ALWAYS prioritize global summary at the TOP
                        if is_count_query and global_summary_content:
                            parts.insert(0, global_summary_content)
                            # Also append it at the end as backup to ensure it's in context
                            if global_summary_content not in parts[1:]:
                                parts.append(global_summary_content)
                        
                        # For list queries, prioritize relevant summary documents
                        if is_list_query:
                            if customers_summary_content and ("customer" in qnorm or "customers" in qnorm):
                                if customers_summary_content not in parts:
                                    parts.insert(0, customers_summary_content)
                        
                        # For general queries, include global summary at the end for context
                        if not is_count_query and global_summary_content and global_summary_content not in parts:
                            parts.append(global_summary_content)
                        
                        context = "\n\n---\n\n".join(parts)
                        prompt = self.prompt_template.format(
                            context=context,
                            conversation_history=conversation_history or "No previous conversation.",
                            question=qnorm,
                        )
                        response = self.llm.invoke(prompt)
                        return getattr(response, 'content', str(response))
                    except Exception as e:
                        print(f"Error in RAGChain.invoke: {e}")
                        return f"Error processing request: {str(e)}"

            return RAGChain(llm, retriever, prompt_template, vectorstore), retriever

        except Exception as e:
            import traceback
            self.last_error = (
                "AI chain creation failed\n"
                f"Error: {e}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            print(self.last_error)
            return None, None
