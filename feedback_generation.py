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
                    suggestions.append("Add docstrings to functions for better readability.")
                if 'W0612' in item or 'unused variable' in item.lower():
                    suggestions.append("Remove unused variables to improve performance.")
                if 'W0101' in item or 'unreachable code' in item.lower():
                    suggestions.append("Remove unreachable code to improve clarity.")
                # Flake8 codes
                if 'E231' in item or 'missing whitespace' in item.lower():
                    suggestions.append("Add proper spacing after commas to comply with PEP 8.")
                if 'F841' in item or 'local variable' in item.lower():
                    suggestions.append("Remove unused variables to improve performance.")
        return list(set(suggestions))  # Remove duplicates