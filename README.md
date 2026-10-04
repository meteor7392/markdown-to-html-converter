# Markdown to HTML Converter

A lightweight Python library to convert basic Markdown syntax into HTML5.

## Features
- Headers (H1-H6)
- Bold and Italic text
- Unordered and Ordered lists
- Blockquotes
- Code blocks and inline code
- Links and Images (including reference-style links)
- Horizontal Rules
- Paragraph handling
- Tables with alignment
- Footnotes
- Task lists
- Table of Contents generation

## Usage
```python
from converter import MarkdownConverter

conv = MarkdownConverter()
md_text = "# Welcome\nThis is **bold** text.\n\n## Section 1\nSome content."

# Generate TOC
toc = conv.generate_toc(md_text)
# Convert content
html = conv.convert(md_text)

print(toc + html)
```