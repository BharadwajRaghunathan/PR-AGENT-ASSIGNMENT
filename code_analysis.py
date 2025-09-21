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
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
                print(f"📝 Created temp file: {temp_path}")
            
            # Run all analysis tools and merge results
            pylint_issues = self._run_pylint_analysis(temp_path)
            flake8_issues = self._run_flake8_analysis(temp_path)
            ast_issues = self._run_ast_analysis(file_content, filename)
            security_issues = self._run_security_analysis(file_content)
            
            # Merge all issues properly
            for category in issues.keys():
                if category in pylint_issues:
                    issues[category].extend(pylint_issues[category])
                if category in flake8_issues:
                    issues[category].extend(flake8_issues[category])
                if category in ast_issues:
                    issues[category].extend(ast_issues[category])
                if category in security_issues:
                    issues[category].extend(security_issues[category])
            
            total_issues = sum(len(lst) for lst in issues.values())
            print(f"📊 Analysis complete: {total_issues} total issues found")
            
            # Debug: Print issues by category
            for category, issue_list in issues.items():
                if issue_list:
                    print(f"   {category}: {len(issue_list)} issues")
            
        except Exception as e:
            issues['bugs'].append(f"Analysis error: {str(e)}")
            print(f"❌ Analysis error for {filename}: {str(e)}")
        finally:
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"🧹 Cleaned up temp file")
        
        return issues
    
    def _run_pylint_analysis(self, temp_path):
        """Run pylint analysis with improved parsing."""
        issues = {'structure': [], 'standards': [], 'bugs': []}
        
        try:
            print("🔍 Running Pylint analysis...")
            output = StringIO()
            reporter = TextReporter(output)
            
            # Run pylint with minimal config
            Run([temp_path, 
                 '--disable=C0103,R0801', 
                 '--reports=no',
                 '--score=no'], 
                reporter=reporter, exit=False)
            
            pylint_output = output.getvalue()
            print(f"📋 Pylint output ({len(pylint_output)} chars):")
            if pylint_output.strip():
                # Show first few lines for debugging
                lines = pylint_output.split('\n')[:10]
                for line in lines:
                    if line.strip():
                        print(f"  DEBUG: {line}")
            
            # Improved parsing for Windows paths
            lines_processed = 0
            for line in pylint_output.splitlines():
                if line.strip() and any(code in line for code in ['C0', 'R0', 'W0', 'E0', 'F0']):
                    try:
                        # Use regex to extract code and message
                        # Pattern: path:line:col: CODE: message
                        match = re.search(r'([CRWEF]\d{4}):\s*(.+)', line)
                        if match:
                            code = match.group(1)
                            message = match.group(2).strip()
                            full_message = f"{code}: {message}"
                            
                            print(f"  PARSED: {code} -> {message[:50]}...")
                            
                            # Categorize by code prefix
                            if code.startswith('C'):
                                issues['standards'].append(full_message)
                            elif code.startswith('R'):
                                issues['structure'].append(full_message)
                            elif code.startswith(('E', 'W', 'F')):
                                issues['bugs'].append(full_message)
                            
                            lines_processed += 1
                        else:
                            print(f"  UNPARSED: {line[:100]}...")
                    except Exception as e:
                        print(f"⚠️ Error parsing pylint line: {line[:100]}... - {str(e)}")
            
            print(f"✅ Pylint processed {lines_processed} issue lines")
            print(f"   Standards: {len(issues['standards'])}, Structure: {len(issues['structure'])}, Bugs: {len(issues['bugs'])}")
                            
        except Exception as e:
            issues['bugs'].append(f"Pylint error: {str(e)}")
            print(f"❌ Pylint error: {str(e)}")
            
        return issues
    
    def _run_flake8_analysis(self, temp_path):
        """Run flake8 analysis with better error handling."""
        issues = {'standards': [], 'bugs': []}
        
        try:
            print("🔍 Running Flake8 analysis...")
            
            # Try flake8 subprocess first
            try:
                result = subprocess.run(
                    ['flake8', temp_path, '--max-line-length=120'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                flake8_output = result.stdout
                flake8_errors = result.stderr
                
                print(f"📋 Flake8 stdout ({len(flake8_output)} chars):")
                if flake8_output.strip():
                    for line in flake8_output.split('\n')[:5]:
                        if line.strip():
                            print(f"  DEBUG: {line}")
                
                if flake8_errors.strip():
                    print(f"📋 Flake8 stderr: {flake8_errors[:200]}")
                
                # Parse flake8 output
                lines_processed = 0
                for line in flake8_output.splitlines():
                    if ':' in line and any(code in line for code in ['E', 'W', 'F']):
                        try:
                            # Use regex for better parsing
                            # Pattern: path:line:col: code message
                            match = re.search(r'([EWF]\d{3})\s+(.+)', line)
                            if match:
                                error_code = match.group(1)
                                error_desc = match.group(2).strip()
                                full_message = f"{error_code}: {error_desc}"
                                
                                print(f"  PARSED: {error_code} -> {error_desc[:50]}...")
                                
                                # Categorize by code prefix
                                if error_code.startswith(('E', 'F')):
                                    issues['bugs'].append(full_message)
                                elif error_code.startswith('W'):
                                    issues['standards'].append(full_message)
                                
                                lines_processed += 1
                        except Exception as e:
                            print(f"⚠️ Error parsing flake8 line: {line[:100]}... - {str(e)}")
                
                print(f"✅ Flake8 subprocess processed {lines_processed} issue lines")
                            
            except (FileNotFoundError, subprocess.SubprocessError):
                print("⚠️ Flake8 subprocess failed - trying Python module...")
                
                # Fallback to Python module
                result = subprocess.run(
                    ['python', '-m', 'flake8', temp_path, '--max-line-length=120'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                flake8_output = result.stdout
                
                # Same parsing logic as above
                lines_processed = 0
                for line in flake8_output.splitlines():
                    if ':' in line and any(code in line for code in ['E', 'W', 'F']):
                        match = re.search(r'([EWF]\d{3})\s+(.+)', line)
                        if match:
                            error_code = match.group(1)
                            error_desc = match.group(2).strip()
                            full_message = f"{error_code}: {error_desc}"
                            
                            if error_code.startswith(('E', 'F')):
                                issues['bugs'].append(full_message)
                            elif error_code.startswith('W'):
                                issues['standards'].append(full_message)
                            
                            lines_processed += 1
                
                print(f"✅ Flake8 module processed {lines_processed} issue lines")
                
        except Exception as e:
            print(f"❌ All flake8 methods failed, trying direct import...")
            # Final fallback to direct import
            try:
                import flake8.api.legacy as flake8_api
                style_guide = flake8_api.get_style_guide(max_line_length=120)
                report = style_guide.check_files([temp_path])
                stats = report.get_statistics('')
                
                for error in stats:
                    parts = error.strip().split(' ', 1)
                    if len(parts) >= 2:
                        count_and_code = parts[0]
                        message = parts[1]
                        # Extract just the code (like "E231")
                        code_match = re.search(r'([EWF]\d+)', count_and_code)
                        if code_match:
                            code = code_match.group(1)
                            full_message = f"{code}: {message}"
                            
                            if code.startswith(('E', 'F')):
                                issues['bugs'].append(full_message)
                            elif code.startswith('W'):
                                issues['standards'].append(full_message)
                
                print(f"✅ Flake8 direct import found issues: {len(issues['standards']) + len(issues['bugs'])}")
                
            except ImportError:
                print("❌ Flake8 not available at all - please install with: pip install flake8")
                issues['bugs'].append("Flake8 not available - install with: pip install flake8")
        
        print(f"   Standards: {len(issues['standards'])}, Bugs: {len(issues['bugs'])}")
        return issues
    
    def _run_ast_analysis(self, file_content, filename):
        """Run AST-based analysis for complexity and structure."""
        issues = {'complexity': [], 'structure': []}
        
        try:
            print("🔍 Running AST analysis...")
            tree = ast.parse(file_content)
            
            # Analyze complexity and structure
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
            
            print(f"✅ AST analysis found: Complexity: {len(issues['complexity'])}, Structure: {len(issues['structure'])}")
                        
        except SyntaxError as e:
            issues['bugs'].append(f"Syntax error in {filename}: {str(e)}")
            print(f"❌ Syntax error: {str(e)}")
        except Exception as e:
            issues['bugs'].append(f"AST analysis error: {str(e)}")
            print(f"❌ AST error: {str(e)}")
            
        return issues
    
    def _run_security_analysis(self, file_content):
        """Run security-focused analysis."""
        issues = {'security': []}
        
        print("🔍 Running Security analysis...")
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
        
        print(f"✅ Security analysis found: {len(issues['security'])} issues")
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
                max_depth = max(child_depth, max_depth)
        
        return max_depth
