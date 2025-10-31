"""
UI components module for the Eptura Asset AI.
Handles all Streamlit UI elements and interactions with a clean, ChatGPT-like interface.
"""

import streamlit as st
from typing import Any


class UIComponents:
    """Handles all UI components and interactions."""
    
    def __init__(self):
        """Initialize UI components and ephemeral multi-chat state."""
        self.example_queries = [
            "Show me all assets from Singapore",
            "List all Caterpillar machines", 
            "What is the warranty expiration date for MPT-001?",
            "How many assets are in each category?"
        ]
        self._ensure_chat_state()

    def _ensure_chat_state(self):
        """Create in-memory chat registry without external storage."""
        if "chats" not in st.session_state:
            st.session_state.chats = []  # [{id, title, messages:[{role,content}]}]
        if "active_chat_id" not in st.session_state:
            st.session_state.active_chat_id = None
        if "next_chat_id" not in st.session_state:
            st.session_state.next_chat_id = 1

        # Ensure at least one chat exists and is active
        if not st.session_state.chats:
            self._start_new_chat()
        if st.session_state.active_chat_id is None:
            st.session_state.active_chat_id = st.session_state.chats[0]["id"]

    def _start_new_chat(self):
        """Create a new empty chat and make it active (newest on top)."""
        cid = st.session_state.next_chat_id
        st.session_state.next_chat_id += 1
        chat = {"id": cid, "title": "Open chat", "messages": []}
        st.session_state.chats.insert(0, chat)
        st.session_state.active_chat_id = cid

    def _get_active_chat(self):
        for c in st.session_state.chats:
            if c["id"] == st.session_state.active_chat_id:
                return c
        return None

    def _truncate_title(self, title: str, max_len: int = 20) -> str:
        """Return a display-safe title of at most max_len characters, adding '...' if truncated."""
        safe = (title or "").strip()
        if len(safe) <= max_len:
            return safe
        return safe[:max_len] + "..."

    def _delete_chat(self, chat_id: int):
        st.session_state.chats = [c for c in st.session_state.chats if c["id"] != chat_id]
        if not st.session_state.chats:
            self._start_new_chat()
        st.session_state.active_chat_id = st.session_state.chats[0]["id"]
    
    def _select_chat(self, chat_id: int):
        """Set the active chat (button callback)."""
        if any(c["id"] == chat_id for c in st.session_state.chats):
            st.session_state.active_chat_id = chat_id
    
    def _delete_chat_callback(self, chat_id: int):
        """Start delete confirmation for a chat."""
        st.session_state.pending_delete_chat_id = chat_id
    
    def display_title(self):
        """Display the main title and description."""
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main-title {
            font-size: 1rem;
            font-weight: 600;
            color: #1f2937;
            text-align: left;
            margin-bottom: 0.25rem;
        }
        .subtitle {
            font-size: 0.875rem;
            color: #6b7280;
            text-align: left;
            margin-bottom: 1rem;
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
        /* Chat message alignment - User messages on right, Assistant on left */
        [data-testid="stChatMessage"] {
            display: flex;
        }
        [data-testid="stChatMessage"][data-message-author="user"] {
            flex-direction: row-reverse;
            justify-content: flex-end;
        }
        [data-testid="stChatMessage"][data-message-author="assistant"] {
            flex-direction: row;
            justify-content: flex-start;
        }
        /* Message content containers */
        [data-testid="stChatMessage"][data-message-author="user"] > div {
            max-width: 70%;
            margin-left: auto;
        }
        [data-testid="stChatMessage"][data-message-author="assistant"] > div {
            max-width: 70%;
            margin-right: auto;
        }
        /* Avatar styling */
        [data-testid="stChatMessage"] .stChatAvatar {
            flex-shrink: 0;
        }
        [data-testid="stChatMessage"][data-message-author="user"] .stChatAvatar {
            margin-left: 0.75rem;
            margin-right: 0;
        }
        [data-testid="stChatMessage"][data-message-author="assistant"] .stChatAvatar {
            margin-right: 0.75rem;
            margin-left: 0;
        }
        /* Message bubbles styling */
        [data-testid="stChatMessage"][data-message-author="user"] [class*="message"] {
            background-color: #f3f4f6;
            border-radius: 1rem 1rem 0.25rem 1rem;
        }
        [data-testid="stChatMessage"][data-message-author="assistant"] [class*="message"] {
            background-color: #ffffff;
            border-radius: 1rem 1rem 1rem 0.25rem;
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
        /* Chat list styling */
        .chat-list-title { font-weight: 600; margin-bottom: 0.25rem; }
        .chat-item-row {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.25rem 0.2rem;
            border-radius: 8px;
            flex-wrap: nowrap;
            background: transparent;
        }
        .chat-item-row:hover { background: #f8fafc; }
        .chat-item-btn { all: unset; cursor: pointer; color: #0f172a; }
        .chat-item-btn.active { font-weight: 600; }
        .chat-del-btn { all: unset; cursor: pointer; color: #64748b; opacity: 0; transition: opacity 0.15s; padding: 0 0.25rem; }
        .chat-item-row:hover .chat-del-btn { opacity: 1; }
        .chat-del-btn:hover { color: #ef4444; }
        /* Streamlined buttons: remove borders/background fully inside sidebar chat rows */
        section[data-testid="stSidebar"] .chat-row .stButton>button {
            background: transparent !important;
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            min-height: auto !important;
            line-height: 1.2 !important;
            color: #0f172a !important;
            text-decoration: none !important;
            width: auto !important;
            text-align: left !important;
            overflow: hidden !important;
            white-space: nowrap !important;
            text-overflow: ellipsis !important;
        }
        section[data-testid="stSidebar"] .chat-row .stButton>button:hover {
            background: transparent !important;
            color: #0f172a !important;
            text-decoration: none !important;
        }
        section[data-testid="stSidebar"] .chat-row .del .stButton>button {
            color: #64748b !important;
            font-weight: 400 !important;
        }
        section[data-testid="stSidebar"] .chat-row .del .stButton>button:hover {
            color: #ef4444 !important;
            text-decoration: none !important;
        }
        /* Row layout tidy spacing */
        .chat-item-row { padding: 0.2rem 0.15rem; }
        .chat-row .del { opacity: 0; transition: opacity 0.15s; }
        .chat-row:hover .del { opacity: 1; }
        .chat-row .del .stButton>button { padding-right: 4px !important; }
        .chat-row [data-testid="column"] { padding-left: 0 !important; padding-right: 0 !important; }
        /* Keep both buttons on one line on mobile too */
        .chat-row [data-testid="stHorizontalBlock"] { display: flex !important; flex-wrap: nowrap !important; align-items: center !important; gap: 6px !important; width: 100% !important; }
        .chat-row [data-testid="column"]:first-child { flex: 1 1 auto !important; min-width: 0 !important; }
        .chat-row [data-testid="column"]:last-child { flex: 0 0 auto !important; }
        /* Small red dot button appearance */
        section[data-testid="stSidebar"] .chat-row .dot .stButton>button {
            width: 14px !important;
            height: 14px !important;
            min-width: 14px !important;
            min-height: 14px !important;
            padding: 0 !important;
            border-radius: 50% !important;
            background: #ef4444 !important;
            border: 0 !important;
            box-shadow: none !important;
            color: transparent !important;
        }
        section[data-testid="stSidebar"] .chat-row .dot .stButton>button:hover { filter: brightness(0.9); }

        /* Responsive: tighten fonts/padding on narrow screens */
        @media (max-width: 480px) {
            .main-title { font-size: 1.6rem; }
            .subtitle { font-size: 0.95rem; }
            .chat-item-row { gap: 0.35rem; padding: 0.15rem 0.1rem; }
            section[data-testid="stSidebar"] .chat-row .stButton>button { font-size: 0.95rem !important; }
        }
        @media (max-width: 360px) {
            .main-title { font-size: 1.4rem; }
            .subtitle { font-size: 0.9rem; }
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-title"><strong>Eptura Asset AI</strong></div>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Ask me anything about your assets. I can help you find, analyze, and understand your asset data.</p>', unsafe_allow_html=True)
    
    def display_sidebar(self, config):
        """Sidebar with New chat button and list of ephemeral chats."""
        with st.sidebar:
            st.markdown('<strong style="font-size: 1rem;">Chats</strong>', unsafe_allow_html=True)
            active = self._get_active_chat()
            disable_new = active is not None and len(active.get("messages", [])) == 0 and len(st.session_state.chats) > 0
            if st.button("➕ New chat", use_container_width=True, disabled=disable_new, help=("Finish the current chat before creating a new one" if disable_new else None)):
                self._start_new_chat()
                st.rerun()

            # Render chat list (newest first) using minimal-styled buttons
            for chat in st.session_state.chats:
                # Backward-compatible: rename any legacy "New chat N" placeholders for display
                display_title = chat["title"]
                if display_title.lower().startswith("new chat "):
                    display_title = "Open chat"
                # Enforce a max of 20 visible characters for sidebar labels
                display_title = self._truncate_title(display_title, 20)
                with st.container(border=False):
                    st.button(
                        display_title,
                        key=f"open_{chat['id']}",
                        on_click=self._select_chat,
                        args=(chat["id"],),
                        use_container_width=True,
                    )

            st.markdown('<strong style="font-size: 1rem;">💡 Tips</strong>', unsafe_allow_html=True)
            st.markdown("• Ask specific questions about your assets")
            st.markdown("• Use asset IDs for precise searches")
            st.markdown("• Ask for summaries or comparisons")
            st.markdown("• Request data analysis or insights")
    
    def display_chat_interface(self, ai_chain: Any, retriever: Any):
        """Display the main chat interface for the active conversation."""
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        active_chat = self._get_active_chat()
        if active_chat is None:
            self._start_new_chat()
            active_chat = self._get_active_chat()

        # Display chat history for the active chat
        for message in active_chat["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about your assets..."):
            # Name chat immediately when user submits first message
            if len(active_chat["messages"]) == 0:
                active_chat["title"] = (prompt.strip() or "New chat")[:48]
            
            # Add user message to current chat
            active_chat["messages"].append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Build conversation history from previous messages
                        conversation_history = self._build_conversation_history(active_chat)
                        
                        # Check if it's a specific query that needs exact data
                        if self._is_data_query(prompt):
                            response = self._get_exact_data_response(prompt)
                        else:
                            response = ai_chain.invoke(prompt, conversation_history=conversation_history)
                        
                        st.markdown(response)
                        
                        # Add assistant response to chat history
                        active_chat["messages"].append({"role": "assistant", "content": response})
                        
                    except Exception as e:
                        error_msg = "I'm sorry, I encountered an error processing your request. Please try again or rephrase your question."
                        st.markdown(error_msg)
                        active_chat["messages"].append({"role": "assistant", "content": error_msg})
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display footer below the chat input
        st.markdown(
            '<div style="text-align: center; color: #6b7280; font-size: 0.85rem; margin-top: 1rem;">Eptura Asset AI • Powered by Sector7</div>', 
            unsafe_allow_html=True
        )
    
    def _is_data_query(self, query: str) -> bool:
        """Check if query needs exact data lookup (deterministic)."""
        q = (query or "").lower()
        if ("work order" in q or "work orders" in q) and "asset" in q:
            return True
        # Detect open work orders intents
        if ("open work orders" in q or "open work order" in q or "open wo" in q or "open wos" in q
            or ("work orders" in q and "open" in q)):
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
        """Deterministic lookup for work orders by assetId, including priorities and linked invoices."""
        try:
            import re
            import json
            from pathlib import Path

            q = (query or "")
            ql = q.lower()

            # If query requests open work orders (global)
            if ("open work orders" in ql or "open work order" in ql or "open wo" in ql or "open wos" in ql
                or ("work orders" in ql and "open" in ql)):
                return self._get_open_work_orders_response()

            # Otherwise, extract assetId token after the word 'asset'
            m = re.search(r"asset\s+([A-Za-z0-9\-_.]+)", q, flags=re.IGNORECASE)
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

    def _get_open_work_orders_response(self) -> str:
        """Return open work orders with strict filtering and nested list formatting grouped by entity."""
        try:
            import json
            from pathlib import Path

            base = Path("JsonData")
            wo_path = base / "WorkOrders.json"
            if not wo_path.exists():
                return "No work order data available."

            def load_json_safe(path: Path):
                for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                    try:
                        with open(path, 'r', encoding=enc) as f:
                            return json.load(f)
                    except Exception:
                        continue
                return []

            work_orders = load_json_safe(wo_path) or []

            # Option B: statusId=="New" AND dateCompleted is null AND workOrderActive==true
            def is_open(wo: dict) -> bool:
                return (
                    (wo.get("statusId") or "").strip().lower() == "new" and
                    (wo.get("dateCompleted") is None or str(wo.get("dateCompleted")).strip() == "") and
                    bool(wo.get("workOrderActive", False))
                )

            open_wos = [wo for wo in work_orders if is_open(wo)]
            if not open_wos:
                return "**0 open work orders** found."

            # Group by entityName
            grouped = {}
            for wo in open_wos:
                ent = (wo.get("entityName") or "Unknown").strip()
                grouped.setdefault(ent, []).append(wo)

            # Sort groups and items (by dateCreated desc within group)
            for ent, items in grouped.items():
                items.sort(key=lambda x: (x.get("dateCreated") or ""), reverse=True)

            lines = ["### Open Work Orders", "", f"- **Count**: {len(open_wos)}", "- **By entity**:"]
            for ent in sorted(grouped.keys()):
                items = grouped[ent]
                lines.append(f"  - **{ent}** ({len(items)})")
                for wo in items:
                    won = wo.get("workOrderNumber")
                    wok = wo.get("workOrderKey")
                    dc = wo.get("dateCreated")
                    st = wo.get("statusId")
                    pr = wo.get("priorityId")
                    lines.append(f"    - WO #{won or wok}: {st}, created {dc}, priority {pr}")

            return "\n".join(lines)
        except Exception:
            return "Unable to compute open work orders right now."
    
    def _build_conversation_history(self, chat) -> str:
        """Build conversation history string from a chat dict."""
        msgs = chat["messages"]
        if not msgs or len(msgs) < 2:
            return "No previous conversation."
        
        # Get last 10 messages (5 exchanges) to avoid token limits
        recent_messages = msgs[-10:]
        
        history = ""
        for message in recent_messages:
            role = "User" if message["role"] == "user" else "Assistant"
            history += f"{role}: {message['content']}\n\n"
        
        return history.strip()
