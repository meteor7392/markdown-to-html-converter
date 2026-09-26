import unittest
from converter import MarkdownConverter

class TestMarkdownConverter(unittest.TestCase):
    def setUp(self):
        self.converter = MarkdownConverter()

    def test_headers(self):
        self.assertEqual(self.converter.convert('# Hello'), '<h1 id="hello">Hello</h1>')
        self.assertEqual(self.converter.convert('## Subtitle'), '<h2 id="subtitle">Subtitle</h2>')
        self.assertEqual(self.converter.convert('### Section'), '<h3 id="section">Section</h3>')
        self.assertEqual(self.converter.convert('#### Sub'), '<h4 id="sub">Sub</h4>')
        self.assertEqual(self.converter.convert('##### Sub'), '<h5 id="sub">Sub</h5>')
        self.assertEqual(self.converter.convert('###### Sub'), '<h6 id="sub">Sub</h6>')

    def test_bold_italic(self):
        self.assertEqual(self.converter.convert('This is **bold**'), '<p>This is <strong>bold</strong></p>')
        self.assertEqual(self.converter.convert('This is *italic*'), '<p>This is <em>italic</em></p>')

    def test_strikethrough(self):
        self.assertEqual(self.converter.convert('This is ~~strikethrough~~'), '<p>This is <s>strikethrough</s></p>')

    def test_lists(self):
        md = "- Item 1\n- Item 2"
        expected = "<ul>\n<li>Item 1</li>\n<li>Item 2</li>\n</ul>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_ordered_lists(self):
        md = "1. First\n2. Second"
        expected = "<ol>\n<li>First</li>\n<li>Second</li>\n</ol>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_nested_lists(self):
        md = "- Parent\n  - Child 1\n  - Child 2\n    - Grandchild\n- Parent 2"
        expected = "<ul>\n<li>Parent</li>\n<ul>\n<li>Child 1</li>\n<li>Child 2</li>\n<ul>\n<li>Grandchild</li>\n</ul>\n</ul>\n<li>Parent 2</li>\n</ul>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_mixed_nested_lists(self):
        md = "1. Step 1\n   - Detail A\n   - Detail B\n2. Step 2"
        expected = "<ol>\n<li>Step 1</li>\n<ul>\n<li>Detail A</li>\n<li>Detail B</li>\n</ul>\n<li>Step 2</li>\n</ol>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_blockquotes(self):
        md = "> Quote"
        self.assertEqual(self.converter.convert(md), "<blockquote>\n<p>Quote</p></blockquote>")

    def test_paragraphs(self):
        self.assertEqual(self.converter.convert('Plain text'), '<p>Plain text</p>')

    def test_links_and_images(self):
        self.assertEqual(self.converter.convert('[Google](https://google.com)'), '<p><a href="https://google.com">Google</a></p>')
        self.assertEqual(self.converter.convert('![Alt text](img.jpg)'), '<p><img src="img.jpg" alt="Alt text"></p>')
        self.assertEqual(self.converter.convert('![Alt text](img.jpg "Title")'), '<p><img src="img.jpg" alt="Alt text" title="Title"></p>')

    def test_code(self):
        # Inline code
        self.assertEqual(self.converter.convert('Use `print()`'), '<p>Use <code>print()</code></p>')
        # Empty inline code
        self.assertEqual(self.converter.convert('Empty `` code'), '<p>Empty <code></code> code</p>')
        # Code block
        md = "```\nprint('hello')\n```"
        self.assertEqual(self.converter.convert(md), "<pre><code>print('hello')</code></pre>")

    def test_indented_code(self):
        md = "Some text\n\n    indented code\n    more code\n\nBack to text"
        expected = "<p>Some text</p>\n<pre><code>indented code\nmore code</code></pre>\n<p>Back to text</p>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_horizontal_rule(self):
        self.assertEqual(self.converter.convert('---'), '<hr>')
        self.assertEqual(self.converter.convert('***'), '<hr>')
        self.assertEqual(self.converter.convert('___'), '<hr>')
        self.assertEqual(self.converter.convert('==='), '<hr>')

    def test_mixed_content(self):
        md = "# Title\n\nThis is **bold** and [a link](url).

