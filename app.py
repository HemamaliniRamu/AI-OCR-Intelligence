"""
app.py - Streamlit Web Application for AI OCR Intelligence System
Powered by Tesseract, Mojo, Modular MAX, and LangChain
"""

import os
import json
import tempfile
from pathlib import Path
from PIL import Image
import streamlit as st

from ocr import extract_text, is_tesseract_installed, is_mojo_installed, find_tesseract_path
from extractor import extract_information, save_information
from max_inference import MAXEngineClient
from qa import answer_document_question, create_prompt

# Page configuration
st.set_page_config(
    page_title="AI OCR Intelligence System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #4f46e5;
        margin-bottom: 10px;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge-active { background-color: #dcfce7; color: #15803d; }
    .badge-offline { background-color: #fee2e2; color: #b91c1c; }
    .badge-mojo { background-color: #e0e7ff; color: #3730a3; }
</style>
""", unsafe_allow_html=True)

# ----------------- Sidebar: System Diagnostics -----------------
with st.sidebar:
    st.title("⚡ System Status")
    
    # Tesseract Status
    tess_installed = is_tesseract_installed()
    tess_path = find_tesseract_path()
    if tess_installed:
        st.success("✅ **Tesseract OCR:** Active")
        st.caption(f"`{tess_path}`")
    else:
        st.error("❌ **Tesseract OCR:** Not Detected")
        st.caption("Install from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)")

    st.divider()

    # Mojo Status
    mojo_available = is_mojo_installed()
    if mojo_available:
        st.success("🔥 **Mojo Preprocessor:** Enabled")
    else:
        st.info("ℹ️ **Mojo Preprocessor:** Python Fallback Active")
        st.caption("Mojo binary not found in PATH. Preprocessing running in high-fidelity fallback mode.")

    st.divider()

    # Modular MAX Server Status
    max_client = MAXEngineClient()
    max_online = max_client.is_online()
    if max_online:
        st.success(f"🚀 **Modular MAX Serve:** Online")
        st.caption(f"Model: `{max_client.model_name}`")
    else:
        st.warning("⚠️ **Modular MAX Serve:** Offline")
        st.caption("Using document heuristic responder. To activate neural inference, run:")
        st.code(f"max serve --model {max_client.model_name} --port 8000", language="bash")

    st.divider()
    st.caption("AI OCR Intelligence System v0.1.0 • Windows + Anaconda + MAX/Mojo")

# ----------------- Main Interface -----------------
st.title("📄 AI OCR Intelligence System")
st.markdown(
    "**End-to-End Pipeline:** `Document Image` ➔ `Tesseract OCR` ➔ `Mojo Preprocessing` ➔ `Structured Extraction` ➔ `LangChain + Modular MAX` ➔ `Intelligent Q&A`"
)

# Upload or Sample Selector
col_upload, col_sample = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload an Invoice or Form (PNG, JPG, JPEG):",
        type=["png", "jpg", "jpeg"]
    )

with col_sample:
    st.write("Or use built-in demo:")
    use_sample = st.button("Load Sample Invoice 🧾")

image_path = None
active_image = None

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
        temp.write(uploaded_file.read())
        image_path = temp.name
    active_image = Image.open(image_path)
elif use_sample:
    sample_file = Path(__file__).parent / "documents" / "invoice.png"
    if not sample_file.exists():
        # Generate sample invoice if not present
        from generate_sample import generate_invoice_image
        generate_invoice_image(str(sample_file))
    image_path = str(sample_file)
    active_image = Image.open(image_path)

# Execution Pipeline
if active_image and image_path:
    # 1. OCR Extraction
    with st.spinner("Executing Tesseract OCR & Mojo Preprocessor..."):
        try:
            ocr_result = extract_text(image_path, use_mojo=True)
        except FileNotFoundError as e:
            st.error(str(e))
            st.stop()

    raw_text = ocr_result["raw_text"]
    cleaned_text = ocr_result["cleaned_text"]
    mojo_accelerated = ocr_result["mojo_accelerated"]

    # 2. Structured Information Extraction
    structured_info = extract_information(cleaned_text)
    save_information(structured_info, Path(__file__).parent / "output" / "extracted.json")

    # Display in 4 Tabs
    tab_doc, tab_mojo, tab_json, tab_qa = st.tabs([
        "🖼️ Document & Raw OCR",
        "🔥 Mojo Preprocessing",
        "📊 Structured JSON",
        "🤖 MAX + LangChain Q&A"
    ])

    with tab_doc:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.subheader("Source Document")
            st.image(active_image, use_container_width=True)
        with c2:
            st.subheader("Raw Tesseract OCR Output")
            st.text_area("OCR Text Stream", raw_text, height=360)

    with tab_mojo:
        st.subheader("Mojo Preprocessing Pipeline")
        st.markdown(
            f"**Status:** {'🔥 Accelerated by Mojo Native Engine' if mojo_accelerated else '⚙️ High-Fidelity Python Fallback'}"
        )
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("**Original Raw Stream:**")
            st.code(raw_text, language="text")
        with col_m2:
            st.markdown("**Mojo Normalized Stream:**")
            st.code(cleaned_text, language="text")
        st.info("Mojo normalizes linebreaks, collapses redundant whitespace tokens, and standardizes key invoice delimiters.")

    with tab_json:
        st.subheader("Structured Document Data")
        
        # Metric cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Invoice Number", structured_info.get("invoice_number") or "N/A")
        m2.metric("Date", structured_info.get("date") or "N/A")
        m3.metric("Customer", structured_info.get("customer") or "N/A")
        m4.metric("Grand Total", structured_info.get("total") or "N/A")

        if structured_info.get("items"):
            st.markdown("### 🛒 Line Items")
            st.table(structured_info["items"])

        st.markdown("### 📁 Raw JSON (`output/extracted.json`)")
        st.json(structured_info)

    with tab_qa:
        st.subheader("🤖 Ask Questions About This Document")
        st.caption("Powered by LangChain prompt orchestrator and Modular MAX Inference Engine")

        # Quick Question Buttons
        st.markdown("**Quick Prompts:**")
        q_cols = st.columns(3)
        selected_prompt = None
        if q_cols[0].button("What is the total?"):
            selected_prompt = "What is the total amount?"
        if q_cols[1].button("Who is the customer?"):
            selected_prompt = "Who is the customer?"
        if q_cols[2].button("What is the invoice number?"):
            selected_prompt = "What is the invoice number?"

        q_cols2 = st.columns(3)
        if q_cols2[0].button("How much did the laptop cost?"):
            selected_prompt = "How much did the laptop cost?"
        if q_cols2[1].button("Which item is most expensive?"):
            selected_prompt = "Which item is the most expensive?"
        if q_cols2[2].button("List all items"):
            selected_prompt = "What are the items present in this invoice?"

        user_question = st.text_input(
            "Enter your question:",
            value=selected_prompt if selected_prompt else ""
        )

        if st.button("Ask Assistant ⚡", type="primary") or selected_prompt:
            if user_question:
                with st.spinner("Processing with LangChain & MAX..."):
                    response = answer_document_question(
                        document_text=cleaned_text,
                        structured_data=structured_info,
                        question=user_question,
                        max_client=max_client
                    )
                st.markdown("### Answer:")
                st.success(response["answer"])
                st.caption(f"**Inference Provider:** `{response['engine']}` • **Model:** `{response['model']}`")
else:
    st.info("👆 Upload an invoice image or click **'Load Sample Invoice'** to run the complete pipeline.")
