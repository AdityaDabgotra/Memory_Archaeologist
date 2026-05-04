from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from dotenv import load_dotenv
import json
import time
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
    temperature=0
)


def extract_entities(doc: Document, retries: int = 3) -> dict:
    prompt = f"""Analyze this personal document excerpt and extract:
1. Key concepts/ideas/topics (max 4, short phrases)
2. People mentioned by name (first names or full names only)

Document (written on {doc.metadata.get('date', 'unknown date')}):
\"\"\"{doc.page_content}\"\"\"

Respond ONLY with valid JSON, no explanation, no markdown:
{{
  "concepts": ["concept1", "concept2"],
  "people": ["name1", "name2"]
}}

Rules:
- Concepts should be meaningful ideas, not generic words
- Only include real people's names, not pronouns
- If none found, return empty lists
"""

    for attempt in range(retries):
        try:
            response = llm.invoke(prompt)
            text = response.content.strip()

            
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()

            result = json.loads(text)

            # Validate structure
            if "concepts" not in result:
                result["concepts"] = []
            if "people" not in result:
                result["people"] = []

            print(f"    Concepts: {result['concepts']}")
            print(f"    People:   {result['people']}")
            return result

        except json.JSONDecodeError as e:
            print(f"    SON parse error (attempt {attempt+1}): {e}")
            print(f"    Raw response: {text[:200]}")
            time.sleep(1)

        except Exception as e:
            print(f"    Extraction error (attempt {attempt+1}): {e}")
            time.sleep(2)

    print("    All retries failed, returning empty entities")
    return {"concepts": [], "people": []}