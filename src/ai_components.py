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
import re


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
                    
                    "## Response Style (Concise & Structured):\n"
                    "- Default to brevity; keep under 6 lines unless asked for more.\n"
                    "- Answer only what is asked. No extra context or preamble.\n"
                    "- Organize with short headings (use '###') and bullets.\n"
                    "- Prefer lists/tables over paragraphs.\n"
                    "- Put key numbers first and make them **bold**.\n"
                    "- If information is missing, state it in one line, then ask one targeted follow-up.\n"
                    "- For long lists (>20 items), ask for confirmation before listing all.\n"
                    "- Never repeat the question or include source citations.\n\n"

                    "## Language Behavior:\n"
                    "- Respond in the user's requested language when specified.\n"
                    "- If the user says to 'tell the previous details again in Japanese' (e.g., '日本語で', 'Japanese'),\n"
                    "  then re-state the last assistant answer translated into natural Japanese, preserving structure, counts, and items exactly.\n"
                    "- Do not re-analyze or change numbers/content; only translate and adapt headings/bullets to Japanese.\n"
                    "- Use concise Japanese, with short headings and bullets.\n\n"

                    "## Analytical Response Guidelines:\n"
                    "1. Count Queries (how many, count, total):\n"
                    "   - Prefer GLOBAL SUMMARY when present.\n"
                    "   - Extract exact numbers only.\n"
                    "   - Answer with just the metric; key number first and **bold**.\n"
                    "   - Keep it to a single bullet unless more detail is requested.\n\n"

                    "2. List Queries (list all, show all):\n"
                    "   - Return bullets only, no commentary.\n"
                    "   - Prefer authoritative summary docs when present.\n"
                    "   - Include human-readable identifiers only (e.g., name, id, email, status).\n"
                    "   - Exclude internal keys (e.g., contactKey, customerKey, vendorKey, addressKey, phoneKey).\n"
                    "   - Use 'Name – id, email, status' inline format; use '-' for missing fields.\n"
                    "   - If total N is stated, output exactly N items.\n"
                    "   - If N > 20, first ask: 'Show all N?' and wait unless user confirms.\n"
                    "   - One item per line starting with '- '.\n\n"

                    "3. Aggregations (sum, average, min, max, median, group by):\n"
                    "   - Calculate strictly from the provided context; do not invent values.\n"
                    "   - State units and currency when known.\n"
                    "   - Show a one-line formula summary when non-trivial.\n"
                    "   - When grouping, present a compact table: group, count, sum, avg as relevant.\n"
                    "   - Keep to 3-5 bullets unless asked for more.\n"
                    "   - Handle missing values by excluding nulls unless the user requests otherwise.\n\n"

                    "4. Analytics (trends, outliers, distributions, comparisons):\n"
                    "   - Base insights only on data in context.\n"
                    "   - Identify top contributors and anomalies with simple metrics.\n"
                    "   - If a time range is implied, state the range detected from the data.\n"
                    "   - Keep insights to 3 to 5 tight bullets unless asked for more.\n\n"

                    "5. Detail Queries (tell me about, details of):\n"
                    "   - Extract comprehensive information from DOC entries.\n"
                    "   - Include related entities only if asked.\n"
                    "   - Never expose internal keys; omit fields ending with 'Key' (e.g., contactKey).\n\n"
                    

                    "## General Rules:\n"
                    "- Use exact numbers from context; include units and currency when known.\n"
                    "- Do not hallucinate fields or records; if data is insufficient, say what is missing.\n"
                    "- Include only human-readable IDs where relevant (assetId, workOrderNumber, invoiceNumber, customerId, vendorId).\n"
                    "- Do NOT include internal numeric keys (e.g., contactKey, customerKey, vendorKey, addressKey, phoneKey).\n"
                    "- No recommendations unless asked.\n\n"

                    "CRITICAL FORMATTING RULES:\n"
                    "- Start responses immediately; no preambles or sources.\n"
                    "- One bullet per line, starting with '- '.\n"
                    "- Use short '###' headings when helpful.\n"
                    "- Keep under 6 lines by default; ask to expand if needed.\n\n"
                    
                    "Remember: Be concise, structured, and grounded only in the provided documents."
                ).replace("{k}", str(self.config.VECTOR_STORE_K))
            )

            class RAGChain:
                def __init__(self, llm, retriever, prompt_template, vectorstore):
                    self.llm = llm
                    self.retriever = retriever
                    self.prompt_template = prompt_template
                    self.vectorstore = vectorstore

                @staticmethod
                def _sanitize_output(text: str) -> str:
                    """Remove internal keys such as contactKey from LLM output and fix formatting."""
                    if not isinstance(text, str):
                        return text
                    # Remove explicit 'contactKey: <number>' patterns
                    text = re.sub(r"\bcontactKey\s*:\s*\d+", "", text)
                    # Remove standalone 'contactKey' labels in bullets or tables
                    text = re.sub(r"(?i)\bcontactKey\b", "", text)
                    
                    # Fix bullet point formatting - ensure each bullet is on its own line
                    # Look for patterns like "Site: X - Another Site: Y" where multiple items are on one line
                    # Split on " - " that separates different entities
                    lines = text.split('\n')
                    fixed_lines = []
                    for line in lines:
                        # Check if line contains multiple items separated by " - "
                        # Pattern: "Name: value - Name2: value2" but not "Name - value" (which is single item)
                        if line.count(' - ') > 1 or (' - ' in line and line.count(':') >= 2):
                            # This line has multiple items, split them
                            parts = line.split(' - ')
                            for part in parts:
                                part = part.strip()
                                if part and not part.startswith('- '):
                                    fixed_lines.append(part)
                        else:
                            fixed_lines.append(line)
                    
                    text = '\n'.join(fixed_lines)
                    
                    # Add blank line before conclusion sentences
                    # Look for patterns like "The entity with..." or "In conclusion" etc after lists
                    conclusion_patterns = [
                        r'^(The (?:entity|company|organization|business).+)',
                        r'^(In conclusion.+)',
                        r'^(Therefore.+)',
                        r'^(As (?:a result|shown).+)'
                    ]
                    
                    lines = text.split('\n')
                    result_lines = []
                    prev_was_list_item = False
                    
                    for i, line in enumerate(lines):
                        # Check if line is a list item (has "Name: number" pattern)
                        is_list_item = (line.strip() and ':' in line and 
                                       any(char.isdigit() for char in line) and
                                       not line.strip().startswith('#') and
                                       not line.strip().startswith('The ') and
                                       not line.strip().startswith('- '))
                        
                        # Check if line is a conclusion
                        is_conclusion = any(re.search(pattern, line.strip()) for pattern in conclusion_patterns)
                        
                        if is_conclusion and prev_was_list_item:
                            # Add blank line before conclusion
                            result_lines.append('')
                        
                        result_lines.append(line)
                        prev_was_list_item = is_list_item
                    
                    text = '\n'.join(result_lines)
                    
                    # Minimal cleanup - preserve structure
                    text = re.sub(r' {2,}', ' ', text)  # Multiple spaces to single space
                    return text.strip()

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
                        
                        # Detect list queries for special handling (broadened)
                        list_keywords = [
                            "list all", "show all", "show me all", "all customers", "all vendors", "all employees", "all assets",
                            "list customers", "list customer", "customers list", "customer list", "list customer details", "customer details",
                            "show customers", "show customer details", "get customers", "display customers"
                        ]
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
                        
                        # For list queries, prioritize relevant summary documents and ensure they are first
                        if is_list_query:
                            if customers_summary_content and ("customer" in qnorm or "customers" in qnorm):
                                if customers_summary_content in parts:
                                    parts.remove(customers_summary_content)
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
                        raw = getattr(response, 'content', str(response))
                        return self._sanitize_output(raw)
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
