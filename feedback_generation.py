class FeedbackGeneration:
    """Module for feedback generation with AI suggestions and scoring (AI, Backend tech stack)."""
    def generate_feedback(self, analysis_results):
        """Generates report with score and suggestions."""
        report = "PR Review Feedback:\n"
        total_issues = 0
        all_issues = {}
        for result in analysis_results:
            filename = result['filename']
            issues = result['issues']
            report += f"\nFile: {filename}\n"
            if not any(issues.values()):
                report += "- No issues detected\n"
            for category, items in issues.items():
                for item in items:
                    report += f"- {category.capitalize()}: {item}\n"
                    total_issues += 1
                all_issues[category] = all_issues.get(category, []) + items
        
        # Scoring
        score = max(0, 100 - (total_issues * 5))
        report += f"\nPR Score: {score}/100\n"
        
        # AI Suggestions
        suggestions = self._get_ai_suggestions(all_issues)
        report += "\nRecommendations:\n"
        if suggestions:
            for sug in suggestions:
                report += f"- {sug}\n"
        else:
            report += "- No additional recommendations.\n"
        
        return report
    
    def _get_ai_suggestions(self, issues):
        """AI-driven suggestions (simulate with rules; integrate CodeMate AI)."""
        suggestions = []
        for category, items in issues.items():
            for item in items:
                # Pylint codes
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
                # Flake8 codes
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