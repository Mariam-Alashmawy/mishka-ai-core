import streamlit as st
import os
import json
from typing import Dict, Any, List
#Mind Map Component Import
from streamlit_agraph import agraph, Node, Edge, Config 
# 1. IMPORTS & CONFIGURATION
from modules.file_processor import FileProcessor
from modules.generator import Generator
from modules.memory_manager import MemoryManager
#Custom CSS for Layout and Theme
def inject_custom_css():
    st.markdown(
        """
        <style>
        /* CRITICAL: Force full width content area */
        .main .block-container {
            max-width: 90% !important; 
            padding-left: 5rem; 
            padding-right: 5rem;
            margin: unset; 
        }
        /* 2. Round the Edges of Widgets and Boxes */
        div.stDownloadButton, div.stButton > button, div[data-baseweb="select"], 
        div[data-baseweb="file-uploader"], div[data-baseweb="textarea"], div[data-baseweb="input"] {
            border-radius: 12px; 
        }
        /* 3. Apply Gradient to Primary Button */
        .stButton button.css-1n9y56p { 
            background-color: #dfbe55; 
            background-image: linear-gradient(to bottom, #dfbe55, #B8860B); 
            color: #141f2c; 
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4); 
            font-weight: bold;
            padding: 10px 20px;
        }
        /* 4. Fix Text Color on Main Background */
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .css-1d2o2ui { 
            color: #ECEFF1; 
        }
        </style>
        """,
        unsafe_allow_html=True
    )
#Page Setup
st.set_page_config(page_title="Mishka AI Tutor", layout="wide") 
inject_custom_css() 
#Session State
if "session_id" not in st.session_state: st.session_state.session_id = None
if "messages" not in st.session_state: st.session_state.messages = []
if "processing_complete" not in st.session_state: st.session_state.processing_complete = False
if "quiz_data" not in st.session_state: st.session_state.quiz_data = None
if "flashcard_data" not in st.session_state: st.session_state.flashcard_data = None
if "mindmap_data" not in st.session_state: st.session_state.mindmap_data = None
if "raw_content_data" not in st.session_state: st.session_state.raw_content_data = {} 
if "final_summary" not in st.session_state: st.session_state.final_summary = None 
#Load Classes
@st.cache_resource
def load_modules():
    return FileProcessor(), Generator(), MemoryManager()
processor, ai_engine, memory_manager = load_modules()

# 2. HELPER FUNCTIONS

def generate_and_store_tool(tool_type: str, complexity: str = 'Intermediate'):

    """

    Calls the direct API generation logic and stores the result.

    """
    if not st.session_state.session_id:
        st.error("Session not started. Please upload a file first.")
        return
    content_data = st.session_state.raw_content_data
    if not content_data or "content" not in content_data:
        st.error("Cannot generate tools. Document content is missing from memory.")
        return
    with st.spinner(f"Mishka is generating {tool_type.replace('_', ' ')}..."):
        result = ai_engine.generate_tool_directly(
            tool_type=tool_type,
            complexity=complexity,
            content_data=content_data 
        )
        if result.get("status") == "success":
            if tool_type == 'quizzes':
                st.session_state.quiz_data = result['content']
            elif tool_type == 'flashcards':
                st.session_state.flashcard_data = result['content']
            elif tool_type == 'mind_maps':
                st.session_state.mindmap_data = result['content']
            st.success(f"{tool_type.replace('_', ' ').title()} Generated Successfully!")
        else:
            st.error(f"Error generating {tool_type}: {result.get('message', 'Unknown error')}")
def finalize_session():

    """

    Generates the final JSON summary of the session using the full conversation history.

    """
    if not st.session_state.session_id:
        st.error("Cannot finalize: Session ID is missing.")
        return
    # Retrieve full conversation history from memory manager
    conversation_history = memory_manager.get_history(st.session_state.session_id)
    if not conversation_history:
        st.warning("No conversation history found to summarize.")
        return
    with st.spinner("Mishka is generating your final study report..."):
        # Call the generator function to get the raw JSON string
        raw_json_string = ai_engine.generate_json_summary(conversation_history)
        try:
            # Clean and parse the output
            clean_json = raw_json_string.replace("```json", "").replace("```", "").strip()
            parsed_summary = json.loads(clean_json)
            # Store and display success
            st.session_state.final_summary = parsed_summary
            st.success("Study Report Generated Successfully!")
        except json.JSONDecodeError:
            st.error(f"Failed to parse model output into JSON. Output: {raw_json_string[:50]}...")
        except Exception as e:
            st.error(f"An unexpected error occurred during summary generation: {e}")
