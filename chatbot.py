from groq import Groq
from tavily import TavilyClient
from memory import load_memory, save_memory, remember 
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def get_ai_response(prompt, pdf_text=""):
    try:
        if prompt is None:
            return "Please type or speak a message." 
        memory = load_memory() 
        if "my name is" in prompt.lower():
            name = prompt.split("my name is")[-1].strip()

            memory["name"] = name
            save_memory(memory)

            return f"Nice to meet you, {name}! I will remember your name."

        if "what is my name" in prompt.lower():

            if "name" in memory:
                return f"Your name is {memory['name']}."

            return "I don't know your name yet. Tell me by saying 'My name is...'"
        search = tavily.search(
            query=prompt,
            search_depth="advanced",
            max_results=5,
            include_answer=True
        )

        web_info = ""
        if search.get("results"):
            for result in search["results"]:
                web_info += (
                    f"Title: {result.get('title','')}\n"
                    f"Content: {result.get('content','')}\n"
                    f"URL: {result.get('url','')}\n\n"
                )

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": f"""
You are Kabitix AI, a smart, friendly and helpful AI assistant.

Rules:
- Use the uploaded PDF whenever possible.
- If the PDF doesn't contain the answer, use the Tavily search results.
- If neither helps, answer using your own knowledge.
- Keep your answers short, clear and helpful.

Live Search Results:

{web_info}

PDF Content:

{pdf_text}
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {e}"


def speech_to_text(audio_file):
    try:
        with open(audio_file, "rb") as file:
            transcript = client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3"
            )

        return transcript.text

    except Exception as e:
        return f"Error: {e}"
