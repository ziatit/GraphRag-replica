import sys
import os
import json
import unittest

# Add the project root and app directory to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from app.core.extractor import EntityExtractor
from app.core.llm import LLMClient

class MockLLMClient(LLMClient):
    def __init__(self):
        pass

class TestJsonExtraction(unittest.TestCase):
    def setUp(self):
        self.extractor = EntityExtractor(MockLLMClient())

    def test_clean_json(self):
        content = '{"key": "value"}'
        result = self.extractor._extract_json(content)
        self.assertEqual(result, {"key": "value"})

    def test_markdown_json(self):
        content = '```json\n{"key": "value"}\n```'
        result = self.extractor._extract_json(content)
        self.assertEqual(result, {"key": "value"})

    def test_markdown_no_lang(self):
        content = '```\n{"key": "value"}\n```'
        result = self.extractor._extract_json(content)
        self.assertEqual(result, {"key": "value"})

    def test_json_with_noise(self):
        content = 'Here is the JSON:\n{"key": "value"}\nHope this helps.'
        result = self.extractor._extract_json(content)
        self.assertEqual(result, {"key": "value"})

    def test_markdown_with_noise(self):
        content = 'Sure, here is the output:\n```json\n{"key": "value"}\n```\nDone.'
        result = self.extractor._extract_json(content)
        self.assertEqual(result, {"key": "value"})

if __name__ == '__main__':
    unittest.main()
