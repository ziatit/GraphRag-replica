import asyncio
from core.llm import LLMClient
from core.extractor import EntityExtractor
from prompts.extract_entities import ENTITIES_EXTRACTION_PROMPT_JSON
import json
import os

async def main():
    llm = LLMClient()
    extractor = EntityExtractor(llm)
    results = await extractor.process_chunks("/home/ziatit/Codes/ms_graphrag_replica/data/testin.txt", ENTITIES_EXTRACTION_PROMPT_JSON)

    for result in results:
        if result["status"] == "success":
            print(f"Chunk {result['chunk_id']}: {result['data']}")
        else:
            print(f"Chunk {result['chunk_id']} failed: {result['error']}")

    # Save results to output directory
    output_path = os.path.join("output", "extracted_entities.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())