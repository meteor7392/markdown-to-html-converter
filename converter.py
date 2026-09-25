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
        list_stack = [] # Stack to track nesting levels: (indent, type)
        in_blockquote = False
        in_code_block = False
        code_buffer = []
        in_table = False
        table_buffer = []
        
        footnotes = []

        def flush_table():
            nonlocal in_table, table_buffer
            if not in_table:
                return
            
            if len(table_buffer) < 2:
                # Not a valid table (needs header and separator)
                for line in table_buffer:
                    html_output.append(f'<p>{self._parse_inline(line)}</p>')
                table_buffer = []
                in_table = False
                return

            # Process table lines
            table_html = ['<table border="1">']
            
            # Header - handle leading/trailing pipes
            header_line = table_buffer[0].strip()
            if header_line.startswith('|'): header_line = header_line[1:]
            if header_line.endswith('|'): header_line = header_line[:-1]
            headers = [h.strip() for h in header_line.split('|')]
            
            # Alignment from separator line (index 1)
            sep_line = table_buffer[1].strip()
            if sep_line.startswith('|'): sep_line = sep_line[1:]
            if sep_line.endswith('|'): sep_line = sep_line[:-1]
            sep_cells = [s.strip() for s in sep_line.split('|')]
            alignments = []
            for s in sep_cells:
                if s.startswith(':') and s.endswith(':'):
                    alignments.append('center')
                elif s.endswith(':'):
                    alignments.append('right')
                else:
                    alignments.append('left')

            table_html.append('<thead><tr>')
            for i, h in enumerate(headers):
                align = alignments[i] if i < len(alignments) else 'left'
                table_html.append(f'<th style="text-align:{align}">{self._parse_inline(h)}</th>')
            table_html.append('</tr></thead><tbody>')

            # Rows (skip the separator line at index 1)
            for line in table_buffer[2:]:
                row_line = line.strip()
                if not row_line:
                    continue
                if row_line.startswith('|'): row_line = row_line[1:]
                if row_line.endswith('|'): row_line = row_line[:-1]
                
                cells = [c.strip() for c in row_line.split('|')]
                table_html.append('<tr>')
                # Use header count to ensure row consistency
                for i in range(len(headers)):
                    cell_content = cells[i] if i < len(cells) else ''
                    align = alignments[i] if i < len(alignments) else 'left'
                    table_html.append(f'<td style="text-align:{align}">{self._parse_inline(cell_content)}</td>')
                table_html.append('</tr>')

            table_html.append('</tbody></table>')
            html_output.append(''.join(table_html))
            table_buffer = []
            in_table = False

        idx = 0
        while idx < len(lines):
            line = lines[idx]
            
            # Handle fenced code blocks
            if line.startswith('```'):
                flush_table()
                if not in_code_block:
                    in_code_block = True
                    code_buffer = []
                else:
                    html_output.append('<pre><code>')
                    html_output.append('\n'.join(code_buffer))
                    html_output.append('</code></pre>')
                    in_code_block = False
                idx += 1
                continue
            
            # Handle indented code blocks (4 spaces or 1 tab)
            if not in_code_block and (line.startswith('    ') or line.startswith('\t')):
                flush_table()
                if in_list:
                    while list_stack:
                        html_output.append(f'</{list_stack[-1][1]}>')
                        list_stack.pop()
                    in_list = False
                if in_blockquote:
                    html_output.append('</blockquote>')
                    in_blockquote = False
                
                in_code_block = True
                code_buffer = []
                content = line[4:] if line.startswith('    ') else line[1:]
                code_buffer.append(html.escape(content))
                idx += 1
                continue
            elif in_code_block and not line.startswith('```') and (line.startswith('    ') or line.startswith('\t') or not line.strip()):
                if line.strip():
                    content = line[4:] if line.startswith('    ') else line[1:]
                    code_buffer.append(html.escape(content))
                else:
                    code_buffer.append('')
                idx += 1
                continue
            elif in_code_block:
                # End of indented code block
                html_output.append('<pre><code>')
                html_output.append('\n'.join(code_buffer))
                html_output.append('</code></pre>')
                in_code_block = False
                # We don't increment idx here so this line can be processed as other markdown
                continue

            if in_code_block:
                # This is for fenced blocks
                code_buffer.append(html.escape(line))
                idx += 1
                continue

            # Handle tables
            if '|' in line:
                if not in_table:
                    in_table = True
                    table_buffer = [line]
                else:
                    table_buffer.append(line)
                idx += 1
                continue
            else:
                flush_table()

            # Handle blockquotes
            if line.startswith('> '):
                if not in_blockquote:
                    html_output.append('<blockquote>')
                    in_blockquote = True
                
                content = line[2:]
                html_output.append(f'<p>{self._parse_inline(content)}</p>')
                idx += 1
                continue
            else:
                if in_blockquote:
                    html_output.append('</blockquote>')
                    in_blockquote = False

            # Handle lists (including nested)
            ul_match = re.match(r'^(\s*)- ', line)
            ol_match = re.match(r'^(\s*)\d+\.\s', line)
            
            if ul_match or ol_match:
                indent = len(ul_match.group(1)) if ul_match else len(ol_match.group(1))
                current_type = 'ul' if ul_match else 'ol'
                content = re.sub(r'^\s*(- |\d+\.\s)', '', line)

                if not in_list:
                    in_list = True
                    html_output.append(f'<{current_type}>')
                    list_stack.append((indent, current_type))
                else:
                    # Check for nesting
                    if indent > (list_stack[-1][0] if list_stack else -1):
                        html_output.append(f'<{current_type}>')
                        list_stack.append((indent, current_type))
                    elif indent < (list_stack[-1][0] if list_stack else -1):
                        while list_stack and indent < list_stack[-1][0]:
                            html_output.append(f'</{list_stack[-1][1]}>')
                            list_stack.pop()
                        if not list_stack or indent != list_stack[-1][0]:
                            html_output.append(f'<{current_type}>')
                            list_stack.append((indent, current_type))
                    elif current_type != list_stack[-1][1]:
                        # Transition from UL to OL or vice versa at same level
                        html_output.append(f'</{list_stack[-1][1]}>')
                        html_output.append(f'<{current_type}>')
                        list_stack[-1] = (indent, current_type)
                
                html_output.append(f'<li>{self._parse_inline(content)}</li>')
                idx += 1
                continue
            else:
                if in_list:
                    while list_stack:
                        html_output.append(f'</{list_stack[-1][1]}>')
                        list_stack.pop()
                    in_list = False

            # Handle Setext-style headers
            if idx + 1 < len(lines):
                next_line = lines[idx + 1]
                if next_line and re.match(r'^\s*(=+)\s*$', next_line):
                    html_output.append(f'<h1>{self._parse_inline(line)}</h1>')
                    idx += 2
                    continue
                elif next_line and re.match(r'^\s*(-+)\s*$', next_line):
                    # Check if it's a horizontal rule instead of a header
                    # In simple markdown, a line of --- after a blank line is an HR.
                    # If it's immediately after text, it's an H2.
                    if line.strip():
                        html_output.append(f'<h2>{self._parse_inline(line)}</h2>')
                        idx += 2
                        continue

            # Handle horizontal rules
            if re.match(r'^\s*([-*_=])(\s*\1){2,}\s*$', line):
                html_output.append('<hr>')
                idx += 1
                continue

            # Handle footnote definitions
            fn_match = re.match(r'^\s*\[\^([^]]+)\]:\s*(.*)', line)
            if fn_match:
                footnotes.append((fn_match.group(1), fn_match.group(2)))
                idx += 1
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
                if not line.strip():
                    idx += 1
                    continue
                html_output.append(f'<p>{self._parse_inline(line)}</p>')
            
            idx += 1

        flush_table()
        while list_stack:
            html_output.append(f'</{list_stack[-1][1]}>')
            list_stack.pop()
        if in_blockquote:
            html_output.append('</blockquote>')
        if in_code_block:
            html_output.append('<pre><code>')
            html_output.append('\n'.join(code_buffer))
            html_output.append('</code></pre>')

        # Process footnotes at the end of the document
        if footnotes:
            html_output.append('<hr><section class="footnotes"><ol>')
            for id, content in footnotes:
                html_output.append(f'<li id="fn-{id}">{self._parse_inline(content)} <a href="#cn-{id}">↩</a></li>')
            html_output.append('</ol></section>')

        return '\n'.join(html_output)

    def _parse_inline(self, text):
        # First, escape HTML special characters to prevent XSS
        text = html.escape(text)

        # Support for inline HTML: allow specific safe tags (e.g., <span>, <div>, <br>)
        # This replaces escaped versions of these tags back to original HTML
        # Note: In a real library, a whitelist of tags and attributes would be used
        safe_html_pattern = r'&lt;(/?[a-zA-Z0-9]+)([^&gt;]*)&gt;'
        def restore_html(match):
            tag = match.group(1)
            attrs = match.group(2)
            # Basic check to ensure we aren't restoring scripts or styles
            if tag.lower() in ['script', 'style', 'iframe', 'object', 'embed']:
                return match.group(0)
            return f'<{tag}{attrs}>'
        
        text = re.sub(safe_html_pattern, restore_html, text)

        # Task lists support (checkboxes)
        text = re.sub(r'\[ \] ', r'<input type="checkbox" disabled> ', text)
        text = re.sub(r'\[x\] ', r'<input type="checkbox" checked disabled> ', text)
        text = re.sub(r'\[X\] ', r'<input type="checkbox" checked disabled> ', text)

        # Footnote references: [^1]
        text = re.sub(r'\[\^([^]]+)\]', r'<sup><a href="#fn-\1" id="cn-\1">\1</a></sup>', text)

        # Handle escaping by storing escaped characters
        escapes = []
        def save_escape(match):
            escapes.append(match.group(1))
            return f'__ESC_{len(escapes)-1}__'
        
        # Escape *, _, `, ~, [, ]
        text = re.sub(r'\\([*_`~\[\]])', save_escape, text)

        # Inline code: `code` - Processed first and stored in placeholders to avoid interpreting markdown inside code
        code_blocks = []
        def save_code(match):
            code_blocks.append(match.group(1))
            return f'__CODE_BLOCK_{len(code_blocks)-1}__'
        
        text = re.sub(r'`([^`]*)`', save_code, text)
        
        # Process bold and italic before links so we can have styling inside links
        # Bold-Italic
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'___(.*?)___', r'<strong><em>\1</em></strong>', text)

        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*([^*]+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_([^_]+?)_', r'<em>\1</em>', text)

        # Strike-through
        text = re.sub(r'~~(.*?)~~', r'<s>\1</s>', text)

        # Inline images: ![alt](url 'title') or ![alt](url)
        def replace_image(match):
            alt_text = match.group(1)
            url_part = match.group(2).strip()
            title_match = re.search(r'\s+(["\'])(.*?)\1$', url_part)
            if title_match:
                url = url_part[:title_match.start()].strip()
                title = title_match.group(2)
                return f'<img src="{url}" alt="{alt_text}" title="{title}">'
            else:
                return f'<img src="{url_part}" alt="{alt_text}">'

        text = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_image, text)
        
        # Inline links: [text](url 'title') or [text](url)
        def replace_link(match):
            text_content = match.group(1)
            url_part = match.group(2).strip()
            # Better title matching: search for quoted string at the end of the URL part
            title_match = re.search(r'\s+(["\'])(.*?)\1$', url_part)
            if title_match:
                url = url_part[:title_match.start()].strip()
                title = title_match.group(2)
                return f'<a href="{url}" title="{title}">{text_content}</a>'
            else:
                return f'<a href="{url_part}">{text_content}</a>'

        text = re.sub(r'\[(.*?)\]\((.*?)\)', replace_link, text)
        
        # Restore inline code
        for i, code in enumerate(code_blocks):
            text = text.replace(f'__CODE_BLOCK_{i}__', f'<code>{code}</code>')

        # Restore escaped characters
        for i, char in enumerate(escapes):
            text = text.replace(f'__ESC_{i}__', char)

        return text