from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from dotenv import load_dotenv
import json
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
    temperature=0
)

def extract_entities(doc: Document) -> dict:
    prompt = f"""Analyze this personal document excerpt and extract:
            1. Key concepts/ideas/topics (max 4, short phrases)
            2. People mentioned by name (first names or full names only)

            Document (written on {doc.metadata.get('date', 'unknown date')}):
            \"\"\"{doc.page_content}\"\"\"

            Respond ONLY with valid JSON, no explanation:
            {{
            "concepts": ["concept1", "concept2"],
            "people": ["name1", "name2"]
            }}

            Rules:
            - Concepts should be meaningful ideas, not generic words
            - Only include real people's names, not pronouns
            - If none found, return empty lists
            """
    try:
        response = llm.invoke(prompt)
        text = response.content.strip()

        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Entity extraction failed: {e}")
        return {"concepts": [], "people": []}