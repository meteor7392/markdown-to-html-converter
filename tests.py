import unittest
from converter import MarkdownConverter

class TestMarkdownConverter(unittest.TestCase):
    def setUp(self):
        self.converter = MarkdownConverter()

    def test_headers(self):
        self.assertEqual(self.converter.convert('# Hello'), '<h1>Hello</h1>')
        self.assertEqual(self.converter.convert('## Subtitle'), '<h2>Subtitle</h2>')
        self.assertEqual(self.converter.convert('### Section'), '<h3>Section</h3>')
        self.assertEqual(self.converter.convert('#### Sub'), '<h4>Sub</h4>')
        self.assertEqual(self.converter.convert('##### Sub'), '<h5>Sub</h5>')
        self.assertEqual(self.converter.convert('###### Sub'), '<h6>Sub</h6>')

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
        self.assertEqual(self.converter.convert(md), "<blockquote>\n<p>Quote</p></blockquote>")

    def test_paragraphs(self):
        self.assertEqual(self.converter.convert('Plain text'), '<p>Plain text</p>')

    def test_links_and_images(self):
        self.assertEqual(self.converter.convert('[Google](https://google.com)'), '<p><a href="https://google.com">Google</a></p>')
        self.assertEqual(self.converter.convert('![Alt text](img.jpg)'), '<p><img src="img.jpg" alt="Alt text"></p>')

    def test_code(self):
        # Inline code
        self.assertEqual(self.converter.convert('Use `print()`'), '<p>Use <code>print()</code></p>')
        # Empty inline code
        self.assertEqual(self.converter.convert('Empty `` code'), '<p>Empty <code></code> code</p>')
        # Code block
        md = "```\nprint('hello')\n```"
        self.assertEqual(self.converter.convert(md), "<pre><code>print('hello')</code></pre>")

    def test_horizontal_rule(self):
        self.assertEqual(self.converter.convert('---'), '<hr>')
        self.assertEqual(self.converter.convert('***'), '<hr>')
        self.assertEqual(self.converter.convert('___'), '<hr>')

    def test_mixed_content(self):
        md = "# Title\n\nThis is **bold** and [a link](url).

- List 1
- List 2"
        expected = "<h1>Title</h1>\n<p>This is <strong>bold</strong> and <a href=\"url\">a link</a>.</p>\n<ul>\n<li>List 1</li>\n<li>List 2</li>\n</ul>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_html_escaping(self):
        self.assertEqual(self.converter.convert('<script>alert(1)</script>'), '<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>')

    def test_nested_styles(self):
        # Bold inside link
        self.assertEqual(self.converter.convert('[**Bold Link**](url)'), '<p><a href="url"><strong>Bold Link</strong></a></p>')
        # Italic inside bold
        self.assertEqual(self.converter.convert('***Bold Italic***'), '<p><strong><em>Bold Italic</em></strong></p>')

    def test_empty_input(self):
        self.assertEqual(self.converter.convert(''), '')
        self.assertEqual(self.converter.convert('\n\n'), '')

    def test_unordered_list_transition(self):
        md = "- UL 1\n1. OL 1"
        expected = "<ul>\n<li>UL 1</li>\n</ul>\n<ol>\n<li>OL 1</li>\n</ol>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_complex_lists(self):
        md = "- Item 1\n- Item 2\n\n1. First\n2. Second"
        expected = "<ul>\n<li>Item 1</li>\n<li>Item 2</li>\n</ul>\n<ol>\n<li>First</li>\n<li>Second</li>\n</ol>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_multiple_blockquotes(self):
        md = "> Quote 1\n\nPlain text\n\n> Quote 2"
        expected = "<blockquote>\n<p>Quote 1</p></blockquote>\n<p>Plain text</p>\n<blockquote>\n<p>Quote 2</p></blockquote>"
        self.assertEqual(self.converter.convert(md), expected)

if __name__ == '__main__':
    unittest.main()