- List 1
- List 2"
        expected = "<h1 id="title">Title</h1>\n<p>This is <strong>bold</strong> and <a href=\"url\">a link</a>.</p>\n<ul>\n<li>List 1</li>\n<li>List 2</li>\n</ul>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_html_escaping(self):
        self.assertEqual(self.converter.convert('<script>alert(1)</script>'), '<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>')

    def test_inline_html(self):
        self.assertEqual(self.converter.convert('This is <span style="color:red">red</span> text'), '<p>This is <span style="color:red">red</span> text</p>')
        self.assertEqual(self.converter.convert('Line<br>Break'), '<p>Line<br>Break</p>')
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

    def test_empty_link(self):
        self.assertEqual(self.converter.convert('[]()'), '<p><a href=""></a></p>')

    def test_task_lists(self):
        md = "- [ ] Unchecked\n- [x] Checked"
        expected = "<ul>\n<li><input type=\"checkbox\" disabled> Unchecked</li>\n<li><input type=\"checkbox\" checked disabled> Checked</li>\n</ul>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_escaping(self):
        self.assertEqual(self.converter.convert('\*Not bold\*'), '<p>*Not bold*</p>')
        self.assertEqual(self.converter.convert('\`Not code\`'), '<p>`Not code`</p>')
        self.assertEqual(self.converter.convert('Escaped \\ backslash'), '<p>Escaped \ backslash</p>')
        self.assertEqual(self.converter.convert('Mixed \*bold\* and **real bold**'), '<p>Mixed *bold* and <strong>real bold</strong></p>')

    def test_tables(self):
        md = "| Header 1 | Header 2 |\n| --- | --- |\n| Cell 1 | Cell 2 |"
        expected = "<table border=\"1\"><thead><tr><th style=\"text-align:left\">Header 1</th><th style=\"text-align:left\">Header 2</th></tr></thead><tbody><tr><td style=\"text-align:left\">Cell 1</td><td style=\"text-align:left\">Cell 2</td></tr></tbody></table>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_tables_alignment(self):
        md = "| Left | Center | Right |\n| :--- | :---: | ---: |\n| L | C | R |"
        expected = "<table border=\"1\"><thead><tr><th style=\"text-align:left\">Left</th><th style=\"text-align:center\">Center</th><th style=\"text-align:right\">Right</th></tr></thead><tbody><tr><td style=\"text-align:left\">L</td><td style=\"text-align:center\">C</td><td style=\"text-align:right\">R</td></tr></tbody></table>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_tables_with_formatting(self):
        md = "| **Bold** | *Italic* |\n| --- | --- |\n| Cell **1** | Cell *2* |"
        expected = "<table border=\"1\"><thead><tr><th style=\"text-align:left\"><strong>Bold</strong></th><th style=\"text-align:left\"><em>Italic</em></th></tr></thead><tbody><tr><td style=\"text-align:left\">Cell <strong>1</strong></td><td style=\"text-align:left\">Cell <em>2</em></td></tr></tbody></table>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_footnotes(self):
        md = "This is a claim[^1].\n\n[^1]: This is the footnote content."
        expected = "<p>This is a claim<sup><a href=\"#fn-1\" id=\"cn-1\">1</a></sup>.</p>\n<hr><section class=\"footnotes\"><ol><li id=\"fn-1\">This is the footnote content. <a href=\"#cn-1\">↩</a></li></ol></section>"
        self.assertEqual(self.converter.convert(md), expected)

    def test_multiple_footnotes(self):
        md = "First[^1] and second[^2].\n\n[^1]: Footnote 1\n[^2]: Footnote 2"
        expected = "<p>First<sup><a href=\"#fn-1\" id=\"cn-1\">1</a></sup> and second<sup><a href=\"#fn-2\" id=\"cn-2\">2</a></sup>.</p>\n<hr><section class=\"footnotes\"><ol><li id=\"fn-1\">Footnote 1 <a href=\"#cn-1\">↩</a></li><li id=\"fn-2\">Footnote 2 <a href=\"#cn-2\">↩</a></li></ol></section>"
        self.assertEqual(self.converter.convert(md), expected)

if __name__ == '__main__':
    unittest.main()