def display_quiz_ui(quiz_content):
    st.subheader("Practice Quiz")
    if not quiz_content: return
    for i, quiz in enumerate(quiz_content):
        st.markdown(f"**Q{i+1}: {quiz.get('question', 'Question text')}:**")
        options = quiz.get("options", [])
        correct = quiz.get("correct_answer", "")
        st.radio(f"Select answer:", options, key=f"q_{i}_{st.session_state.session_id}") 
        with st.expander("Show Correct Answer"):
            st.write(f"Correct Answer: **{correct}**") 
        st.markdown("---")
def display_flashcards_ui(flashcards):
    st.subheader("Flashcards") 
    if not flashcards: return
    for card in flashcards:
        card_type = card.get('type', 'term').upper() 
        title = f"{card_type}: {card.get('front')}" 
        with st.expander(title):
            st.info(f"Explanation: {card.get('back')}")
#Mind Map Display Function 
def display_mindmap_ui(mindmap):
    st.subheader("🧠 Structure (Interactive Mind Map)")
    if not mindmap: return
    nodes = []
    edges = []
    node_id_counter = 0
    # Define color scheme for better hierarchy
    ROOT_COLOR = "#dfbe55"  # Gold
    LEVEL1_COLOR = "#00BFFF" # Deep Sky Blue for main topics
    LEVEL2_COLOR = "#ECEFF1" # White/Light Gray for details
    def build_graph(data, parent_id=None, depth=0):
        nonlocal node_id_counter
        node_title = data.get('title', 'Unknown') 
        current_id = str(node_id_counter)
        node_id_counter += 1
        # Determine color based on depth
        if depth == 0:
            color = ROOT_COLOR
        elif depth == 1:
            color = LEVEL1_COLOR
        else:
            color = LEVEL2_COLOR

        nodes.append(Node(
            id=current_id, 
            label=node_title, 
            # Size based on depth for hierarchy
            size=20 if depth == 0 else (15 if depth == 1 else 10), 
            color=color, 
            # Fixed font color for readability on dark background
            font={"size": 18 if depth == 0 else 14, "color": "#FFFFFF"}, 
            title=node_title
        ))
        if parent_id is not None:
            edges.append(Edge(
                source=parent_id,
                target=current_id,
                # Removed edge label for a clean Mind Map look
                label="", 
                color={"color": "#FFC0CB"} # Light pink/rose color for edges
            ))
        # Recursively process children
        if data.get('children'):
            for child in data['children']:
                build_graph(child, current_id, depth + 1)
    # Start building the graph from the root
    build_graph(mindmap)
    # 3. Configure the visualization component
    config = Config(
        width=700,
        height=500,
        directed=True, 
        nodeHighlightBehavior=True,
        highlightColor="#F7931A", 
        nodeDistance=150, 
        linkDistance=150,
        # Set collapsible back to True for native component control
        collapsible=True, 
        # Use Hierarchical Layout for clear structure
        layout={"hierarchical": {"enabled": True, "direction": "UD", "sortMethod": "directed"}},
        staticGraphWithForces=False, 
        backgroundColor="#141f2c",
        view_scale=True, 
        physics=True, 
        edges={"smooth": False} 
    )
    # 4. Render the Mind Map
    if nodes:
        # Note: We are no longer capturing the click result for custom collapse
        agraph(nodes=nodes, edges=edges, config=config)
    else:
        st.warning("No nodes generated for the mind map.")
# 3. MAIN APP UI

st.title("Mishka: AI Interactive Tutor") 

# Phase 1: File Upload

