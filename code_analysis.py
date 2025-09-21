import subprocess
import tempfile
import os
import json
import ast
import re
from typing import Dict, List, Any


class CodeAnalysis:
    """Enhanced code analysis engine with multiple tools."""
    
    def __init__(self):
        print("🔧 Initializing Code Analysis Engine...")
        self.analysis_tools = {
            'pylint': True,
            'flake8': True, 
            'ast': True,
            'security': True
        }

    def analyze_file(self, content: str, filename: str) -> Dict[str, List[str]]:
        """
        Comprehensive analysis of a single file.
        Returns categorized issues.
        """
        print(f"🔎 Starting comprehensive analysis for {filename}...")
        
        # Validate content first
        if not content or not content.strip():
            print(f"   ⚠️  Empty or invalid content for {filename}")
            return {
                'standards': [],
                'structure': [],
                'bugs': ['Empty file or no content to analyze'],
                'complexity': [],
                'security': [],
                'performance': []
            }
        
        # Check for binary content or encoding issues
        try:
            # Try to encode/decode to verify it's valid text
            content.encode('utf-8').decode('utf-8')
        except UnicodeError:
            print(f"   ⚠️  Content encoding issue for {filename}")
            return {
                'standards': [],
                'structure': [],
                'bugs': ['File contains invalid characters or encoding issues'],
                'complexity': [],
                'security': [],
                'performance': []
            }
        
        # Check for null bytes or binary content
        if '\x00' in content:
            print(f"   ⚠️  Binary content detected in {filename}")
            return {
                'standards': [],
                'structure': [],
                'bugs': ['File appears to be binary, not Python source code'],
                'complexity': [],
                'security': [],
                'performance': []
            }
        
        issues = {
            'standards': [],
            'structure': [],
            'bugs': [],
            'complexity': [],
            'security': [],
            'performance': []
        }
        
        # Create temporary file for analysis
        try:
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            print(f"📝 Created temp file: {temp_file_path}")
            
            # Run all analysis tools
            self._run_pylint_analysis(temp_file_path, issues)
            self._run_flake8_analysis(temp_file_path, issues)
            self._run_ast_analysis(content, issues)
            self._run_security_analysis(content, issues)
            
        except Exception as e:
            print(f"   ❌ Error creating temp file for {filename}: {str(e)}")
            issues['bugs'].append(f"Analysis setup error: {str(e)}")
        finally:
            # Clean up temp file
            try:
                if 'temp_file_path' in locals():
                    os.unlink(temp_file_path)
                    print("🧹 Cleaned up temp file")
            except Exception as e:
                print(f"   ⚠️  Could not clean up temp file: {str(e)}")
        
        # Count issues by category
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        categories = [cat for cat, issue_list in issues.items() if issue_list]
        
        print(f"📊 Analysis complete: {total_issues} total issues found")
        if categories:
            print(f"   {', '.join(categories)}: {', '.join([f'{len(issues[cat])}' for cat in categories])} issues")
        
        return issues

    def _run_pylint_analysis(self, temp_file_path: str, issues: Dict[str, List[str]]):
        """Run Pylint analysis."""
        try:
            print("🔍 Running Pylint analysis...")
            
            result = subprocess.run(
                ['pylint', temp_file_path, '--output-format=json', '--reports=no'],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            pylint_output = result.stdout or ""
            print(f"📋 Pylint output ({len(pylint_output)} chars):")
            
            if pylint_output.strip():
                debug_output = pylint_output[:500] + "..." if len(pylint_output) > 500 else pylint_output
                print(f"  DEBUG: {debug_output}")
                
                try:
                    pylint_issues = json.loads(pylint_output)
                    parsed_count = 0
                    standards_count = 0
                    structure_count = 0
                    bugs_count = 0
                    
                    for issue in pylint_issues:
                        issue_type = issue.get('type', 'unknown')
                        message = issue.get('message', 'Unknown issue')
                        symbol = issue.get('symbol', '')
                        message_id = issue.get('message-id', '')
                        
                        # Create formatted issue string
                        formatted_issue = f"{message_id}: {message} ({symbol})" if symbol else f"{message_id}: {message}"
                        print(f"  PARSED: {message_id} -> {message[:50]}...")
                        parsed_count += 1
                        
                        # Categorize issues
                        if issue_type in ['convention', 'C']:
                            issues['standards'].append(formatted_issue)
                            standards_count += 1
                        elif issue_type in ['refactor', 'R']:
                            issues['structure'].append(formatted_issue)
                            structure_count += 1
                        elif issue_type in ['warning', 'error', 'W', 'E']:
                            issues['bugs'].append(formatted_issue)
                            bugs_count += 1
                        else:
                            issues['bugs'].append(formatted_issue)
                            bugs_count += 1
                    
                    print(f"✅ Pylint processed {parsed_count} issue lines")
                    print(f"   Standards: {standards_count}, Structure: {structure_count}, Bugs: {bugs_count}")
                    
                except json.JSONDecodeError as e:
                    print(f"   ⚠️  Could not parse Pylint JSON output: {str(e)}")
                    # Try to extract issues from text output
                    if result.stderr:
                        stderr_lines = result.stderr.strip().split('\n')
                        for line in stderr_lines[:5]:  # Take first 5 error lines
                            if line.strip():
                                issues['bugs'].append(f"Pylint error: {line.strip()}")
            else:
                print("   ✅ No Pylint issues found")
                
        except subprocess.TimeoutExpired:
            issues['bugs'].append("Pylint analysis timed out")
            print("   ⚠️  Pylint analysis timed out")
        except Exception as e:
            issues['bugs'].append(f"Pylint analysis failed: {str(e)}")
            print(f"   ⚠️  Pylint analysis error: {str(e)}")

    def _run_flake8_analysis(self, temp_file_path: str, issues: Dict[str, List[str]]):
        """Run Flake8 analysis."""
        try:
            print("🔍 Running Flake8 analysis...")
            
            result = subprocess.run(
                ['flake8', temp_file_path, '--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s'],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            flake8_output = result.stdout or ""
            flake8_stderr = result.stderr or ""
            
            print(f"📋 Flake8 stdout ({len(flake8_output)} chars):")
            if flake8_stderr:
                print(f"📋 Flake8 stderr: {flake8_stderr[:200]}...")
            
            if flake8_output.strip():
                debug_output = flake8_output[:500] + "..." if len(flake8_output) > 500 else flake8_output
                print(f"  DEBUG: {debug_output}")
                
                flake8_lines = flake8_output.strip().split('\n')
                parsed_count = 0
                
                for line in flake8_lines:
                    if line.strip() and ':' in line:
                        # Extract error code and message
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            error_part = parts[3].strip()
                            if error_part:
                                # Parse error code (E231, F841, etc.)
                                error_match = re.match(r'^([A-Z]\d+)\s+(.+)$', error_part)
                                if error_match:
                                    error_code = error_match.group(1)
                                    error_message = error_match.group(2)
                                    formatted_issue = f"{error_code}: {error_message}"
                                    print(f"  PARSED: {error_code} -> {error_message[:50]}...")
                                    issues['bugs'].append(formatted_issue)
                                    parsed_count += 1
                
                print(f"✅ Flake8 subprocess processed {parsed_count} issue lines")
                print(f"   Standards: 0, Bugs: {parsed_count}")
                
            else:
                print("✅ Flake8 subprocess processed 0 issue lines")
                print("   Standards: 0, Bugs: 0")
                
        except subprocess.TimeoutExpired:
            issues['bugs'].append("Flake8 analysis timed out")
            print("   ⚠️  Flake8 analysis timed out")
        except Exception as e:
            issues['bugs'].append(f"Flake8 analysis failed: {str(e)}")
            print(f"   ⚠️  Flake8 analysis error: {str(e)}")

    def _run_ast_analysis(self, content: str, issues: Dict[str, List[str]]):
        """Run AST-based analysis."""
        try:
            print("🔍 Running AST analysis...")
            
            # Try to parse the AST
            tree = ast.parse(content)
            
            # Count complexity indicators
            complexity_count = 0
            structure_count = 0
            
            for node in ast.walk(tree):
                # Count complexity indicators
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                    complexity_count += 1
                    
                # Count structural elements
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    structure_count += 1
            
            print(f"✅ AST analysis found: Complexity: {complexity_count}, Structure: {structure_count}")
            
            # Only add issues if complexity is very high
            if complexity_count > 10:
                issues['complexity'].append(f"High complexity: {complexity_count} control structures")
                
        except SyntaxError as e:
            issues['bugs'].append(f"Syntax error: {str(e)}")
            print(f"   ⚠️  AST parsing failed: {str(e)}")
        except Exception as e:
            print(f"   ⚠️  AST analysis error: {str(e)}")

    def _run_security_analysis(self, content: str, issues: Dict[str, List[str]]):
        """Run basic security analysis."""
        try:
            print("🔍 Running Security analysis...")
            
            security_patterns = [
                (r'eval\s*\(', 'Use of eval() function is dangerous'),
                (r'exec\s*\(', 'Use of exec() function is dangerous'),
                (r'__import__\s*\(', 'Dynamic imports can be security risks'),
                (r'subprocess\.call\s*\(.*shell\s*=\s*True', 'Shell injection vulnerability'),
                (r'os\.system\s*\(', 'Command injection vulnerability')
            ]
            
            security_issues = 0
            for pattern, message in security_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues['security'].append(message)
                    security_issues += 1
            
            print(f"✅ Security analysis found: {security_issues} issues")
            
        except Exception as e:
            print(f"   ⚠️  Security analysis error: {str(e)}")
