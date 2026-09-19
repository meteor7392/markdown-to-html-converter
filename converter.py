import re
import html

class MarkdownConverter:
    """A simple Markdown to HTML converter."""
    
    def __init__(self):
        pass

    def convert(self, text):
        lines = text.split('\n')
        html_output = []
        in_list = False
        list_type = None  # 'ul' or 'ol'
        in_blockquote = False
        in_code_block = False
        code_buffer = []

        for line in lines:
            # Handle fenced code blocks
            if line.startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_buffer = []
                else:
                    html_output.append('<pre><code>')
                    html_output.append('\n'.join(code_buffer))
                    html_output.append('</code></pre>')
                    in_code_block = False
                continue
            
            if in_code_block:
                code_buffer.append(html.escape(line))
                continue

            # Handle blockquotes
            if line.startswith('> '):
                if not in_blockquote:
                    html_output.append('<blockquote>')
                    in_blockquote = True
                
                content = line[2:]
                html_output.append(f'<p>{self._parse_inline(content)}</p>')
                continue
            else:
                if in_blockquote:
                    html_output.append('</blockquote>')
                    in_blockquote = False

            # Handle unordered lists
            if line.startswith('- ') or (in_list and list_type == 'ul' and line.startswith('  - ')):
                if not in_list or list_type != 'ul':
                    if in_list:
                        html_output.append(f'</{list_type}>')
                    html_output.append('<ul>')
                    in_list = True
                    list_type = 'ul'
                content = re.sub(r'^\s*- ', '', line)
                html_output.append(f'<li>{self._parse_inline(content)}</li>')
                continue
            
            # Handle ordered lists
            elif re.match(r'\d+\.\s', line) or (in_list and list_type == 'ol' and re.search(r'\s+\d+\.\s', line)):
                if not in_list or list_type != 'ol':
                    if in_list:
                        html_output.append(f'</{list_type}>')
                    html_output.append('<ol>')
                    in_list = True
                    list_type = 'ol'
                content = re.sub(r'^\s*\d+\.\s', '', line)
                html_output.append(f'<li>{self._parse_inline(content)}</li>')
                continue
            else:
                if in_list:
                    html_output.append(f'</{list_type}>')
                    in_list = False
                    list_type = None

            # Handle horizontal rules
            if line.strip() == '---' or line.strip() == '***' or line.strip() == '___':
                html_output.append('<hr>')
                continue

            # Handle headers and blocks
            processed = False
            if line.startswith('# '):
                html_output.append(f'<h1>{self._parse_inline(line[2:])}</h1>')
                processed = True
            elif line.startswith('## '):
                html_output.append(f'<h2>{self._parse_inline(line[3:])}</h2>')
                processed = True
            elif line.startswith('### '):
                html_output.append(f'<h3>{self._parse_inline(line[4:])}</h3>')
                processed = True
            elif line.startswith('#### '):
                html_output.append(f'<h4>{self._parse_inline(line[5:])}</h4>')
                processed = True
            elif line.startswith('##### '):
                html_output.append(f'<h5>{self._parse_inline(line[6:])}</h5>')
                processed = True
            elif line.startswith('###### '):
                html_output.append(f'<h6>{self._parse_inline(line[7:])}</h6>')
                processed = True
            
            if not processed:
                if line.strip() == '':
                    continue
                html_output.append(f'<p>{self._parse_inline(line)}</p>')

        if in_list:
            html_output.append(f'</{list_type}>')
        if in_blockquote:
            html_output.append('</blockquote>')
        if in_code_block:
            html_output.append('<pre><code>')
            html_output.append('\n'.join(code_buffer))
            html_output.append('</code></pre>')

        return '\n'.join(html_output)

    def _parse_inline(self, text):
        # First, escape HTML special characters to prevent XSS
        text = html.escape(text)

        # Inline code: `code` - Processed first to avoid interpreting markdown inside code
        text = re.sub(r'`([^`]*)`', r'<code-block>\1</code-block>', text)
        
        # Re-evaluating: the provided source had <code-block> as a temporary marker
        text = re.sub(r'<code-block>(.*?)</code-block>', r'<code>\1</code>', text)
        
        # Process bold and italic before links so we can have styling inside links
        # Bold-Italic
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'___(.*?)___', r'<strong><em>\1</em></strong>', text)

        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)

        # Inline images: ![alt](url)
        text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', text)
        # Inline links: [text](url)
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
        
        return text