if not st.session_state.processing_complete:
    st.markdown("### Welcome! Upload your lecture to start.")
    uploaded_file = st.file_uploader("Drop your PDF, Image, or PowerPoint here:", type=['pdf', 'docx', 'pptx', 'png', 'jpg', 'txt'])
    summary_level = st.selectbox("Choose Explanation Level:", ["detailed", "simple"])
    start_btn = st.button("Start Learning", type="primary") 
    if start_btn and uploaded_file:
        with st.spinner("Mishka is reading your file..."):
            try:
                # 1. Save File
                upload_dir = "data/uploads"
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                # 2. Create Session
                session_id = memory_manager.create_new_session(file_path)
                st.session_state.session_id = session_id
                # 3. Extract Content
                content_data = processor.extract_content(file_path, uploaded_file.type)
                if "error" in content_data:
                    st.error(f"Extraction Error: {content_data['error']}")
                else:
                    st.session_state.raw_content_data = content_data 
                    # 4. Generate Explanation
                    explanation = ai_engine.generate_explanation(content_data, summary_level)
                    # 5. Save to History
                    memory_manager.add_turn(
                        session_id, 
                        f"Explain this file. Level: {summary_level}", 
                        explanation
                    )
                    # Update State
                    st.session_state.messages.append({"role": "assistant", "content": explanation})
                    st.session_state.processing_complete = True
                    st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Phase 2: Chat & Tools

else:
    col1, col2 = st.columns([1.5, 1])
    #Left Column: Chat & Summary 
    with col1:
        st.subheader("Chat") 
        # Display existing messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        # Chat Input and Logic (FULLY ENABLED)
        if prompt := st.chat_input("Ask a question..."):
            # Display user message immediately
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.spinner("Mishka is thinking..."):
                # 1. Retrieve the *full* conversation history from MemoryManager
                full_history = memory_manager.get_history(st.session_state.session_id)
                # 2. Call the generator's chat method
                response_text = ai_engine.chat(full_history, prompt)
                # 3. Add both turns to the MemoryManager 
                memory_manager.add_turn(st.session_state.session_id, prompt, response_text)
                # 4. Update session state to display the new assistant response
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            # Re-run the app to display the new messages
            st.rerun() 
        st.markdown("---")
        #Finalize Session / Study Report
        st.subheader("Session Control")
        if st.button("Generate Study Report", key="finalize_btn", help="Analyze the entire conversation and generate a final summary."):
            finalize_session()
        if st.session_state.final_summary:
            with st.expander("📝 View Study Report"):
                summary_data = st.session_state.final_summary
                st.markdown(f"**Topic:** {summary_data.get('topic', 'N/A')}")
                st.markdown(f"**Difficulty:** {summary_data.get('difficulty_level', 'N/A')}")
                st.markdown("---")
                st.markdown("**Comprehensive Summary**")
                st.write(summary_data.get('summary', ''))
                st.markdown("**Key Points Covered**")
                st.markdown("\n".join(f"* {point}" for point in summary_data.get('key_points', [])))
                st.markdown("**Student Questions Asked**")
                st.markdown("\n".join(f"* {q}" for q in summary_data.get('student_questions', [])))
        if st.button("New Session", key="new_session_btn"): 
            st.session_state.clear()
            st.rerun()
    # --- Right Column: Tools ---
    with col2:
        st.subheader("Study Tools") 
        tab1, tab2, tab3 = st.tabs(["Quizzes", "Flashcards", "Mind Map"])
        # QUIZZES
        with tab1:
            quiz_diff = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Expert"], key="q_diff")
            if st.button("Generate Quiz", type="primary"): 
                generate_and_store_tool("quizzes", complexity=quiz_diff)
            if st.session_state.quiz_data:
                display_quiz_ui(st.session_state.quiz_data)
        # FLASHCARDS
        with tab2:
            if st.button("Generate Flashcards", type="primary"):
                generate_and_store_tool("flashcards")
            if st.session_state.flashcard_data:
                display_flashcards_ui(st.session_state.flashcard_data)
        # MIND MAP
        with tab3:
            if st.button("Generate Map", type="primary"):
                generate_and_store_tool("mind_maps")
            if st.session_state.mindmap_data:
                display_mindmap_ui(st.session_state.mindmap_data)