from groq import Groq
from tavily import TavilyClient
from memory import load_memory, save_memory
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Keywords that DON'T need web search
NO_SEARCH_WORDS = ["hi", "hello", "my name", "who are you", "thank", "bye", "what is my name"]

def should_search(prompt: str):
    p = prompt.lower()
    # Don't search for greetings / memory
    for w in NO_SEARCH_WORDS:
        if w in p:
            return False
    # Only search if question needs fresh info
    if any(x in p for x in ["today", "news", "latest", "2026", "price", "who is", "what is", "weather", "score"]):
        return True
    return len(p.split()) > 6 # search only for longer queries

def get_ai_response(prompt, pdf_text=""):
    try:
        if not prompt or not prompt.strip():
            return "Please type or speak a message."

        memory = load_memory() or {}
        pl = prompt.lower()

        # --- MEMORY ---
        if "my name is" in pl:
            name = prompt.split("my name is")[-1].strip().split("\n")[0][:50]
            memory["name"] = name
            save_memory(memory)
            return f"Nice to meet you, {name}! I'll remember you from now on. 🤖"

        if "what is my name" in pl:
            return f"Your name is {memory.get('name')}!" if memory.get("name") else "I don't know your name yet. Tell me 'My name is...'"

        web_info = ""
        # --- SMART SEARCH (only when needed) ---
        if should_search(prompt):
            try:
                search = tavily.search(
                    query=prompt,
                    search_depth="basic", # basic = faster + cheaper
                    max_results=3, # 3 not 5 = save tokens
                    include_answer=True
                )
                if search.get("results"):
                    for r in search["results"][:2]: # only top 2
                        web_info += f"- {r.get('content','')[:400]}\n"
            except Exception:
                web_info = "" # if tavily fails, continue anyway

        # --- TRIM PDF ---
        pdf_snippet = pdf_text[:3000] if pdf_text else "No document uploaded."

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # FASTEST Groq model
            temperature=0.7,
            max_tokens=1024,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are Kabitix AI, built by KTIX Studio. You are smart, friendly, helpful.

Rules:
1. If user uploaded a document, use it first to answer.
2. Use Web Search results if provided.
3. Keep answers short, clear, with emojis.
4. If you don't know, say honestly.

Web Search:
{web_info}

Document:
{pdf_snippet}
"""
                },
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Kabitix error: {str(e)[:200]}. Check GROQ_API_KEY in Render."

def speech_to_text(audio_file):
    try:
        with open(audio_file, "rb") as file:
            transcript = client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3"
            )
        return transcript.text
    except Exception as e:
        print(f"STT Error: {e}")
        return None # Return None, not error string!
