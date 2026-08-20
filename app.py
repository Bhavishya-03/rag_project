# import os
# import base64
# import requests
# import streamlit as st
# from main import ask_rag

# st.set_page_config(page_title="NUTRI-QUERY RAG", layout="wide")

# # CSS
# st.markdown(
#     """
#     <style>
#     div[data-testid="stStatusWidget"], 
#     div[data-testid="stToolbar"] {
#         visibility: visible !important;
#         display: flex !important;
#     }

#     div[data-testid="stException"] button,
#     div[data-testid="stException"] a {
#         display: none !important;
#     }

#     div[data-testid="stChatInput"] textarea:focus {
#         border-color: #4A5568 !important;
#         box-shadow: 0 0 0 1px #4A5568 !important;
#     }

#     div[data-testid="stChatInput"] > div:focus-within {
#         border-color: #4A5568 !important;
#     }

#     div[data-testid="stChatInput"] button {
#         background-color: #4A5568 !important;
#         color: #FFFFFF !important;
#         border: none !important;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# # Initialize Session States
# if "selected_bucket" not in st.session_state:
#     st.session_state.selected_bucket = None
# if "selected_doc" not in st.session_state:
#     st.session_state.selected_doc = None
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# DATA_DIR = "data"
# ALLOWED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.pdf', '.txt')


# def render_sources(sources_dict: dict):
#     """Renders sources grouped by bucket, with inline image previews."""
#     if not sources_dict:
#         return

#     st.markdown("---")
#     st.markdown("### 📌 Sources Used")

#     for bucket, files in sources_dict.items():
#         with st.expander(f"📁 **Bucket:** `{bucket}` ({len(files)} items)", expanded=True):
#             for file_name in files:
#                 file_path = os.path.join(DATA_DIR, bucket, file_name)
                
#                 # Render Image files with inline preview
#                 if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
#                     st.markdown(f"🖼️ **Image:** `{file_name}`")
#                     if os.path.exists(file_path):
#                         st.image(file_path, width=320, caption=file_name)
#                     else:
#                         st.caption(f"*(Image preview unavailable at `{file_path}`)*")
                
#                 # Render PDF files
#                 elif file_name.lower().endswith('.pdf'):
#                     st.markdown(f"📄 **Document:** `{file_name}`")
                
#                 # Render Text files
#                 else:
#                     st.markdown(f"📝 **Text File:** `{file_name}`")


# # Sidebar Workspace
# with st.sidebar:
#     st.subheader("📁 Knowledge Base")
    
#     if os.path.exists(DATA_DIR):
#         buckets = [b for b in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, b))]
        
#         for bucket in buckets:
#             bucket_path = os.path.join(DATA_DIR, bucket)
#             files = [
#                 f for f in os.listdir(bucket_path) 
#                 if os.path.isfile(os.path.join(bucket_path, f)) and f.lower().endswith(ALLOWED_EXTENSIONS)
#             ]
            
#             col1, col2 = st.columns([3, 1])
#             with col1:
#                 st.write(f"**{bucket}** ({len(files)} docs)")
#             with col2:
#                 if st.button("View", key=f"view_{bucket}"):
#                     st.session_state.selected_bucket = bucket
#                     st.session_state.selected_doc = None
#                     st.rerun()


# # Main Workspace
# st.title("🥗 NUTRI-QUERY RAG")
# st.caption("Food & Nutrition Assistant")

# # Document & Bucket Viewer
# if st.session_state.selected_bucket:
#     bucket_name = st.session_state.selected_bucket
#     bucket_dir = os.path.join(DATA_DIR, bucket_name)
    
#     with st.expander(f"📁 Previewing: {bucket_name}", expanded=True):
#         if st.button("Close Preview"):
#             st.session_state.selected_bucket = None
#             st.session_state.selected_doc = None
#             st.rerun()
            
#         if os.path.exists(bucket_dir):
#             doc_files = [
#                 f for f in os.listdir(bucket_dir) 
#                 if os.path.isfile(os.path.join(bucket_dir, f)) and f.lower().endswith(ALLOWED_EXTENSIONS)
#             ]
            
