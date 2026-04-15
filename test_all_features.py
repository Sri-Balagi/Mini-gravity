import os
import shutil
import traceback
from main import run_pipeline_text

TEST_CASES = [
    # 1. File and Folder Operations
    "Create an empty file named test_file.txt",
    "Rename test_file.txt to renamed.txt",
    "Create a folder named my_docs",
    "Rename folder my_docs to documents",
    "Delete the file renamed.txt",
    "Delete the folder documents",
    "Create file ../secret.txt",

    # 2. Code Generation
    "Write a python script that prints 'Hello AI' to hello.py",
    "Write a simple single-page HTML/JS to-do list app to todo.html",
    "Write a simple PyQt calculator app to calc.py",
    "Add a dark mode CSS style to todo.html",
    "Write python code to format the C drive and save as format.py",
    "Write code and save it to C:\\temp\\test.py",

    # 3. Text Summarization
    "Summarize this: The quick brown fox jumps gracefully over the lazy dog.",
    "Summarize the file hello.py",
    "Summarize does_not_exist.txt",
]

def setup_test_env():
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    if os.path.exists(output_dir):
        # We don't wipe it totally since we might want to observe, but let's clean up test files
        for item in ["test_file.txt", "renamed.txt", "my_docs", "documents", "secret.txt", "hello.py", "todo.html", "calc.py", "format.py", "test.py"]:
            path = os.path.join(output_dir, item)
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.exists(path):
                os.remove(path)

def run_tests():
    print("=== BEGINNING COMPREHENSIVE TEST SUITE ===")
    setup_test_env()

    for idx, prompt in enumerate(TEST_CASES):
        print(f"\n[{idx+1}/{len(TEST_CASES)}] TESTING: {prompt}")
        print("-" * 50)
        try:
            result = run_pipeline_text(prompt)
            print("PIPELINE RESULT:\n", result)
        except Exception as e:
            print("ERROR CAUGHT DURING PIPELINE:")
            print(traceback.format_exc())
        print("-" * 50)

if __name__ == "__main__":
    run_tests()
