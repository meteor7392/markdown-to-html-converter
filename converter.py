import re

class MarkdownConverter:
    """A simple Markdown to HTML converter."""
    
    def __init__(self):
        self.rules = [
            (r'^# (.*)$', r'<h1>\1</h1>'),
            (r'^## (.*)$', r'<h2>\1</h2>'),
            (r'^### (.*)$', r'<h3>\1</h3>'),
            (r'^\*\*(.*?)\*\*', r'<strong>\1</strong>'),
            (r'^__(.*?)__', r'<strong>\1</strong>'),
            (r'^\*(.*?)\*$', r'<em>\1</em>'),
            (r'^_(.*?)_$', r'<em>\1</em>'),
        ]

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
            for pattern, replacement in self.rules:
                if re.match(pattern, line):
                    html_output.append(re.sub(pattern, replacement, line))
                    processed = True
                    break
            
            if not processed:
                if line.strip() == '':
                    continue
                html_output.append(f'<p>{self._parse_inline(line)}</p>')

        if in_list:
            html_output.append('</ul>')

        return '\n'.join(html_output)

    def _parse_inline(self, text):
        # Simple inline formatting for bold and italic
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
        return text