#             st.write("### Documents in Bucket:")
#             for doc in doc_files:
#                 if st.button(f"📄 {doc}", key=f"doc_{doc}"):
#                     st.session_state.selected_doc = doc

#             # Document Display Renderer
#             if st.session_state.selected_doc:
#                 doc_path = os.path.join(bucket_dir, st.session_state.selected_doc)
#                 st.markdown(f"--- \n#### Displaying: `{st.session_state.selected_doc}`")
                
#                 try:
#                     if doc_path.lower().endswith('.txt'):
#                         with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
#                             st.text_area("File Content", f.read(), height=300)

#                     elif doc_path.lower().endswith(('.png', '.jpg', '.jpeg')):
#                         st.image(doc_path, caption=st.session_state.selected_doc, use_container_width=True)
                    
#                     elif doc_path.lower().endswith('.pdf'):
#                         with open(doc_path, "rb") as f:
#                             base64_pdf = base64.b64encode(f.read()).decode('utf-8')
#                         pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
#                         st.markdown(pdf_display, unsafe_allow_html=True)

#                 except Exception as e:
#                     st.error(f"Could not render file: {e}")

# # Render Chat History
# for message in st.session_state.messages:
#     avatar = "👤" if message["role"] == "user" else "🤖"
#     with st.chat_message(message["role"], avatar=avatar):
#         st.markdown(message["content"])
#         if "sources" in message and message["sources"]:
#             render_sources(message["sources"])

# # Chat Input Handler
# if prompt := st.chat_input("Ask your nutrition or document query..."):
#     # Render User Message
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user", avatar="👤"):
#         st.markdown(prompt)

#     with st.chat_message("assistant", avatar="🤖"):
#         with st.spinner("Analyzing knowledge base..."):
#             try:
#                 # Send HTTP POST request to FastAPI Swagger backend
#                 response = requests.post(
#                     "http://127.0.0.1:8000/ask",
#                     json={"query": prompt},
#                     timeout=120  # Gives Ollama time to process response
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     answer = result.get("answer", "")
#                     sources = result.get("sources", {})
#                 else:
#                     answer = f"⚠️ API Error (Status {response.status_code}): {response.text}"
#                     sources = {}

#             except requests.exceptions.ConnectionError:
#                 answer = "❌ **Connection Error:** Could not connect to FastAPI server. Make sure `uvicorn api:app --reload` is running on `http://127.0.0.1:8000`."
#                 sources = {}
#             except Exception as e:
#                 answer = f"❌ An unexpected error occurred: {e}"
#                 sources = {}

#             st.markdown(answer)
#             render_sources(sources)

#     # Save to Session State for Chat Persistence
#     st.session_state.messages.append({
#         "role": "assistant",
#         "content": answer,
#         "sources": sources
#     })
import os
import base64
import requests
import streamlit as st

st.set_page_config(page_title="NUTRI-QUERY RAG", layout="wide")

