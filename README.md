# Markdown to HTML Converter

A lightweight Python library to convert basic Markdown syntax into HTML5.

## Features
- Headers (H1-H6)
- Bold and Italic text
- Unordered and Ordered lists
- Blockquotes
- Code blocks and inline code
- Links and Images
- Horizontal Rules
- Paragraph handling
- Tables with alignment
- Footnotes
- Task lists

## Usage
```python
from converter import MarkdownConverter

conv = MarkdownConverter()
html = conv.convert("# Welcome\nThis is **bold** text.")
print(html)
```