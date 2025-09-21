import json
from datetime import datetime

class FeedbackGeneration:
    """Enhanced feedback generation with comprehensive reporting."""
    
    def __init__(self):
        self.scoring_weights = {
            'bugs': 15,           # High weight for bugs
            'security': 20,       # Highest weight for security
            'standards': 8,       # Medium weight for standards
            'structure': 10,      # Medium-high for structure
            'complexity': 12,     # High for complexity
            'performance': 10     # Medium-high for performance
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
        report += self._generate_recommendations(all_issues)
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
        """Generate overall summary and scoring."""
        # Calculate weighted score
        weighted_score = 100
        for category, weight in self.scoring_weights.items():
            issue_count = len(all_issues.get(category, []))
            penalty = min(issue_count * weight, 50)  # Cap penalty at 50 per category
            weighted_score -= penalty
        
        weighted_score = max(0, weighted_score)
        
        # Overall risk assessment
        avg_risk = risk_score / max(file_count, 1)
        overall_risk = self._get_risk_level(avg_risk)
        
        summary = f"""
🎯 OVERALL ASSESSMENT
{'='*30}
📊 Total Issues: {total_issues}
🏆 Quality Score: {weighted_score}/100
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
    
    def _generate_recommendations(self, all_issues):
        """Generate AI-powered recommendations."""
        recommendations = "\n🚀 SMART RECOMMENDATIONS:\n"
        recommendations += "=" * 30 + "\n"
        
        priority_suggestions = self._get_priority_suggestions(all_issues)
        
        if not priority_suggestions:
            recommendations += "✅ No specific recommendations - code looks good!\n"
            return recommendations
        
        for i, suggestion in enumerate(priority_suggestions, 1):
            recommendations += f"{i}. 🎯 {suggestion}\n"
        
        # Add learning resources
        recommendations += self._get_learning_resources(all_issues)
        
        return recommendations
    
    def _generate_inline_comments_section(self, analysis_results):
        """Generate inline comments section."""
        section = "\n💬 INLINE REVIEW COMMENTS:\n"
        section += "=" * 30 + "\n"
        
        has_comments = False
        for result in analysis_results:
            inline_comments = result.get('inline_comments', [])
            if inline_comments:
                has_comments = True
                section += f"\n📄 {result['filename']}:\n"
                for comment in inline_comments[:10]:  # Limit to first 10
                    line_num = comment.get('line', 'N/A')
                    code = comment.get('code', '')[:50] + ('...' if len(comment.get('code', '')) > 50 else '')
                    suggestion = comment.get('suggestion', '')
                    
                    section += f"  Line {line_num}: `{code}`\n"
                    section += f"  💡 {suggestion}\n\n"
        
        if not has_comments:
            section += "ℹ️  No line-specific comments generated.\n"
        
        return section
    
    def _calculate_file_risk(self, issues):
        """Calculate risk score for a file."""
        risk_score = 0
        for category, items in issues.items():
            weight = self.scoring_weights.get(category, 5)
            risk_score += len(items) * weight
        return risk_score
    
    def _get_risk_level(self, score):
        """Get risk level based on score."""
        if score >= 50:
            return "🔴 HIGH"
        elif score >= 25:
            return "🟡 MEDIUM"
        elif score >= 10:
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
        """Get prioritized suggestions based on issues found."""
        suggestions = []
        
        # Security first
        if all_issues.get('security'):
            suggestions.append("🔒 **SECURITY PRIORITY**: Fix security vulnerabilities immediately")
        
        # Critical bugs
        bugs = all_issues.get('bugs', [])
        critical_bugs = [b for b in bugs if any(x in b.lower() for x in ['error', 'exception', 'undefined'])]
        if critical_bugs:
            suggestions.append("🐛 Fix critical bugs that may cause runtime errors")
        
        # High complexity
        if all_issues.get('complexity'):
            suggestions.append("🔄 Refactor complex functions to improve maintainability")
        
        # Structure issues
        if all_issues.get('structure'):
            suggestions.append("🏗️ Improve code structure and organization")
        
        # Performance
        if all_issues.get('performance'):
            suggestions.append("⚡ Optimize performance bottlenecks")
        
        # Standards
        if len(all_issues.get('standards', [])) > 5:
            suggestions.append("📏 Address coding standard violations for better readability")
        
        # Specific suggestions for detected issues
        for category, items in all_issues.items():
            for item in items:
                if 'C0114' in item or 'C0116' in item or 'missing docstring' in item.lower():
                    suggestions.append("Add docstrings to functions and modules for better readability.")
                if 'W0612' in item or 'unused variable' in item.lower():
                    suggestions.append("Remove unused variables to improve performance.")
                if 'W0101' in item or 'unreachable code' in item.lower():
                    suggestions.append("Remove unreachable code to improve clarity.")
                if 'C3001' in item or 'unnecessary-lambda-assignment' in item.lower():
                    suggestions.append("Replace lambda assignments with proper function definitions.")
                if 'W0125' in item or 'using a conditional statement with a constant value' in item.lower():
                    suggestions.append("Avoid using constant values in conditional statements.")
                if 'C0115' in item or 'missing class docstring' in item.lower():
                    suggestions.append("Add docstrings to classes for better documentation.")
                if 'R0903' in item or 'too few public methods' in item.lower():
                    suggestions.append("Consider adding more public methods to classes for better functionality.")
                if 'E231' in item or 'missing whitespace' in item.lower():
                    suggestions.append("Add proper spacing after commas to comply with PEP 8.")
                if 'E261' in item or 'spaces before inline comment' in item.lower():
                    suggestions.append("Ensure at least two spaces before inline comments per PEP 8.")
                if 'F841' in item or 'local variable' in item.lower():
                    suggestions.append("Remove unused variables to improve performance.")
                if 'E302' in item or 'expected 2 blank lines' in item.lower():
                    suggestions.append("Add two blank lines before function or class definitions for better readability.")
                if 'E305' in item or 'expected 2 blank lines after' in item.lower():
                    suggestions.append("Add two blank lines after function or class definitions for better readability.")
                if 'E731' in item or 'do not assign a lambda expression' in item.lower():
                    suggestions.append("Use 'def' for function definitions instead of lambda assignments.")
        
        return list(set(suggestions))  # Remove duplicates
    
    def _get_learning_resources(self, all_issues):
        """Provide learning resources based on issues."""
        resources = "\n📚 LEARNING RESOURCES:\n"
        
        if all_issues.get('security'):
            resources += "• Security: https://owasp.org/www-project-top-ten/\n"
        
        if all_issues.get('standards'):
            resources += "• Python Style: https://pep8.org/\n"
        
        if all_issues.get('complexity'):
            resources += "• Code Complexity: https://refactoring.guru/\n"
        
        if all_issues.get('structure'):
            resources += "• Clean Code: https://clean-code-developer.com/\n"
        
        return resources