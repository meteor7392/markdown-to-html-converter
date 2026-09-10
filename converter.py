import re

class MarkdownConverter:
    """A simple Markdown to HTML converter."""
    
    def __init__(self):
        pass

    def convert(self, text):
        lines = text.split('\n')
        html_output = []
        in_list = False

        for line in lines:
            # Handle unordered lists
            if line.startswith('- '):
                if not in_list:
                    html_output.append('<ul>')
                    in_list = True
                html_output.append(f'<li>{self._parse_inline(line[2:])}</li>')
                continue
            else:
                if in_list:
                    html_output.append('</ul>')
                    in_list = False

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
            
            if not processed:
                if line.strip() == '':
                    continue
                html_output.append(f'<p>{self._parse_inline(line)}</p>')

        if in_list:
            html_output.append('</ul>')

        return '\n'.join(html_output)

    def _parse_inline(self, text):
        # Inline images: ![alt](url)
        text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', text)
        # Inline links: [text](url)
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
        return text
