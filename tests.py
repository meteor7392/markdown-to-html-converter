import unittest
from converter import MarkdownConverter

class TestMarkdownConverter(unittest.TestCase):
    def setUp(self):
        self.converter = MarkdownConverter()

    def test_headers(self):
        self.assertEqual(self.converter.convert('# Hello'), '<h1>Hello</h1>')
        self.assertEqual(self.converter.convert('## Subtitle'), '<h2>Subtitle</h2>')

    def test_bold_italic(self):
        self.assertEqual(self.converter.convert('This is **bold**'), '<p>This is <strong>bold</strong></p>')
        self.assertEqual(self.converter.convert('This is *italic*'), '<p>This is <em>italic</em></p>')

    def test_lists(self):
        md = "- Item 1\n- Item 2"
        expected = "<ul>\n<li>Item 1</li>\n<li>Item 2</li>\n</ul>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_paragraphs(self):
        self.assertEqual(self.converter.convert('Plain text'), '<p>Plain text</p>')

if __name__ == '__main__':
    unittest.main()
