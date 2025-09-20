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
                print(f"Pylint output: {'Empty' if not pylint_output else 'Generated'}")
                # Parse pylint output more robustly
                for line in pylint_output.splitlines():
                    # Look for issue codes (e.g., C0301, R0903, E0602, W0612)
                    if ': ' in line and any(code in line for code in ['C', 'R', 'E', 'W']):
                        if 'C' in line.split()[0]: issues['standards'].append(line)
                        elif 'R' in line.split()[0]: issues['structure'].append(line)
                        elif 'E' in line.split()[0] or 'W' in line.split()[0]: issues['bugs'].append(line)
                print(f"Pylint found {len(issues['standards'])} standards, {len(issues['structure'])} structure, {len(issues['bugs'])} bugs")
            except Exception as e:
                issues['bugs'].append(f"Pylint error: {str(e)}")
                print(f"Pylint failed: {str(e)}")
            
            # flake8 analysis
            print("Running flake8 analysis...")
            try:
                flake8_style = flake8.get_style_guide()
                report = flake8_style.check_files([temp_file])
                # Capture all issues
                stats = report.get_statistics('')
                for error in stats:
                    if error.startswith('E') or error.startswith('F'): issues['bugs'].append(error)
                    elif error.startswith('W'): issues['standards'].append(error)
                print(f"Flake8 issues - Total: {len(stats)}")
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