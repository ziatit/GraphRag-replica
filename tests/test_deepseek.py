import sys
import os
import asyncio
from dotenv import load_dotenv

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.llm import LLMClient

load_dotenv()

from app.prompts.extract_entities import ENTITIES_EXTRACTION_PROMPT_JSON

async def test_generation():
    os.environ["LLM_MODEL"] = "deepseek-reasoner"
    print(f"LLM_MODEL: {os.getenv('LLM_MODEL')}")
    llm = LLMClient()
    
    prompt = ENTITIES_EXTRACTION_PROMPT_JSON
    
    text = """
    In the year 1878 I took my degree of Doctor of Medicine of the
    University of London, and proceeded to Netley to go through the course
    prescribed for surgeons in the army. Having completed my studies there,
    I was duly attached to the Fifth Northumberland Fusiliers as Assistant
    Surgeon. The regiment was stationed in India at the time, and before I
    could join it, the second Afghan war had broken out. On landing at
    Bombay, I learned that my corps had advanced through the passes, and
    was already deep in the enemy’s country. I followed, however, with many
    other officers who were in the same situation as myself, and succeeded
    in reaching Candahar in safety, where I found my regiment, and at once
    entered upon my new duties.
    """
    
    print("--- Test 1: System Message + User Message ---")
    try:
        user_content = f"Chunk 0: {text}"
        response = await llm.generate(prompt=user_content, system_message=prompt)
        print(f"Response start:\n{response[:500]}...\n")
    except Exception as e:
        print(f"Error: {e}")

    print("--- Test 2: User Message Only (Combined) ---")
    try:
        combined_prompt = f"{prompt}\n\nChunk 0: {text}"
        response = await llm.generate(prompt=combined_prompt, system_message=None)
        print(f"Response start:\n{response[:500]}...\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_generation())
