"""Quick text-mode test - no mic, no Whisper load. Tests file + task + vision."""
import os
import pandas as pd
from datetime import datetime
from tools import TOOLS, describe_screen

print("TOOLS:", [t["function"]["name"] for t in TOOLS])

# 1. File create/read directly
with open("demo.txt", "w", encoding="utf-8") as f:
    f.write("hello world")
print("demo.txt ->", open("demo.txt", encoding="utf-8").read())

# 2. Task add directly
try:
    df = pd.read_csv("tasks.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=["task", "status", "creation_date", "completed_date"])
new = pd.DataFrame({"task": ["buy groceries"], "status": ["Not Started"],
    "creation_date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    "completed_date": [None]})
df = pd.concat([df, new], ignore_index=True)
df.to_csv("tasks.csv", index=False)
print(pd.read_csv("tasks.csv").tail(2).to_string())

# 3. Vision tool (needs GROQ_API_KEY)
if os.getenv("GROQ_API_KEY"):
    print("Screen:", describe_screen())
else:
    print("SKIP vision: $env:GROQ_API_KEY not set (console.groq.com -> Keys, then $env:GROQ_API_KEY='gsk_...')")

# 4. LLM routing (needs Ollama APP running + llama3.2 pulled)
try:
    import ollama
    r = ollama.chat(model="llama3.2",
        messages=[{"role": "user", "content": "Create a file called notes.txt with the text meeting at 3pm"}],
        tools=TOOLS)
    msg = r["message"]
    print("LLM tool_calls:", [c["function"]["name"] for c in msg.get("tool_calls", [])] or "(none - conversational)")
    print("LLM content:", (msg.get("content") or "")[:200])
except Exception as e:
    print(f"LLM SKIP: {e}")
    print("FIX: install Ollama app from ollama.com, open it, then run: ollama pull llama3.2")
