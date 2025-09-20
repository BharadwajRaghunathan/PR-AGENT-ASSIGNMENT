import os
from pylint.lint import Run
from pylint.reporters.text import TextReporter
from io import StringIO
import flake8.api as flake8

class CodeAnalysis:
    """Module for code review using pylint/flake8 (Code Review tech stack)."""
    def analyze_file(self, file_content, filename):
        """Analyzes file for structure, standards, bugs."""
        issues = {'structure': [], 'standards': [], 'bugs': []}
        
        temp_file = f"temp_{filename}"
        with open(temp_file, 'w') as f:
            f.write(file_content)
        
        # pylint
        output = StringIO()
        reporter = TextReporter(output)
        Run([temp_file], reporter=reporter, do_exit=False)
        pylint_output = output.getvalue()
        for line in pylint_output.splitlines():
            if 'C' in line: issues['standards'].append(line)
            elif 'R' in line: issues['structure'].append(line)
            elif 'E' in line or 'W' in line: issues['bugs'].append(line)
        
        # flake8
        flake8_style = flake8.get_style_guide()
        flake8_report = flake8_style.check_files([temp_file])
        for error in flake8_report.get_statistics('E'): issues['bugs'].append(error)
        for error in flake8_report.get_statistics('W'): issues['standards'].append(error)
        
        os.remove(temp_file)
        return issues