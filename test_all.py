import os
import sys

from tools.intent import classify_intent
from tools.executor import execute

def run_test(name, prompt):
    print(f"\n{'='*50}\nTEST: {name}\nPROMPT: {prompt}")
    try:
        intents = classify_intent(prompt)
        print(f"-> CLASSIFIED INTENT(S): {intents}")
        for i, intent in enumerate(intents):
            print(f"   Executing task {i+1} ({intent.get('intent')})...")
            result = execute(intent)
            if len(str(result)) > 200:
                print(f"-> RESULT: {str(result)[:200]}... (truncated)")
            else:
                print(f"-> RESULT: {result}")
    except Exception as e:
        print(f"-> ERROR: {e}")

if __name__ == "__main__":
    tests = [
        ("Create File", "Just create an empty file called test_mock.txt"),
        ("Write Code (Algorithm)", "Write a python script that prints the fibonacci sequence up to 10 and save it as fib.py"),
        ("Summarize Text", "Summarize this paragraph: Artificial Intelligence is a branch of computer science focused on building intelligent machines capable of performing tasks that typically require human intelligence."),
        ("General Chat", "What is the capital of France?"),
        ("Compound Command", "Create an empty file called blank.txt and write a python script to calculate the area of a circle saved as area.py and tell me a short joke.")
    ]
    
    for t in tests:
        run_test(t[0], t[1])
