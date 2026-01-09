import asyncio
import json
from core.text_utils import chunk_text, load_text
from core.llm import LLMClient

class EntityExtractor:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def _extract_json(self, content: str):
        """
        Extracts JSON from a string that might contain markdown code blocks or other text.
        """
        try:
            # Try parsing directly first
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try to find markdown code blocks
        import re
        match = re.search(r'```(?:json)?\s*(.*?)```', content, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Try to find the first { and last }
        start = content.find('{')
        end = content.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            json_str = content[start:end+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
                
        # If all else fails, raise the original error or a new one
        raise ValueError("Could not extract valid JSON from response")

    async def process_single_chunk(self, chunk_id, chunk_text, prompt: str):
        try:
            user_content = f"Chunk {chunk_id}: {chunk_text}"
            content = await self.llm_client.generate(prompt=user_content, system_message=prompt)
            
            data = self._extract_json(content)
            
            return {
                "chunk_id": chunk_id,
                "status": "success",
                "data": data
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
        chunks = chunk_text(text, chunk_size=1200, overlap=100)

        tasks = []
        for i, chunk in enumerate(chunks):
            task = self.process_single_chunk(i, chunk, prompt)
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        
        return results
