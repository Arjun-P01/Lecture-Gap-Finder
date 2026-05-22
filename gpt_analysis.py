from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import json
import os

load_dotenv()
_api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=_api_key)

@st.cache_data
def get_gap_analysis(missing_topics: list[str]) -> list[dict]:
    prompt = f"""
    You are a helpful study assistant.

The following topics were in the course syllabus but were NOT covered in the lecture:
{missing_topics}

For each topic, respond in JSON as a list of objects with exactly these fields:
- "topic": the topic name
- "explanation": explain the topic in 2 sentences
- "importance": how important it is for the exam, either "low", "mid", or "high"

Respond with only the JSON array, no extra text.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    text = text[text.index("[") : text.rindex("]") + 1]
    return json.loads(text)
