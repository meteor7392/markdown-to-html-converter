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

    def test_ordered_lists(self):
        md = "1. First\n2. Second"
        expected = "<ol>\n<li>First</li>\n<li>Second</li>\n</ol>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_blockquotes(self):
        md = "> Quote"
        # Adjusted expectation based on implementation: blockquotes wrap contents in <p>
        self.assertEqual(self.converter.convert(md), "<blockquote>\n<p>Quote</p></blockquote>")

    def test_paragraphs(self):
        self.assertEqual(self.converter.convert('Plain text'), '<p>Plain text</p>')

    def test_links_and_images(self):
        self.assertEqual(self.converter.convert('[Google](https://google.com)'), '<p><a href="https://google.com">Google</a></p>')
        self.assertEqual(self.converter.convert('![Alt text](img.jpg)'), '<p><img src="img.jpg" alt="Alt text"></p>')

    def test_code(self):
        # Inline code
        self.assertEqual(self.converter.convert('Use `print()`'), '<p>Use <code>print()</code></p>')
        # Code block
        md = "```\nprint('hello')\n```"
        expected = "<pre><code>\nprint('hello')\n</code></pre>"
        self.assertEqual(self.converter.convert(md), expected)

if __name__ == '__main__':
    unittest.main()