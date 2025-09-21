import os
from pylint.lint import Run
from pylint.reporters.text import TextReporter
from io import StringIO
import flake8.api.legacy as flake8

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
            print(f"Writing content to {temp_file} (length: {len(file_content)} chars)...")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            # pylint analysis
            print("Running pylint analysis...")
            output = StringIO()
            reporter = TextReporter(output)
            try:
                Run([temp_file], reporter=reporter, exit=False)
                pylint_output = output.getvalue()
                print(f"Pylint raw output:\n{pylint_output if pylint_output else 'Empty'}")
                # Robust parsing
                for line in pylint_output.splitlines():
                    if ': ' in line:
                        parts = line.split(': ', 1)
                        if len(parts) > 1 and parts[0].startswith(temp_file):
                            issue_parts = parts[0].split(':')
                            if len(issue_parts) >= 3:  # Ensure format: file:line:col: code
                                issue_code = issue_parts[-1].strip().split()[0]
                                issue_desc = parts[1].strip()
                                if issue_code.startswith('C'): issues['standards'].append(f"{issue_code}: {issue_desc}")
                                elif issue_code.startswith('R'): issues['structure'].append(f"{issue_code}: {issue_desc}")
                                elif issue_code.startswith('E') or issue_code.startswith('W'): issues['bugs'].append(f"{issue_code}: {issue_desc}")
                print(f"Pylint found {len(issues['standards'])} standards, {len(issues['structure'])} structure, {len(issues['bugs'])} bugs")
            except Exception as e:
                issues['bugs'].append(f"Pylint error: {str(e)}")
                print(f"Pylint failed: {str(e)}")
            
            # flake8 analysis
            print("Running flake8 analysis...")
            try:
                flake8_style = flake8.get_style_guide()
                report = flake8_style.check_files([temp_file])
                stats = report.get_statistics('')  # Get all issues
                print(f"Flake8 raw output:\n{stats if stats else 'Empty'}")
                for error in stats:
                    parts = error.split(' ', 2)
                    if len(parts) >= 2:
                        error_code = parts[1]
                        error_desc = parts[2] if len(parts) > 2 else ''
                        if error_code.startswith('E') or error_code.startswith('F'): issues['bugs'].append(f"{error_code}: {error_desc}")
                        elif error_code.startswith('W'): issues['standards'].append(f"{error_code}: {error_desc}")
                print(f"Flake8 found {len(stats)} issues")
            except Exception as e:
                issues['bugs'].append(f"Flake8 error: {str(e)}")
                print(f"Flake8 failed: {str(e)}")
        except Exception as e:
            issues['bugs'].append(f"Analysis error: {str(e)}")
            print(f"General analysis error: {str(e)}")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"Cleaned up {temp_file}")
        
        return issues