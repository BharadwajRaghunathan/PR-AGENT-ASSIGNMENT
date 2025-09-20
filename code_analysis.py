import os
from pylint.lint import Run
from pylint.reporters.text import TextReporter
from io import StringIO
import flake8.api as flake8

class CodeAnalysis:
    """Module for code review using pylint/flake8 (Code Review tech stack)."""
    def analyze_file(self, file_content, filename):
        """Analyzes file for structure, standards, bugs."""
        print(f"Starting analysis for {filename}...")
        issues = {'structure': [], 'standards': [], 'bugs': []}
        
        if not file_content or not filename.endswith('.py'):
            issues['bugs'].append("Skipping non-Python or empty file")
            print(f"Skipped: {filename} is not Python or empty.")
            return issues
        
        temp_file = f"temp_{filename}"
        try:
            print(f"Writing content to {temp_file}...")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            # pylint analysis
            print("Running pylint analysis...")
            output = StringIO()
            reporter = TextReporter(output)
            Run([temp_file], reporter=reporter)
            pylint_output = output.getvalue()
            print(f"Pylint output: {pylint_output if pylint_output else 'Empty'}")
            for line in pylint_output.splitlines():
                if line.startswith('C'): issues['standards'].append(line)
                elif line.startswith('R'): issues['structure'].append(line)
                elif line.startswith('E') or line.startswith('W'): issues['bugs'].append(line)
            
            # flake8 analysis
            print("Running flake8 analysis...")
            flake8_style = flake8.get_style_guide()
            flake8_report = flake8_style.check_files([temp_file])
            for error in flake8_report.get_statistics('E'):
                issues['bugs'].append(error)
            for error in flake8_report.get_statistics('W'):
                issues['standards'].append(error)
            print(f"Flake8 issues - Errors: {len(flake8_report.get_statistics('E'))}, Warnings: {len(flake8_report.get_statistics('W'))}")
        except Exception as e:
            issues['bugs'].append(f"Analysis error: {str(e)}")
            print(f"Error during analysis: {str(e)}")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"Cleaned up {temp_file}")
        
        return issues