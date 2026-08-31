import os
import time
import requests
import streamlit as st

from logging_config import get_logger


logger = get_logger(__name__)


st.set_page_config(
    page_title="NUTRI-QUERY RAG",
    layout="wide"
)


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


if "selected_bucket" not in st.session_state:
    st.session_state.selected_bucket = None

if "messages" not in st.session_state:
    st.session_state.messages = []


DATA_DIR = "data"

ALLOWED_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".pdf",
    ".txt"
)


def render_sources(sources_dict: dict):
    """Render retrieved source files grouped by bucket."""

    if not sources_dict:
        return

    st.markdown("---")
    st.markdown("### 📌 Sources Used")

    for bucket, files in sources_dict.items():

        with st.expander(
            f"📁 **Bucket:** `{bucket}` ({len(files)} items)",
            expanded=True
        ):

            for file_name in files:

                file_path = os.path.join(
                    DATA_DIR,
                    bucket,
                    file_name
                )

                # Display retrieved images in chat
                if file_name.lower().endswith(
                    (".png", ".jpg", ".jpeg")
                ):
                    st.markdown(
                        f"🖼️ **Image:** `{file_name}`"
                    )

                    if os.path.exists(file_path):
                        st.image(
                            file_path,
                            width=320,
                            caption=file_name
                        )
                    else:
                        st.caption(
                            f"*(Image preview unavailable at "
                            f"`{file_path}`)*"
                        )

                # Display PDF source name
                elif file_name.lower().endswith(".pdf"):
                    st.markdown(
                        f"📄 **Document:** `{file_name}`"
                    )

                # Display TXT source name
                else:
                    st.markdown(
                        f"📝 **Text File:** `{file_name}`"
                    )


with st.sidebar:

    st.subheader("📁 Knowledge Base")

    if os.path.exists(DATA_DIR):

        buckets = [
            bucket
            for bucket in os.listdir(DATA_DIR)
            if os.path.isdir(
                os.path.join(DATA_DIR, bucket)
            )
        ]

        for bucket in buckets:

            bucket_path = os.path.join(
                DATA_DIR,
                bucket
            )

            files = [
                file_name
                for file_name in os.listdir(bucket_path)
                if (
                    os.path.isfile(
                        os.path.join(
                            bucket_path,
                            file_name
                        )
                    )
                    and file_name.lower().endswith(
                        ALLOWED_EXTENSIONS
                    )
                )
            ]

            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(
                    f"**{bucket}** ({len(files)} docs)"
                )

            with col2:

                is_selected = (
                    st.session_state.selected_bucket
                    == bucket
                )

                button_label = (
                    "Close"
                    if is_selected
                    else "View"
                )

                if st.button(
                    button_label,
                    key=f"view_{bucket}"
                ):

                    if is_selected:
                        st.session_state.selected_bucket = None
                    else:
                        st.session_state.selected_bucket = bucket

                    st.rerun()

            if st.session_state.selected_bucket == bucket:

                with st.expander(
                    f"📂 {bucket} Contents",
                    expanded=True
                ):

                    for file_name in files:
                        st.write(
                            f"📄 {file_name}"
                        )

                st.markdown("---")


st.title("🥗 NUTRI-QUERY RAG")
st.caption("Food & Nutrition Assistant")


for message in st.session_state.messages:

    avatar = (
        "👤"
        if message["role"] == "user"
        else "🤖"
    )

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):

        st.markdown(
            message["content"]
        )

        if (
            "sources" in message
            and message["sources"]
        ):
            render_sources(
                message["sources"]
            )


if prompt := st.chat_input(
    "Ask your nutrition or document query..."
):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message(
        "user",
        avatar="👤"
    ):
        st.markdown(prompt)

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner(
            "Analyzing knowledge base..."
        ):

            request_start = time.perf_counter()

            logger.info(
                "request_sent",
                extra={
                    "details": {
                        "endpoint": "/ask",
                        "query": prompt
                    }
                }
            )

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/ask",
                    json={"query": prompt},
                    timeout=120
                )

                request_latency = (
                    time.perf_counter()
                    - request_start
                )

                if response.status_code == 200:

                    result = response.json()

                    answer = result.get(
                        "answer",
                        ""
                    )

                    sources = result.get(
                        "sources",
                        {}
                    )

                    logger.info(
                        "response_received",
                        extra={
                            "details": {
                                "endpoint": "/ask",
                                "status_code": 200,
                                "latency_sec": round(
                                    request_latency,
                                    3
                                )
                            }
                        }
                    )

                else:

                    answer = (
                        f"⚠️ API Error "
                        f"(Status {response.status_code}): "
                        f"{response.text}"
                    )

                    sources = {}

                    logger.warning(
                        "api_response_error",
                        extra={
                            "details": {
                                "endpoint": "/ask",
                                "status_code": response.status_code,
                                "latency_sec": round(
                                    request_latency,
                                    3
                                )
                            }
                        }
                    )

            except requests.exceptions.Timeout:

                logger.error(
                    "api_request_timeout",
                    extra={
                        "details": {
                            "endpoint": "/ask",
                            "timeout_sec": 120,
                            "latency_sec": round(
                                time.perf_counter()
                                - request_start,
                                3
                            )
                        }
                    }
                )

                answer = (
                    "The request timed out while "
                    "waiting for the backend."
                )

                sources = {}

            except requests.exceptions.ConnectionError:

                logger.error(
                    "backend_connection_failed",
                    extra={
                        "details": {
                            "endpoint": "/ask",
                            "latency_sec": round(
                                time.perf_counter()
                                - request_start,
                                3
                            )
                        }
                    }
                )

                answer = (
                    "❌ **Connection Error:** "
                    "Could not connect to FastAPI server."
                )

                sources = {}

            except Exception as e:

                logger.exception(
                    "frontend_request_failed",
                    extra={
                        "details": {
                            "endpoint": "/ask",
                            "error": str(e),
                            "latency_sec": round(
                                time.perf_counter()
                                - request_start,
                                3
                            )
                        }
                    }
                )

                answer = (
                    f"❌ An unexpected error occurred: {e}"
                )

                sources = {}

            st.markdown(answer)

            render_sources(sources)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )