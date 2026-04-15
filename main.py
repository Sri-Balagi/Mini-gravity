from tools.stt import transcribe_audio
from tools.intent import classify_intent
from tools.executor import execute

def run_pipeline_audio(file_path:str,uploaded_file=None):
    text=transcribe_audio(file_path)
    print("Transcription:",text)

    intents=classify_intent(text)
    if isinstance(intents, dict):
        intents = [intents]
    print("Intents:",intents)

    results = []
    for intent_data in intents:
        if intent_data["intent"]=="summarize" and uploaded_file:
            if "details" not in intent_data:
                intent_data["details"] = {}
            intent_data["details"]["file_path"]=uploaded_file
        res=execute(intent_data)
        results.append(res)
        print("Result:",res)

    return {
        "text":text,
        "intent":intents,
        "result":results
    }

def run_pipeline_text(user_text: str):
    intents=classify_intent(user_text)
    if isinstance(intents, dict):
        intents = [intents]
    print("Intents:",intents)

    results = []
    for intent_data in intents:
        res=execute(intent_data)
        results.append(res)
        print("Result:",res)

    return{
        "text":user_text,
        "intent":intents,
        "result":results
    }



if __name__=="__main__":
    run_pipeline_text("create a python file named demo.py")

    #run_pipeline_audio("input/sample.wav")

    