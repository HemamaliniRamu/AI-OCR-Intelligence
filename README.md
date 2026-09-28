# ⚡ AI OCR Intelligence System

An end-to-end intelligent document processing system built with **Tesseract OCR**, **Mojo**, **Modular MAX**, **LangChain**, and **Streamlit**.

---

## 🏗️ Architecture Pipeline

```text
       ┌────────────────────────┐
       │   Invoice / Form Image │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │     Tesseract OCR      │ ➔ Raw Text Stream
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   Mojo Preprocessor    │ ➔ Fast Line/Token Normalization
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  Structured Extractor  │ ➔ Extracted JSON (Invoice #, Date, Items, Total)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │       LangChain        │ ➔ Few-shot Document Grounding Prompt
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   Modular MAX Serve    │ ➔ Hardware-Accelerated Neural Inference
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  Streamlit Web UI / QA │ ➔ Interactive Dashboard & Q&A
       └────────────────────────┘
```

---

## 📁 Project Structure

```text
AI_OCR_Intelligence/
├── mojoproject.toml        # Modular Magic & MAX project configuration
├── requirements.txt        # Python library dependencies
├── mojo_preprocess.mojo    # High-performance Mojo text normalizer
├── ocr.py                  # Tesseract OCR engine + Mojo preprocessor bridge
├── extractor.py            # Regex & heuristic structured field parser
├── max_inference.py        # Modular MAX Serve client & fallback orchestrator
├── qa.py                   # LangChain prompt builder & Q&A pipeline
├── app.py                  # Streamlit web application
├── generate_sample.py      # Generates a sample invoice image
├── documents/              # Input invoice images (e.g. invoice.png)
├── output/                 # Extracted JSON output (extracted.json)
└── tests/                  # Automated verification test suite
    ├── test_ocr.py
    ├── test_extractor.py
    └── test_qa.py
```

---

## 🚀 Step-by-Step Setup Guide (Windows + Anaconda)

### 1. Create and Activate the Conda Environment
Open **Anaconda Prompt** and run:
```bash
conda create -n aiocr python=3.11 -y
conda activate aiocr
```

### 2. Navigate to the Project Folder & Install Python Packages
```bash
cd "C:\Users\Hema Malini\.gemini\antigravity\scratch\AI_OCR_Intelligence"
pip install -r requirements.txt
```

### 3. Install Tesseract OCR for Windows
1. Download the Windows installer from [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki).
2. Run the installer and install to the default location:
   `C:\Program Files\Tesseract-OCR`
3. Verify in Anaconda Prompt:
   ```bash
   tesseract --version
   ```
   *(The project's `ocr.py` automatically checks `C:\Program Files\Tesseract-OCR\tesseract.exe` and system PATH).*

### 4. Install Modular MAX and Mojo
Modular uses the `magic` package manager to manage Mojo and MAX environments:

1. **Install Magic CLI on Windows (PowerShell):**
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://magic.modular.com | iex"
   ```
2. **Verify Mojo:**
   ```bash
   mojo --version
   ```
3. **Test the Mojo Preprocessor:**
   ```bash
   mojo mojo_preprocess.mojo
   ```
   > **Note:** If Mojo is not yet installed on your system, the system automatically uses the high-fidelity Python fallback preprocessor without interrupting your workflow.

### 5. Launch Modular MAX Serve (Optional for Neural LLM)
Modular MAX Serve hosts local open-weight LLMs (like Llama 3.1, Mistral, or Gemma) with compiled graph acceleration:
```bash
max serve --model modular/llama-3.1-8b-instruct --port 8000
```
When running, MAX exposes an OpenAI-compatible endpoint at `http://localhost:8000/v1`.
*(If MAX Serve is offline, the app seamlessly runs with local context-grounded extraction so you can test immediately).*

---

## 🧪 Running Verification Tests

Run each test individually to verify each stage:

```bash
# Test 1: Test Tesseract OCR and Mojo bridge
python tests/test_ocr.py

# Test 2: Test Structured JSON extraction
python tests/test_extractor.py

# Test 3: Test LangChain + MAX Question Answering
python tests/test_qa.py
```

---

## 🌐 Launch the Streamlit Web Application

```bash
streamlit run app.py
```

### Features in the Web App:
- **System Health Diagnostics:** Live status of Tesseract, Mojo Preprocessor, and MAX Serve in the sidebar.
- **One-Click Demo:** Click **"Load Sample Invoice"** to immediately test without needing to upload an image.
- **Visual Inspection Tabs:**
  - `🖼️ Document & Raw OCR`: Side-by-side view of invoice and raw OCR text.
  - `🔥 Mojo Preprocessing`: Before/after comparison of raw text vs. Mojo-cleaned tokens.
  - `📊 Structured JSON`: Key summary cards (Invoice #, Date, Customer, Total, Line items) + raw JSON viewer.
  - `🤖 MAX + LangChain Q&A`: Ask questions ("What is the total?", "Who is the customer?", "List all items") with one-click buttons or custom text.
