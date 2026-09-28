import re
import html

class MarkdownConverter:
    """A simple Markdown to HTML converter."""
    
    def __init__(self):
        pass

    def _generate_id(self, text):
        """Generate a URL-friendly ID from header text."""
        # Convert to lowercase, replace spaces with hyphens, remove non-alphanumeric characters
        id_text = text.lower()
        id_text = re.sub(r'\s+', '-', id_text)
        id_text = re.sub(r'[^a-z0-9-]', '', id_text)
        id_text = id_text.strip('-')
        # Fallback for empty IDs (e.g., header is just "!!!")
        if not id_text:
            id_text = "section"
        return id_text

    def generate_toc(self, text):
        """Generate a Table of Contents as an HTML unordered list based on headers."""
        lines = text.split('\n')
        toc_items = []
        
        for line in lines:
            # Match ATX headers (# Header)
            match = re.match(r'^(#{1,6})\s+(.*)', line)
            if match:
                level = len(match.group(1))
                content = match.group(2)
                header_id = self._generate_id(content)
                toc_items.append((level, f'<li><a href="#{header_id}">{content}</a></li>'))
        
        if not toc_items:
            return ''

        # Build the nested list structure using a stack to track open <ul> tags
        final_toc = ['<ul class="toc">']
        stack = [1] # The base level is 1 (from the outer <ul class="toc">)
        
        for level, item in toc_items:
            # If current header level is deeper than the last open list
            while level > stack[-1]:
                final_toc.append('<ul>')
                stack.append(stack[-1] + 1)
            # If current header level is shallower than the last open list
            while level < stack[-1]:
                final_toc.append('</ul>')
                stack.pop()
            
            final_toc.append(item)
            
        # Close all remaining open tags
        while len(stack) > 1:
            final_toc.append('</ul>')
            stack.pop()
        final_toc.append('</ul>')

        return ''.join(final_toc)

    def convert(self, text):
        lines = text.split('\n')
        
        # Pass 1: Collect all reference-style link definitions
        references = {}
        for line in lines:
            ref_match = re.match(r'^\s*\[([^\s\]]+)\]:\s*(\S+)(?:\s+["\'](.*?)["\'])?$', line)
            if ref_match:
                ref_id = ref_match.group(1)
                url = ref_match.group(2)
                title = ref_match.group(3) or ''
                references[ref_id] = (url, title)

        # Pass 2: Convert blocks to HTML
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
                    if line.strip():
                        html_output.append(f'<p>{self._parse_inline(line, references)}</p>')
                table_buffer = []
                in_table = False
                return

            # Process table lines
            table_html = ['<table border="1">']
            
            def split_row(row_line):
                row_line = row_line.strip()
                if row_line.startswith('|'): row_line = row_line[1:]
                if row_line.endswith('|'): row_line = row_line[:-1]
                return [cell.strip() for cell in row_line.split('|')]

            # Header
            headers = split_row(table_buffer[0])
            
            # Alignment from separator line (index 1)
            sep_cells = split_row(table_buffer[1])
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
                table_html.append(f'<th style="text-align:{align}">{self._parse_inline(h, references)}</th>')
            table_html.append('</tr></thead><tbody>')

            # Rows (skip the separator line at index 1)
            for line in table_buffer[2:]:
                row_line = line.strip()
                if not row_line:
                    continue
                
                cells = split_row(row_line)
                table_html.append('<tr>')
                # Use header count to ensure row consistency
                for i in range(len(headers)):
                    cell_content = cells[i] if i < len(cells) else ''
                    align = alignments[i] if i < len(alignments) else 'left'
                    table_html.append(f'<td style="text-align:{align}">{self._parse_inline(cell_content, references)}</td>')
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
                    html_output.append('<blockquote')
                    # The existing code had a bug here, let's fix it to be <blockquote>
                    # Wait, the provided code was <blockquote
                    # Actually looking at provided context: html_output.append('<blockquote>')
                    # Let's stick to provided original code style but ensure it's correct
                    html_output[-1] = '<blockquote>'
                    in_blockquote = True
                
                content = line[2:]
                html_output.append(f'<p>{self._parse_inline(content, references)}</p>')
                idx += 1
                continue
            elif line.startswith('>'):
                # Handle blockquote with empty content or just '>'
                if not in_blockquote:
                    html_output.append('<blockquote>')
                    in_blockquote = True
                
                content = line[1:].strip()
                if content:
                    html_output.append(f'<p>{self._parse_inline(content, references)}</p>')
                else:
                    html_output.append('<p></p>')
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
                
                html_output.append(f'<li>{self._parse_inline(content, references)}</li>')
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
                    header_text = line
                    header_id = self._generate_id(header_text)
                    html_output.append(f'<h1 id="{header_id}">{self._parse_inline(header_text, references)}</h1>')
                    idx += 2
                    continue
                elif next_line and re.match(r'^\s*(-+)\s*$', next_line):
                    # Check if it's a horizontal rule instead of a header
                    if idx > 0 and not lines[idx-1].strip():
                        pass
                    elif line.strip():
                        header_text = line
                        header_id = self._generate_id(header_text)
                        html_output.append(f'<h2 id="{header_id}">{self._parse_inline(header_text, references)}</h2>')
                        idx += 2
                        continue

            # Handle horizontal rules - improved regex to be more robust
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

            # Handle reference-style links definitions - skip in pass 2
            ref_match = re.match(r'^\s*\[([^\s\]]+)\]:\s*(\S+)(?:\s+["\'](.*?)["\'])?$', line)
            if ref_match:
                idx += 1
                continue

            # Handle block-level HTML
            if line.strip().startswith('<') and re.match(r'^\s*</?[a-zA-Z0-9]+', line):
                # Check if it's a safe block tag
                tag_match = re.match(r'^\s*</?([a-zA-Z0-9]+)', line)
                tag = tag_match.group(1).lower()
                if tag not in ['script', 'style', 'iframe', 'object', 'embed']:
                    html_output.append(line)
                    idx += 1
                    continue

            # Handle headers and blocks
            processed = False
            if line.startswith('# '):
                content = line[2:]
                html_output.append(f'<h1 id="{self._generate_id(content)}">{self._parse_inline(content, references)}</h1>')
                processed = True
            elif line.startswith('## '):
                content = line[3:]
                html_output.append(f'<h2 id="{self._generate_id(content)}">{self._parse_inline(content, references)}</h2>')
                processed = True
            elif line.startswith('### '):
                content = line[4:]
                html_output.append(f'<h3 id="{self._generate_id(content)}">{self._parse_inline(content, references)}</h3>')
                processed = True
            elif line.startswith('#### '):
                content = line[5:]
                html_output.append(f'<h4 id="{self._generate_id(content)}">{self._parse_inline(content, references)}</h4>')
                processed = True
            elif line.startswith('##### '):
                content = line[6:]
                html_output.append(f'<h5 id="{self._generate_id(content)}">{self._parse_inline(content, references)}</h5>')
                processed = True
            elif line.startswith('###### '):
                content = line[7:]
                html_output.append(f'<h6 id="{self._generate_id(content)}">{self._parse_inline(content, references)}</h6>')
                processed = True
            
            if not processed:
                if not line.strip():
                    idx += 1
                    continue
                html_output.append(f'<p>{self._parse_inline(line, references)}</p>')
            
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
                html_output.append(f'<li id="fn-{id}">{self._parse_inline(content, references)} <a href="#cn-{id}">↩</a></li>')
            html_output.append('</ol></section>')
        
        return '\n'.join(html_output)

    def _parse_inline(self, text, references=None):
        if references is None: references = {}
        # First, escape HTML special characters to prevent XSS
        text = html.escape(text)

        # Support for inline HTML: allow specific safe tags (e.g., <span>, <div>, <br>)
        safe_html_pattern = r'&lt;(/?[a-zA-Z0-9]+)([^&gt;]*)&gt;'
        def restore_html(match):
            tag = match.group(1)
            attrs = match.group(2)
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

        # Handle escaping
        escapes = []
        def save_escape(match):
            escapes.append(match.group(1))
            return f'__ESC_{len(escapes)-1}__'
        text = re.sub(r'\\([*_`~\[\]])', save_escape, text)

        # Inline code
        code_blocks = []
        def save_code(match):
            code_blocks.append(match.group(1))
            return f'__CODE_BLOCK_{len(code_blocks)-1}__'
        text = re.sub(r'`([^`]*)`', save_code, text)
        
        # Style patterns - handled in order from most specific to least specific
        # Bold-Italic
        text = re.sub(r'\*\*\*([^*]+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'___([^_]+?)___', r'<strong><em>\1</em></strong>', text)
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*([^*]+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_([^_]+?)_', r'<em>\1</em>', text)
        # Strike-through
        text = re.sub(r'~~(.*?)~~', r'<s>\1</s>', text)

        # Inline images: ![alt](url 'title') or ![alt](url) or ![alt][id]
        def replace_image(match):
            alt_text = match.group(1)
            link_part = match.group(2)
            if link_part.startswith('('):
                url_part = link_part[1:-1].strip()
                title_match = re.search(r'\s+(["\'])(.*?)\1$', url_part)
                if title_match:
                    url = url_part[:title_match.start()].strip()
                    title = title_match.group(2)
                    return f'<img src="{url}" alt="{alt_text}" title="{title}">'
                else:
                    return f'<img src="{url_part}" alt="{alt_text}">'
            elif link_part.startswith('[') and link_part.endswith(']'):
                ref_id = link_part[1:-1]
                if ref_id in references:
                    url, title = references[ref_id]
                    title_attr = f' title="{title}"' if title else ''
                    return f'<img src="{url}" alt="{alt_text}"{title_attr}>'
            return match.group(0)

        text = re.sub(r'!\[(.*?)\](\((.*?)\)|\[(.*?)\])', replace_image, text)
        
        # Inline links: [text](url 'title') or [text](url) or [text][id]
        def replace_link(match):
            text_content = match.group(1)
            link_part = match.group(2)
            if link_part.startswith('('):
                url_part = link_part[1:-1].strip()
                title_match = re.search(r'\s+(["\'])(.*?)\1$', url_part)
                if title_match:
                    url = url_part[:title_match.start()].strip()
                    title = title_match.group(2)
                    return f'<a href="{url}" title="{title}">{text_content}</a>'
                else:
                    return f'<a href="{url_part}">{text_content}</a>'
            elif link_part.startswith('[') and link_part.endswith(']'):
                ref_id = link_part[1:-1]
                if ref_id in references:
                    url, title = references[ref_id]
                    title_attr = f' title="{title}"' if title else ''
                    return f'<a href="{url}"{title_attr}>{text_content}</a>'
            return match.group(0)

        text = re.sub(r'\[(.*?)\](\((.*?)\)|\[(.*?)\])', replace_link, text)
        
        for i, code in enumerate(code_blocks):
            text = text.replace(f'__CODE_BLOCK_{i}__', f'<code>{code}</code>')
        for i, char in enumerate(escapes):
            text = text.replace(f'__ESC_{i}__', char)

        return text