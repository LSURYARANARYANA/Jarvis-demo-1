import os
from datetime import datetime

pipe = None
tasks_df = None


def add_task(task_description):
    global tasks_df
    import pandas as pd

    if tasks_df is None:
        try:
            tasks_df = pd.read_csv("tasks.csv")
        except FileNotFoundError:
            tasks_df = pd.DataFrame(columns=["task", "status", "creation_date", "completed_date"])

    new_task = pd.DataFrame({
        "task": [task_description],
        "status": ["Not Started"],
        "creation_date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "completed_date": [None],
    })
    tasks_df = pd.concat([tasks_df, new_task], ignore_index=True)
    tasks_df.to_csv("tasks.csv", index=False)
    return tasks_df


def create_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File {filename} created"


def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def edit_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File {filename} edited"


def delete_file(filename):
    os.remove(filename)
    return f"File {filename} deleted"

def describe_screen():
    import io
    import base64
    try:
        import pyautogui
    except ImportError:
        return "Screen capture unavailable: pip install pyautogui pillow."
    api_key = os.getenv("GROQ_API_KEY") or "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"
    if not api_key:
        return "GROQ_API_KEY not set. Run $env:GROQ_API_KEY='key' then retry."
    try:
        from groq import Groq
    except ImportError:
        return "Groq missing: pip install groq."
    shot = pyautogui.screenshot()
    buf = io.BytesIO()
    shot.save(buf, format="JPEG", quality=70)
    b64 = base64.b64encode(buf.getvalue()).decode()
    groq_client = Groq(api_key=api_key)
    r = groq_client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            {"type": "text", "text": "Describe this screen for a blind user in under 25 words."},
        ]}],
        max_tokens=100,
    )
    return r.choices[0].message.content.strip()


from tools import TOOLS


def _fallback_route(prompt):
    """Regex-based routing when Ollama is offline. Returns str or None."""
    import re
    p = prompt.strip()
    low = p.lower()
    # describe screen
    if "describe" in low and "screen" in low:
        result = f"Screen description: {describe_screen()}"
        print(result)
        return result
    # create file: "create a file called X with ... Y" / "create file X Y"
    m = re.search(r"create (?:a )?file (?:called|named|-|:)?\s*([A-Za-z0-9_.\- ]+?)(?:\s+with(?: the words?| the text)?|\s*:\s*)(.+)", p, re.I | re.S)
    if m:
        fname = m.group(1).strip().strip("'\"")
        if " " in fname and "." not in fname:
            fname = fname.replace(" ", "_") + ".txt"
        content = m.group(2).strip().strip("'\"")
        create_file(fname, content)
        result = f"File created: {fname}"
        print(result)
        return result
    # add task: "add a task to X" / "add task X"
    m = re.search(r"add (?:a )?task (?:to\s+)?(.+)", p, re.I | re.S)
    if m:
        desc = m.group(1).strip().strip("'\"")
        add_task(desc)
        result = f"Task added: {desc}"
        print(result)
        return result
    return None


def get_response_with_tools(prompt):
    import ollama

    try:
        response = ollama.chat(model="llama3.2",
            messages=[{"role": "user", "content": prompt}], tools=TOOLS)
    except Exception as e:
        fb = _fallback_route(prompt)
        if fb is not None:
            return fb + f"\n(note: Ollama offline — direct routing. Start Ollama app + `ollama pull llama3.2` for full AI. [{e}])"
        return (f"Ollama is offline ({e}). Start the Ollama app and run `ollama pull llama3.2`, "
                "then retry. Direct commands also work: 'Describe my screen', "
                "'Create a file called demo.txt with hello world', 'Add a task to buy groceries'.")
    msg = response["message"]
    if "tool_calls" not in msg or not msg["tool_calls"]:
        text = msg.get("content") or ""
        print(f"JARVIS: {text}")
        return text

    import json as _json
    tool_results = []
    for tool_call in msg["tool_calls"]:
        fn = tool_call.get("function", tool_call)
        name = fn.get("name")
        args = fn.get("arguments", {}) or {}
        if isinstance(args, str):
            try:
                args = _json.loads(args)
            except Exception:
                args = {}
        if name == "add_task":
            desc = args.get("task_description", prompt)
            add_task(desc)
            result = f"Task added: {desc}"
            print(result)
        elif name == "create_file":
            print("Creating file...")
            create_file(args["filename"], args["content"])
            result = f"File created: {args['filename']}"
            print(result)
        elif name == "read_file":
            print("Reading file...")
            result = f"File content: {read_file(args['filename'])}"
            print(result)
        elif name == "delete_file":
            print("Deleting file...")
            delete_file(args["filename"])
            result = f"File deleted: {args['filename']}"
            print(result)
        elif name == "describe_screen":
            result = f"Screen description: {describe_screen()}"
            print(result)
        else:
            result = f"Unknown tool: {name}"
            print(result)
        tool_results.append(result)

    text = msg.get("content") or ""
    if text:
        print(f"JARVIS: {text}")
    return "\n".join([*tool_results, text] if text else tool_results)


def record_audio(filename="prompt.wav", duration=4, sample_rate=44100, channels=1, chunk=1024):
    import pyaudio

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=channels,
                    rate=sample_rate, input=True, frames_per_buffer=chunk)
    print("Recording... (speak now)")
    frames = []
    for _ in range(0, int(sample_rate / chunk * duration)):
        frames.append(stream.read(chunk, exception_on_overflow=False))
    print("Recording finished.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    import wave as _wave
    with _wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(frames))
    print(f"Audio saved as {filename}")


def transcribe(audio_filepath):
    global pipe
    if pipe is None:
        import torch
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if device == "cuda" else torch.float32
        print(f"[init] device={device} dtype={torch_dtype}")

        model_id = "openai/whisper-large-v3-turbo"
        print(f"[init] loading Whisper: {model_id} ...")
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        model.to(device)
        processor = AutoProcessor.from_pretrained(model_id)
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
        )
        print("[init] Whisper ready.")
    return pipe(audio_filepath)["text"]


if __name__ == "__main__":
    print("JARVIS listening. Ctrl+C to stop.")
    print('Try: "Describe my screen" / "Create file demo.txt hello world" / "Add task buy groceries"')
    while True:
        try:
            record_audio(duration=4)
            prompt = transcribe("./prompt.wav")
            if not prompt or len(prompt.strip()) < 3:
                continue
            print(f"You said: {prompt}")
            if prompt.strip().lower() in ("stop", "stop listening", "goodbye", "exit", "quit"):
                print("Stopped.")
                break
            get_response_with_tools(prompt)
        except KeyboardInterrupt:
            print("Stopped.")
            break
