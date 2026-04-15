# Mini Gravity

Mini Gravity is a locally-hosted Voice AI Agent designed to bridge the gap between spoken intent and file-based actions. The system leverages local Large Language Models (LLMs) to interpret natural language commands and execute file operations, code generation, and text processing safely within a designated environment.

## Architecture Overview

The system operates as a sequential pipeline consisting of three primary layers:

1.  **Speech-to-Text (STT) Layer**: Converts incoming audio streams or files into text strings.
2.  **Intent Classification Layer**: Uses a local instance of `deepseek-coder:6.7B` to parse the text into a structured JSON array. This layer identifies the specific intent (e.g., `create_file`, `write_code`, `summarize`) and extracts associated metadata (filenames, instructions, destinations).
3.  **Execution Layer**: A logic engine that maps validated intents to system-level actions including file I/O, subprocess execution for code generation, and document parsing across multiple formats (PDF, DOCX, XLSX).

## Hardware and LLM Workarounds

To ensure reliability when running on local consumer hardware and smaller models, several robust workarounds have been implemented:

-   **Resilient JSON Fallback**: Smaller models (6.7B parameters) frequently fail to produce perfectly formatted JSON. The system includes a Regular Expression-based fallback parser that can reconstruct the intent and metadata from fragmented or malformed LLM outputs.
-   **Safe Execution Sandbox**: All file-modifying actions are strictly bound to the `output/` directory and use `os.path.basename` to prevent directory traversal or accidental system file overwrites.
-   **Terminal Artifact Sanitization**: The system automatically strips ANSI/VT100 escape sequences emitted by Ollama's progress displays, ensuring that generated code remains valid and runnable.

## Prerequisites

- **Python 3.10 or higher**
- **Ollama**: Required for local model execution.
- **LLM Models**:
    - `deepseek-coder:6.7B`: Optimized for intent interpretation and code generation.
    - `qwen2.5:7b`: Utilized for text summarization and general dialogue.

## Installation and Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Sri-Balagi/Mini-gravity.git
    cd Mini-gravity
    ```

2.  **Initialize Virtual Environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Required Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download Local Models**:
    ```bash
    ollama pull deepseek-coder:6.7B
    ollama pull qwen2.5:7b
    ```

## Usage

To start the graphical user interface, run the following command:

```bash
streamlit run ui/app.py
```

Access the interface through your web browser (typically at `http://localhost:8501`).

## Project Structure

- `main.py`: CLI entry point for testing the text-based pipeline.
- `ui/app.py`: Streamlit-based user interface.
- `tools/intent.py`: Intent classification logic with regex fallback support.
- `tools/executor.py`: Core logic for file operations and document parsing.
- `output/`: Secure target directory for all generated content.
