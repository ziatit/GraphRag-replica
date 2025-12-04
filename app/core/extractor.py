import asyncio
import json
from core.text_utils import chunk_text, load_text
from core.llm import LLMClient

class EntityExtractor:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def process_single_chunk(self, chunk_id, chunk_text, prompt: str):
        try:
            user_content = f"Chunk {chunk_id}: {chunk_text}"
            content = await self.llm_client.generate(prompt=user_content, system_message=prompt)
            
            return {
                "chunk_id": chunk_id,
                "status": "success",
                "data": json.loads(content)
            }
        except Exception as e:
            print(f"Błąd przy chunku {chunk_id}: {e}")
            if 'content' in locals():
                print(f"Raw content: {content}")
            return {
                "chunk_id": chunk_id,
                "status": "error",
                "error": str(e)
            }

    async def process_chunks(self, text_path: str, prompt: str):
        text = load_text(text_path)
        chunks = chunk_text(text, chunk_size=2400, overlap=100)

        tasks = []
        for i, chunk in enumerate(chunks):
            task = self.process_single_chunk(i, chunk, prompt)
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        
        return results
