"""
UI components module for the Asset Management Assistant.
Handles all Streamlit UI elements and interactions with a clean, ChatGPT-like interface.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
import time


class UIComponents:
    """Handles all UI components and interactions."""
    
    def __init__(self):
        """Initialize UI components."""
        self.example_queries = [
            "Show me all assets from Singapore",
            "List all Caterpillar machines", 
            "Which vehicles are assigned to Homer Simpson?",
            "What is the warranty expiration date for MPT-001?",
            "How many assets are in each category?",
            "Tell me about the most expensive assets"
        ]
        
        # Initialize session state for chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
    
    def display_title(self):
        """Display the main title and description."""
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1f2937;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            font-size: 1.1rem;
            color: #6b7280;
            text-align: center;
            margin-bottom: 2rem;
        }
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
        }
        .message-user {
            background-color: #f3f4f6;
            padding: 1rem;
            border-radius: 1rem 1rem 0.25rem 1rem;
            margin: 0.5rem 0;
            margin-left: 2rem;
        }
        .message-assistant {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 1rem 1rem 1rem 0.25rem;
            margin: 0.5rem 0;
            margin-right: 2rem;
            border: 1px solid #e5e7eb;
        }
        .example-button {
            background-color: #f9fafb;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            margin: 0.25rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .example-button:hover {
            background-color: #f3f4f6;
            border-color: #9ca3af;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<h1 class="main-title">Asset Management Assistant</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Ask me anything about your assets. I can help you find, analyze, and understand your asset data.</p>', unsafe_allow_html=True)
    
    def display_sidebar(self, config):
        """Display a minimal sidebar with basic info."""
        with st.sidebar:
            st.markdown("### 📊 Quick Stats")
            
            # Get basic stats without showing technical details
            from pathlib import Path
            if config.JSON_FILE_PATH and Path(config.JSON_FILE_PATH).exists():
                try:
                    import json
                    with open(config.JSON_FILE_PATH, 'r') as f:
                        data = json.load(f)
                    
                    total_assets = len(data)
                    entities = len(set(asset.get('entityName', '') for asset in data if asset.get('entityName')))
                    manufacturers = len(set(asset.get('manufacturer', '') for asset in data if asset.get('manufacturer')))
                    
                    st.metric("Total Assets", total_assets)
                    st.metric("Locations", entities)
                    st.metric("Manufacturers", manufacturers)
                except:
                    st.info("Loading asset data...")
            else:
                st.warning("No data file found")
            
            st.markdown("---")
            st.markdown("### ⚙️ AI Settings")
            # Runtime controls (no hardcoding logic)
            temp = st.slider("Model temperature", 0.0, 1.0, float(config.LLM_TEMPERATURE), 0.05,
                             help="Lower = more deterministic; higher = more creative")
            k = st.slider("Results to retrieve (k)", 3, 30, int(config.VECTOR_STORE_K), 1,
                          help="Number of top matches given to the model")
            # Apply to config for this session
            config.LLM_TEMPERATURE = float(temp)
            config.VECTOR_STORE_K = int(k)

            st.markdown("---")
            st.markdown("### 💡 Tips")
            st.markdown("• Ask specific questions about your assets")
            st.markdown("• Use asset IDs for precise searches")
            st.markdown("• Ask for summaries or comparisons")
            st.markdown("• Request data analysis or insights")
    
    def display_chat_interface(self, ai_chain: Any, retriever: Any):
        """Display the main chat interface."""
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Example queries
        if not st.session_state.messages:
            st.markdown("### 💡 Try asking me:")
            
            # Create example buttons in a grid
            cols = st.columns(2)
            for i, query in enumerate(self.example_queries):
                with cols[i % 2]:
                    if st.button(f"💡 {query}", key=f"example_{i}", help="Click to use this example"):
                        st.session_state.user_query = query
                        st.rerun()
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about your assets..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Build conversation history from previous messages
                        conversation_history = self._build_conversation_history()
                        
                        # Check if it's a specific query that needs exact data
                        if self._is_data_query(prompt):
                            response = self._get_exact_data_response(prompt)
                        else:
                            response = ai_chain.invoke(prompt, conversation_history=conversation_history)
                        
                        st.markdown(response)
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                    except Exception as e:
                        error_msg = "I'm sorry, I encountered an error processing your request. Please try again or rephrase your question."
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # Clear chat button
        if st.session_state.messages:
            if st.button("🗑️ Clear Chat", type="secondary"):
                st.session_state.messages = []
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def display_footer(self):
        """Display a minimal footer."""
        st.markdown("---")
        st.markdown(
            '<div style="text-align: center; color: #6b7280; font-size: 0.9rem;">Asset Management Assistant • Powered by AI</div>', 
            unsafe_allow_html=True
        )
    
    def _is_data_query(self, query: str) -> bool:
        """Check if query needs exact data lookup (deterministic).
        Detects patterns like "work orders for asset MPT-001" - specific ID-based lookups.
        Note: Count queries are now handled intelligently by the AI through GLOBAL SUMMARY.
        """
        q = (query or "").lower()
        if ("work order" in q or "work orders" in q) and "asset" in q:
            return True
        return False
    
    def _analyze_floors(self, data: list) -> str:
        """Comprehensive floor analysis from the dataset."""
        floors = set()
        floor_details = {}
        
        for asset in data:
            # Check group field for floor indicators
            group = asset.get('groupId', '')
            if any(floor_indicator in group for floor_indicator in ['_1F', '_2F', '_3F', '_4F', '_5F', 'FLOOR']):
                floors.add(group)
                if group not in floor_details:
                    floor_details[group] = []
                floor_details[group].append(asset.get('assetId', 'N/A'))
            
            # Check custom fields for Floor field
            custom_fields = asset.get('customFields', [])
            for field in custom_fields:
                if field.get('fieldName') == 'Floor' and field.get('value'):
                    floor_value = field.get('value')
                    if floor_value and floor_value != 'null':
                        floor_key = f"Floor {floor_value}"
                        floors.add(floor_key)
                        if floor_key not in floor_details:
                            floor_details[floor_key] = []
                        floor_details[floor_key].append(asset.get('assetId', 'N/A'))
        
        if not floors:
            return "**0 floors** found in the data."
        
        response = f"**{len(floors)} floors** found:\n\n"
        for floor in sorted(floors):
            asset_count = len(floor_details[floor])
            response += f"**{floor}** ({asset_count} assets)\n"
        
        return response

    def _analyze_hk_equipment_plants(self, data: list) -> str:
        """Analyze HK Equipment plants from the dataset."""
        hk_assets = [asset for asset in data if asset.get('entityName', '').upper() == 'HK EQUIPMENT']
        
        if not hk_assets:
            return "**0 plants** found for HK Equipment."
        
        plants = {}
        for asset in hk_assets:
            group = asset.get('groupId', 'No Group')
            if group not in plants:
                plants[group] = []
            plants[group].append({
                'assetId': asset.get('assetId', 'N/A'),
                'description': asset.get('description', 'N/A'),
                'categoryId': asset.get('categoryId', 'N/A')
            })
        
        # Filter for plant-related groups
        plant_groups = {k: v for k, v in plants.items() if 'PLANT' in k.upper()}
        
        if not plant_groups:
            return f"**0 plants** found for HK Equipment. Found {len(plants)} other groups: {', '.join(plants.keys())}"
        
        response = f"**HK Equipment has {len(plant_groups)} plants:**\n\n"
        for plant, assets in sorted(plant_groups.items()):
            response += f"**{plant}** ({len(assets)} assets)\n"
            for asset in assets[:5]:  # Show first 5 assets
                response += f"  - {asset['assetId']}: {asset['description']} ({asset['categoryId']})\n"
            if len(assets) > 5:
                response += f"  ... and {len(assets) - 5} more assets\n"
            response += "\n"
        
        return response

    def _get_exact_data_response(self, query: str) -> str:
        """Deterministic lookup for work orders by assetId, including priorities and linked invoices.
        
        This handles ONLY specific ID-based queries (e.g., "work orders for asset MPT-001").
        For count queries, the AI now handles these intelligently through GLOBAL SUMMARY documents.
        """
        try:
            import re
            import json
            from pathlib import Path

            # Extract assetId token after the word 'asset'
            m = re.search(r"asset\s+([A-Za-z0-9\-_.]+)", query, flags=re.IGNORECASE)
            if not m:
                return None
            asset_id = m.group(1).strip()

            base = Path("JsonData")
            wo_path = base / "WorkOrders.json"
            inv_path = base / "Invoice.json"

            if not wo_path.exists():
                return None

            def load_json_safe(path: Path):
                for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                    try:
                        with open(path, 'r', encoding=enc) as f:
                            return json.load(f)
                    except Exception:
                        continue
                return []

            wos = load_json_safe(wo_path) or []
            invoices = load_json_safe(inv_path) or []

            # Index invoices by originating work order (both key and number)
            invs_by_wo_key = {}
            invs_by_wo_num = {}
            for inv in invoices:
                if inv.get("originatingWorkOrderKey") is not None:
                    invs_by_wo_key.setdefault(inv.get("originatingWorkOrderKey"), []).append(inv)
                if inv.get("originatingWorkOrderNumber") is not None:
                    invs_by_wo_num.setdefault(inv.get("originatingWorkOrderNumber"), []).append(inv)

            # Filter WOs
            target_wos = [wo for wo in wos if (wo.get("assetId") or "").strip() == asset_id]
            if not target_wos:
                return f"No work orders found for asset {asset_id}."

            # Format
            lines = [f"Work orders for asset {asset_id} ({len(target_wos)} found):"]
            for wo in sorted(target_wos, key=lambda x: x.get("workOrderNumber") or 0)[:50]:
                wo_num = wo.get("workOrderNumber")
                wo_key = wo.get("workOrderKey")
                pr = wo.get("priorityId")
                wt = wo.get("workTypeId")
                st = wo.get("statusId")
                asg = wo.get("assigned")
                # Find invoices linked to this WO
                linked = []
                linked.extend(invs_by_wo_key.get(wo_key, []))
                linked.extend(invs_by_wo_num.get(wo_num, []))
                inv_nums = sorted({inv.get("invoiceNumber") for inv in linked if inv.get("invoiceNumber") is not None})
                inv_text = f"Linked invoices: {inv_nums}" if inv_nums else "Linked invoices: None"
                lines.append(f"- WO #{wo_num} [$" + str(st) + f"] Type={wt} Priority={pr} Assigned={asg}. {inv_text}")

            return "\n".join(lines)
        except Exception:
            return None
    
    def _build_conversation_history(self) -> str:
        """Build conversation history string from session state messages."""
        if not st.session_state.messages or len(st.session_state.messages) < 2:
            return "No previous conversation."
        
        # Get last 10 messages (5 exchanges) to avoid token limits
        recent_messages = st.session_state.messages[-10:]
        
        history = ""
        for message in recent_messages:
            role = "User" if message["role"] == "user" else "Assistant"
            history += f"{role}: {message['content']}\n\n"
        
        return history.strip()
