import os
import tempfile
import subprocess
from pylint.lint import Run
from pylint.reporters.text import TextReporter
from io import StringIO
import ast
import re


class CodeAnalysis:
    """Enhanced code analysis with multiple tools and AI insights."""
    
    def __init__(self):
        self.complexity_threshold = 10
        self.line_length_threshold = 120
    
    def analyze_file(self, file_content, filename):
        """Comprehensive file analysis using multiple tools."""
        print(f"🔎 Starting comprehensive analysis for {filename}...")
        
        issues = {
            'structure': [],
            'standards': [],
            'bugs': [],
            'performance': [],
            'security': [],
            'complexity': []
        }
        
        if not file_content or not filename.endswith('.py'):
            issues['bugs'].append("Skipping: Not a Python file or empty content")
            print(f"⏭️  Skipped: {filename} (not Python or empty)")
            return issues
        
        # Create temporary file for analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name
        
        try:
            # Run all analysis tools
            pylint_issues = self._run_pylint_analysis(temp_path)
            flake8_issues = self._run_flake8_analysis(temp_path)
            ast_issues = self._run_ast_analysis(file_content, filename)
            security_issues = self._run_security_analysis(file_content)
            
            # Merge all issues
            for category in issues.keys():
                issues[category].extend(pylint_issues.get(category, []))
                issues[category].extend(flake8_issues.get(category, []))
                issues[category].extend(ast_issues.get(category, []))
                issues[category].extend(security_issues.get(category, []))
            
            total_issues = sum(len(lst) for lst in issues.values())
            print(f"📊 Analysis complete: {total_issues} total issues found")
            
        except Exception as e:
            issues['bugs'].append(f"Analysis error: {str(e)}")
            print(f"❌ Analysis error for {filename}: {str(e)}")
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return issues
    
    def _run_pylint_analysis(self, temp_path):
        """Run pylint analysis."""
        issues = {'structure': [], 'standards': [], 'bugs': []}
        
        try:
            print("🔍 Running Pylint analysis...")
            output = StringIO()
            reporter = TextReporter(output)
            Run([temp_path, '--disable=C0103'], reporter=reporter, exit=False)
            
            pylint_output = output.getvalue()
            print(f"Pylint output length: {len(pylint_output)} chars")
            
            for line in pylint_output.splitlines():
                if ': ' in line and any(x in line for x in ['C0', 'R0', 'W0', 'E0', 'F0']):
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        issue_info = parts[3].strip()
                        issue_code = issue_info.split(' ')[0]
                        issue_desc = ' '.join(issue_info.split(' ')[1:]).strip()
                        
                        if issue_code.startswith('C'):
                            issues['standards'].append(f"{issue_code}: {issue_desc}")
                        elif issue_code.startswith('R'):
                            issues['structure'].append(f"{issue_code}: {issue_desc}")
                        elif issue_code.startswith(('E', 'W', 'F')):
                            issues['bugs'].append(f"{issue_code}: {issue_desc}")
            
            print(f"Pylint found: {len(issues['standards'])} standards, {len(issues['structure'])} structure, {len(issues['bugs'])} bugs")
                            
        except Exception as e:
            issues['bugs'].append(f"Pylint error: {str(e)}")
            print(f"Pylint error: {str(e)}")
            
        return issues
    
    def _run_flake8_analysis(self, temp_path):
        """Run flake8 analysis using subprocess."""
        issues = {'standards': [], 'bugs': []}
        
        try:
            print("🔍 Running Flake8 analysis...")
            
            # Run flake8 as subprocess to capture output properly
            result = subprocess.run(
                ['flake8', temp_path, '--max-line-length=120'],
                capture_output=True,
                text=True
            )
            
            flake8_output = result.stdout
            print(f"Flake8 output length: {len(flake8_output)} chars")
            
            # Parse flake8 output
            for line in flake8_output.splitlines():
                if ':' in line:
                    # Format: filename:line:col: code message
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        error_part = parts[3].strip()
                        error_code = error_part.split(' ')[0]
                        error_desc = ' '.join(error_part.split(' ')[1:])
                        
                        if error_code.startswith(('E', 'F')):
                            issues['bugs'].append(f"{error_code}: {error_desc}")
                        elif error_code.startswith('W'):
                            issues['standards'].append(f"{error_code}: {error_desc}")
            
            print(f"Flake8 found: {len(issues['standards'])} standards, {len(issues['bugs'])} bugs")
                            
        except FileNotFoundError:
            issues['bugs'].append("Flake8 not found - install with: pip install flake8")
            print("❌ Flake8 not found")
        except Exception as e:
            issues['bugs'].append(f"Flake8 error: {str(e)}")
            print(f"Flake8 error: {str(e)}")
            
        return issues
    
    def _run_ast_analysis(self, file_content, filename):
        """Run AST-based analysis for complexity and structure."""
        issues = {'complexity': [], 'structure': []}
        
        try:
            tree = ast.parse(file_content)
            
            # Analyze complexity
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > self.complexity_threshold:
                        issues['complexity'].append(
                            f"Function '{node.name}' has high complexity: {complexity} (threshold: {self.complexity_threshold})"
                        )
                
                # Check for deeply nested code
                if isinstance(node, (ast.If, ast.For, ast.While)):
                    depth = self._calculate_nesting_depth(node)
                    if depth > 4:
                        issues['structure'].append(f"Deeply nested code detected: {depth} levels")
                        
        except SyntaxError as e:
            issues['bugs'].append(f"Syntax error: {str(e)}")
        except Exception as e:
            issues['bugs'].append(f"AST analysis error: {str(e)}")
            
        return issues
    
    def _run_security_analysis(self, file_content):
        """Run security-focused analysis."""
        issues = {'security': []}
        
        security_patterns = {
            r'eval\s*\(': "Avoid using eval() - security risk",
            r'exec\s*\(': "Avoid using exec() - security risk",
            r'__import__\s*\(': "Dynamic imports can be security risk",
            r'pickle\.loads?': "Pickle deserialization can be unsafe",
            r'input\s*\([^)]*\)': "Consider validating user input",
            r'os\.system\s*\(': "os.system() can be security risk - use subprocess",
            r'shell=True': "subprocess with shell=True can be dangerous",
        }
        
        for pattern, message in security_patterns.items():
            if re.search(pattern, file_content, re.IGNORECASE):
                issues['security'].append(message)
        
        return issues
    
    def _calculate_complexity(self, node):
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity
    
    def _calculate_nesting_depth(self, node, depth=0):
        """Calculate maximum nesting depth."""
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