# CSS
st.markdown(
    """
    <style>
    div[data-testid="stStatusWidget"], 
    div[data-testid="stToolbar"] {
        visibility: visible !important;
        display: flex !important;
    }

    div[data-testid="stException"] button,
    div[data-testid="stException"] a {
        display: none !important;
    }

    div[data-testid="stChatInput"] textarea:focus {
        border-color: #4A5568 !important;
        box-shadow: 0 0 0 1px #4A5568 !important;
    }

    div[data-testid="stChatInput"] > div:focus-within {
        border-color: #4A5568 !important;
    }

    div[data-testid="stChatInput"] button {
        background-color: #4A5568 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize Session States
if "selected_bucket" not in st.session_state:
    st.session_state.selected_bucket = None
if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = None
if "messages" not in st.session_state:
    st.session_state.messages = []

DATA_DIR = "data"
ALLOWED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.pdf', '.txt')


def render_sources(sources_dict: dict):
    """Renders sources grouped by bucket, with inline image previews in the chat."""
    if not sources_dict:
        return

    st.markdown("---")
    st.markdown("### 📌 Sources Used")

    for bucket, files in sources_dict.items():
        with st.expander(f"📁 **Bucket:** `{bucket}` ({len(files)} items)", expanded=True):
            for file_name in files:
                file_path = os.path.join(DATA_DIR, bucket, file_name)
                
                # Render Image files with inline preview
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    st.markdown(f"🖼️ **Image:** `{file_name}`")
                    if os.path.exists(file_path):
                        st.image(file_path, width=320, caption=file_name)
                    else:
                        st.caption(f"*(Image preview unavailable at `{file_path}`)*")
                
                # Render PDF files
                elif file_name.lower().endswith('.pdf'):
                    st.markdown(f"📄 **Document:** `{file_name}`")
                
                # Render Text files
                else:
                    st.markdown(f"📝 **Text File:** `{file_name}`")


# Sidebar Workspace (Handles Buckets & In-Sidebar Document Preview)
with st.sidebar:
    st.subheader("📁 Knowledge Base")
    
    if os.path.exists(DATA_DIR):
        buckets = [b for b in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, b))]
        
        for bucket in buckets:
            bucket_path = os.path.join(DATA_DIR, bucket)
            files = [
                f for f in os.listdir(bucket_path) 
                if os.path.isfile(os.path.join(bucket_path, f)) and f.lower().endswith(ALLOWED_EXTENSIONS)
            ]
            
            # Bucket List Header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{bucket}** ({len(files)} docs)")
            with col2:
                # Toggle view state for this bucket
                is_selected = st.session_state.selected_bucket == bucket
                btn_label = "Close" if is_selected else "View"
                
                if st.button(btn_label, key=f"view_{bucket}"):
                    if is_selected:
                        st.session_state.selected_bucket = None
                        st.session_state.selected_doc = None
                    else:
                        st.session_state.selected_bucket = bucket
                        st.session_state.selected_doc = None
                    st.rerun()

            # Render bucket items inside sidebar if selected
            if st.session_state.selected_bucket == bucket:
                with st.expander(f"📂 {bucket} Contents", expanded=True):
                    for doc in files:
                        if st.button(f"📄 {doc}", key=f"sidebar_doc_{bucket}_{doc}"):
                            st.session_state.selected_doc = doc

                    # Display document preview right inside the sidebar
                    if st.session_state.selected_doc and st.session_state.selected_doc in files:
                        doc_path = os.path.join(bucket_path, st.session_state.selected_doc)
                        st.markdown("---")
                        st.markdown(f"**Previewing:** `{st.session_state.selected_doc}`")
                        
                        try:
                            if doc_path.lower().endswith('.txt'):
                                with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    st.text_area("Content", f.read(), height=200)

                            elif doc_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                                st.image(doc_path, caption=st.session_state.selected_doc, use_container_width=True)
                            
                            elif doc_path.lower().endswith('.pdf'):
                                with open(doc_path, "rb") as f:
                                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)

                        except Exception as e:
                            st.error(f"Error previewing file: {e}")
                st.markdown("---")


# Main Workspace (Chat Interface Only)
st.title("🥗 NUTRI-QUERY RAG")
st.caption("Food & Nutrition Assistant")

# Render Chat History
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            render_sources(message["sources"])

# Chat Input Handler
if prompt := st.chat_input("Ask your nutrition or document query..."):
    # Render User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analyzing knowledge base..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/ask",
                    json={"query": prompt},
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("answer", "")
                    sources = result.get("sources", {})
                else:
                    answer = f"⚠️ API Error (Status {response.status_code}): {response.text}"
                    sources = {}

            except requests.exceptions.ConnectionError:
                answer = "❌ **Connection Error:** Could not connect to FastAPI server. Make sure `uvicorn api:app --reload` is running on `http://127.0.0.1:8000`."
                sources = {}
            except Exception as e:
                answer = f"❌ An unexpected error occurred: {e}"
                sources = {}

            st.markdown(answer)
            render_sources(sources)

    # Save to Session State for Chat Persistence
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })