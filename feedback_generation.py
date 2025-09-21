import json
from datetime import datetime


class FeedbackGeneration:
    """Enhanced feedback generation with comprehensive reporting."""
    
    def __init__(self):
        self.scoring_weights = {
            'bugs': 8,            # Reduced from 15 - still important but not overly harsh
            'security': 20,       # Highest weight for security
            'standards': 4,       # Reduced from 8 - standards are important but not critical  
            'structure': 8,       # Medium for structure
            'complexity': 12,     # High for complexity
            'performance': 8      # Medium for performance
        }
    
    def generate_comprehensive_feedback(self, analysis_results, pr_data):
        """Generate comprehensive PR review report."""
        report = self._generate_header(pr_data)
        
        # File-by-file analysis
        total_issues = 0
        all_issues = {}
        risk_score = 0
        
        for result in analysis_results:
            file_report, file_issues, file_risk = self._generate_file_report(result)
            report += file_report
            total_issues += file_issues
            risk_score += file_risk
            
            # Aggregate issues by category
            for category, items in result['issues'].items():
                if category not in all_issues:
                    all_issues[category] = []
                all_issues[category].extend(items)
        
        # Overall scoring and recommendations
        report += self._generate_summary(all_issues, total_issues, risk_score, len(analysis_results))
        report += self._generate_smart_recommendations(all_issues)
        report += self._generate_inline_comments_section(analysis_results)
        
        return report
    
    def _generate_header(self, pr_data):
        """Generate report header with PR metadata."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_files = len(pr_data)
        total_additions = sum(f.get('additions', 0) for f in pr_data)
        total_deletions = sum(f.get('deletions', 0) for f in pr_data)
        
        header = f"""
📋 PR REVIEW REPORT
📅 Generated: {timestamp}
📁 Files Analyzed: {total_files}
➕ Lines Added: {total_additions}
➖ Lines Deleted: {total_deletions}
🔍 Analysis Tools: Pylint, Flake8, AST, Security Scanner

"""
        return header
    
    def _generate_file_report(self, result):
        """Generate report for individual file."""
        filename = result['filename']
        issues = result['issues']
        
        file_issues = sum(len(items) for items in issues.values())
        
        report = f"\n📄 FILE: {filename}\n"
        report += "─" * (len(filename) + 8) + "\n"
        
        if file_issues == 0:
            report += "✅ No issues detected - Great job!\n"
            return report, 0, 0
        
        # Risk assessment
        risk_score = self._calculate_file_risk(issues)
        risk_level = self._get_risk_level(risk_score)
        
        report += f"🎯 Issues Found: {file_issues}\n"
        report += f"⚠️  Risk Level: {risk_level}\n\n"
        
        # Issues by category
        for category, items in issues.items():
            if items:
                icon = self._get_category_icon(category)
                report += f"{icon} {category.upper()} ({len(items)} issues):\n"
                for i, item in enumerate(items[:5], 1):  # Limit to first 5
                    report += f"  {i}. {item}\n"
                if len(items) > 5:
                    report += f"  ... and {len(items) - 5} more {category} issues\n"
                report += "\n"
        
        return report, file_issues, risk_score
    
    def _generate_summary(self, all_issues, total_issues, risk_score, file_count):
        """Generate overall summary and scoring with improved calculation."""
        # Improved weighted score calculation
        base_score = 100
        total_penalty = 0
        
        for category, weight in self.scoring_weights.items():
            issue_count = len(all_issues.get(category, []))
            if issue_count > 0:
                # Progressive penalty - first few issues have less impact
                if issue_count <= 3:
                    penalty = issue_count * weight * 0.5  # 50% penalty for first 3
                elif issue_count <= 7:
                    penalty = (3 * weight * 0.5) + ((issue_count - 3) * weight * 0.8)  # 80% for next 4
                else:
                    penalty = (3 * weight * 0.5) + (4 * weight * 0.8) + ((issue_count - 7) * weight)  # Full penalty for rest
                
                total_penalty += min(penalty, 40)  # Cap per category at 40 points
        
        weighted_score = max(5, base_score - total_penalty)  # Minimum score of 5
        
        # Overall risk assessment
        avg_risk = risk_score / max(file_count, 1)
        overall_risk = self._get_risk_level(avg_risk)
        
        summary = f"""
🎯 OVERALL ASSESSMENT
{'='*30}
📊 Total Issues: {total_issues}
🏆 Quality Score: {int(weighted_score)}/100
⚠️  Risk Level: {overall_risk}
📁 Files Affected: {file_count}

🔢 ISSUE BREAKDOWN:
"""
        
        for category in ['security', 'bugs', 'complexity', 'structure', 'standards', 'performance']:
            count = len(all_issues.get(category, []))
            if count > 0:
                icon = self._get_category_icon(category)
                summary += f"{icon} {category.title()}: {count}\n"
        
        return summary
    
    def _generate_smart_recommendations(self, all_issues):
        """Generate prioritized, actionable recommendations."""
        recommendations = "\n🚀 SMART RECOMMENDATIONS:\n"
        recommendations += "=" * 30 + "\n"
        
        priority_suggestions = self._get_priority_suggestions(all_issues)
        
        if not priority_suggestions:
            recommendations += "✅ No specific recommendations - code looks good!\n"
            return recommendations
        
        # Group recommendations by priority
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for suggestion in priority_suggestions:
            if any(word in suggestion.lower() for word in ['security', 'critical', 'error']):
                high_priority.append(suggestion)
            elif any(word in suggestion.lower() for word in ['unused', 'unreachable', 'complexity']):
                medium_priority.append(suggestion)
            else:
                low_priority.append(suggestion)
        
        # Add recommendations by priority
        if high_priority:
            recommendations += "\n🔴 HIGH PRIORITY:\n"
            for i, suggestion in enumerate(high_priority, 1):
                recommendations += f"{i}. {suggestion}\n"
        
        if medium_priority:
            recommendations += "\n🟡 MEDIUM PRIORITY:\n"
            for i, suggestion in enumerate(medium_priority, 1):
                recommendations += f"{i}. {suggestion}\n"
        
        if low_priority:
            recommendations += "\n🟢 LOW PRIORITY:\n"
            for i, suggestion in enumerate(low_priority, 1):
                recommendations += f"{i}. {suggestion}\n"
        
        # Add learning resources
        recommendations += self._get_learning_resources(all_issues)
        
        return recommendations
    
    def _generate_inline_comments_section(self, analysis_results):
        """Generate enhanced inline comments section."""
        section = "\n💬 INLINE REVIEW COMMENTS:\n"
        section += "=" * 30 + "\n"
        
        has_comments = False
        comment_count = 0
        
        for result in analysis_results:
            filename = result['filename']
            issues = result['issues']
            
            # Generate line-specific comments from issues
            file_comments = []
            for category, issue_list in issues.items():
                for issue in issue_list:
                    comment = self._create_inline_comment(issue, category, filename)
                    if comment:
                        file_comments.append(comment)
            
            if file_comments:
                has_comments = True
                section += f"\n📄 {filename}:\n"
                
                for comment in file_comments[:8]:  # Limit to 8 per file
                    section += f"  💡 **{comment['category'].upper()}**: {comment['suggestion']}\n"
                    if comment.get('example'):
                        section += f"     📝 Example: {comment['example']}\n"
                    section += "\n"
                    comment_count += 1
                
                if len(file_comments) > 8:
                    section += f"     ... and {len(file_comments) - 8} more suggestions\n\n"
        
        if not has_comments:
            section += "ℹ️  No line-specific comments generated.\n"
        else:
            section += f"📊 Generated {comment_count} actionable suggestions\n"
        
        return section
    
    def _create_inline_comment(self, issue, category, filename):
        """Create actionable inline comment from issue."""
        comment_templates = {
            'C0114': {
                'suggestion': "Add a module docstring at the top of the file to describe its purpose",
                'example': '"""This module contains utility functions for data processing."""'
            },
            'C0116': {
                'suggestion': "Add docstrings to functions/methods to explain their purpose and parameters", 
                'example': '"""Calculate the sum of two numbers. Args: a, b (int/float). Returns: sum."""'
            },
            'C0115': {
                'suggestion': "Add a class docstring to describe the class purpose and functionality",
                'example': '"""A utility class for mathematical calculations."""'
            },
            'W0612': {
                'suggestion': "Remove unused variables or use them in your logic",
                'example': "Remove 'temp = a + b' since it's not used, or use temp in return statement"
            },
            'W0101': {
                'suggestion': "Remove unreachable code that comes after return statements",
                'example': "Delete lines that appear after 'return' statements - they will never execute"
            },
            'E231': {
                'suggestion': "Add spaces after commas for better readability (PEP 8)",
                'example': "Change 'def add(a,b):' to 'def add(a, b):'"
            },
            'E261': {
                'suggestion': "Add at least two spaces before inline comments (PEP 8)",
                'example': "Change 'x = 1 # comment' to 'x = 1  # comment'"
            },
            'E302': {
                'suggestion': "Add 2 blank lines before function/class definitions (PEP 8)",
                'example': "Insert 2 empty lines before 'def function_name():' or 'class ClassName:'"
            },
            'E731': {
                'suggestion': "Replace lambda assignments with proper function definitions",
                'example': "Change 'func = lambda x: x*2' to 'def func(x): return x*2'"
            },
            'F841': {
                'suggestion': "Remove or use local variables that are assigned but never used",
                'example': "Either delete the variable or use it in your code logic"
            }
        }
        
        # Extract error code from issue
        for code, template in comment_templates.items():
            if code in issue:
                return {
                    'category': category,
                    'code': code,
                    'suggestion': template['suggestion'],
                    'example': template.get('example', '')
                }
        
        # Generic comment for unmatched issues
        return {
            'category': category,
            'code': 'GENERIC',
            'suggestion': f"Review this {category} issue: {issue[:100]}...",
            'example': ''
        }
    
    def _calculate_file_risk(self, issues):
        """Calculate risk score for a file."""
        risk_score = 0
        for category, items in issues.items():
            weight = self.scoring_weights.get(category, 5)
            risk_score += len(items) * weight
        return risk_score
    
    def _get_risk_level(self, score):
        """Get risk level based on score."""
        if score >= 80:
            return "🔴 HIGH"
        elif score >= 40:
            return "🟡 MEDIUM"
        elif score >= 15:
            return "🟢 LOW"
        else:
            return "✅ MINIMAL"
    
    def _get_category_icon(self, category):
        """Get icon for issue category."""
        icons = {
            'security': '🔒',
            'bugs': '🐛',
            'standards': '📏',
            'structure': '🏗️',
            'complexity': '🔄',
            'performance': '⚡'
        }
        return icons.get(category, '📝')
    
    def _get_priority_suggestions(self, all_issues):
        """Get prioritized suggestions based on issues found - FIXED VERSION."""
        suggestions = []
        
        # Security first (critical)
        if all_issues.get('security'):
            suggestions.append("🔒 **CRITICAL**: Fix security vulnerabilities immediately")
        
        # Critical bugs
        bugs = all_issues.get('bugs', [])
        if bugs:
            # Check for specific types of bugs
            if any('unreachable' in str(bug).lower() for bug in bugs):
                suggestions.append("🐛 Remove unreachable code that will never execute")
            if any('unused' in str(bug).lower() for bug in bugs):
                suggestions.append("🐛 Clean up unused variables to improve code clarity")
            if any('constant' in str(bug).lower() for bug in bugs):
                suggestions.append("🐛 Fix conditional statements with constant values")
        
        # Standards issues
        standards = all_issues.get('standards', [])
        if standards:
            if any('docstring' in str(std).lower() for std in standards):
                suggestions.append("📏 Add docstrings to improve code documentation")
            if any('whitespace' in str(std).lower() for std in standards):
                suggestions.append("📏 Fix spacing and formatting issues (PEP 8)")
        
        # Structure issues  
        if all_issues.get('structure'):
            suggestions.append("🏗️ Improve code structure and class design")
        
        # Complexity
        if all_issues.get('complexity'):
            suggestions.append("🔄 Refactor complex functions to improve maintainability")
        
        return suggestions
    
    def _get_learning_resources(self, all_issues):
        """Provide learning resources based on issues."""
        resources = "\n📚 LEARNING RESOURCES:\n"
        
        has_resources = False
        if all_issues.get('security'):
            resources += "• Security Best Practices: https://owasp.org/www-project-top-ten/\n"
            has_resources = True
        
        if all_issues.get('standards'):
            resources += "• Python Style Guide (PEP 8): https://pep8.org/\n"
            has_resources = True
        
        if all_issues.get('complexity') or all_issues.get('structure'):
            resources += "• Clean Code Principles: https://refactoring.guru/\n"
            has_resources = True
        
        # Fixed this line - convert to string first before checking
        standards_str = str(all_issues.get('standards', []))
        if 'docstring' in standards_str.lower():
            resources += "• Python Docstring Guide: https://peps.python.org/pep-0257/\n"
            has_resources = True
        
        if not has_resources:
            resources += "• General Python Best Practices: https://docs.python-guide.org/\n"
        
        return resources
