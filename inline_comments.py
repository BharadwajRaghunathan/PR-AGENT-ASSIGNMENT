import re

class InlineCommentGenerator:
    """Generate inline review comments similar to GitHub/GitLab."""
    
    def generate_inline_comments(self, file_data, issues):
        """Generate inline comments for specific lines of code."""
        inline_comments = []
        content_lines = file_data['content'].split('\n')
        patch_lines = file_data.get('patch', '').split('\n')
        
        # Parse patch to get line numbers
        line_mapping = self._parse_patch_line_numbers(patch_lines)
        
        for category, issue_list in issues.items():
            for issue in issue_list:
                line_comment = self._generate_line_specific_comment(issue, category, content_lines, line_mapping)
                if line_comment:
                    inline_comments.append(line_comment)
        
        return inline_comments
    
    def _parse_patch_line_numbers(self, patch_lines):
        """Parse patch to get line number mappings."""
        line_mapping = {}
        current_line = 0
        
        for line in patch_lines:
            if line.startswith('@@'):
                # Extract line number from @@ -x,y +a,b @@
                match = re.search(r'\+(\d+)', line)
                if match:
                    current_line = int(match.group(1))
            elif line.startswith('+') and not line.startswith('+++'):
                line_mapping[current_line] = line[1:]  # Remove + prefix
                current_line += 1
            elif not line.startswith('-'):
                current_line += 1
        
        return line_mapping
    
    def _generate_line_specific_comment(self, issue, category, content_lines, line_mapping):
        """Generate specific inline comment for an issue."""
        # Extract line number from pylint/flake8 output
        line_num = self._extract_line_number(issue)
        
        if line_num and line_num <= len(content_lines):
            code_line = content_lines[line_num - 1].strip()
            
            comment = {
                'line': line_num,
                'category': category,
                'issue': issue,
                'code': code_line,
                'suggestion': self._get_line_specific_suggestion(issue, code_line)
            }
            
            return comment
        
        return None
    
    def _extract_line_number(self, issue):
        """Extract line number from issue string."""
        # Look for patterns like "temp_file.py:5:0:" or just numbers
        match = re.search(r':(\d+):', issue)
        if match:
            return int(match.group(1))
        return None
    
    def _get_line_specific_suggestion(self, issue, code_line):
        """Get specific suggestion for the code line."""
        suggestions = {
            'E231': f"Add space after comma: `{code_line.replace(',', ', ')}`",
            'E261': "Add at least two spaces before inline comment",
            'E302': "Add 2 blank lines before this function/class definition",
            'E305': "Add 2 blank lines after this function/class definition",
            'E731': f"Replace lambda with def function",
            'F841': "Remove this unused variable",
            'C0114': "Add module docstring at the top of file",
            'C0116': f"Add docstring: `\"\"\"{self._suggest_docstring(code_line)}\"\"\"`",
            'W0612': "Remove or use this variable",
            'W0101': "This code is unreachable - remove it",
            'C3001': "Replace lambda with proper function definition",
            'W0125': "Avoid constant conditionals - use variable or logic",
            'C0115': "Add class docstring",
            'R0903': "Consider adding more public methods"
        }
        
        for code, suggestion in suggestions.items():
            if code in issue:
                return suggestion
        
        return "Consider reviewing this line for code quality improvements"
    
    def _suggest_docstring(self, code_line):
        """Suggest appropriate docstring based on code."""
        if 'def ' in code_line:
            func_name = code_line.split('def ')[1].split('(')[0]
            return f"Brief description of {func_name} function."
        elif 'class ' in code_line:
            class_name = code_line.split('class ')[1].split(':')[0]
            return f"Brief description of {class_name} class."
        else:
            return "Add appropriate description."