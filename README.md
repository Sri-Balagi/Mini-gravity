# Mini Gravity

Mini Gravity is a powerful, locally-hosted Voice AI Agent designed to bridge the gap between spoken intent and file-based actions. It uses local LLMs to interpret user commands and execute various tasks safely on your machine.

## 🚀 Features

- **Voice & Text Command Input**: Interact via voice recordings, uploaded audio files, or direct text.
- **Intelligent File Operations**: Create, rename, delete, and move files or folders securely within a dedicated `output/` directory.
- **Multi-Framework Code Generation**: Generate complete, functional code in Python, HTML/JS, PyQt, and more based on natural language requests.
- **Robust Text Processing**: Summarize contents of text files, PDFs, Word documents, and Excel spreadsheets.
- **Safety First**: All file-modifying operations are restricted to the `output/` folder with built-in protection against directory traversal.
- **Resilient Pipeline**: Includes a regex-based fallback parser to handle malformed outputs from local LLMs.

## 📋 Prerequisites

- **Python 3.10+**
- **Ollama**: Required for running the local LLMs.
- **Models**:
  - `deepseek-coder:6.7B` (Used for intent classification and code generation)
  - `qwen2.5:7b` (Used for summarization and general chat)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sri-Balagi/Mini-gravity.git
   cd Mini-gravity
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Pull the required Ollama models**:
   ```bash
   ollama pull deepseek-coder:6.7B
   ollama pull qwen2.5:7b
   ```

## 🏃 Usage

Start the Streamlit interface:

```bash
streamlit run ui/app.py
```

Open your browser to the local URL provided by Streamlit (usually `http://localhost:8501`) to start interacting with the agent.

## 📁 Project Structure

- `main.py`: Entry point for text-based pipeline testing.
- `ui/app.py`: Streamlit-based graphical user interface.
- `tools/`:
  - `intent.py`: Intent classification logic with a resilient fallback parser.
  - `executor.py`: Logic for file operations, code generation, and summarization.
  - `stt.py`: Speech-to-text integration.
- `output/`: Dedicated folder for all generated files and folders (created at runtime).

---
Created with ❤️ by Sri Balagi
