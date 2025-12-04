import tiktoken

def chunk_text(text: str, chunk_size: int, overlap: int):
    """
    Splits the input text into chunks of tokens using the cl100k_base encoding (used by GPT-4/3.5).
    
    Args:
        text (str): The input text to be chunked.
        chunk_size (int): The maximum number of tokens in each chunk.
        overlap (int): The number of overlapping tokens between consecutive chunks.
        
    Yields:
        str: A chunk of text decoded from tokens.
    """
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    
    for i in range(0, len(tokens), chunk_size - overlap):
        yield encoder.decode(tokens[i:i + chunk_size])

if __name__ == "__main__":
    text = 'word ' * 5000
    for chunk in chunk_text(text, chunk_size=2400, overlap=100):
        print(chunk)

def load_text(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()