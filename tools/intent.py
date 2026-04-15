import requests
import json
import re

def classify_intent(text:str, context_file:str=None) -> list:
    context_hint = ""
    if context_file:
        context_hint = f"\n[CONTEXT]: The user currently has a file named '{context_file}' uploaded and active. If the user refers to 'the file', 'this document', 'it', or provides a name that is phonetically similar to '{context_file}', you MUST use '{context_file}' as the filename."

    prompt = f"""
You are a STRICT intent classifier. Your job is to read a user request and output a JSON array.
{context_hint}

Supported intents:
1. create_file   - when the user asks to create an empty file or a folder
2. rename_file   - when the user asks to rename a file or folder (provide "old_name" and "new_name" in details)
3. delete_file   - when the user asks to delete or remove a file or folder
4. modify_file   - when the user asks to edit or modify an existing file
5. repair_file   - when the user asks to fix or repair broken code in a file
6. move_file     - when the user asks to move a file or folder (provide "filename" and "destination" in details)
7. write_code    - when the user asks to build, generate, implement, or write ANY program, script, app, function, or code
8. summarize     - when the user asks to summarize text or a file
9. general_chat  - everything else (questions, greetings, explanations)

CRITICAL RULES:
- If a context file is provided and the user says 'Summarize this' or 'Delete the document', use the context file name for the 'filename' field.
- A single user request = a SINGLE task. Do NOT split one request into multiple tasks.
- If user asks for ANY app or program → ALWAYS choose "write_code".
- Return ONLY a valid JSON array. No markdown fences, no trailing commas, no comments.

Output format:
[{{"intent": "<intent>", "details": {{"filename": "<filename>", "instruction": "<full instruction from user>"}}}}]

User input:
"{text}"
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-coder:6.7B",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        raw_output = response.json().get("response", "").strip()
    except Exception as e:
        print(f"Ollama API Error: {e}")
        raw_output = ""

    print("RAW OUTPUT:", raw_output)

    # ── pre-sanitise BEFORE extracting JSON ────────────────────────────────
    # Strip ANSI/VT100 escape sequences (Ollama progress outputs)
    raw_output = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw_output)
    raw_output = re.sub(r'\x1b[>=?]', '', raw_output)

    # Strip markdown fences (e.g. ```json ... ```)
    # Collapse ALL literal newlines → space  (LLM word-wraps inside string
    # values, which is illegal JSON and causes json.loads to crash)
    raw_output = raw_output.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
    # Strip trailing commas before ] or }
    raw_output = re.sub(r',\s*([\]\}])', r'\1', raw_output)
    # Collapse multiple spaces
    raw_output = re.sub(r'  +', ' ', raw_output)
    # ───────────────────────────────────────────────────────────────────────

    match = re.search(r"\[.*\]", raw_output, re.DOTALL)
    if not match:
        return [{
            "intent": "general_chat",
            "details": {"text": text}
        }]
    json_str = match.group()

    # ── sanitise common LLM JSON mistakes ──────────────────────────────────
    # Replace ALL control characters (anything below 0x20 except the allowed
    # JSON structural escapes \t \n \r) with a space so json.loads never sees
    # illegal control characters inside string values.
    json_str = re.sub(r'[\x00-\x1f]', ' ', json_str)
    # Re-collapse trailing commas and multiple spaces
    json_str = re.sub(r',\s*([\]\}])', r'\1', json_str)
    json_str = re.sub(r'  +', ' ', json_str)
    # ───────────────────────────────────────────────────────────────────────


    try:
        parsed = json.loads(json_str)
        if isinstance(parsed, dict):
            parsed = [parsed]
        
        # Post-validation: merge spurious split tasks back into one write_code
        code_tasks = [t for t in parsed if t.get("intent") == "write_code"]
        other_tasks = [t for t in parsed if t.get("intent") != "write_code"]
        if len(code_tasks) > 1:
            merged_instruction = " ".join(
                t.get("details", {}).get("instruction", "") for t in code_tasks
            )
            first = code_tasks[0]
            first["details"]["instruction"] = merged_instruction.strip()
            parsed = [first] + other_tasks
        return parsed
    except json.JSONDecodeError as e:
        print(f"JSON parse failed ({e}), attempting regex fallback...")
        
        # Fallback to pure regex to salvage corrupted JSON
        intent_match = re.search(r'"intent"\s*:\s*"([^"]+)"', raw_output)
        if intent_match:
            intent = intent_match.group(1)
            details = {}
            
            filename_match = re.search(r'"filename"\s*:\s*"([^"]+)"', raw_output)
            instruction_match = re.search(r'"instruction"\s*:\s*"([^"]+)"', raw_output)
            old_name_match = re.search(r'"old_name"\s*:\s*"([^"]+)"', raw_output)
            new_name_match = re.search(r'"new_name"\s*:\s*"([^"]+)"', raw_output)
            dest_match = re.search(r'"destination"\s*:\s*"([^"]+)"', raw_output)
            
            if filename_match: details["filename"] = filename_match.group(1)
            if instruction_match: 
                details["instruction"] = instruction_match.group(1)
            else: 
                details["instruction"] = text
                
            if old_name_match: details["old_name"] = old_name_match.group(1)
            if new_name_match: details["new_name"] = new_name_match.group(1)
            if dest_match: details["destination"] = dest_match.group(1)
            
            return [{"intent": intent, "details": details}]
            
        print("Regex fallback failed, defaulting to general_chat")
        return [{"intent": "general_chat", "details": {"text": text}}]
    