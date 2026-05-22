from dotenv import load_dotenv
from openai import OpenAI
import json
import os

load_dotenv(override=True)
client = OpenAI()
CACHE_FILE = "cache.json"

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

    

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    else:
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
        text = response.choices[0].message.content
        text = text[text.index("[") : text.rindex("]") + 1]
        result = json.loads(text)
        with open(CACHE_FILE, "w") as f:
            json.dump(result, f)
        return result

if __name__ == "__main__":
    test_topics = ["loss functions", "neural networks", "gradient descent"]
    result = get_gap_analysis(test_topics)
    for item in result:
        print(item)