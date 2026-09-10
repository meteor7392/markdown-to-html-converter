# Markdown to HTML Converter

A lightweight Python library to convert basic Markdown syntax into HTML5.

## Features
- Headers (H1, H2, H3)
- Bold and Italic text
- Unordered lists
- Paragraph handling

## Usage
```python
from converter import MarkdownConverter

conv = MarkdownConverter()
html = conv.convert("# Welcome\nThis is **bold** text.")
print(html)
```